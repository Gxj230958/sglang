# Speculative Decoding Training

## Summary

`<MODEL_NAME>` speculative-decoding training tracking covers data preparation, draft architecture, training recipes, checkpoint evaluation, selection, and inference handoff. The project is `<STATUS>`; its target is `<DRAFT_QUALITY_GOAL>` under `<TRAINING_CONSTRAINTS>`. Related work is `<TRAINING_BRANCH_OR_RUN>`, with dependencies on `<DATA_REVISION>`, `<TARGET_MODEL_REVISION>`

## Scope

### In Scope

- Dataset sourcing, filtering, versioning, and governance.
- Draft architecture and target-model compatibility.
- Training and evaluation recipes.
- Checkpoint comparison and final selection.
- Immutable checkpoint publication and inference handoff.

### Out of Scope

- Serving integration owned by `p0-general-performance`.
- Target-model pretraining or post-training unrelated to the draft.
- Checkpoints without reproducible recipe and evaluation evidence.

## Success Criteria

- [ ] Dataset and preprocessing revisions are immutable and documented.
- [ ] Training recipe is reproducible from `<TRAINING_COMMIT>`.
- [ ] Candidate checkpoints meet `<OFFLINE_QUALITY_GATE>`.
- [ ] Selected checkpoint meets `<ACCEPTANCE_GATE>` and `<SERVING_PERFORMANCE_GATE>` in SGLang.
- [ ] Required model, tokenizer, and precision compatibility is confirmed.
- [ ] Final checkpoint is published at `<DRAFT_MODEL_REVISION>` with provenance and checksums.

## Training Recipe

| Field | Value | Evidence |
|---|---|---|
| Target model revision | `<TARGET_MODEL_REVISION>` | `<REFERENCE_LINK>` |
| Draft architecture | `<DRAFT_ARCHITECTURE>` | `<CONFIG_LINK>` |
| Dataset revision | `<DATA_REVISION>` | `<DATA_LINK>` |
| Preprocessing revision | `<PREPROCESSING_REVISION>` | `<CODE_LINK>` |
| Training code commit | `<TRAINING_COMMIT>` | `<CODE_LINK>` |
| Hardware | `<TRAINING_HARDWARE>` | `<RUN_LINK>` |
| Precision | `<TRAINING_PRECISION>` | `<RUN_LINK>` |
| Hyperparameters | `<HYPERPARAMETERS>` | `<RUN_LINK>` |

## Checkpoint Evaluation

| Checkpoint | Training Step | Offline Metric | Acceptance | Serving Impact | Compatibility | Status | Evidence |
|---|---:|---:|---:|---:|---|---|---|
| `<CHECKPOINT_REVISION>` | `<STEP>` | `<OFFLINE_RESULT>` | `<ACCEPTANCE>` | `<SERVING_RESULT>` | `<COMPATIBILITY_RESULT>` | `<STATUS>` | `<ROUND_PATH>` |

## Release Handoff

| Artifact | Revision or Checksum | Consumer | Validation | Owner | Status |
|---|---|---|---|---|---|
| Draft checkpoint | `<DRAFT_MODEL_REVISION>` | `p0-general-performance` | `<VALIDATION_GATE>` | `<OWNER>` | `<STATUS>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Freeze data and recipe — `<STATUS>`

- [ ] Pin target model, dataset, preprocessing, and training code.
- [ ] Define offline, acceptance, quality, and serving gates.
- [ ] Validate a small reproducibility run.

### Stage 2: Train and compare checkpoints — `<STATUS>`

- [ ] Execute `<TRAINING_RUN_SET>`.
- [ ] Evaluate checkpoints with stable offline methodology.
- [ ] Send candidate checkpoints through inference acceptance and serving tests.

### Stage 3: Select and publish — `<STATUS>`

- [ ] Select `<CHECKPOINT_REVISION>` using reviewed evidence.
- [ ] Publish immutable artifacts, provenance, and checksums.
- [ ] Complete inference handoff and release artifact lock.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<TRAINING_HARDWARE>; <DATA_REVISION>; <CHECKPOINT_REVISION>` | `<RESULT>` | `data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md` |
