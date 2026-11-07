# Kernel Optimization

## Summary

`zai-org/GLM-5-1028-Provider` kernel-optimization tracking connects profile evidence to kernel changes, microbenchmarks, and end-to-end serving impact. Status: In progress. [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) validates the SM100 small-head FlashMLA sparse-prefill specialization on 8 and 32 local heads with BF16 Q/KV. All 36 cases match native head64 exactly and reduce median latency by 6.63–16.26%. Serving impact is linked separately. The original integration PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891); release gates remain open.

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

## Optimization Results

| Date | Kernel | Platform | Shape | Metric | Baseline | Candidate | Delta | Parity | End-to-End Impact | Round |
|---|---|---|---|---|---:|---:|---:|---|---|---|
| 2026-11-06 | Small-head sparse prefill | B300 | 8/32 heads; D512/D576; 8K–100K context | Median kernel latency | Native head64 | Compact small-head | −6.63–16.26% | Exact in 36/36 cases | [Serving E01](../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |

## Dispatch and Fallback Matrix

| Hardware | Shape or Mode | Preferred Path | Fallback | Gate | Status | Evidence |
|---|---|---|---|---|---|---|
| SM100 FlashMLA 1.0.3 | Prefill; 8/32 heads; BF16 Q/KV; no LSE | Compact small-head | Native head64 for LSE, dual-bank, decode, or unsupported shapes | Exact active-output parity | E01 passed for measured shapes | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |
| Older or mismatched FlashMLA wheel | Public capability probe unavailable | Native head64 | Native head64 | No startup failure | Probe behavior checked; serving not rerun | [Serving E01](../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| Hopper and other platforms | All small-head-eligible shapes | Native backend | Native backend | No architecture regression claimed | Not covered | None |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Profile and prioritize — In progress

- [x] Identify padded-head sparse-prefill work as the optimization target; completed 2026-11-06.
- [ ] Rank the remaining kernel regions by user-visible impact on locked release profiles.

### Stage 2: Implement and microbenchmark — In progress

- [x] Measure the small-head specialization on 8/32 heads and D512/D576; completed 2026-11-06.
- [x] Confirm exact parity and positive latency reduction in all 36 cases; completed 2026-11-06.
- [ ] Cover the remaining eligible head counts, edge cases, and platforms on the release candidate.

### Stage 3: Prove end-to-end impact — In progress

- [x] Record serving TTFT and throughput with actual small-head dispatch; completed 2026-11-06.
- [ ] Repeat long-context serving and rerun on locked release artifacts.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-06 | Small-head FlashMLA sparse prefill | B300; 8/32 heads; D512/D576; 8K–100K context | 36/36 exact; median latency −6.63–16.26%; no negative case | [round](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) |
