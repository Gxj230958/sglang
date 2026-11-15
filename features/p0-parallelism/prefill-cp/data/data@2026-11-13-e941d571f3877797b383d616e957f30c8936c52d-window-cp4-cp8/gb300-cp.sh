source /scratch/cc-regate/lib.sh
N=cp-swa; L=$R/logs/$N; mkdir -p $L; ST=$L/status; : > $ST
serve $N cp 30000 "SGLANG_JIT_DEEPGEMM_PRECOMPILE=0" --host 127.0.0.1 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable
waitready $N 30000 || { echo NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
echo "READY $(date -u +%T)" >> $ST
python3 /scratch/cc-swa/bin/probe.py http://127.0.0.1:30000/v1 $L/probe.json 300 3000 9000 24000 60000 120000 > $L/probe.log 2>&1; echo "probe rc=$? $(date -u +%T)" >> $ST
gsm8k $N 30000; echo "gsm8k rc=$? $(date -u +%T)" >> $ST
curl -sf -m 5 localhost:30000/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
stop $N; echo DONE >> $ST
