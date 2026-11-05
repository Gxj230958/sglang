# Day-0 Model Track Operating Rules

This orphan branch is the planning, validation, and release-tracking hub for a Day-0 model integration. It contains tracking material only and must never be merged into a code branch.

Read this file before editing any tracked content.

## Branch Contract

- Keep `sglang-main` aligned with the latest upstream SGLang `main`; do not land Day-0 model development directly on it. The mirror branch is not named `main` so that upstream's `push: branches: [main]` workflows do not fire here on every sync.
- Keep `dev` aligned with the latest upstream SGLang `main` as a second exact, fast-forward-only mirror; do not commit or merge Day-0 model development directly into it.
- Use `ref-code` for simple, readable, unoptimized implementations that serve as correctness references; do not use it for production optimizations.
- Create short-lived implementation branches from `dev` and submit validated changes directly upstream; never merge them back into `dev`.
- Sync upstream changes automatically into `sglang-main` and `dev`; sync them into `ref-code` through reviewed updates.
- Tracking work belongs on branches based on `track`.
- Merge tracking changes into `track` through pull requests.
- Never merge `track` into `sglang-main`, `dev`, `ref-code`, or another code branch.
- Never copy source files from a code branch into this branch.
- Bind every official result to an exact code commit and reproducible environment.
- Keep experiment rounds and any chronological operation records append-only.
- Write all human-authored content in English.

## Code Development Workflow

1. Let the scheduled workflow update `sglang-main` and `dev` from upstream SGLang.
2. Bring the required `sglang-main` updates into `ref-code` through reviewed changes.
3. Add a readability-first baseline to `ref-code` when a reference implementation is needed.
4. Create implementation branches from `dev`.
5. Validate implementation code from an exact commit against an exact `ref-code` commit, then record the evidence on `track`.
6. Open upstream SGLang pull requests from reviewed and validated implementation branches.
7. Let merged upstream changes return through the scheduled mirrors before starting dependent work.

## Repository Layout

```text
(branch root)
├── .github/
│   └── workflows/
│       └── sync-sglang-main.yml
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── scripts/
│   └── sync_sglang_main.sh
├── features/
│   ├── p0-correctness/
│   ├── p0-tool-call-parser/
│   ├── p0-reasoning-parser/
│   ├── p0-general-performance/
│   ├── p0-agentx-performance/
│   ├── p0-kernel-opt/
│   ├── p0-spec-decoding-training/
│   ├── p0-pd-disagg/
│   ├── p0-hicache/
│   ├── p0-megamoe/
│   ├── p0-parallelism/
│   │   ├── analysis-and-design/
│   │   ├── dp-attention/
│   │   ├── prefill-cp/
│   │   ├── decode-cp/
│   │   ├── pp/
│   │   └── wide-ep/
│   ├── p1-breakable-cuda-graph/
│   ├── p1-unified-memory/
│   ├── p1-multimodal-opt/
│   │   ├── epd-disagg/
│   │   ├── dp-encoder/
│   │   └── encoder-cuda-graph/
│   ├── p1-multi-platform/
│   │   ├── nvidia-hopper/
│   │   ├── nvidia-blackwell/
│   │   ├── amd/
│   │   ├── intel-xpu-xeon/
│   │   ├── ascend-npu/
│   │   └── tpu/
│   └── p1-rl/
└── day0-delivery/
    ├── README.md
    ├── cookbook/
    │   └── README.md
    ├── docker/
    │   └── README.md
    └── blog/
        └── README.md
```

Every feature and subproject directory contains a `README.md`.

Reserve the root `.github/workflows/` and `scripts/` directories for repository automation. Create `scripts/` and `data/` below a feature only when real work produces reusable feature scripts or experiment evidence. Do not add empty scaffolding directories.

## Content Routing

