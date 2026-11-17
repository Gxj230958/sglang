# E07 Paired FP8/NVFP4 natural MTP

## Environment

Four GB300 GPUs, TP4. All four servers imported Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT providers 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. Exact package/module paths are in each candidate's `server-imports.json`. Container digest, interconnect topology and power mode were not captured; this is non-release evidence.

FP8 source revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. NVFP4 checkpoint `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Use the model/tokenizer inventories and acquisition instructions in the [private artifact handoff](../data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md). This round reused verified local checkpoints; it did not repeat every weight-shard hash.

## Commit

Runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`, with all 12,581 source-manifest files verified before and after execution. Reconstruct the local integration from the [Correctness E18 source recipe](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/repro.md). The code remains local while its stopping gate is unmet.

## Setup and scripts

Verify `SHA256SUMS`, extract `evidence.tar.gz`, then compare every extracted file with `files.json`. Reconstruct the source/packages/checkpoints above and adapt model, source and overlay paths in `kv-mtp-natural.json` and the included adapters. Preserve the recorded overlay order and environment. The external `serve_sweep.py` must match SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`. Run `python3 execute.py run --config kv-mtp-natural.json --run-dir run1` on an exclusively held four-GPU allocation. Each `replica-0.process.json` and `client-command.json` preserves exact argv/environment.

Common server settings: TP4, TRTLLM MoE, separate shared experts, context 32768, memory fraction 0.80, running/decode graph cap 64, chunk 8192, FP32 LM head, disabled prefill graphs, glm45/glm47 parsers, default window KV layout. BF16 KV uses FlashMLA sparse; FP8 E4M3 KV uses TRTLLM DSA. Natural EAGLE uses 3 steps/topk 1/4 draft tokens and the original FP8 draft with explicit FP8 draft quantization in every arm. Set `SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1`, `PYTHONNOUSERSITE=1`, `SGLANG_RUST_BUILD_MODE=auto`, `CARGO_BUILD_JOBS=4`; unset explicit tree-core selection and simulation variables.

All four ranks in each server mapped the Rust extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. `capture_client.py` preserves the client's metric implementation while exporting raw chunks, intervals and runtime-tokenizer chunk counts after measurement. `load_adapter.py` independently reconstructs normalized P90 interactivity. These are round-specific measurement adapters preserved in the archive.

## Workload

Use the [frozen four-turn chat workload](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompressed SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Inputs start around 2.4K tokens, with complete generated history resent on later turns. Per repeat: concurrency 1/2/4/8/16/32, max(16,2×concurrency) conversations, four turns, 128 output tokens/turn, temperature 1, top_p 0.95, thinking off, ignore EOS. Request seeds 1/2; cache flush and one warmup conversation precede each measured load. Each candidate also has three separate natural-stop chat sanity probes. Load timeout 1200 seconds; startup 1800 seconds; outer driver 6 hours.

Score=(actual input+output tokens)/measured duration/4 GPUs. It counts resent/cached inputs; generated history can change input totals. Report medians of two repeats. SLO: P90 TTFT<=3 seconds, P90 interactivity>=30 tok/s, all requests successful and nonempty. Interactivity is the reciprocal of token-weighted P90 ITL: distribute each recorded interval over its associated runtime-tokenizer chunk count. `stream-chunks.json` and `bench.jsonl` allow reconstruction; this is not a distribution of physical per-token timestamps. Natural acceptance is the client's per-load estimate. Server seeds were auto-selected and differ across arms, as listed below; request seeds are matched.

## Results

All 48 loads completed, with 5,120 successful nonempty 128-token requests and 12 naturally stopped sanity replies. All four arms pass C1/2/4; C8/16/32 fail the interactivity threshold. The best passing point for each is C4.

| Candidate | C | Score tok/s/GPU | P90 TTFT s | P90 interactivity tok/s | Natural acceptance | Server seed |
|---|---:|---:|---:|---:|---:|---:|
| fp8-kv-bf16-mtp-natural | 4 | 1477.357 | 0.727 | 43.641 | 2.5155 | 136602530 |
| nvfp4-kv-bf16-mtp-natural | 4 | 1533.185 | 0.749 | 52.890 | 2.4308 | 459115525 |
| fp8-kv-fp8_e4m3-mtp-natural | 4 | 1351.859 | 0.771 | 40.833 | 2.4633 | 1013935116 |
| nvfp4-kv-fp8_e4m3-mtp-natural | 4 | 1456.682 | 0.790 | 49.185 | 2.4677 | 70322572 |

At C4, NVFP4 scores 3.78% above FP8 with BF16/FlashMLA and 7.75% above FP8 with FP8 KV/TRTLLM DSA. Within NVFP4, the FP8 KV deployment scores 4.99% below BF16 KV. These KV comparisons also change attention backend. Two repeats and different server seeds support descriptive results, not causal attribution or statistical significance. Fixed-seed controlled acceptance 3.5 and MTP-off measurements are a separate round.

[Correctness E18](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/nvfp4-full/repro.md) remains the quality boundary: FP8 has 1256 correct/1316 stop and NVFP4 has 1243 correct/1313 stop out of 1319. Stopping nonregression is unmet. Fixed-length throughput and three startup probes do not establish full quality parity.

## Data and figures

[evidence.tar.gz](evidence.tar.gz) preserves 633 files including complete raw load results, stream timing, resolved flags, imports, Rust mappings, GPU samples and terminal cleanup. [files.json](files.json) gives per-file SHA256; [audit.json](audit.json) consolidates independent checks. The four `*-audit.json` files retain every concurrency point and pair comparison. No load or request was excluded. All sampled GPU processes resolved to the owning server; sampling cannot exclude activity between samples. Terminal source checks passed, cleanup had zero remaining owned processes, and all four GPUs reported 0 MiB before the next experiment.
