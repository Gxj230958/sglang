# E14 H200 default-profile sweep — data@2026-11-17-ac08d9be93-h200-defaults

## Environment

- Machine: 8x H200 GPUs on the shared Hopper development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Model: FP8 GLM LoopLM at revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; the draft uses the same checkpoint.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

The two TP8 configurations compare natural EAGLE and MTP off with the streamlined launch defaults: BF16 KV, FlashMLA Sparse DSA, automatic MoE selection, default breakable prefill, self-draft, max-running-requests 64 and no explicit context length, prefill chunk, memory fraction or FP32 LM head. `natural.json` and `mtp-off.json` preserve the exact candidate definitions; `launch-call.json` records the launch and `preparation-review.json` records staging checks.

## Commit

- Code commit: `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`.
- Working tree: staged source verified by the sweep harness.
- Release status: non-release; this test head predates the final squash-merge identities and must be reproduced on the locked delivery artifacts.

## Scripts

- Canonical `serve_sweep.py` and the executed inputs are retained with the local raw archive.
- Candidate plans and the canonical workload SHA256 are included in this round.

## Workload

- Workload: synthetic four-turn service-debugging chat, SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`.
- Output: 128 tokens per turn, thinking disabled; temperature 1.0, top_p 0.95.
- Concurrency: 1, 4, 8, 16, 32 and 64, two repeats with request seeds 1 and 2.
- Gates: TTFT p90 <= 3 s, interactivity p90 >= 30 tok/s, zero request errors and zero empty responses.

## Results

All 24 points completed with 4,352 successful responses, zero errors and zero empty outputs.

| Configuration | Best SLO concurrency | Output tok/s | Total tok/s/GPU | TTFT p90 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|
| FP8 TP8 defaults, MTP off | 16 | 458.6 | 1665 | 2151 | 590.8 (32) |
| FP8 TP8 defaults, natural MTP | 8 | 364.4 | 1323 | 1316 | 742.9 (64) |

Conclusions:

1. MTP-off at C16 is the best SLO-passing default-profile point in this H200 round.
2. Natural MTP passes through C8 and improves low-concurrency output, but misses the interactivity gate from C16.
3. These measurements are specific to the frozen four-turn workload and do not certify quality or release readiness.

## Data and Figures

- `summary.md` and `independent-report.md` — best points and all per-concurrency rows.
- `independent-report.json` — independently recomputed aggregates.
- `natural.json` and `mtp-off.json` — exact candidate plans.
- `terminal-evidence.tar.gz` — retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `SHA256SUMS` — integrity records for files included in this branch.
