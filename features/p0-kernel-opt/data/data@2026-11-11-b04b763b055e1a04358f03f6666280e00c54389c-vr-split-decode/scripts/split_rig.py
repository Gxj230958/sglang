import sys, time, torch
import sglang
assert sglang.__file__.startswith("/nfs_home/glm5-lcd/src"), sglang.__file__
import sglang.kernels.ops.attention.glm_loop_sparse_decode as sd
torch.manual_seed(0)
dev = torch.device("cuda")
import os
H, L, CTX, NREQ = int(os.environ.get("HEADS", 8)), 4, 131072, 8
DUALS = (False, True) if os.environ.get("DUAL", "1") == "1" else (False,)
SLOTS = CTX * NREQ
kvs = [torch.randn(SLOTS, 1, 576, device=dev, dtype=torch.bfloat16) for _ in range(L)]
kvb = [torch.randn(SLOTS, 1, 576, device=dev, dtype=torch.bfloat16) for _ in range(L)]
ws = sd.SparseDecodeWorkspace()

def inputs(rows):
    req = torch.arange(rows, device=dev) % NREQ
    idx_a = (req[:, None] * CTX + torch.randint(0, CTX, (rows, 2048), device=dev)).int()
    idx_b = (req[:, None] * CTX + CTX - 128 + torch.arange(128, device=dev)[None]).int()
    q = torch.randn(rows, H, 576, device=dev, dtype=torch.bfloat16)
    return q, idx_a, idx_b

def ref(q, kv, idx):
    k = kv[idx.long(), 0].float()                        # rows, topk, 576
    s = torch.einsum("rhd,rkd->rhk", q.float(), k) * 0.05
    return s, k[..., :512]

def run(q, l, idx_a, idx_b, dual):
    return sd.sparse_mla_decode(q=q, num_heads=H, kv_a=kvs[l], idx_a=idx_a, kv_b=kvb[l] if dual else None,
                                idx_b=idx_b if dual else None, sm_scale=0.05, d_v=512, workspace=ws)

def check(rows, dual):
    q, ia, ib = inputs(rows)
    o = run(q, 0, ia, ib, dual).float()
    s, v = ref(q, kvs[0], ia)
    if dual:
        s2, v2 = ref(q, kvb[0], ib); s = torch.cat([s, s2], -1); v = torch.cat([v, v2], 1)
    r = torch.einsum("rhk,rkd->rhd", torch.softmax(s, -1), v)
    return ((o - r).abs().max() / r.abs().max()).item()

def bench(rows, dual, reps=300):
    q, ia, ib = inputs(rows)
    def body():
        for l in range(L): run(q, l, ia, ib, dual)
    body(); torch.cuda.synchronize()
    g = torch.cuda.CUDAGraph()
    with torch.cuda.graph(g): body()
    for _ in range(20): g.replay()
    torch.cuda.synchronize()
    best = 1e9
    for _ in range(5):
        t0 = time.perf_counter()
        for _ in range(reps): g.replay()
        torch.cuda.synchronize()
        best = min(best, (time.perf_counter() - t0) / reps / L * 1e6)
    return best

ROWS = [int(v) for v in sys.argv[1].split(",")]
CFGS = [tuple(map(int, c.split(","))) for c in sys.argv[2].split(";")]   # block_h, warps, target, block_k
for rows in ROWS:
    for dual in DUALS:
        res = []
        for bh, nw, tgt, bk in [(0, 0, 0, 64)] + CFGS:
            sd._BLOCK_K = bk
            if bh: sd._DECODE_CONFIGS[(rows, H)] = (bh, nw, tgt)
            else: sd._DECODE_CONFIGS.pop((rows, H), None)
            try:
                err = check(rows, dual); us = bench(rows, dual)
                res.append((us, bh, nw, tgt, bk, err))
                print(f"H={H} rows={rows} dual={int(dual)} cfg=({bh},{nw},{tgt},{bk}) err {err:.1e} us {us:.2f}", flush=True)
            except Exception as ex:
                print(f"H={H} rows={rows} dual={int(dual)} cfg=({bh},{nw},{tgt},{bk}) FAIL {str(ex)[:200]}", flush=True)
        b = min(res); print(f"BEST H={H} rows={rows} dual={int(dual)} {b[1:5]} {b[0]:.2f} us vs default {res[0][0]:.2f}", flush=True)
print("RIG_DONE")