| Content | Destination |
|---|---|
| Branch purpose, directory map, project index, or shared workflow | Root `README.md` |
| Agent editing rules and reusable templates | `AGENTS.md` |
| Shared benchmark formats and comparison methodology | Benchmark Conventions in this file |
| Scheduled repository automation | `.github/workflows/` with implementation in root `scripts/` |
| Feature goal, decision, todo, stage, or concise experiment result | `features/<project>/README.md` |
| Versioned reproduction script for one feature | `features/<project>/scripts/vN/` |
| Complete evidence from one experiment | `features/<project>/data/data@<YYYY-MM-DD>-<CODE_SHA>/` |
| Cross-feature correctness result | `features/p0-correctness/README.md` and its experiment round |
| Release status and immutable artifact pins | `day0-delivery/README.md` |
| User deployment guidance | `day0-delivery/cookbook/` |
| Container recipes and publication evidence | `day0-delivery/docker/` |
| Release announcement and claim evidence | `day0-delivery/blog/` |

## Feature README Template

Each directory under `features/`, including nested subprojects, owns one capability or planning responsibility. Use this structure when initializing or updating its README:

````markdown
# <FEATURE_NAME>

## Summary

<One concise paragraph covering background, goal, constraints, current status, key metrics, related code branch or pull request, and dependencies.>

## Scope

### In Scope

- <IN_SCOPE_ITEM>

### Out of Scope

- <OUT_OF_SCOPE_ITEM>

## Success Criteria

- [ ] <MEASURABLE_CRITERION>

## Assignees

- `<OWNER>` — <RESPONSIBILITY>

## Stages

### Stage 1: <STAGE_NAME> — <STATUS>

