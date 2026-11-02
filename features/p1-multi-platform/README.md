# Multi-Platform Support

## Summary

`<MODEL_NAME>` tracking for selecting and validating the hardware platforms required for the model release. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## Subprojects

We select the features we need from the subdirectories below for implementation.

| Directory | Focus |
|---|---|
| [NVIDIA Hopper](nvidia-hopper/README.md) (`nvidia-hopper/`) | Track the required Hopper GPU configurations. |
| [AMD](amd/README.md) (`amd/`) | Track the required AMD accelerator configurations. |
| [Intel XPU/Xeon](intel-xpu-xeon/README.md) (`intel-xpu-xeon/`) | Track Intel accelerator and Xeon CPU configurations separately. |
| [Ascend NPU](ascend-npu/README.md) (`ascend-npu/`) | Track the required Ascend NPU configurations. |
| [TPU](tpu/README.md) (`tpu/`) | Track the required TPU configurations. |

## Scope

### In Scope

- Select target platforms and define their runtime, kernel, precision, and feature requirements.
- Track platform-specific correctness, performance, and deployment evidence.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Each selected platform has a reproducible environment and documented support boundaries.
- [ ] Required configurations pass `<CORRECTNESS_GATE>` and `<PLATFORM_PERFORMANCE_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Record selected and deferred subprojects with the reasons for each decision.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
