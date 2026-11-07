# NVIDIA Blackwell

## Summary

`zai-org/GLM-5-1028-Provider` tracking for establishing and validating the selected NVIDIA Blackwell configurations. Status: In progress. E03 used `a15aa7c3`; E04 used `8451a1bf` on `fix/glm5-lp-implementation`. The B300 TP8 MTP configuration completed full GSM8K at 93.86% accuracy with 99.24% stop rate, and GPQA-Diamond with a 4096-token output budget at 45.52% pass@1 and 69.19% pass@8 ([Correctness E03](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)). The optional vision SwiGLU fix passed unit, text/image, and full-GSM8K validation ([Correctness E04](../../p0-correctness/data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md)). GPQA truncation reached 51.33%. Small-head kernel/serving and host-L2/file-L3 experiments now have B300 evidence; non-MTP baselines, release performance gates, and additional configurations remain unvalidated.

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

- B300 MTP configuration: 8 B300 GPUs, `--tp-size 8`, `--moe-runner-backend deep_gemm`, EAGLE 3/1/4, decode CUDA graph, and prefill CUDA graph disabled.
- Dependencies in the evaluation environment: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`, and sgl-eval `0.1.3`; flashinfer was not installed.
- [ ] Record target workloads, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — In progress

- Experiment [Correctness E03](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md): full GSM8K and GPQA-4096 completed without request errors; GPQA results retain their 51.33% truncation boundary.
- Experiment [Correctness E04](../../p0-correctness/data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md): the optional vision SwiGLU fix passed 42 unit tests, text/image E2E, and full GSM8K at 95.22% accuracy with 99.32% stop rate.
- Experiment [Kernel Optimization E01](../../p0-kernel-opt/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md): all 36 small-head cases match native head64 exactly and reduce median latency by 6.63–16.26%.
- Experiment [General Performance E01](../../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md): cap-64 8K TTFT decreased by 4.31% on average, with +0.42% throughput; the 100K result needs repetition.
- Experiment [HiCache E01](../../p0-hicache/data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md): host L2 and file L3 passed eviction, full-restart, and clear-and-recompute checks with 18/18 correct answers.
- [ ] Record a non-MTP baseline using the same evaluation methodology.
- [ ] Repeat long-context serving and revalidate the locked upstream small-head implementation.
- [ ] Validate alternative parallel, storage-backend, and KV-cache configurations on B300.

## Experiments

B300 MTP accuracy is recorded as [Correctness E03](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md); optional vision SwiGLU fix validation is recorded as [Correctness E04](../../p0-correctness/data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md). Small-head kernel and serving evidence is recorded as [Kernel Optimization E01](../../p0-kernel-opt/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md) and [General Performance E01](../../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md). Host-L2/file-L3 evidence is recorded as [HiCache E01](../../p0-hicache/data/data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file/repro.md).
