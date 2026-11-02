# Decode Context Parallelism

## Summary

`<MODEL_NAME>` tracking for reducing per-rank decode KV storage and reads for supported attention paths. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Prerequisite: complete [Analysis and Design](../analysis-and-design/README.md) before implementation.

## How It Works

In the documented MLA path, DCP distributes KV entries by token position across ranks within an existing attention tensor-parallel group. Each rank attends to its local context shard and produces a partial output with normalization statistics. A collective exchanges these values, and a log-sum-exp weighted merge reconstructs the full-context result. This reduces per-rank cache storage and reads while adding communication each step. DCP groups must stay within an attention-TP group and a single attention-DP replica; backend and feature combinations need explicit validation.

Reference: [Decode context parallelism guide](https://docs.sglang.io/docs/advanced_features/dcp).

## Scope

### In Scope

- KV ownership, virtual token mapping, partial attention, and collective merging.
- Long-context capacity and compatibility with the selected serving features.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Sharded attention agrees with the reference within `<NUMERICAL_TOLERANCE>`.
- [ ] Long-context capacity and decode latency meet `<DECODE_GATE>`.

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
