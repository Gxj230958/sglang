# B300 FP8/NVFP4 serving sweep

8 configurations, 96 measured points, 17408 successful responses, 0 errors, 0 empty outputs on 8 B300 GPUs. Two repeats per concurrency (1/4/8/16/32/64); fixed synthetic four-turn workload, 128 output tokens per turn. Source `e9a0a0287215c18b08ecb120f9d00db52986052b`.

SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s. Each row is the configuration’s best SLO-passing concurrency (median of two repeats), with its peak output throughput at any concurrency.

| Configuration | SLO concurrency | Output tok/s | Total tok/s per GPU | TTFT p50 / p90 / p99 ms | TPOT p50 / p99 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|---:|
| nvfp4-tp8-fp8kv-eager-mtp-off | 64 | 1488.7 | 5406 | 2348 / 2759 / 3460 | 23.15 / 35.93 | 1488.7 (64) |
| fp8-tp8-fp8kv-eager-mtp-off | 32 | 940.1 | 3414 | 1461 / 2184 / 2865 | 21.35 / 30.75 | 1347.3 (64) |
| nvfp4-dep8-fp8kv-eager-mtp-off | 32 | 939.1 | 3410 | 1763 / 1849 / 1902 | 21.86 / 24.35 | 1395.0 (64) |
| fp8-dep8-fp8kv-eager-mtp-off | 32 | 839.6 | 3049 | 1776 / 1931 / 1960 | 25.95 / 29.75 | 1265.1 (64) |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 4 | 240.0 | 872 | 355 / 657 / 727 | 13.55 / 18.20 | 669.8 (64) |
| fp8-tp8-fp8kv-eager-mtp-natural | 4 | 231.5 | 841 | 347 / 649 / 747 | 14.05 / 18.76 | 692.4 (64) |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 4 | 212.5 | 772 | 395 / 610 / 782 | 15.46 / 20.74 | 587.1 (64) |
| fp8-dep8-fp8kv-eager-mtp-natural | 4 | 198.9 | 722 | 396 / 522 / 673 | 16.71 / 21.76 | 596.1 (64) |

Best SLO configuration: `nvfp4-tp8-fp8kv-eager-mtp-off` at concurrency 64.

Per-concurrency rows: `independent-report.md`. Raw responses, stream timing, runtime evidence and commands: `terminal-evidence.tar.gz`.
