R=/scratch/cc-regate; M=/scratch/models/GLM-5-1028-Provider
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report"
# serve <name> <tree> <port> "<ENV=V ...>" <flags...>
serve() {
  local NAME=$1 TREE=$2 PORT=$3 ENVS=$4; shift 4
  local L=$R/logs/$NAME; mkdir -p $L
  {
    echo "export PYTHONPATH=/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:$R/src-$TREE/python"
    echo "export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python"
    echo "export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1"
    for e in $ENVS; do echo "export $e"; done
    echo "cd $R/src-$TREE"
    echo "exec python3 -m sglang.launch_server --model-path $M --port $PORT $* $MTP"
  } > $L/launch.sh
  tmux kill-session -t $NAME 2>/dev/null
  tmux new -d -s $NAME "bash $L/launch.sh 2>&1 | tee $L/serve.log"
}
# waitready <name> <port>
waitready() {
  for i in $(seq 1 480); do
    curl -sf -m 3 localhost:$2/health >/dev/null && return 0
    tmux has-session -t $1 2>/dev/null || return 1
    sleep 5
  done; return 2
}
stop() { tmux kill-session -t $1 2>/dev/null; sleep 8; pkill -9 -f sglang.launch_server; pkill -9 -f "sglang::" ; sleep 5; }
gsm8k() { /scratch/cc-swa/evalenv/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:$2/v1 --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $R/logs/$1/eval > $R/logs/$1/gsm8k.log 2>&1; }
