NAME=$1; L=/scratch/cc-pr43/logs/$NAME
echo "== $NAME: $(tr '\n' ';' < $L/job.status 2>/dev/null)"
tail -12 $L/gsm8k.log 2>/dev/null | tr '\r' '\n' | grep -vE "^gsm8k:" | cut -c1-200 | tail -6
/opt/sglang/bin/python - $L <<'PY'
import glob, json, sys, collections, re
L = sys.argv[1]
for f in glob.glob(L + "/eval/**/*.jsonl", recursive=True):
    rows = [json.loads(x) for x in open(f)]
    fr = collections.Counter(str(r.get("finish_reason")) for r in rows)
    corr = [r.get("correct", r.get("score")) for r in rows]
    err = sum(1 for r in rows if r.get("error"))
    print("gsm8k", f.split("/")[-1], "rows", len(rows), "finish_reason", dict(fr), "errors", err, "correct", sum(1 for c in corr if c in (True, 1, 1.0)))
try:
    acc = [float(m) for line in open(L + "/serve.log", errors="replace") for m in re.findall(r"accept len: ([0-9.]+)", line)]
    if acc: print("mtp accept len: mean %.3f over %d decode log lines" % (sum(acc) / len(acc), len(acc)))
except OSError: pass
PY
grep -E "perf |throughput|TTFT|ITL|E2E" $L/perf.log 2>/dev/null | cut -c1-120
[ -f $L/longprefill.log ] && cat $L/longprefill.log | cut -c1-200
[ -f $L/suite.log ] && tail -60 $L/suite.log | cut -c1-230
cat $L/gpu-after-ready.txt 2>/dev/null; echo
for f in $L/mem/mem-*.log; do [ -f "$f" ] || continue; echo "$(basename $f): $(awk '{e=$2; a[e]=$0} END{for(k in a) print a[k]}' $f | sort -k2 | cut -d' ' -f2- | tr '\n' '|' | cut -c1-2500)"; done 2>/dev/null | head -3
grep -E "GLMLOOP_VAL" $L/serve.log 2>/dev/null | tail -9 | cut -c1-200
grep -n -m3 -E "Traceback|CUDA out of memory|OutOfMemory" $L/serve.log 2>/dev/null | cut -c1-200
