#!/bin/bash
# hc_dep8.sh: HiCache on DEP8 + window layout + MTP, following NVIDIA HiCache E03's sequence.
# L2 run: probe, fill one DP rank past its GPU pool (forces host eviction), probe again, GSM8K.
# L3 run: file backend; probe (writes storage), restart on the same directory, probe (storage restore).
# All probe/fill requests are pinned to DP rank $R with X-Data-Parallel-Rank.
cd /persistent/work/glm_loop_amd
export PATH=/opt/venv/bin:/persistent/work/evalenv/bin:$PATH
R=${R:-3}; B=http://127.0.0.1:30000/v1; OUT=evals/hicache_dep8; mkdir -p $OUT; ST=$OUT/status; : > $ST
M=/persistent/models/GLM-5-1028-Provider
DEP8="--tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.85 --context-length 262144 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report"
HC="--enable-hierarchical-cache --hicache-size ${HC_GB:-200} --hicache-write-policy write_through"
export SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1
ready() { scripts/wait_bg.sh $1 | tee -a $ST | grep -q ALIVE; }
probe() { DP_RANK=$R python3 scripts/midfork.py $B $OUT/$1.json m2 > $OUT/$1.log 2>&1; python3 - $OUT/$1.json <<'PY' | tee -a $ST
import json,sys; r=json.load(open(sys.argv[1]))
print(sys.argv[1].split('/')[-1], f"{sum(x['correct'] for x in r)}/{len(r)} correct", f"{sum(x['finish']=='stop' for x in r)}/{len(r)} stop", "cached", [x['cached'] for x in r])
PY
}
pf() { grep -c 'HiCache prefetch success\|prefetch.*success' logs/$1.log; }

scripts/start_bg.sh dep8_hc 30000 $DEP8 $HC >> $ST
ready dep8_hc || { echo L2_NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
probe l2-a
DP_RANK=$R python3 scripts/hicache.py $B $OUT/anchor.json fill ${FILL:-260} l2fill > $OUT/fill.log 2>&1; echo "fill rc=$? $(tail -1 $OUT/fill.log)" >> $ST
grep -E "DP$R .*Decode batch|DP$R .*Prefill batch" logs/dep8_hc.log | tail -1 | cut -c1-260 >> $ST
probe l2-b
echo "l2 done $(date -u +%T)" >> $ST
sgl-eval run gsm8k --base-url $B --num-examples 1319 --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $OUT/gsm8k > $OUT/gsm8k.log 2>&1
tr '\r' '\n' < $OUT/gsm8k.log | grep -E "score|stop_rate|truncated_rate|examples" | tail -4 >> $ST
curl -sf -m 5 localhost:30000/health >/dev/null && echo ALIVE_AT_END >> $ST || echo DOWN_AT_END >> $ST
scripts/stop_bg.sh dep8_hc >> $ST

rm -rf /persistent/work/glm_loop_amd/hicache-store; mkdir -p /persistent/work/glm_loop_amd/hicache-store
export SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=/persistent/work/glm_loop_amd/hicache-store
scripts/start_bg.sh dep8_l3a 30000 $DEP8 $HC --hicache-storage-backend file >> $ST
ready dep8_l3a || { echo L3A_NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
probe l3-a
sleep 20; echo "store files $(find hicache-store -type f | wc -l) $(du -sh hicache-store | cut -f1)" >> $ST
scripts/stop_bg.sh dep8_l3a >> $ST
scripts/start_bg.sh dep8_l3b 30000 $DEP8 $HC --hicache-storage-backend file >> $ST
ready dep8_l3b || { echo L3B_NOT_READY >> $ST; echo DONE >> $ST; exit 1; }
probe l3-b
echo "prefetch success lines: $(pf dep8_l3b)" >> $ST
scripts/stop_bg.sh dep8_l3b >> $ST
echo DONE >> $ST
