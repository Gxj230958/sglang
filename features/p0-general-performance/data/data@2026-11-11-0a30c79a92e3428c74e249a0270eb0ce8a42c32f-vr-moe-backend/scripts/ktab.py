import gzip, json, sys, re, collections
ev = json.load(gzip.open(sys.argv[1]))["traceEvents"]
top = int(sys.argv[2]) if len(sys.argv) > 2 else 40
k = [e for e in ev if e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset") and "dur" in e]
k.sort(key=lambda e: e["ts"])
t0, t1 = k[0]["ts"], k[-1]["ts"] + k[-1]["dur"]
busy = sum(e["dur"] for e in k)
print(f"kernels {len(k)} span {(t1-t0)/1e3:.1f} ms busy {busy/1e3:.1f} ms")
def short(n):
    n = re.sub(r"<.*", "", n); n = re.sub(r"\(.*", "", n)
    return n[-70:]
agg = collections.defaultdict(lambda: [0, 0.0, set()])
for e in k:
    a = agg[short(e["name"])]; a[0] += 1; a[1] += e["dur"]
    g = e.get("args", {}).get("grid"); a[2].add(str(g))
for n, (c, d, g) in sorted(agg.items(), key=lambda x: -x[1][1])[:top]:
    print(f"{d/1e3:9.2f} ms {100*d/busy:5.1f}% n={c:6d} avg {d/c:8.1f} us  {n}  grids={sorted(g)[:3]}")
