source /scratch/cc-regate/lib.sh
N=cp-long; L=$R/logs/$N; mkdir -p $L; ST=$L/status; : > $ST
serve $N cp 30000 "SGLANG_JIT_DEEPGEMM_PRECOMPILE=0" --host 127.0.0.1 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable
if waitready $N 30000; then python3 /scratch/cc-swa/bin/probe.py http://127.0.0.1:30000/v1 $L/probe.json 110000 > $L/probe.log 2>&1; echo "probe rc=$? $(date -u +%T)" >> $ST; else echo NOT_READY >> $ST; fi
stop $N; echo DONE >> $ST
bash /scratch/cc-regate/pd-p.sh
