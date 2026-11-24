#!/bin/bash
# acc_suite.sh <tag> [port] [benches...]: CUDA-parity accuracy set against a running server.
#   smoke  : text / image / long-context greedy smokes (scripts/smoke.py)
#   gsm8k  : full 1319, T=1.0 top_p=0.95, 64 threads, --max-tokens 32768 (Correctness E34 capped gate)
#   gpqa   : GPQA diamond 198 x 2 repeats, --max-tokens 32768, 32 threads (Correctness E29)
#   ruler2 : RULER2 32K, 1200 examples, --max-tokens 8192, 64 threads (Correctness E29)
set -u
export PATH=/opt/venv/bin:$PATH
TAG=$1; PORT=${2:-30000}; shift 2 || shift $#
BENCHES=${*:-smoke gsm8k gpqa ruler2}
D=/scratch/mobius/mi350x; OUT=$D/acc/$TAG; mkdir -p $OUT
URL=http://127.0.0.1:$PORT/v1
MODEL_DIR=/scratch/hf_home/hub/models--RadixArk--GLM-5-1028-Provider/snapshots/9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff
COMMON="--base-url $URL --temperature 1.0 --top-p 0.95"
for b in $BENCHES; do
  echo "== $b start $(date +%T)"
  case $b in
    smoke) /opt/venv/bin/python $D/scripts/smoke.py $PORT $OUT/smoke > $OUT/smoke.log 2>&1 ;;
    gsm8k) /opt/venv/bin/sgl-eval run gsm8k $COMMON --num-examples 1319 --num-threads 64 --max-tokens 32768 --out-dir $OUT/gsm8k > $OUT/gsm8k.log 2>&1 ;;
    gpqa) /opt/venv/bin/sgl-eval run gpqa $COMMON --n-repeats 2 --num-threads 32 --max-tokens 32768 --out-dir $OUT/gpqa > $OUT/gpqa.log 2>&1 ;;
    ruler2) /opt/venv/bin/sgl-eval run ruler2 $COMMON --ruler2-seq-len 32768 --num-threads 64 --max-tokens 8192 --ruler2-tokenizer $MODEL_DIR --out-dir $OUT/ruler2 > $OUT/ruler2.log 2>&1 ;;
  esac
  echo "== $b exit=$? $(date +%T)"
  tail -c 1500 $OUT/$b.log | tr '\r' '\n' | grep -E "score|rate|pass@|majority|ALL PASS|FAIL|PASS\]|Error|error" | grep -v "it/s" | head -12
done
