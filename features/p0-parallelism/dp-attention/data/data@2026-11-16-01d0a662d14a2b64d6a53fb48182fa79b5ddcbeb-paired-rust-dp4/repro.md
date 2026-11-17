# E03 Paired Rust attention DP4 validation

## Environment

Four GB300 GPUs on one exclusively held devbox rank. Live per-launch package versions and import paths are retained in each archive's server-imports.json. Matched versions: `{"flashinfer-cubin": "0.7.4", "flashinfer-jit-cache": "0.7.4+cu130", "flashinfer-jit-cache-sm103a": "0.7.4+cu130", "flashinfer-python": "0.7.4", "kernels": "0.14.1", "sgl-deep-gemm": "0.2.8", "sgl-flash-mla": "1.0.5", "sglang-kernel": "0.4.11", "torch": "2.14.1+cu130", "transformers": "5.19.0"}`. Container digest, power mode and complete topology were not captured for this round.

FP8 provider revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. Performance-only NVFP4 revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 draft with explicit FP8 draft quantization.

## Commit

Exact runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`; source manifests match before and after execution. All four DP/TP/EP worker tuples map Rust extension SHA256 `d2547a9f9a3edc3f79318922dfd2aceb162c0339c9c00d69514e00aafb979cc3` in each launch.

## Setup and scripts

Verify SHA256SUMS, extract each archive into its own directory and verify every member against its files.json. The terminal archive retains eleven hashed round inputs, launch receipts, the source manifest and verification tools, final result and owned-process cleanup. Provision the exact runtime, checkpoint revisions, evaluated FP8 config and recorded dependency versions on an exclusively held four-GPU devbox. Adapt absolute source/model/evaluator/output paths in plan.json and start.sh; preserve the workload, seeds and budgets. Run bounded start.sh after its predecessor/source/idle checks; run.py executes FP8 and NVFP4 sequentially. These are round-specific reproduction inputs.

Common server settings: TP4, EP4, attention DP4, all-to-all `none`, TRTLLM MoE and DSA, FP8 E4M3 KV, window layout, context 131072, memory fraction 0.80, global running/decode graph cap 64, requested chunk 8192, FP32 LM head, separate shared experts, prefill graphs disabled, natural EAGLE 3/1/4 and server seed 1. Actual chunk resolves to 2048 and per-DP running cap to 16. Both target formats retain the same FP8 draft. Full commands and resolved fields are archived.

## Workload

Three natural startup stopping requests precede 18 deterministic random-record retrieval probes spanning approximately 2K–121K prompt tokens, with max 96 output tokens. Sixteen directed prefix requests cover each DP rank's cold/warm/fork/warm-fork sequence. They use identical prompts across ranks, routed_dp_rank, temperature 0, seed 1 and max 512. Per-request raw server-log windows identify the actual DP rank that prefills each request. Cache flushes separate probe stages and full evaluation.

Each format runs full 1319 GSM8K through sgl-eval: temperature 1.0, top_p 0.95, seed 1, 64 threads and max 32768 output tokens. Complete IDs, answers, finish reasons, generated-token counts, metrics and evaluator commands are retained. Natural generation/verify ratios describe correctness traffic, not a throughput benchmark.

## Results

| Weights | Correct | Stop | Length | Errors | Generation / verify ratio |
|---|---:|---:|---:|---:|---:|---:|
| FP8 | 1249/1319 (94.6929%) | 1308/1319 (99.1660%) | 11 | 0 | 2.674439 |
| NVFP4 | 1251/1319 (94.8446%) | 1313/1319 (99.5451%) | 6 | 0 | 2.653511 |

Both formats pass all 18 retrieval probes and all 16 directed routing/cache checks, plus three startup stops. Every rank reports cold 0 / warm 6656 / fork 1984 / warm-fork 6656 cached tokens, exact expected answers and natural stops. Actual prefill logs route each directed request to its requested DP rank. The same cold prompt across ranks establishes isolation for this probe sequence.

NVFP4 minus FP8 correct/stop counts: +2/+5. These are single paired observations, not evidence that quantization causes a quality difference. Length truncations remain recorded separately from correctness; full stopping nonregression and release qualification remain unmet.

Length IDs:

- FP8: gsm8k-255, gsm8k-654 (correct), gsm8k-1303, gsm8k-380, gsm8k-189, gsm8k-505, gsm8k-552, gsm8k-690, gsm8k-1016, gsm8k-835, gsm8k-926.
- NVFP4: gsm8k-161, gsm8k-423, gsm8k-835, gsm8k-796, gsm8k-1035, gsm8k-1254.

## Data and audit

Two complete arm archives retain all raw startup/probe/evaluation/runtime outputs; terminal evidence retains the source/input/cleanup lifecycle. Per-arm audits independently recount all 1319 unique IDs and finish reasons, sum token accounting, compare generation/verify counters, verify all four Rust mappings, and check every directed request/response plus its actual DP-prefill log. The 65 files in each early probe snapshot match the complete snapshot byte for byte. Paired audit checks actual commands, recorded environment, imported versions, generation settings and probe requests.

Launch environment receipts are whitelists, and server-imports.json does not capture the full simulation environment. The archived pinned run.py/server.py explicitly remove inherited simulation variables; this is the retained environment evidence. FP8 has 946 owned GPU samples with zero query errors; NVFP4 has 908 with one process-query error after generation during shutdown, retained in its audit. GPU samples establish ownership at sampled times; they do not observe activity between samples. Terminal audit requires driver exit 0, all owned processes gone, empty GPU process lists, four GPUs at 0 MiB and final source parity.

This round covers standard all-to-all `none` attention DP4 with natural MTP and FP8 KV. DeepEP, CP/DP composition, HiCache/DP, disaggregated prefill and performance scaling require separate measured evidence.
