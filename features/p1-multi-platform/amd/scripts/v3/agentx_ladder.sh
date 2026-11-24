#!/bin/bash
# agentx_ladder.sh <cohort> <candidate> <duration> <conc...>: walks the rungs in order with
# agentx_rung.sh (fresh server per rung) and stops at the first failure.
# Candidates (server args after scripts/launch.sh's defaults):
# --mem-fraction-static defaults to 0.80: at 0.85 concurrent long-context prefill left 0 GiB outside torch
# for Triton code objects and kernel scratch, and ranks aborted (late load at 0 GiB; launch out of resources).
#   dep8_bf16_hc : DEP8 + window + MTP 3/1/4, bf16 KV, HiCache L2 (HC_GB per rank, write_through)
#   dep8_fp8     : DEP8 + window + MTP 3/1/4, raw fp8_e4m3 KV
#   dep8_fp8_hc  : dep8_fp8 + HiCache L2
set -uo pipefail
COHORT=$1; CAND=$2; DUR=$3; shift 3
M=/persistent/models/GLM-5-1028-Provider
HC_GB=${HC_GB:-250}
BASE="--tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static ${MEM_FRAC:-0.80} --context-length 262144 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --enable-metrics --watchdog-timeout 3600"
HC="--enable-hierarchical-cache --hicache-size $HC_GB --hicache-write-policy write_through"
case $CAND in
  dep8_bf16_hc) ARGS="$BASE --kv-cache-dtype bfloat16 $HC"; export HC_TOTAL_GB=$((HC_GB * 8));;
  dep8_fp8)     ARGS="$BASE --kv-cache-dtype fp8_e4m3"; export HC_TOTAL_GB=0;;
  # DSV4.1 MI355X DP recipe's scheduling levers: decode rounds between prefills, and ranks prefilling together.
  dep8_fp8_sched) ARGS="$BASE --kv-cache-dtype fp8_e4m3 --prefill-decode-interval ${PDI:-16} --enable-prefill-delayer --prefill-delayer-token-usage-low-watermark 0.7"; export HC_TOTAL_GB=0;;
  # + exact variable-length DP gather for prefill (DSV4.1 MI355X DP recipe) and 8192-token chunks per rank:
  # long-context prefill 17.9K -> 21.1K tok/s aggregate (profiled).
  # Exact variable-length DP gather alone (4096-token chunks per rank): a communication-only change.
  dep8_fp8_sched_gv4) ARGS="$BASE --kv-cache-dtype fp8_e4m3 --prefill-decode-interval ${PDI:-16} --enable-prefill-delayer --prefill-delayer-token-usage-low-watermark 0.7"; export HC_TOTAL_GB=0 SGLANG_DP_USE_GATHERV=1;;
  dep8_fp8_sched_gv) ARGS="$BASE --kv-cache-dtype fp8_e4m3 --prefill-decode-interval ${PDI:-16} --enable-prefill-delayer --prefill-delayer-token-usage-low-watermark 0.7 --chunked-prefill-size 65536"; export HC_TOTAL_GB=0 SGLANG_DP_USE_GATHERV=1;;
  dep8_fp8_hc)  ARGS="$BASE --kv-cache-dtype fp8_e4m3 $HC"; export HC_TOTAL_GB=$((HC_GB * 8));;
  # Low concurrency: TP8 (every GPU on each request, no attention-DP lockstep), window layout, bf16 KV,
  # AITER allreduce fusion; E01's TP8 MTP configuration plus the window layout and a 262144 context.
  tp8_bf16) ARGS="--tp-size 8 --kv-cache-dtype bfloat16 --mem-fraction-static ${MEM_FRAC:-0.80} --context-length 262144 --chunked-prefill-size 16384 --max-running-requests 64 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --enable-aiter-allreduce-fusion --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --enable-metrics --watchdog-timeout 3600"; export HC_TOTAL_GB=0 DP_SIZE=1 TP=8 EP_SIZE=1 DP_ATTENTION=false;;
  # TP8 with an fp8 KV cache: about twice tp8_bf16's tokens, to carry TP8 past concurrency 8.
  tp8_fp8) ARGS="--tp-size 8 --kv-cache-dtype fp8_e4m3 --mem-fraction-static ${MEM_FRAC:-0.80} --context-length 262144 --chunked-prefill-size 16384 --max-running-requests 64 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --enable-aiter-allreduce-fusion --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report --enable-metrics --watchdog-timeout 3600"; export HC_TOTAL_GB=0 DP_SIZE=1 TP=8 EP_SIZE=1 DP_ATTENTION=false;;
  *) echo "unknown candidate $CAND"; exit 2;;
esac
export AL=${AL:-2.49}
for C in "$@"; do
  /persistent/work/glm_loop_amd/scripts/agentx_rung.sh "${COHORT}_${CAND}_c${C}" "$C" "$DUR" $ARGS || { echo "rung c$C failed; stopping"; exit 1; }
done
echo "ladder done"
