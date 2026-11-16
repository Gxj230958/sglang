# General Performance

## Summary

`zai-org/GLM-5-1028-Provider` general-performance tracking measures controlled one-batch efficiency and online-serving behavior across representative workloads and platforms. Status: In progress. [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) compares native head64 with small-head sparse prefill on 8×B300. Cap-64 8K TTFT decreased by 4.31% on average, while throughput changed by +0.42%; a single 100K run gained 3.01% throughput. The result is non-release because it predates the PR rebase and uses an unpinned configuration compatibility file. The original PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891). [E02](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md) measures long-context decode on 2×4 Vera Rubin GPUs at TP8: the FlashInfer TRT-LLM MoE runner, which plain TP selects when `--moe-runner-backend` is unset, decodes 36% faster than an explicit DeepGEMM runner at batch 1 and 22% faster at batch 8 with 131072 input tokens, with equal GSM8K accuracy; the result is non-release. [E03](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md) sweeps eight serving configurations on 4× GB300 with a four-turn chat workload at concurrency 1 to 8: TP4 with BF16 KV and MTP off scores highest at concurrency 8 (2060.1 total tokens/s per GPU, 283.7 output tokens/s), MTP raises output throughput at concurrency 1 and lowers it at concurrency 8, and TP4 is ahead of DEP4 at equal settings; the sweep ran on FlashInfer 0.7.3 with one launch per configuration and is non-release. Release goals and required platforms remain `<PERFORMANCE_GOAL>` under `<SERVICE_LEVEL_OBJECTIVE>`.

## Scope

### In Scope

- Prefill and decode one-batch measurements.
- Online latency, throughput, concurrency scaling, and request failures.
- Memory capacity and scheduling behavior.
- Representative parallelism and backend configurations.
- Baseline comparison and release-candidate regression gates.

### Out of Scope

- Agentic-trace replay owned by `p0-agentx-performance`.
- Kernel-only microbenchmarks without end-to-end attribution.
- Results that do not pass the required correctness gate.
- Release claims based on the unpinned compatibility configuration or an unmerged upstream implementation.

## Success Criteria

- [x] E01 baseline and candidate use identical model, source, wheel, workload, and measurement procedure.
- [ ] Required workload and platform cells meet `<PERFORMANCE_GATE>`.
- [ ] Release profiles satisfy `<TTFT_GATE>`, `<ITL_GATE>`, and `<ERROR_RATE_GATE>`.
- [ ] Capacity limits and out-of-memory boundaries are documented.
- [x] Every E01 number links to raw evidence and an exact measured code revision.
- [ ] Repeat the 100K comparison and rerun the locked upstream release candidate.

## Workload Matrix

| Workload ID | Input Shape | Output Shape | Request Distribution | Batch or Concurrency | Sampling | Purpose | Status |
|---|---|---|---|---|---|---|---|
| RANDOM-8K-1K | 8192 tokens | 1024 tokens | Random IDs, seeds 42/43 | Caps 1 and 64 | Temperature 0; ignore EOS | Small-head serving A/B | Measured on B300; non-release |
| RANDOM-100K-2K | 102400 tokens | 2048 tokens | Random IDs, seed 42 | Cap 64; KV-resident limited | Temperature 0; ignore EOS | Long-context prefill A/B | One run; repetition required |
| RANDOM-128K-512 | 131072 tokens | 512 tokens | Random prompts of `one_batch_server` | Batch 1 and 8 | Benchmark defaults; simulated MTP acceptance 2.5 | Long-context decode, MoE runner A/B | Measured on Vera Rubin; non-release |
| CHAT-4TURN-128 | 2,427 tokens on turn 1, about 640 new tokens per later turn, up to about 4,754 on turn 4; full history resent | 128 tokens per turn | Synthetic service-debugging chat, 16 conversations × 4 turns, request seeds 1/2 | Closed loop, concurrency 1, 2, 4, 8 | Temperature 1.0, top_p 0.95; thinking off; ignore EOS | Serving-configuration sweep under a TTFT and interactivity SLO | Measured on GB300; non-release |

## Performance Results

| Date | Configuration | Workload | Result | Evidence |
|---|---|---|---|---|
| 2026-11-06 | Native head64 vs small-head sparse prefill; 8×B300 TP8; BF16 KV; FlashMLA 1.0.3 | RANDOM-8K-1K | +0.42% mean cap-64 throughput; 4.31% lower mean median TTFT | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| 2026-11-06 | Same paired methodology | RANDOM-100K-2K | +3.01% throughput; 2.81% lower TTFT in one run | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| 2026-11-11 | DeepGEMM vs FlashInfer TRT-LLM MoE runner; 2×4 Vera Rubin TP8; BF16 KV; MTP 3/1/4 | RANDOM-128K-512 | Batch 1: 190.6 → 259.2 output tokens/s (+36%); batch 8: 940.3 → 1145.6 (+22%) | [E02](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md) |
| 2026-11-15 | Window KV layout (default of pull request 67) vs full-length layout; 8×B300; DEP8 `trtllm` FP8 and TP8 BF16; MTP 3/1/4 | Random IDs 2000 / 500 at caps 1 and 32, 30000 / 300 at cap 4, seeds 1/2; 8-turn chat | No difference attributable to the layout: DEP8 cap-32 1061 vs 1077 output tokens/s, TP8 cap-32 1171 vs 1175; multi-turn median TTFT within 10 ms | [Correctness E14](../p0-correctness/data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md) |
| 2026-11-16 | Eight configurations on 4×GB300: TP4 and DEP4, BF16 and FP8 KV, `flashmla_sparse` and `trtllm` DSA routes, MTP on and off, window and full-length layout; FlashInfer 0.7.3 | CHAT-4TURN-128 | Highest passing score: TP4 BF16 MTP off at concurrency 8, 2060.1 total tokens/s per GPU, 283.7 output tokens/s, P90 TTFT 0.913 s, P90 interactivity 43.1 tokens/s; DEP4 FP8 MTP off 1735.4; MTP configurations pass up to concurrency 4 (1050.1–1390.3) | [E03](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md) |
| 2026-11-16 | TP8 `trtllm` FP8 KV vs TP8 `flashmla_sparse` BF16 KV; 8×B300; MTP 3/1/4; FlashInfer 0.7.4 | Random IDs 2000 / 500 at caps 1 and 32, 30000 / 300 at cap 4, seeds 1/2 | Output tokens/s FP8 / BF16: 211.3–220.3 / 231.8–234.7 at cap 1, 1203.8–1215.2 / 1125.4–1193.5 at cap 32, 144.2–145.2 / 127.6–128.9 at 30K; 2,321,664 against 1,195,520 full-length KV tokens | [Correctness E17](../p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv/repro.md) |

