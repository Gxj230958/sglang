# E11 GB300 delivery configuration sweep — data@2026-11-17-e9a0a02872-gb300-delivery

## Environment

- Machine: 4x GB300 GPUs on the shared Blackwell development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Models: FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` and NVFP4 revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`; both natural-MTP configurations use the FP8 draft checkpoint.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

Eight configurations cross FP8/NVFP4 weights, natural EAGLE 3/1/4 or MTP off, BF16 KV with FlashMLA Sparse and breakable prefill, or FP8-E4M3 KV with TRTLLM DSA and eager prefill. All use TP4, TRTLLM MoE, max-running-requests 64 and chunk 8192. Exact launch commands and resolved arguments are preserved in `terminal-evidence.tar.gz`.

## Commit

- Code commit: `e9a0a0287215c18b08ecb120f9d00db52986052b`.
- Working tree: clean source archive; post-run verification found all 12,586 source files unchanged.
- Release status: non-release. KV dtype and prefill mode vary together in this round; use E13 for the FP8-KV breakable follow-up.

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
| NVFP4, BF16 KV, breakable, MTP off | 32 | 896.8 | 6513 | 1919 | 1203.0 (64) |
| NVFP4, FP8 KV, eager, MTP off | 32 | 852.3 | 6190 | 2239 | 1215.3 (64) |
| FP8, FP8 KV, eager, MTP off | 32 | 722.8 | 5249 | 2167 | 1020.0 (64) |
| FP8, BF16 KV, breakable, MTP off | 32 | 722.7 | 5248 | 2265 | 969.2 (64) |
| NVFP4, BF16 KV, breakable, natural | 8 | 504.6 | 3664 | 946 | 1202.6 (64) |
| FP8, BF16 KV, breakable, natural | 8 | 399.7 | 2902 | 1088 | 979.8 (64) |
| NVFP4, FP8 KV, eager, natural | 4 | 200.9 | 1459 | 813 | 569.2 (64) |
| FP8, FP8 KV, eager, natural | 4 | 186.5 | 1354 | 770 | 545.5 (64) |

Conclusions:

1. The best SLO-passing point in this round is NVFP4 with BF16 KV, breakable prefill and MTP off at concurrency 32.
2. The FP8-KV natural-MTP rows used eager prefill and must not be interpreted as an intrinsic KV-dtype regression; E13 isolates that follow-up.
3. NVFP4 remains performance-only, and these profiles require validation on the locked delivery artifacts.

## Data and Figures

- `summary.md` — best SLO-passing configurations.
- `independent-report.md` and `independent-report.json` — independently recomputed per-level results.
- `terminal-evidence.tar.gz` — raw responses, timing, launch commands and runtime evidence, retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `manifest.json` and `SHA256SUMS` — artifact integrity records.
