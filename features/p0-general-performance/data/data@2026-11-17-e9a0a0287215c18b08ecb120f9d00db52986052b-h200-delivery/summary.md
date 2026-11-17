# H200 FP8 serving sweep

Completed 4 configurations, 48 measured points and 8,704 successful responses on 8 H200 GPUs. Two repeats per concurrency; fixed synthetic four-turn workload. Source `e9a0a0287215c18b08ecb120f9d00db52986052b`.

SLO: TTFT p90 ≤ 3 seconds, interactivity p90 ≥ 30 tokens/second, zero error and empty responses. Rows below show each configuration’s best measured SLO point.

| MTP | Max running / prefill chunk | Concurrency | Output tok/s | TTFT p50 / p99 ms | TPOT p50 / p99 ms |
|---|---:|---:|---:|---:|---:|
| Natural 3/1/4 | 32 / 32768 | 4 | 222.15 | 322.33 / 1378.93 | 14.82 / 20.01 |
| Off | 32 / 32768 | 16 | 435.42 | 1599.03 / 2868.53 | 22.71 / 31.43 |
| Natural 3/1/4 | 64 / 8192 | 4 | 226.56 | 319.19 / 952.33 | 14.35 / 19.43 |
| Off | 64 / 8192 | 16 | 437.00 | 1703.78 / 2588.48 | 22.80 / 31.48 |

Near-tie configurations: fp8-tp8-r32-chunk32768-mtp-off, fp8-tp8-r64-chunk8192-mtp-off. Natural MTP provides higher output throughput at concurrency 1. Full per-concurrency results, raw responses, stream timing audits and exact commands are preserved alongside this summary.
