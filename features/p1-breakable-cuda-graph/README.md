# Breakable CUDA Graph

## Summary

`zai-org/GLM-5-1028-Provider` tracking for retaining graph replay benefits around operations that require eager execution. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. Ordinary decode CUDA graph with EAGLE 3/1/4 returned a normal response with `accept len=2.27` and `cuda graph: True` ([Correctness E02](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)). This is prerequisite evidence only; no breakable backend or eager/graph boundary has been exercised.

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

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Current scope: H200 TP8, EAGLE 3/1/4, and decode CUDA graph; replay must preserve generation correctness and normal stop behavior.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.
- Next action: select the breakable backend, exercise an eager/graph boundary, and compare the result with eager execution.

## Experiments

No breakable-graph experiment is recorded. Ordinary decode-graph prerequisite evidence is recorded in [Correctness E02](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md).
