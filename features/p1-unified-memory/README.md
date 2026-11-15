# Unified Memory

## Summary

`zai-org/GLM-5-1028-Provider` tracking for evaluating unified-memory support for the selected model and hardware. Status: In progress; only design scoping has been done. Related code work: none; `radixark/sglang-zai` branch `glm-5-lp` at `710bcb2a` was read to scope the port. Unified memory is unsupported for this model: `--enable-unified-memory` does not serve the DSA attention backend on either KV layout, and the launch rejection for the hybrid window layout is the outermost of several blockers. No experiment has been run and there is no support or capacity claim. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Unified memory replaces hybrid pools only, so for this model it applies to the hybrid window layout. The staged port plan is recorded under Stage 1; the supported platform set is not selected yet.

## Scope

### In Scope

- Define which allocations are eligible and select the runtime mechanism.
- Measure memory placement, movement, capacity limits, and latency under the target workload.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Supported allocations and hardware/runtime prerequisites are documented.
- [ ] Correctness, peak memory usage, and latency satisfy `<MEMORY_ACCEPTANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Blockers at `710bcb2a`, in the order a launch meets them (from reading the code; none was exercised on a GPU):
  1. The page-major MLA backend allow-list in `arg_groups/kv_cache_hook.py` does not contain `dsa`.
  2. `mem_cache/kv_cache_configurator.py` asserts that a window plan does not use an MLA backend and hard-codes an MHA geometry for the window.
  3. The unified MLA view has no index-K storage and none of the pool attributes the DSA backend reads (FP8 store flag, KV scale, KV dimension, index page size).
  4. The DSA backend reads the request-to-token table and the pool directly at about 38 sites and writes with bare locations; the unified pool hands out virtual ids and refuses write locations that are not marked physical.
  5. The loop attention translates window ids with a pool method the unified pool does not have, and the unified translation maps an out-of-range `-1` to the sink row, so the `-1` mask the sparse kernel relies on must be restored after translating.
  6. MTP: the NextN draft has to become a fused draft region with its own index-K, and unified memory with EAGLE currently refuses HiCache.
- Proposed stages, each as its own pull request with a serve and GSM8K gate:
  1. Unified plan: an MLA full side with a DSA index-K derived part and an MLA window sub-pool, plus the pool attributes the backend reads.
  2. DSA backend on translated runner ids: all page-table and Top-K reads translated, writes through layer write locations, window write ids buffered outside the decode graph; audit of the remaining sparse kernels against strided, page-major KV views.
  3. Loop attention on the unified window sub-pool with the `-1` mask restored, the allow-list entry, and the launch rejection lifted; `flashmla_sparse` with BF16 KV and without MTP first.
  4. Fused MTP draft, then the `trtllm` routes, PD and HiCache on the unified pool.
- A strided-view check of the legacy sparse prefill kernel was run once on GB300 during scoping; its output was not retained, so it must be repeated and recorded before stage 2.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
