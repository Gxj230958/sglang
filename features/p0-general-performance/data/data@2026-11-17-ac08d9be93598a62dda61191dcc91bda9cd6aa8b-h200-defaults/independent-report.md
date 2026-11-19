# H200 performance sweep — independent report

Source `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`; 8 GPUs; measured 24/24 points, 4352 responses, 0 errors, 0 empty, 0 failures. Median of two repeats per row. SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s.

| Configuration | Conc | Output tok/s (r1/r2) | Total tok/s/GPU | TTFT p50/p90/p99 ms | TPOT p50/p99 ms | Interactivity p90 | SLO |
|---|---:|---:|---:|---:|---:|---:|---|
| fp8-tp8-defaults-mtp-natural | 1 | 135.8 (134.6/137.0) | 493 | 150/164/280 | 6.07/8.15 | 128.7 | pass |
| fp8-tp8-defaults-mtp-natural | 4 | 287.9 (282.8/293.1) | 1045 | 194/306/1096 | 11.79/15.50 | 43.0 | pass |
| fp8-tp8-defaults-mtp-natural | 8 | 364.4 (373.2/355.7) | 1323 | 266/1316/1797 | 17.75/24.58 | 31.5 | pass |
| fp8-tp8-defaults-mtp-natural | 16 | 457.5 (436.1/478.9) | 1661 | 323/1642/2951 | 29.22/43.61 | 18.6 | fail |
| fp8-tp8-defaults-mtp-natural | 32 | 595.0 (604.1/586.0) | 2161 | 436/3017/4287 | 47.07/61.75 | 10.8 | fail |
| fp8-tp8-defaults-mtp-natural | 64 | 742.9 (738.3/747.4) | 2697 | 609/4384/6943 | 75.23/103.99 | 6.1 | fail |
| fp8-tp8-defaults-mtp-off | 1 | 78.4 (78.4/78.4) | 285 | 141/155/275 | 11.69/11.76 | 84.8 | pass |
| fp8-tp8-defaults-mtp-off | 4 | 217.4 (215.7/219.1) | 790 | 424/834/1014 | 14.50/15.84 | 67.9 | pass |
| fp8-tp8-defaults-mtp-off | 8 | 332.6 (332.8/332.4) | 1208 | 724/1055/1684 | 17.56/22.73 | 55.6 | pass |
| fp8-tp8-defaults-mtp-off | 16 | 458.6 (453.2/463.9) | 1665 | 1404/2151/2627 | 22.82/31.41 | 42.6 | pass |
| fp8-tp8-defaults-mtp-off | 32 | 590.8 (590.6/591.1) | 2145 | 2809/3470/4060 | 30.80/47.96 | 31.6 | fail |
| fp8-tp8-defaults-mtp-off | 64 | 559.2 (546.0/572.4) | 2030 | 8383/14191/14721 | 40.70/135.40 | 23.9 | fail |
