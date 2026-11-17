#!/bin/bash
# After the ratio-6 chain, rerun decode saturation with a larger host pool (ratio 12).
W=$WORK
cd $W
until grep -q -E "DEC_AB_DONE|DEC_AB_FAILED" logs/dec_ab.out; do sleep 60; done
P=$(ps -eo pid,args | grep -E "launch_server.*--port 32021" | grep -v grep | head -1 | awk "{print \$1}")
kill -- -$(ps -o pgid= $P | tr -d " ")
for i in $(seq 60); do sleep 5; [ $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l) = 0 ] && break; done
HS=1 RATIO=12 DBS=4096 setsid nohup ./pd_decode.sh > logs/pd_decode_hs12.log 2>&1 < /dev/null &
until grep -q -E "fired up|Traceback" logs/pd_decode_hs12.log; do sleep 20; done
grep -q Traceback logs/pd_decode_hs12.log && { echo DEC_R12_FAILED; exit 1; }
until curl -s -m5 http://<PREFILL_NODE_IP>:32022/workers | grep -q "\"worker_type\":\"decode\",\"is_healthy\":true"; do sleep 10; done
WARMUP=1 OSL=4096 ./agentx_run.sh pd_hs12 48 900
WARMUP=1 OSL=4096 ./agentx_run.sh pd_hs12 64 900
echo DEC_R12_DONE
