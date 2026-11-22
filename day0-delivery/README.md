# Day-0 Delivery

## Summary

The [November 18 fallback delivery](2026-11-16-1938-xinyuan-no-code-fallback-delivery.md) targets a GPU-validated feature set, the best usable measured deployment, and a pinned Docker image plus cutoff commit for Z.ai. The accepted candidate freezes after Z.ai benchmarks accuracy.

Delivery status: In progress. The cutoff candidate is pinned at `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`, and the [multi-architecture cutoff image](docker/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) is published with immutable AMD64, ARM64 and index digests. Exact-digest GPU validation and final performance selection remain open. The [2026-11-18 status refresh](2026-11-18-0317-xinyuan-26c4816830-default-results-and-pd-diagnosis.md) records the earlier default results, self-draft fix and PD diagnosis.

General Performance [E10](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-h200-delivery/repro.md)–[E13](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-fp8kv-breakable/repro.md) preserve the initial delivery matrix. [E14](../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-h200-defaults/repro.md) adds 24 H200 points and [E15](../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-gb300-defaults/repro.md) adds 96 GB300 points with zero errors or empty outputs. E15 NVFP4 natural-MTP rows predate #89 and are excluded from final selection. B300 FP8-only r4 has no final summary. The separate cutoff reference-method run requires raw per-run outputs and an immutable model revision before an official performance round can be recorded.

Correctness E30 records #89 restoring NVFP4 self-draft accept lengths to 2.56–2.60 with zero evaluation errors. [Correctness E31](../features/p0-correctness/data/data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync/repro.md) validates upstream-sync candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` on GB300 TP4 at 94.92% accuracy and 100% stop, against 94.69% and 99.92% for the matched baseline. The candidate has not landed and does not replace the cutoff. PD E04 attributes 27 HTTP 503 responses to router health-check timeouts. The NVFP4 natural-MTP performance rerun remains open. NVFP4 remains performance-only.

Historical candidate `52ef77912fd004f34cfe340b392018632ce69c2c` retains Correctness E22–E28 and the [ARM64 construction evidence](docker/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-arm64-build/repro.md). Those results are not the release artifact lock.

An artifact without an immutable pin and reviewed validation evidence cannot ship.

## Assignees

| Responsibility | Owner | Reviewer | Status |
|---|---|---|---|
| Release coordination | `<OWNER>` | `<REVIEWER>` | Not started |
| SGLang code | `<OWNER>` | `<REVIEWER>` | In progress |
| Model artifacts | `<OWNER>` | `<REVIEWER>` | In progress |
| Correctness sign-off | `<OWNER>` | `<REVIEWER>` | Not started |
| Performance sign-off | `<OWNER>` | `<REVIEWER>` | Not started |
| Docker | `<OWNER>` | `<REVIEWER>` | Not started |
| Cookbook | `<OWNER>` | `<REVIEWER>` | Not started |
| Blog | `<OWNER>` | `<REVIEWER>` | Not started |

## Release Status

| Field | Value |
|---|---|
| Model | `zai-org/GLM-5-1028-Provider` |
| Target date | November 18, 2026 — fallback Docker and cutoff commit to Z.ai |
| Release owner | `<OWNER>` |
| Overall status | In progress; not release-ready |
| Current blocker | Required basic-feature GPU coverage, cutoff quality review, final performance selection and image-level validation remain incomplete. |
| Release decision | Pending |
| Decision timestamp | `<YYYY-MM-DD_HHMM_TIMEZONE>` |

## Artifact Lock

### Code and Pull Requests

