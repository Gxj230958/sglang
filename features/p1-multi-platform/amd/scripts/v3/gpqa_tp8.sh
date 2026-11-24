#!/bin/bash
# gpqa_tp8.sh: GPQA-Diamond with 4096 output tokens (Correctness E03 workload) on the mtp_r4 TP8 config.
cd /persistent/work/glm_loop_amd
export PATH=/opt/venv/bin:/persistent/work/evalenv/bin:$PATH
OUT=evals/gpqa4096_tp8; mkdir -p $OUT; ST=$OUT/status; : > $ST
M=/persistent/models/GLM-5-1028-Provider
TP8="--tp-size 8 --kv-cache-dtype bfloat16 --mem-fraction-static 0.75 --context-length 65536 --max-running-requests 32 --chunked-prefill-size 32768 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --enable-aiter-allreduce-fusion --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report"
scripts/start_bg.sh gpqa_tp8 30000 $TP8 >> $ST
scripts/wait_bg.sh gpqa_tp8 | tee -a $ST | grep -q ALIVE || { echo NOT_READY >> $ST; scripts/stop_bg.sh gpqa_tp8 >> $ST; echo DONE >> $ST; exit 1; }
sgl-eval run gpqa --base-url http://127.0.0.1:30000/v1 --temperature 1.0 --top-p 0.95 --max-tokens 4096 --out-dir $OUT/run > $OUT/gpqa.log 2>&1
echo "gpqa rc=$?" >> $ST
tr '\r' '\n' < $OUT/gpqa.log | grep -iE "pass@|majority|stop_rate|truncat|error_rate|examples" | tail -10 >> $ST
scripts/stop_bg.sh gpqa_tp8 >> $ST
echo DONE >> $ST
