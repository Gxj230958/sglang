# E24 fallback candidate paired TP4 correctness

## Environment

Four NVIDIA GB300 GPUs, 284208 MiB per GPU, driver 580.178.04, 1400 W default/current power limits. The recorded topology has NV18 links between all GPUs and two NUMA nodes. hardware-live.json preserves UUIDs, topology and power observations. The allocation was exclusively reserved for each run; GPU process ownership was sampled every two seconds.

Actual dependencies: Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache and sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.2. Rust/Cargo 1.92.0 toolchain strings are archived. Container digest was not captured; this round qualifies source execution, while image-level GPU qualification remains pending.

Models: FP8 `zai-org/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; performance-only NVFP4 `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 checkpoint's NextN draft. Config, index and tokenizer hashes are pinned in each plan. Preparation verified all 163 NVFP4 files totaling 439756337764 bytes against Git blob/LFS identities; nvfp4-verification.json retains the inventory. FP8 weight shards were not all rehashed in this round.

## Setup

Verify SHA256SUMS, extract each format's evidence.tar.gz separately and verify its 52 members against files.json. Obtain the exact source commit and authorized model revisions, then install the recorded dependencies in a CUDA13 environment. FlashInfer cubin uses the CUDA-independent https://flashinfer.ai/whl index; compare actual imports with the archived server-imports.json.

On an exclusively reserved four-GB300 allocation, materialize the source, overlay and model paths named in plan.json. server.py verifies the source import against that exact path. Preserve the original evidence; use a separate extracted input directory for a reproduction. Select one format at a time, reserve ports 32180/32181, and copy the environment exports from its start.sh while setting TASK to the extracted input directory, R to a fresh output directory, and all four kernel-cache variables to fresh per-run locations. Keep S/M/D/OVERLAY consistent with plan.json. Set PY and EVAL to the matching interpreter/evaluator executables. Invoke from the input directory:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

The runner verifies source and idle GPUs, builds/selects Rust, launches serving, checks all four worker mappings and resolved settings, evaluates full GSM8K, and terminates its server process group. start.sh/preflight.py/launch.py retain original allocation and predecessor checks; they are execution receipts for the original allocation. After reproduction, run verify_source.py and cleanup.py with the exported owner, and independently confirm idle GPUs before releasing the lock.

Behavior-changing environment: SGLANG_RUST_BUILD_MODE=auto, default Rust TreeCore selection, SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0, SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1, CUDA_VISIBLE_DEVICES=0,1,2,3, OMP_NUM_THREADS=4, PYTHONNOUSERSITE=1, CARGO_BUILD_JOBS=4, SPT_NOENV=1, NCCL_SOCKET_IFNAME=cilium_host, GLOO_SOCKET_IFNAME=cilium_host and NCCL_DEBUG=WARN. HF/Transformers offline mode and explicit source/overlay PYTHONPATH are enabled. The simulation environment is empty. Network interface changes on another allocation require an explicit new environment record.

The original runs used separate caches copied from one terminated same-candidate preparation cache: 2230 identical inventory entries, 1303468379 bytes. paired-cache-seed-audit.json independently compares the two preserved inventories. Cache binaries are referenced by inventory rather than included. A fresh-cache reproduction changes startup compilation, so startup durations are not comparable. These are correctness measurements.

## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean worktree. All 12586 tracked files match the source manifest before and after both runs. Four live Rust mappings per run share extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. Startup receipts bind actual PID/start ticks, mapped binaries, evaluator commands, imports and process environments.

## Scripts

Each raw archive contains 12 hashed round inputs, exact service/evaluator commands, full raw predictions, metrics, source checks, runtime settings and cleanup evidence. Runtime source is referenced by commit. paired-final-audit.json compares normalized actual commands, dependencies, draft, source and workload. paired-live-quantization.json verifies actual FP8 `fp8` and NVFP4 `modelopt_mixed` selection.

Service: TP4/EP1/attention-DP1, BF16 KV, FlashMLA sparse prefill/decode, TRTLLM MoE, separate shared experts, FP32 lm_head, context 65536, memory fraction 0.80, prefill chunk 8192, maximum running requests/decode graph batch 64, eager prefill, natural EAGLE steps/topk/draft-tokens 3/1/4, FP8 draft quantization, server seed 1, glm45/glm47 parsers, metrics and cache reporting. Original command lines are in results/tp4/argv.txt.

## Workload

Full [GSM8K test split](https://huggingface.co/datasets/openai/gsm8k): 1319 unique examples, one run per format, 64 threads, temperature 1.0, top_p 0.95, seed 1, max_tokens 32768. The evaluator commit is preserved in metrics.json; the dataset checkout revision was not independently captured. SGLang's startup warmup precedes the recorded evaluation-counter baseline. Each run has 1320 successful chat HTTP attempts in the serving log and 1319 evaluated examples; failed HTTP attempts are zero.

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:32180/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

FP8 ready 22:01:58 UTC, completed 22:15:03 UTC; NVFP4 ready 22:24:46 UTC, completed 22:38:27 UTC on November 16, 2026. Full output lengths and finish reasons are retained per example. Each launch has a six-hour bound.

## Results

| Metric | FP8 | NVFP4 |
|---|---:|---:|
| Correct | 1258/1319 | 1240/1319 |
| Accuracy | 95.3753% | 94.0106% |
| Normal stop | 1318/1319 | 1312/1319 |
| Stop rate | 99.9242% | 99.4693% |
| Length truncations | 1 | 7 |
| Request errors | 0 | 0 |
| Generated tokens | 621714 | 751377 |
| Verification calls | 230784 | 284647 |
| Natural acceptance, tokens/verification call | 2.693922 | 2.639680 |

The FP8 length-limited response is gsm8k-1074. NVFP4 length-limited responses are gsm8k-119, 505, 675, 835, 926, 1052, 1176. Every truncated response reaches 32768 tokens and is incorrect. NVFP4 has 18 fewer correct answers and six fewer normal stops: accuracy differs by -1.364670 percentage points and stop rate by -0.454890 points. This is a single paired observation; NVFP4 remains performance-only. Quality parity, stopping nonregression and final delivery qualification are not established. These correctness-workload acceptance ratios do not replace a bounded performance comparison.

## Data and Figures

| Format | Raw files | Compressed bytes | Archive SHA256 |
|---|---:|---:|---|
| FP8 | 52 | 1372129 | `4744cb3b9f6b0b73b0b7f20d49249570eeb9f885c78455367ef05237cff2fd2e` |
| NVFP4 | 52 | 1483052 | `bd70da89f98de923dbf7161788a828cc9157e642b09f529034c2a34747d89c16` |

Each files.json hashes every raw member. audit.json independently recounts predictions, finish reasons, token/counter equality, source integrity and ownership; startup-audit.json and startup-receipt.json retain live evidence. FP8 has 469 GPU samples and 2260 process-ownership records; NVFP4 has 613 and 2823. Neither has sampling errors or observed foreign processes. Sampling cannot exclude activity between observations. Both drivers exit zero, exact process identities are terminal, cleanup is empty and independent final observation confirms four idle GPUs. The execution lock was released after both runs.
