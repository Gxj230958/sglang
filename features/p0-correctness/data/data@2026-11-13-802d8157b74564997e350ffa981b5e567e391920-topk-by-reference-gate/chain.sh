#!/bin/bash
L=/scratch/kimi-pr43-final; ST=$L/chain.status; : > $ST
export HF_HOME=/scratch/cc-pr43/hf-home
ev() { /opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:31743/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/$1 > $L/$1.log 2>&1; echo "$1 rc=$? $(date -u +%T)" >> $ST; }
ev eval-cand2
kill $(cat $L/server.pid); sleep 20; pkill -9 -f sglang.launch_server; pkill -9 -f "sglang::"; sleep 10
mkdir -p $L/base && tar -xzf $L/base.tar.gz -C $L/base
sed -e "s#$L/source/python#$L/base/python#" -e "s#serve.log#serve-base.log#" -e "s#server.pid#server-base.pid#" $L/launch.sh > $L/launch-base.sh
bash $L/launch-base.sh
ready=0; for i in $(seq 1 240); do curl -sf -m 3 localhost:31743/health >/dev/null && { ready=1; break; }; kill -0 $(cat $L/server-base.pid) 2>/dev/null || break; sleep 10; done
[ $ready -eq 1 ] || { echo BASE_NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
echo "BASE_READY $(date -u +%T)" >> $ST
ev eval-base1
ev eval-base2
kill $(cat $L/server-base.pid); sleep 20; pkill -9 -f sglang.launch_server; pkill -9 -f "sglang::"
echo DONE >> $ST
