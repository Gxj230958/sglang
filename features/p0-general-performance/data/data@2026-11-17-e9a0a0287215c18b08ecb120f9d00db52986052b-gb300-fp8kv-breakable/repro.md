# E13 GB300 FP8 KV with breakable prefill — data@2026-11-17-e9a0a02872-gb300-fp8kv-breakable

## Environment

- Machine: 4x GB300 GPUs on the shared Blackwell development allocation.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Models: FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` and NVFP4 revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`; natural MTP uses the FP8 draft checkpoint.
- Software: torch 2.14.1+cu130, transformers 5.19.0, FlashInfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1.

## Setup

Four configurations cross FP8/NVFP4 weights with natural EAGLE 3/1/4 or MTP off. All use FP8-E4M3 KV, TRTLLM DSA and breakable prefill. The recipe values, workload and repeats match [E11](../data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-delivery/repro.md), allowing comparison with its BF16-KV breakable and FP8-KV eager rows. Exact commands are in `terminal-evidence.tar.gz`.

## Commit

- Code commit: `e9a0a0287215c18b08ecb120f9d00db52986052b`.
- Working tree: clean source archive; post-run source and idle-GPU checks passed.
- Release status: non-release; final profile selection moves to the integrated default-BCG source.

## Scripts

- Canonical `serve_sweep.py` SHA256: `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`.
- Executed inputs and command records are in the evidence archive.

## Workload

- Workload: synthetic four-turn service-debugging chat, SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`.
- Output: 128 tokens per turn, thinking disabled; temperature 1.0, top_p 0.95.
- Concurrency: 1, 4, 8, 16, 32 and 64, two repeats with request seeds 1 and 2.
- Gates: TTFT p90 <= 3 s, interactivity p90 >= 30 tok/s, zero request errors and zero empty responses.

## Results

All 48 points completed with 8,704 successful responses, zero errors and zero empty outputs.

| Configuration | Best SLO concurrency | Output tok/s | TTFT p90 ms | Interactivity p90 | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|
| NVFP4, MTP off | 64 | 1357.1 | 2760 | 34.6 | 1357.1 (64) |
| FP8, MTP off | 32 | 771.8 | 1896 | 32.5 | 1073.8 (64) |
| NVFP4, natural | 8 | 502.6 | 687 | 40.8 | 1337.0 (64) |
| FP8, natural | 8 | 411.4 | 878 | 33.0 | 1067.3 (64) |

Conclusions:

1. FP8 KV works with breakable prefill in all four measured configurations.
2. The earlier natural-MTP deficit came from eager prefill, not from FP8 KV or the TRTLLM backend. With breakable prefill, FP8 KV is within 7% of BF16 KV at C1–C4 and 3–13% ahead from C8/C16 upward, with lower TTFT p90 at every level from C8.
3. NVFP4 FP8-KV MTP-off reaches a new best SLO point at C64; the BF16-KV configuration fails the interactivity gate at that concurrency.
4. The rejected attribution to the 16-row TRTLLM split-decode limit is not supported by these measurements.

## Data and Figures

- `summary.md` — best SLO-passing configurations.
- `independent-report.md` and `independent-report.json` — independently recomputed per-level results.
- `terminal-evidence.tar.gz` — raw responses, timing, launch commands and runtime evidence, retained locally outside the branch; see [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
- `manifest.json` and `SHA256SUMS` — artifact integrity records.
