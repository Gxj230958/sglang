#!/bin/bash
# usage: serve.sh <run-name> <source-tree> <port> <gpus> -- <extra env KEY=VAL ...> -- <launch flags...>
set -u
NAME=$1; TREE=$2; PORT=$3; GPUS=$4; shift 4
[ "$1" = "--" ] && shift
ENVS=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do ENVS+=("$1"); shift; done
[ $# -gt 0 ] && shift
L=/scratch/cc-swa/logs/$NAME; mkdir -p $L
{
  echo "export PYTHONPATH=/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:$TREE/python"
  echo "export CUDA_VISIBLE_DEVICES=$GPUS"
  echo "export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python"
  for e in "${ENVS[@]}"; do echo "export $e"; done
  echo "cd $TREE"
  echo "exec python3 -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port $PORT $*"
} > $L/launch.sh
tmux kill-session -t $NAME 2>/dev/null || true
tmux new -d -s $NAME "bash $L/launch.sh 2>&1 | tee $L/serve.log"
echo "started $NAME"; cat $L/launch.sh
