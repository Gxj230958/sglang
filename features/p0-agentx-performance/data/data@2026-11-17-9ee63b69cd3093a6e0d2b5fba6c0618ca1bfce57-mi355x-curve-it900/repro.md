# E02 MI355X AgentX curve, local 900-second iteration — data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-curve-it900

This round produces a first throughput-versus-interactivity curve for GLM LoopLM on 8x MI355X. Concurrency 1–8 uses TP8; concurrency 32–128 uses the DEP8 configuration selected in [E01](../data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-dep8-c64-levers/repro.md). Every point is a local 900-second iteration under E01's protocol and acceptance contract (acceptance length 2.49 forced; realized 2.487–2.498 per point, in `accept_length.txt`). There is no reference-platform point.

## Setup

Environment, client, corpus, controller and acceptance are as E01, at `9ee63b69cd`. Commands and identities are in each point's directory. Candidates come from [`agentx_ladder.sh`](../../../p1-multi-platform/amd/scripts/v3/agentx_ladder.sh), with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` for both.

- **`tp8_bf16`** (concurrency 1, 4, 8): `--tp-size 8 --kv-cache-dtype bfloat16 --mem-fraction-static 0.80 --context-length 262144 --chunked-prefill-size 16384 --max-running-requests 64 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --enable-aiter-allreduce-fusion`, MTP 3/1/4, and the router as E01.
  - Before the run, GSM8K-200 on this configuration scored 97.0% with 99.5% stop. The KV pool holds 1,481,088 full-layer tokens.
- **`dep8_fp8_sched_gv4`** (concurrency 32, 64, 128): E01's `sched_gv4` point, that is, DEP8, fp8 KV, `--prefill-decode-interval 16 --enable-prefill-delayer --prefill-delayer-token-usage-low-watermark 0.7`, and `SGLANG_DP_USE_GATHERV=1`.
  - Concurrency 128 also ran with `--prefill-decode-interval 4`.
  - The concurrency-64 point is E01's.

## Results

| Deployment | Concurrency | Requests (errors) | Total tok/s/GPU | Output tok/s/GPU | TTFT mean / p90 (s) | ITL mean / p90 (ms) | Interactivity mean / p90 (tok/s) | GPU prefix-cache hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TP8 bf16 | 1 | 111 (0) | 1,367 | 12.0 | 0.64 / 1.11 | 8.6 / 10.0 | 116.4 / 100.2 | 94.4% |
| TP8 bf16 | 4 | 198 (0) | 1,966 | 22.2 | 0.72 / 1.42 | 10.9 / 13.8 | 91.4 / 72.6 | 93.2% |
| TP8 bf16 | 8 | 342 (0) | 3,888 | 31.9 | 0.82 / 1.52 | 14.2 / 17.9 | 70.4 / 55.8 | 95.1% |
| DEP8 fp8, interval 16 | 32 | 871 (0) | 9,018 | 62.0 | 5.05 / 11.92 | 42.2 / 51.9 | 23.7 / 19.3 | 94.3% |
| DEP8 fp8, interval 16 | 64 | 1,219 (0) | 13,273 | 95.4 | 8.10 / 19.84 | 52.0 / 60.3 | 19.2 / 16.6 | 94.7% |
| DEP8 fp8, interval 16 | 128 | 1,286 (0) | 11,286 | 105.6 | 50.46 / 135.47 | 70.0 / 79.0 | 14.3 / 12.7 | 89.9% |
| DEP8 fp8, interval 4 | 128 | 1,247 (0) | 11,288 | 88.7 | 15.46 / 47.31 | 136.9 / 156.9 | 7.3 / 6.4 | 89.4% |

Metrics are defined as in E01 and come from each point's aggregate. Every point passed the upstream validator with 100% TTFT and ITL coverage.

Conclusions:

1. **Low concurrency (TP8).** TP8 keeps TTFT under 1 s and p90 interactivity between 56 and 100 tokens/s from concurrency 1 to 8.
2. **High concurrency (DEP8).** Throughput peaks near concurrency 64 at 13.3K tokens/s/GPU. At 128 the node saturates: total throughput stops rising, the prefix-cache hit rate falls to 90%, and prefill queues. A shorter interval only moves time from TTFT to ITL (50.5 s / 70 ms becomes 15.5 s / 137 ms) at the same throughput. The ceiling is raw prefill and decode speed, not scheduling.
3. **Not covered.** The crossover between TP8 and DEP8 lies between concurrency 8 and 32 and has no point yet. The 3600-second confirmation has not been run. GPU prefix-cache hit stays at 93–95% through concurrency 64.

## Data and Figures

- One directory per point, with the same contents as E01. The concurrency-64 point is in E01's directory.
- [`summary.txt`](summary.txt): the Results table as computed by [`agentx_summary.py`](../../../p1-multi-platform/amd/scripts/v3/agentx_summary.py).
