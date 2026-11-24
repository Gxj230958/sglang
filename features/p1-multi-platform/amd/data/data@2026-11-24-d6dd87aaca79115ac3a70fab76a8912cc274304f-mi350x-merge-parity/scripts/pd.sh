#!/bin/bash
# pd.sh: 1P1D on one node. Prefill TP4 (GPUs 0-3, :30000), decode TP4 (GPUs 4-7, :30001), Mooncake over TCP,
# MTP on both, sglang_router on :8000; then smoke + capped GSM8K through the router.
cd /scratch/mobius/mi350x; ST=/scratch/mobius/mi350x/acc/matrix.status; echo "=== pd-tp4 $(date +%T)" >> $ST
M=/scratch/hf_home/hub/models--RadixArk--GLM-5-1028-Provider/snapshots/9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report"
COMMON="--tp-size 4 --mem-fraction-static 0.85 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --disaggregation-transfer-backend mooncake $MTP"
export MOONCAKE_PROTOCOL=tcp
HIP_VISIBLE_DEVICES=0,1,2,3 setsid nohup scripts/launch.sh 30000 $COMMON --disaggregation-mode prefill > logs/pd-prefill.log 2>&1 < /dev/null & echo $! > logs/pd-prefill.pid
HIP_VISIBLE_DEVICES=4,5,6,7 setsid nohup scripts/launch.sh 30001 $COMMON --disaggregation-mode decode > logs/pd-decode.log 2>&1 < /dev/null & echo $! > logs/pd-decode.pid
scripts/wait_ready.sh pd-prefill 30000 > logs/pd-prefill.ready.txt 2>&1; head -1 logs/pd-prefill.ready.txt | sed 's/^/pd prefill startup: /' >> $ST
scripts/wait_ready.sh pd-decode 30001 > logs/pd-decode.ready.txt 2>&1; head -1 logs/pd-decode.ready.txt | sed 's/^/pd decode startup: /' >> $ST
if grep -q READY logs/pd-prefill.ready.txt && grep -q READY logs/pd-decode.ready.txt; then
  setsid nohup /opt/venv/bin/python -m sglang_router.launch_router --pd-disaggregation --prefill http://127.0.0.1:30000 8998 --decode http://127.0.0.1:30001 --request-timeout-secs 7200 --host 127.0.0.1 --port 8000 > logs/pd-router.log 2>&1 < /dev/null & echo $! > logs/pd-router.pid
  for i in $(seq 60); do curl -sf -o /dev/null http://127.0.0.1:8000/health && break; sleep 2; done
  scripts/acc_suite.sh pd-tp4 8000 smoke gsm8k >> $ST 2>&1
fi
for n in pd-router pd-prefill pd-decode; do P=$(cat logs/$n.pid); kill -TERM -- -$P 2>/dev/null; done
for n in pd-prefill pd-decode; do P=$(cat logs/$n.pid); while pgrep -g $P >/dev/null; do sleep 2; done; done
echo "=== PD DONE $(date +%T)" >> $ST
