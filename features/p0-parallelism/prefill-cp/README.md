# Prefill Context Parallelism

## Summary

`zai-org/GLM-5-1028-Provider` tracking for sharing long-prompt computation across GPUs during prefill. Status: In progress. Related code work: `radixark/sglang-zai` pull request 57, merged into `glm-5-lp` as `5337c504`, which runs the hybrid window KV sub-pool under prefill CP. With interleaved CP, MTP and decode CUDA graphs the window layout passes full GSM8K at CP4 on 4×GB300 ([E01](data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md): 95.30% accuracy, 99.92% stop, against 94.16% / 99.92% for the full-length layout in the same configuration), at CP4 on GB300 and CP8 on 8×B300 after a rebase ([E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md): 94.69% / 100% and 95.68% / 99.92%), and at CP4 on the branch containing the upstream `main` merge ([E03](data/data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev/repro.md): 94.47% / 99.92%). Retrieval probes are correct up to 120936 prompt tokens except one of three at that length on CP8. All results are single runs on unlocked environments and are non-release. Not validated: the `trtllm` DSA backend under CP, HiCache under CP, and CP prefill under PD. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Prerequisite: complete [Analysis and Design](../analysis-and-design/README.md) before implementation.

Constraint history: the implementation at `a15aa7c3` rejected `--attn-cp-size > 1` and `--enable-prefill-cp` because the current-cycle window is built over the whole packed query range; see [Analysis and Design](../analysis-and-design/README.md). At `710bcb2a` the full-length layout runs under prefill CP ([E01](data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md) reference arm) and only the window sub-pool was rejected; pull request 57 lifts that rejection.

## How It Works

Prefill CP partitions prompt tokens across an attention group. Each rank computes its local queries while exchanging KV data needed for attention. The zigzag layout pairs early and late token blocks to balance causal-attention work; the interleave layout distributes token positions round-robin. Metadata preserves each request’s positions and causal boundaries. This partitions prompt computation, whereas decode CP partitions context during generation. Strategy, model, and attention-backend compatibility must be checked before composing CP with other features.

Reference: [Prefill context parallelism guide](https://docs.sglang.io/docs/advanced_features/prefill_cp).

## Scope

### In Scope

- Token partitioning, causal metadata, KV exchange, and output reconstruction.
- Long prompts, uneven lengths, cached prefixes, and selected backend combinations.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Uneven prompt lengths and cached-prefix cases match the reference outputs.
- [ ] Prefill latency, communication cost, and memory usage meet `<PREFILL_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Configuration used by every round: `--enable-prefill-cp --cp-strategy interleave --attn-cp-size <4|8> --cuda-graph-backend-prefill breakable` with `--context-length 131072`.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Link implementation work: `radixark/sglang-zai` pull request 57, gated at `0c95a2b1`, `e941d571` and `f02daab4`, squash-merged as `5337c504`; completed 2026-11-15.
- [x] Record correctness evidence in self-contained rounds: [E01](data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md), [E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md), [E03](data/data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev/repro.md); completed 2026-11-15.
- Experiment [E01](data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md): at the same memory fraction the window layout holds 304640 full-layer tokens against 234560 for the full-length layout (+29.9%).
- Open item from [E02](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md): on CP8 one of three 120936-token probes returned a wrong code with `stop`; the GB300 CP4 probes at that length are all correct.
- [ ] Validate the `trtllm` DSA backend and HiCache under prefill CP.
- [ ] Record prefill latency, communication cost and memory usage; no performance evidence exists yet.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-12 | Window layout under CP4 | 4×GB300; TP4; interleaved CP4; MTP; ctx 131072; `710bcb2a` + `0c95a2b1` patch | Window 95.30% accuracy, 99.92% stop; full-length 94.16%, 99.92%; probes 18/18 on both to 120936 tokens | [round](data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md) |
| E02 | 2026-11-13 | Window layout under CP4 (GB300) and CP8 (B300) | `e941d571`; GB300 TP4 CP4; 8×B300 TP8 CP8 | CP4 94.69% / 100% stop; CP8 95.68% / 99.92% stop, probes 17/18, prefix reuse 6/6 | [round](data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md) |
| E03 | 2026-11-15 | Window layout under CP4 after the main merge | 4×GB300; `f02daab4`; bumped kernel packages | 94.47% accuracy, 99.92% stop; probes 18/18; prefix reuse 6/6 | [round](data/data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev/repro.md) |
