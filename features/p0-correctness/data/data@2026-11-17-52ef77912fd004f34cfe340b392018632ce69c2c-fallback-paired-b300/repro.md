# E26 fallback candidate paired B300 correctness


## Environment

Eight NVIDIA B300 SXM6 AC GPUs, 275040 MiB each, driver 590.48.01, 1100 W power limits, NV18 links and x86_64 host. hardware-reference.json captures this allocation at November 16 22:57:49 UTC; every run separately records its GPU UUIDs and process ownership. Container digest was not captured; these are source-level results.

FP8 checkpoint: `zai-org/GLM-5-1028-Provider` at `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`. Performance-only NVFP4: `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 NextN draft. Per-run plans pin checkpoint metadata and tokenizer hashes.

Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT cache/sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.2. Actual imports, toolchain strings and Rust shared-object mappings are archived.


## Setup

Verify SHA256SUMS, extract each evidence.tar.gz into a separate reproduction directory, and verify every member against its files.json. Obtain the exact source and authorized checkpoint revisions, install the pinned packages in a CUDA 13 environment, and materialize the source/overlay/model paths in plan.json. For a different filesystem layout, record the path substitutions in a new run.

Reserve eight exclusive B300 GPUs and the ports in the selected plan. Use the environment exports from its archived start.sh with TASK pointing to the extracted inputs and R to a fresh result directory. Preserve S/M/D/OVERLAY/P/SOURCE_MANIFEST and interpreter/evaluator paths. Use fresh cache directories and a unique owner. The archived preflight and launch scripts retain original allocation/predecessor checks as execution receipts. After adapting those checks for the new allocation, execute the runner under a bounded supervisor:

```bash
timeout --signal=TERM --kill-after=90s 6h bash runner.sh
```

Always run cleanup.py and verify_source.py on completion or failure, preserve their output, and independently verify that the owned processes are terminal and the GPUs are idle. The guarded DEP8 NVFP4 run also samples GPU ownership continuously and stops its own watchdog on external GPU activity or observation failure.

Behavior-changing environment: Rust TreeCore, SGLANG_RUST_BUILD_MODE=auto, SGLANG_ENABLE_GLM_LOOP_FUSED_H64_DECODE=0, SGLANG_FLASHINFER_NVFP4_PER_TOKEN_ACTIVATION=1, CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7, OMP_NUM_THREADS=4, PYTHONNOUSERSITE=1, CARGO_BUILD_JOBS=4, SPT_NOENV=1, NCCL_SOCKET_IFNAME=eth0, GLOO_SOCKET_IFNAME=eth0, NCCL_DEBUG=WARN, explicit source/overlay PYTHONPATH and offline checkpoint loading. Simulation variables are absent.


## Commit

Runtime `52ef77912fd004f34cfe340b392018632ce69c2c`, clean candidate. All 12586 tracked source files verify before and after every run. Eight live workers per run map Rust extension SHA256 `2ef3093b301a9302ceb0ab0208d65ad27cece3220fb1591b16d7a8e47af4c64f`. Actual quantization is fp8 or modelopt_mixed according to the checkpoint.


## Scripts

The archives preserve execution scripts and complete raw outputs. Each paired-audit.json compares normalized actual service/evaluator commands, dependencies, source, draft and resolved settings. Source code is referenced by commit.

All cells use natural EAGLE steps/topk/draft tokens 3/1/4, FP8 draft quantization, TRTLLM MoE, separate shared experts, FP32 lm_head, eager prefill, decode CUDA graph, glm45/glm47 parsers, server seed 1 and maximum running requests 32. The three service configurations are:


| Configuration | EP / attention DP | KV / DSA | Context | Memory fraction | Effective chunk |
|---|---|---|---:|---:|---:|
| tp8-bf16 | 1 / 1 | bfloat16 / flashmla_sparse | 65536 | 0.75 | 32768 |
| tp8-fp8kv | 1 / 1 | fp8_e4m3 / trtllm | 65536 | 0.75 | 32768 |
| dep8 | 8 / 8 | fp8_e4m3 / trtllm | 147456 | 0.88 | 8192 |


DEP8 launches chunked-prefill-size 65536, resolved to 8192 per attention DP rank; its effective request limit is four per DP rank. Full actual commands are retained in results/<configuration>/argv.txt.


## Workload

Full GSM8K test split: 1319 unique examples per cell, one run, 64 threads, temperature 1.0, top_p 0.95, seed 1 and max_tokens 32768. The dataset checkout revision was not independently captured. Startup warmup precedes the evaluation-counter baseline. Runs span November 16–17 UTC; all timestamps are retained in the raw archives.

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:32190/v1 --temperature 1.0 --top-p 0.95 --seed 1 --num-threads 64 --max-tokens 32768 --out-dir eval-t1
```

