# E05 Rust MoE and KV deployment sweep

## Environment

Four GB300 GPUs, TP4, FP8 target weights, FlashInfer Python/cubin 0.7.4 and JIT providers 0.7.4+cu130. Every server imported Torch 2.14.1+cu130, Transformers 5.19.0, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. The container digest was not captured; this is non-release evidence.

The model is the node-local GLM-5-1028-Provider checkpoint. Config SHA256 is `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`; index `55979a9446143325fac64918861333910a3f776d5719d2021d2b75a5c16112c1`; tokenizer `19e773648cb4e65de8660ea6365e10acca112d42a854923df93db4a6f333a82d`; tokenizer config `98b1271574f41abf89427ae2dda030d94dc9478f0edc5a8bd240db213c6fd5fc`. Use the immutable FP8 source and evaluated config described in [E04 private release](../data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md). This round verified metadata, not all weight shards.

## Setup and commit

Serving commit: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`. Preserved Python and Rust deployment archives match all 6,915 Git blobs in those subtrees; [source audit](source-audit.json) records archive hashes and the verification limit. Per-server imports identify the loaded source path. The independent archive check does not rehash every live remote source file.

Extract [evidence.tar.gz](evidence.tar.gz), verify its hash using [SHA256SUMS](SHA256SUMS), then verify its files with [files.json](files.json). Install the recorded dependencies, deploy the pinned Python/Rust source, and use `rust/sweep.json` with the workspace `serve_sweep.py` matching SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`. Adapt task-local paths in the config and included external adapters while preserving arguments and environment. The runner itself is unchanged. The candidate `replica-0.process.json` and repeat `client-command.json` files also provide exact direct server/client commands.

Common launch: context 32768, memory fraction 0.80, max running requests/decode graph cap 64, prefill chunk 8192, prefill graphs disabled, FP32 LM head, glm45/glm47 parsers and default window layout. The omitted MoE flag resolves to `flashinfer_trtllm`; explicit comparison uses `deep_gemm`. BF16 KV uses FlashMLA sparse; FP8 KV uses TRTLLM DSA, so the latter comparison changes a deployment combination. MTP uses natural EAGLE steps/top-k/draft-tokens 3/1/4, with the checkpoint's own draft. Simulation is absent.

Set `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=rust`, `SGLANG_RUST_BUILD_MODE=auto`, a task-local `SGLANG_CACHE_DIR` and `CARGO_BUILD_JOBS=4`. Rust 1.92.0 built the native extension. All four scheduler ranks in every candidate logged `RustUnifiedTreeCore` and mapped the captured native hash `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. Idle checks and sampled process ownership accompany each launch.

## Workload and metrics

Use the [E03 frozen workload](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), whose decompressed SHA256 is `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Six concurrency levels 1/2/4/8/16/32, two seeds 1/2, max(16, 2×concurrency) conversations per repeat, four turns each, 128 output tokens, temperature 1, top_p 0.95, thinking off and ignore EOS. Each repeat flushes the cache and runs one warmup conversation.

Score is (sum of per-request input tokens + generated output tokens) / measured duration / four physical GPUs. It includes resent and cached input. Aggregate rate/latency values are medians of two repeats. SLO: P90 TTFT <=3 seconds, P90 interactivity >=30 tok/s, successful-request ratio 1 and empty-response ratio 0. Candidate selection maximizes passing aggregate throughput. Natural stopping is checked separately by three chat probes per candidate; this is not a full accuracy gate.

## Results

All 72 loads completed: 36 points and 7,680 successful, nonempty requests. All 18 chat probes returned nonempty content and normal stop. Each row below is the highest passing concurrency measured for that candidate.

| Candidate | Concurrency | Total tok/s/GPU | P90 TTFT (s) | P90 interactivity (tok/s) |
|---|---:|---:|---:|---:|
| tp4-auto | 32 | 5098.106 | 2.306 | 32.028 |
| tp4-auto-fp8 | 32 | 5261.126 | 2.150 | 32.489 |
| tp4-auto-fp8-mtp | 4 | 1410.121 | 0.775 | 42.457 |
| tp4-auto-mtp | 4 | 1480.146 | 0.758 | 44.313 |
| tp4-deepgemm | 16 | 3071.611 | 1.492 | 34.035 |
| tp4-deepgemm-mtp | 4 | 1368.451 | 0.690 | 35.264 |

The highest passing FP8-weight configuration in this finite grid is the default TRTLLM MoE runner with FP8 KV/TRTLLM DSA and MTP off, at C32. C32 is the highest tested level and still passes, so the upper capacity boundary is unmeasured. FP8-KV MTP at C8 has one passing and one failing repeat; its aggregate fails. No production deployment selection follows from this partial precision matrix. Matched FP8/NVFP4 coverage is a separate round on a common supporting revision.

## Audit and limits

[Independent audit](audit.json) recomputes every request/token total, throughput, raw P90 TTFT, MTP-off raw P90 ITL, median score and candidate selection. For MTP, the pinned client retokenizes each streamed chunk and normalizes its interval by that chunk's token count. The export omits chunk text, so those 36 MTP P90 values can only be reconciled to saved client aggregates. They cannot be independently reconstructed from the exported raw intervals. Future paired MTP rounds retain chunk-level evidence; raw SSE-chunk latency must not be substituted for token latency.

One launch per candidate and two fixed-order load seeds do not measure launch-to-launch reproducibility or confidence intervals. There is no full accuracy gate in this round. GPU sampling cannot rule out activity shorter than its interval. The environment is non-release, and the paired NVFP4 matrix remains required before closing performance validation.
