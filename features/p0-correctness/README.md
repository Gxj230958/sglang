# Correctness

## Summary

`<MODEL_NAME>` correctness tracking covers model quality, API behavior, feature compatibility, and release-gating regressions. The project is `<STATUS>`; its current target is `<GOAL>`, constrained by `<CONSTRAINTS>`, and evaluated against `<REFERENCE_IMPLEMENTATION>` at immutable revisions. Related code work is tracked in `<CODE_BRANCH_OR_PR>`, with dependencies on `<DEPENDENCIES>`.

## Scope

### In Scope

- Text generation quality and deterministic smoke tests.
- Chat-template and reasoning-mode behavior, consuming evidence from `features/p0-reasoning-parser/`.
- Tool use, structured output, and API compatibility, consuming evidence from `features/p0-tool-call-parser/`.
- Long-context, batching, parallelism, and cache correctness.
- Multimodal correctness when the model exposes multimodal inputs.
- Cross-platform and cross-configuration regression gates.

### Out of Scope

- Tool-call detector and reasoning parser implementation and their detailed validation matrices, owned by `features/p0-tool-call-parser/` and `features/p0-reasoning-parser/`.
- Performance tuning that does not change outputs.
- Unreleased capabilities outside `<RELEASE_SCOPE>`.
- Evaluation datasets without a stable revision and reproducible scorer.

## Success Criteria

- [ ] The release capability matrix has no unexplained gaps.
- [ ] Every required evaluation meets `<QUALITY_GATE>` against `<REFERENCE_RESULT>`.
- [ ] Required APIs pass `<API_COMPATIBILITY_GATE>`.
- [ ] Required hardware and parallel configurations pass `<CONFIGURATION_GATE>`.
- [ ] All release results are pinned to `<CODE_SHA>` and `<MODEL_REVISION>`.
- [ ] Every failure has an owner, severity, reproduction record, and release decision.

## Capability Matrix

| Capability | Mode | Configuration | Gate | Status | Evidence | Owner |
|---|---|---|---|---|---|---|
| `<CAPABILITY>` | `<MODE>` | `<CONFIGURATION>` | `<PASS_CRITERION>` | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |

## Reference Results

| Evaluation | Reference Runtime | Model Revision | Hardware | Settings | Metric | Result | Evidence |
|---|---|---|---|---|---|---|---|
| `<EVALUATION>` | `<REFERENCE_RUNTIME>` | `<MODEL_REVISION>` | `<HARDWARE>` | `<SETTINGS>` | `<METRIC>` | `<REFERENCE_RESULT>` | `<REFERENCE_LINK>` |

## Accuracy Results

| Date | Code Commit | Model Revision | Platform | Configuration | Evaluation | Result | Gate | Status | Round |
|---|---|---|---|---|---|---|---|---|---|
| `<YYYY-MM-DD>` | `<CODE_SHA>` | `<MODEL_REVISION>` | `<PLATFORM>` | `<CONFIGURATION>` | `<EVALUATION>` | `<RESULT>` | `<GATE>` | `<STATUS>` | `data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Establish reference behavior — `<STATUS>`

- [ ] Pin `<REFERENCE_IMPLEMENTATION>`, `<MODEL_REVISION>`, and evaluation revisions.
- [ ] Define release capabilities and required configurations.
- [ ] Record reference results with raw evidence.

### Stage 2: Validate implementation — `<STATUS>`

- [ ] Run smoke, quality, API, and configuration matrices on `<CODE_SHA>`.
- [ ] Triage deltas and bind each issue to `<OWNER>`.
- [ ] Add regression coverage for every fixed release-blocking issue.

### Stage 3: Certify release artifacts — `<STATUS>`

- [ ] Rerun gates on the locked code, model, and container artifacts.
- [ ] Resolve every failed or missing cell with an explicit release decision.
- [ ] Link final evidence from `day0-delivery/README.md`.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<HARDWARE>; <EVALUATION>; <CONFIGURATION>` | `<RESULT>` | `data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md` |
