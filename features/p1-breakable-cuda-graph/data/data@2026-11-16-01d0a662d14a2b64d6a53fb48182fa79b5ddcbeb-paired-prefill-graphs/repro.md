# E02 Paired FP8/NVFP4 prefill graphs

## Environment

Four NVIDIA GB300 GPUs, TP4, BF16 KV, FlashMLA sparse attention and FlashInfer TRTLLM MoE. Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT providers 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. Each cell preserves actual package imports and environment. Container digest was not captured. The postrun hardware observation records driver 580.178.04, 284208 MiB per GPU, persistence enabled, 1400 W power limits and NV18 GPU links. It does not measure clocks or power during load.

FP8 checkpoint revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. NVFP4 checkpoint `RadixArk/GLM-5-1028-Provider-NVFP4-perf` revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both speculative formats use the original FP8 draft with explicit FP8 draft quantization. Checkpoint acquisition and tokenizer pins are in the [immutable model handoff](../../../p0-general-performance/data/data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md).

## Commit

Exact runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`. All 12581 source-manifest files match before and after the suite. All four workers in every cell map Rust extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. [Correctness E18](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/repro.md) supplies reconstruction and full-quality evidence; this runtime remains local pending its stopping gate.

## Setup and scripts

Verify SHA256SUMS and the member manifests before extracting each archive to a separate directory. The terminal archive contains the frozen round-specific adapters, three configurations, phase reports, source manifest and source-verification helpers. Each candidate archive contains actual server argv/environment, imported packages, worker mappings, client commands and raw outputs. The input manifest pins all 18 original files; the publication archive references the workload separately.

Obtain the [frozen four-turn workload](../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompress as workload.json and verify SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Provision the pinned source, checkpoints and dependency versions on an exclusive four-GPU devbox. Preserve the evaluated FP8 configuration and recorded environment order; adapt absolute source, overlay, model and output paths in the adapters/configurations to that devbox. The workspace runner is archived at SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`.

From the terminal directory, execute these phases in order under a six-hour outer timeout, TERM then KILL after 90 seconds:

```bash
python3 execute.py run --config mtp-off.json --run-dir off
python3 execute.py run --config natural.json --run-dir natural
python3 execute.py run --config controlled35.json --run-dir controlled
```

Require four complete candidates and six points per candidate before advancing. The original start.sh includes idle/source checks, predecessor checks and owned-process cleanup; adapt its historical predecessor paths when reproducing. Common settings are TP4/EP1/attention-DP1, separate shared experts, FP32 LM head, context 32768, memory fraction 0.80, running/decode graph cap 64, chunk 8192, glm45/glm47 parsers and server seed 1. Eager prefill sets disable-prefill-cuda-graph; breakable sets cuda-graph-backend-prefill=breakable. Ordinary decode graphs remain enabled in both. Natural and controlled EAGLE use steps/topk/draft-tokens 3/1/4. Only controlled sets SGLANG_SIMULATE_ACC_LEN=3.5, SGLANG_SIMULATE_ACC_METHOD=match-expected and SGLANG_SIMULATE_ACC_TOKEN_MODE=real-draft-token.

## Workload and metrics

Twelve server starts cross FP8/NVFP4, eager/breakable prefill and MTP-off/natural/controlled modes. Each cell runs C1/2/4/8/16/32 with two repeats, request seeds 1/2, max(16, 2*C) conversations and four turns per conversation. Initial input is about 2.4K tokens; later turns resend generated assistant history. Each turn requests 128 tokens, temperature 1, top_p 0.95, thinking disabled and ignore EOS. Flush cache and issue one warmup request before each measured load. Off and natural cells each have three separate startup stopping probes. Controlled cells have no quality probes.

