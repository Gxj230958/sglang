# DP Attention

## Summary

**Backend validation:** E01, E02 serving results used the Python tree core. They remain historical measurements; default-Rust validation and deployment selection require new runs. See the [Rust validation contract](../../p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/2026-11-16-0845-xinyuan-dbfef91e7d-rust-validation-contract.md).

`zai-org/GLM-5-1028-Provider` tracking for scaling attention request capacity while coordinating the remaining model layers. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp`; attention DP needed no code change for the hybrid window KV layout. With MTP and decode CUDA graphs the window layout passes full GSM8K under TP4 + EP4 + DP4 with DeepEP on 4×GB300 at `710bcb2a` ([E01](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md): 94.16% accuracy, 99.47% stop) and under TP8 + EP8 + DP8 with the `trtllm` DSA backend and FP8 KV on 8×B300 at `e941d571` ([E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md): 94.16%, 99.85%). Full-length DEP8 gates on later commits are in [Correctness](../../p0-correctness/README.md) E08–E10. Random-record retrieval at 60K tokens and above on the DEP8 FP8 configuration misses at the same rate on TP8 with BF16 KV, so attention DP and FP8 KV are not the cause ([Correctness E11](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), [E12](../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)). All results are single runs on unlocked environments and are non-release. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

[E03 current paired Rust validation](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-dp4/repro.md) measures TP4/EP4/attention-DP4 with all-to-all `none`, FP8 KV and natural MTP at `01d0a662d1`. FP8: 1249/1319 correct, 1308 stop; NVFP4: 1251 correct, 1313 stop, both zero errors. All 18 retrieval and 16 directed routing/cache probes pass per format, with all four Rust worker mappings verified. Full stopping nonregression remains unmet; DeepEP and CP/DP composition need separate current evidence.

[E04 paired TP4/DEP4 performance](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-tp4-dep4-performance/repro.md) completes 100 loads on current `01d0a662d1`: separate natural sanity, MTP-off and simulated acceptance 3.5, paired FP8/NVFP4. Off best passing concurrency is C32 for TP4 and C16 for DEP4, with NVFP4 gains 16.65% and 15.00%; controlled TP4 C32 is a near tie (+1.32%) with repeat dispersion retained. All actual topology tuples, scheduler subdivisions and raw data are audited. Results are performance-only.

[Fallback correctness E27](../../p0-correctness/data/data@2026-11-17-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-dp4/repro.md) records candidate `52ef77912f`: FP8/NVFP4 complete full GSM8K with 1250/1247 correct and 1313 stops each. Four actual Rust workers and directed routing/cache16/16 verify per format. Retrieval passes17/18 for FP8 and18/18 for NVFP4; the FP8 cold wrong answer remains under bounded diagnosis.

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
- [x] Record paired current TP4/DEP4 KV capacity, concurrency and serving throughput in E04 (xinyuan, 2026-11-16).

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-12 | Window layout under DEP4 | 4×GB300; TP4 + EP4 + DP4; DeepEP; MTP; `710bcb2a` | Python tree core; Rust rerun pending. 94.16% accuracy, 99.47% stop; probes 12/12; prefix reuse 6/6 correct | [round](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md) |
| E02 | 2026-11-13 | Window layout under DEP8 | 8×B300; TP8 + EP8 + DP8; `trtllm`; FP8 KV; MTP; `e941d571` | Python tree core; Rust rerun pending. 94.16% accuracy, 99.85% stop; probes 18/18 to 120936 tokens; prefix reuse 6/6 correct | [round](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md) |
| E03 | 2026-11-16 | Paired current Rust DP4 | 4×GB300; TP4/EP4/DP4; a2a none; FP8 KV; natural MTP; FP8/NVFP4 | Correct/stop FP8 1249/1308, NVFP4 1251/1313 of 1319; probes 18+16 pass each; stopping qualification unmet | [round](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-dp4/repro.md) |
| E04 | 2026-11-16 | Paired TP4/DEP4 performance | 4×GB300; FP8/NVFP4; FP8 KV; off/controlled MTP and natural sanity; C1–32 | 100 loads; off best C32 TP4/C16 DEP4; NV gains 16.65%/15.00%; performance-only | [round](data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-tp4-dep4-performance/repro.md) |
