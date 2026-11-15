#!/bin/bash
R=/scratch/cc-combo; M=/scratch/models/GLM-5-1028-Provider; ST=$R/status; : > $ST
export HF_HOME=/scratch/cc-pr43/hf-home
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47"
run() { # name "envs" "probe lengths" flags...
  local N=$1 ENVS=$2 PL=$3; shift 3; local L=$R/logs/$N; mkdir -p $L
  BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
  [ "$BUSY" -ne 0 ] && { echo "$N GPU_BUSY_FOREIGN" >> $ST; return; }
  { echo "export PYTHONPATH=/scratch/cc-pr43/overlay:$R/src/python"; echo "export HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home"
    echo "export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1"; for e in $ENVS; do echo "export $e"; done
    echo "cd $R/src"; echo "exec /opt/sglang/bin/python -m sglang.launch_server --model-path $M --host 127.0.0.1 --port 31744 $* $MTP"; } > $L/launch.sh
  tmux kill-session -t cccombo 2>/dev/null; tmux new -d -s cccombo "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:31744/health >/dev/null && { ok=1; break; }; tmux has-session -t cccombo 2>/dev/null || break; sleep 10; done
  if [ $ok -eq 1 ]; then echo "$N READY $(date -u +%T)" >> $ST
    /opt/sglang/bin/python $R/probe.py http://127.0.0.1:31744/v1 $L/probe.json $PL > $L/probe.log 2>&1; echo "$N probe rc=$? $(date -u +%T)" >> $ST
    /opt/sglang/bin/python $R/midfork.py http://127.0.0.1:31744/v1 $L/midfork.json $N > $L/midfork.log 2>&1; echo "$N midfork rc=$? $(date -u +%T)" >> $ST
    /opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:31744/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/eval > $L/gsm8k.log 2>&1; echo "$N gsm8k rc=$? $(date -u +%T)" >> $ST
    curl -sf -m 5 localhost:31744/health >/dev/null && echo "$N ALIVE_AT_END" >> $ST || echo "$N DOWN_AT_END" >> $ST
  else echo "$N NOT_READY $(date -u +%T)" >> $ST; fi
  tmux kill-session -t cccombo 2>/dev/null; sleep 10
  for p in $(pgrep -f "port 31744|sglang::"); do kill -9 $p 2>/dev/null; done; sleep 15
}
run cp8 "SGLANG_JIT_DEEPGEMM_PRECOMPILE=0" "300 3000 9000 24000 60000 110000" --tp-size 8 --mem-fraction-static 0.75 --context-length 131072 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 8 --cuda-graph-backend-prefill breakable
run dep8 "" "300 3000 9000 24000 60000 110000" --tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head
echo DONE >> $ST
