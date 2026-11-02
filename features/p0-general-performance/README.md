# General Performance

## Summary

`zai-org/GLM-5-1028-Provider` general-performance tracking measures controlled one-batch efficiency and online-serving behavior across representative workloads and platforms. Status: Not started. No performance has been measured; the H200 bring-up ran with CUDA graph disabled and recorded no performance metric. The target is `<PERFORMANCE_GOAL>` under `<SERVICE_LEVEL_OBJECTIVE>`, compared with `<REFERENCE_IMPLEMENTATION>` using identical methodology. Related code work is `<CODE_BRANCH_OR_PR>`, with dependencies on `<DEPENDENCIES>`.

## Scope

### In Scope

- Prefill and decode one-batch measurements.
- Online latency, throughput, concurrency scaling, and request failures.
- Memory capacity and scheduling behavior.
- Representative parallelism and backend configurations.
- Baseline comparison and release-candidate regression gates.

### Out of Scope

- Agentic-trace replay owned by `p0-agentx-performance`.
- Kernel-only microbenchmarks without end-to-end attribution.
- Results that do not pass the required correctness gate.

## Success Criteria

- [ ] Baseline and candidate use identical pinned methodology.
- [ ] Required workload and platform cells meet `<PERFORMANCE_GATE>`.
- [ ] Release profiles satisfy `<TTFT_GATE>`, `<ITL_GATE>`, and `<ERROR_RATE_GATE>`.
- [ ] Capacity limits and out-of-memory boundaries are documented.
- [ ] Every published number links to raw evidence and `<CODE_SHA>`.

## Workload Matrix

| Workload ID | Input Shape | Output Shape | Request Distribution | Batch or Concurrency | Sampling | Purpose | Status |
|---|---|---|---|---|---|---|---|
| `<WORKLOAD_ID>` | `<INPUT_SHAPE>` | `<OUTPUT_SHAPE>` | `<DISTRIBUTION>` | `<LOAD_SHAPE>` | `<SETTINGS>` | `<PURPOSE>` | `<STATUS>` |

## Performance Results

No performance results recorded yet.

## Release Profiles

| Profile | Target User | Hardware | Configuration | Workload Envelope | Expected SLO | Evidence | Status |
|---|---|---|---|---|---|---|---|
| `<PROFILE>` | `<USER_SCENARIO>` | `<HARDWARE>` | `<CONFIGURATION>` | `<ENVELOPE>` | `<SLO>` | `<ROUND_PATH>` | `<STATUS>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Freeze methodology and baseline — Not started

- [ ] Pin workloads, metrics, warmup, repetitions, and environment.
- [ ] Measure `<REFERENCE_IMPLEMENTATION>` on required platforms.
- [ ] Record capacity and failure boundaries.
- Next action: define the workload matrix and methodology, then measure the H200 TP8 configuration with CUDA graph enabled after it passes the correctness accuracy gate.

### Stage 2: Optimize release profiles — Not started

- [ ] Measure `<CANDIDATE_CONFIGURATION_SET>`.
- [ ] Attribute material changes to code, configuration, or environment.
- [ ] Select profiles that satisfy correctness and service-level gates.

### Stage 3: Revalidate locked artifacts — Not started

- [ ] Rerun the required matrix on `<CODE_SHA>` and `<MODEL_REVISION>`.
- [ ] Confirm no release profile depends on an unpinned component.
- [ ] Publish reviewed profiles to the delivery cookbook.

## Experiments

No experiments recorded yet.