Use the endpoint port recorded for the selected configuration. This is a correctness workload, not a throughput sweep.


## Results


| Configuration | Weights | Correct /1319 | Accuracy | Stop /1319 | Length | Errors | Natural tokens/verify |
|---|---|---:|---:|---:|---:|---:|---:|
| tp8-bf16 | FP8 | 1249 | 94.6929% | 1314 | 5 | 0 | 2.662511 |
| tp8-bf16 | NVFP4 | 1259 | 95.4511% | 1313 | 6 | 0 | 2.646300 |
| tp8-fp8kv | FP8 | 1255 | 95.1478% | 1316 | 3 | 0 | 2.662304 |
| tp8-fp8kv | NVFP4 | 1247 | 94.5413% | 1315 | 4 | 0 | 2.662983 |
| dep8 | FP8 | 1244 | 94.3139% | 1311 | 8 | 0 | 2.702652 |
| dep8 | NVFP4 | 1250 | 94.7688% | 1314 | 5 | 0 | 2.666662 |


All length-limited responses reach 32768 generated tokens and are incorrect; individual IDs are in audit.json. NVFP4 remains performance-only. Single paired runs do not establish quality parity, stopping nonregression or performance superiority. Final stopping acceptance, remaining features, bounded performance selection and image-level qualification remain open.

Every controlled cell has zero observed foreign GPU processes, zero measurement-time sampling errors, 1320 successful chat HTTP attempts and zero failed attempts. DEP8 NVFP4 has one failed nvidia-smi sample after evaluation ended, during explicit shutdown; the separate guard has 867 samples with no external process or stop event. All six drivers exit zero, cleanup lists are empty and independent terminal checks find eight idle GPUs. Sampling cannot rule out activity between observations.

Two earlier attempts are excluded from these controlled pairs: TP8 FP8-KV FP8 had external GPU interference during evaluation (raw archive SHA256 4ac918612372d5db1ad1ccccff05fe5369fbda10f569c75fb3938d71c85cf6d0); the first DEP8 NVFP4 startup was stopped after external GPU activity before evaluation began (archive SHA256 2261fa4dd1e07121b535d7410cf24e00e4bdbb0b368c214e93812022ffd7b28c). Both are preserved in private local records and are not included in this round's result table.


## Data and Figures


| Configuration | Weights | Raw files | GPU samples / ownership records | Archive SHA256 |
|---|---|---:|---:|---|
| tp8-bf16 | FP8 | 50 | 561 / 5065 | `f56ef1be5638cee1fa3301d7502b6fce9c1dfa96b96ecd51585159291d64d1fd` |
| tp8-bf16 | NVFP4 | 50 | 647 / 5730 | `44113391a117515d027e01ef122f469e5954d48d103bacf2b900d1386e8edfd6` |
| tp8-fp8kv | FP8 | 50 | 567 / 5127 | `78251cd85e6b1ccfecf739c38a679f920777512d3e56d7fd654e19fc1e5663e6` |
| tp8-fp8kv | NVFP4 | 50 | 628 / 5558 | `d69cbc6d79d8ab8375d5e96d1eb97031b3fe56bbd9a80b313bf71547aab24caa` |
| dep8 | FP8 | 50 | 933 / 8464 | `3d153f610869333074b845d3f0bd03a4a31a42598e9fb213e601e13308010204` |
| dep8 | NVFP4 | 55 | 766 / 6888 | `1d71c6bafdaacdc504a9cfb4ddf1bf0ff071936d3a0d63c3f33e3bec00a82701` |


files.json hashes every raw member. audit.json independently recounts predictions and reconciles counters, source, settings, GPU ownership and cleanup. startup-receipt.json binds actual live workers and evaluator commands; startup-audit.json records its verification. Three paired-audit.json files bind matched FP8/NVFP4 settings.
