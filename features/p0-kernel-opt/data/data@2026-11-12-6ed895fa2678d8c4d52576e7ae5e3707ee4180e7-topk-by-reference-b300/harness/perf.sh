# usage: perf.sh NAME SEED
NAME=$1; SEED=$2; R=/scratch/cc-pr43; L=$R/logs/$NAME
export PYTHONPATH=$R/src-base/python:$R/overlay HF_HOME=$R/hf-home HF_HUB_CACHE=$R/hf-home/hub HF_DATASETS_CACHE=$R/hf-home/datasets
cd $R
for cfg in "serve 2000 256 16 96" "decode 200 512 8 48"; do
  set -- $cfg
  echo "bench-$1" > $L/mem/epoch
  GLMVAL_MEMLOG= /opt/sglang/bin/python -m sglang.bench_serving --backend sglang-oai-chat --base-url http://127.0.0.1:31743 \
    --model /scratch/models/GLM-5-1028-Provider --dataset-name random --random-input-len $2 --random-output-len $3 \
    --random-range-ratio 1.0 --max-concurrency $4 --num-prompts $5 --flush-cache --seed $SEED \
    --output-file $L/perf-$1.jsonl > $L/perf-$1.log 2>&1
  echo "perf $1 rc=$?"; grep -E "Successful requests|Output token throughput|Mean TTFT|Median TTFT|Mean ITL|Median ITL|Mean TPOT|Mean E2E" $L/perf-$1.log
done
