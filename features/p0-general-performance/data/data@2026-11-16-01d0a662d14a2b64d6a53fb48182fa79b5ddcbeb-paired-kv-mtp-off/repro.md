# E06 Matched FP8/NVFP4 KV deployment sweep

## Environment

Four GB300 GPUs, TP4, FlashInfer Python/cubin 0.7.4 and CUDA 13 JIT providers 0.7.4+cu130. All four servers imported identical versions: Torch 2.14.1+cu130, Transformers 5.19.0, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. The container digest was not captured. This is performance-only, non-release evidence.

FP8 source revision: `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; use the evaluated config with SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f` and the immutable model/tokenizer inventory in [E04 private handoff](../data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md). NVFP4 checkpoint: `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. The same handoff preserves its verified 163-file inventory. This sweep reused those node-local checkpoints; it did not repeat all weight-shard hashing.

## Setup and commit

Runtime: `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`. Reconstruct the local integration tree using the immutable source recipe in [Correctness E18](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/repro.md). Before and after the sweep, all 12,581 source files matched its manifest. The runtime commit remains local while its publication gate is unmet.

Extract [evidence.tar.gz](evidence.tar.gz), check [SHA256SUMS](SHA256SUMS), and verify each extracted file against [files.json](files.json). Provision the recorded packages and reconstruct the source tree, then adapt task-local model/source/overlay paths in `kv-mtp-off.json` and the included external adapters. Use the unchanged workspace `serve_sweep.py` matching SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee` with `python3 execute.py run --config kv-mtp-off.json --run-dir run1`. The runner and input dataset are externally referenced. Each candidate's `replica-0.process.json` and each repeat's `client-command.json` preserve exact server/client argv and behavior-changing environment.

Common settings: TRTLLM MoE, separate shared experts, MTP off, context 32768, memory fraction 0.80, running/decode-graph cap 64, chunk 8192, disabled prefill graphs, FP32 LM head, glm45/glm47 parsers and default window KV layout. BF16 KV uses FlashMLA sparse; FP8 E4M3 KV uses TRTLLM DSA. Comparing KV deployments therefore changes both dtype and attention backend.

Set `SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1` in both weight arms, `PYTHONNOUSERSITE=1`, `SGLANG_RUST_BUILD_MODE=auto` and `CARGO_BUILD_JOBS=4`. Preserve the recorded overlay order. Unset `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND` and every `SGLANG_SIMULATE_ACC_*` variable. Every launch verified default Rust in all four ranks, with native extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`.

## Workload and metrics

Use the [E03 frozen workload](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompressed SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Concurrency 1/2/4/8/16/32, seeds 1/2, max(16, 2×concurrency) conversations per repeat, four turns, 128 output tokens per turn, temperature 1, top_p 0.95, thinking off and ignore EOS. Every repeat flushes cache and executes one warmup conversation before measurement.

Score is (sum of actual per-request input tokens + output tokens) / measured duration / four physical GPUs. It includes resent/cached inputs; generated history can change later-turn input totals between weight formats. Output throughput below is per node. Aggregate rates and latencies are medians of two repeats. SLO: P90 TTFT <=3 seconds, P90 interactivity >=30 tok/s, all requests successful and nonempty. P90 ITL is independently reconstructed from raw intervals for this MTP-off round. Natural stopping is checked separately by three chat probes per candidate.

## Results

All 48 loads completed: 24 points and 5,120 successful, nonempty requests, each generating exactly 128 tokens. All 24 aggregate points pass the SLO. The 12 separate chat probes returned nonempty final content and stopped normally. Each candidate's best measured passing point is C32.

| Candidate | Concurrency | Total tok/s/GPU | Output tok/s/node | P90 TTFT (s) | P90 interactivity (tok/s) |
|---|---:|---:|---:|---:|---:|
| fp8-kv-bf16-mtp-off | 32 | 5109.241 | 703.566 | 2.313 | 32.107 |
| fp8-kv-fp8_e4m3-mtp-off | 32 | 5276.688 | 726.609 | 2.137 | 32.602 |
| nvfp4-kv-bf16-mtp-off | 32 | 6200.219 | 853.797 | 2.039 | 41.606 |
| nvfp4-kv-fp8_e4m3-mtp-off | 32 | 6292.029 | 866.422 | 2.019 | 42.608 |

Matched NVFP4 score gain over FP8 weights:

| Concurrency | BF16 KV / FlashMLA | FP8 KV / TRTLLM DSA |
|---|---:|---:|
| 1 | +3.19% | +3.54% |
| 2 | +3.09% | +2.74% |
| 4 | +6.70% | +6.44% |
| 8 | +12.93% | +12.02% |
| 16 | +18.63% | +13.78% |
| 32 | +21.35% | +19.24% |

NVFP4 with FP8 KV scores 6292.0 total tok/s/GPU at C32, 19.24% above its matched FP8-weight deployment. NVFP4 with BF16 KV scores 6200.2, 21.35% above its matched FP8 deployment. The two NVFP4 KV deployments differ by 1.48% at C32, within the frozen 2% throughput tie band; there is no unique throughput winner between them. C32 is the highest tested concurrency and still passes, so capacity limits remain unmeasured.

The [matched full GSM8K result](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/nvfp4-full/repro.md) remains the quality boundary: FP8 95.22% accuracy/99.77% stop versus NVFP4 94.24%/99.55%, using natural MTP. Stop nonregression is unmet. This throughput sweep does not establish quality parity or authorize runtime publication. Natural MTP, controlled acceptance 3.5, additional MoE/parallelism and paired BCG/AgentX coverage remain separate work.

## Audit and evidence

[audit.json](audit.json) independently recomputes all request/token counts, throughput, raw P90 TTFT/ITL, median metrics and pass decisions. [environment-audit.json](environment-audit.json) checks equal dependency versions and the sampled process ownership: no foreign GPU process appeared during sampled active loads. Sampling cannot exclude shorter activity between samples. Final cleanup left no owned process or GPU compute context and zero MiB used on all four GPUs. The complete raw archive contains 536 files; its source checks, resolved settings, exact commands, per-rank Rust evidence, logs, raw requests and GPU samples are preserved verbatim.

One launch per candidate and two fixed-order load seeds do not establish launch-to-launch variance or confidence intervals. The archive is retained on the relay because shared GPFS is unavailable on this allocation. Historical E05 used a different runtime and is not combined with this round into a precision comparison.
