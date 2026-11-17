# H200 FP8 performance sweep

Measured 48/48 points; 0 candidate failures. Median of two repeats per row. Raw metrics remain available for failed SLO points.

| Configuration | Concurrency | Output tok/s | TTFT p50/p99 ms | TPOT p50/p99 ms | ITL p90 ms | SLO |
|---|---:|---:|---:|---:|---:|---|
| fp8-tp8-r32-chunk32768-mtp-natural | 1 | 113.63 | 305.74/661.44 | 6.24/8.16 | 7.80 | pass |
| fp8-tp8-r32-chunk32768-mtp-natural | 4 | 222.15 | 322.33/1378.93 | 14.82/20.01 | 22.87 | pass |
| fp8-tp8-r32-chunk32768-mtp-natural | 8 | 263.66 | 350.46/2354.89 | 24.45/35.33 | 67.14 | fail |
| fp8-tp8-r32-chunk32768-mtp-natural | 16 | 348.46 | 575.26/3130.98 | 38.32/56.22 | 91.92 | fail |
| fp8-tp8-r32-chunk32768-mtp-natural | 32 | 461.10 | 626.33/4445.58 | 60.25/84.57 | 136.42 | fail |
| fp8-tp8-r32-chunk32768-mtp-natural | 64 | 339.38 | 12932.83/21529.82 | 81.73/126.89 | 178.65 | fail |
| fp8-tp8-r32-chunk32768-mtp-off | 1 | 72.28 | 287.88/316.30 | 11.66/11.75 | 11.76 | pass |
| fp8-tp8-r32-chunk32768-mtp-off | 4 | 206.02 | 598.08/945.21 | 14.48/15.32 | 14.71 | pass |
| fp8-tp8-r32-chunk32768-mtp-off | 8 | 322.04 | 831.42/1833.62 | 17.50/20.10 | 17.96 | pass |
| fp8-tp8-r32-chunk32768-mtp-off | 16 | 435.42 | 1599.03/2868.53 | 22.71/31.43 | 23.43 | pass |
| fp8-tp8-r32-chunk32768-mtp-off | 32 | 408.78 | 3383.43/8004.16 | 44.49/90.13 | 32.07 | fail |
| fp8-tp8-r32-chunk32768-mtp-off | 64 | 388.07 | 12637.51/23696.60 | 61.04/109.05 | 31.99 | fail |
| fp8-tp8-r64-chunk8192-mtp-natural | 1 | 120.50 | 299.44/350.69 | 5.83/7.66 | 7.74 | pass |
| fp8-tp8-r64-chunk8192-mtp-natural | 4 | 226.56 | 319.19/952.33 | 14.35/19.43 | 22.94 | pass |
| fp8-tp8-r64-chunk8192-mtp-natural | 8 | 285.08 | 339.34/1767.99 | 23.67/31.65 | 39.86 | fail |
| fp8-tp8-r64-chunk8192-mtp-natural | 16 | 377.31 | 565.21/2539.30 | 36.44/52.06 | 91.25 | fail |
| fp8-tp8-r64-chunk8192-mtp-natural | 32 | 478.80 | 611.49/4030.23 | 58.74/86.07 | 136.30 | fail |
| fp8-tp8-r64-chunk8192-mtp-natural | 64 | 329.47 | 11999.35/21619.02 | 92.07/151.14 | 200.52 | fail |
| fp8-tp8-r64-chunk8192-mtp-off | 1 | 72.27 | 287.53/335.66 | 11.66/11.74 | 11.76 | pass |
| fp8-tp8-r64-chunk8192-mtp-off | 4 | 206.22 | 589.46/968.50 | 14.47/15.10 | 14.70 | pass |
| fp8-tp8-r64-chunk8192-mtp-off | 8 | 324.48 | 838.85/1613.61 | 17.54/21.22 | 17.98 | pass |
| fp8-tp8-r64-chunk8192-mtp-off | 16 | 437.00 | 1703.78/2588.48 | 22.80/31.48 | 23.39 | pass |
| fp8-tp8-r64-chunk8192-mtp-off | 32 | 423.90 | 4174.40/7887.41 | 33.17/82.53 | 31.78 | fail |
| fp8-tp8-r64-chunk8192-mtp-off | 64 | 349.62 | 11401.63/26254.14 | 80.82/155.93 | 43.49 | fail |
