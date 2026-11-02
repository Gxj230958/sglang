# Pipeline Parallelism (PP)

## Summary

`<MODEL_NAME>` tracking for partitioning model execution across pipeline stages for the target context lengths and topology. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

Prerequisite: complete [Analysis and Design](../analysis-and-design/README.md) before implementation.

## How It Works

Pipeline parallelism assigns successive model layers to different stages and passes activations between them. SGLang uses microbatches and asynchronous point-to-point communication to overlap stage computation, transfers, and CPU scheduling. Chunked prefill allows different chunks of a long prompt to occupy different stages concurrently. Optional dynamic chunking adjusts chunk sizes as context grows to balance execution time and reduce idle pipeline periods. Layer placement, chunk sizes, and communication latency determine utilization and end-to-end performance.

Reference: [Pipeline parallelism guide](https://docs.sglang.io/docs/advanced_features/pipeline_parallelism).

## Scope

### In Scope

- Layer partitioning, stage interfaces, asynchronous transfers, and scheduling.
- Fixed and dynamic prefill chunking for the selected topology.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Stage boundaries and chunked execution preserve reference correctness.
- [ ] Long-context TTFT, throughput, and stage utilization meet `<PIPELINE_GATE>`.

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
