# E28 fallback candidate long-context retrieval diagnosis

## Environment

Four NVIDIA GB300 GPUs, 284208 MiB each, driver 580.178.04, 1400 W power limits and NV18 links. hardware-reference.json records the allocation topology; each run records its GPU UUIDs. Container digest was not captured. Image-level qualification remains separate.

FP8 checkpoint `zai-org/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its original FP8 NextN draft and tokenizer. Configuration records pin model metadata hashes and all eleven dependency versions: Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache/sm103a 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.2.

## Setup

Verify SHA256SUMS, extract each evidence.tar.gz into a separate directory and check its 99 selected raw members against files.json. export-provenance.json identifies both the complete original archive and the published subset. Published members preserve their original bytes. configuration.json is a derived execution plan; allocate an exclusive machine and adapt paths, ports, owner, predecessor checks and cache directories before using it as plan.json. Recompute the execution-input manifest for that new reproduction.

Obtain the pinned source and authorized checkpoint, install the recorded CUDA 13 dependencies, and materialize the source/overlay/model paths. The archived start.sh and runner.sh contain the complete launch environment and commands. Use fresh output directories and preserve cleanup.py and verify_source.py on success or failure. The original launch is bounded to 90 minutes:

```bash
timeout --signal=TERM --kill-after=90s 90m bash start.sh
```

Default Rust TreeCore, natural EAGLE steps/topk/draft tokens 3/1/4, FP8 draft, BF16 KV, FlashMLA Sparse prefill/decode, TRTLLM MoE, FP32 lm_head, separate shared experts and breakable prefill graphs. TP4/EP1/DP1, context 131072, memory 0.80, chunk 8192, maximum running requests 64 and server seed 1. CP4 additionally enables interleaved prefill CP with attention CP size 4. Actual arguments are in results/cp4/argv.txt or results/tp4/argv.txt.

Environment includes SGLANG_RUST_BUILD_MODE=auto, SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0, SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1, explicit source/overlay PYTHONPATH, SPT_NOENV=1, CARGO_BUILD_JOBS=4, offline checkpoints and NCCL/Gloo cilium_host. Simulation variables are absent. start.sh records the complete environment.

## Commit

Clean runtime `52ef77912fd004f34cfe340b392018632ce69c2c`. All 12586 tracked source files match before and after each run. Runner-side process-map capture records four Rust workers per run with extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`.

## Scripts

Each archive preserves diagnostic.py, runtime checks, launch commands, 22 raw request/response pairs, logs and cleanup records. The same diagnostic request sequence is used throughout. cp4-tp4-pair.json verifies that the original arms differ only in CP settings. tp4-budget-pair.json verifies identical actual TP4 service arguments and all 22 request bodies except max_tokens.

## Workload

The original post-GSM8K CP4 run returned adjacent-record code 968752 instead of 709295 for a warm 120936-token query for Record 4230. This round starts a fresh server, flushes, and repeats the 18 original requests, then the failed request alone after another flush, then the original preceding/failed/following three-query sequence after a third flush. Cache counters distinguish cold and warm requests. The original full-GSM8K history is absent.

Temperature 0, one request at a time, max_tokens 96 for the CP4/TP4 pair and 2048 for the TP4 follow-up. Requests retain enable_thinking=False; the checkpoint template still prefills reasoning. The original two TP4 truncations contain the correct codes in reasoning but no final content. No full accuracy evaluation or performance sweep is part of this round.

## Results

| Measurement | CP4, cap 96 | TP4, cap 96 | TP4, cap 2048 |
|---|---:|---:|---:|
| Exact answer and normal stop /22 | 22 | 20 | 22 |
| Expected cache state /22 | 22 | 22 | 22 |
| Length-limited responses | 0 | 2 | 0 |
| Failed diagnostic HTTP attempts | 0 | 0 | 0 |
| GPU samples | 267 | 255 | 260 |
| Owned GPU process records | 1068 | 1026 | 1044 |
| Independently collected live startup receipt | Yes | Yes | Unavailable |

The two TP4 cap 96 failures are Record 4612 at target 60000 and Record 8458 in the final long sequence. Both consumed 96 reasoning tokens. With cap 2048, the same requests return expected 512401 and 968427 and stop after 5 and 56 completion tokens. All three appearances of the original failing Record 4230 return 709295 in every run.

The original CP4 wrong answer is not reproduced. These measurements establish the bounded diagnostic outcomes, not a fix, kernel/cache attribution or broad long-context correctness. The output-cap comparison also remains a single pair; execution variability is not isolated.

For cap 2048, terminal collection verifies source, inputs, raw requests/responses, recorded runtime maps, ownership and cleanup. The separate independent live collector missed the diagnostic window; its receipt is unavailable. functional-recorded-runtime auditing therefore remains distinct from the stricter live-receipt audit used for the original pair.

All drivers exit 0, owned cleanup is empty and independent terminal observations find four idle GPUs. No foreign GPU processes are observed. Each server records one successful startup warmup plus 22 successful diagnostic HTTP requests. Sampling cannot exclude activity between observations.

## Data and Figures

Each cell contains evidence.tar.gz, files.json, configuration.json and audit.json. The original 96-token cells also contain startup-audit.json and startup-receipt.json. The pair audits, hardware reference and export-provenance.json bind comparisons and archive identities. Raw local provenance remains preserved separately from this selected publication.
