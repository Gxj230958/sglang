# Kernel Optimization

## Summary

`zai-org/GLM-5-1028-Provider` kernel-optimization tracking connects profile evidence to kernel changes, microbenchmarks, and end-to-end serving impact. Status: In progress. [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) validates the SM100 small-head FlashMLA sparse-prefill specialization on 8 and 32 local heads with BF16 Q/KV. All 36 cases match native head64 exactly and reduce median latency by 6.63–16.26%. Serving impact is linked separately. The original integration PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891); release gates remain open. [E02](data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md) selects the split-K sparse decode config on Vera Rubin by local head count: time per call is 0.76–0.96× the previous config at 8 local heads and 0.71–1.00× at 32 and 64, unchanged at 16; the change is [PR #44](https://github.com/radixark/sglang-zai/pull/44), unmerged and non-release.

## Scope

### In Scope

- Profile-based kernel bottleneck identification.
- Kernel implementation, dispatch, fusion, and launch optimization.
- Microbenchmark and numerical-parity validation.
- End-to-end latency, throughput, memory, and compatibility attribution.
- Architecture-specific paths with explicit fallback behavior.

### Out of Scope

- Configuration-only tuning with no kernel change.
- Optimizations without correctness coverage or a supported fallback.
- Release claims from kernel-only results or an unmerged implementation.

## Success Criteria

- [x] E01 numerical parity is exact across all 36 measured shapes and dtypes.
- [ ] Define parity, performance, and portability gates for the remaining required shapes and platforms.
- [ ] Confirm microbenchmark and end-to-end gains on the locked upstream release candidate.
- [ ] Complete dispatch and fallback validation beyond the measured B300 cases.

## Kernel Inventory

| Kernel or Region | Operation | Shapes and Dtypes | Backend | Bottleneck | Baseline | Target | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| FlashMLA sparse prefill | DSA sparse attention with padded query heads | 8/32 local heads; D512/D576; BF16 Q/KV; top-k 2048 | SM100 FlashMLA | Padded-head softmax and output work | Native head64 | Compact small-head output | `<OWNER>` | E01 passed on B300; non-release |
| Split-K sparse decode (`glm_loop_sparse_decode`) | DSA sparse attention for decode, verify and draft rows, one or two KV banks | 8/16/32/64 local heads; 2–64 rows; BF16 Q/KV; top-k 2048 | Triton | Head-block padding and a split target tuned for 148 SMs | B300 table or `(16, 4, 296)` | Config by local head count on SM107 | `<OWNER>` | E02 measured on Vera Rubin; non-release |

## Optimization Results

| Date | Kernel | Platform | Shape | Metric | Baseline | Candidate | Delta | Parity | End-to-End Impact | Round |
|---|---|---|---|---|---:|---:|---:|---|---|---|
| 2026-11-06 | Small-head sparse prefill | B300 | 8/32 heads; D512/D576; 8K–100K context | Median kernel latency | Native head64 | Compact small-head | −6.63–16.26% | Exact in 36/36 cases | [Serving E01](../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |
| 2026-11-11 | Split-K sparse decode | Vera Rubin | 8/32/64 local heads; 2–64 rows | Time per call, rig | Previous config | Config by head count | 0.76–0.96× (8 heads); 0.71–1.00× (32); 0.75–1.00× (64) | Dense-reference error unchanged; GPU test passed | Kernel 15.9 → 12.2 µs per call at 32 verify rows in a TP8 server | [E02](data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md) |

## Dispatch and Fallback Matrix

| Hardware | Shape or Mode | Preferred Path | Fallback | Gate | Status | Evidence |
|---|---|---|---|---|---|---|
| SM100 FlashMLA 1.0.3 | Prefill; 8/32 heads; BF16 Q/KV; no LSE | Compact small-head | Native head64 for LSE, dual-bank, decode, or unsupported shapes | Exact active-output parity | E01 passed for measured shapes | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |
| Older or mismatched FlashMLA wheel | Public capability probe unavailable | Native head64 | Native head64 | No startup failure | Probe behavior checked; serving not rerun | [Serving E01](../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| Hopper and other platforms | All small-head-eligible shapes | Native backend | Native backend | No architecture regression claimed | Not covered | None |
| Vera Rubin (compute capability 10.7) | Split-K decode, 64 rows or fewer | 4 warps; 8-, 16- or 32-head block by local head count | Other devices keep the B300 table and `(16, 4, 296)` | Dense-reference parity; registered GPU test | E02 measured; PR #44 unmerged | [E02](data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md) |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Profile and prioritize — In progress

- [x] Identify padded-head sparse-prefill work as the optimization target; completed 2026-11-06.
- [ ] Rank the remaining kernel regions by user-visible impact on locked release profiles.
- Experiment [General Performance E02](../p0-general-performance/data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md): on Vera Rubin at TP8 the MoE runner is the largest decode region (about half of a layer with DeepGEMM); context length enters the decode step only through the indexer logits and Top-K kernels.

### Stage 2: Implement and microbenchmark — In progress

- [x] Measure the small-head specialization on 8/32 heads and D512/D576; completed 2026-11-06.
- [x] Confirm exact parity and positive latency reduction in all 36 cases; completed 2026-11-06.
- [ ] Cover the remaining eligible head counts, edge cases, and platforms on the release candidate.
- Experiment [E02](data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md): split-K sparse decode config by local head count on Vera Rubin, 0.71–1.00× the previous time per call, unchanged at 16 heads.
- [ ] Measure the split-K decode config on B300, where the table and fallback are unchanged.

### Stage 3: Prove end-to-end impact — In progress

- [x] Record serving TTFT and throughput with actual small-head dispatch; completed 2026-11-06.
- [ ] Repeat long-context serving and rerun on locked release artifacts.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-06 | Small-head FlashMLA sparse prefill | B300; 8/32 heads; D512/D576; 8K–100K context | 36/36 exact; median latency −6.63–16.26%; no negative case | [round](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |
| E02 | 2026-11-11 | Split-K sparse decode config on Vera Rubin | Vera Rubin; 8/16/32/64 local heads; 2–64 rows; 131072 context | 0.76–0.96× at 8 heads; 0.71–1.00× at 32 and 64; unchanged at 16 | [round](data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md) |
