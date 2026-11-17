# E04 Paired TP4 and DEP4 serving performance

## Environment

Four NVIDIA GB300 GPUs, FP8 E4M3 KV, TRTLLM DSA attention and FlashInfer TRTLLM MoE. Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT providers 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. Every cell preserves actual package imports and environment; container digest was not captured. postrun-hardware.json records separately timestamped GPU identity, driver, memory, power limits and topology; it does not establish clocks or power during load.

FP8 checkpoint revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. NVFP4 checkpoint `RadixArk/GLM-5-1028-Provider-NVFP4-perf` revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Speculative configurations retain the original FP8 draft with explicit FP8 draft quantization. Acquisition and tokenizer pins are in the [immutable model handoff](../../../../p0-general-performance/data/data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md).

## Commit

Exact runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`. All 12581 source files and 20 frozen inputs verify before/after execution. All four workers in each cell map Rust extension SHA256 `d2547a9f9a3edc3f79318922dfd2aceb162c0339c9c00d69514e00aafb979cc3`. [Correctness E18](../../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/repro.md) supplies source reconstruction and TP4 quality evidence; [DP Attention E03](../data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-dp4/repro.md) supplies current DEP4 quality and routing evidence. Runtime integration remains local pending stopping qualification.

## Setup and scripts

Verify SHA256SUMS and each archive's member manifest, then extract archives into separate directories. terminal-evidence.tar.gz contains round-specific adapters, configurations, phase reports, source-verification dependencies and terminal receipts. Every candidate archive retains actual argv/environment, worker mappings, resolved settings, raw client measurements and GPU observations. The workspace runner SHA256 is `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`.

Obtain the [frozen four-turn workload](../../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompress as workload.json and verify SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. Provision the pinned runtime, checkpoints and package versions on an exclusive four-GPU devbox. Adapt absolute source, overlay, model and output paths; preserve evaluated FP8 metadata, environment order and checks. From the extracted terminal directory, run under a six-hour outer timeout with TERM then KILL after 90 seconds:

```bash
python3 execute.py run --config natural-gate.json --run-dir gate
python3 execute.py run --config mtp-off.json --run-dir off
python3 execute.py run --config controlled35.json --run-dir controlled
```

Require all four natural gate cells to pass before advancing. Each full phase must complete four candidates and six concurrency points; SLO failures remain measured results. Original start.sh additionally performs predecessor, idle, source and cleanup checks; adapt historical predecessor paths when reproducing.

Common settings: context 32768, memory fraction 0.80, total running/decode-graph cap 64, requested prefill chunk 8192, FP32 LM head, separate shared experts, eager prefill, glm45/glm47 parsers and server seed 1. TP4 means TP4/EP1/attention-DP1. DEP4 means TP4/EP4/attention-DP4, all-to-all none, resolved chunk 2048 and per-DP running cap 16. This comparison changes attention DP, EP, scheduler subdivision and KV capacity together. It does not isolate an EP or TP effect. Natural/controlled EAGLE uses steps/topk/draft-tokens 3/1/4; only controlled sets SGLANG_SIMULATE_ACC_LEN=3.5, SGLANG_SIMULATE_ACC_METHOD=match-expected and SGLANG_SIMULATE_ACC_TOKEN_MODE=real-draft-token.

## Workload and metrics

Twelve starts: four C1 natural sanity cells, four MTP-off cells and four simulated-acceptance cells. Full grids use C1/2/4/8/16/32, two repeats with request seeds 1/2, max(16, 2*C) conversations and four turns each. Initial input is about 2.4K tokens; subsequent turns resend generated assistant histories. Each turn requests 128 tokens, temperature 1, top_p 0.95, thinking disabled and ignore EOS. Flush cache and issue one warmup request before each measured load. Gate/off starts have three separate stopping probes each; controlled starts have no quality probes.

Score is actual input plus output tokens divided by measured duration and four GPUs, including cached/resent input. Tables use medians of two repetitions. SLO requires P90 TTFT <= 3 seconds, P90 interactivity >= 30 tokens/s and all requests successful/nonempty. Off interactivity uses raw client ITL; MTP distributes each stream interval over its runtime-tokenizer chunk count before token-weighted P90. This is not a physical per-token timestamp distribution. Raw chunks, counts, requests and benchmark outputs are preserved. Reported acceptance and generation/verify ratios have different accounting; counters include warmup while throughput excludes warmup. Simulated 3.5 is an expected length, and DP scheduling can change each repeat's realized acceptance.

## Results

All 100 loads complete: 256 successful requests in four natural gate loads, 5120 in 48 off loads and 5120 in 48 controlled loads. Every measured response is nonempty with 128 output tokens. All 24 separate startup stopping probes pass. Natural C1 gates are sanity evidence, not a natural-performance grid or full quality gate.

Best passing points per deployment:

| Mode | Layout | Weights | C | Total tok/s/GPU | P90 TTFT seconds | Interactivity tok/s |
|---|---|---|---:|---:|---:|---:|
| off | TP4 | FP8 | 32 | 5203.687 | 2.212 | 32.752 |
| off | TP4 | NVFP4 | 32 | 6070.241 | 2.194 | 42.346 |
| off | DEP4 | FP8 | 16 | 2640.529 | 2.464 | 33.247 |
| off | DEP4 | NVFP4 | 16 | 3036.490 | 2.242 | 40.528 |
| controlled | TP4 | FP8 | 32 | 7917.422 | 2.303 | 66.483 |
| controlled | TP4 | NVFP4 | 32 | 8022.076 | 2.441 | 86.391 |
| controlled | DEP4 | FP8 | 16 | 4178.537 | 2.740 | 63.790 |
| controlled | DEP4 | NVFP4 | 16 | 4374.043 | 2.602 | 79.247 |

SLO failures, retained in all raw reports:

| Mode | Layout | Weights | C | P90 TTFT seconds | Interactivity tok/s |
|---|---|---|---:|---:|---:|
| off | DEP4 | FP8 | 32 | 4.087 | 25.473 |
| off | DEP4 | NVFP4 | 32 | 4.324 | 32.243 |
| controlled | DEP4 | FP8 | 32 | 4.884 | 60.366 |
| controlled | DEP4 | NVFP4 | 32 | 4.942 | 77.715 |

With MTP off, NVFP4 gains 16.65% at TP4 C32 and 15.00% at DEP4 C16. Controlled DEP4 C16 has an observed NVFP4 delta of +4.68%. Controlled TP4 C32 differs by +1.32%, a near tie; NVFP4 repeat scores are 8800.771 and 7243.381 total tok/s/GPU. This dispersion is retained and exceeds the paired median difference. Two client repetitions and one server startup per cell provide descriptive observations, not significance or isolated quantization causality. Identical user fixtures and protocol yield different generated histories; equal memory fraction yields different KV capacities. Natural gates and simulated throughput are reported separately.

Current DEP4 E03 has FP8 1249 correct/1308 stop and NVFP4 1251 correct/1313 stop out of 1319, with zero errors. TP4 E18 has FP8 1256 correct/1316 stop and NVFP4 1243 correct/1313 stop. Full stopping nonregression remains unmet. This performance round does not qualify release, DeepEP or CP/DP composition.

## Data and audit

Thirteen archives preserve 1468 raw files: 1428 candidate files and 40 terminal files. archive-index.json pins archive and original terminal digests; the terminal publication omits only the separately referenced workload. Candidate archives and all retained terminal members are byte-identical to collected snapshots. Per-cell audits reconstruct counts, TTFT, interactivity, throughput, mappings and resolved scheduler settings. Paired/matrix audits compare actual server/client argv, imported versions, environments and workload lengths while preserving the original FP8 draft.

All observed GPU processes belong to the candidate. One FP8 TP4 off GPU query error occurred after the benchmark and summary writes with no active load, adjacent to the shutdown log's timestamp second; ordering within that second relative to SIGTERM is unproven. That sample remains recorded. All other cells have zero query errors. Sampling does not exclude activity between observations. The driver exits 0 and its PID is absent; cleanup is empty, final GPU process output is empty and all four GPUs report 0 MiB. Fresh postrun process observation also verifies idle. Final source and frozen-input checks pass. No load, failure or request was discarded.
