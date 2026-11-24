# E03 MI355X AgentX deployment crossover between TP8 and DEP8 — data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-crossover-it900

This round fills the gap in [E02](../data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-curve-it900/repro.md)'s curve between concurrency 8 and 32. It adds TP8 with an fp8 KV cache at concurrency 8, 16 and 32, TP8 bf16 at 16, and DEP8 at 16. Protocol, client, corpus and acceptance contract are as E01: local 900-second iterations with acceptance length 2.49 forced, realized 2.483–2.497 per point.

## Setup

- **`tp8_fp8`**: E02's `tp8_bf16` with `--kv-cache-dtype fp8_e4m3`. The KV pool holds 2,876,224 full-layer tokens (bf16: 1,481,088). Before the runs, GSM8K-200 on this configuration scored 95.0% with 99.0% stop ([`gsm8k200_tp8_fp8.log`](gsm8k200_tp8_fp8.log); the bf16 check is [`gsm8k200_tp8_bf16.log`](gsm8k200_tp8_bf16.log)).
- **`dep8_fp8_sched_gv4`** at concurrency 16: as E02.
  - Its `identity.txt` records a dirty tree. During that run the working tree carried an uncommitted change confined to the `SGLANG_ENABLE_DP_GATHER_FP8` path, which this candidate does not enable; the change was reverted afterwards.

## Results

All points measured so far, best deployment per concurrency in bold:

| Deployment | Concurrency | Requests (errors) | Total tok/s/GPU | Output tok/s/GPU | TTFT mean / p90 (s) | ITL mean / p90 (ms) | Interactivity mean / p90 (tok/s) | GPU prefix-cache hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **TP8 bf16** | 1 | 111 (0) | 1,367 | 12.0 | 0.64 / 1.11 | 8.6 / 10.0 | 116.4 / 100.2 | 94.4% |
| **TP8 bf16** | 4 | 198 (0) | 1,966 | 22.2 | 0.72 / 1.42 | 10.9 / 13.8 | 91.4 / 72.6 | 93.2% |
| TP8 bf16 | 8 | 342 (0) | 3,888 | 31.9 | 0.82 / 1.52 | 14.2 / 17.9 | 70.4 / 55.8 | 95.1% |
| **TP8 fp8** | 8 | 350 (0) | 3,892 | 32.9 | 0.56 / 1.10 | 13.3 / 17.3 | 75.0 / 57.8 | 96.4% |
| TP8 bf16 | 16 | 259 (0) | 2,581 | 17.5 | 12.97 / 38.97 | 75.6 / 169.3 | 13.2 / 5.9 | 63.8% |
| **TP8 fp8** | 16 | 522 (0) | 6,456 | 57.6 | 1.59 / 3.11 | 26.3 / 38.6 | 38.0 / 25.9 | 92.9% |
| DEP8 fp8 | 16 | 470 (0) | 5,669 | 38.9 | 3.21 / 6.48 | 31.9 / 40.6 | 31.3 / 24.6 | 95.0% |
| TP8 fp8 | 32 | 322 (0) | 2,880 | 16.7 | 26.30 / 80.66 | 88.5 / 258.6 | 11.3 / 3.9 | 65.3% |
| **DEP8 fp8** | 32 | 871 (0) | 9,018 | 62.0 | 5.05 / 11.92 | 42.2 / 51.9 | 23.7 / 19.3 | 94.3% |
| **DEP8 fp8** | 64 | 1,219 (0) | 13,273 | 95.4 | 8.10 / 19.84 | 52.0 / 60.3 | 19.2 / 16.6 | 94.7% |
| **DEP8 fp8** | 128 | 1,286 (0) | 11,286 | 105.6 | 50.46 / 135.47 | 70.0 / 79.0 | 14.3 / 12.7 | 89.9% |

The concurrency 1, 4, 32, 64 and 128 points and TP8 bf16 at 8 are E01's and E02's. Every point passed the upstream validator with 100% TTFT and ITL coverage.

Conclusions:

1. **TP8 fp8 up to concurrency 16.** It beats DEP8 at 16 on every metric: 14% more throughput, half the TTFT, and lower ITL. At 8 it matches TP8 bf16's throughput with lower TTFT.
2. **The crossover follows KV capacity.** Each TP8 variant falls over once its working set exceeds the pool. bf16 (1.48M tokens) collapses at 16, with the cache hit rate down to 64%; fp8 (2.88M tokens) collapses at 32 (65%). DEP8's eight attention-DP pools (about 20M tokens) hold concurrency 32–64 at a 94% hit rate.
3. **Best measured deployment by concurrency.** TP8 bf16 or fp8 at 1–8, TP8 fp8 at 16, and DEP8 fp8 with the E01 scheduling levers from 32 on.

## Data and Figures

- One directory per new point, with the same contents as E01.
- [`summary.txt`](summary.txt): the full table.
- The GSM8K-200 sanity logs for the two TP8 configurations.
