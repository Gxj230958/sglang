# NVIDIA Hopper

## Summary

`zai-org/GLM-5-1028-Provider` tracking for establishing and validating the selected NVIDIA Hopper configurations for the target model. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. The H200 TP8 baseline passed text, image, and long-context smokes ([Correctness E01](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)). GSM8K-200 reached 95.50% accuracy with 100% stop rate and 0% truncation; built-in MTP returned `accept len=2.27` with `cuda graph: True` ([Correctness E02](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)). H200 MTP full GSM8K reached 94.31% accuracy with 99.39% stop rate; GPQA reached 52.53% pass@1 and 75.76% pass@8 with 43.31% truncation at context length 8192 ([Correctness E05](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)). Performance and additional configurations remain unvalidated.

## Scope

### In Scope

- Pin the device type, runtime, dependencies, model revision, and execution backend.
- Track kernel coverage, supported precision, feature compatibility, and deployment requirements.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] The selected configurations reproduce from a documented environment and exact code commit.
- [ ] Correctness, capacity, and performance meet the platform-specific release gates.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- H200 baseline configuration: 8 H200 GPUs, `--tp-size 8`, `--moe-runner-backend triton`, default DSA backends (FlashMLA Sparse), BF16 KV cache, `--disable-cuda-graph`, no MTP.
- Dependencies in the baseline environment: torch `2.14.1+cu130`, flashinfer `0.7.1`, transformers `5.19.0`, sgl-flash-mla `1.0.0`, sglang-kernel `0.4.10`; DeepEP not installed.
- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — In progress

- Experiment [Correctness E01](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md): at `a15aa7c3`, the H200 TP8 baseline passed the dual-bank attention test (4 passed, 2 platform-dependent skipped) and the text, image, and long-context smokes.
- Experiment [Correctness E02](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md): GSM8K-200 reached 95.50% accuracy with 100% stop rate and 0% truncation; built-in MTP returned `accept len=2.27` with `cuda graph: True`.
- Experiment [Correctness E05](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md): H200 MTP full GSM8K reached 94.31% accuracy with 99.39% stop rate; GPQA reached 52.53% pass@1 and 75.76% pass@8 with 43.31% truncation at context length 8192.
- [ ] Record performance evidence on H200 in a self-contained experiment round.
- [ ] Validate alternative parallel and KV-cache configurations on H200.

## Experiments

The H200 baseline is recorded as [Correctness E01](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md); accuracy and MTP with decode CUDA graph are recorded as [Correctness E02](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md); full MTP evaluation is recorded as [Correctness E05](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md).