## Release Profiles

| Profile | Target User | Hardware | Configuration | Workload Envelope | Expected SLO | Evidence | Status |
|---|---|---|---|---|---|---|---|
| `<PROFILE>` | `<USER_SCENARIO>` | `<HARDWARE>` | `<CONFIGURATION>` | `<ENVELOPE>` | `<SLO>` | `<ROUND_PATH>` | `<STATUS>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Freeze methodology and baseline — In progress

- [x] Pin E01 workloads, metrics, cache flushing, prompt hashes, and native-wheel baseline; completed 2026-11-06.
- [x] Measure native head64 and small-head sparse prefill on B300; completed 2026-11-06.
- [ ] Repeat the 100K case and establish variance across additional independent rounds.
- [ ] Measure `<REFERENCE_IMPLEMENTATION>` on the remaining required platforms and record capacity boundaries.

### Stage 2: Optimize release profiles — In progress

- [x] Attribute the E01 change to the small-head prefill path with kernel dispatch evidence; completed 2026-11-06.
- [ ] Rerun [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891) at its locked merge candidate.
- Decision: for plain TP leave `--moe-runner-backend` unset, which resolves to `flashinfer_trtllm` on SM100-class devices, instead of passing `deep_gemm`; keep DeepGEMM for DeepEP layouts. Measured on Vera Rubin only.
- Experiment [E02](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md): the TRT-LLM runner decodes 36% (batch 1) and 22% (batch 8) faster than DeepGEMM at 131072 input tokens, with GSM8K at 93.1% against 92.3–92.6%.
- [ ] Repeat the MoE runner comparison on B300 and above 8 concurrent requests, where one GSM8K run finished 4–7% later with TRT-LLM.
- Reference: [Kernel Optimization E03](../p0-kernel-opt/data/data@2026-11-12-6ed895fa2678d8c4d52576e7ae5e3707ee4180e7-topk-by-reference-b300/repro.md) holds a B300 serving A/B at `710bcb2a` (TP8: about 619 tok/s at 2000 input / 256 output tokens and concurrency 16; DEP8: about 531 tok/s) taken to compare a loop-state memory change. It is not a baseline round: three rounds, one seed each, unlocked environment.
- Experiment [E03](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md): on 4× GB300 with CHAT-4TURN-128, TP4 with BF16 KV and MTP off scores highest at concurrency 8 (2060.1 total tokens/s per GPU) and still passes the SLO there; every MTP configuration passes up to concurrency 4 and fails the 30 tokens/s interactivity gate at 8; TP4 is ahead of DEP4 at equal settings; the window and full-length layouts score within 4.4%. FlashInfer 0.7.3, one launch per configuration, no accuracy evaluation. [Event record](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/2026-11-16-0735-xinyuan-dbfef91e7d-gb300-serve-sweep.md).
- Reference: [Correctness E17](../p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv/repro.md) compares TP8 with FP8 KV on the `trtllm` DSA routes against TP8 with BF16 KV on B300: 6–9% lower output throughput at concurrency 1, 2–7% higher at concurrency 32, 13% higher on 30K-token inputs, and 1.94× the full-length KV tokens, in one launch per arm.
- [ ] Repeat the MTP on / off comparison above concurrency 4 on B300 and with longer outputs and thinking enabled; extend the GB300 grid above concurrency 8.
- [ ] Select profiles that satisfy correctness and service-level gates.

### Stage 3: Revalidate locked artifacts — Not started

- [ ] Rerun the required matrix on `<CODE_SHA>` and `<MODEL_REVISION>`.
- [ ] Confirm no release profile depends on an unpinned component.
- [ ] Publish reviewed profiles to the delivery cookbook.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-06 | Small-head sparse-prefill serving | 8×B300 TP8; random IDs; 8K/1K and 100K/2K | Cap-64 8K TTFT −4.31%; throughput +0.42%; 100K throughput +3.01% in one run | [round](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| E02 | 2026-11-11 | MoE runner backend for long-context decode | 2×4 Vera Rubin TP8; 131072 in / 512 out; batch 1 and 8 | TRT-LLM vs DeepGEMM: +36% batch 1, +22% batch 8; GSM8K equal | [round](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md) |
| E03 | 2026-11-16 | GB300 serving-configuration sweep | 4×GB300; eight TP4 / DEP4 configurations; four-turn chat, 128 output tokens per turn; concurrency 1–8; FlashInfer 0.7.3 | TP4 BF16 MTP off highest at concurrency 8: 2060.1 total tokens/s per GPU; MTP configurations pass up to concurrency 4; non-release | [round](data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md) |
