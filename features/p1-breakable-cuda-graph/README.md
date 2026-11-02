# Breakable CUDA Graph

## Summary

`<MODEL_NAME>` tracking for retaining graph replay benefits around operations that require eager execution. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

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

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