- [ ] <CONCRETE_TASK> (`<OWNER>`)
- Decision: <TECHNICAL_DECISION>
- Experiment [E01](data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md): <ONE_SENTENCE_RESULT>
- Scripts: [scripts/v1/](scripts/v1/) — <PURPOSE>

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<HARDWARE>; <WORKLOAD>` | `<RESULT>` | [round](data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md) |
````

### Feature README Rules

- Initialize a template Summary from the requested scope; the human owner confirms model-specific goals, dependencies, and acceptance thresholds and keeps it current as the project changes.
- A stage may freely mix decisions, todos, experiment summaries, and script pointers.
- Use `Not started`, `In progress`, `Blocked`, or `Complete` for status text.
- When completing a todo, append the owner and completion date.
- Keep only a link and one-sentence result in the Experiments table.
- Store full setup, raw output, analysis, and conclusions in the experiment round.
- For a parent project with subdirectories, list and link each subproject and state that the team selects the features it needs for implementation. Record selected and deferred work explicitly.
- Complete `features/p0-parallelism/analysis-and-design/` before implementing any concrete parallelism feature.
- Assign experiment IDs per feature in increasing order: `E01`, `E02`, and so on.
- Never reuse an experiment ID, even if an earlier round is invalidated.
- Do not record a metric without a code commit and reproduction record.

## Experiment Round Rules

Name each round `data@<YYYY-MM-DD>-<CODE_SHA>`. Add a short topic suffix when multiple rounds share the same date and commit.

Examples:

```text
data/data@<YYYY-MM-DD>-<CODE_SHA>/
data/data@<YYYY-MM-DD>-<CODE_SHA>-<TOPIC>/
```

Every round must be self-contained and include `repro.md` with this structure:

````markdown
# E01 <TOPIC> — data@<YYYY-MM-DD>-<CODE_SHA>

## Environment

- Machine: `<HOST_ALIAS_OR_TYPE>`
- Container: `<CONTAINER_NAME>` using `<IMAGE_DIGEST>`
- Hardware: `<HARDWARE>` x `<DEVICE_COUNT>`
- Model: `<MODEL_NAME>` at revision `<MODEL_REVISION>`
- Software: `<DEPENDENCY_VERSIONS>`

## Setup

<Complete steps from a clean environment to a runnable command. Include dependency installation, model acquisition, environment variables, and launch commands.>

## Commit

- Code commit: `<CODE_SHA>`
- Working tree: `<CLEAN_OR_DESCRIBE_CHANGES>`

## Scripts

- Version: [scripts/v1/](../../scripts/v1/)
- Temporary changes: `<NONE_OR_LIST_EACH_CHANGE>`

## Workload

- Dataset or request source: `<SOURCE_URL_OR_REVISION>`
- Input and output lengths: `<WORKLOAD_SHAPE>`
- Concurrency or batch size: `<LOAD_SHAPE>`
- Sampling and evaluation settings: `<SETTINGS>`

## Results

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| `<METRIC>` | `<BASELINE>` | `<CANDIDATE>` | `<DELTA>` |

Conclusions:

1. <CONCLUSION>

## Data and Figures

- `<RAW_FILE>` — <MEANING>
- `<FIGURE>.svg` — generated by `<SCRIPT>` from `<RAW_FILE>`
````

### Evidence Rules

- Preserve raw outputs as produced; do not backfill or rewrite fields.
- Compress large logs, traces, and record files before committing them.
- Store input datasets by stable external reference instead of copying them into this branch.
- Keep only files relevant to the round.
- Use public, descriptive names instead of internal codenames.
- Use SVG for generated figures when practical and record the rendering command.
- Visually inspect every figure before committing it.
- If a run mixes code commits, record the full commit window and mark the result non-release until rerun on one pinned commit.

## Script Versioning Rules

- Store reusable scripts in `scripts/vN/`.
- Create a new version when changing behavior used by a recorded round.
- Never rewrite a script version referenced by historical evidence.
- Add `CHANGES.md` to every version, stating what changed and why.
- Keep one-off round-specific changes in the round and document them in `repro.md`.

## Benchmark Conventions

Use the following formats in the owning feature README and experiment rounds. Record shared workload definitions in the relevant performance feature and link other comparisons to the same definition. Keep release-gating quality and compatibility evidence under `features/p0-correctness/`.

### Benchmark Matrix

| Lane | Purpose | Workload | Primary Metrics | Required Platforms | Owner | Status |
|---|---|---|---|---|---|---|
| Correctness | Detect quality and behavior regressions | `<EVALUATION_SUITE>` | `<QUALITY_METRIC>` | `<PLATFORM_SET>` | `<OWNER>` | `<STATUS>` |
| One-batch performance | Measure controlled prefill and decode efficiency | `<INPUT_OUTPUT_SHAPE>; <BATCH_SWEEP>` | `<LATENCY_OR_THROUGHPUT_METRIC>` | `<PLATFORM_SET>` | `<OWNER>` | `<STATUS>` |
| Online serving | Measure scheduler and system behavior under load | `<REQUEST_DISTRIBUTION>; <CONCURRENCY_SWEEP>` | `<TTFT>; <ITL>; <THROUGHPUT>` | `<PLATFORM_SET>` | `<OWNER>` | `<STATUS>` |
| AgentX | Replay representative agentic traces | `<TRACE_SET>; <CONCURRENCY_SWEEP>` | `<LATENCY>; <THROUGHPUT>; <CACHE_METRIC>` | `<PLATFORM_SET>` | `<OWNER>` | `<STATUS>` |
| Speculative decoding | Measure draft effectiveness and serving impact | `<DRAFT_CONFIGURATION>; <LOAD_SHAPE>` | `<ACCEPTANCE>; <SPEEDUP>; <MEMORY>` | `<PLATFORM_SET>` | `<OWNER>` | `<STATUS>` |

### Required Result Metadata

Every benchmark result must record:

- code commit and working-tree state;
- model revision and tokenizer or processor revision;
- container digest or complete dependency versions;
- hardware type, device count, topology, and relevant power mode;
- launch command and all behavior-changing environment variables;
- workload source, revision, input distribution, output distribution, and request count;
- batch size, concurrency, sampling, warmup, repetition, and timeout settings;
- metric definitions and aggregation method;
- raw-output filenames and rendering commands;
- baseline selection and a concise conclusion.

### Methodology Rules

- Compare baseline and candidate with the same workload, environment, and measurement procedure.
- Pin every comparison to immutable code and model revisions.
- Separate warmup from measured requests.
- Report failed requests, timeouts, outliers, and excluded samples.
- Record enough raw data to recompute every published aggregate.
- Open a new benchmark round when methodology changes.
- Do not join results from incompatible methodology into one trend line.
- Keep correctness gates enabled for performance configurations intended to ship.
- Treat preview numbers as non-release until reproduced on the locked release artifacts.

### Results Index

| ID | Date | Lane | Platform | Code Commit | Model Revision | Result | Evidence |
|---|---|---|---|---|---|---|---|
| `<BENCHMARK_ID>` | `<YYYY-MM-DD>` | `<LANE>` | `<PLATFORM>` | `<CODE_SHA>` | `<MODEL_REVISION>` | `<RESULT_SUMMARY>` | `<ROUND_LINK>` |

### Release Gate

A benchmark lane is release-ready only when its workload definition is stable, required platforms are covered, raw evidence is available, correctness gates pass, and the result is bound to the artifact lock in `day0-delivery/README.md`.

## Journal Format Conventions

When a chronological operation record is useful, keep it with the owning feature's experiment evidence or in an agreed external log and link it from the feature README. These conventions define the record format without requiring a separate root-level directory. Routine commands do not need a record.

### Filename

Use:

```text
<YYYY-MM-DD>-<HHMM>-<AUTHOR>-<CODE_SHA>-<DESCRIPTION>.md
```

Use a short, lowercase, hyphenated description. Use the related code commit; when no code commit applies, use a short tracking commit or the token `no-code`.

### When to Add a Journal

Add one journal for a meaningful event such as:

- an experiment completing;
- a debugging conclusion changing the next action;
- a design decision being accepted or rejected;
- a pull request opening, merging, or being abandoned;
- a release artifact being built, validated, or published;
- a project status changing;
- a blocker being discovered or cleared.

Do not add journals for routine commands that produce no reusable context.

### Minimum Useful Content

A journal has no rigid schema, but it must answer:

- What happened?
- Why did it matter?
- Which code commit, model revision, environment, or artifact was involved?
- Where is the detailed evidence?
- What decision or next action followed?
- Which feature or delivery item owns the follow-up?

Suggested structure:

```markdown
# <EVENT_TITLE>

