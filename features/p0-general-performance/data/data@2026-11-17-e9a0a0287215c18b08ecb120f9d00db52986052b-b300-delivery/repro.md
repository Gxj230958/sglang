# E12 B300 delivery configuration sweep — data@2026-11-17-e9a0a02872-b300-delivery

## Environment

- Machine: 8x B300 GPUs on the shared Blackwell development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Models: FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` and NVFP4 revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`; both natural-MTP configurations use the FP8 draft checkpoint.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

Eight configurations cross TP8 and DEP8, FP8/NVFP4 weights, and natural EAGLE 3/1/4 or MTP off. All use FP8 KV, TRTLLM DSA and MoE, eager prefill and fused H64 decode disabled. Exact launch commands, per-rank subdivisions and resolved arguments are preserved in `terminal-evidence.tar.gz`.

## Commit

- Code commit: `e9a0a0287215c18b08ecb120f9d00db52986052b`.
- Working tree: clean source archive; post-run verification found all 12,586 source files unchanged.
- Release status: non-release. The subsequent default-BCG sweep supersedes this eager configuration for final profile selection.

## Scripts

- Canonical `serve_sweep.py` SHA256: `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`.
- Executed inputs and command records are in the evidence archive.

## Workload

- Workload: synthetic four-turn service-debugging chat, SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`.
- Output: 128 tokens per turn, thinking disabled; temperature 1.0, top_p 0.95.
- Concurrency: 1, 4, 8, 16, 32 and 64, two repeats with request seeds 1 and 2.
- Gates: TTFT p90 <= 3 s, interactivity p90 >= 30 tok/s, zero request errors and zero empty responses.

## Results

All 96 points completed with 17,408 successful responses, zero errors and zero empty outputs.

| Configuration | SLO concurrency | Output tok/s | Total tok/s/GPU | TTFT p90 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|
| NVFP4, TP8, MTP off | 64 | 1488.7 | 5406 | 2759 | 1488.7 (64) |
| FP8, TP8, MTP off | 32 | 940.1 | 3414 | 2184 | 1347.3 (64) |
| NVFP4, DEP8, MTP off | 32 | 939.1 | 3410 | 1849 | 1395.0 (64) |
| FP8, DEP8, MTP off | 32 | 839.6 | 3049 | 1931 | 1265.1 (64) |
| NVFP4, TP8, natural | 4 | 240.0 | 872 | 657 | 669.8 (64) |
| FP8, TP8, natural | 4 | 231.5 | 841 | 649 | 692.4 (64) |
| NVFP4, DEP8, natural | 4 | 212.5 | 772 | 610 | 587.1 (64) |
| FP8, DEP8, natural | 4 | 198.9 | 722 | 522 | 596.1 (64) |

Conclusions:

1. NVFP4 TP8 with MTP off at concurrency 64 is the best SLO-passing point in this eager-prefill round.
2. TP8 leads DEP8 at every matched point in this workload.
3. These results do not measure the default fused-H64 or default-BCG delivery path; final selection waits for the integrated default sweep.

## Data and Figures

- `summary.md` — best SLO-passing configurations.
- `independent-report.md` and `independent-report.json` — independently recomputed per-level results.
- `terminal-evidence.tar.gz` — raw responses, timing, launch commands and runtime evidence, retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `manifest.json` and `SHA256SUMS` — artifact integrity records.
