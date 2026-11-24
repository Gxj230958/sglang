#!/bin/bash
# GLM-5-1028-Provider on 8x MI355X. Usage: launch.sh <port> [extra sglang args...]
set -euo pipefail
ulimit -c 0  # core_pattern pipes to host apport; a 300 GB-virtual rank dump stalls the node
PORT=${1:-30000}; shift || true
export PATH=/opt/venv/bin:$PATH
export PYTHONPATH=/path/to/sglang-zai/python
export HF_HUB_OFFLINE=1
export SGLANG_USE_AITER=${SGLANG_USE_AITER:-1}
exec python -m sglang.launch_server \
  --model-path "${MODEL:-/path/to/GLM-5-1028-Provider}" \
  --served-model-name glm-loop \
  --host 0.0.0.0 --port "$PORT" \
  --tp-size 8 \
  --kv-cache-dtype bfloat16 \
  --mem-fraction-static 0.80 \
  --context-length 32768 --max-running-requests 64 \
  --chunked-prefill-size 16384 \
  --watchdog-timeout 1800 \
  --reasoning-parser glm45 --tool-call-parser glm47 \
  "$@"
