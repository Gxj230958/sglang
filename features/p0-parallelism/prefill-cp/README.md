# Prefill Context Parallelism

## Summary

`<MODEL_NAME>` tracking for sharing long-prompt computation across GPUs during prefill. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Prerequisite: complete [Analysis and Design](../analysis-and-design/README.md) before implementation.

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

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
