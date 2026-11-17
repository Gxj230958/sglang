# Shared PD settings: P on rank0 (<PREFILL_NODE_IP>), D on rank1 (<DECODE_NODE_IP>).
export WORK=$WORK
FI=$FLASHINFER_074; [ -d $FI ] || FI=$WORK/fi074
export PYTHONPATH=$FI:$KERNEL_OVERLAY:$FLASH_MLA_103:$WORK/src/python
export MODEL=$MODEL_PATH
export P_IP=<PREFILL_NODE_IP> D_IP=<DECODE_NODE_IP>
export IB_DEVICES=ibp0p0,ibp1p0,ibp2p0,ibp3p0
export MOONCAKE_MASTER=$P_IP:8700
export MOONCAKE_TE_META_DATA_SERVER=http://$P_IP:8701/metadata
export MC_ENABLE_DEST_DEVICE_AFFINITY=1
COMMON=(--model-path $MODEL --served-model-name glm-loop --trust-remote-code
  --moe-runner-backend flashinfer_trtllm --disable-shared-experts-fusion
  --kv-cache-dtype bf16 --dsa-prefill-backend flashmla_sparse --dsa-decode-backend flashmla_sparse
  --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
  --speculative-draft-model-path $MODEL --speculative-draft-model-quantization fp8
  --mem-fraction-static 0.80 --context-length 147456 --chunked-prefill-size 8192 --disable-prefill-cuda-graph
  --enable-fp32-lm-head --reasoning-parser glm45 --tool-call-parser glm47 --random-seed 1
  --enable-cache-report --enable-metrics
  --disaggregation-transfer-backend mooncake --disaggregation-ib-device $IB_DEVICES --disaggregation-bootstrap-port 32023)
# Decode-saturation runs queue requests at D longer than the 300 s defaults; queueing shows as TTFT, not errors.
export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=${PD_TIMEOUT:-3600} SGLANG_DISAGGREGATION_WAITING_TIMEOUT=${PD_TIMEOUT:-3600}
