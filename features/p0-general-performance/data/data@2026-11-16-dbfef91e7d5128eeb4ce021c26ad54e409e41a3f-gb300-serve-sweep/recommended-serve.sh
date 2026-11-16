#!/usr/bin/env bash
set -eu
export CUDA_VISIBLE_DEVICES=0,1,2,3
export PYTHONPATH=/scratch/cc-regate2/overlay:/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:/scratch/codex-serve-sweep/src/python
export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
exec python3 -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port 31080 --dist-init-addr 127.0.0.1:31120 --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --chunked-prefill-size 8192 --enable-fp32-lm-head --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report --enable-metrics --tp-size 4 --moe-runner-backend deep_gemm
