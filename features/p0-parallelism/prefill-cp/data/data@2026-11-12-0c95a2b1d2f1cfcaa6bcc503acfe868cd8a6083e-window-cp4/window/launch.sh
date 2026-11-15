export PYTHONPATH=/scratch/cc-swa/fi073:/scratch/kimi-glm42-repro/packages:/scratch/cc-swa/src-cp/python
export CUDA_VISIBLE_DEVICES=0,1,2,3
export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python
export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1
export SGLANG_JIT_DEEPGEMM_PRECOMPILE=0
cd /scratch/cc-swa/src-cp
exec python3 -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port 30000 --tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path /scratch/models/GLM-5-1028-Provider --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report
