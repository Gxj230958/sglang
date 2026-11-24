#!/bin/bash
# B300-parity serving benchmark (mirrors Correctness E14's TP8 workloads).
# Usage: bench_parity.sh <port> <out_dir> [workloads...]  (default: short-c1 short-c32 long-c4)
set -uo pipefail
PORT=$1; OUT=$2; shift 2
WORKLOADS=${*:-short-c1 short-c32 long-c4}
mkdir -p "$OUT"
export PATH=/opt/venv/bin:$PATH PYTHONPATH=/persistent/work/sglang-zai-amd/python HF_HUB_OFFLINE=1
MODEL=/persistent/models/GLM-5-1028-Provider
for wl in $WORKLOADS; do
  case $wl in
    short-c1)  IN=2000;  OUTL=500; N=16;  C=1 ;;
    short-c32) IN=2000;  OUTL=500; N=128; C=32 ;;
    long-c4)   IN=30000; OUTL=300; N=16;  C=4 ;;
    *) echo "unknown workload $wl"; continue ;;
  esac
  for seed in 1 2; do
    python -m sglang.bench_serving --backend sglang --host 127.0.0.1 --port "$PORT" \
      --model glm-loop --tokenizer "$MODEL" \
      --dataset-name random-ids --random-range-ratio 1 \
      --random-input-len $IN --random-output-len $OUTL \
      --num-prompts $N --max-concurrency $C --seed $seed \
      --flush-cache --warmup-requests 2 \
      --output-file "$OUT/$wl-seed$seed.jsonl" > "$OUT/$wl-seed$seed.log" 2>&1
    grep -E "Output token throughput|Median TTFT|Mean TPOT|Accept length|Successful requests" "$OUT/$wl-seed$seed.log" | sed "s/^/[$wl seed$seed] /"
  done
done
