# E09 FP8/NVFP4 MoE dispatch coverage — data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-moe-dispatch-coverage

## Environment

- Inspection: Python 3.12.3 standard-library AST and direct source review on a clean runtime worktree.
- Target deployment: four GB300 GPUs, TP4, standard fused MoE with all-to-all backend `none`.
- FP8 checkpoint revision: `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; dynamic FP8 E4M3, weight block size `[128, 128]`.
- NVFP4 checkpoint revision: `f2c64cebac62b1888c92c9d317adbb0b0aef5955`; performance-only artifact.
- This round is static inspection. It launches zero model servers and reports no new GPU measurements.

## Setup

Use a runtime checkout containing the pinned commit. Inspect committed objects so a different checked-out branch cannot change the result:

```bash
runtime_tree=/path/to/runtime-checkout
revision=01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb
git -C "$runtime_tree" show "$revision:python/sglang/srt/layers/quantization/modelopt_quant.py" | sha256sum
git -C "$runtime_tree" show "$revision:python/sglang/srt/layers/quantization/fp8.py" | sha256sum
git -C "$runtime_tree" show "$revision:python/sglang/srt/layers/quantization/modelopt_quant.py" | sed -n '3143,3182p;3216,3402p'
git -C "$runtime_tree" show "$revision:python/sglang/srt/layers/quantization/fp8.py" | sed -n '3311,3383p'
```

Compare file hashes with [dispatch-audit.json](dispatch-audit.json). Follow the explicit runner predicate, the FP8 resolver assignment, and the NVFP4 terminal exception. A branch existing in source is a candidate for GPU validation, not evidence that this checkpoint can run it.

The evaluated FP8 metadata is retained in [E04 private-release](../data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/fp8-source-config.json), SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`.

## Commit

- Code commit: `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`.
- Working tree: clean; the two inspected files match the committed objects.
- Source hashes and method line ranges: [dispatch-audit.json](dispatch-audit.json).

## Scripts

The reproduction commands above read immutable Git objects. The audit records the inspected method names, backend predicates, exception outcome and resolver target. Runtime source files remain in the code branch.

## Workload

Static inspection of `ModelOptNvFp4FusedMoEMethod.create_moe_runner/apply` and `Fp8MoEMethod._resolve_moe_runner_backend/create_moe_runner`. There are no requests, sampling settings or throughput aggregation in this round.

## Results

| Requested MoE runner | FP8 experts | NVFP4 experts | Evidence status |
|---|---|---|---|
| `flashinfer_trtllm` | Explicit runner path | Explicit NVFP4 path | Current matched deployments measured in E06–E08 |
| `deep_gemm` | Explicit runner path | Unsupported by the standard NVFP4 apply path | FP8 historical E05 exists; current-revision FP8 measurement remains pending; NVFP4 cell is unsupported |
| `flashinfer_cutlass` | Resolver selects `TRITON` | Explicit NVFP4 path exists | Checkpoint/GPU validation pending; a paired deployment would use different actual MoE backends |
| `flashinfer_cutedsl` | Resolver selects `TRITON` | Explicit NVFP4 path exists, with additional activation/layout conditions | Checkpoint/GPU validation pending; a paired deployment would use different actual MoE backends |
| `cutlass` | Outside this inspection's FP8 conclusion | Explicit `NotImplementedError` during runner creation | Distinct from `flashinfer_cutlass`; NVFP4 cell is unsupported |

The NVFP4 apply method contains no DeepGEMM dispatch and raises `NotImplementedError` for an unhandled runner. A launch may fail earlier; this source result does not claim an observed GPU exception. The FP8 resolver unconditionally maps explicit `flashinfer_cutlass` and `flashinfer_cutedsl` to Triton for FP8 experts. Global server arguments alone therefore cannot prove the expert kernel backend.

Current matched TRTLLM performance is recorded separately in [E06](../data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-kv-mtp-off/repro.md), [E07](../data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-natural-mtp/repro.md), and [E08](../data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-fixed-seed-mtp/repro.md). Historical FP8 DeepGEMM results in [E05](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-moe-sweep/repro.md) use a different runtime and are not a current paired baseline.

Remaining coverage: current-revision FP8 DeepGEMM performance with an explicit unsupported NVFP4 cell; matched alternative-runner deployments with actual per-expert dispatch evidence; model startup and stopping validation for each viable configuration. MegaMoE all-to-all, routed variants, LoRA and other hardware paths require their own evidence.

## Data and Figures

- [dispatch-audit.json](dispatch-audit.json): immutable file hashes, method ranges, dispatch predicates and scope.
- [SHA256SUMS](SHA256SUMS): checksums for this round.
