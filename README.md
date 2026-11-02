# Day-0 Model Track

This repository template separates upstream SGLang mirrors, Day-0 model implementation work, reference implementations, and project tracking across four branches.

## Branches
- `track`(default): Stores planning, validation, feature evidence, and release-delivery records on standalone orphan history.
- `sglang-main`: Mirrors the latest upstream SGLang `main` and provides the clean baseline for starting or updating Day-0 model work. It is deliberately not named `main`, so upstream's `push: branches: [main]` workflows do not fire in this repository on every sync.
- `dev`: Maintains a second exact, fast-forward-only mirror of upstream SGLang `main` and serves as the base for short-lived Day-0 implementation branches. Do not commit or merge Day-0 changes directly into it.
- `ref-code`: Stores simple, readable reference implementations, such as naïve PyTorch implementations, for correctness validation and comparison.

## Repository Structure

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

The template intentionally starts without experiment data, reproduction scripts, or release assets. Add those artifacts only when real work produces them.

## Directory Responsibilities

| Path | Responsibility |
|---|---|
| `.github/workflows/` | Scheduled and manually dispatched repository automation. |
| `AGENTS.md` | Canonical operating rules, content-routing rules, and reusable templates for agents and contributors. |
| `CLAUDE.md` | Entry point that directs Claude-compatible agents to the canonical rules. |
| `scripts/` | Implementations for repository automation. |
| `features/` | Capability projects and selectable subprojects, each with its own summary, assignees, stages, and experiment index. |
| `day0-delivery/` | Release coordination, artifact locks, and the cookbook, Docker, and blog deliverables. |

## Feature Catalog

The catalog contains P0 and P1 tracking projects. New top-level features follow `features/p<X>-<feature-name>`; subprojects use lowercase, hyphen-separated directory names. Select the required subprojects within Parallelism, Multimodal Optimization, and Multi-Platform Support. Complete Parallelism Analysis and Design before implementing any concrete parallelism feature.

| Project | Purpose | Status | Assignees |
|---|---|---|---|
| `features/p0-correctness/` | Validate model quality, API behavior, feature compatibility, and regression gates. | `<STATUS>` | `<OWNER>` |
| [Tool-Call Parser](features/p0-tool-call-parser/README.md) | Implement and validate the tool-call detector and parser auto-detection against the model's native call format. | `<STATUS>` | `<OWNER>` |
| [Reasoning Parser](features/p0-reasoning-parser/README.md) | Implement and validate the reasoning parser, thinking defaults, and supported reasoning levels. | `<STATUS>` | `<OWNER>` |
| `features/p0-general-performance/` | Track one-batch and serving performance across representative workloads and hardware. | `<STATUS>` | `<OWNER>` |
| `features/p0-agentx-performance/` | Measure agentic-workload latency, throughput, concurrency scaling, and cache behavior. | `<STATUS>` | `<OWNER>` |
| `features/p0-kernel-opt/` | Track kernel bottlenecks, optimization stages, microbenchmarks, and end-to-end impact. | `<STATUS>` | `<OWNER>` |
| `features/p0-spec-decoding-training/` | Track draft-model training, checkpoint selection, evaluation, and release readiness. | `<STATUS>` | `<OWNER>` |
| [Prefill–Decode Disaggregation](features/p0-pd-disagg/README.md) | Separate prefill and decode resources and validate routing, KV transfer, and latency. | Not started | `<OWNER>` |
| [Hierarchical KV Caching (HiCache)](features/p0-hicache/README.md) | Reuse prompt prefixes across GPU, host, and storage cache tiers. | Not started | `<OWNER>` |
| [MegaMoE](features/p0-megamoe/README.md) | Evaluate and integrate the selected MegaMoE implementation. | Not started | `<OWNER>` |
| [Parallelism](features/p0-parallelism/README.md) | Complete the shared design, then implement selected parallelism strategies. | Not started | `<OWNER>` |
| [Breakable CUDA Graph](features/p1-breakable-cuda-graph/README.md) | Combine captured graph segments with operations that require eager execution. | Not started | `<OWNER>` |
| [Unified Memory](features/p1-unified-memory/README.md) | Evaluate memory-management support, capacity, and latency tradeoffs. | Not started | `<OWNER>` |
| [Multimodal Optimization](features/p1-multimodal-opt/README.md) | Select and validate encoder and serving optimizations for multimodal workloads. | Not started | `<OWNER>` |
| [Multi-Platform Support](features/p1-multi-platform/README.md) | Select and validate hardware platforms required for the model release. | Not started | `<OWNER>` |
| [Reinforcement Learning](features/p1-rl/README.md) | Define and validate serving integration for reinforcement-learning workflows. | Not started | `<OWNER>` |

Recommended status values are `Not started`, `In progress`, `Blocked`, and `Complete`.

## Content Routing

| Content | Destination |
|---|---|
| Reusable benchmark and operation-record formats | `AGENTS.md` |
| Feature goal, technical decision, todo, or progress update | The corresponding `features/<project>/README.md` stage |
| Reproduction script used by one feature | `features/<project>/scripts/vN/` |
| One reproducible experiment round | `features/<project>/data/data@<YYYY-MM-DD>-<CODE_SHA>/` |
| Release-wide status or immutable artifact pin | `day0-delivery/README.md` |
| Deployment guidance for users | `day0-delivery/cookbook/` |
| Container build and publication material | `day0-delivery/docker/` |
| Release announcement and supporting prose | `day0-delivery/blog/` |

## Placeholder Convention

Angle-bracket tokens identify information that must be supplied by a model-support team. Common placeholders include:

- `<MODEL_NAME>`
- `<OWNER>`
- `<STATUS>`
- `<YYYY-MM-DD>`
- `<CODE_SHA>`
- `<MODEL_REVISION>`
- `<HARDWARE>`
- `<IMAGE_DIGEST>`
- `<METRIC>`
- `<PR_URL>`

Replace placeholders only when the value is known and can be linked to reproducible evidence. Do not publish unbound performance or correctness numbers.
