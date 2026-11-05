# Day-0 Delivery

## Summary

This directory coordinates the release bundle for `zai-org/GLM-5-1028-Provider`. It owns immutable artifact pins, release gates, sign-off, and the three in-repository deliverables: cookbook guidance, Docker material, and the release blog. The delivery is not release-ready. Current evidence is pinned to implementation commits `a15aa7c3` and `8451a1bf` with model revision `7e66c405`; none is a release cut. The target date, owners, release commit, container image, and release decision are unresolved.

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
| Target date | `<RELEASE_DATE>` |
| Release owner | `<OWNER>` |
| Overall status | In progress; not release-ready |
| Current blocker | Release scope, owners, and gates are undefined. The H200 bring-up ([Correctness E01](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) and baseline accuracy plus ordinary decode-graph/MTP smoke ([Correctness E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)) have evidence, but release gates are not passed. |
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
| General performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | None | `<REVIEWER>` | Not started |
| AgentX performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | None | `<REVIEWER>` | Not started |
| Kernel compatibility | `<CODE_SHA>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | None | `<REVIEWER>` | Not started |
| Speculative decoding | `<CODE_SHA>; <MODEL_REVISION>; <DRAFT_MODEL_REVISION>` | `<PLATFORM_SET>` | [Correctness E02](../features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md): built-in NextN/MTP returned `accept len=2.27` with `cuda graph: True`; performance and release handoff remain open | `<REVIEWER>` | In progress |
| Docker runtime | `<IMAGE_DIGEST>; <MODEL_REVISION>` | `<PLATFORM_SET>` | None; no image has been built | `<REVIEWER>` | Not started |

## Delivery Stages

### Stage 1: Freeze release scope — Not started

- [ ] Name all required capabilities and supported platforms.
- [ ] Assign owners and reviewers.
- [ ] Define correctness, performance, compatibility, and publication gates.
- [ ] Record explicit out-of-scope items.
- Missing release gates: text accuracy and stop rate; reasoning and tool-call API behavior; MTP; CUDA graph replay; required parallel, KV-cache, and disaggregated configurations; general and AgentX performance; Docker runtime.
- Next action: name the release owner, target date, required platforms, and required capabilities, then define the gates above.

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
- [ ] Pass `features/p0-agentx-performance/` gates on locked artifacts.
- [ ] Pass `features/p0-kernel-opt/` compatibility gates.
- [ ] Pass speculative-decoding training and inference handoff gates.
- [ ] Resolve every missing matrix cell with an explicit release decision.

### Stage 4: Build and publish Docker artifacts — Not started

- [ ] Review recipes and dependency pins in `docker/`.
- [ ] Build every required architecture from a clean context.
- [ ] Pass static, security, import, smoke, and runtime checks.
- [ ] Publish immutable image digests and verify registry metadata.
- [ ] Record rollback images and procedures.

### Stage 5: Finalize cookbook — Not started

- [ ] Document installation and prerequisites.
- [ ] Publish validated launch profiles by workload and platform.
- [ ] Include correctness checks, tuning, troubleshooting, and fallbacks.
- [ ] Bind every command to locked artifacts.
- [ ] Complete technical and user review.

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
