# Fallback Docker

The [November16 ARM64 candidate build](data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-arm64-build/repro.md) completed for runtime `52ef77912fd004f34cfe340b392018632ce69c2c`. Loaded-image CPU checks pass; private registry publication and image-level GPU qualification are pending.

## Purpose

This directory tracks Docker recipe provenance, dependency pins, build validation, runtime validation, publication, and rollback for the Day-0 model. Do not commit built images, credentials, or private registry tokens.

## Image Matrix

| Profile | Base Image | Architecture | Accelerator Runtime | SGLang Commit | Recipe | Published Reference | Digest | Status |
|---|---|---|---|---|---|---|---|---|
| `<PROFILE>` | `<BASE_IMAGE_DIGEST>` | `<ARCHITECTURE>` | `<RUNTIME_VERSION>` | `<FULL_CODE_SHA>` | `<RECIPE_PATH>` | `<IMAGE_REFERENCE>` | `<IMAGE_DIGEST>` | `<STATUS>` |

## Recipe Provenance

| File | Source | Source Commit | Local Checksum | Purpose | Owner |
|---|---|---|---|---|---|
| `<RECIPE_FILE>` | `<SOURCE_URL>` | `<FULL_CODE_SHA>` | `<CHECKSUM>` | `<PURPOSE>` | `<OWNER>` |

Any copied patch, binary, archive, or generated file must have an origin, immutable revision, checksum, license or access note, and reason for inclusion.

## Dependency Pins

| Dependency | Version or Revision | Source | Checksum | Architecture | Required By | Status |
|---|---|---|---|---|---|---|
| `<DEPENDENCY>` | `<VERSION_OR_REVISION>` | `<SOURCE_URL>` | `<CHECKSUM>` | `<ARCHITECTURE>` | `<COMPONENT>` | `<STATUS>` |

## Build Record

| Field | Value |
|---|---|
| Build date | `<YYYY-MM-DD>` |
| Builder | `<OWNER>` |
| Build host type | `<HOST_TYPE>` |
| Source commit | `<FULL_CODE_SHA>` |
| Build context checksum | `<CHECKSUM>` |
| Build command | `<BUILD_COMMAND>` |
| Base image digest | `<BASE_IMAGE_DIGEST>` |
| Output image reference | `<IMAGE_REFERENCE>` |
| Output image digest | `<IMAGE_DIGEST>` |
| Build log | `<LOG_LINK>` |

## Build Requirements

- Build from a clean, minimal context.
- Pin the base image by digest.
- Pin all externally downloaded dependencies.
- Keep credentials in the approved secret mechanism and outside image layers.
- Record target architectures and accelerator capabilities.
- Remove build-only caches, source credentials, and temporary artifacts.
- Make the installed SGLang commit and dependency versions inspectable at runtime.

## Static Validation

- [ ] Image architecture matches `<ARCHITECTURE>`.
- [ ] Base image digest matches `<BASE_IMAGE_DIGEST>`.
- [ ] Installed SGLang commit matches `<FULL_CODE_SHA>`.
- [ ] Required modules import successfully.
- [ ] Required kernels or binary artifacts cover `<HARDWARE_SET>`.
- [ ] Package and system dependencies match the lock table.
- [ ] No credentials, private keys, tokens, or unintended repository metadata exist.
- [ ] Vulnerability and license checks meet `<SECURITY_GATE>`.

## Runtime Validation Matrix

| Platform | Profile | Model Revision | Smoke Test | Correctness Gate | Performance Gate | Result | Evidence |
|---|---|---|---|---|---|---|---|
| `<PLATFORM>` | `<PROFILE>` | `<MODEL_REVISION>` | `<SMOKE_RESULT>` | `<CORRECTNESS_RESULT>` | `<PERFORMANCE_RESULT>` | `<STATUS>` | `<ROUND_LINK>` |

Runtime validation must use the published digest, not a mutable local tag.

## Publication Checklist

- [ ] Build and static validation passed.
- [ ] Required runtime matrix passed on the published digest.
- [ ] Registry architecture and manifest metadata verified.
- [ ] Immutable digest recorded in `../README.md`.
- [ ] User-facing tag policy documented.
- [ ] Access permissions verified without exposing credentials.
- [ ] Cookbook commands updated to the published digest.

## Rollback

| Profile | Current Digest | Previous Known-Good Digest | Trigger | Procedure | Owner |
|---|---|---|---|---|---|
| `<PROFILE>` | `<IMAGE_DIGEST>` | `<ROLLBACK_DIGEST>` | `<ROLLBACK_TRIGGER>` | `<ROLLBACK_PROCEDURE>` | `<OWNER>` |

Record every replaced or withdrawn image in the release decision log. Never reuse an immutable tag for different content.
