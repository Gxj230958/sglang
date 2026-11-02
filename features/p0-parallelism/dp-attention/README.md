# DP Attention

## Summary

`<MODEL_NAME>` tracking for scaling attention request capacity while coordinating the remaining model layers. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

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

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
