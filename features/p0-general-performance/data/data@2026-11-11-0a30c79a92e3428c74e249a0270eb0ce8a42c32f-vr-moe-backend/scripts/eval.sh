#!/bin/bash
export PYTHONPATH=${SRCDIR:-/nfs_home/glm5-lcd/src/python}
echo "=== GSM8K $ARM $(date +%T)"
python3 -m sglang.test.few_shot_gsm8k --data-path /nfs_home/gsm8k_test.jsonl --num-questions 1319 --parallel 32 --host $MASTER_ADDR --port 30701 2>&1 | grep -v "^\s*$" | tail -12
echo "=== ACCEPT"; grep "Decode batch" $RUN/server-0.log | grep -oE "accept len: [0-9.]+" | awk "{s+=\$3; n++} END {print \"mean accept len\", s/n, \"over\", n, \"lines\"}"
grep -o "moe_runner_backend. *: *.[a-z_]*." $RUN/server-0.log | sort | uniq -c
echo EVAL_DONE
