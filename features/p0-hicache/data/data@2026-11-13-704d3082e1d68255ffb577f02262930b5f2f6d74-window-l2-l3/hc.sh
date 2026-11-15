source /scratch/cc-regate/lib.sh
N=hc-swa; L=$R/logs/$N; mkdir -p $L; ST=$L/status; : > $ST; B=http://127.0.0.1:30000/v1
rm -rf $R/hicache-store; mkdir -p $R/hicache-store
HC="--host 127.0.0.1 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --enable-hierarchical-cache --hicache-size 64 --hicache-storage-backend file"
serve $N hc 30000 "SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=$R/hicache-store" $HC
waitready $N 30000 || { echo NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
echo "READY $(date -u +%T)" >> $ST
python3 /scratch/cc-swa/bin/midfork.py $B $L/midfork-a.json m2 > $L/midfork-a.log 2>&1
python3 /scratch/cc-swa/bin/hicache.py $B $L/anchor.json fill 70 l2fill2 > $L/fill2.log 2>&1
grep -c 'HiCache prefetch success' $L/serve.log > $L/prefetch-before-b.txt
python3 /scratch/cc-swa/bin/midfork.py $B $L/midfork-b.json m2 > $L/midfork-b.log 2>&1
grep -c 'HiCache prefetch success' $L/serve.log > $L/prefetch-after-b.txt
echo "l2 done $(date -u +%T)" >> $ST
gsm8k $N 30000; echo "gsm8k rc=$? $(date -u +%T)" >> $ST
curl -sf -m 5 localhost:30000/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
stop $N
N2=hc-l3; L2=$R/logs/$N2; mkdir -p $L2
serve $N2 hc 30000 "SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=$R/hicache-store" $HC
waitready $N2 30000 || { echo L3_NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
python3 /scratch/cc-swa/bin/midfork.py $B $L2/midfork-c.json m2 > $L2/midfork-c.log 2>&1
echo "l3 done $(date -u +%T)" >> $ST
stop $N2; echo DONE >> $ST
