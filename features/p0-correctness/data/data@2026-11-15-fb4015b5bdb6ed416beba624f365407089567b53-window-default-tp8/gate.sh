#!/bin/bash
R=/scratch/cc-merge; L=$R/logs; mkdir -p $L; ST=$R/status; : > $ST; M=/scratch/models/GLM-5-1028-Provider
BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
[ "$BUSY" -ne 0 ] && { echo GPU_BUSY_FOREIGN >> $ST; echo DONE >> $ST; exit 3; }
{ echo "export PYTHONPATH=/scratch/cc-merge/overlay:/scratch/cc-pr43/overlay:$R/src/python"; echo "export HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python"; echo "cd $R/src"
  echo "exec /opt/sglang/bin/python -m sglang.launch_server --model-path $M --host 127.0.0.1 --port 31745 --tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47"; } > $L/launch.sh
tmux kill-session -t ccmerge 2>/dev/null; tmux new -d -s ccmerge "bash $L/launch.sh 2>&1 | tee $L/serve.log"
ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:31745/health >/dev/null && { ok=1; break; }; tmux has-session -t ccmerge 2>/dev/null || break; sleep 10; done
if [ $ok -eq 1 ]; then echo "READY $(date -u +%T)" >> $ST
  export HF_HOME=/scratch/cc-pr43/hf-home
  sed "s/31743/31745/g" /scratch/cc-pr43/box/suite.py > $R/suite.py
  /opt/sglang/bin/python $R/suite.py $L/suite.json smoke > $L/suite.log 2>&1; echo "suite rc=$? $(date -u +%T)" >> $ST
  /opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:31745/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/eval > $L/gsm8k.log 2>&1; echo "gsm8k rc=$? $(date -u +%T)" >> $ST
  curl -sf -m 5 localhost:31745/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
else echo "NOT_READY $(date -u +%T)" >> $ST; fi
tmux kill-session -t ccmerge 2>/dev/null; sleep 10; for p in $(pgrep -f "port 31745|sglang::"); do kill -9 $p 2>/dev/null; done
echo DONE >> $ST
