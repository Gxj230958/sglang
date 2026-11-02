# Day-0 Delivery

## Summary

This directory coordinates the release bundle for `<MODEL_NAME>`. It owns immutable artifact pins, release gates, sign-off, and the three in-repository deliverables: cookbook guidance, Docker material, and the release blog. The delivery is `<STATUS>` for target date `<RELEASE_DATE>`, with release cut `<CODE_SHA>` and model revision `<MODEL_REVISION>`.

An artifact without an immutable pin and reviewed validation evidence cannot ship.

## Assignees

| Responsibility | Owner | Reviewer | Status |
|---|---|---|---|
| Release coordination | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| SGLang code | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Model artifacts | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Correctness sign-off | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Performance sign-off | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Docker | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Cookbook | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |
| Blog | `<OWNER>` | `<REVIEWER>` | `<STATUS>` |

## Release Status

| Field | Value |
|---|---|
| Model | `<MODEL_NAME>` |
| Target date | `<RELEASE_DATE>` |
| Release owner | `<OWNER>` |
| Overall status | `<STATUS>` |
| Current blocker | `<BLOCKER_OR_NONE>` |
| Release decision | `<GO_OR_NO_GO_OR_PENDING>` |
| Decision timestamp | `<YYYY-MM-DD_HHMM_TIMEZONE>` |

## Artifact Lock

### Code and Pull Requests

| Artifact | Immutable Pin or Link | Validation | Owner | Status |
|---|---|---|---|---|
| SGLang release commit | `<FULL_CODE_SHA>` | `<VALIDATION_LINK>` | `<OWNER>` | `<STATUS>` |
| SGLang pull request | `<PR_URL>` | `<REVIEW_STATUS>` | `<OWNER>` | `<STATUS>` |
| Tracking pull request | `<TRACKING_PR_URL>` | `<REVIEW_STATUS>` | `<OWNER>` | `<STATUS>` |
| Release issue | `<ISSUE_URL>` | `<ISSUE_STATUS>` | `<OWNER>` | `<STATUS>` |

### Model Revisions

| Artifact | Repository | Immutable Revision | Checksum | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| Target model | `<MODEL_REPOSITORY>` | `<MODEL_REVISION>` | `<CHECKSUM>` | `<VALIDATION_LINK>` | `<OWNER>` | `<STATUS>` |
| Draft model | `<DRAFT_MODEL_REPOSITORY>` | `<DRAFT_MODEL_REVISION>` | `<CHECKSUM>` | `<VALIDATION_LINK>` | `<OWNER>` | `<STATUS>` |
| Tokenizer or processor | `<ARTIFACT_REPOSITORY>` | `<ARTIFACT_REVISION>` | `<CHECKSUM>` | `<VALIDATION_LINK>` | `<OWNER>` | `<STATUS>` |

### Docker Images

| Profile | Architecture | Recipe Commit | Image Reference | Digest | Runtime Validation | Status |
|---|---|---|---|---|---|---|
| `<PROFILE>` | `<ARCHITECTURE>` | `<CODE_SHA>` | `<IMAGE_REFERENCE>` | `<IMAGE_DIGEST>` | `<VALIDATION_LINK>` | `<STATUS>` |

### Non-Git Dependencies

| Dependency | Version or Checksum | Source | License or Access | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| `<DEPENDENCY>` | `<VERSION_OR_CHECKSUM>` | `<SOURCE_URL>` | `<LICENSE_OR_ACCESS>` | `<VALIDATION_LINK>` | `<OWNER>` | `<STATUS>` |

## Release Validation Matrix

| Gate | Required Artifact Set | Required Platforms | Evidence | Reviewer | Status |
|---|---|---|---|---|---|
| Correctness | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | `<CORRECTNESS_LINK>` | `<REVIEWER>` | `<STATUS>` |
| General performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | `<PERFORMANCE_LINK>` | `<REVIEWER>` | `<STATUS>` |
| AgentX performance | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | `<AGENTX_LINK>` | `<REVIEWER>` | `<STATUS>` |
| Kernel compatibility | `<CODE_SHA>; <IMAGE_DIGEST>` | `<PLATFORM_SET>` | `<KERNEL_LINK>` | `<REVIEWER>` | `<STATUS>` |
| Speculative decoding | `<CODE_SHA>; <MODEL_REVISION>; <DRAFT_MODEL_REVISION>` | `<PLATFORM_SET>` | `<SPEC_LINK>` | `<REVIEWER>` | `<STATUS>` |
| Docker runtime | `<IMAGE_DIGEST>; <MODEL_REVISION>` | `<PLATFORM_SET>` | `<DOCKER_LINK>` | `<REVIEWER>` | `<STATUS>` |

## Delivery Stages

### Stage 1: Freeze release scope — `<STATUS>`

- [ ] Name all required capabilities and supported platforms.
- [ ] Assign owners and reviewers.
- [ ] Define correctness, performance, compatibility, and publication gates.
- [ ] Record explicit out-of-scope items.

### Stage 2: Lock code and model artifacts — `<STATUS>`

- [ ] Pin the SGLang release commit and public pull request.
- [ ] Pin target-model, draft-model, tokenizer, and processor revisions.
- [ ] Pin non-Git dependencies with versions or checksums.
- [ ] Confirm artifact access and license requirements.

### Stage 3: Complete validation — `<STATUS>`

- [ ] Pass `features/p0-correctness/` gates on locked artifacts.
- [ ] Pass `features/p0-general-performance/` gates on locked artifacts.
- [ ] Pass `features/p0-agentx-performance/` gates on locked artifacts.
- [ ] Pass `features/p0-kernel-opt/` compatibility gates.
- [ ] Pass speculative-decoding training and inference handoff gates.
- [ ] Resolve every missing matrix cell with an explicit release decision.

### Stage 4: Build and publish Docker artifacts — `<STATUS>`

- [ ] Review recipes and dependency pins in `docker/`.
- [ ] Build every required architecture from a clean context.
- [ ] Pass static, security, import, smoke, and runtime checks.
- [ ] Publish immutable image digests and verify registry metadata.
- [ ] Record rollback images and procedures.

### Stage 5: Finalize cookbook — `<STATUS>`

- [ ] Document installation and prerequisites.
- [ ] Publish validated launch profiles by workload and platform.
- [ ] Include correctness checks, tuning, troubleshooting, and fallbacks.
- [ ] Bind every command to locked artifacts.
- [ ] Complete technical and user review.

### Stage 6: Finalize blog — `<STATUS>`

- [ ] Approve the audience, outline, and owners.
- [ ] Bind every technical claim and number to reviewed evidence.
- [ ] Verify figure data and rendering provenance.
- [ ] Remove internal-only references and sensitive information.
- [ ] Complete technical, editorial, and release review.

### Stage 7: Release sign-off — `<STATUS>`

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
