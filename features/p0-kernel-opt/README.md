# Kernel Optimization

## Summary

`<MODEL_NAME>` kernel-optimization tracking connects profile evidence to kernel changes, microbenchmarks, and end-to-end serving impact. The project is `<STATUS>`; its target is `<KERNEL_GOAL>` without violating `<CORRECTNESS_OR_PORTABILITY_CONSTRAINT>`. Related code work is `<CODE_BRANCH_OR_PR>`, with dependencies on `<BACKEND_OR_HARDWARE_DEPENDENCIES>`.

## Scope

### In Scope

- Profile-based kernel bottleneck identification.
- Kernel implementation, dispatch, fusion, and launch optimization.
- Microbenchmark and numerical-parity validation.
- End-to-end latency, throughput, memory, and compatibility attribution.
- Architecture-specific paths with explicit fallback behavior.

### Out of Scope

- Configuration-only tuning with no kernel change.
- Optimizations without correctness coverage or a supported fallback.
- Microbenchmark wins that do not improve a target end-to-end workload.

## Success Criteria

- [ ] Every optimization starts from profile evidence pinned to `<CODE_SHA>`.
- [ ] Numerical parity meets `<PARITY_GATE>` across required shapes and dtypes.
- [ ] Microbenchmark improvement meets `<MICROBENCHMARK_GATE>`.
- [ ] End-to-end improvement meets `<END_TO_END_GATE>` without regression elsewhere.
- [ ] Dispatch boundaries and fallback behavior are tested.
- [ ] Required hardware and software architectures are covered.

## Kernel Inventory

| Kernel or Region | Operation | Shapes and Dtypes | Backend | Bottleneck | Baseline | Target | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| `<KERNEL>` | `<OPERATION>` | `<SHAPES_AND_DTYPES>` | `<BACKEND>` | `<BOTTLENECK>` | `<BASELINE>` | `<TARGET>` | `<OWNER>` | `<STATUS>` |

## Optimization Results

| Date | Kernel | Platform | Shape | Metric | Baseline | Candidate | Delta | Parity | End-to-End Impact | Round |
|---|---|---|---|---|---:|---:|---:|---|---|---|
| `<YYYY-MM-DD>` | `<KERNEL>` | `<PLATFORM>` | `<SHAPE>` | `<METRIC>` | `<BASELINE>` | `<CANDIDATE>` | `<DELTA>` | `<PARITY_RESULT>` | `<END_TO_END_RESULT>` | `data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md` |

## Dispatch and Fallback Matrix

| Hardware | Shape or Mode | Preferred Path | Fallback | Gate | Status | Evidence |
|---|---|---|---|---|---|---|
| `<HARDWARE>` | `<SHAPE_OR_MODE>` | `<PREFERRED_PATH>` | `<FALLBACK_PATH>` | `<GATE>` | `<STATUS>` | `<ROUND_PATH>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Profile and prioritize — `<STATUS>`

- [ ] Capture `<PROFILE_TYPE>` on representative workloads.
- [ ] Rank kernel regions by user-visible impact.
- [ ] Define parity, performance, and portability gates.

### Stage 2: Implement and microbenchmark — `<STATUS>`

- [ ] Implement `<OPTIMIZATION>` with explicit dispatch boundaries.
- [ ] Validate required shapes, dtypes, edge cases, and fallbacks.
- [ ] Record microbenchmark results and profile changes.

### Stage 3: Prove end-to-end impact — `<STATUS>`

- [ ] Run correctness and general-performance gates.
- [ ] Attribute end-to-end changes to the kernel work.
- [ ] Rerun on locked release artifacts and required platforms.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<HARDWARE>; <KERNEL>; <SHAPE>` | `<RESULT>` | `data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md` |
