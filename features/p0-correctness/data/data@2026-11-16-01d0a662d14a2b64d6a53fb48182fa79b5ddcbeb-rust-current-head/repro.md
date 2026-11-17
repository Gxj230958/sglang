# E18 Rust correctness on the current integration

## Environment

- Hardware: four NVIDIA GB300 GPUs, TP4, one exclusively locked allocation. GPU snapshots show idle devices before each server and after teardown.
- Runtime: `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`, integrating the mixed-precision slot mapping on `8a6cdc9d7c71798e307f098f0d3998d4d0de3d00`.
- Image tag: `lmsysorg/sglang:latest`; digest not captured. This is non-release validation.
- FlashInfer Python/cubin `0.7.4`, JIT/provider `sm103a` `0.7.4+cu130`, PyTorch `2.14.1+cu130`, Rust/cargo `1.92.0`. Complete installed package metadata is in `python-packages.txt` inside the archive; resolved launch paths are in each `launch.json`.
- FP8 weights: private `RadixArk/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, with the evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`.
- NVFP4 performance checkpoint: private `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`.
- Immutable checkpoint inventory, FP8 config and acquisition details: [E04 private handoff](../../../p0-general-performance/data/data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md).

## Setup

Extract [evidence.tar.gz](evidence.tar.gz) into an empty directory. [files.json](files.json) gives the SHA256 for each extracted file. The top-level [SHA256SUMS](SHA256SUMS) verifies the archived evidence and round metadata.

Reconstruct the runtime from private `radixark/sglang-zai` base `8a6cdc9d7c71798e307f098f0d3998d4d0de3d00` plus `conversion/runtime.patch` from the NVFP4 checkpoint revision above. The patch SHA256 is `644d3afda7709206a1c4e5e10caf4f3ce1036a7e1bc0f8d141c2337b45dd2e1a`; the resulting Git tree is `16b1249e58da225cac7e94a2e0fff80bf533e63d`. [runtime-reconstruction.json](runtime-reconstruction.json) records an independent index-only reconstruction matching the tested integration tree. The integration commit is local; this source-tree recipe makes its contents reproducible before a runtime PR push.

Use the evaluated FP8 config from the handoff and verify the model/tokenizer files against its inventory. Preserve the launch dependency overlay order or provision an equivalent isolated environment from the recorded package versions. Install FlashInfer cubins from `https://flashinfer.ai/whl/` and the CUDA 13 JIT provider from `https://flashinfer.ai/whl/cu130/`. Build/load the pinned Rust extension on the GPU devbox with cargo/rustc 1.92.0 and `SGLANG_RUST_BUILD_MODE=auto`.

Exact server argv and behavior-changing environment are stored in `runs/<arm>/launch.json`. Launch those commands from the reconstructed source tree after adapting local model/source/overlay paths. Keep `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND` and all `SGLANG_SIMULATE_ACC_*` variables unset. Require positive `RustUnifiedTreeCore` initialization in all four TP ranks before any request.

Execute the exact `runs/<arm>/gsm8k-command.json` argv using `sgl-eval==0.1.3`. Use a bounded driver, check health, preserve outputs and stop the owned process group before the next arm. The server uses port 31960 and distributed initialization port 31961. All GPU work requires an exclusive allocation.

## Commit and validation

All 12,581 source archive entries matched the integration manifest. The imported mapping check covered 103 sparse execution slots and preserved the original quantization configuration. Both completed arms logged Rust in ranks 0–3. Each returned three nonempty, naturally stopped chat replies before GSM8K. The independent audit recomputed scores and finish-reason counts from every prediction, required unique IDs and checked their agreement with evaluator metrics.

## Workload

FP8 full evaluation: all 1,319 GSM8K test questions, `sgl-eval==0.1.3`, scorer dependency commit `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`, temperature 1, top_p 0.95, seed 1, output limit 32,768,64 threads. Natural EAGLE with steps/top-k/draft-tokens 3/1/4 uses the original FP8 draft with explicit `--speculative-draft-model-quantization fp8`; no acceptance simulation. Context 65,536, BF16 KV, FlashMLA sparse, TRTLLM MoE, separate shared experts, memory fraction 0.80, chunk 8192, running/decodegraph cap 64, FP32 LM head and disabled prefill graphs.

NVFP4 sanity: first 100 GSM8K questions, temperature 1, top_p 0.95, seed 1, output limit 8192,16 threads, MTP off and context 32,768. The remaining server settings match the FP8 recipe. These two rows have different sample sizes and MTP/output settings and do not measure quantization quality parity.

## Results

| Arm | Correct | Accuracy | Stop | Length | Errors |
|---|---:|---:|---:|---:|---:|
| FP8 full, natural MTP | 1256/1319 | 95.22% | 1316/1319 (99.77%) | 3 | 0 |
| NVFP4 sanity, MTP off | 95/100 | 95.00% | 99/100 (99.00%) | 1 | 0 |

FP8 requests `gsm8k-423`, `gsm8k-87` and `gsm8k-1176` reached the 32,768-token output limit and were incorrect. All 1,319 prediction IDs were unique. Evaluation elapsed 875.7 s; evaluator throughput is diagnostic and is not a serving-performance comparison.

This establishes full FP8 and limited NVFP4 correctness evidence on the selected integration. Historical Python-core results used other code, hardware or evaluation settings; this round does not attribute a quality change to the tree core. NVFP4 full natural-MTP evaluation is a separate pending run. The performance-only checkpoint has no quality-parity or multimodal release claim. B300/H200 Rust gates, feature combinations, the locked release environment and matched future performance sweeps remain open.

## Data and figures

- [evidence.tar.gz](evidence.tar.gz): unchanged evaluator metrics and predictions, chat replies, server logs, exact launches, resolved settings, GPU snapshots and source/package validation records.
- [audit.json](audit.json): independent prediction accounting, per-rank Rust checks and source/mapping evidence.
- [evidence-selection.json](evidence-selection.json): capture hash and selected files. Operational driver copies are excluded; raw measurement bytes are preserved.
- [runtime-reconstruction.json](runtime-reconstruction.json): source-tree identity proof from the immutable published patch and current private base.
