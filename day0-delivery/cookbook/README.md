# Cookbook Template

## Purpose

The cookbook turns validated Day-0 model results into reproducible deployment guidance. Every command must use artifacts pinned in `../README.md` and must match a reviewed correctness and performance result.

## Page Metadata

| Field | Value |
|---|---|
| Model | `<MODEL_NAME>` |
| Audience | `<TARGET_AUDIENCE>` |
| SGLang commit | `<FULL_CODE_SHA>` |
| Model revision | `<MODEL_REVISION>` |
| Draft-model revision | `<DRAFT_MODEL_REVISION_OR_NOT_USED>` |
| Container digest | `<IMAGE_DIGEST>` |
| Supported platforms | `<PLATFORM_SET>` |
| Owner | `<OWNER>` |
| Reviewers | `<REVIEWERS>` |
| Status | `<STATUS>` |

## Supported Configuration Matrix

| Platform | Workload | Profile | Parallelism | Backend | Precision | Speculative Decoding | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| `<PLATFORM>` | `<WORKLOAD>` | `<PROFILE>` | `<PARALLELISM>` | `<BACKEND>` | `<PRECISION>` | `<SPEC_CONFIGURATION>` | `<STATUS>` | `<ROUND_LINK>` |

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
