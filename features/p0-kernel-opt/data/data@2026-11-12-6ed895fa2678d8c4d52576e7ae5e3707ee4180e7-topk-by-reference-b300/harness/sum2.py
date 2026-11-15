import glob, json, sys, collections, re, os, statistics as st
R = "/scratch/cc-pr43/logs"
for name in sys.argv[1:]:
    L = os.path.join(R, name)
    if not os.path.isdir(L): continue
    out = [name, open(L + "/job.status").read().replace("\n", ";") if os.path.exists(L + "/job.status") else "nostatus"]
    print("== " + " ".join(out))
    for f in glob.glob(L + "/eval/*/metrics.json"):
        m = json.load(open(f)); a = m["aggregate"]
        print("  gsm8k n=%d score=%.4f stop=%.4f trunc=%.4f err=%.4f lat=%.0fs" % (m["num_examples"], a["score"], a["stop_rate"], a["truncated_rate"], a["error_rate"], m["latency_seconds"]))
    try:
        acc = [float(x) for line in open(L + "/serve.log", errors="replace") for x in re.findall(r"accept len: ([0-9.]+)", line)]
        if acc: print("  mtp accept len mean %.3f over %d lines" % (sum(acc) / len(acc), len(acc)))
        txt = open(L + "/serve.log", errors="replace").read()
        v = re.findall(r"GLMLOOP_VAL pid=\d+ topk_checks=(\d+) topk_mismatches=(\d+)", txt)
        if v: print("  VAL last per-rank:", sorted(set(v[-8:])))
        tb = len(re.findall(r"Traceback|CUDA out of memory", txt))
        print("  tracebacks/oom in serve.log:", tb)
    except OSError: pass
    for k in ("serve", "decode"):
        p = L + "/perf-%s.log" % k
        if os.path.exists(p):
            t = open(p).read()
            g = lambda pat: (re.findall(pat + r"[^0-9]*([0-9.]+)", t) or ["?"])[0]
            print("  perf-%s ok=%s out_tok/s=%s meanTTFT=%s medTTFT=%s meanITL=%s meanE2E=%s" % (k, g("Successful requests:"), g("Output token throughput \(tok/s\):"), g("Mean TTFT \(ms\):"), g("Median TTFT \(ms\):"), g("Mean ITL \(ms\):"), g("Mean E2E Latency \(ms\):")))
    p = L + "/longprefill.json"
    if os.path.exists(p):
        rows = json.load(open(p)); by = collections.defaultdict(list)
        for r in rows: by[r["target"]].append(r.get("latency_s"))
        for n, v in by.items():
            ok = [x for x in v if x is not None]
            print("  lp %d: n=%d all=%s median=%.4f min=%.4f" % (n, len(ok), ok, st.median(ok) if ok else -1, min(ok) if ok else -1), "ERR" if len(ok) != len(v) else "")
    # memory: main scheduler rank log = the one with nonzero alloc
    for f in sorted(glob.glob(L + "/mem/mem-*.log")):
        ep = {}
        for line in open(f):
            m = re.search(r"epoch=(\S+) .*alloc_mib=(\d+) max_alloc_mib=(\d+) max_reserved_mib=(\d+)", line)
            if m: ep[m.group(1)] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
        if not ep or max(v[1] for v in ep.values()) < 1000: continue
        agg = collections.defaultdict(list)
        for k, v in ep.items():
            key = re.sub(r"-\d+$", "", k) if k.startswith("lp-") else k
            agg[key].append(v)
        print("  mem %s:" % os.path.basename(f), " | ".join("%s alloc=%d maxalloc=%s maxres=%s" % (k, v[0][0], sorted(set(x[1] for x in v)), sorted(set(x[2] for x in v))) for k, v in sorted(agg.items())))
    p = L + "/suite.json"
    if os.path.exists(p):
        s = json.load(open(p)); sm = s.get("smoke", {})
        print("  smoke:", {k: (v.get("finish_reason"), v.get("ok"), (v.get("content") or "")[:24]) for k, v in sm.items()})
        c = s.get("cache", {})
        def walk(o, key=""):
            if isinstance(o, dict) and "finish_reason" in o:
                yield key, o
            elif isinstance(o, dict):
                for k, v in o.items(): yield from walk(v, key + "/" + k)
        rows = list(walk(c))
        print("  cache:", [(k, r["finish_reason"], r["cached_tokens"], r.get("ok")) for k, r in rows])
        d = s.get("det", {})
        if d: print("  det self-identical: %d/%d" % (sum(x["same_tokens"] for x in d["self_cmp"]), len(d["self_cmp"])))
