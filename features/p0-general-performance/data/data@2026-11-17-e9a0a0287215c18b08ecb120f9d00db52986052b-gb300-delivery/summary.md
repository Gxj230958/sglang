# GB300 FP8/NVFP4 serving sweep

8 configurations, 96 measured points, 17408 successful responses, 0 errors, 0 empty outputs on 4 GB300 GPUs. Two repeats per concurrency (1/4/8/16/32/64); fixed synthetic four-turn workload, 128 output tokens per turn. Source `e9a0a0287215c18b08ecb120f9d00db52986052b`.

SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s. Each row is the configuration’s best SLO-passing concurrency (median of two repeats), with its peak output throughput at any concurrency.

| Configuration | SLO concurrency | Output tok/s | Total tok/s per GPU | TTFT p50 / p90 / p99 ms | TPOT p50 / p99 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|---:|
| nvfp4-bf16-breakable-mtp-off | 32 | 896.8 | 6513 | 1485 / 1919 / 2213 | 23.54 / 30.65 | 1203.0 (64) |
| nvfp4-fp8_e4m3-eager-mtp-off | 32 | 852.3 | 6190 | 1631 / 2239 / 2476 | 23.03 / 32.16 | 1215.3 (64) |
| fp8-fp8_e4m3-eager-mtp-off | 32 | 722.8 | 5249 | 1720 / 2167 / 2519 | 29.61 / 38.65 | 1020.0 (64) |
| fp8-bf16-breakable-mtp-off | 32 | 722.7 | 5248 | 1744 / 2265 / 2623 | 30.09 / 39.14 | 969.2 (64) |
| nvfp4-bf16-breakable-mtp-natural | 8 | 504.6 | 3664 | 158 / 946 / 1069 | 13.30 / 17.67 | 1202.6 (64) |
| fp8-bf16-breakable-mtp-natural | 8 | 399.7 | 2902 | 202 / 1088 / 1373 | 16.58 / 22.75 | 979.8 (64) |
| nvfp4-fp8_e4m3-eager-mtp-natural | 4 | 200.9 | 1459 | 426 / 813 / 857 | 16.30 / 23.02 | 569.2 (64) |
| fp8-fp8_e4m3-eager-mtp-natural | 4 | 186.5 | 1354 | 426 / 770 / 808 | 17.77 / 24.38 | 545.5 (64) |

Best SLO configuration: `nvfp4-bf16-breakable-mtp-off` at concurrency 32.

Per-concurrency rows: `independent-report.md`. Raw responses, stream timing, runtime evidence and commands: `terminal-evidence.tar.gz`.
