#!/bin/bash
# Decode (rank1): DPA4 + EP4; HS=1 adds HiSparse.
source $WORK/pd_env.sh
export MOONCAKE_LOCAL_HOSTNAME=$D_IP
HSARGS=()
if [ "${HS:-0}" = 1 ]; then
  HSARGS=(--enable-hisparse --hisparse-config "{\"top_k\":2048,\"device_buffer_size\":${DBS:-4096},\"host_to_device_ratio\":${RATIO:-8}}")
fi
exec /opt/sglang/bin/python -m sglang.launch_server "${COMMON[@]}" --host 0.0.0.0 --port 32021 \
  --dist-init-addr 127.0.0.1:32025 --tp-size 4 --dp-size 4 --enable-dp-attention --ep-size 4 \
  --max-running-requests ${MAXREQ:-256} --cuda-graph-max-bs-decode ${GRAPHBS:-32} \
  --disaggregation-mode decode "${HSARGS[@]}" "$@"
