export PYTHONPATH=/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:/scratch/cc-regate/src-pd/python
export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1
cd /scratch/cc-regate/src-pd
exec python3 -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --port 30000 --host 0.0.0.0 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum --disaggregation-mode prefill --disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0 --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path /scratch/models/GLM-5-1028-Provider --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report
