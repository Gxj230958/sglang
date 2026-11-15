#!/bin/bash
# usage: eval.sh <run-name> <port> [extra sgl-eval args]
NAME=$1; PORT=$2; shift 2
L=/scratch/cc-swa/logs/$NAME
/scratch/cc-swa/bin/wait.sh $NAME $PORT 360 > $L/wait.log 2>&1 || { echo EVAL_ABORTED > $L/eval.status; exit 1; }
/scratch/cc-swa/evalenv/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:$PORT/v1 --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $L/eval "$@" > $L/gsm8k.log 2>&1
echo "EVAL_DONE rc=$?" > $L/eval.status
