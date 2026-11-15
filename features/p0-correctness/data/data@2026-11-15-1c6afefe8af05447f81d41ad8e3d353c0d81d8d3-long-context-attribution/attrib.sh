#!/bin/bash
R=/scratch/cc-long; ST=$R/status2; : > $ST; M=/scratch/models/GLM-5-1028-Provider
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47"
DEP="--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head"
arm() { # name flags
  local N=$1 L=$R/logs/$1; mkdir -p $L
  BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l); [ "$BUSY" -ne 0 ] && { echo "$N GPU_BUSY" >> $ST; return; }
  { echo "export PYTHONPATH=/scratch/cc-merge/overlay:/scratch/cc-pr43/overlay:$R/src-new/python"; echo "export HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python"; echo "cd $R/src-new"
    echo "exec /opt/sglang/bin/python -m sglang.launch_server --model-path $M --host 127.0.0.1 --port 31746 $2 $MTP"; } > $L/launch.sh
  tmux kill-session -t cclong 2>/dev/null; tmux new -d -s cclong "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:31746/health >/dev/null && { ok=1; break; }; tmux has-session -t cclong 2>/dev/null || break; sleep 10; done
  if [ $ok -eq 1 ]; then echo "$N READY $(date -u +%T)" >> $ST
    [ "$3" = skipoff ] || { /opt/sglang/bin/python $R/stress.py http://127.0.0.1:31746/v1 $L/long.jsonl 12 2 long 60000 110000 > $L/long.log 2>&1; echo "$N off rc=$? $(date -u +%T)" >> $ST; }
    /opt/sglang/bin/python $R/stress-think.py http://127.0.0.1:31746/v1 $L/think.jsonl 12 2 long 60000 110000 > $L/think.log 2>&1; echo "$N think rc=$? $(date -u +%T)" >> $ST
  else echo "$N NOT_READY $(date -u +%T)" >> $ST; fi
  tmux kill-session -t cclong 2>/dev/null; sleep 10; for p in $(pgrep -f "port 31746|sglang::"); do kill -9 $p 2>/dev/null; done; sleep 15
}
arm dep8-bf16 "$DEP --kv-cache-dtype bfloat16"
arm tp8-bf16 "--tp-size 8 --mem-fraction-static 0.75 --context-length 147456 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph"
arm dep8-fp8-think "$DEP --kv-cache-dtype fp8_e4m3" skipoff
echo DONE >> $ST
