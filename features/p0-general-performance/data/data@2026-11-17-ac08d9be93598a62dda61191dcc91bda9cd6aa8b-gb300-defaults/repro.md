# E15 GB300 default-profile sweep — data@2026-11-17-ac08d9be93-gb300-defaults

## Environment

- Machine: 4x GB300 GPUs on the shared Blackwell development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Models: FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` and NVFP4 revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

Eight configurations cross FP8/NVFP4 weights, BF16/FP8 KV and natural EAGLE or MTP off. They use TP4, default breakable prefill and self-draft, max-running-requests 64, and streamlined defaults for the remaining tuning flags. FP8 KV is explicitly selected where applicable. `natural.json` and `mtp-off.json` preserve exact candidate definitions.

## Commit

- Code commit: `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`.
- Working tree: staged source verified by the sweep harness.
- Release status: non-release. The NVFP4 natural-MTP rows predate #89 and are excluded from final profile selection.

## Scripts

- Canonical `serve_sweep.py` and the executed inputs are retained with the local raw archive.
- Candidate plans and the canonical workload SHA256 are included in this round.

## Workload

- Workload: synthetic four-turn service-debugging chat, SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`.
- Output: 128 tokens per turn, thinking disabled; temperature 1.0, top_p 0.95.
- Concurrency: 1, 4, 8, 16, 32 and 64, two repeats with request seeds 1 and 2.
- Gates: TTFT p90 <= 3 s, interactivity p90 >= 30 tok/s, zero request errors and zero empty responses.

## Results

All 96 points completed with 17,408 successful responses, zero errors and zero empty outputs.

| Configuration | Best SLO concurrency | Output tok/s | Total tok/s/GPU | TTFT p90 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|
| NVFP4, FP8 KV, MTP off | 64 | 1398.8 | 10159 | 2460 | 1398.8 (64) |
| NVFP4, BF16 KV, MTP off | 64 | 1292.4 | 9386 | 2756 | 1292.4 (64) |
| FP8, FP8 KV, MTP off | 32 | 794.5 | 5769 | 1690 | 1114.6 (64) |
| FP8, BF16 KV, MTP off | 32 | 760.5 | 5523 | 1977 | 1026.7 (64) |
| NVFP4, FP8 KV, natural, pre-#89 | 16 | 453.9 | 3296 | 1142 | 985.4 (64) |
| FP8, FP8 KV, natural | 8 | 423.5 | 3076 | 1038 | 1113.2 (64) |
| NVFP4, BF16 KV, natural, pre-#89 | 16 | 422.2 | 3066 | 1313 | 905.6 (64) |
| FP8, BF16 KV, natural | 8 | 395.3 | 2870 | 1331 | 999.8 (64) |

Conclusions:

1. NVFP4 with FP8 KV and MTP off at C64 is the best SLO-passing configuration in this round.
2. The NVFP4 natural-MTP rows used the broken self-draft path with accept length near one; they must be rerun after #89 before making a natural-MTP recommendation.
3. FP8 natural-MTP rows and all MTP-off rows are valid measurements within this workload; NVFP4 remains performance-only.

## Data and Figures

- `summary.md` and `independent-report.md` — best points and all per-concurrency rows.
- `independent-report.json` — independently recomputed aggregates.
- `natural.json` and `mtp-off.json` — exact candidate plans.
- `terminal-evidence.tar.gz` — retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `SHA256SUMS` — integrity records for files included in this branch.
