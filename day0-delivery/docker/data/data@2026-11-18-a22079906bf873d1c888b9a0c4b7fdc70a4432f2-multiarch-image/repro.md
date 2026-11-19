# Multi-architecture cutoff image build and publication

## Environment

- Build date: 2026-11-18.
- Builders: native x86_64 and ARM64 EC2 CPU VMs with Docker 29.6; the ARM64 builder was a c7g.4xlarge.
- Base image: `lmsysorg/sglang:nightly-dev-cu13-20261115-7b5fb39b`, OCI index `sha256:b7306e5396c7b5f09cbbbfd714eb03ecfc5908be2188d1ebfddb40857643200f`.
- Base AMD64 manifest: `sha256:b2eb906e383d53e918ac761ea15db31f04afc0c4ec3859ca16774fc28e4b23a8`.
- Base ARM64 manifest: `sha256:d42a31385980dd921667d4986909468ae2bd7bec7f98881fa2114308c3891e2c`.
- Runtime dependencies: torch 2.14.1+cu130, CUDA 13.0.3, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8+cu130.megamoefp8, sgl-flash-mla 1.0.5, transformers 5.19.0, kernels 0.14.1, Python 3.12.16 and Rust 1.100.0.

## Setup

Run `make-manifest.sh <sglang-clone> .` in a context containing this round's Dockerfile and scripts. The clone must contain base commit `7b5fb39bb952da5f6da3bb7fe73c671cf449b6fa` and cutoff commit `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`. This generates the source archive and manifests; the archive itself remains outside Git as recorded in [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).

On a native CPU builder for each architecture:

```bash
bash build.sh
bash verify-image.sh xinyuantongradixark/sglang-private:dev-glm-loop-1118-amd64 amd64
bash verify-image.sh xinyuantongradixark/sglang-private:dev-glm-loop-1118-arm64 arm64
```

Use the command matching the builder's architecture. After authentication through the approved secret mechanism, run `bash push.sh` on each builder. Create and inspect the multi-architecture index:

```bash
R=xinyuantongradixark/sglang-private
docker buildx imagetools create -t $R:dev-glm-loop-1118 \
  $R:dev-glm-loop-1118-amd64 $R:dev-glm-loop-1118-arm64
docker buildx imagetools inspect $R:dev-glm-loop-1118
```

## Commit

- Runtime source: `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` from `radixark/sglang-zai`.
- Upstream merge base: `6de483b326c7dd4145fde06afcac9866bf491024`.
- Source archive SHA256: `e39d419e5669a165ea019ecb57ecc07867cd5128318260686bebb2a175fd8c13`.
- Working tree: the Docker build replaces 277 files that differ from the nightly base and removes one base-only file. It verifies 12,578 source files and nine symlinks against the included manifest.
- DeepGEMM: v0.2.8 at `e3f6b84093dab1213f50cd1865d847365697ef23`, plus the cutoff MegaMoE FP8 TRT-LLM weight-layout patch with SHA256 `4e5297071d9488df061b0f850accd2dd326c4006f6eb1f238535fc7020131746`.

## Scripts

- `make-manifest.sh` — generates the source archive and immutable source manifests.
- `Dockerfile` — replaces the nightly source, rebuilds all five Rust extensions and builds patched sgl-deep-gemm.
- `build.sh` and `push.sh` — native build and publication entry points.
- `verify-source.sh` and `verify-image.sh` — source-integrity and CPU-only image checks.

## Workload

Two native CPU image builds, two independent CPU verification runs, two registry pushes and one multi-architecture index publication. GPU serving, model loading, JIT compilation, accuracy and stop-rate evaluation are outside this round.

## Results

| Published reference | Architecture | Immutable digest | Compressed size | Status |
|---|---|---|---:|---|
| `xinyuantongradixark/sglang-private:dev-glm-loop-1118` | OCI index for AMD64 and ARM64 | `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9` | — | Published; GPU validation pending |
| `xinyuantongradixark/sglang-private:dev-glm-loop-1118-amd64` | linux/amd64 | `sha256:933ab3b225383467094874ddba9f9f8ae21c024a01a937fca162ac51abfa1927` | 15,606,487,605 bytes | Push exit 0; CPU checks passed |
| `xinyuantongradixark/sglang-private:dev-glm-loop-1118-arm64` | linux/arm64 | `sha256:fafb965404837c37d4807f21a4584ebc66994a1b529630b19cebcb8ff8064145` | 16,260,333,081 bytes | Push exit 0; CPU checks passed |

Both architecture checks confirm the source manifest, Python compilation, SGLang and model imports, CLI help, all five Rust extensions, patched DeepGEMM sources and binary, DeepGEMM import and dependency versions. `flash_mla` cannot be imported on a CPU builder because `libcuda.so.1` comes from the GPU host driver; the base image has the same constraint.

The registry was confirmed private before and after publication. The image retains released sgl-flash-mla 1.0.5 without the optional h64 sparse-decode patches, matching the measured reference-method environment.

Conclusions:

1. The cutoff source and both architecture images now have immutable publication pins.
2. This is not a release-ready runtime qualification. Exact-digest GPU serve, MegaMoE FP8 forward, MTP, accuracy and stop-rate checks remain required on B300, H200 and GB300.

## Data and Figures

- `logs/verify-amd64.log` and `logs/verify-arm64.log` — CPU verification receipts.
- `logs/push-amd64.log` and `logs/push-arm64.log` — registry push receipts with terminal exit status.
- `manifest/` — source hashes, symlinks and base-to-cutoff file lists used by the build.
- [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md) — local-only source archive, build logs and build-kit archive identities.
- `SHA256SUMS` — integrity records for every file included in this round.
