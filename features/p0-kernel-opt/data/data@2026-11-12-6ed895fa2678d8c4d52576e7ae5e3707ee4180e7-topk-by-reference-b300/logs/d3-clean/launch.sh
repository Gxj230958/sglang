export PYTHONPATH=/scratch/cc-pr43/src-clean/python:/scratch/cc-pr43/overlay
export HF_HOME=/scratch/cc-pr43/hf-home
export GLMVAL_MEMLOG=/scratch/cc-pr43/logs/d3-clean/mem
cd /scratch/cc-pr43/src-clean
exec /opt/sglang/bin/python -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port 31743 --tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path /scratch/models/GLM-5-1028-Provider --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47
