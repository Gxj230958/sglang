# E01 Rust breakable prefill on GB300

## Environment

Four GB300 GPUs, TP4, FP8 GLM-5-1028-Provider weights, BF16 KV, FlashMLA sparse attention and FlashInfer TRTLLM MoE. Imported versions: Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT providers 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. The container digest was not captured; these are non-release measurements.

Model metadata matches [General Performance E05](../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-moe-sweep/repro.md): config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`, tokenizer SHA256 `19e773648cb4e65de8660ea6365e10acca112d42a854923df93db4a6f333a82d`. Provision the immutable FP8 provider revision and evaluated config from the [private artifact handoff](../../../p0-general-performance/data/data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md). This experiment verified metadata rather than every weight shard.

## Commit

Serving source: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`. The [source audit](source-audit.json) verifies all 6,915 preserved Python/Rust deployment files against Git; it does not establish a fresh hash of every live source file. All four scheduler ranks in both launched configurations logged `RustUnifiedTreeCore` and mapped extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`.

## Setup

Verify [SHA256SUMS](SHA256SUMS), extract [evidence.tar.gz](evidence.tar.gz), and verify the extracted bytes against [files.json](files.json). Install the recorded dependencies and deploy the pinned source. Set `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=rust`, `SGLANG_RUST_BUILD_MODE=auto`, a task-local `SGLANG_CACHE_DIR`, and `CARGO_BUILD_JOBS=4`; the recorded compiler is Rust 1.92.0.

Use `bcg/sweep.json` with the unchanged workspace `serve_sweep.py`, SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`. Adapt task-local paths in the configuration and external adapters. Server argv/environment and client commands are preserved in the candidate and repeat records. The common serving arguments are:

```bash
python3 -m sglang.launch_server \
  --model-path /scratch/models/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31080 --dist-init-addr 127.0.0.1:31120 \
  --tp-size 4 --mem-fraction-static 0.80 --context-length 32768 \
  --max-running-requests 64 --cuda-graph-max-bs-decode 64 \
  --chunked-prefill-size 8192 --enable-fp32-lm-head \
  --reasoning-parser glm45 --tool-call-parser glm47 \
  --enable-cache-report --enable-metrics \
  --cuda-graph-backend-prefill breakable
```

The eager comparison replaces the last option with `--disable-prefill-cuda-graph`. At this source revision, omitting both options also resolves to disabled prefill graphs for this model. Explicit breakable selection captures 58 aggregate-token buckets through 8192. Buckets describe uncached scheduler-forward tokens, not request history or concurrency. Argument resolution for a 2048-token cap is preserved, but that configuration was not launched.

## Scripts

The archive contains the exact configuration, external server/load/sanity adapters, argument controls, graph census and evaluation commands. Serving source and the unchanged benchmark runner are identified by commit/hash above. The eager baseline's complete raw data is in [General Performance E05](../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-moe-sweep/repro.md).

## Workload

Use the [frozen four-turn workload](../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompressed SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Each repeat uses max(16, 2×concurrency) conversations, four turns each, 128 output tokens per turn, temperature 1, top_p 0.95, thinking off and ignore EOS. Concurrency is 1/2/4/8/16/32; seeds are 1/2. Flush cache before each repeat and run one warmup conversation.

Score is total input plus output tokens divided by measured seconds and four GPUs, including resent/cached input. Aggregate rates and latencies are medians of two repeats. Gates are P90 TTFT ≤3 seconds, P90 interactivity ≥30 tok/s, all requests successful and all responses nonempty. Three natural-stop probes precede load measurement.

## Results

MTP-off BCG completed 12 loads and 1,280 successful, nonempty requests. Every point and both individual repeats pass the load gates; three sanity requests stopped normally.

| Concurrency | Eager total tok/s/GPU | BCG total tok/s/GPU | Eager P90 TTFT (s) | BCG P90 TTFT (s) |
|---|---:|---:|---:|---:|
| 1 | 561.937 | 661.086 | 0.381 | 0.125 |
| 2 | 874.148 | 1102.034 | 0.728 | 0.246 |
| 4 | 1470.494 | 1727.825 | 0.754 | 0.580 |
| 8 | 2453.754 | 2645.435 | 1.069 | 1.012 |
| 16 | 3528.850 | 3755.269 | 1.662 | 1.648 |
| 32 | 5098.106 | 5242.682 | 2.306 | 2.289 |

C32 gains 2.84% over its eager BF16 twin; its P90 interactivity is 32.126 tok/s. C32 remains the highest tested concurrency, so the passing capacity boundary is unknown. All 524 logged prefill forwards within measured load windows report graph replay. This census includes warmup and uses sampled windows with two-second margins and one-second log timestamps.

Target prefill capture takes 69.29–69.31 seconds and adds 5.77–5.78 GiB per rank. The full/window KV pools remain 485,120/48,512 tokens. This is a capture allocation delta, not a total model-memory estimate.

The first arm's separate GSM8K200 indicator used sgl-eval 0.1.2, seed 1, temperature 1/top_p 0.95, 16 threads, max_tokens 16384 and requests with thinking disabled: **182/200 correct, 198 stop, two length-limited empty final answers, zero request errors**. It is not a paired eager/BCG accuracy gate.

The natural EAGLE 3/1/4 BCG arm captured successfully on four Rust ranks, then stopped at pre-load sanity: two replies stopped, while the HTTP503 diagnostic prompt exhausted 1024 reasoning tokens and returned an empty final answer. The saved reasoning is coherent; this establishes output-budget truncation, not a Rust-core cause. No throughput result exists for that arm. The 2048-cap arm was blocked before server launch.

## Data and limits

- [Independent audit](audit.json): all load totals, raw TTFT/ITL, throughput, median selection, GSM8K IDs/finish reasons and graph census.
- [Eager comparison](eager-baseline-audit.json): matched points from General Performance E05.
- [Raw evidence and adapters](evidence.tar.gz), [file manifest](files.json), [source audit](source-audit.json), [checksums](SHA256SUMS).

Matched NVFP4 BCG measurements remain required on a common supporting source. This historical FP8 round remains incomplete for deployment selection. One launch per arm and two fixed-order repeats do not establish launch-to-launch variability. Full correctness, MTP performance, the 2048 cap, wider parallelism and locked release validation remain pending.
