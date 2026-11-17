# E25 fallback candidate paired CP4 correctness

## Environment

Four NVIDIA GB300 GPUs, 284208 MiB each, driver580.178.04, 1400 W power limits, NV18 links between GPUs. hardware-reference.json is the earlier same-allocation observation used for E24; both CP4 runs independently record the same four GPU UUIDs. GPU ownership is sampled throughout each run.

Torch2.14.1+cu130, Transformers5.19.0, FlashInfer Python/cubin0.7.4, JIT cache and sm103a provider0.7.4+cu130, sglang-kernel0.4.11, sgl-deep-gemm0.2.8, sgl-flash-mla1.0.5, kernels0.14.1 and sgl-eval0.1.2. Rust/Cargo1.92.0 toolchain strings and actual imports are archived. This is source-level validation; the container digest was not captured and image-level qualification remains pending.

FP8 model: `zai-org/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`. Performance-only NVFP4: `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 checkpoint's NextN draft. Each plan pins config, index and tokenizer hashes. The shared checkpoint preparation verified all163 NVFP4 files; its inventory is preserved in [E24](../data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-tp4/nvfp4-verification.json). FP8 weight shards were not all rehashed in this round.

## Setup

Verify SHA256SUMS, extract each evidence.tar.gz into a separate reproduction directory, and verify all62 members against files.json. Obtain the exact source commit and authorized model revisions. Install the versions in plan.json in a CUDA13 environment; FlashInfer cubin uses https://flashinfer.ai/whl. Compare actual imports with server-imports.json.

Materialize the source, overlay and models at the paths recorded in plan.json, or record all path changes in a new reproduction. Reserve an exclusive four-GB300 allocation and ports32210/32211. Use the environment exports in start.sh with TASK pointing to the extracted input directory, R pointing to a fresh result directory, and fresh SGLANG_CACHE_DIR, TRITON_CACHE_DIR, FLASHINFER_WORKSPACE_BASE and TORCH_EXTENSIONS_DIR. Preserve S/M/D/OVERLAY/P/SOURCE_MANIFEST and the recorded interpreter/evaluator paths. From the extracted input directory run:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

The runner verifies source and idle GPUs, selects Rust, starts serving, verifies actual worker mappings/settings, runs full GSM8K, flushes and runs the retrieval/prefix protocols, then stops its server group. Original preflight.py/start.sh/launch.py retain allocation/predecessor checks as execution receipts. After reproduction, run verify_source.py and cleanup.py using the exported owner, then independently confirm idle GPUs before releasing the lock.

Behavior-changing environment: SGLANG_RUST_BUILD_MODE=auto, default Rust TreeCore, SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0, SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1, CUDA_VISIBLE_DEVICES=0,1,2,3, OMP_NUM_THREADS=4, PYTHONNOUSERSITE=1, CARGO_BUILD_JOBS=4, SPT_NOENV=1, NCCL_SOCKET_IFNAME=cilium_host, GLOO_SOCKET_IFNAME=cilium_host, NCCL_DEBUG=WARN, explicit source/overlay PYTHONPATH, and HF/Transformers offline mode. Simulation variables are absent. Each format uses a fresh separate cache directory. Startup compilation time is not a performance result.

## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean worktree. All12586 tracked source files verify before and after each run. Four live Rust workers per format map extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. Actual FP8 quantization is `fp8`; NVFP4 is `modelopt_mixed`.

## Scripts

The archives contain15 hashed execution/probe inputs per format and full raw outputs. Runtime source is referenced by commit. paired-final-audit.json verifies normalized actual service/evaluator commands, dependencies, source, draft and settings. The probe.py, midfork.py and functional-audit.py inputs are byte-identical across formats. Independent audits reconstruct all24 functional request hashes and require the exact numeric answer plus natural stop.

Service: TP4/EP1/attention-DP1, interleaved prefill CP4, whole KV per rank, BF16 KV, FlashMLA sparse prefill/decode, TRTLLM MoE, separate shared experts, FP32 lm_head, context131072, memory fraction0.80, chunk8192, maximum running requests/decode graph batch64, breakable prefill graphs, natural EAGLE steps/topk/draft tokens3/1/4, FP8 draft quantization, server seed1 and glm45/glm47 parsers. Full commands are in results/cp4/argv.txt.

## Workload

Full [GSM8K test split](https://huggingface.co/datasets/openai/gsm8k):1319 unique examples per format, one run,64 threads, temperature1.0, top_p0.95, seed1 and max_tokens32768. metrics.json records evaluator identity; dataset checkout revision was not independently captured. Startup warmup precedes the evaluation-counter baseline.

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:32210/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

After full GSM8K, flush and sequentially query18 synthetic retrieval requests: three record positions each at target sizes300/3000/9000/24000/60000/110000, temperature0,max_tokens96. The largest actual prompts are about120936 tokens. Then flush and run six prefix/mid-fork/follow-up probes at temperature0,max_tokens512. Both functional protocols disable thinking; retrieval requests also collect log probabilities. Archived scripts deterministically generate the requests; outputs retain usage, cache counts, finish reasons and request hashes.

FP8 ready22:51:25UTC, full evaluation complete23:05:05, functional probes complete23:05:23. NVFP4 ready23:20:51, full evaluation complete23:31:52, probes complete23:32:07 on November16,2026. Each launch has a six-hour bound.

## Results

| Metric | FP8 | NVFP4 |
|---|---:|---:|
| Correct | 1247/1319 | 1246/1319 |
| Accuracy | 94.5413% | 94.4655% |
| Normal stop | 1312/1319 | 1314/1319 |
| Stop rate | 99.4693% | 99.6209% |
| Length truncations | 7 | 5 |
| Request errors | 0 | 0 |
| Exact retrieval answers with natural stop | 17/18 | 18/18 |
| Exact prefix answers with natural stop | 6/6 | 6/6 |
| Generated GSM8K tokens | 794707 | 751512 |
| Verification calls | 292916 | 284424 |
| Natural acceptance, tokens/verification call | 2.713088 | 2.642224 |

FP8's failed warm retrieval asks for Record4230 at120936 prompt tokens, with120896 cached tokens. Expected709295; returned968752, the neighboring Record4229 value, with six output tokens and natural stop. The preceding cold Record1208 and following warm Record8458 are correct. NVFP4 answers all18 correctly. This confirms one FP8 wrong answer; the cause remains unresolved. CP4 functional qualification stays open pending bounded reproduction and TP4 control.

FP8 length IDs410,164,380,675,1016,1176,1074 all reach32768 tokens;164 is correct and the other six are incorrect. NVFP4 length IDs87,494,423,1176,1059 all reach32768 tokens and are incorrect. NVFP4 has one fewer correct answer and two more normal stops. These single observations do not establish quality parity or stopping nonregression. NVFP4 remains performance-only. Correctness-workload acceptance ratios do not establish a serving performance advantage.

## Data and Figures

| Format | Raw files | Compressed bytes | Archive SHA256 |
|---|---:|---:|---|
| FP8 | 62 | 1392553 | `1b27bcad03af49d29788627983426e2b7bb7c2d9197ce81669831918925d0336` |
| NVFP4 | 62 | 1427622 | `075f99a4d85f1fbd764c0a8b380ba70428cfcbaa46c2b4acbf631f7d7f5294d9` |

files.json hashes every raw member. audit.json recounts all predictions and reconciles counters, source, runtime and ownership. functional-audit.json reconstructs requests and verifies raw answers; startup receipts bind live process identities and commands. FP8 has669 GPU samples/3128 ownership records; NVFP4 has662/2968. Both have zero sampling errors and no observed foreign GPU processes; sampling cannot exclude activity between observations. Each run has1344 successful chat HTTP attempts and zero failed attempts. Drivers exit zero, exact identities are terminal, cleanup is empty and independent final checks show four idle GPUs.