| Artifact | Immutable Pin or Link | Validation | Owner | Status |
|---|---|---|---|---|
| SGLang cutoff candidate | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` (`radixark/sglang-zai` branch `glm-5-lp`) | [Image source and CPU checks](docker/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md); cutoff quality review and exact-image GPU validation pending | `<OWNER>` | In progress |
| Upstream-sync integration candidate (not a release cut) | `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` (`sync/glm-5-lp-on-upstream-main`) | [Correctness E31](../features/p0-correctness/data/data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync/repro.md): GB300 TP4 gate passes; DEP/MegaMoE, PD, HiSparse and image validation pending | `<OWNER>` | Review candidate; not landed |
| Upstream-sync integration (not a release cut) | `710a842c5741dade3ecd7d8583ef622745dcd9f2` (`radixark/sglang-zai` branch `glm-5-lp`) | [Correctness E32](../features/p0-correctness/data/data@2026-11-21-710a842c5741dade3ecd7d8583ef622745dcd9f2-upstream-main-sync/repro.md): GB300 TP4 and DEP4 + megamoe gates pass; PD, HiSparse and image validation pending | `<OWNER>` | Complete |
| Upstream-sync integration candidate (not a release cut) | `534c27c2414db7cf47038d4da5b347cb56600981` (`sync/glm-5-lp-on-upstream-main`) | [Correctness E33](../features/p0-correctness/data/data@2026-11-22-534c27c2414db7cf47038d4da5b347cb56600981-upstream-main-sync/repro.md): GB300 TP4, DEP4 + megamoe and full serving recipe gates pass; image validation and deployment selection pending | `<OWNER>` | Review candidate; not landed |
| E01–E03 and E05 implementation commit (not a release cut) | `a15aa7c3edefee67d557f15d640899b825c58ba6` (`radixark/sglang-zai` branch `glm-5-lp`) | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md), [E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md), [E03](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md), [E05](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md) | `<OWNER>` | In progress |
| Optional vision SwiGLU fix (not a release cut) | `8451a1bf9d6156a8ff76f8d603abe9a89c1b1002` (`fix/glm5-lp-implementation`) | [Correctness E04](../features/p0-correctness/data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md) | `<OWNER>` | In progress |
| SGLang pull request | `<PR_URL>` | None | `<OWNER>` | Not started |
| Tracking pull request | [sglang-zai #98](https://github.com/radixark/sglang-zai/pull/98) | Merged 2026-11-19; subsequent evidence arrives on rolling tracking branches | `xinyuan` | Complete |
| Release issue | `<ISSUE_URL>` | None | `<OWNER>` | Not started |

### Model Revisions

| Artifact | Repository | Immutable Revision | Checksum | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| Target model | `zai-org/GLM-5-1028-Provider` | `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43` | `<CHECKSUM>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |
| Draft model | `<DRAFT_MODEL_REPOSITORY>`; the target checkpoint contains one NextN/MTP layer | `<DRAFT_MODEL_REVISION>` | `<CHECKSUM>` | None | `<OWNER>` | Not started |
| Tokenizer and processor | `zai-org/GLM-5-1028-Provider` (bundled with the target model) | `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43` | `<CHECKSUM>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |

### Docker Images

| Profile | Architecture | Recipe Commit | Image Reference | Digest | Runtime Validation | Status |
|---|---|---|---|---|---|---|
| Cutoff multi-architecture index | AMD64 + ARM64 | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2` | `xinyuantongradixark/sglang-private:dev-glm-loop-1118` | `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9` | CPU source/import checks passed; exact-digest GPU validation pending | Published; not release-ready |
| Cutoff AMD64 | linux/amd64 | Same cutoff | `xinyuantongradixark/sglang-private:dev-glm-loop-1118-amd64` | `sha256:933ab3b225383467094874ddba9f9f8ae21c024a01a937fca162ac51abfa1927` | CPU checks passed; B300/H200 runtime pending | Published; not release-ready |
| Cutoff ARM64 | linux/arm64 | Same cutoff | `xinyuantongradixark/sglang-private:dev-glm-loop-1118-arm64` | `sha256:fafb965404837c37d4807f21a4584ebc66994a1b529630b19cebcb8ff8064145` | CPU checks passed; GB300 runtime pending | Published; not release-ready |

### Non-Git Dependencies

| Dependency | Version or Checksum | Source | License or Access | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| torch | `2.14.1+cu130` (observed in E01, not locked) | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |
| flashinfer | `0.7.1` (observed in E01, not locked) | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |
| transformers | `5.19.0` (observed in E01, not locked) | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |
| sgl-flash-mla | `1.0.0` (observed in E01, not locked) | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |
| sglang-kernel | `0.4.10` (observed in E01, not locked) | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` | In progress |

## Release Validation Matrix

| Gate | Required Artifact Set | Required Platforms | Evidence | Reviewer | Status |
|---|---|---|---|---|---|
| Correctness | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md): bring-up; [Correctness E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md): baseline 95.50% accuracy with 100% stop rate, plus ordinary decode-graph/MTP smoke. API, configuration, and release gates are undefined. | `<REVIEWER>` | In progress |
| General performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | [General Performance E01](../features/p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md): cap-64 8K TTFT −4.31% and throughput +0.42%; non-release, with rebase and locked-artifact validation pending | `<REVIEWER>` | In progress |
| AgentX performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | None | `<REVIEWER>` | Not started |
| Kernel compatibility | `<CODE_SHA>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | [Kernel Optimization E01](../features/p0-kernel-opt/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md): exact parity in 36/36 B300 cases; upstream and remaining-platform validation pending | `<REVIEWER>` | In progress |
| Speculative decoding | `<CODE_SHA>; <MODEL_REVISION>; <DRAFT_MODEL_REVISION>` | `<PLATFORM_SET>` | [Correctness E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md): built-in NextN/MTP returned `accept len=2.27` with `cuda graph: True`; performance and release handoff remain open | `<REVIEWER>` | In progress |
| Docker runtime | `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`; model revision to be confirmed at launch; `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9` | 8×B300; 8×H200; 4×GB300 | [AMD64 and ARM64 source/import checks](docker/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) passed; published-digest GPU validation pending | `<REVIEWER>` | In progress |

