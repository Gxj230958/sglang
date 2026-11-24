#!/bin/bash
# agentx_rung.sh <attempt> <conc> <duration> [server args...]: one AgentX point.
# Fresh server (scripts/launch.sh + args) on :30001, sglang-router (dp-aware, cache_aware,
# x-correlation-id) on :30000, saved /flush_cache reset, then InferenceX's replay-only driver
# (python -m infx.bench agentic, pinned 67c3ed26, agentx-harness 1.0.14) with scoring/validation.
# Env: AL=<golden AL> enables SGLang acceptance simulation (match-expected, real-draft-token);
#      HC_TOTAL_GB records the host-DRAM budget when HiCache is on.
set -uo pipefail
NAME=$1; CONC=$2; DURATION=$3; shift 3
W=/persistent/work/glm_loop_amd; AX=/persistent/work/agentx; E2E=$AX/InferenceX/inferencex-e2e
RES=$AX/results/$NAME
[ -e "$RES" ] && { echo "attempt dir exists: $RES"; exit 2; }
mkdir -p "$RES"; ST=$RES/status; : > "$ST"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$ST"; }
cleanup() {
  [ -n "${RPID:-}" ] && kill "$RPID" 2>/dev/null
  $W/scripts/stop_bg.sh "ax_$NAME" >> "$ST" 2>&1
  pkill -f "[d]octor.py ax_$NAME" 2>/dev/null
  log "cleanup done; VRAM $(rocm-smi --showmemuse 2>/dev/null | grep 'VRAM%' | awk '{print $NF}' | tr '\n' ' ')"
}
trap cleanup EXIT

# 1. identities
{ echo "attempt=$NAME conc=$CONC duration=$DURATION"; echo "server_args=$*"
  echo "sglang=$(git -C /persistent/work/sglang-zai-amd rev-parse HEAD) dirty=$(git -C /persistent/work/sglang-zai-amd status --porcelain | grep -v '^??' | wc -l)"
  echo "inferencex=$(git -C $AX/InferenceX rev-parse HEAD) agentx-harness=$($AX/.venv-agentx/bin/pip show agentx-harness | awk '/^Version/{print $2}')"
  echo "AL=${AL:-none} HC_TOTAL_GB=${HC_TOTAL_GB:-0}"; } > "$RES/identity.txt"

# 2. server + router
export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1 SGLANG_TIMEOUT_KEEP_ALIVE=900
if [ -n "${AL:-}" ]; then
  export SGLANG_SIMULATE_ACC_LEN=$AL SGLANG_SIMULATE_ACC_METHOD=match-expected SGLANG_SIMULATE_ACC_TOKEN_MODE=real-draft-token
fi
log "launch server"
$W/scripts/start_bg.sh "ax_$NAME" 30001 "$@" >> "$ST"
$W/scripts/wait_bg.sh "ax_$NAME" > "$RES/startup.txt" 2>&1
grep -q ALIVE "$RES/startup.txt" || { log "SERVER_FAILED"; cp $W/logs/ax_$NAME.log "$RES/server.log"; exit 1; }
SPID=$(pgrep -f "[s]glang::scheduler_DP0" | head -1); [ -n "$SPID" ] && tr '\0' '\n' < /proc/$SPID/environ | grep -E "^SGLANG_(SIMULATE|GLM_LOOP|TIMEOUT)" > "$RES/scheduler_env.txt"
setsid /opt/venv/bin/python -m sglang_router.launch_router --worker-urls http://127.0.0.1:30001 \
  --host 127.0.0.1 --port 30000 --policy cache_aware --dp-aware --request-id-headers x-correlation-id \
  --connect-timeout-secs 900 --request-timeout-secs 14400 --disable-health-check --disable-retries \
  --prometheus-port 29000 > "$RES/router.log" 2>&1 < /dev/null &
