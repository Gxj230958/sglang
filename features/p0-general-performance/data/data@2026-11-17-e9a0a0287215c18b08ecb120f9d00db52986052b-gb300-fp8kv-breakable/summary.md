# GB300 FP8/NVFP4 serving sweep

4 configurations, 48 measured points, 8704 successful responses, 0 errors, 0 empty outputs on 4 GB300 GPUs. Two repeats per concurrency (1/4/8/16/32/64); fixed synthetic four-turn workload, 128 output tokens per turn. Source `e9a0a0287215c18b08ecb120f9d00db52986052b`.

SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s. Each row is the configuration’s best SLO-passing concurrency (median of two repeats), with its peak output throughput at any concurrency.

| Configuration | SLO concurrency | Output tok/s | Total tok/s per GPU | TTFT p50 / p90 / p99 ms | TPOT p50 / p99 ms | Peak output tok/s (conc) |
|---|---:|---:|---:|---:|---:|---:|
| nvfp4-fp8_e4m3-breakable-mtp-off | 64 | 1357.1 | 9856 | 2311 / 2760 / 2887 | 28.47 / 43.50 | 1357.1 (64) |
| fp8-fp8_e4m3-breakable-mtp-off | 32 | 771.8 | 5605 | 1446 / 1896 / 2165 | 29.76 / 37.37 | 1073.8 (64) |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 8 | 502.6 | 3650 | 148 / 687 / 855 | 13.37 / 16.71 | 1337.0 (64) |
| fp8-fp8_e4m3-breakable-mtp-natural | 8 | 411.4 | 2988 | 195 / 878 / 1260 | 15.86 / 24.08 | 1067.3 (64) |

Best SLO configuration: `nvfp4-fp8_e4m3-breakable-mtp-off` at concurrency 64.

Per-concurrency rows: `independent-report.md`. Raw responses, stream timing, runtime evidence and commands: `terminal-evidence.tar.gz`.
