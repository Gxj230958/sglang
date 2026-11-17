#!/bin/bash
# PD router (rank0) in front of one prefill and one decode server.
source $WORK/pd_env.sh
exec /opt/sglang/bin/python -m sglang_router.launch_router --host 0.0.0.0 --port 32022 --pd-disaggregation \
  --prefill http://$P_IP:32020 32023 --decode http://$D_IP:32021 --request-timeout-secs 7200 --prometheus-port 32026
