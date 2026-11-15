# usage: serve.sh <run-name> <tree> <config: tp8|dep8>
set -u
NAME=$1; TREE=$2; CFG=$3
R=/scratch/cc-pr43; L=$R/logs/$NAME; mkdir -p $L/mem
M=/scratch/models/GLM-5-1028-Provider
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M"
case $CFG in
  tp8) FLAGS="--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph" ;;
  dep8) FLAGS="--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head" ;;
esac
cat > $L/launch.sh <<EOS
export PYTHONPATH=$R/src-$TREE/python:$R/overlay
export HF_HOME=$R/hf-home
export GLMVAL_MEMLOG=$L/mem
cd $R/src-$TREE
exec /opt/sglang/bin/python -m sglang.launch_server --model-path $M --host 127.0.0.1 --port 31743 $FLAGS $MTP --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47
EOS
tmux kill-session -t ccpr43 2>/dev/null || true
tmux new -d -s ccpr43 "bash $L/launch.sh 2>&1 | tee $L/serve.log"
echo "started $NAME tree=$TREE cfg=$CFG"
