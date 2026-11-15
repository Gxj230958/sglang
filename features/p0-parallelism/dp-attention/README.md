# DP Attention

## Summary

`zai-org/GLM-5-1028-Provider` tracking for scaling attention request capacity while coordinating the remaining model layers. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp`; attention DP needed no code change for the hybrid window KV layout. With MTP and decode CUDA graphs the window layout passes full GSM8K under TP4 + EP4 + DP4 with DeepEP on 4×GB300 at `710bcb2a` ([E01](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md): 94.16% accuracy, 99.47% stop) and under TP8 + EP8 + DP8 with the `trtllm` DSA backend and FP8 KV on 8×B300 at `e941d571` ([E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md): 94.16%, 99.85%). Full-length DEP8 gates on later commits are in [Correctness](../../p0-correctness/README.md) E08–E10. Random-record retrieval at 60K tokens and above on the DEP8 FP8 configuration misses at the same rate on TP8 with BF16 KV, so attention DP and FP8 KV are not the cause ([Correctness E11](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), [E12](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)). All results are single runs on unlocked environments and are non-release. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Prerequisite: complete [Analysis and Design](../analysis-and-design/README.md) before implementation.

## How It Works

DP Attention assigns different request batches to attention replicas, each maintaining the KV cache for its assigned requests. For MLA models, this avoids duplicating the same request cache across all attention ranks as ordinary tensor parallelism can do. Other layers can use their own parallel layout; MoE layers may use expert parallelism with token dispatch and combine collectives. Attention DP therefore differs from replicating the entire model, and it does not require expert parallelism. Request routing and compatible rank groups are part of the design.

Reference: [DP, DPA, and SGLang DP Router guide](https://docs.sglang.io/docs/advanced_features/dp_dpa_smg_guide).

## Scope

### In Scope

- Attention replica groups, request routing, and per-replica cache ownership.
- Layout transitions to dense or expert layers and imbalanced replica workloads.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Mixed request batches and selected layer layouts preserve correctness.
- [ ] KV memory usage, supported concurrency, and throughput meet `<PERFORMANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Observation: requests of one conversation can land on different DP ranks, so warm-prefix requests report few or no cached tokens under DP4 and DP8; answers stay correct.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Record correctness evidence for the window layout: [E01](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md) (DEP4, GB300), [E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md) (DEP8, B300); completed 2026-11-13.
- [x] Attribute the long-context random-record retrieval misses on DEP8 with FP8 KV ([Correctness E11](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md)): BF16 KV, TP8 and thinking-on arms miss at the same rate ([Correctness E12](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)); no serving configuration attributed, treated as non-blocking; completed 2026-11-15.
- [ ] Record KV memory usage, supported concurrency and throughput; no performance evidence exists yet.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-12 | Window layout under DEP4 | 4×GB300; TP4 + EP4 + DP4; DeepEP; MTP; `710bcb2a` | 94.16% accuracy, 99.47% stop; probes 12/12; prefix reuse 6/6 correct | [round](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md) |
| E02 | 2026-11-13 | Window layout under DEP8 | 8×B300; TP8 + EP8 + DP8; `trtllm`; FP8 KV; MTP; `e941d571` | 94.16% accuracy, 99.85% stop; probes 18/18 to 120936 tokens; prefix reuse 6/6 correct | [round](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md) |
