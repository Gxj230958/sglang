#!/bin/bash
# Prefill (rank0): TP4, radix cache + Mooncake store linker.
source $WORK/pd_env.sh
export MOONCAKE_PROTOCOL=rdma MOONCAKE_DEVICE=$IB_DEVICES MOONCAKE_GLOBAL_SEGMENT_SIZE=140gb
export MOONCAKE_LOCAL_HOSTNAME=$P_IP MC_TCP_BIND_ADDRESS=$P_IP MOONCAKE_STANDALONE_STORAGE=0
exec /opt/sglang/bin/python -m sglang.launch_server "${COMMON[@]}" --host 0.0.0.0 --port 32020 \
  --dist-init-addr 127.0.0.1:32024 --tp-size 4 --max-running-requests 64 --cuda-graph-max-bs-decode 64 \
  --disaggregation-mode prefill \
  --enable-unified-cache-external-linker --unified-cache-external-linker-backend mooncake \
  --hicache-storage-backend-extra-config '{"enable_group_semantics":true}' "$@"
