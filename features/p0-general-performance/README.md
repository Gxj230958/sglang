# General Performance

## Summary

`zai-org/GLM-5-1028-Provider` general-performance tracking measures controlled one-batch efficiency and online-serving behavior across representative workloads and platforms. Status: In progress. [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) compares native head64 with small-head sparse prefill on 8×B300. Cap-64 8K TTFT decreased by 4.31% on average, while throughput changed by +0.42%; a single 100K run gained 3.01% throughput. The result is non-release because it predates the PR rebase and uses an unpinned configuration compatibility file. The original PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891). [E02](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md) measures long-context decode on 2×4 Vera Rubin GPUs at TP8: the FlashInfer TRT-LLM MoE runner, which plain TP selects when `--moe-runner-backend` is unset, decodes 36% faster than an explicit DeepGEMM runner at batch 1 and 22% faster at batch 8 with 131072 input tokens, with equal GSM8K accuracy; the result is non-release. Release goals and required platforms remain `<PERFORMANCE_GOAL>` under `<SERVICE_LEVEL_OBJECTIVE>`.

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

## Performance Results

| Date | Configuration | Workload | Result | Evidence |
|---|---|---|---|---|
| 2026-11-06 | Native head64 vs small-head sparse prefill; 8×B300 TP8; BF16 KV; FlashMLA 1.0.3 | RANDOM-8K-1K | +0.42% mean cap-64 throughput; 4.31% lower mean median TTFT | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| 2026-11-06 | Same paired methodology | RANDOM-100K-2K | +3.01% throughput; 2.81% lower TTFT in one run | [E01](data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) |
| 2026-11-11 | DeepGEMM vs FlashInfer TRT-LLM MoE runner; 2×4 Vera Rubin TP8; BF16 KV; MTP 3/1/4 | RANDOM-128K-512 | Batch 1: 190.6 → 259.2 output tokens/s (+36%); batch 8: 940.3 → 1145.6 (+22%) | [E02](data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md) |

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
