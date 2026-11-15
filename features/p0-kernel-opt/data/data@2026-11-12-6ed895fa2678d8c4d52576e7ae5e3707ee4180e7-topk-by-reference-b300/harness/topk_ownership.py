"""Does a Top-K producer's returned tensor keep its values while later producer
calls run?  Eager and CUDA-graph capture/replay, per producer path."""
import json, sys, traceback
from types import SimpleNamespace
import torch

from sglang.srt.layers.attention.dsa import dsa_topk_backend as tb
from sglang.srt.layers.attention.dsa.dsa_topk_backend import DSATopKBackend, TopkTransformMethod
from sglang.kernels.ops.attention.dsv4.topk import plan_topk_v2
from sglang.srt.environ import envs

dev = torch.device("cuda:0")
TOPK, PAGE = 2048, 64
g = torch.Generator(device=dev).manual_seed(0)


def paged_inputs(rows, max_len, seed):
    g.manual_seed(seed)
    pages = max_len // PAGE
    lengths = torch.randint(1, max_len + 1, (rows,), generator=g, device=dev, dtype=torch.int32)
    lengths[0] = max_len
    if rows > 1:
        lengths[1] = 100  # shorter than topk: -1 padded tail
    scores = torch.randn((rows, max_len), generator=g, device=dev, dtype=torch.float32)
    real_pt = torch.stack([torch.randperm(pages * 4, generator=g, device=dev)[:pages] + 1 for _ in range(rows)]).to(torch.int32)
    pt1 = (real_pt.long().unsqueeze(-1) * PAGE + torch.arange(PAGE, device=dev)).reshape(rows, -1).to(torch.int32)
    md = SimpleNamespace(
        real_page_table=real_pt, page_table_1=pt1, page_size=PAGE,
        topk_v2_plan=plan_topk_v2(lengths), token_to_batch_idx=None,
        prefill_cp_sharded=False,
        cu_seqlens_k=None,
    )
    return scores, lengths, md


def call(path, scores, lengths, md):
    scores = scores.clone()  # some kernels mask scores in place
    if path == "sgl_v2_paged":
        return tb._topk_transform_v2_paged(scores, lengths, TOPK, md)
    if path == "sgl_v2_ragged":
        off = torch.arange(scores.shape[0], device=dev, dtype=torch.int32) * 7
        return tb._topk_transform_v2_ragged(scores, lengths, TOPK, off, None)
    if path == "sgl_v2_packed":
        rs = torch.zeros(scores.shape[0], device=dev, dtype=torch.int32)
        r2b = torch.arange(scores.shape[0], device=dev, dtype=torch.int32)
        return tb._topk_transform_v2_packed(scores, lengths, TOPK, md, row_starts=rs, row_to_batch=r2b)
    if path == "sgl_legacy_paged":
        from sgl_kernel import fast_topk_transform_fused
        cu = torch.arange(scores.shape[0] + 1, device=dev, dtype=torch.int32)
        return fast_topk_transform_fused(score=scores, lengths=lengths, page_table_size_1=md.page_table_1, cu_seqlens_q=cu, topk=TOPK)
    if path == "sgl_legacy_ragged":
        from sgl_kernel import fast_topk_transform_ragged_fused
        off = torch.arange(scores.shape[0], device=dev, dtype=torch.int32) * 7
        return fast_topk_transform_ragged_fused(score=scores, lengths=lengths, topk_indices_offset=off, topk=TOPK)
    if path == "sgl_fast_topk_v2":
        from sgl_kernel import fast_topk_v2
        return fast_topk_v2(scores, lengths, TOPK)
    if path == "torch_unfused":
        return tb._topk_unfused(scores, lengths, TOPK)
    if path == "flashinfer_paged":
        import flashinfer
        return flashinfer.top_k_page_table_transform(
            scores.contiguous(), md.page_table_1.contiguous(), lengths.contiguous(), TOPK,
            row_to_batch=None, deterministic=True, tie_break=0, dsa_graph_safe=True,
            row_starts=None, page_table_row_starts=None)
    if path == "flashinfer_ragged":
        import flashinfer
        off = torch.arange(scores.shape[0], device=dev, dtype=torch.int32) * 7
        return flashinfer.top_k_ragged_transform(
            scores.contiguous(), off.contiguous(), lengths.contiguous(), TOPK,
            deterministic=True, tie_break=0, dsa_graph_safe=True, row_starts=None)
    if path == "flashinfer_unfused":
        import flashinfer
        return tb._topk_unfused(scores, lengths, TOPK, topk_op=flashinfer.top_k,
                                topk_op_kwargs={"sorted": False, "deterministic": True, "tie_break": 0, "dsa_graph_safe": True})
    raise KeyError(path)


