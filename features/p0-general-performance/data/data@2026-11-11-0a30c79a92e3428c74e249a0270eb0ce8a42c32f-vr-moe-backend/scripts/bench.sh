#!/bin/bash
export PYTHONPATH=${SRCDIR:-/nfs_home/glm5-lcd/src/python}
M=/nfs_home/models/GLM-5-1028-Provider
B="python3 -m sglang.benchmark.one_batch_server --model-path $M --base-url http://$MASTER_ADDR:30701 --show-report --result-filename $RUN/results.jsonl"
for bs in ${LEVELS:-1 8}; do
  for r in 1 2; do
    echo "=== RUN bs=$bs r=$r $(date +%T)"
    $B --input-len ${ILEN:-131072} --output-len ${OLEN:-512} --batch-size $bs --run-name bs$bs-r$r
  done
  if [ -n "${PROF:-}" ]; then
    echo "=== PROFILE bs=$bs $(date +%T)"
    $B --input-len ${ILEN:-131072} --output-len ${OLEN:-512} --batch-size $bs --skip-warmup --run-name bs$bs-prof \
      --profile --profile-by-stage --profile-steps 5 --profile-output-dir $RUN/prof-bs$bs
  fi
done
echo BENCH_DONE
