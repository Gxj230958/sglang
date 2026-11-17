# E04 Paired Rust HiCache host and file validation

## Environment and commit

Four NVIDIA GB300 GPUs on one exclusively held devbox rank, exact clean runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`. All 12,581 source-manifest files match before and after the round. Actual mappings on all four workers use Rust extension SHA256 `d2547a9f9a3edc3f79318922dfd2aceb162c0339c9c00d69514e00aafb979cc3` in each launch. Container digest, power mode and topology were not captured for this round.

Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT and sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.3. Per-launch server-imports.json records the actual distributions and import paths. FP8 and NVFP4 use identical environments and server/request seeds.

FP8 provider revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` uses evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. Preserve that configuration. Performance-only `RadixArk/GLM-5-1028-Provider-NVFP4-perf` is pinned to `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both formats use the original FP8 draft with explicit FP8 draft quantization.

## Setup and scripts

Verify SHA256SUMS and extract each archive into a separate directory; its files.json binds every raw member. The terminal archive preserves the round's ten hashed inputs, launch and terminal receipts, source verification, and source-manifest/verification dependencies. Provision the pinned runtime, checkpoints and recorded dependency versions on an exclusively held devbox. Adapt the absolute source, model, evaluator and output paths in plan.json and start.sh. Retain the evaluated FP8 config and full input/source verification. Run the bounded start.sh after the recorded predecessor/idle checks; run.py drives the six sequential launches. These are round-specific reproduction inputs.

Common settings: TP4, BF16 KV, FlashMLA sparse DSA, TRTLLM MoE, window KV layout, separate shared experts, context 65536, memory fraction 0.80, running/decode graph cap 64, chunk 8192, FP32 LM head, prefill graphs disabled, natural EAGLE 3/1/4, server seed 1. HiCache uses device cap 262144 tokens, host size 64 GiB, file storage and write-through. Each weight format has distinct positive and negative storage directories. Full commands, resolved settings and original responses are preserved.

## Workload

Each format first requests a cold anchor and its device-cached repeat. Seventy unique filler prompts exceed the resolved device token capacity; a repeated anchor must then report host-only restoration. Six prefix/fork probes and a full GSM8K evaluation follow. A full process restart reuses the positive file store, and its anchor must report storage restoration before a second full GSM8K evaluation. A third launch uses a fresh negative store and must recompute the anchor with zero cache hits.

All anchors require the exact five generated codes and a natural stop, temperature 0 and max 512 output tokens. Cache-source claims are checked against raw response fields; a zero-hit response may omit tier details. Host fills total 467835 FP8 and 467815 NVFP4 prompt tokens, both above the 262144-token device pool. Both formats pass all six prefix probes.

Each of four GSM8K runs covers 1319 unique examples: temperature 1.0, top_p 0.95, seed 1, 64 threads and max 32768 output tokens. Actual evaluator commands, all predictions and metrics are archived. Natural generation/verify counter ratios describe these correctness runs, not a performance benchmark.

## Results

| Weights | Phase | Correct | Stop | Length | Errors | Generation / verify ratio |
|---|---|---:|---:|---:|---:|---:|
| FP8 | host | 1251/1319 (94.8446%) | 1315/1319 (99.6967%) | 4 | 0 | 2.662807 |
| FP8 | storage | 1256/1319 (95.2237%) | 1311/1319 (99.3935%) | 8 | 0 | 2.640917 |
| NVFP4 | host | 1242/1319 (94.1622%) | 1314/1319 (99.6209%) | 5 | 0 | 2.653997 |
| NVFP4 | storage | 1252/1319 (94.9204%) | 1317/1319 (99.8484%) | 2 | 0 | 2.648013 |

Both formats report cold 0, device 6656, host 6656 and storage 6656 cached tokens. Host restoration reports device=0/storage=0; file restoration reports device=0/host=0 and storage_backend=HiCacheFile. All anchor answers and natural stops pass, including fresh-store zero-hit negative controls. File-store inventory and cache-tier evidence are archived separately from quality results.

NVFP4 minus FP8 correct/stop counts are -9/-1 for host and -4/+6 for storage. These are single paired observations; neither phase comparison nor format comparison establishes causality. All four full evaluations retain length truncations, so stopping nonregression and release qualification remain unmet.

Length IDs: FP8 host 267, 1042, 675, 1176; FP8 storage 135, 255, 87, 423, 924, 505, 796, 1074; NVFP4 host 552, 924, 858, 1074, 1176; NVFP4 storage 182, 1303. Every length row generated 32768 tokens and was incorrect. No completed row was discarded.

## Data and audit

Six phase archives and their manifests preserve complete raw request/response, runtime, cache-tier and evaluation evidence. The four full-evaluation audits independently recount IDs, correct answers, stop/length counts, token sums and generation/verify counters. paired-full-gsm8k-audit.json checks matching normalized commands, imports, environments, sampling and probe requests across formats. Two negative audits verify exact answers, zero hits, distinct store paths and actual Rust mappings. Terminal evidence records zero remaining owned processes, four GPUs at 0 MiB and final source parity.

GPU ownership samples for FP8 host/storage are 522/557 and NVFP4 host/storage 531/496; all observed processes are owned. FP8 host has one process-query error after generation during shutdown, retained in its audit. Sampling cannot exclude activity between samples.

Two earlier failed attempts remain archived. The initial zero-hit probe incorrectly required a tier-details object; its 128-token anchor also ended in reasoning at the output limit. The second attempt proved host restoration but produced 1319 HTTP400 errors because context 32768 could not accommodate the requested 32768 output tokens plus prompt. Those evaluations are invalid. This round uses context 65536, 512-token anchors, fresh stores and complete/zero-error evaluator checks before advancing.

This evidence covers standalone host/file caching with natural MTP and BF16 KV. Prefill-CP, attention-DP, disaggregated-prefill and alternative storage/backend combinations require their own measured rounds.
