# Docker

The [November 18 multi-architecture cutoff image](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) is built from runtime `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` and published for AMD64 and ARM64. Source integrity and CPU checks pass on both architectures. Exact-digest GPU serving, accuracy and stop-rate qualification remain pending, so the image is not release-ready.

The earlier [November 16 ARM64 candidate build](data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-arm64-build/repro.md) remains historical construction evidence for runtime `52ef77912fd004f34cfe340b392018632ce69c2c`; it is not the current cutoff artifact.

## Purpose

This directory tracks Docker recipe provenance, dependency pins, build validation, runtime validation, publication, and rollback for the Day-0 model. Do not commit built images, source archives, credentials, or registry tokens.

## Image Matrix

| Profile | Base Image | Architecture | Accelerator Runtime | SGLang Commit | Recipe | Published Reference | Digest | Status |
|---|---|---|---|---|---|---|---|---|
| Cutoff multi-architecture index | `lmsysorg/sglang@sha256:b7306e5396c7b5f09cbbbfd714eb03ecfc5908be2188d1ebfddb40857643200f` | AMD64 + ARM64 | CUDA 13.0.3 | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` | [Dockerfile](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/Dockerfile) | `xinyuantongradixark/sglang-private:dev-glm-loop-1118` | `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9` | Published; GPU validation pending |
| Cutoff AMD64 | Same index | linux/amd64 | CUDA 13.0.3 | Same cutoff | [Build record](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) | `xinyuantongradixark/sglang-private:dev-glm-loop-1118-amd64` | `sha256:933ab3b225383467094874ddba9f9f8ae21c024a01a937fca162ac51abfa1927` | Push exit 0; CPU checks passed |
| Cutoff ARM64 | Same index | linux/arm64 | CUDA 13.0.3 | Same cutoff | [Build record](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) | `xinyuantongradixark/sglang-private:dev-glm-loop-1118-arm64` | `sha256:fafb965404837c37d4807f21a4584ebc66994a1b529630b19cebcb8ff8064145` | Push exit 0; CPU checks passed |

## Recipe Provenance

| File | Source | Source Commit | Local Checksum | Purpose |
|---|---|---|---|---|
| [Dockerfile](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/Dockerfile) | Cutoff image build kit | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` | `0f5a225bfec22438b8ed933e8e8bb7ecd23c3ff08f89fa6fb9299d1ea3d9cee1` | Incremental native image build |
| [make-manifest.sh](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/make-manifest.sh) | Cutoff image build kit | Same cutoff | `5a3b11179fb6de86fbcf20c9d0c659d3529c02b78625ac0c4938a5ae3e47d5cc` | Generate source archive and manifests |
| [verify-image.sh](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/verify-image.sh) | Cutoff image build kit | Same cutoff | `f5a5258755ddc4ba1eeaeb397af29b00358375885e576504e2c9b0af4869e66d` | CPU-only image verification |

The source archive, original build-kit archive and raw build logs remain outside Git. Their byte sizes and hashes are in [EVIDENCE-STORAGE.md](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/EVIDENCE-STORAGE.md).

## Dependency Pins

| Dependency | Version or Revision | Source | Architecture | Status |
|---|---|---|---|---|
| torch | 2.14.1+cu130 | Base image | AMD64 + ARM64 | Verified by CPU inspection |
| flashinfer-python / flashinfer-cubin | 0.7.4 | Base image | AMD64 + ARM64 | Verified by CPU inspection |
| sglang-kernel | 0.4.11 | Base image | AMD64 + ARM64 | Verified by CPU inspection |
| sgl-deep-gemm | 0.2.8+cu130.megamoefp8; DeepGEMM `e3f6b84093dab1213f50cd1865d847365697ef23` plus cutoff patch | Rebuilt in the image | AMD64 + ARM64 | Source, binary and import checks passed |
| sgl-flash-mla | 1.0.5 | Base image | AMD64 + ARM64 | Version verified; import requires GPU driver |
| transformers | 5.19.0 | Base image | AMD64 + ARM64 | Verified by CPU inspection |
| kernels | 0.14.1 | Base image | AMD64 + ARM64 | Verified by CPU inspection |

## Build Record

| Field | Value |
|---|---|
| Build date | 2026-11-18 |
| Builder | Native x86_64 and ARM64 EC2 CPU VMs with Docker 29.6 |
| Source commit | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` |
| Source archive checksum | `e39d419e5669a165ea019ecb57ecc07867cd5128318260686bebb2a175fd8c13` |
| Build command | [build.sh](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/build.sh) |
| Base image digest | `sha256:b7306e5396c7b5f09cbbbfd714eb03ecfc5908be2188d1ebfddb40857643200f` |
| Output image references and digests | See the image matrix |
| Verification and push logs | [Round evidence](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md#data-and-figures) |

## Static Validation

- [x] Both image architectures match their targets.
- [x] The base and cutoff commits are pinned and recorded in image metadata.
- [x] All 12,578 source files and nine symlinks match the cutoff manifest.
- [x] SGLang, model modules, CLI entry points and all five Rust extensions pass CPU checks.
- [x] Patched DeepGEMM source, binary and import checks pass on both architectures.
- [x] Recorded package and runtime versions match on both architectures.
- [ ] Vulnerability, license and secret scanning of the final image filesystem meet a defined security gate.

## Runtime Validation Matrix

| Platform | Profile | Model Revision | Smoke Test | Correctness Gate | Performance Gate | Result | Evidence |
|---|---|---|---|---|---|---|---|
| 8×B300 | Cutoff AMD64 | FP8 revision must be confirmed at launch | Pending | Pending | Pending | Not started | [Build round](data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) |
| 8×H200 | Cutoff AMD64 | FP8 revision must be confirmed at launch | Pending | Pending | Pending | Not started | Same build round |
| 4×GB300 | Cutoff ARM64 | FP8 revision must be confirmed at launch | Pending | Pending | Pending | Not started | Same build round |

Runtime validation must pull the published digest, not a mutable tag. Development-container results on the same source commit do not qualify the image itself.

## Publication Checklist

- [x] Native builds and recorded CPU validation passed.
- [x] Registry architecture and manifest metadata were verified.
- [x] Immutable digests are recorded in `../README.md` and the build round.
- [x] The mutable multi-architecture tag and immutable per-architecture tags are documented.
- [x] Repository privacy was confirmed before and after publication without exposing credentials.
- [ ] Required runtime matrix passed on the published digests.
- [ ] Cookbook commands are bound to the published digest after runtime validation.
- [ ] Rollback images and procedures are assigned.

## Rollback

| Profile | Current Digest | Previous Known-Good Digest | Trigger | Procedure |
|---|---|---|---|---|
| Cutoff multi-architecture image | `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9` | None approved | Failed exact-digest runtime or correctness qualification | Stop release selection, retain the failed evidence and select a new reviewed cutoff; do not reuse a digest for different content |

Record every replaced or withdrawn image in the release decision log. Never reuse an immutable tag for different content.
