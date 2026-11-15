#!/bin/bash
# usage: wait.sh <run-name> <port> <max-iters>
L=/scratch/cc-swa/logs/$1
for i in $(seq 1 $3); do
  curl -sf -m 3 localhost:$2/health >/dev/null && { echo READY; exit 0; }
  tmux has-session -t $1 2>/dev/null || { echo DEAD; tail -60 $L/serve.log; exit 1; }
  sleep 5
done
echo TIMEOUT; tail -30 $L/serve.log; exit 2
