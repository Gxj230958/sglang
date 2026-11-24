#!/opt/venv/bin/python
"""decode_breakdown.py <trace.json.gz> [min_kernels]: per-kernel time over decode cycles only
(GPU segments split at >50 us idle gaps with at least min_kernels kernels)."""
import collections, gzip, json, re, sys
tr = json.load(gzip.open(sys.argv[1]))
mink = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
ev = sorted([e for e in tr["traceEvents"] if e.get("ph") == "X" and e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset")], key=lambda e: e["ts"])
segs, cur = [], [ev[0]]
for a, b in zip(ev, ev[1:]):
    if b["ts"] - (a["ts"] + a["dur"]) > 50:
        segs.append(cur); cur = []
    cur.append(b)
segs.append(cur)
dec = [s for s in segs if len(s) >= mink and not any("fmoe" in e["name"] for e in s)]
n = len(dec)
agg = collections.defaultdict(lambda: [0, 0.0])
for s in dec:
    for e in s:
        k = re.sub(r"<.*", "", e["name"])
        k = re.sub(r"_ZN5aiter37dynamic_per_group_scaled_quant_kernel.*", "aiter::dynamic_per_group_scaled_quant", k)
        a = agg[k[:100]]; a[0] += 1; a[1] += e["dur"]
tot = sum(v[1] for v in agg.values())
span = sum(s[-1]["ts"] + s[-1]["dur"] - s[0]["ts"] for s in dec)
print(f"decode cycles={n} span/cycle={span/n/1e3:.2f} ms kernel/cycle={tot/n/1e3:.2f} ms kernels/cycle={sum(v[0] for v in agg.values())/n:.0f}")
print(f"{'ms/cyc':>7} {'%':>6} {'n/cyc':>6} {'avg_us':>7}  name")
for k, (c, d) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:30]:
    print(f"{d/n/1e3:7.3f} {d/tot:6.1%} {c/n:6.0f} {d/c:7.1f}  {k}")
