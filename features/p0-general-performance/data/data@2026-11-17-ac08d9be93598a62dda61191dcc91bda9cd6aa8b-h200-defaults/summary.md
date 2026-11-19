# H200 FP8/NVFP4 serving sweep

2 configurations, 24 measured points, 4352 successful responses, 0 errors, 0 empty outputs on 8 H200 GPUs. Two repeats per concurrency (1/4/8/16/32/64); fixed synthetic four-turn workload, 128 output tokens per turn. Source `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`.

SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s. Each row is the configuration’s best SLO-passing concurrency (median of two repeats), with its peak output throughput at any concurrency.

| Configuration | SLO concurrency | Output tok/s | Total tok/s per GPU | TTFT p50 / p90 / p99 ms | TPOT p50 / p99 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|---:|
| fp8-tp8-defaults-mtp-off | 16 | 458.6 | 1665 | 1404 / 2151 / 2627 | 22.82 / 31.41 | 590.8 (32) |
| fp8-tp8-defaults-mtp-natural | 8 | 364.4 | 1323 | 266 / 1316 / 1797 | 17.75 / 24.58 | 742.9 (64) |

Best SLO configuration: `fp8-tp8-defaults-mtp-off` at concurrency 16.

Per-concurrency rows: `independent-report.md`. Raw responses, stream timing, runtime evidence and commands: `terminal-evidence.tar.gz`.
