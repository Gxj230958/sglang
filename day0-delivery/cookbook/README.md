# Cookbook Template

## Purpose

The cookbook turns validated Day-0 model results into reproducible deployment guidance. Every command must use artifacts pinned in `../README.md` and must match a reviewed correctness and performance result.

## Page Metadata

| Field | Value |
|---|---|
| Model | `zai-org/GLM-5-1028-Provider` |
| Audience | Deployment and performance engineers |
| SGLang commit | Cutoff candidate `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`; final release acceptance pending |
| Model revision | FP8 `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; NVFP4 `f2c64cebac62b1888c92c9d317adbb0b0aef5955` |
| Draft-model revision | FP8 checkpoint revision above; #89 validates NVFP4 self-draft on GB300 |
| Container digest | `xinyuantongradixark/sglang-private@sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9`; exact-digest GPU validation pending |
| Supported platforms | H200 and GB300 default sweeps complete; cutoff reference-method evidence import and exact-image runtime validation pending on all three platforms |
| Owner | `xinyuan` |
| Reviewers | `<REVIEWERS>` |
| Status | Local draft `a62b1db914357ed5430191f005471c7c30d05f0d`; unpublished; refresh from raw cutoff results, exact-image validation and the NVFP4 natural-MTP rerun |

## Supported Configuration Matrix

| Platform | Workload | Profile | Parallelism | Backend | Precision | Speculative Decoding | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| H200 | Four-turn chat | Latency and throughput | TP8 | BF16 KV, FlashMLA Sparse, breakable prefill | FP8 | Natural and off measured | Default sweep complete; non-release | [E14](../../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-h200-defaults/repro.md) |
| GB300 | Four-turn chat | Latency and throughput | TP4 | BF16/FP8 KV, breakable prefill | FP8/NVFP4 | Natural and off measured | Default sweep complete; NVFP4 natural-MTP rerun required after #89 | [E15](../../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-gb300-defaults/repro.md) |
| B300 | Four-turn chat | Latency and throughput | TP8 preferred over DEP8 in the eager baseline | FP8 KV, TRTLLM | FP8/NVFP4 | Natural and off measured | Eager baseline only; FP8-only r4 running | [E12](../../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-b300-delivery/repro.md) |

[Correctness E31](../../features/p0-correctness/data/data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync/repro.md) validates upstream-sync candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` on GB300 TP4 at 94.92% accuracy and 100% stop. This is integration evidence only: it does not replace the cutoff launch profiles, validate DEP/MegaMoE or PD, or select a deployment configuration.

[Correctness E32](../../features/p0-correctness/data/data@2026-11-21-710a842c5741dade3ecd7d8583ef622745dcd9f2-upstream-main-sync/repro.md) validates `glm-5-lp` `710a842c5741dade3ecd7d8583ef622745dcd9f2` on GB300 with TP4 and with DEP4 + megamoe. This is integration evidence only: it does not replace the cutoff launch profiles or select a deployment configuration.

[Correctness E33](../../features/p0-correctness/data/data@2026-11-22-534c27c2414db7cf47038d4da5b347cb56600981-upstream-main-sync/repro.md) validates upstream-sync candidate `534c27c2414db7cf47038d4da5b347cb56600981` on GB300 with TP4, DEP4 + megamoe and the full PD serving recipe, including hierarchical cache and AgentX. The candidate remains on `sync/glm-5-lp-on-upstream-main` and has not landed on `glm-5-lp`. This is integration evidence only: it does not replace the cutoff launch profiles or select a deployment configuration.

## Required Page Structure

### 1. Overview

- Explain the model's serving characteristics in public terms.
- State the supported scope and known limitations.
- Identify which profiles optimize latency, throughput, capacity, or agentic workloads.

### 2. Prerequisites

- Hardware and topology.
- Driver and accelerator runtime.
- Container or installation method.
- Model and draft-model access.
- Required external dependencies.

### 3. Installation

Provide commands pinned to `<IMAGE_DIGEST>` or `<FULL_CODE_SHA>`. Include a verification command that prints the SGLang import path and dependency versions.

### 4. Model Preparation

Document immutable revisions, expected files, storage requirements, access steps, and checksum verification without embedding credentials.

### 5. Launch Profiles

| Profile | Intended Workload | Hardware | Command | Expected Envelope | Evidence |
|---|---|---|---|---|---|
| `<PROFILE>` | `<WORKLOAD>` | `<HARDWARE>` | `<COMMAND_OR_SCRIPT_LINK>` | `<EXPECTED_ENVELOPE>` | `<ROUND_LINK>` |

For every command:

- include all behavior-changing flags and environment variables;
- explain why the profile exists;
- state unsupported combinations and fallback behavior;
- bind expected results to reviewed evidence.

### 6. Correctness Check

Provide a fast smoke test and a release-grade evaluation command. State the expected output or metric gate and link to `features/p0-correctness/` evidence.

### 7. Performance Check

Provide the exact benchmark command, workload shape, warmup, repetition, and metric definition. Link to the owning general-performance or AgentX round.

### 8. Tuning Guide

Explain how workload shape, concurrency, memory budget, parallelism, backend, precision, and speculative decoding affect the recommended profile. Separate validated guidance from hypotheses.

### 9. Troubleshooting

| Symptom | Likely Cause | Diagnostic | Resolution | Evidence |
|---|---|---|---|---|
| `<SYMPTOM>` | `<CAUSE>` | `<DIAGNOSTIC>` | `<RESOLUTION>` | `<LINK>` |

### 10. Known Limitations

List unsupported or unvalidated combinations with impact, fallback, owner, and tracking link.

## Reproducibility Checklist

- [ ] Every code, model, draft-model, image, and dependency reference is immutable.
- [ ] Commands work from a clean documented environment.
- [ ] Expected results match the referenced evidence.
- [ ] Required platforms have runtime validation.
- [ ] Correctness gates pass for every recommended performance profile.
- [ ] Unsupported combinations and fallbacks are explicit.
- [ ] No credentials, private endpoints, or internal hostnames are present.

## Publication Checklist

- [ ] Technical owner review.
- [ ] Correctness and performance owner review.
- [ ] Fresh-reader command review.
- [ ] Link and artifact-pin review.
- [ ] English and terminology review.
- [ ] Publication location and source commit recorded in `../README.md`.
