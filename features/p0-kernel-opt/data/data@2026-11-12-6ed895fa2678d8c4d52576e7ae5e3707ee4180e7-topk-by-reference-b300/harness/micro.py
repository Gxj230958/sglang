"""Kernel-level cost of the pieces: Top-K anchor clones and the damp blend forms."""
import json, sys, time, torch
dev = torch.device("cuda:0")
def timeit(fn, n=30):
    for _ in range(5): fn()
    torch.cuda.synchronize(); t = time.perf_counter()
    for _ in range(n): fn()
    torch.cuda.synchronize(); return (time.perf_counter() - t) / n * 1e3
def peak(fn):
    torch.cuda.synchronize(); torch.cuda.empty_cache(); base = torch.cuda.memory_allocated(); torch.cuda.reset_peak_memory_stats()
    out = fn(); torch.cuda.synchronize(); p = torch.cuda.max_memory_allocated() - base; del out; return p >> 20
res = []
for rows in (32, 8192, 32768):
    anchors = [torch.randint(0, 1 << 20, (rows, 2048), dtype=torch.int32, device=dev) for _ in range(7)]
    x = torch.randn(rows, 6144, device=dev, dtype=torch.bfloat16); z = torch.randn_like(x); beta = torch.rand(rows, 1, device=dev, dtype=torch.bfloat16)
    def clones(): return [a.clone() for a in anchors]
    def ref(): return x + beta * (z - x)
    def one():
        o = z - x; o.mul_(beta); o.add_(x); return o
    assert torch.equal(ref().view(torch.int16), one().view(torch.int16))
    row = {"rows": rows, "clone7_ms": round(timeit(clones), 4), "blend_ref_ms": round(timeit(ref), 4), "blend_onebuf_ms": round(timeit(one), 4),
           "clone7_peak_mib": peak(clones), "blend_ref_peak_mib": peak(ref), "blend_onebuf_peak_mib": peak(one)}
    res.append(row); print(row, flush=True)
    del anchors, x, z, beta
json.dump(res, open(sys.argv[1], "w"), indent=1)
