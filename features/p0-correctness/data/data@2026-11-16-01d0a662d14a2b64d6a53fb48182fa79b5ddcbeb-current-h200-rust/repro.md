# E21 Current H200 TP8 Rust correctness

## Environment

Eight NVIDIA H200 GPUs, 143771 MiB each, driver 595.71.05, persistence enabled and 700 W current/default power limits. Every GPU pair reports NV18 connectivity. hardware.json contains the timestamped hardware and topology queries. The container image digest was not captured; the actual server import receipt pins Torch 2.14.1 with CUDA 13.0, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT cache 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.2 and sgl-fa3 0.1.0. The JIT provider is sm90a. Cargo and rustc report 1.92.0; complete build strings are archived.

Model: `zai-org/GLM-5-1028-Provider`, FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, with its original FP8 NextN draft. plan.json pins config, index, tokenizer and tokenizer-config hashes. Preflight rechecked those four files; every weight shard was not rehashed in this run.

## Commit

Runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`, clean worktree. All 12,581 source-manifest files match before and after execution. The default Rust backend was selected with the explicit tree-core override unset. All eight live worker process maps contain Rust extension SHA256 `5465ff96ba96e1dc4f0e41387bda0c5608ec86303b9ac95dfd6a622ea785f947`. startup-receipt.json independently rereads those mappings and hashes while evaluation is running.

## Setup

Verify SHA256SUMS, extract evidence.tar.gz, and verify its 50 members against files.json. Obtain the exact runtime commit and the authorized checkpoint revision. Install the package versions listed in plan.json in a CUDA 13 environment with the recorded Rust toolchain; verify the FA3 and FlashInfer imports against results/h200-tp8/server-imports.json. Keep the FP8 draft checkpoint and quantization explicit.

On an exclusively reserved eight-H200 devbox, set `S` to the exact source tree, `M` to the checkpoint, `OVERLAY` to the pinned dependency directory, `SOURCE_MANIFEST` to the extracted source-manifest.json, `R` to a fresh output directory and `P=31878`. Set `PY` and `EVAL` to the matching Python and sgl-eval executables. Use task-specific empty SGLANG_CACHE_DIR, TRITON_CACHE_DIR, TORCH_EXTENSIONS_DIR and FLASHINFER_WORKSPACE_BASE paths, `PYTHONNOUSERSITE=1` and `CARGO_BUILD_JOBS=4`. Run:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

runner.sh builds Rust on the devbox, verifies source and exclusive GPU access, launches the server, verifies eight Rust ranks and resolved settings, runs the evaluator, records counters and cleans up the owned process group. start.sh, preflight.py and probe.py retain the original machine-specific orchestration, including historical-job and orphan-wrapper checks; those historical prerequisites belong to the original host. The runner entry point above uses the pinned experiment inputs on a fresh allocation.

## Scripts

The archive contains the original 13 hashed launch inputs, files.json, source manifest, launch preflight, exact server/evaluation commands, source checks and cleanup receipts. These are round-specific scripts. Runtime source files are referenced by commit and manifest rather than copied into the tracking branch.

Server: TP8, EP1, attention DP1, BF16 KV, FlashMLA sparse prefill/decode, automatic MoE selection, context 65536, memory fraction 0.75, chunk 32768, maximum running requests and decode graph batch 32, eager prefill, natural EAGLE steps/topk/draft-tokens 3/1/4, explicit FP8 draft quantization and server seed 1. glm45/glm47 parsers, metrics and cache reports are enabled. Simulation environment is empty in the actual import/runtime receipts. argv.txt and server_info.json preserve exact arguments and resolved values.

## Workload

Full GSM8K test split, 1319 unique examples, through sgl-eval 0.1.2; metrics.json records ns_commit_sha `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`. Dataset reference: [GSM8K](https://huggingface.co/datasets/openai/gsm8k). The dataset checkout revision was not separately recorded. One run, 64 evaluator threads, temperature 1.0, top_p 0.95, request seed 1 and max_tokens 32768:

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31878/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

The server became ready at 17:02:33 UTC and the evaluation completed at 17:15:53 UTC. This is a correctness run. Historical H200 E20 uses another runtime revision, server/request seed policy and output limit; its results do not form a controlled baseline for E21.

## Results

| Metric | Current H200 Rust |
|---|---:|
| Correct | 1258 / 1319 |
| Accuracy | 95.3753% |
| Normal stop | 1317 / 1319 |
| Stop rate | 99.8484% |
| Length truncations | 2 |
| Request errors | 0 |

Both length-limited responses reached 32768 completion tokens: gsm8k-487 is symbolically correct and gsm8k-505 is incorrect. Accuracy therefore includes one truncated answer. Same-setting stopping nonregression is not established by this single run. Runtime integration remains subject to the broader correctness gate.

All 1319 unique IDs, predictions and finish reasons were independently recounted. Aggregate accuracy, stop/truncation/error rates and completion-token sums agree with the evaluator. Generation-token delta 586503 equals the prediction completion-token sum; 213896 verification calls give a natural acceptance ratio of 2.742000785. This correctness-workload counter ratio is separate from controlled performance measurements.

## Data and Figures

evidence.tar.gz contains 50 raw files, 1337511 compressed bytes, SHA256 `99b0b13ece35ee265c512f8fc1df6e79cd3b8f2e76b9e7819ad8ed9cb5b24a8a`. files.json hashes every member. audit.json records the independent output, source, command, backend and cleanup checks. startup-audit.json and startup-receipt.json preserve live import and mapped-extension evidence; hardware.json records topology and power configuration.

The JSON monitor recorded 596 GPU samples with no query errors or foreign-process observations. A separate process-tree log resolves all 5345 GPU-process observations to the owned server. Sampling does not exclude activity between observations. Driver exit is zero; cleanup reports no remaining owned processes. The final independent probe confirms eight idle GPUs, no GPU processes and no active blocked workload. The H200 lock was released after archive verification; the shared allocation remains available.