RPID=$!
for i in $(seq 1 60); do curl -sf -m 5 http://127.0.0.1:30000/v1/models > "$RES/models.json" 2>/dev/null && break; sleep 5; done
grep -q glm-loop "$RES/models.json" || { log "ROUTER_FAILED"; exit 1; }
curl -sf -m 300 http://127.0.0.1:30000/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"glm-loop","messages":[{"role":"user","content":"Say OK."}],"max_tokens":16,"chat_template_kwargs":{"enable_thinking":false}}' > "$RES/sanity.json" || { log "SANITY_FAILED"; exit 1; }
log "ready; sanity $(head -c 300 $RES/sanity.json)"
# Pre-load the long-context kernel variants on every DP rank while free device memory remains.
/opt/venv/bin/python $W/scripts/warm_long_ctx.py 30001 ${DP_SIZE:-8} > "$RES/warm_long_ctx.txt" 2>&1 || { log "WARM_FAILED"; exit 1; }
log "warm: $(tr '\n' ' ' < $RES/warm_long_ctx.txt | cut -c1-400)"
grep -v "^\[aiter\]" $W/logs/ax_$NAME.log | grep -c "device-loaded after serving started" > "$RES/late_loads_before_replay.txt"

# 3. reset (to the worker; must succeed)
code=$(curl -s -m 60 -X POST http://127.0.0.1:30001/flush_cache -D "$RES/cache-reset.headers" -o "$RES/cache-reset.body" -w '%{http_code}')
log "flush_cache http=$code body=$(head -c 200 $RES/cache-reset.body)"
[ "$code" = 200 ] || exit 1

# 4. replay + scoring (pinned replay-only driver)
cd "$E2E"
export RESULT_DIR=$RES RESULT_FILENAME=agentx_$NAME AGENTIC_OUTPUT_DIR=$RES EVAL_ONLY=false IS_MULTINODE=false PRECISION=fp8 \
  MODEL=/persistent/models/GLM-5-1028-Provider TOKENIZER=/persistent/models/GLM-5-1028-Provider SERVED_MODEL_NAME=glm-loop \
  MODEL_PREFIX=glmloop FRAMEWORK=sglang CONC=$CONC DURATION=$DURATION \
  WEKA_LOADER_OVERRIDE=semianalysis_cc_traces_weka_062126_256k \
  AIPERF_DYNAMO_SESSION_TIMEOUT_SECONDS=3600 AIPERF_EXPERIMENTAL_FAST=0 AIPERF_UNSAFE_OVERRIDE=false \
  AIPERF_HTTP_X_DYNAMO_SESSION_ID_FROM_CORRELATION_ID=false AIPERF_USE_DYNAMO_CONV_AWARE_ROUTING=1 \
  AIPERF_HTTP_X_SMG_ROUTING_KEY_FROM_CORRELATION_ID=true AIPERF_HTTP_TCP_USER_TIMEOUT=900000 \
  AIPERF_SERVER_URL=http://127.0.0.1:30000 AIPERF_SERVER_METRICS_URLS=http://127.0.0.1:30001/metrics \
  AIPERF_REQUIRED_SERVER_METRIC_PREFIX=sglang: AIPERF_RUNTIME_DIR=$AX/runtime-67c3ed26 \
  HF_HOME=$AX/hf-cache OPENAI_API_KEY=EMPTY PYTHONSAFEPATH=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E2E
# Result metadata the aggregator requires (single node, this deployment).
export TP=${TP:-8} EP_SIZE=${EP_SIZE:-8} DP_ATTENTION=${DP_ATTENTION:-true} SPEC_DECODING=mtp SPEC_ALGORITHM=EAGLE \
  SPEC_DRAFT_MODEL=native-nextn RUNNER_TYPE=mi355x IMAGE=local-rocm10-sglang TOTAL_CPU_DRAM_GB=${HC_TOTAL_GB:-0}
if [ "${HC_TOTAL_GB:-0}" -gt 0 ]; then export KV_OFFLOADING=dram KV_OFFLOAD_BACKEND=sglang-hicache; else export KV_OFFLOADING=none; fi
env | grep -E "^(AIPERF_|RESULT_|AGENTIC_|MODEL|TOKENIZER|SERVED_|CONC|DURATION|WEKA_|FRAMEWORK|PRECISION|EVAL_ONLY|IS_MULTINODE|TP|EP_SIZE|DP_ATTENTION|SPEC_|KV_OFFLOAD|TOTAL_CPU|RUNNER_TYPE|IMAGE)" | sort > "$RES/client_env.txt"
log "replay start"
$AX/runtime-67c3ed26/venv/bin/python -m infx.bench agentic > "$RES/driver.log" 2>&1
rc=$?
log "replay+score rc=$rc"
cp $W/logs/ax_$NAME.log "$RES/server.log"
echo "rc=$rc" > "$RES/terminal_status"
exit $rc
