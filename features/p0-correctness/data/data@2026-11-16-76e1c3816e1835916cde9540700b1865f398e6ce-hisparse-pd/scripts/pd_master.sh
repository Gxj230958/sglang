#!/bin/bash
# Mooncake store master for the prefill linker (rank0).
exec /opt/sglang/bin/mooncake_master --port 8700 --enable_http_metadata_server true --http_metadata_server_port 8701 \
  --default_kv_lease_ttl 10000 --rpc_thread_num 16 --eviction_high_watermark_ratio 0.90
