# E04 FP8/NVFP4 Rust serving baseline

## Environment

- Hardware: 4× NVIDIA GB300 on one node; TP4, GPUs idle before each arm and after teardown.
- Container tag: `lmsysorg/sglang:latest`; image digest was not captured. This round is non-release.
- Imported PyTorch: `2.14.1+cu130`; FlashInfer `0.7.4`, with `flashinfer-cubin==0.7.4` and `flashinfer-jit-cache==0.7.4+cu130`, provider `sm103a`. Rust/cargo `1.92.0`.
- FP8 source weights: private `RadixArk/GLM-5-1028-Provider` revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`. Local configuration and tokenizer SHA256 values are in `conversion-manifest.json` inside the archive.
- NVFP4: performance-only conversion of the source routed experts in physical layers 3–77. The private checkpoint upload and immutable release verification are in progress; publication is not established by this round.

## Setup

Extract [evidence.tar.gz](evidence.tar.gz) into an empty directory and verify `sha256sum -c SHA256SUMS` there. Paths below refer to that extracted directory.

Provision the FP8 source and converted checkpoint under the paths in `runner.py`. Preserve the configuration/tokenizer hashes in `conversion-manifest.json`. The converter and tensor audit are included as `convert.py`, `_common.py` and `audit.py`; `conversion-command.json` records the exact invocation. Conversion used NVIDIA Model Optimizer `43fd41a58d52c4e6e5dec1d1ff5989ecc737ae1a` (v0.46.0), group size 16, absmax rounding, shared gate/up global scales and dynamic per-token activation quantization. The 142 source weight shards matched their provider hashes. MTP and vision tensors were byte-preserved.

Use the recorded SGLang source revision and place its Python and Rust sources at the paths in `runner.py`. The mapping patch is required: mixed-precision quantization entries must expand into the 106 execution slots. `mapping-check.json` verifies all 103 sparse slots and preservation of the original quantization config. Runtime source publication accompanies the checkpoint handoff; a current-head integration is a separate validation target.

Install the FlashInfer packages above into the isolated overlay; cubins use `https://flashinfer.ai/whl/`, and the JIT provider uses `https://flashinfer.ai/whl/cu130/`. Preserve the remaining dependency overlays from the launch metadata. `runtime-import.log` records the selected package paths. The complete original image/dependency lock remains a release prerequisite.

Build/load Rust on the devbox using `run-rust-build.py`. Run `runner.py --job sanity --attempt rust1`, then `--job nvfp4-mtp`, `fp8-mtp`, `nvfp4-off`, and `fp8-off`, each with `--attempt rust1`. The driver requires completed checkpoint-audit and Rust-build statuses. It creates fresh result directories, rejects occupied GPUs, checks Rust selection, executes the workload and stops its owned server. Use a devbox lock and a bounded outer driver. Exact server commands and behavior-changing environment variables are in each `runs/*-rust1/launch.json`; exact client commands are the `bench-*-command.json` files.

## Commit

- Code: `3b6b0064d2e7743378191b5b906e8e1cea37319f`, based on `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`.
- Deployment verification: 6,607 Python-package files matched the code commit; the pinned Rust source was separately deployed and built.
- All four TP ranks in every final arm logged `RustUnifiedTreeCore`. Both weight formats used the same revision and dependency paths.

## Scripts

Round-specific commands and drivers are in the evidence archive. The measured source is unchanged between arms. The final comparison selects only the `*-rust1` runs; historical attempts remain in the capture with their recorded backend/status.

## Workload

- Native serving benchmark: random token IDs, `--tokenize-prompt`, fixed lengths, range ratio 1, cache flush and two warmup requests.
- Seeds 1 and 2. At 2000 input / 500 output tokens: C1 uses 16 requests, C8 uses 32, C32 uses 128. At 30000 / 300, C4 uses 16 requests. All requested input/output token totals and successful request counts matched exactly.
- Both arms: TP4, FlashInfer TRTLLM MoE, separate shared experts, FlashMLA sparse DSA, BF16 KV, static memory fraction 0.80, context 32768, chunked prefill 8192, maximum running/decode-graph batch 64, FP32 LM head and disabled prefill CUDA graphs.
- MTP: EAGLE 3/1/4, original FP8 source as draft with explicit FP8 draft quantization. Simulated acceptance 3.5 uses `match-expected` and `real-draft-token`. Realized acceptance matched exactly between formats for each seed. MTP-off clears all simulation variables.
- One sequential server launch per arm; two client seeds per point. Startup/compilation/autotuning are outside benchmark timing. These are controlled runtime measurements, not natural-acceptance results or a confidence interval.

## Results

Aggregate server output tokens/s, arithmetic mean of two seeds:

| Mode | Input/output | Concurrency | FP8 | NVFP4 | NVFP4 gain |
|---|---:|---:|---:|---:|---:|
| MTP 3.5 | 2000/500 | 1 | 206.97 | 225.46 | 8.93% |
| MTP 3.5 | 2000/500 | 8 | 803.18 | 962.55 | 19.84% |
| MTP 3.5 | 2000/500 | 32 | 1585.28 | 1946.49 | 22.79% |
| MTP 3.5 | 30000/300 | 4 | 121.41 | 143.11 | 17.87% |
| MTP off | 2000/500 | 1 | 92.91 | 97.20 | 4.62% |
| MTP off | 2000/500 | 32 | 876.36 | 1089.12 | 24.28% |

At the same memory fraction, MTP target weight memory was 176.15 GiB/GPU for FP8 and 102.28 GiB/GPU for NVFP4; full KV capacity was 441,664 and 1,257,152 tokens respectively. This comparison keeps allocation policy fixed and allows the reduced weight footprint to enlarge the KV pool.

NVFP4 Rust sanity: three sensible chat replies stopped normally; GSM8K100 at temperature 1.0, top-p 0.95, seed 1, max8192 and 16 threads scored 96%, with 99% stop and zero errors. One response reached the token limit. This is non-gating sanity for a performance-only artifact and does not establish quality parity or production readiness.

## Data and Figures

- [evidence.tar.gz](evidence.tar.gz): raw benchmark JSONL including request details, exact commands, resolved server information, server logs, GPU snapshots, conversion audit and round drivers. Measurements retain their original bytes.
- [audit.json](audit.json): independent checks and recomputed means for all 24 points. Checks cover artifact hashes, exact revision, four Rust ranks, workload/token totals, paired commands/environments, simulation settings and per-seed realized acceptance.
- [evidence-selection.json](evidence-selection.json): capture provenance and export selection. The archive has its own `SHA256SUMS`; `capture-SHA256SUMS` identifies the original capture.

Private checkpoint publication, a locked image/environment, full correctness gates and current-head validation remain pending. Deployment selection also requires the subsequent matched NVFP4 sweeps.
