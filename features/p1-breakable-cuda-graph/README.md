# Breakable CUDA Graph

## Summary

Breakable prefill is now the default for GLM LoopLM after [#85](https://github.com/radixark/sglang-zai/pull/85) merged. [E02](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-prefill-graphs/repro.md) completes 144 historical paired loads; [General Performance E13](../p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-fp8kv-breakable/repro.md) adds 48 FP8-KV points and shows that the earlier natural-MTP deficit came from eager prefill. The H200 minimal-command check resolves and captures BCG, completes full GSM8K with zero errors and reproduces the same 11/14 image/tool checks as eager. Integrated default-profile selection remains in progress; full stopping and locked-artifact qualification remain unmet.

## How It Works

Breakable CUDA Graph divides a forward pass into captured segments separated by eager operations. Capture pauses at a graph break and resumes afterward; replay executes the saved segments and eager operations in order. This lets dynamic or otherwise non-capturable operations run outside a graph while surrounding GPU work retains reduced launch overhead. Selective breaks can also expose intermediate behavior for debugging. An all-eager debug path removes graph acceleration, so its performance is not representative of production replay.

Reference: [Breakable CUDA Graph guide](https://docs.sglang.io/docs/advanced_features/breakable_cuda_graph).

## Scope

### In Scope

- Identify necessary graph breaks and integrate the selected execution path.
- Validate eager/graph boundaries, replay correctness, and capture overhead.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Repeated replay matches eager execution for the supported input cases.
- [ ] Launch overhead, graph memory, and end-to-end latency meet `<GRAPH_PERFORMANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Measured scope: GB300 TP4, FP8/NVFP4 weights, BF16 KV, eager/breakable prefill and ordinary decode graphs; MTP off, natural EAGLE 3/1/4 and simulated acceptance 3.5. E02 uses chunk 8192. H200 TP8 graph comparison remains pending.
- Require paired FP8/NVFP4 measurements on a common source, with weight format separate from KV dtype and simulated acceptance separate from natural MTP.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Bind the measured breakable implementation to `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f` and all four Rust ranks (xinyuan, 2026-11-16).
- [x] Record the completed FP8 MTP-off load grid, GSM8K200 indicator and natural-MTP stopping probe in E01 (xinyuan, 2026-11-16).
- [x] Complete matched FP8/NVFP4 prefill graph performance coverage in E02 (xinyuan, 2026-11-16).
- [ ] Complete the 2048 capture cap and full stopping/correctness gates.
- [x] Complete current natural-MTP startup checks and separate fixed-length performance coverage in E02 (xinyuan, 2026-11-16).
- Experiment [E01](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-prefill/repro.md): 524 observed prefill forwards replayed graphs; capture adds about 5.77 GiB per rank; the MTP-off C32 score improves 2.84% over eager.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-16 | Rust breakable prefill | 4×GB300 TP4, FP8 weights, BF16 KV, C1–32, two seeds | 12 MTP-off loads pass; C32 +2.84%; natural-MTP sanity reaches length limit; paired NVFP4 pending | [round](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-prefill/repro.md) |
| E02 | 2026-11-16 | Paired prefill graphs | 4×GB300 TP4; FP8/NVFP4; eager/breakable; off/natural/simulated MTP; C1–32 | 144 loads; natural best C4 eager/C8 breakable; NV +26.00% at natural breakable C8; performance-only | [round](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-prefill-graphs/repro.md) |
| E03 | 2026-11-17 | FP8-KV breakable and default enablement | 4×GB300 TP4; FP8/NVFP4; FP8 KV; natural/off; C1–64 | 48 points, 8,704 successes; FP8-KV natural-MTP deficit attributed to eager prefill; #85 enables BCG by default | [round](../p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-fp8kv-breakable/repro.md) |
