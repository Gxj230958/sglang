#!/bin/bash
# After the baseline decode-saturation chain, switch D to HiSparse and run the same chain.
W=$WORK
cd $W
until grep -q "AGENTX_DONE pd_base 4 4096" logs/agentx_dec_base.out; do sleep 60; done
P=$(ps -eo pid,args | grep -E "launch_server.*--port 32021" | grep -v grep | head -1 | awk "{print \$1}")
kill -- -$(ps -o pgid= $P | tr -d " ")
for i in $(seq 60); do sleep 5; [ $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l) = 0 ] && break; done
HS=1 RATIO=6 DBS=4096 setsid nohup ./pd_decode.sh > logs/pd_decode_hs_dec.log 2>&1 < /dev/null &
until grep -q -E "fired up|Traceback" logs/pd_decode_hs_dec.log; do sleep 20; done
grep -q Traceback logs/pd_decode_hs_dec.log && { echo DEC_AB_FAILED; exit 1; }
until curl -s -m5 http://<PREFILL_NODE_IP>:32022/workers | grep -q "\"worker_type\":\"decode\",\"is_healthy\":true"; do sleep 10; done
WARMUP=1 OSL=4096 ./agentx_run.sh pd_hs 48 900
WARMUP=1 OSL=4096 ./agentx_run.sh pd_hs 8 900
WARMUP=1 OSL=4096 ./agentx_run.sh pd_hs 4 900
echo DEC_AB_DONE
