export PYTHONPATH=/scratch/cc-pr43/src-base/python:/scratch/cc-pr43/overlay
export HF_HOME=/scratch/cc-pr43/hf-home
export GLMVAL_MEMLOG=/scratch/cc-pr43/logs/r3-base/mem
cd /scratch/cc-pr43/src-base
exec /opt/sglang/bin/python -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --host 127.0.0.1 --port 31743 --tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path /scratch/models/GLM-5-1028-Provider --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47
