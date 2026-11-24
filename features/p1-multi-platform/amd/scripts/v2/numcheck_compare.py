#!/opt/venv/bin/python
"""numcheck_compare.py <a.json> <b.json>: teacher-forced logprob deltas and top-1 agreement on the
shared reference tokens, plus greedy common-prefix lengths."""
import json
import statistics
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
d, agree, n, prefix, same = [], 0, 0, [], 0
for x, y in zip(a, b):
    if "tf_logprob" in x and "tf_logprob" in y:
        assert x["ref_ids"] == y["ref_ids"]
        for lx, ly, tx, ty in zip(x["tf_logprob"], y["tf_logprob"], x["tf_top1"], y["tf_top1"]):
            if lx is None or ly is None:
                continue
            d.append(abs(lx - ly))
            agree += tx == ty
            n += 1
    gx, gy = x["greedy_ids"], y["greedy_ids"]
    k = next((i for i, (u, v) in enumerate(zip(gx, gy)) if u != v), min(len(gx), len(gy)))
    prefix.append(k)
    same += gx == gy
if d:
    d.sort()
    print(
        f"teacher-forced tokens={n} mean|dlogp|={statistics.mean(d):.4f} p50={d[len(d)//2]:.4f} "
        f"p99={d[int(len(d)*.99)]:.4f} max={d[-1]:.3f} top1-agree={agree/n:.4%}"
    )
print(f"greedy identical {same}/{len(prefix)}; common prefix median={statistics.median(prefix)} min={min(prefix)}")
