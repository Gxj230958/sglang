export PYTHONPATH=/scratch/cc-pr43/overlay:/scratch/cc-combo/src/python
export HF_HOME=/scratch/cc-pr43/hf-home HF_HUB_CACHE=/scratch/cc-pr43/hf-home
export SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1
export SGLANG_JIT_DEEPGEMM_PRECOMPILE=0
cd /scratch/cc-combo/src
exec /opt/sglang/bin/python -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port 31744 --tp-size 8 --mem-fraction-static 0.75 --context-length 131072 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 8 --cuda-graph-backend-prefill breakable --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path /scratch/models/GLM-5-1028-Provider --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47
