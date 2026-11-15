# Hierarchical KV Caching (HiCache)

## Summary

`zai-org/GLM-5-1028-Provider` tracking for reusing prompt prefixes beyond GPU cache capacity. Status: In progress. [E01](data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md) validates host L2 and file L3 on 8×B300 with BF16 KV. Host restore, file restore after a full process restart, and clear-and-recompute all returned correct answers with normal stop behavior in 18/18 semantic probes. On the hybrid window KV layout with MTP (4×GB300, TP4, BF16 KV), host L2 and file L3 restores return the full cached prefix with all probe answers correct, and full GSM8K passes with HiCache enabled: 94.84% accuracy and 99.77% stop at `e1ac59e6` ([E02](data/data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3/repro.md)), 95.22% and 99.62% at `704d3082` ([E03](data/data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3/repro.md)). The launch fix those rounds validate is on `glm-5-lp` as `8d9f8c21`; `radixark/sglang-zai` pull request 59, which carried the same fix, was closed as superseded. HiCache on a PD prefill server is recorded in [PD Disaggregation E03](../p0-pd-disagg/data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md). Mooncake storage, direct external linker, FP8 KV, and other IO/layout combinations remain unvalidated.

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
- [x] Validate host L2 and file L3 on the hybrid window layout with MTP at `e1ac59e6` and `704d3082` ([E02](data/data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3/repro.md), [E03](data/data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3/repro.md)); completed 2026-11-13.
- Fix: a static window pool with a host stack failed at launch because pool names were read as enum values; fixed on `glm-5-lp` by `8d9f8c21` with a regression test. Pull request 59 was closed on 2026-11-14 as superseded by that commit.
- Observation from [E02](data/data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3/repro.md): with `--hicache-size 32` the host pool is smaller than the device pool on this configuration; the run is kept in the round and was not investigated further.
- [ ] Validate Mooncake, direct external linker, FP8 KV, HiCache under prefill CP, and additional IO/layout combinations as required.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-06 | Host L2 and file L3 | 8×B300 TP8; BF16 KV; 65K device pool; 98K filler tokens | Host restore 4480/1408 tokens; restart storage restore 4480/1408/4416 tokens; 18/18 correct and stop | [round](data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md) |
| E02 | 2026-11-12 | Host L2 and file L3 on the window layout | 4×GB300 TP4; MTP; BF16 KV; `--hicache-size 64`; file backend; `710bcb2a` + `e1ac59e6` fix | GSM8K 94.84% accuracy, 99.77% stop; host and storage restores 6656 cached tokens, 6/6 correct each | [round](data/data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3/repro.md) |
| E03 | 2026-11-13 | Window layout L2 and L3 after the rebase | Same configuration at `704d3082` | GSM8K 95.22% accuracy, 99.62% stop; host and storage restores 6656 cached tokens, 6/6 correct each | [round](data/data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3/repro.md) |
