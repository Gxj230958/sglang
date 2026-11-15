source /scratch/cc-regate/lib.sh
N=pd-d; L=$R/logs/$N; mkdir -p $L; : > $L/status
serve $N pd 30001 "" --host 0.0.0.0 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum --disaggregation-mode decode --disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0
waitready $N 30001 && echo "READY $(date -u +%T)" >> $L/status || echo NOT_READY >> $L/status
