#!/bin/bash
# usage: run_tests.sh <tree> <listfile> <outdir>
TREE=$1; LIST=$2; OUT=$3
mkdir -p $OUT; : > $OUT/summary.tsv
cd $TREE
while read f; do
  [ -f "$f" ] || { printf "%s\tMISSING\n" "$f" >> $OUT/summary.tsv; continue; }
  log=$OUT/$(echo $f | tr '/' '_').log
  PYTHONPATH=python:/tmp/usync/tf519:/tmp/usync/vllm_stub SGLANG_IS_IN_CI=0 timeout 900 /home/ubuntu/cpu-venv/bin/python -m pytest -q -p no:cacheprovider -o addopts="" "$f" > $log 2>&1
  rc=$?
  last=$(grep -E '^(=+ )?[0-9]+ (passed|failed|error)|no tests ran|^=+ .*(passed|failed|error|skipped).* =+$' $log | tail -1)
  printf "%s\t%s\t%s\n" "$f" "$rc" "$last" >> $OUT/summary.tsv
done < $LIST
echo DONE >> $OUT/summary.tsv
