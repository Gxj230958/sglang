import gzip, json, sys, re, collections
ev = json.load(gzip.open(sys.argv[1]))["traceEvents"]
k = [e for e in ev if e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset") and "dur" in e]
k.sort(key=lambda e: e["ts"])
def short(n):
    n = re.sub(r"<.*", "", n); n = re.sub(r"\(.*", "", n); return n.split("::")[-1][-40:]
# find layer period: positions of _split_kernel
idx = [i for i, e in enumerate(k) if "_split_kernel" in e["name"]]
a, b = idx[int(sys.argv[2])], idx[int(sys.argv[2]) + 1]
prev = k[a - 1]["ts"] + k[a - 1]["dur"]
for e in k[a:b]:
    gap = e["ts"] - prev; prev = e["ts"] + e["dur"]
    print(f"{e['dur']:7.1f} us gap {gap:6.1f} grid {str(e['args'].get('grid')):14s} blk {str(e['args'].get('block')):12s} {short(e['name'])}")
print("layer total us", k[b]["ts"] - k[a]["ts"])
# DG gemm histogram
h = collections.Counter()
for e in k:
    if "gemm_1d1d" in e["name"]:
        h[(str(e["args"].get("grid")), round(e["dur"] / 2) * 2)] += 1
for (g, d), c in sorted(h.items()): print(g, d, c)
