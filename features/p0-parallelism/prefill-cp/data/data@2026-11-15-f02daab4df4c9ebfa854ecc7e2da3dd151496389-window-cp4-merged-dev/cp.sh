R=/scratch/cc-regate2; M=/scratch/models/GLM-5-1028-Provider; N=cp-swa; L=$R/logs/$N; mkdir -p $L; ST=$L/status; : > $ST
BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l); [ "$BUSY" -ne 0 ] && { echo GPU_BUSY_FOREIGN >> $ST; echo DONE >> $ST; exit 3; }
{ echo "export PYTHONPATH=$R/overlay:/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:$R/src-cp/python"
  echo "export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1 SGLANG_JIT_DEEPGEMM_PRECOMPILE=0"; echo "cd $R/src-cp"
  echo "exec python3 -m sglang.launch_server --model-path $M --host 127.0.0.1 --port 30000 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report"; } > $L/launch.sh
tmux kill-session -t $N 2>/dev/null; tmux new -d -s $N "bash $L/launch.sh 2>&1 | tee $L/serve.log"
ok=0; for i in $(seq 1 480); do curl -sf -m 3 localhost:30000/health >/dev/null && { ok=1; break; }; tmux has-session -t $N 2>/dev/null || break; sleep 5; done
if [ $ok -eq 1 ]; then echo "READY $(date -u +%T)" >> $ST
  python3 /scratch/cc-swa/bin/probe.py http://127.0.0.1:30000/v1 $L/probe.json 300 3000 9000 24000 60000 110000 > $L/probe.log 2>&1; echo "probe rc=$? $(date -u +%T)" >> $ST
  python3 /scratch/cc-swa/bin/midfork.py http://127.0.0.1:30000/v1 $L/midfork.json g2 > $L/midfork.log 2>&1; echo "midfork rc=$? $(date -u +%T)" >> $ST
  /scratch/cc-swa/evalenv/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:30000/v1 --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $L/eval > $L/gsm8k.log 2>&1; echo "gsm8k rc=$? $(date -u +%T)" >> $ST
  curl -sf -m 5 localhost:30000/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
else echo "NOT_READY $(date -u +%T)" >> $ST; fi
tmux kill-session -t $N 2>/dev/null; sleep 8; for p in $(pgrep -f "sglang[.]launch_server|sglang::"); do kill -9 $p 2>/dev/null; done
echo DONE >> $ST
