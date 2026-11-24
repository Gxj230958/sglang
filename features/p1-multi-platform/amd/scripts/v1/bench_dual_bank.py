"""Microbenchmark: GLM LoopLM dual-bank sparse MLA decode on one GPU.

Compares, at TP8 local heads (8), Top-K 2048 + window 128, bf16 KV:
  dual   - glm_loop_sparse_decode.sparse_mla_decode with both banks (current ROCm route)
  single - the ROCm triton DSA decode (triton_sparse_mla_decode_splitk) over Top-K only,
           i.e. what a non-loop slot pays
"""

import sys

import torch

from sglang.kernels.ops.attention.dsa.triton_sparse_mla_decode import (
    triton_sparse_mla_decode_splitk,
)
from sglang.kernels.ops.attention.glm_loop_sparse_decode import (
    SparseDecodeWorkspace,
    sparse_mla_decode,
)

torch.manual_seed(0)
dev = "cuda"
H = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SLOTS = 1 << 20
kv_a = torch.randn(SLOTS, 1, 576, device=dev, dtype=torch.bfloat16)
kv_b = torch.randn(SLOTS, 1, 576, device=dev, dtype=torch.bfloat16)
ws = SparseDecodeWorkspace()
ws.reserve(entries=1 << 22, d_v=512, device=dev)


def bench(fn, iters=50):
    for _ in range(5):
        fn()
    torch.cuda.synchronize()
    g = torch.cuda.CUDAGraph()
    with torch.cuda.graph(g):
        for _ in range(10):
            fn()
    torch.cuda.synchronize()
    start, end = torch.cuda.Event(True), torch.cuda.Event(True)
    start.record()
    for _ in range(iters):
        g.replay()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end) / (iters * 10) * 1000  # us


print(f"heads={H}")
print(f"{'rows':>5} {'dual_us':>9} {'single_us':>10}")
for rows in (1, 2, 4, 8, 16, 32, 64, 128, 256, 1024):
    q = torch.randn(rows, H, 576, device=dev, dtype=torch.bfloat16)
    q_nope, q_rope = q[..., :512], q[..., 512:]
    idx_a = torch.randint(1, SLOTS, (rows, 2048), device=dev, dtype=torch.int32)
    idx_b = torch.randint(1, SLOTS, (rows, 128), device=dev, dtype=torch.int32)
    valid = torch.ones(rows, dtype=torch.bool, device=dev)

    def dual():
        sparse_mla_decode(
            q=q_nope, q_rope=q_rope, num_heads=H, kv_a=kv_a, idx_a=idx_a,
            kv_b=kv_b, idx_b=idx_b, sm_scale=0.0625, d_v=512, workspace=ws,
            valid_rows=valid,
        )

    tws = []

    def single():
        triton_sparse_mla_decode_splitk(
            q_nope=q_nope, q_rope=q_rope, kv=kv_a, indices=idx_a.unsqueeze(1),
            sm_scale=0.0625, d_v=512, workspace=tws,
        )

    print(f"{rows:>5} {bench(dual):>9.1f} {bench(single):>10.1f}")
