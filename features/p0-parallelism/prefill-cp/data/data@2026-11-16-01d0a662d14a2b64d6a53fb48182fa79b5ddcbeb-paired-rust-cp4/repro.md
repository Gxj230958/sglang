# E04 Paired FP8 and NVFP4 Rust CP4 validation

## Environment

Four NVIDIA GB300 GPUs on one exclusively held devbox rank. Container digest, interconnect topology and power mode were not captured for this round. Both formats use the same source and dependency overlay: Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT and sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, and sgl-eval 0.1.3. Each server-imports.json preserves the actual import paths and installed distributions.

FP8 provider revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` uses evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. Preserve that evaluated configuration when reproducing. The performance-only `RadixArk/GLM-5-1028-Provider-NVFP4-perf` checkpoint is pinned to `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both use the original FP8 NextN draft with explicit FP8 draft quantization. Preparation rehashed all 142 FP8 weight shards (756945709348 bytes), 163 NVFP4 files (439756337764 bytes), and the evaluated FP8 metadata. The complete preparation receipt is in the FP8 archive.

## Commit and setup

Exact runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`, from a clean validation worktree. All 12,581 source-manifest files matched at launch; a fresh post-evaluation check also matched before the next workload. The Rust extension was built on the devbox and mapped by all four ranks in each launch, SHA256 `d2547a9f9a3edc3f79318922dfd2aceb162c0339c9c00d69514e00aafb979cc3`.

Verify SHA256SUMS and extract each evidence archive into a separate directory. Verify extracted bytes using its files.json. Obtain the exact runtime source, install the recorded dependency versions, and provision the pinned checkpoints. The FP8 archive contains source-manifest.json, prepare.py, verify_source.py and plan.json; adapt its absolute source, model, evaluator and cache paths to the exclusively held devbox. Run the preparation and review its status before running the bounded start.sh. Each results directory preserves launch.json, server imports, resolved server info, raw probes, evaluator command and predictions. These are one-round reproduction inputs, not a reusable package installer.

Common launch settings: TP4, interleaved prefill CP4, window KV layout, BF16 KV, FlashMLA sparse DSA, TRTLLM MoE, separate shared experts, context 131072, memory fraction 0.80, maximum running requests/decode graph batch 64, chunk 8192, FP32 LM head, breakable prefill graphs, natural EAGLE 3/1/4, server seed 1. Logs contain actual prefill graph execution. Both source and package versions match. Launch flag differences are model path and service/rendezvous ports; the environment differs only in the process ownership label. Full arguments and comparison are retained in paired-audit.json.

The original combined driver completed FP8 and then failed the port-bind precheck before starting NVFP4. Its raw failure remains in the FP8 archive. NVFP4 retrieval ran independently on ports 31982/31983. After its failed retrieval gate, the remaining prefix and full GSM8K measurements ran on ports 31984/31985, preserving prior_retrieval_gate=failed. This continuation completes measurements and does not convert the failed retrieval gate into a pass.

## Workload

The deterministic retrieval probe generates eighteen requests across prompt lengths through 120936 tokens, including cold and cached long-context requests. Temperature 0, thinking disabled, max 96 output tokens; probe.py and raw retrieval.json preserve the generated targets, expected answers and responses. The six prefix-fork requests require exact answers and natural stops; cache counts are 0, 6656, 6656, 0, 6656, 6656 for both formats.

Each format runs all 1319 GSM8K examples through sgl-eval 0.1.3 with temperature 1.0, top_p 0.95, seed 1, 64 threads and max 32768 output tokens. Exact commands and complete generation parameters are in gsm8k-command.json and metrics.json. These are correctness workloads; natural acceptance ratios do not constitute a throughput benchmark.

## Results

| Metric | FP8 | NVFP4 |
|---|---:|---:|
| Correct / 1319 | 1238 | 1250 |
| Accuracy | 93.8590% | 94.7688% |
| Stop / 1319 | 1313 | 1315 |
| Stop rate | 99.5451% | 99.6967% |
| Length / errors | 6 / 0 | 4 / 0 |
| Retrieval exact answer and stop | 18/18 | 17/18 |
| Prefix exact answer and stop | 6/6 | 6/6 |
| Generated / verify counter delta | 847431 / 318684 | 687414 / 260863 |
| Natural acceptance ratio | 2.659158 | 2.635153 |

NVFP4 has observed accuracy +0.909780 percentage points and stop rate +0.151630 points against the matched FP8 CP4 run. Both are single runs; this does not establish a causal Rust effect or satisfy the outstanding runtime release gate. Neither reaches 100% stopping.

The NVFP4 retrieval failure is a cold 120935-token request targeting record 1208, expected 797221. It emits reasoning despite the thinking-off request, reaches 96 completion tokens and returns empty final content with finish_reason=length. The other 17 probes pass, including two cached 120936-token cases. FP8 passes the same eighteen targets. This CP4 feature gate remains unmet.

FP8 GSM8K length IDs: 87, 241, 255, 369, 380, 1176. NVFP4 length IDs: 505, 534, 515, 1303. All ten reach 32768 generated tokens and are marked incorrect. No request was discarded. Token sums equal generation counter deltas in both full runs.

## Data and audit

- fp8-evidence.tar.gz: 63 files, full FP8 run, preparation and original driver failure. fp8-audit.json independently recounts all 1319 predictions, counters, Rust maps and resolved flags.
- nvfp4-retrieval-evidence.tar.gz: 40 files, failed retrieval round and owned cleanup. nvfp4-retrieval-audit.json preserves the failing response and cross-format target checks.
- nvfp4-full-evidence.tar.gz: 47 files, remaining prefix/full GSM8K run and owned cleanup. nvfp4-full-audit.json independently recounts all 1319 predictions.
- paired-audit.json: exact launch/environment comparison and observed deltas.
- The three files.json manifests bind all 150 raw files. SHA256SUMS binds archives and audits.

All observed GPU processes were owned. The FP8 run has 687 ownership samples and one GPU-memory query failure 0.410 seconds after the last generation; NVFP4 full has 482 samples and no query errors. Sampling cannot exclude activity between samples. All server groups were gone and all four GPUs reported 0 MiB before the next workload. CP with HiCache, TRTLLM DSA, and disaggregated prefill remain separate validation requirements.
