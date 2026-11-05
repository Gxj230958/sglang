# Multi-Platform Support

## Summary

`zai-org/GLM-5-1028-Provider` tracking for selecting and validating the hardware platforms required for the model release. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. [NVIDIA Hopper](nvidia-hopper/README.md) has H200 bring-up and accuracy evidence; [NVIDIA Blackwell](nvidia-blackwell/README.md) has B300 MTP full GSM8K and GPQA-4096 evidence. The other subprojects have no selection decision yet. Target workloads and acceptance thresholds remain to be defined.

## Subprojects

We select the features we need from the subdirectories below for implementation.

| Directory | Focus |
|---|---|
| [NVIDIA Hopper](nvidia-hopper/README.md) (`nvidia-hopper/`) | Track the required Hopper GPU configurations. |
| [NVIDIA Blackwell](nvidia-blackwell/README.md) (`nvidia-blackwell/`) | Track the required Blackwell GPU configurations. |
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

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Record selected and deferred subprojects with the reasons for each decision.
- Next action: decide which platforms beyond NVIDIA Hopper the release requires and record each decision here.

### Stage 2: Implement and validate the selected scope — In progress

- [NVIDIA Hopper](nvidia-hopper/README.md): In progress; H200 TP8 baseline recorded as [Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md).
- [NVIDIA Blackwell](nvidia-blackwell/README.md): In progress; B300 MTP full GSM8K and GPQA-4096 recorded as [Correctness E03](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md).
- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No platform-level experiments are recorded. Subproject evidence is linked from each subproject README.
