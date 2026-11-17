# Day-0 Delivery

## Summary

The [November 18 fallback delivery](2026-11-16-1938-xinyuan-no-code-fallback-delivery.md) targets a GPU-validated feature set, the best usable measured deployment, and a pinned Docker image plus cutoff commit for Z.ai. The accepted candidate freezes after Z.ai benchmarks accuracy.

Delivery status: In progress. `glm-5-lp` is at `4ef2500d29ca90bc415247d5e476fe25ddd47f29` after #85–#87 merged. The cutoff commit, image digest and final default-BCG performance profile remain pending. The [2026-11-17 status refresh](2026-11-17-1646-xinyuan-4ef2500d29-delivery-status-refresh.md) records the exact merges, active test head and remaining gates.

General Performance [E10](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-h200-delivery/repro.md)–[E13](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-fp8kv-breakable/repro.md) now preserve 288 independently audited points and 52,224 successful responses with zero errors or empty outputs across H200, GB300 and B300. E13 shows that FP8 KV works with breakable prefill and that eager prefill caused the earlier natural-MTP deficit. E12's B300 eager results remain historical; final selection uses the active integrated default sweeps.

The #85 H200 minimal-command validation resolves default BCG and self-draft, completes full GSM8K with zero errors and reproduces the same 11/14 image/tool checks as eager. The three solid-colour image failures, stopping qualification, remaining feature coverage and image-level validation remain open. NVFP4 remains performance-only.

Historical candidate `52ef77912fd004f34cfe340b392018632ce69c2c` retains Correctness E22–E28 and the [ARM64 construction evidence](docker/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-arm64-build/repro.md). Those results are not the release artifact lock. Registry publication and exact-image GPU validation remain pending.

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
| SGLang release commit | `<FULL_CODE_SHA>` | None | `<OWNER>` | Not started |
| E01–E03 and E05 implementation commit (not a release cut) | `a15aa7c3edefee67d557f15d640899b825c58ba6` (`radixark/sglang-zai` branch `glm-5-lp`) | [Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md), [E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md), [E03](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md), [E05](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md) | `<OWNER>` | In progress |
| Optional vision SwiGLU fix (not a release cut) | `8451a1bf9d6156a8ff76f8d603abe9a89c1b1002` (`fix/glm5-lp-implementation`) | [Correctness E04](../features/p0-correctness/data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md) | `<OWNER>` | In progress |
| SGLang pull request | `<PR_URL>` | None | `<OWNER>` | Not started |
| Tracking pull request | `<TRACKING_PR_URL>` | `<REVIEW_STATUS>` | `<OWNER>` | `<STATUS>` |
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
| `<PROFILE>` | `<ARCHITECTURE>` | `<CODE_SHA>` | `<IMAGE_REFERENCE>` | `<IMAGE_DIGEST>` | None | Not started |

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
| Docker runtime | `<IMAGE_DIGEST>; <MODEL_REVISION>` | `<PLATFORM_SET>` | [ARM64 construction checks](docker/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-arm64-build/repro.md) passed; published-digest GPU validation pending | `<REVIEWER>` | Not started |

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

### Stage 4: Build and publish Docker artifacts — Not started

- [ ] Review recipes and dependency pins in `docker/`.
- [ ] Build every required architecture from a clean context.
- [ ] Pass static, security, import, smoke, and runtime checks.
- [ ] Publish immutable image digests and verify registry metadata.
- [ ] Record rollback images and procedures.

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
