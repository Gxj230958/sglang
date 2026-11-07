# Hierarchical KV Caching (HiCache)

## Summary

`zai-org/GLM-5-1028-Provider` tracking for reusing prompt prefixes beyond GPU cache capacity. Status: In progress. [E01](data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md) validates host L2 and file L3 on 8×B300 with BF16 KV. Host restore, file restore after a full process restart, and clear-and-recompute all returned correct answers with normal stop behavior in 18/18 semantic probes. Mooncake, direct external linker, FP8 KV, MTP, and other IO/layout combinations remain unvalidated.

## How It Works

HiCache extends prefix reuse across GPU memory (L1), host memory (L2), and an optional storage backend (L3). A hierarchical radix tree tracks local cached prefixes. Requests match local entries, fetch additional matching KV data from storage, and restore reusable state to the GPU before computation. Newly computed state can be written to lower tiers for later reuse. L1 and L2 belong to an individual inference instance; sharing across instances requires an L3 backend configured for that scope. Transfer cost and cache policy determine whether reuse improves latency.

Reference: [HiCache guide](https://docs.sglang.io/docs/advanced_features/hicache).

Design reference: [HiCache system design](https://docs.sglang.io/docs/advanced_features/hicache_design).

## Scope

### In Scope

- Cache-tier sizing, storage integration, and prefix-reuse workloads.
- Prefetch, write policies, eviction, and cold/warm cache comparisons.
- Host L2 and file L3 with BF16 KV, write-through, kernel IO, and page-first layout.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.
- Mooncake, direct external linker, FP8 KV, MTP, and alternative IO/layout combinations unless separately validated.

## Success Criteria

- [x] E01 cache hits, misses, evictions, process restart, and clear-and-recompute preserve output correctness in the covered cases.
- [ ] Cache hit rate, TTFT, transfer volume, and memory usage meet `<CACHE_PERFORMANCE_GATE>`.
- [ ] Validate the remaining required storage backends and feature combinations.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [x] Record the E01 workloads, dependencies, configuration boundaries, and correctness checks; completed 2026-11-06.
- [ ] Define acceptance thresholds for hit rate, TTFT, transfer volume, and host/storage capacity.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Validate host L2 and file L3 at `77c2b3bd19860ffaa6294fa983820e8cad70b83b`; completed 2026-11-06.
- [x] Record raw cache-source evidence and negative controls in a self-contained experiment round; completed 2026-11-06.
- [ ] Validate Mooncake, direct external linker, FP8 KV, MTP, and additional IO/layout combinations as required.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-06 | Host L2 and file L3 | 8×B300 TP8; BF16 KV; 65K device pool; 98K filler tokens | Host restore 4480/1408 tokens; restart storage restore 4480/1408/4416 tokens; 18/18 correct and stop | [round](data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md) |
