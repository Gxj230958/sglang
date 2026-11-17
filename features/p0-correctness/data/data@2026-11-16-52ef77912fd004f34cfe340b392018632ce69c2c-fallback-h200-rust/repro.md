# E22 Fallback candidate H200 TP8 Rust correctness

## Environment

Eight NVIDIA H200 GPUs, with their UUIDs recorded throughout execution. The post-evaluation hardware receipt reports 143771 MiB per GPU, driver 595.71.05, persistence enabled, 700 W current/default power limits and NV18 connectivity between every GPU pair. Its UUIDs match the evaluation; power configuration was not monitored continuously. The container digest was not captured.

Actual imports pin Torch 2.14.1 with CUDA 13.0, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache 0.7.4+cu130 with sm90a provider, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.2 and sgl-fa3 0.1.0. Rust and Cargo are 1.92.0; build strings are archived.

Model: `zai-org/GLM-5-1028-Provider`, FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its original FP8 NextN draft. The archived plan pins config, weight index, tokenizer and tokenizer-config hashes, all rechecked before launch. Weight shards were not individually rehashed in this round.

## Setup

Verify SHA256SUMS, extract evidence.tar.gz, and verify all 51 members against files.json. Obtain the exact source commit and authorized model revision. Install the package versions above in a CUDA 13 environment with the recorded Rust toolchain, and verify their actual imports against results/h200-tp8/server-imports.json.

On an exclusively reserved eight-H200 devbox, set `S` to the exact source tree, `M` to the checkpoint, `OVERLAY` to the pinned dependency directory, `SOURCE_MANIFEST` to the extracted source-manifest.json, `R` to a fresh output directory and `P=31880`. Set `PY` and `EVAL` to the matching Python and sgl-eval executables. Use task-specific empty `SGLANG_CACHE_DIR`, `TRITON_CACHE_DIR`, `TORCH_EXTENSIONS_DIR` and `FLASHINFER_WORKSPACE_BASE`; set `PYTHONNOUSERSITE=1`, `CARGO_BUILD_JOBS=4` and `SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0`. Run:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

The runner builds Rust, verifies source and exclusive GPU access, checks actual worker mappings and resolved service settings, runs the evaluator, records counters and cleans up its owned process group. Archived start.sh, preflight.py and probe.py contain the original host-specific historical-job prerequisites; use the runner entry point on a fresh allocation.

## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean local worktree. This combines fixed development snapshot `dd452d241ae9075a414255b62acca80e9b80d64d` with the NVFP4 mixed-precision fix. All 12586 tracked source files match before and after execution. The default Rust backend selected eight live workers mapping extension SHA256 `5465ff96ba96e1dc4f0e41387bda0c5608ec86303b9ac95dfd6a622ea785f947`.

The source changes 31 files relative to [E21](../data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-current-h200-rust/repro.md), with no Rust source changes. candidate-comparison.json records unchanged checkpoint, dependency, service and full-evaluation settings. E22 explicitly disables optional fused H64 decode. This local candidate has not been accepted as the release cutoff.

## Scripts

The archive contains 13 hashed round-specific inputs, source manifest, exact server/evaluation commands, startup/source checks, raw outputs and cleanup receipts. Runtime source is referenced by commit and manifest.

Server: TP8, EP1, attention DP1, BF16 KV, FlashMLA sparse prefill/decode, automatic MoE, context 65536, memory fraction 0.75, chunk 32768, maximum running requests/decode graph batch 32, eager prefill, natural EAGLE steps/topk/draft-tokens 3/1/4, explicit FP8 draft quantization and server seed 1. The glm45/glm47 parsers, metrics and cache reporting are enabled. Actual import/runtime receipts show an empty simulation environment.

## Workload

Full [GSM8K](https://huggingface.co/datasets/openai/gsm8k) test split, 1319 unique examples, through sgl-eval 0.1.2. Evaluator commit is recorded in metrics.json; dataset checkout revision was not separately captured. One run, 64 threads, temperature 1.0, top_p 0.95, request seed 1 and max_tokens 32768:

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31880/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

Server ready at 20:08:03 UTC; evaluation completed at 20:24:43 UTC on November 16. These are correctness measurements.

## Results

| Metric | E21, source `01d0a662d1` | E22, source `52ef77912f` |
|---|---:|---:|
| Correct | 1258 / 1319 | 1251 / 1319 |
| Accuracy | 95.3753% | 94.8446% |
| Normal stop | 1317 / 1319 | 1314 / 1319 |
| Stop rate | 99.8484% | 99.6209% |
| Length truncations | 2 | 5 |
| Request errors | 0 | 0 |

The five length-limited responses all reached 32768 output tokens: gsm8k-89 is symbolically correct; gsm8k-87, gsm8k-423, gsm8k-1016 and gsm8k-1176 are incorrect. Accuracy includes the truncated correct answer. Stopping qualification remains open. Both source revisions have one run; the difference alone does not establish a source-caused regression or stopping nonregression against a same-setting native reference.

Independent audit recounted every prediction and finish reason and verified aggregate metrics. All prediction completion tokens sum to 746240, matching the generation counter delta; 273055 verification calls give natural acceptance 2.7329292633. This correctness-workload ratio is separate from performance sweep results. NVFP4 and image-level qualification require their own evidence.

## Data and Figures

evidence.tar.gz contains 51 files, 1435398 compressed bytes, SHA256 `7cfaaee49483601f78232c108ec35db0119c91d507876ee9f7a4cdca72b847c7`. files.json hashes each member; audit.json records independent row, metric, input/source, backend and cleanup checks. startup-audit.json and startup-receipt.json retain live mapped-extension and import evidence.

The 683 GPU samples and 6189 process-ownership records contain no query errors or foreign processes. Sampling cannot exclude activity between observations. Driver exit is zero. The successful final health check and evaluation completion precede the runner's shutdown signals. Independent postrun observation confirms no owned processes, no compute processes and zero used memory on all eight GPUs. The execution lock was released after cleanup and archive verification; the shared allocation remains available.
