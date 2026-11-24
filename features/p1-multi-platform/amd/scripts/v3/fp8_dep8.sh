#!/bin/bash
# fp8_dep8.sh: raw fp8_e4m3 KV on DEP8 + window layout + MTP (ROCm triton dual-bank).
# Context 32768 as NVIDIA Correctness E06 (window-layout matrix incl. trtllm fp8).
# 1) bf16 baseline: numcheck on the same layout. 2) fp8: pool sizes, parser smoke, prefix probe,
# numcheck against the same reference tokens, full GSM8K.
cd /persistent/work/glm_loop_amd
export PATH=/opt/venv/bin:/persistent/work/evalenv/bin:$PATH
B=http://127.0.0.1:30000/v1; OUT=evals/fp8_dep8; mkdir -p $OUT; ST=$OUT/status; : > $ST
M=/persistent/models/GLM-5-1028-Provider
DEP8="--tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.85 --context-length 32768 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report"
export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1
ready() { scripts/wait_bg.sh $1 | tee -a $ST | grep -q ALIVE; }
pool() { grep -v "^\[aiter\]" logs/$1.log | grep -m2 "DP0 .*\(sliding window memory pool\|KV Cache is allocated\)" | cut -c1-200 >> $ST; }

scripts/start_bg.sh dep8_bf16nc 30000 $DEP8 --kv-cache-dtype bfloat16 >> $ST
ready dep8_bf16nc || { echo BF16_NOT_READY >> $ST; scripts/stop_bg.sh dep8_bf16nc >> $ST; echo DONE >> $ST; exit 1; }
pool dep8_bf16nc
python3 scripts/numcheck.py 30000 $OUT/nc_bf16.json --ref numcheck/A_ref.json > $OUT/nc_bf16.log 2>&1; echo "numcheck bf16 rc=$?" >> $ST
scripts/stop_bg.sh dep8_bf16nc >> $ST

scripts/start_bg.sh dep8_fp8 30000 $DEP8 --kv-cache-dtype fp8_e4m3 >> $ST
ready dep8_fp8 || { echo FP8_NOT_READY >> $ST; scripts/stop_bg.sh dep8_fp8 >> $ST; echo DONE >> $ST; exit 1; }
pool dep8_fp8
python3 scripts/parser_smoke.py $B $OUT/parsers.json > $OUT/parsers.log 2>&1; tail -1 $OUT/parsers.log >> $ST
DP_RANK=3 python3 scripts/midfork.py $B $OUT/midfork.json m2 > $OUT/midfork.log 2>&1
python3 - $OUT/midfork.json <<'PY' >> $ST
import json,sys; r=json.load(open(sys.argv[1]))
print("midfork", f"{sum(x['correct'] for x in r)}/{len(r)} correct", f"{sum(x['finish']=='stop' for x in r)}/{len(r)} stop", "cached", [x['cached'] for x in r])
PY
python3 scripts/numcheck.py 30000 $OUT/nc_fp8.json --ref numcheck/A_ref.json > $OUT/nc_fp8.log 2>&1; echo "numcheck fp8 rc=$?" >> $ST
python3 scripts/numcheck_compare.py $OUT/nc_bf16.json $OUT/nc_fp8.json >> $ST 2>&1
sgl-eval run gsm8k --base-url $B --num-examples 1319 --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $OUT/gsm8k > $OUT/gsm8k.log 2>&1
tr '\r' '\n' < $OUT/gsm8k.log | grep -E "score|stop_rate|truncated_rate|examples" | tail -4 >> $ST
curl -sf -m 5 localhost:30000/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
scripts/stop_bg.sh dep8_fp8 >> $ST
echo DONE >> $ST