## Context

<WHY_THE_OPERATION_WAS_RUN>

## Outcome

<OBSERVED_RESULT_OR_DECISION>

## Evidence

- Code: `<CODE_SHA>`
- Model: `<MODEL_REVISION>`
- Experiment: `<ROUND_LINK>`
- Pull request: `<PR_URL>`

## Follow-up

- [ ] <NEXT_ACTION> (`<OWNER>`)
```

### Append-Only Rules

- Add one file per operation.
- Never edit or delete an existing journal to make history appear cleaner.
- Correct a materially wrong journal with a new entry that links to the earlier one.
- Link the owning feature README, experiment round, code commit, or pull request.
- Update the owning feature summary separately when the event changes project status.
- Keep human-authored journal text in English.
- Never include credentials, private endpoints, or unredacted sensitive logs.

## Tracking Update Workflow

1. Use a dedicated worktree created from `track`.
2. Pull or fetch the latest `track` before starting.
3. Create a short-lived tracking branch.
4. Read the owning feature README and its linked evidence and decisions.
5. Add evidence before updating conclusions or status.
6. Run language, scope, link, and formatting checks.
7. Open a pull request targeting `track` for human review.
8. Rebase if the shared branch advances; never force-push shared `track` history.

If another change takes the same stage number or experiment ID, preserve the earlier entry and move the new work to the next unused number. If an experiment-round directory name collides, add a descriptive topic suffix.

## General Discipline

- Never commit access tokens, credentials, private endpoints, or secrets.
- Write one fact per line when practical.
- Keep all human-authored prose, headings, tables, script comments, and commit messages in English.
- Preserve raw benchmark output verbatim when evidence integrity requires it.
- Use descriptive text for pull-request and issue links.
- Use short commit hashes in prose and full hashes in immutable artifact locks.
- Keep the root project table synchronized with each feature README.
- Replace angle-bracket placeholders only with verified values.
- Do not leave unmarked estimates in release-facing documents.
