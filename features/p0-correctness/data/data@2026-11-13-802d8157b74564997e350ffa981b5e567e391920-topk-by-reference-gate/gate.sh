#!/bin/bash
L=/scratch/kimi-pr43-final; ST=$L/gate.status; : > $ST
export HF_HOME=/scratch/cc-pr43/hf-home
ready=0
for i in $(seq 1 240); do
  curl -sf -m 3 localhost:31743/health >/dev/null && { ready=1; break; }
  kill -0 $(cat $L/server.pid) 2>/dev/null || break
  sleep 10
done
[ $ready -eq 1 ] || { echo "NOT_READY" >> $ST; echo DONE >> $ST; exit 1; }
echo "READY $(date -u +%H:%M:%S)" >> $ST
/opt/sglang/bin/python /scratch/cc-pr43/box/suite.py $L/suite.json smoke > $L/suite.log 2>&1
echo "suite rc=$? $(date -u +%H:%M:%S)" >> $ST
/opt/sglang/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:31743/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/eval > $L/gsm8k.log 2>&1
echo "gsm8k rc=$? $(date -u +%H:%M:%S)" >> $ST
curl -sf -m 5 localhost:31743/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
echo DONE >> $ST
