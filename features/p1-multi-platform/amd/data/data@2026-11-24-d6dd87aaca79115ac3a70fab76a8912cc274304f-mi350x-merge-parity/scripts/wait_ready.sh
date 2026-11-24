#!/bin/bash
# wait_ready.sh <name> [port]: exits when /health is 200, the server dies, the log shows an error, or the log is silent 300 s.
NAME=$1; PORT=${2:-30000}; L=/scratch/mobius/mi350x/logs/$NAME.log; P=$(cat /scratch/mobius/mi350x/logs/$NAME.pid); start=$(date +%s); last=0; lastt=$start
while true; do
  if curl -sf -o /dev/null http://127.0.0.1:$PORT/health; then echo READY; break; fi
  if ! kill -0 $P 2>/dev/null; then echo "SERVER EXITED"; break; fi
  if grep -qE "Traceback|out of memory|HSA_STATUS_ERROR" $L; then echo "ERROR IN LOG"; break; fi
  sz=$(stat -c %s $L); now=$(date +%s)
  [ $sz != $last ] && { last=$sz; lastt=$now; }
  [ $((now-lastt)) -gt ${STALL_S:-900} ] && { echo "STALL: log silent ${STALL_S:-900}s"; break; }
  [ $((now-start)) -gt 2400 ] && { echo "TIMEOUT"; break; }
  sleep 5
done
echo "elapsed $(( $(date +%s)-start ))s"
grep -E "DSA backends|Load weight end|KV Cache is allocated|graph end|hybrid|swa|window" $L | grep -E "TP0|DSA" | tail -8 | cut -c1-260
grep -n -A25 "Traceback" $L | tail -40 | cut -c1-260
tail -3 $L | cut -c1-260
