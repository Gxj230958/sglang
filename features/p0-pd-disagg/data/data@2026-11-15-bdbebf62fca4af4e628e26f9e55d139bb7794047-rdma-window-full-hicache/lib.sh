R=/scratch/cc-regate2; M=/scratch/models/GLM-5-1028-Provider
COMMON="--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report --host 0.0.0.0 --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum --disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0"
killall_sgl() { tmux kill-server 2>/dev/null; sleep 6; for p in $(pgrep -f "sglang[.]launch_server|sglang::|sglang_router"); do kill -9 $p 2>/dev/null; done; sleep 8; }
# serve <leg> <role prefill|decode> <port> <swa 0|1> [extra flags...]
serve() {
  local LEG=$1 ROLE=$2 PORT=$3 SWA=$4; shift 4; local L=$R/logs/$LEG-$ROLE; mkdir -p $L
  { echo "export PYTHONPATH=$R/overlay:/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:$R/src-pd/python"
    echo "export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python"; [ "$SWA" = 1 ] && echo "export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1"
    echo "export SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=$R/hicache-store"; echo "cd $R/src-pd"
    echo "exec python3 -m sglang.launch_server --model-path $M --port $PORT $COMMON --disaggregation-mode $ROLE $*"; } > $L/launch.sh
  tmux new -d -s $ROLE "bash $L/launch.sh 2>&1 | tee $L/serve.log"
  for i in $(seq 1 480); do curl -sf -m 3 localhost:$PORT/health >/dev/null && { echo READY; return 0; }; tmux has-session -t $ROLE 2>/dev/null || { echo DEAD; return 1; }; sleep 5; done; echo TIMEOUT; return 2
}
