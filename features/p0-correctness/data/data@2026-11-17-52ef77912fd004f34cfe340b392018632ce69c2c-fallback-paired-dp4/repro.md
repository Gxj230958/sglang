# E27 fallback candidate paired DP4 correctness

## Environment

Four NVIDIA GB300 GPUs, 284208 MiB each, driver 580.178.04, 1400 W power limits and NV18 links. hardware-reference.json is an earlier observation of the same allocation; both runs independently record the same GPU UUIDs. Container digest was not captured; image-level qualification remains separate.

FP8 checkpoint `zai-org/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`; performance-only NVFP4 checkpoint `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 NextN draft. The plans pin checkpoint config, index and tokenizer hashes.

Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache/sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.2. Actual dependency imports, toolchain and runtime settings are archived.

## Setup

Verify SHA256SUMS, extract each evidence.tar.gz separately and verify all 112 raw members against files.json. Obtain the pinned source and authorized checkpoints; install the package versions above in a CUDA 13 environment. Materialize source, overlay and model paths from plan.json, or record substitutions in a new reproduction.

Reserve four exclusive GB300 GPUs and ports 32240/32241. Use the exports in start.sh with TASK pointing to the extracted inputs and R to fresh results. Preserve S/M/D/OVERLAY/P/SOURCE_MANIFEST and interpreter/evaluator paths; use a fresh owner and separate cache directories. Original preflight/launch scripts retain predecessor and allocation checks as receipts. Adapt these checks for the reproduction allocation, then run:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

On success or failure, run cleanup.py and verify_source.py, retain their output and independently confirm terminal owned processes and idle GPUs before releasing the lock.

Behavior-changing environment: default Rust TreeCore, SGLANG_RUST_BUILD_MODE=auto, SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0, SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1, CUDA_VISIBLE_DEVICES=0,1,2,3, OMP_NUM_THREADS=4, PYTHONNOUSERSITE=1, CARGO_BUILD_JOBS=4, SPT_NOENV=1, NCCL_SOCKET_IFNAME=cilium_host, GLOO_SOCKET_IFNAME=cilium_host, NCCL_DEBUG=WARN, explicit source/overlay PYTHONPATH and offline checkpoint loading. Simulation variables are absent.

## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean candidate. All 12586 tracked files match before and after both runs. Four actual Rust workers per run map extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. Actual quantization is fp8 or modelopt_mixed.

## Scripts

Archives preserve 15 hashed execution inputs per format, requests, responses, logs and predictions. Source code is referenced by commit. paired-audit.json verifies matching actual source/dependencies/draft/service/evaluation, all 1319 evaluation problems and the 34-request functional protocol. Functional audits independently reconstruct every probe request and compare exact answers, finish reasons, cache counts and actual rank routing.

Service: TP4/EP4/attention-DP4, MoE all-to-all none, FP8 KV, TRTLLM DSA prefill/decode and MoE, separate shared experts, FP32 lm_head, context 131072, memory fraction 0.80, eager prefill, decode CUDA graph and natural EAGLE steps/topk/draft tokens 3/1/4 with FP8 draft quantization. Launch chunk 8192 resolves to 2048 per DP rank; global maximum running requests 64 resolves to 16 per rank. Server seed 1 and glm45/glm47 parsers. Full commands are in results/dp4/argv.txt.

## Workload

After startup warmup, flush and run 18 synthetic retrieval requests: three record positions each at target sizes 300/3000/9000/24000/60000/110000, temperature 0 and max_tokens 2048. The largest actual prompts are about 120936 tokens. All 18 requests report zero cached tokens; the runner flushes once before the retrieval sequence. Then flush and execute 16 directed requests: cold, warm, fork and warm-fork for each DP rank, temperature 0, seed 1 and max_tokens 512. The checkpoint template ignores enable_thinking=False and prefills the reasoning marker; the output budgets allow reasoning and a final answer.

Flush again, then run the full GSM8K test split: 1319 unique examples, one run, 64 threads, temperature 1.0, top_p 0.95, seed 1 and max_tokens 32768. The dataset checkout revision was not independently captured. The evaluation counter baseline excludes warmup and functional requests.

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:32240/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

FP8 became ready at November 17 01:16:46 UTC and completed full evaluation at 01:38:53. NVFP4 became ready at 01:56:05, completed functional probes at 01:59:10 and full evaluation at 02:16:24. Each launch has a six-hour bound.

## Results

| Metric | FP8 | NVFP4 |
|---|---:|---:|
| Correct /1319 | 1250 | 1247 |
| Normal stop /1319 | 1313 | 1313 |
| Length limits | 6 | 6 |
| Request errors | 0 | 0 |
| Retrieval exact and stopped /18 | 17 | 18 |
| Directed routing/cache passed /16 | 16 | 16 |
| Natural tokens/verify | 2.640945 | 2.663936 |

FP8's cold 64737-token retrieval for Record 2307 returns 443434, the value for adjacent Record 2308, instead of expected 946335. It stops after six completion tokens with zero cached tokens. NVFP4 returns the expected value and stops. The FP8 functional gate stays open pending the prepared same-source Rust/Python reference; these observations do not establish a backend or quantization cause.

Both formats have six length-limited GSM8K responses, all incorrect at 32768 tokens. Individual IDs and exact sampling are in audit.json. NVFP4 has three fewer correct answers in this single pair and remains performance-only. Quality parity, stopping nonregression and serving performance are not established by this round.

Each run has 1354 successful chat HTTP attempts (one warmup, 34 functional, 1319 evaluation), zero failed attempts, zero sampling errors and no observed foreign GPU processes. Drivers exit zero, cleanup is empty, source is unchanged and independent terminal checks find four idle GPUs. Shutdown diagnostics occur after the explicit termination signal. Sampling cannot exclude activity between observations.

## Data and Figures

| Weights | Raw files | GPU samples / ownership records | Archive SHA256 |
|---|---:|---:|---|
| FP8 | 112 | 990 / 4654 | `503db5813c2ff9847b5df4b272e2406343a2d36634385603af7e66e4b91154b5` |
| NVFP4 | 112 | 989 / 4596 | `ea53f27249a8ecd0602a1c6fdf6e2398bcdffcf773611e98aa73e4614f921352` |

files.json hashes every original raw member. audit.json recounts full predictions and counters. functional-audit.json reconstructs probes and keeps failures explicit. startup-receipt.json and startup-audit.json bind actual workers, commands and source; paired-audit.json compares the two arms.
