#!/bin/bash
R=/scratch/cc-speed; ST=$R/status-tp8; : > $ST; M=/scratch/models/GLM-5-1028-Provider; S=/scratch/cc-merge/src; P=31745
export PYTHONPATH=/scratch/cc-merge/overlay:/scratch/cc-pr43/overlay:$S/python HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
PY=/opt/sglang/bin/python
stop() { tmux kill-session -t ccspeed 2>/dev/null; sleep 10; for p in $(pgrep -f "port $P|sglang::"); do kill -9 $p 2>/dev/null; done; sleep 20; }
bench() {
  $PY -m sglang.bench_serving --backend sglang --host 127.0.0.1 --port $P --model $M --dataset-name random-ids --random-input-len $2 --random-output-len $3 --random-range-ratio 1 --num-prompts $4 --max-concurrency $5 --seed $6 --flush-cache --warmup-requests 2 --output-file $L/$1-s$6.jsonl > $L/$1-s$6.log 2>&1
  echo "$ARM $1 seed=$6 rc=$? $(date -u +%T)" >> $ST; }
for ARM in tp8-window-r2; do
  L=$R/$ARM; mkdir -p $L; FLAG=""; [ $ARM = tp8-full ] && FLAG="--disable-hybrid-swa-memory"
  BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
  [ "$BUSY" -ne 0 ] && { echo "GPU_BUSY $ARM" >> $ST; break; }
  echo "cd $S; exec $PY -m sglang.launch_server --model-path $M --host 127.0.0.1 --port $P --tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 $FLAG" > $L/launch.sh
  tmux kill-session -t ccspeed 2>/dev/null; tmux new -d -s ccspeed "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:$P/health >/dev/null && { ok=1; break; }; tmux has-session -t ccspeed 2>/dev/null || break; sleep 10; done
  [ $ok -eq 1 ] || { echo "NOT_READY $ARM $(date -u +%T)" >> $ST; stop; break; }
  echo "READY $ARM $(date -u +%T)" >> $ST
  for seed in 1 2; do
    bench short-c1 2000 500 16 1 $seed
    bench short-c32 2000 500 128 32 $seed
    bench long-c4 30000 300 16 4 $seed
    for th in 1 4; do
      curl -s -m 60 -X POST localhost:$P/flush_cache > /dev/null; sleep 3
      $PY $R/mt.py http://127.0.0.1:$P/v1 $L/mt-t$th-s$seed.jsonl 8 8 $th mt-$th-$seed > $L/mt-t$th-s$seed.log 2>&1; echo "$ARM mt th=$th seed=$seed rc=$? $(date -u +%T)" >> $ST
    done
  done
  curl -sf -m 5 localhost:$P/health >/dev/null && echo "ALIVE $ARM" >> $ST || echo "DOWN $ARM" >> $ST
  stop
done
echo DONE >> $ST