## Delivery Stages

### Stage 1: Freeze release scope — In progress

- [x] Set the November 18 fallback deadline and feature-first execution order ([decision](2026-11-16-1938-xinyuan-no-code-fallback-delivery.md), November 16).
- [ ] Complete the required capability/platform matrix and record unsupported cells.
- [ ] Assign remaining owners and reviewers.
- [ ] Review correctness and finish-reason limits against the intended cutoff.
- [ ] Confirm the performance profile and image-level gates for the fallback handoff.

### Stage 2: Lock code and model artifacts — In progress

- Current evidence pins: `a15aa7c3edefee67d557f15d640899b825c58ba6` for E01–E03 and E05, `8451a1bf9d6156a8ff76f8d603abe9a89c1b1002` for E04, and model revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`; they are not release locks.
- [ ] Pin the SGLang release commit and public pull request.
- [ ] Pin target-model, draft-model, tokenizer, and processor revisions.
- [ ] Pin non-Git dependencies with versions or checksums.
- [ ] Confirm artifact access and license requirements.

### Stage 3: Complete validation — In progress

- [ ] Pass `features/p0-correctness/` gates on locked artifacts.
- Bring-up evidence: [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md); no release gate has passed.
- [ ] Pass `features/p0-general-performance/` gates on locked artifacts.
- AgentX performance remains deferred for this fallback delivery.
- [ ] Pass `features/p0-kernel-opt/` compatibility gates.
- [ ] Pass speculative-decoding training and inference handoff gates.
- [ ] Resolve every missing matrix cell with an explicit release decision.

### Stage 4: Build and publish Docker artifacts — In progress

- [x] Record cutoff recipes and dependency pins in `docker/`; completed 2026-11-18.
- [x] Build AMD64 and ARM64 images from the pinned cutoff source; completed 2026-11-18.
- [x] Publish immutable image digests and verify registry metadata; completed 2026-11-18.
- [ ] Pass final-image security, GPU smoke, correctness and runtime checks.
- [ ] Assign an approved rollback image and complete the rollback procedure.

### Stage 5: Finalize cookbook — In progress

- [x] Prepare a local documentation-only branch with deployment and benchmark pages (xinyuan, 2026-11-17).
- [x] Validate the Mintlify build, links, configuration generator and 69 node tests on the draft (xinyuan, 2026-11-17).
- [ ] Refresh the launch profiles and performance cells from the integrated default sweeps.
- [ ] Replace the model-name placeholder only after the public name and repository are confirmed.
- [ ] Bind every command to locked artifacts.
- [ ] Complete technical and user review before publication.

### Stage 6: Finalize blog — Not started

- [ ] Approve the audience, outline, and owners.
- [ ] Bind every technical claim and number to reviewed evidence.
- [ ] Verify figure data and rendering provenance.
- [ ] Remove internal-only references and sensitive information.
- [ ] Complete technical, editorial, and release review.

### Stage 7: Release sign-off — Not started

- [ ] Confirm every artifact-lock row required for release is immutable.
- [ ] Confirm every release gate has reviewed evidence.
- [ ] Confirm cookbook, Docker, and blog artifacts agree on commands and versions.
- [ ] Record the final go or no-go decision.
- [ ] Publish and record final public links.

## Release Decision Log

| Date and Time | Decision | Scope | Evidence | Owner | Reviewers |
|---|---|---|---|---|---|
| `<YYYY-MM-DD_HHMM_TIMEZONE>` | `<DECISION>` | `<SCOPE>` | `<EVIDENCE_LINKS>` | `<OWNER>` | `<REVIEWERS>` |

## Post-Release Follow-up

| Item | Trigger | Owner | Due Date | Status | Link |
|---|---|---|---|---|---|
| `<FOLLOW_UP>` | `<TRIGGER>` | `<OWNER>` | `<YYYY-MM-DD>` | `<STATUS>` | `<LINK>` |
