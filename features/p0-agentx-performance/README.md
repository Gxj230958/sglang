# AgentX Performance

## Summary

`zai-org/GLM-5-1028-Provider` AgentX performance tracking replays representative agentic workloads to measure user-visible latency, throughput, concurrency scaling, prefix reuse, and cache behavior. Status: In progress. [E05](data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md) replays `semianalysisai/cc-traces-weka-062126` against a 1P1D deployment on 2×4 GB300, with and without HiSparse on the decode server. When decode is saturated, HiSparse raises decode output throughput by 67–78%, at about twice the ITL. End to end, it adds 10–19% total throughput, bounded by the single prefill server. The [HiSparse decode](#hisparse-decode) entry under Tuning says when to enable it. The target envelope is `<TARGET_ENVELOPE>` under `<SERVICE_LEVEL_OBJECTIVE>`. Related code work is `<CODE_BRANCH_OR_PR>`, with dependencies on `<TRACE_SOURCE>`, `<CACHE_CONFIGURATION>`, and `<GENERAL_PERFORMANCE_BASELINE>`.

## Scope

### In Scope

- Versioned agentic traces or a reproducible synthetic equivalent.
- Single-user latency and multi-user concurrency sweeps.
- Time to first token, inter-token latency, request duration, and throughput.
- Prefix-cache hit behavior, reuse distance, and memory pressure.
- Failure, timeout, cancellation, and retry behavior.

### Out of Scope

- Generic one-batch or serving workloads owned by `p0-general-performance`.
- Agent quality evaluation unrelated to serving behavior.
- Tool-call format correctness and parser validation, owned by `features/p0-tool-call-parser/`; agentic results here assume its serving gates have passed.
- Private trace payloads that cannot be safely committed or reproduced.

## Success Criteria

- [ ] The trace source is pinned, sanitized, and reproducible.
- [ ] The release profile satisfies `<LATENCY_GATE>` across `<CONCURRENCY_RANGE>`.
- [ ] Throughput and cache behavior meet `<THROUGHPUT_GATE>` and `<CACHE_GATE>`.
- [ ] Failure and timeout rates stay below `<RELIABILITY_GATE>`.
- [ ] The recommended operating envelope includes capacity boundaries.
- [ ] Every result is pinned to code, model, hardware, and trace revisions.

## Workload Profile

| Trace ID | Source Revision | Requests | Input Distribution | Output Distribution | Prefix Reuse | Tool Pattern | Status |
|---|---|---:|---|---|---|---|---|
| `<TRACE_ID>` | `<TRACE_REVISION>` | `<REQUEST_COUNT>` | `<INPUT_DISTRIBUTION>` | `<OUTPUT_DISTRIBUTION>` | `<REUSE_PROFILE>` | `<TOOL_PATTERN>` | `<STATUS>` |
| `semianalysisai/cc-traces-weka-062126` (AgentX harness 1.0.14, closed loop, 900 s windows) | `23f152f6` | Replayed by concurrency, not a fixed count | Up to 147,456 tokens of context; long multi-turn prefixes | Trace-native, or forced to 4,096 tokens for decode saturation | 53–87% prompt-cache read at c16–c32 in E05 | Claude Code sessions | Used in E05 |

## Concurrency Envelope

No concurrency results recorded yet.

## Recommended Operating Envelope

| Profile | Concurrency Range | Hardware | Configuration | SLO | Capacity Boundary | Evidence | Status |
|---|---|---|---|---|---|---|---|
| `<PROFILE>` | `<MIN>-<MAX>` | `<HARDWARE>` | `<CONFIGURATION>` | `<SLO>` | `<BOUNDARY>` | `<ROUND_PATH>` | `<STATUS>` |
| KV-bound PD decode with HiSparse | 16–48 conversations per decode server | 2×4 GB300; 1P (TP4, Mooncake-store linker) + 1D (DPA4 + EP4 + MTP) | BF16 KV, `flashmla_sparse`; decode adds `--enable-hisparse --hisparse-config '{"top_k":2048,"device_buffer_size":4096,"host_to_device_ratio":6}'` | Throughput first; ITL p90 of 35–54 ms is acceptable | The decode saturates at about 9 running per rank (c48, 788 output tok/s). The prefill binds from c32 on (prefill concurrency about 17) | [E05](data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md), [Correctness E29](../p0-correctness/data/data@2026-11-16-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md) | Non-release |

## Tuning

Knobs a deployment sets for AgentX, each with the sign that says it matters.

### HiSparse decode

**Knob:** `--enable-hisparse --hisparse-config '{"top_k":2048,"device_buffer_size":4096,"host_to_device_ratio":R}'` on a PD decode server.

**What it does:**
- The full-attention KV of every request lives in host memory: R logical ids per device row, as host shared memory.
- Each running request keeps a device buffer of 8,256 rows per rank, and each step swaps in the Top-K rows it reads.
- The window sub-pool stays on the GPU.
- Requires the change of `radixark/sglang-zai` pull request 84 (evaluated as `76e1c381`, branch `hisparse-window-subpool-eval`).
- Without the request-capacity part of that change, the decode server rejects prompts longer than its device rows, or gives them zero new tokens. This happened in E05's invalidated runs.

**Sign** that it pays: the decode is KV-bound.
- The decode log shows `#prealloc-req` well above `#running-req` on every rank, with `full token usage` near its ceiling.
- TTFT grows from queueing at the decode server while the prefill is not saturated.
- Measured on 2026-11-17 in E05 (DPA4 decode, 208,256 rows per rank), at c48 with 4,096 output tokens per turn:
  - each rank ran 2.5 requests with 15.8 waiting in pre-allocation;
  - full-KV usage was 0.79;
  - TTFT p50 was 219 s.

**Measured** in E05 on 2×4 GB300 (1P TP4 + 1D DPA4 + EP4 + MTP, BF16 KV), one 900 s window per point. All results are non-release; ratio 6 unless noted.

| Point | Baseline | HiSparse |
|---|---|---|
| Decode saturation, c48, OSL 4096: output tok/s | 471 | 788 (+67%); ratio 12: 837 (+78%) |
| The same: AIPerf decode concurrency | 9.8 | 33.2 |
| The same: ITL p50 / p90 | 20.5 / 27.1 ms | 41.3 / 53.8 ms |
| The same: per-user tok/s p50 | 48.8 | 24.2 |
| The same: TTFT p50 | 219 s | 46 s |
| Same batch, c8, OSL 4096: ITL p50 | 15.5 ms | 20.9 ms (+35%) |
| The same: output tok/s | 335 | 277 (−17%) |
| Same batch, c4: ITL p50 | 13.7 ms | 15.3 ms (+12%) |
| The same: output tok/s | 172 | 159 (−8%) |
| Native trace, c16: requests | 330 | 401 (+21.5%) |
| The same: total tok/s | 27.8K | 33.0K (+18.6%) |
| The same: TTFT p50 | 3.5 s | 1.3 s |
| Native trace, c32: total tok/s | 23.7K | 26.1K (+10.3%) |

- Accuracy in Correctness E29 at ratio 6 through the same PD deployment: GSM8K 96.00 / 94.00, GPQA diamond 69.95 / 72.47, RULER2 32K 91.14 / 90.58, with 0 errors.
- Open observation: RULER2 `mv_niah_hard` was 10.1 points lower (one run per arm, 100 examples per task).

**Tune:**
- **Enable it** on a decode server that shows the Sign, when throughput per GPU matters more than per-user speed.
- **Leave it off** when the decode is not KV-bound. At the same batch it is 8–17% slower.
- **ITL SLO:** with an ITL p90 target below about 30 ms, HiSparse met it only at c8 and below in E05, where it was slower than the baseline. Cap `--max-running-requests` on the decode and check the result at that SLO before enabling it. That throughput-against-ITL curve has not been measured yet.
- **R = 6** is the measured choice.
  - Logical ids are R × device rows. The device rows shrink as R grows, because the index keys and the draft pool are sized per logical id: 122,752 rows at R = 6, 85,440 at R = 12.
  - The running batch per rank is bounded by both the logical ids and device rows / 8,256: about 14.9 at R = 6, 10.3 at R = 12.
  - At R = 6 the logical side bound first (host usage 0.81, device 0.61). At R = 12 the device side bound (device 0.81, host 0.55).
  - R = 12 was +6% over R = 6 in single runs, inside unmeasured noise. A higher R lowers the device bound further.
- **Host memory:** budget about 100 KB of host shared memory per logical id. That is 382.5 GiB on the decode node at R = 12 (4 × 1,025,280 ids), against 955 GiB per node.
- **Prefill capacity:** size it with the decode. In E05 the single TP4 prefill bound from c32 on, so the end-to-end gain was +10% at c32 against +19% at c16.

**Trap:**
- **PD timeouts:** at decode saturation, requests wait at the decode server for longer than the 300 s defaults of `SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT` and `SGLANG_DISAGGREGATION_WAITING_TIMEOUT`.
  - They then fail with a 500 and open the router's circuit: 503 for every request.
  - E05 sets both to 3600 so that queueing shows as TTFT.
  - The baseline GPQA run of Correctness E29 at 128 client threads lost 8.84% of requests this way.
- **Empty warmup replies:** the AgentX client's one-token warmup can return only `</think>`, which the `glm45` reasoning parser removes. The client then reads the reply as empty.
  - Send `separate_reasoning: false` in `--extra-inputs`.

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Establish trace and baseline — Not started

- [ ] Pin and sanitize `<TRACE_SOURCE>`.
- [ ] Define latency, throughput, cache, and reliability metrics.
- [ ] Run the baseline concurrency sweep.
- Next action: select and pin a sanitized agentic trace source; start the baseline sweep after the general-performance baseline exists.

### Stage 2: Map the operating envelope — In progress

- Experiment [E05](data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md): HiSparse on the PD decode raises saturated decode output throughput by 67% (ratio 6) and 78% (ratio 12), adds 12–35% ITL at the same batch, and adds 18.6% total throughput end to end at c16 and 10.3% at c32.
- [ ] Map HiSparse decode output throughput against ITL p90 with a `--max-running-requests` sweep (`alphabetc1`).
- [ ] Sweep `<CONFIGURATION_SET>` across `<CONCURRENCY_RANGE>`.
- [ ] Attribute cache, scheduler, and memory-pressure transitions.
- [ ] Identify recommended and unsafe operating bands.

### Stage 3: Certify release behavior — Not started

- [ ] Rerun the selected envelope on locked artifacts.
- [ ] Confirm trace privacy and reproducibility requirements.
- [ ] Publish reviewed guidance to the delivery cookbook.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E05 | `2026-11-17` | HiSparse decode under PD: decode saturation, same-batch cost and end-to-end gain | `76e1c381`; 2×4 GB300; 1P TP4 with Mooncake-store linker + 1D DPA4 + EP4 + MTP; BF16 KV; HiSparse ratio 6 and 12; AgentX trace, native and 4,096-token output, c4–c64 | Saturated decode output 471 → 788 (ratio 6) / 837 (ratio 12) tok/s; same-batch ITL +12% to +35%; end to end +18.6% total tok/s at c16, +10.3% at c32; 0 errors. Non-release | [round](data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md) |
