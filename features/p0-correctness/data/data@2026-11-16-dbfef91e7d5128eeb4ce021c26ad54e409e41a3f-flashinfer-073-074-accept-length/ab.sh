#!/bin/bash
R=/scratch/cc-fiab; ST=$R/status; : > $ST; M=/scratch/models/GLM-5-1028-Provider; S=/scratch/codex-fi074/src; P=31746
export HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
PY=/opt/sglang/bin/python
stop() { tmux kill-session -t ccfiab 2>/dev/null; sleep 10; for p in $(pgrep -f "port $P"); do kill -9 $p 2>/dev/null; done; sleep 25; }
snap() { curl -s -m 20 localhost:$P/metrics | grep -E "^sglang:(generation_tokens_total|spec_verify_calls_total)" > $L/$1.metrics; }
for ARM in fi073 fi074; do
  L=$R/$ARM; mkdir -p $L
  if [ $ARM = fi073 ]; then OV=/scratch/cc-merge/overlay:/scratch/cc-pr43/overlay; else OV=/scratch/codex-fi074/overlay; fi
  export PYTHONPATH=$OV:$S/python
  BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
  [ "$BUSY" -ne 0 ] && { echo "GPU_BUSY $ARM" >> $ST; break; }
  (cd $S && $PY -c "import flashinfer, sglang, importlib.metadata as m; print(flashinfer.__file__, flashinfer.__version__, sglang.__file__, [(k, m.version(k)) for k in ('flashinfer-python','flashinfer-cubin','flashinfer-jit-cache','sglang-kernel','sgl-deep-gemm','sgl-flash-mla','kernels')])") > $L/imports.txt 2>&1
  echo "cd $S; export PYTHONPATH=$PYTHONPATH; exec $PY -m sglang.launch_server --model-path $M --host 127.0.0.1 --port $P --tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics" > $L/launch.sh
  tmux kill-session -t ccfiab 2>/dev/null; tmux new -d -s ccfiab "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  ok=0; for i in $(seq 1 360); do curl -sf -m 3 localhost:$P/health >/dev/null && { ok=1; break; }; tmux has-session -t ccfiab 2>/dev/null || break; sleep 10; done
  [ $ok -eq 1 ] || { echo "NOT_READY $ARM $(date -u +%T)" >> $ST; stop; continue; }
  echo "READY $ARM $(date -u +%T)" >> $ST
  for T in t1 t0; do
    if [ $T = t1 ]; then SA="--temperature 1.0 --top-p 0.95"; else SA="--temperature 0"; fi
    snap before-$T
    /opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:$P/v1 $SA --out-dir $L/eval-$T > $L/gsm8k-$T.log 2>&1; echo "$ARM gsm8k $T rc=$? $(date -u +%T)" >> $ST
    snap after-$T
  done
  curl -sf -m 5 localhost:$P/health >/dev/null && echo "ALIVE $ARM" >> $ST || echo "DOWN $ARM" >> $ST
  stop
done
echo DONE >> $ST
