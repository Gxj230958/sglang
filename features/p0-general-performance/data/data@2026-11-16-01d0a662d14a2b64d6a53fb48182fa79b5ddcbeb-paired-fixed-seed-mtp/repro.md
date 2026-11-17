# E08 Fixed-seed FP8/NVFP4 controlled MTP and MTP-off comparison

## Environment

Four NVIDIA GB300 GPUs, TP4, exclusively held rank. Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT providers 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1. Actual package paths, environment and resolved server settings are archived per launch. Container digest, topology and power mode were not captured; results are performance-only and non-release.

FP8 model revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, evaluated config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`. Preserve that evaluated configuration. NVFP4 model `RadixArk/GLM-5-1028-Provider-NVFP4-perf` at `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Both MTP formats use the original FP8 draft with explicit FP8 draft quantization. See the [immutable model handoff](../data@2026-11-16-3b6b0064d2e7743378191b5b906e8e1cea37319f-nvfp4-rust-baseline/private-release/2026-11-16-0952-xinyuan-3b6b0064d2-nvfp4-private-release.md).

## Commit

Exact runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`; all 12,581 source-manifest files match before and after execution. [Correctness E18](../../../p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-rust-current-head/repro.md) supplies the source reconstruction and full-quality evidence. Each of four workers maps Rust extension SHA256 `c933d62cbea75638fc7a1c4c1e114cac83fe7e149cfc65591492252ec5536055`. Runtime code remains local pending its stopping gate.

## Setup and scripts

Verify SHA256SUMS, then extract each archive into its own directory and verify its corresponding member manifest. The terminal archive contains all round-specific adapters, three configurations, phase reports, source-verification dependencies, input hashes and terminal receipts. Obtain the [frozen four-turn workload](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/workload.json.gz), decompress as workload.json, and verify SHA256 `235ea06164ba2a9f4700d5bee5ca12206a6ea21ed246ed64c8022b3bbb0d8688`. The publication terminal archive omits this already referenced dataset; archive-index.json records the original archive digest and omitted member digest. Every retained raw member is byte-identical.

Provision the recorded source, model revisions and packages on an exclusive four-GPU devbox. Adapt absolute source, model, overlay and output paths in the configurations and adapters. Preserve environment order, evaluated FP8 configuration and source checks. The archived serve_sweep.py has SHA256 `3a8aacff49a47a142cc5760f8437302d836881c0df9c3bba9abc83a499ba0eee`. From the extracted terminal directory run, in order:

```bash
python3 execute.py run --config natural-gate.json --run-dir gate
python3 execute.py run --config mtp-off.json --run-dir off
python3 execute.py run --config controlled35.json --run-dir controlled
```

Use a six-hour outer timeout with TERM and a 90-second KILL bound. Require all four natural gate candidates to pass before controlled simulation. The original start.sh additionally records predecessor-completion checks, idle/source checks and owned-process cleanup; adapt historical paths when reproducing. Each replica-0.process.json and client-command.json preserves actual argv/environment.

Common server settings: TRTLLM MoE, separate shared experts, window KV layout, context 32768, memory fraction 0.80, running/decode graph cap 64, chunk 8192, FP32 LM head, prefill graphs disabled, glm45/glm47 parsers and server random seed 1. BF16 KV uses FlashMLA sparse; FP8 E4M3 KV uses TRTLLM DSA. Natural and controlled MTP use EAGLE steps/topk/draft-tokens 3/1/4. Set NVFP4 per-token activation, PYTHONNOUSERSITE and Rust auto-build as recorded. Controlled simulation sets SGLANG_SIMULATE_ACC_LEN=3.5, SGLANG_SIMULATE_ACC_METHOD=match-expected and SGLANG_SIMULATE_ACC_TOKEN_MODE=real-draft-token. Natural and MTP-off environments contain no simulation settings.

## Workload and metrics

Twelve server starts: four natural sanity candidates at C1, four MTP-off candidates and four controlled candidates. Each full sweep uses C1/2/4/8/16/32, two repeats with request seeds 1/2, max(16, 2*C) conversations and four turns per conversation. Initial inputs are about 2.4K tokens; later turns resend generated history. Each turn requests 128 output tokens, temperature 1.0, top_p 0.95, thinking disabled and ignore EOS. Flush cache and run one warmup request before every measured load. Natural and MTP-off startups each have three separate natural-stop probes per candidate. Simulated outputs are excluded from correctness claims.

Score = (actual input + output tokens) / measured duration / 4 GPUs, including resent/cached inputs. Generated histories can change input totals despite the common workload and seeds. Tables use the median of two repeats. The frozen SLO is P90 TTFT <= 3 seconds, P90 interactivity >= 30 tokens/s, all requests successful and nonempty. MTP-off uses raw client ITL. MTP interactivity distributes each recorded stream interval over its runtime-tokenizer chunk count before taking token-weighted P90; it is not a physical per-token timestamp distribution. Raw stream-chunks.json, requests.jsonl and bench.jsonl support reconstruction.

Simulation 3.5 is an expected acceptance length sampled between 3 and 4, not an exact length for each verification. Server-reported acceptance and generation/verification counter deltas use distinct accounting. Counter deltas include one warmup request and are labeled accordingly; throughput excludes warmup. At C32, reported acceptance is 3.55/3.45 for repeats 1/2 in all four simulated cells. Counter deltas are 32896 generated tokens / 9252 and 9572 verification calls. Natural acceptance results remain in E07 and the separate low-load gate, not pooled with simulation.

## Results

All 100 loads complete: 4 natural gate loads with 256 successful requests, 48 MTP-off loads with 5,120 successful requests, and 48 controlled loads with 5,120 successful requests. Every measured request is nonempty with 128 output tokens. All 24 separate natural startup probes stop normally. All 24 aggregate points in each full sweep pass the SLO; the grid ends at C32, so capacity boundaries remain unmeasured.

| Mode | KV / attention deployment | FP8 C32 total tok/s/GPU | NVFP4 C32 total tok/s/GPU | NVFP4 gain |
|---|---|---:|---:|---:|
| MTP off | bf16 | 5115.698 | 6172.384 | +20.66% |
| MTP off | fp8kv | 5260.893 | 6264.449 | +19.08% |
| Simulated 3.5 | bf16 | 7689.495 | 9106.717 | +18.43% |
| Simulated 3.5 | fp8kv | 7890.887 | 9303.107 | +17.90% |

The controlled NVFP4 FP8-KV point scores highest among the measured cells, outside the BF16 deployment's 2% tie band. The two NVFP4 MTP-off KV deployments are within that tie band. KV comparisons also change the attention backend. Two repeats provide descriptive measurements, not statistical significance or proof of a quantization-only causal effect.

Correctness E18 reports FP8 1256 correct / 1316 stop and NVFP4 1243 correct / 1313 stop out of 1319. Full-GSM8K stopping nonregression remains unmet. Fixed-length loads, simulated acceptance and startup probes do not establish release qualification.

## Data and audit

Ten archives preserve raw gate, eight sweep cells and terminal evidence. archive-index.json gives archive hashes and member counts; each member manifest verifies raw bytes. Per-arm audits reconstruct request counts, output lengths, score, TTFT, interactivity, actual Rust mappings, resolved settings and ownership samples. Paired audits compare actual commands, versions, environments, seeds and workload. The original FP8 draft remains unchanged when normalizing target-model paths. Both tokenizers have identical tokenizer.json and tokenizer_config.json hashes, recorded in controlled35-bf16-paired-audit.json.

All observed GPU processes belong to the candidate. One NVFP4 FP8-KV MTP-off query error occurred after SIGTERM with no active loads and remains recorded. Sampling does not exclude activity between samples. Final cleanup has zero remaining owned processes, empty GPU process output and four GPUs at 0 MiB; final source verification passes. No completed load or request was discarded.
