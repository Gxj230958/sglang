# E23 H200 Python TreeCore correctness reference

## Environment

Eight NVIDIA H200 GPUs, exclusively reserved for this run. GPU UUIDs and process ancestry are archived. Container digest, power limits and topology were not independently captured in this round.

Actual imports: Torch 2.14.1 with CUDA 13.0, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache 0.7.4+cu130 with sm90a provider, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.2 and sgl-fa3 0.1.0. Rust/Cargo 1.92.0 build strings are archived.

Model: `zai-org/GLM-5-1028-Provider`, FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its original FP8 NextN draft. The plan pins config, weight-index, tokenizer and tokenizer-config hashes; launch preflight rechecks them. This round does not rehash every weight shard.

## Setup

Verify SHA256SUMS, extract evidence.tar.gz and verify its 51 members against files.json. Obtain the exact source commit and authorized model revision. Install the package versions above in a CUDA 13 environment with the recorded Rust toolchain; compare actual imports with results/h200-tp8/server-imports.json.

On an exclusively reserved eight-H200 devbox, set `S` to that source tree, `M` to the checkpoint, `OVERLAY` to the pinned dependency directory, `SOURCE_MANIFEST` to the extracted source-manifest.json, `R` to a fresh output directory and `P=31882`. Set `PY` and `EVAL` to the matching Python and sgl-eval executables. Reserve 31883 for distributed initialization. Set fresh task-specific `SGLANG_CACHE_DIR`, `TRITON_CACHE_DIR`, `TORCH_EXTENSIONS_DIR` and `FLASHINFER_WORKSPACE_BASE`, plus `PYTHONNOUSERSITE=1`, `CARGO_BUILD_JOBS=4` and `SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0`. Run:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

The runner explicitly selects `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`, verifies source and idle GPUs, prebuilds Rust, starts the server, checks all eight Python workers, executes the evaluator and cleans up its owned process group. Use runner.sh on a fresh allocation; archived start.sh/preflight.py/probe.py include the original allocation's historical-job checks.

## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean worktree. All 12586 tracked source files match before and after execution. The live audit verified Python TreeCore construction logs, process identities, backend environment and absent mem_cache extension mappings for all eight workers. Rust prebuild is preparation shared with E22; serving uses Python.

settings-comparison.json binds this run to [E22](../data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-h200-rust/repro.md): checkpoint, dependencies, service settings and evaluation settings match. TreeCore selection differs; ports and task paths are isolated.

## Scripts

The archive contains 13 hashed round-specific inputs, exact server/evaluator commands, source manifest, live startup receipts, raw predictions, counter snapshots and cleanup evidence. Runtime source is referenced by commit.

Service: TP8, EP1, attention DP1, BF16 KV, FlashMLA sparse prefill/decode, automatic MoE, context 65536, memory 0.75, chunk 32768, maximum running requests/decode graph batch 32, eager prefill, natural EAGLE steps/topk/draft-tokens 3/1/4, FP8 draft quantization and server seed 1. glm45/glm47 parsers, metrics and cache reporting are enabled. Runtime/import receipts show an empty simulation environment.

## Workload

Full [GSM8K](https://huggingface.co/datasets/openai/gsm8k) test split: 1319 unique examples, one run, 64 threads, temperature 1.0, top_p 0.95, request seed 1 and max_tokens 32768. Evaluator commit is in metrics.json; the dataset checkout revision was not separately captured.

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31882/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

Server ready at 20:45:41 UTC; evaluation completed at 21:00:37 UTC on November 16. These are correctness measurements.

## Results

| Metric | E22 Rust | E23 Python |
|---|---:|---:|
| Correct | 1251/1319 | 1256/1319 |
| Accuracy | 94.8446% | 95.2237% |
| Normal stop | 1314/1319 | 1316/1319 |
| Stop rate | 99.6209% | 99.7726% |
| Length truncations | 5 | 3 |
| Request errors | 0 | 0 |

Python's three length-limited responses are gsm8k-505, gsm8k-552 and gsm8k-1035; all reach 32768 output tokens and are symbolically incorrect. Rust and Python truncate different request IDs. backend-comparison.json records their union and both outcomes. Both backends have truncations; one run per backend cannot establish causality or statistical stopping nonregression. Delivery stopping qualification remains open.

All 656509 predicted completion tokens match the generation-counter delta. The 246039 verification calls give natural acceptance 2.6683127472. This correctness-workload ratio is separate from performance sweep results; NVFP4 and image-level qualification require their own evidence.

## Data and Figures

evidence.tar.gz contains 51 files, 1428347 compressed bytes, SHA256 `fc541ff2bb8dd682b6dc16e766a3de5c645dd52f2917ba5b7bdddc6e8cf07902`. files.json hashes every member. audit.json independently verifies predictions, aggregate metrics, source, inputs, backend, ownership and cleanup; startup-audit.json and startup-receipt.json retain live evidence.

The 637 GPU samples and 5746 process-ownership records contain no sampling errors or foreign processes. Sampling cannot exclude activity between observations. Driver exit is zero. Independent postrun observation confirms idle GPUs and completed owned-process cleanup. The execution lock was released; the shared allocation remains available.