def canon(t):
    return torch.sort(t.long(), dim=-1).values


def eager(path, rows, max_len):
    s, l, md = paged_inputs(rows, max_len, 1)
    first = call(path, s, l, md)
    snap = first.clone()
    ptr = first.data_ptr()
    aliases = 0
    later_shapes = [(rows, max_len), (rows, max_len), (max(1, rows // 2), max_len), (rows * 2, max_len // 2), (rows, max_len)]
    for i, (r, ml) in enumerate(later_shapes):
        s2, l2, md2 = paged_inputs(r, ml, 100 + i)
        out = call(path, s2, l2, md2)
        aliases += int(out.data_ptr() == ptr)
        del out  # let the allocator and any kernel-side cache recycle
    torch.cuda.synchronize()
    # same inputs again: deterministic producer?
    again = call(path, s, l, md)
    return dict(
        shape=list(first.shape), dtype=str(first.dtype),
        unchanged=bool(torch.equal(first, snap)),
        later_output_aliases_first=aliases,
        repeat_call_set_equal=bool(torch.equal(canon(first), canon(again))),
        repeat_call_bitwise_equal=bool(torch.equal(first, again)),
    )


def graph(path, rows, max_len):
    sA, lA, mdA = paged_inputs(rows, max_len, 1)
    sB, lB, mdB = paged_inputs(rows, max_len, 2)
    stream = torch.cuda.Stream()
    kept = torch.empty((rows, TOPK), dtype=torch.int32, device=dev)
    kept_noclone_view = {}
    gr = torch.cuda.CUDAGraph()
    # warmup outside capture (JIT compile)
    call(path, sA, lA, mdA); call(path, sB, lB, mdB)
    torch.cuda.synchronize()
    with torch.cuda.stream(stream):
        with torch.cuda.graph(gr, stream=stream):
            first = call(path, sA, lA, mdA)      # the anchor a loop keeps
            for _ in range(3):
                other = call(path, sB, lB, mdB)  # later indexers
                del other
            kept.copy_(first)                    # what the paired slot reads
    res = {}
    for trial in range(3):
        nA, nlA, nmdA = paged_inputs(rows, max_len, 10 + trial)
        nB, nlB, nmdB = paged_inputs(rows, max_len, 50 + trial)
        for dst, src in ((sA, nA), (lA, nlA), (sB, nB), (lB, nlB)):
            dst.copy_(src)
        for mdd, mds in ((mdA, nmdA), (mdB, nmdB)):
            mdd.real_page_table.copy_(mds.real_page_table); mdd.page_table_1.copy_(mds.page_table_1)
            mdd.topk_v2_plan.copy_(mds.topk_v2_plan)
        gr.replay(); torch.cuda.synchronize()
        ref = call(path, nA, nlA, nmdA)
        res[f"replay{trial}_first_matches_eager"] = bool(torch.equal(canon(kept), canon(ref)))
    return res


PATHS = ["sgl_v2_paged", "sgl_v2_ragged", "sgl_v2_packed", "sgl_legacy_paged", "sgl_legacy_ragged",
         "sgl_fast_topk_v2", "torch_unfused", "flashinfer_paged", "flashinfer_ragged", "flashinfer_unfused"]
out = {"device": torch.cuda.get_device_name(0), "torch": torch.__version__}
try:
    import flashinfer; out["flashinfer"] = flashinfer.__version__
except Exception as e:
    out["flashinfer"] = repr(e)
for path in PATHS:
    rec = {}
    for tag, rows, ml in (("decode_like", 4, 8192), ("verify_like", 32, 8192), ("prefill_like", 512, 4096)):
        try:
            rec[f"eager_{tag}"] = eager(path, rows, ml)
        except Exception:
            rec[f"eager_{tag}"] = {"error": traceback.format_exc().strip().splitlines()[-1][:300]}
    for tag, rows, ml in (("decode_like", 4, 8192), ("verify_like", 32, 8192)):
        try:
            rec[f"graph_{tag}"] = graph(path, rows, ml)
        except Exception:
            rec[f"graph_{tag}"] = {"error": traceback.format_exc().strip().splitlines()[-1][:300]}
    out[path] = rec
    print(path, json.dumps(rec), flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
