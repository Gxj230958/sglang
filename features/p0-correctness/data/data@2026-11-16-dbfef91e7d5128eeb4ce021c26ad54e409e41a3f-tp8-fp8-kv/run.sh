#!/bin/bash
R=/scratch/cc-tp8fp8; mkdir -p $R; ST=$R/status; : > $ST; M=/scratch/models/GLM-5-1028-Provider; S=/scratch/codex-fi074/src; P=31747
export PYTHONPATH=/scratch/codex-fi074/overlay:$S/python HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
PY=/opt/sglang/bin/python
stop() { tmux kill-session -t cctp8fp8 2>/dev/null; sleep 10; for p in $(pgrep -f "port $P"); do kill -9 $p 2>/dev/null; done; sleep 25; }
snap() { curl -s -m 20 localhost:$P/metrics | grep -E "^sglang:(generation_tokens_total|spec_verify_calls_total)" > $L/$1.metrics; }
bench() {
  $PY -m sglang.bench_serving --backend sglang --host 127.0.0.1 --port $P --model $M --dataset-name random-ids --random-input-len $2 --random-output-len $3 --random-range-ratio 1 --num-prompts $4 --max-concurrency $5 --seed $6 --flush-cache --warmup-requests 2 --output-file $L/$1-s$6.jsonl > $L/$1-s$6.log 2>&1
  echo "$ARM $1 seed=$6 rc=$? $(date -u +%T)" >> $ST; }
for ARM in tp8-fp8 tp8-bf16; do
  L=$R/$ARM; mkdir -p $L; FLAG=""
  [ $ARM = tp8-fp8 ] && FLAG="--dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3"
  BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
  [ "$BUSY" -ne 0 ] && { echo "GPU_BUSY $ARM" >> $ST; break; }
  echo "cd $S; export PYTHONPATH=$PYTHONPATH HF_HOME=$HF_HOME HF_HUB_CACHE=$HF_HUB_CACHE SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python; exec $PY -m sglang.launch_server --model-path $M --host 127.0.0.1 --port $P --tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics $FLAG" > $L/launch.sh
  tmux kill-session -t cctp8fp8 2>/dev/null; tmux new -d -s cctp8fp8 "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:$P/health >/dev/null && { ok=1; break; }; tmux has-session -t cctp8fp8 2>/dev/null || break; sleep 10; done
  [ $ok -eq 1 ] || { echo "NOT_READY $ARM $(date -u +%T)" >> $ST; stop; continue; }
  echo "READY $ARM $(date -u +%T)" >> $ST
  for seed in 1 2; do
    bench short-c1 2000 500 16 1 $seed
    bench short-c32 2000 500 128 32 $seed
    bench long-c4 30000 300 16 4 $seed
  done
  if [ $ARM = tp8-fp8 ]; then
    snap before-t1
    /opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:$P/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/eval-t1 > $L/gsm8k-t1.log 2>&1; echo "$ARM gsm8k t1 rc=$? $(date -u +%T)" >> $ST
    snap after-t1
  fi
  curl -sf -m 5 localhost:$P/health >/dev/null && echo "ALIVE $ARM" >> $ST || echo "DOWN $ARM" >> $ST
  stop
done
echo DONE >> $ST