Score = actual input plus output tokens / measured client duration / four GPUs, including resent/cached input. Tables use two-repeat medians. SLO: P90 TTFT <= 3 seconds, P90 interactivity >= 30 tokens/s, every request successful and nonempty. Off interactivity uses raw client ITL. MTP interactivity distributes each stream interval over its runtime-tokenizer chunk count before token-weighted P90; it is not a physical token timestamp measurement. Raw stream chunks, token counts, requests and benchmark outputs support reconstruction.

Graph evidence matches saved log byte windows to full server logs and verifies resolved backend plus actual prefill replay lines for every load. These windows include warmup; throughput excludes warmup. Natural and controlled acceptance remain separate. At controlled C32, all four cells report 3.55/3.45 acceptance by repeat, with generation/verify deltas 32896/9252 and 32896/9572 including warmup. Reported acceptance and counter ratios have different accounting.

## Results

All 144 loads complete with 15360 successful, nonempty, 128-token responses and 24 separate normal startup stops. All 24 aggregate points pass in each of the off and controlled phases; their capacity boundaries remain unmeasured beyond C32. Natural eager passes through C4 and fails interactivity at C8/16/32 in both formats. Natural breakable passes through C8 and fails interactivity at C16/32 in both formats. All failed SLO points remain in the reports.

Best passing points within each graph/mode pair:

| Mode | Prefill | C | FP8 total tok/s/GPU | NVFP4 total tok/s/GPU | NVFP4 gain | P90 TTFT seconds FP8 / NV | Interactivity tok/s FP8 / NV |
|---|---|---:|---:|---:|---:|---:|---:|
| off | eager | 32 | 5119.119 | 6201.851 | +21.15% | 2.308 / 2.047 | 32.174 / 41.597 |
| off | breakable | 32 | 5224.383 | 6463.188 | +23.71% | 2.286 / 1.965 | 32.004 / 41.582 |
| natural | eager | 4 | 1463.719 | 1596.726 | +9.09% | 0.738 / 0.748 | 43.700 / 52.860 |
| natural | breakable | 8 | 2926.247 | 3687.106 | +26.00% | 1.119 / 0.937 | 32.813 / 39.619 |
| controlled | eager | 32 | 7681.429 | 9080.522 | +18.21% | 2.567 / 2.174 | 65.227 / 85.655 |
| controlled | breakable | 32 | 7946.814 | 9681.792 | +21.83% | 2.436 / 2.072 | 65.313 / 85.522 |

With MTP off at C32, breakable/eager throughput increases 2.06% for FP8 and 4.21% for NVFP4. Under natural MTP at C8, increases are 56.69% and 89.12%; eager C8 fails SLO. These are descriptive observations from one server startup per cell and two client repetitions. The common user fixture and protocol produce different generated histories, and equal memory fraction gives model-dependent KV capacity. The comparison does not isolate a kernel or quantization-only causal effect.

The full-quality E18 evaluations have FP8 1256 correct/1316 stop and NVFP4 1243 correct/1313 stop out of 1319. Stopping nonregression remains unmet. Fixed-length performance, startup probes and simulated acceptance do not establish release qualification, replay-equivalent outputs, a 2048-token capture cap or H200 graph performance.

## Data and audit

Thirteen archives preserve 2264 candidate raw files and 41 terminal files. archive-index.json pins archive digests; per-archive manifests verify every retained raw member. The terminal archive omits only the separately referenced workload, with original archive and omitted-member digests retained. All candidate archives are byte-identical to their collected snapshots. Per-cell audits independently reconstruct timing, counts, Rust mappings and graph windows; matrix audits compare actual commands, environments, imported versions and workload lengths. Target normalization preserves the original FP8 draft.

All GPU ownership samples have zero query errors and zero foreign processes. Sampling does not rule out activity between samples. The driver exits 0, its PID is absent, cleanup has no remaining owned processes, final GPU process output is empty and all four GPUs report 0 MiB. Final source and frozen-input verification pass. postrun-hardware.json supplies separately timestamped hardware metadata. No completed load or request was discarded.
