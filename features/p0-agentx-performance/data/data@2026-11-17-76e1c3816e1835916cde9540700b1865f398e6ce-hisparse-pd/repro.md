# E05 HiSparse decode under PD on AgentX: decode saturation, same-batch cost and end-to-end gain — data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd

## Environment

- Machines, containers, model and software: the same two 4× GB300 nodes, images, `PYTHONPATH` overlay and model revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089` as [Correctness E29](../../../p0-correctness/data/data@2026-11-16-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md):
  - flashinfer 0.7.4, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, torch 2.14.1+cu130;
  - Mooncake 0.3.13.post1, sglang-router 0.3.2, driver 580.178.04;
  - image digests not recorded.
- Client: the AgentX harness 1.0.14 (`agentx profile`, AIPerf 1.0.14) on the decode node.

## Setup

The prefill server, Mooncake master and router are those of E29 ([`scripts/`](scripts/)): one TP4 prefill server with the Mooncake-store external linker on node A, and one decode server on node B, TP4 with DP attention 4 and EP4 and MTP (EAGLE 3/1/4). Both use BF16 KV and `flashmla_sparse`, at `--context-length 147456` and the default window layout. The decode server is launched by [`scripts/pd_decode.sh`](scripts/pd_decode.sh) in one of three arms:

| Arm | Decode flags | Full-attention device rows per rank | Logical ids per rank |
|---|---|---:|---:|
| `pd_base` | none | 208,256 | — |
| `pd_hs` | `--enable-hisparse --hisparse-config '{"top_k":2048,"device_buffer_size":4096,"host_to_device_ratio":6}'` | 122,752 | 736,512 |
| `pd_hs12` | the same with `"host_to_device_ratio":12` | 85,440 | 1,025,280 |

- Every arm also has a 45,568-row window pool per rank.
- Device rows fall as the ratio grows because the index keys and the draft pool are sized per logical id.
- The scheduler token capacity equals the logical ids from 06:14 on 2026-11-17, as described under Commit.

For decode-saturation runs, `pd_env.sh` sets `SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=3600` and `SGLANG_DISAGGREGATION_WAITING_TIMEOUT=3600`. Under the 300 s defaults, a request that waits at a full decode server fails with a 500 and opens the router's circuit, so decode queueing would appear as errors instead of TTFT.

[`scripts/agentx_run.sh`](scripts/agentx_run.sh) runs one point:
1. It flushes the prefill cache.
2. It runs `agentx profile` against the router at a fixed conversation concurrency for a 900 s measured window, with `--extra-inputs '{"separate_reasoning": false}'`.
   - The reasoning parser would otherwise remove a one-token `</think>` warmup reply, and the client would read it as empty.
3. Setting `OSL` adds `"max_completion_tokens": OSL` to every request and lowers `--max-context-length` by the same amount.
4. Setting `WARMUP=1` sets `--warmup-requests-per-lane 1`.

[`scripts/dec_ab.sh`](scripts/dec_ab.sh) and [`scripts/dec_r12.sh`](scripts/dec_r12.sh) chain the decode-saturation points. Each one:
1. stops the decode server by process group;
2. relaunches it in the next arm;
3. waits until the router reports the decode worker healthy;
4. runs the points.

Timeline (UTC, AIPerf `start_time`–`end_time` of the measured window):

| Run | Measured window | Decode log |
|---|---|---|
| `pd_base-c16`, `pd_base-c32` | 2026-11-16 23:22–23:38, 2026-11-17 00:02–00:17 | `pd_decode_base.agentx.log.gz` |
| `pd_hs-c16`, `pd_hs-c32` | 06:26–06:42, 07:11–07:27 | `pd_decode_hs.log.gz` |
| `pd_base-c48/c8/c4-osl4096` | 08:36–08:52, 08:56–09:11, 09:14–09:29 | `pd_decode_base.log.gz` |
| `pd_hs-c48/c8/c4-osl4096` | 09:48–10:04, 10:08–10:24, 10:27–10:42 | `pd_decode_hs_dec.log.gz` |
| `pd_hs12-c48/c64-osl4096` | 11:00–11:16, 11:32–11:48 | `pd_decode_hs12.log.gz` |

The prefill server was restarted at 07:42 and at 08:13 between the two groups of runs, with no flag changes ([`logs/pd_prefill.r1.log.gz`](logs/pd_prefill.r1.log.gz), [`logs/pd_prefill.r2.log`](logs/pd_prefill.r2.log), [`logs/pd_prefill.log.gz`](logs/pd_prefill.log.gz)).

## Commit

- Code commit: `76e1c3816e1835916cde9540700b1865f398e6ce` (branch `hisparse-window-subpool-eval` of `radixark/sglang-zai`; the change of pull request 84 on `glm-5-lp` at `dd452d24`). After the last run, the served Python tree on both nodes matched it file by file (5,281 files).
- Working tree:
  - From 06:14 on 2026-11-17, every run used `76e1c381` exactly: all HiSparse points, and the baseline decode-saturation points.
  - The baseline `c16` and `c32` points ran earlier, on `76e1c381` plus [`without-request-capacity.patch`](without-request-capacity.patch). That patch does nothing without HiSparse (`logical_ids_per_full_row()` is 1).
- Status: non-release.
  - One 900 s window per point.
  - Single launch per arm, in a fixed order.
  - Image digests not recorded.
  - Model revision differs from earlier rounds.

## Scripts

- Version: round-specific scripts under [`scripts/`](scripts/). [`scripts/summarize.py`](scripts/summarize.py) recomputes the tables below from `runs/*/profile_export_aiperf.json` and `profile_export.jsonl.gz`; [`scripts/agx_sum.py`](scripts/agx_sum.py) is the summary used during the runs.
- Redaction: IP addresses, host names and local paths are placeholders in every committed file, as in E29.
- Temporary changes: none beyond the working tree above.

## Workload

- Trace: `semianalysisai/cc-traces-weka-062126` at revision `23f152f6f0f9399a85901b89a6458def0ef16729` (`--public-dataset semianalysis_cc_traces_weka_062126`). Closed-loop agentic replay; concurrency counts conversations.
- The AgentX scenario injects `ignore_eos: true`, `--cache-bust first_turn_prefix` and a 10 s idle-gap cap. Every request sets `separate_reasoning: false`.
- The client's maximum context is 147,456 tokens, or 147,456 − OSL when OSL is set.
- **Native OSL**: output lengths from the trace; c16 and c32; full warmup (179 and 355 requests).
- **Decode-saturation OSL 4096**: every turn decodes 4,096 tokens, so decode work per request is about 5.5× the trace's mean. Concurrency 48 saturates the baseline decode; c8 and c4 give decode batches of similar size in both arms; c64 checks whether ratio 12 saturates at c48. Warmup is one request per lane.
- Every point: 900 s measured window, prefill cache flushed before the run, errors counted over profiling-phase records.

## Results

Recomputed by `python3 scripts/summarize.py runs <run>...`. Output and total tok/s are AIPerf's effective decode and total throughput. Total tokens include prompt tokens served from the prefix cache.

| Run | Requests | Errors | Output tok/s | Total tok/s | Decode conc. | Prefill conc. | TTFT p50 / p90 (s) | ITL p50 / p90 (ms) | Per-user tok/s p50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pd_base-c16 | 330 | 0 | 194.7 | 27796 | 3.2 | 4.7 | 3.5 / 44.7 | 16.6 / 20.4 | 60.4 |
| pd_hs-c16 | 401 | 0 | 231.4 | 32967 | 5.8 | 1.5 | 1.3 / 8.2 | 25.5 / 34.8 | 39.0 |
| pd_base-c32 | 347 | 0 | 245.9 | 23680 | 4.5 | 16.9 | 15.8 / 130.0 | 18.9 / 23.8 | 52.6 |
| pd_hs-c32 | 379 | 0 | 259.8 | 26111 | 7.5 | 17.3 | 8.8 / 139.7 | 31.5 / 39.1 | 31.7 |
| pd_base-c4-osl4096 | 39 | 0 | 171.7 | 3682 | 2.3 | 0.0 | 0.7 / 1.2 | 13.7 / 16.5 | 72.8 |
| pd_hs-c4-osl4096 | 36 | 0 | 158.5 | 3331 | 2.4 | 0.0 | 0.7 / 1.3 | 15.3 / 17.9 | 65.6 |
| pd_base-c8-osl4096 | 76 | 0 | 334.6 | 6622 | 5.3 | 0.8 | 1.3 / 32.9 | 15.5 / 19.6 | 64.7 |
| pd_hs-c8-osl4096 | 63 | 0 | 277.4 | 5484 | 5.9 | 0.1 | 1.2 / 2.4 | 20.9 / 27.9 | 47.8 |
| pd_base-c48-osl4096 | 107 | 0 | 471.1 | 7141 | 9.8 | 25.1 | 218.9 / 439.4 | 20.5 / 27.1 | 48.8 |
| pd_hs-c48-osl4096 | 179 | 0 | 788.1 | 12380 | 33.2 | 16.9 | 45.8 / 194.2 | 41.3 / 53.8 | 24.2 |
| pd_hs12-c48-osl4096 | 190 | 0 | 836.6 | 13029 | 31.3 | 20.8 | 68.5 / 209.9 | 36.8 / 46.4 | 27.2 |
| pd_hs12-c64-osl4096 | 186 | 0 | 810.3 | 13114 | 30.5 | 25.0 | 90.7 / 245.6 | 36.7 / 47.6 | 27.2 |

Decode server state over each measured window: the mean over the `Decode batch` lines of all four ranks, read from the decode logs. Usage fractions are per rank.

| Run | Running per rank | Pre-allocation queue per rank | Device full-KV usage | Host logical usage | Accept length |
|---|---:|---:|---:|---:|---:|
| pd_base-c16 | 1.45 | 1.90 | 0.57 | — | 2.21 |
| pd_hs-c16 | 2.01 | 0.00 | 0.13 | 0.24 | 2.06 |
| pd_base-c32 | 1.68 | 5.26 | 0.74 | — | 2.07 |
| pd_hs-c32 | 2.40 | 0.24 | 0.16 | 0.68 | 2.10 |
| pd_base-c8-osl4096 | 1.44 | 0.19 | 0.54 | — | 2.24 |
| pd_hs-c8-osl4096 | 1.61 | 0.00 | 0.11 | 0.17 | 2.19 |
| pd_base-c48-osl4096 | 2.54 | 15.76 | 0.79 | — | 2.13 |
| pd_hs-c48-osl4096 | 9.10 | 6.90 | 0.61 | 0.81 | 2.19 |
| pd_hs12-c48-osl4096 | 8.38 | 8.16 | 0.81 | 0.55 | 2.19 |

- Each running HiSparse request holds 8,256 device rows in the decode log (for example, `#running-req: 1, #full token: 8256`). Device rows divided by 8,256 bound the running batch per rank: about 14.9 at ratio 6 and 10.3 at ratio 12.
- Host memory at ratio 12 ([`host-memory-ratio12.txt`](host-memory-ratio12.txt), measured with the server idle after the runs): 382.5 GiB of shared memory in the decode container, which is about 100 KB per logical id over 4 × 1,025,280 ids, and 23.4 GiB anonymous memory. The node has 955 GiB. The ratio-6 footprint was not recorded.

Derived comparisons (8 GPUs: 4 prefill + 4 decode):

| Comparison | Baseline | HiSparse | Change |
|---|---:|---:|---:|
| Decode saturation, c48 output tok/s: baseline / ratio 6 / ratio 12 | 471.1 | 788.1 / 836.6 | +67.3% / +77.6% |
| The same as output TPM per GPU | 3,533 | 5,911 / 6,275 | |
| Same batch, c8 ITL p50 (decode concurrency 5.3 / 5.9) | 15.5 ms | 20.9 ms | +35% |
| Same batch, c8 output tok/s | 334.6 | 277.4 | −17.1% |
| Same batch, c4 ITL p50 (decode concurrency 2.3 / 2.4) | 13.7 ms | 15.3 ms | +12% |
| Same batch, c4 output tok/s | 171.7 | 158.5 | −7.7% |
| Native OSL c16: requests / total tok/s | 330 / 27,796 | 401 / 32,967 | +21.5% / +18.6% |
| The same as total TPM per GPU | 208,470 | 247,253 | |
| Native OSL c32: requests / total tok/s | 347 / 23,680 | 379 / 26,111 | +9.2% / +10.3% |

Invalidated runs, kept under `runs/` because they exposed the request-capacity defect fixed in `76e1c381` (scheduler capacity 122,752 = device rows):

- `pd_hs-c16.lenbug` (04:03–04:18, 1 error) and `pd_hs-c32.lenbug`.
  - The decode server limited request length to its device rows, so it refused prompts above about 122.7K tokens.
  - In c32, the client retried such a request forever and the warmup never finished (stopped at 04:49).
- `pd_hs-c16.lenbug2` (05:00–05:15, 10 errors) and `pd_hs-c32.lenbug2` (05:45–06:00, 3 errors).
  - With only the request-length limit widened, the scheduler still counted device rows as its token capacity.
  - Long prompts were admitted but given zero new tokens, which the client records as `InvalidInferenceResultError`.

Conclusions:

1. **Decode side:** the baseline decode is bound by KV capacity on this trace. At c48 each rank runs 2.5 requests while 15.8 wait in pre-allocation, because a request reserves its whole context of up to 147K rows. With HiSparse, AIPerf's decode concurrency is 3.4× the baseline at ratio 6 and 3.2× at ratio 12 (33.2 and 31.3 against 9.8), and output throughput is +67% and +78%. c64 gives the same throughput as c48 at ratio 12, so c48 already saturates it.
2. **Ratio:** ratio 12 over ratio 6 is +6% in single runs, inside the run-to-run noise these points do not measure.
   - At ratio 6, the host logical ids bind first: host usage 0.81, device 0.61.
   - At ratio 12, the device buffer binds first: device usage 0.81, host 0.55, about 10 requests per rank.
   - Raising the ratio further shrinks the device rows and lowers that bound.
3. **Cost:** HiSparse makes each decode step slower at the same batch: ITL is +12% at decode concurrency ~2.4 and +35% at ~5.5. Output throughput is therefore 8–17% lower when the baseline is not KV-bound. At saturation, ITL p50 roughly doubles (20.5 → 41.3 ms) and per-user throughput halves (48.8 → 24.2 tok/s), because the decode batch is 3.4× larger.
4. **End to end:** on the native trace, HiSparse adds 21.5% requests and 18.6% total throughput at c16, and cuts TTFT p50 from 3.5 s to 1.3 s. At c32 the gain is +9–10%, because the single TP4 prefill server binds: prefill concurrency is about 17 in both arms. Turning the decode-side gain into end-to-end gain needs more prefill capacity per decode server.

## Data and Figures

- `runs/<run>/` — per point: `agentx.log`, AIPerf `logs/aiperf.log`, `profile_export_aiperf.json` / `.csv`, `profile_export_console.txt`, per-request `profile_export.jsonl.gz`, and `server_metrics_export.csv`.
  - AIPerf time-slice exports and the 190 MB `server_metrics_export.json` files are not kept; every number above is recomputable from the kept files.
  - `pd_hs-c32.lenbug` has no profiling export, because its warmup never finished.
- `logs/pd_decode_*.log.gz` — decode server logs per arm, in the order of the timeline.
- `logs/pd_prefill*.log*`, `logs/pd_master*.log.gz`, `logs/pd_router*.log` — prefill server, Mooncake master and router logs.
- `logs/agentx_*.out`, `logs/dec_ab.out`, `logs/dec_r12.out` — run-chain progress markers.
- `host-memory-ratio12.txt` — host memory at ratio 12.
- [`evidence-hashes.json`](evidence-hashes.json) — SHA-256 of every file in the round.
