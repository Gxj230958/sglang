# Release Blog Template

## Purpose

The release blog explains the Day-0 model support, validated capabilities, performance, engineering work, and deployment path to a public audience. Every technical claim must be understandable, reviewable, and bound to evidence.

## Metadata

| Field | Value |
|---|---|
| Working title | `<TITLE>` |
| Model | `<MODEL_NAME>` |
| Audience | `<TARGET_AUDIENCE>` |
| Primary author | `<OWNER>` |
| Technical reviewers | `<TECHNICAL_REVIEWERS>` |
| Editorial reviewer | `<EDITORIAL_REVIEWER>` |
| Target publication date | `<RELEASE_DATE>` |
| Publication location | `<PUBLICATION_URL>` |
| Status | `<STATUS>` |

## Claims Policy

- Bind every number to an experiment round and immutable artifact set.
- Use the same metric definition and workload description as the evidence.
- Distinguish measured facts, design explanations, and future work.
- State comparison baselines and methodology clearly.
- Do not generalize beyond the validated hardware and workload envelope.
- Remove internal codenames, private links, hostnames, credentials, and unreleased partner details.
- Revalidate quoted numbers on the locked release artifacts before publication.

## Suggested Outline

### 1. Announcement

State what is supported, where users can find code and artifacts, and why the release matters.

### 2. Model and Serving Characteristics

Explain the public architecture traits that affect serving, using diagrams or tables only when they improve understanding.

### 3. Day-0 Capability Coverage

Summarize correctness, hardware, API, and deployment coverage. Link to public reproduction guidance.

### 4. General Performance

Describe workload methodology, baseline, latency, throughput, capacity, and recommended profiles without cherry-picking unsupported points.

### 5. AgentX Performance

Explain the agentic workload, concurrency envelope, cache behavior, and user-visible implications.

### 6. Kernel Optimization

Connect profile evidence, kernel changes, microbenchmarks, and end-to-end impact.

### 7. Speculative Decoding

Describe training, inference integration, acceptance, serving impact, compatibility, and fallback behavior.

### 8. How to Run

Point readers to immutable Docker and cookbook artifacts.

### 9. Acknowledgments

Credit contributors, reviewers, infrastructure providers, and upstream projects with approved public names.

## Claim Evidence Table

| Claim ID | Draft Claim | Metric Definition | Artifact Pins | Evidence | Owner | Review Status |
|---|---|---|---|---|---|---|
| `<CLAIM_ID>` | `<CLAIM>` | `<METRIC_DEFINITION>` | `<CODE_SHA>; <MODEL_REVISION>; <IMAGE_DIGEST>` | `<ROUND_LINK>` | `<OWNER>` | `<STATUS>` |

No quantitative claim enters the draft without a row in this table.

## Figure Inventory

| Figure | Purpose | Source Data | Rendering Script | Artifact Pins | Owner | Review Status |
|---|---|---|---|---|---|---|
| `<FIGURE_NAME>` | `<PURPOSE>` | `<DATA_LINK>` | `<SCRIPT_LINK>` | `<ARTIFACT_PINS>` | `<OWNER>` | `<STATUS>` |

Figure rules:

- Keep source data and a deterministic rendering command.
- Use labels, units, legends, and baselines that match the evidence.
- Avoid truncated axes or styling that exaggerates differences.
- Inspect the rendered output at publication size.
- Add concise alt text and a caption explaining the takeaway.

## Review Checklist

### Technical

- [ ] All claims have evidence rows and immutable pins.
- [ ] Correctness, performance, AgentX, kernel, and speculative-decoding owners reviewed their sections.
- [ ] Commands and artifact references match the cookbook and Docker records.
- [ ] Limitations and fallback behavior are accurate.

### Editorial

- [ ] The opening states the release clearly.
- [ ] Terminology is consistent and public-facing.
- [ ] Every figure is readable and has alt text.
- [ ] The article avoids unsupported superlatives and internal context.
- [ ] All prose is English and all links are appropriate for public readers.

### Publication

- [ ] Final release artifacts are locked.
- [ ] Quoted numbers were revalidated on the locked artifacts.
- [ ] Public code, model, image, and cookbook links resolve.
- [ ] Required acknowledgments and approvals are complete.
- [ ] Final publication URL is recorded in `../README.md`.
