# E10 H200 FP8 delivery sweep — data@2026-11-17-e9a0a02872-h200-delivery

## Environment

- Machine: 8x H200 GPUs on the shared Hopper development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Model: FP8 GLM LoopLM at revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; the draft uses the same checkpoint.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

The four server configurations use TP8, BF16 KV, FlashMLA Sparse DSA, automatic MoE selection and eager prefill. They cross max-running-requests / prefill chunk values 32 / 32768 and 64 / 8192 with natural EAGLE 3/1/4 and MTP off. Exact launch commands, environment variables, dependency receipts and resolved arguments are preserved in `terminal-evidence.tar.gz` and `benchmark_commands_20261117_133125.json`.

## Commit

- Code commit: `e9a0a0287215c18b08ecb120f9d00db52986052b`.
- Working tree: clean source archive; post-run verification found all 12,586 source files unchanged.
- Release status: non-release; rerun on the locked delivery source and image before using these profiles as release recommendations.

## Scripts

- Canonical `serve_sweep.py` SHA256: `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`.
- No new versioned script is introduced by this round; the executed inputs and command records are in the evidence archive.

## Workload

- Workload: synthetic four-turn service-debugging chat, SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`.
- Output: 128 tokens per turn, thinking disabled.
- Concurrency: 1, 4, 8, 16, 32 and 64, two repeats with request seeds 1 and 2.
- Sampling: temperature 1.0, top_p 0.95; cache flushed between loads.
- Gates: TTFT p90 <= 3 s, interactivity p90 >= 30 tok/s, zero request errors and zero empty responses.

## Results

All 48 points completed with 8,704 successful responses, zero errors and zero empty outputs. The table reports each configuration's best SLO-passing point.

| MTP | Max running / chunk | Concurrency | Output tok/s | TTFT p50 / p99 ms | TPOT p50 / p99 ms |
|---|---:|---:|---:|---:|---:|
| Natural 3/1/4 | 32 / 32768 | 4 | 222.15 | 322.33 / 1378.93 | 14.82 / 20.01 |
| Off | 32 / 32768 | 16 | 435.42 | 1599.03 / 2868.53 | 22.71 / 31.43 |
| Natural 3/1/4 | 64 / 8192 | 4 | 226.56 | 319.19 / 952.33 | 14.35 / 19.43 |
| Off | 64 / 8192 | 16 | 437.00 | 1703.78 / 2588.48 | 22.80 / 31.48 |

Conclusions:

1. The two MTP-off configurations are near ties; neither establishes a decisive scheduling winner.
2. Natural MTP is faster at concurrency 1, while its best SLO-passing point is concurrency 4.
3. These are fixed-workload measurements, not evidence of quality parity or release readiness.

## Data and Figures

- `summary.md` — best SLO-passing configurations.
- `independent-report.md` and `independent-report.json` — independently recomputed per-level results.
- `benchmark_commands_20261117_133125.json` — exact client and server command records.
- `final-audit.json` — source, runtime, stream timing, GPU exclusivity and cleanup checks.
- `terminal-evidence.tar.gz` — raw responses, timing, server logs and runtime evidence, retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `manifest.json` and `SHA256SUMS` — artifact integrity records.
