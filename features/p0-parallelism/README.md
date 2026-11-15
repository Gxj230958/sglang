# Parallelism

## Summary

`zai-org/GLM-5-1028-Provider` tracking for choosing a compatible parallelism design for the target model, workload, and hardware topology. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. The only validated layout is plain TP8 on 8 H200 GPUs ([Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)). The implementation rejects pipeline parallelism, prefill context parallelism, and decode context parallelism at launch; these constraints are recorded in [Analysis and Design](analysis-and-design/README.md), which is not complete. Target workload and acceptance thresholds remain to be defined.

**Complete [Analysis and Design](analysis-and-design/README.md) before implementing DP Attention, Prefill CP, Decode CP, PP, or WideEP.** The design must record the chosen features, rank mapping, composition constraints, communication interfaces, and acceptance gates.

## Subprojects

We select the features we need from the subdirectories below for implementation.

| Directory | Focus |
|---|---|
| [Analysis and Design](analysis-and-design/README.md) (`analysis-and-design/`) | Required prerequisite: choose the topology, interfaces, and validation plan. |
| [DP Attention](dp-attention/README.md) (`dp-attention/`) | Distribute attention requests and their KV caches across replicas. |
| [Prefill CP](prefill-cp/README.md) (`prefill-cp/`) | Distribute prompt-token computation during prefill. |
| [Decode CP](decode-cp/README.md) (`decode-cp/`) | Shard decode context and combine partial attention outputs. |
| [PP](pp/README.md) (`pp/`) | Partition model layers into pipeline stages. |
| [WideEP](wide-ep/README.md) (`wide-ep/`) | Plan expert parallelism across the selected device topology. |

## Scope

### In Scope

- Model decomposition, rank groups, communication, memory ownership, and supported combinations.
- Selection and validation of the required parallelism subprojects.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Analysis and Design is complete before implementation of any concrete parallelism feature starts.
- [ ] Selected combinations pass correctness and meet `<CAPACITY_GATE>` and `<PERFORMANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- Baseline: `--tp-size 8` without expert parallelism or attention data parallelism, validated on 8 H200 GPUs in [Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md).
- Constraint: `--pipeline-parallel-size > 1`, `--attn-cp-size > 1`, `--enable-prefill-cp`, and `--dcp-size > 1` are rejected at launch at `a15aa7c3`; see [Analysis and Design](analysis-and-design/README.md).
- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Complete Analysis and Design before starting any concrete parallelism implementation.
- [ ] Record selected and deferred subprojects with the reasons for each decision.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Prefill CP for the hybrid window KV layout: `radixark/sglang-zai` pull request 57, merged as `5337c504`; evidence in [Prefill CP](prefill-cp/README.md) E01–E03; completed 2026-11-15.
- [x] Attention DP with expert parallelism on the hybrid window KV layout (DEP4 on GB300, DEP8 on B300): evidence in [DP Attention](dp-attention/README.md) E01–E02; completed 2026-11-13.
- [ ] Record performance evidence for the selected combinations.

## Experiments

Experiment rounds are recorded in the subprojects: [Prefill CP](prefill-cp/README.md) E01–E03 and [DP Attention](dp-attention/README.md) E01–E02.
