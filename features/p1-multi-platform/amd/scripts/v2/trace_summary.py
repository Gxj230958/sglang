#!/opt/venv/bin/python
"""trace_summary.py <trace.json.gz> [top]: GPU kernel time by name, busy vs span, per-step counts."""
import gzip, json, sys, collections, re
tr = json.load(gzip.open(sys.argv[1]))
top = int(sys.argv[2]) if len(sys.argv) > 2 else 40
ev = [e for e in tr["traceEvents"] if e.get("ph") == "X" and e.get("cat") in ("kernel", "gpu_memcpy", "gpu_memset")]
ev.sort(key=lambda e: e["ts"])
t0, t1 = ev[0]["ts"], max(e["ts"] + e["dur"] for e in ev)
busy = sum(e["dur"] for e in ev)
# merge overlaps for true busy
merged, cur_s, cur_e = 0.0, None, None
for e in ev:
    s, d = e["ts"], e["ts"] + e["dur"]
    if cur_e is None or s > cur_e:
        if cur_e is not None: merged += cur_e - cur_s
        cur_s, cur_e = s, d
    else:
        cur_e = max(cur_e, d)
merged += cur_e - cur_s
print(f"kernels={len(ev)} span={(t1-t0)/1e3:.1f} ms busy(sum)={busy/1e3:.1f} ms busy(merged)={merged/1e3:.1f} ms ({merged/(t1-t0):.0%})")
# gaps
gaps = []
for a, b in zip(ev, ev[1:]):
    g = b["ts"] - (a["ts"] + a["dur"])
    if g > 0: gaps.append(g)
gaps.sort()
if gaps:
    print(f"gaps: n={len(gaps)} median={gaps[len(gaps)//2]:.1f} us p90={gaps[int(len(gaps)*.9)]:.1f} us sum={sum(gaps)/1e3:.1f} ms; sum(gaps<20us)={sum(g for g in gaps if g<20)/1e3:.1f} ms")
agg = collections.defaultdict(lambda: [0, 0.0])
def norm(n):
    n = re.sub(r"<.*", "", n)
    return n[:110]
for e in ev:
    a = agg[norm(e["name"])]; a[0] += 1; a[1] += e["dur"]
print(f"{'time_ms':>8} {'%':>5} {'count':>6} {'avg_us':>7}  name")
for n, (c, d) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:top]:
    print(f"{d/1e3:8.2f} {d/busy:5.1%} {c:6d} {d/c:7.1f}  {n}")
