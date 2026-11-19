# GB300 FP8/NVFP4 serving sweep

8 configurations, 96 measured points, 17408 successful responses, 0 errors, 0 empty outputs on 4 GB300 GPUs. Two repeats per concurrency (1/4/8/16/32/64); fixed synthetic four-turn workload, 128 output tokens per turn. Source `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`.

SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s. Each row is the configuration’s best SLO-passing concurrency (median of two repeats), with its peak output throughput at any concurrency.

| Configuration | SLO concurrency | Output tok/s | Total tok/s per GPU | TTFT p50 / p90 / p99 ms | TPOT p50 / p99 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|---:|
| nvfp4-fp8_e4m3-breakable-mtp-off | 64 | 1398.8 | 10159 | 2203 / 2460 / 2635 | 28.27 / 36.54 | 1398.8 (64) |
| nvfp4-bf16-breakable-mtp-off | 64 | 1292.4 | 9386 | 2457 / 2756 / 3076 | 29.70 / 39.14 | 1292.4 (64) |
| fp8-fp8_e4m3-breakable-mtp-off | 32 | 794.5 | 5769 | 1381 / 1690 / 1973 | 29.54 / 32.90 | 1114.6 (64) |
| fp8-bf16-breakable-mtp-off | 32 | 760.5 | 5523 | 1577 / 1977 / 2249 | 29.81 / 34.88 | 1026.7 (64) |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 16 | 453.9 | 3296 | 401 / 1142 / 1184 | 31.99 / 35.35 | 985.4 (64) |
| fp8-fp8_e4m3-breakable-mtp-natural | 8 | 423.5 | 3076 | 185 / 1038 / 1054 | 16.05 / 21.09 | 1113.2 (64) |
| nvfp4-bf16-breakable-mtp-natural | 16 | 422.2 | 3066 | 431 / 1313 / 1356 | 34.42 / 37.61 | 905.6 (64) |
| fp8-bf16-breakable-mtp-natural | 8 | 395.3 | 2870 | 204 / 1331 / 1520 | 16.29 / 22.34 | 999.8 (64) |

Best SLO configuration: `nvfp4-fp8_e4m3-breakable-mtp-off` at concurrency 64.

Per-concurrency rows: `independent-report.md`. Raw responses, stream timing, runtime evidence and commands: `terminal-evidence.tar.gz`.
