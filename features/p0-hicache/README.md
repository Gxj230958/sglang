# Hierarchical KV Caching (HiCache)

## Summary

`<MODEL_NAME>` tracking for reusing prompt prefixes beyond GPU cache capacity. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## How It Works

HiCache extends prefix reuse across GPU memory (L1), host memory (L2), and an optional storage backend (L3). A hierarchical radix tree tracks local cached prefixes. Requests match local entries, fetch additional matching KV data from storage, and restore reusable state to the GPU before computation. Newly computed state can be written to lower tiers for later reuse. L1 and L2 belong to an individual inference instance; sharing across instances requires an L3 backend configured for that scope. Transfer cost and cache policy determine whether reuse improves latency.

Reference: [HiCache guide](https://docs.sglang.io/docs/advanced_features/hicache).

Design reference: [HiCache system design](https://docs.sglang.io/docs/advanced_features/hicache_design).

## Scope

### In Scope

- Cache-tier sizing, storage integration, and prefix-reuse workloads.
- Prefetch, write policies, eviction, and cold/warm cache comparisons.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Cache hits, misses, and evictions preserve output correctness.
- [ ] Cache hit rate, TTFT, transfer volume, and memory usage meet `<CACHE_PERFORMANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
