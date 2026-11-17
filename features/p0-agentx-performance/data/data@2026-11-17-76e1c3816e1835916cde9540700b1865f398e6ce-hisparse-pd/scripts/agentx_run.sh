#!/bin/bash
# AgentX closed-loop replay against the PD router. Usage: agentx_run.sh <tag> <concurrency> [duration_s]
set -u
# separate_reasoning=false: a max_tokens=1 warmup reply of </think> would otherwise be parsed away and read as empty.
TAG=$1 CONC=$2 DUR=${3:-900}
# OSL set: every turn decodes OSL tokens, so the replay saturates decode.
EXTRA="{\"separate_reasoning\": false${OSL:+, \"max_completion_tokens\": $OSL}}"
OUT_SUFFIX=${OSL:+-osl$OSL}
# Keep prompt + OSL inside the served context length.
MAXCTX=$((147456 - ${OSL:-0}))
W=$WORK
OUT=$W/agentx/$TAG-c$CONC$OUT_SUFFIX
mkdir -p $OUT
export HF_HOME=$W/agentx-hf HF_HUB_DISABLE_TELEMETRY=1
export AIPERF_HTTP_TCP_USER_TIMEOUT=900000 AIPERF_MAX_CONTEXT_LENGTH=$MAXCTX
curl -s -m 30 -X POST http://<PREFILL_NODE_IP>:32020/flush_cache; echo
$AGENTX_CLIENT/bin/agentx profile --url http://<PREFILL_NODE_IP>:32022 --model glm-loop \
  --tokenizer $MODEL_PATH --tokenizer-trust-remote-code \
  --concurrency $CONC --benchmark-duration $DUR --max-context-length $MAXCTX \
  --server-metrics http://<DECODE_NODE_IP>:32021/metrics \
  --output-artifact-dir $OUT --public-dataset semianalysis_cc_traces_weka_062126 \
  --extra-inputs "$EXTRA" ${WARMUP:+--warmup-requests-per-lane $WARMUP} > $OUT/agentx.log 2>&1
echo "exit $?" >> $OUT/agentx.log
echo AGENTX_DONE $TAG $CONC $OSL
