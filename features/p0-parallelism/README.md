# Parallelism

## Summary

`<MODEL_NAME>` tracking for choosing a compatible parallelism design for the target model, workload, and hardware topology. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

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

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Complete Analysis and Design before starting any concrete parallelism implementation.
- [ ] Record selected and deferred subprojects with the reasons for each decision.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
