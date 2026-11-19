# GB300 performance sweep — independent report

Source `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`; 4 GPUs; measured 96/96 points, 17408 responses, 0 errors, 0 empty, 0 failures. Median of two repeats per row. SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s.

| Configuration | Conc | Output tok/s (r1/r2) | Total tok/s/GPU | TTFT p50/p90/p99 ms | TPOT p50/p99 ms | Interactivity p90 | SLO |
|---|---:|---:|---:|---:|---:|---:|---|
| fp8-bf16-breakable-mtp-natural | 1 | 140.2 (140.4/140.1) | 1018 | 125/136/231 | 5.99/7.91 | 131.1 | pass |
| fp8-bf16-breakable-mtp-natural | 4 | 302.0 (302.9/301.1) | 2193 | 157/242/863 | 11.35/15.83 | 43.4 | pass |
| fp8-bf16-breakable-mtp-natural | 8 | 395.3 (387.2/403.3) | 2870 | 204/1331/1520 | 16.29/22.34 | 32.4 | pass |
| fp8-bf16-breakable-mtp-natural | 16 | 556.4 (537.9/574.9) | 4041 | 258/1675/1870 | 24.59/32.16 | 22.1 | fail |
| fp8-bf16-breakable-mtp-natural | 32 | 760.2 (742.8/777.6) | 5521 | 327/2332/2537 | 36.01/49.98 | 13.3 | fail |
| fp8-bf16-breakable-mtp-natural | 64 | 999.8 (990.2/1009.5) | 7261 | 469/3154/3915 | 56.30/76.19 | 8.1 | fail |
| fp8-bf16-breakable-mtp-off | 1 | 90.9 (90.8/91.0) | 660 | 116/125/216 | 10.11/10.76 | 97.9 | pass |
| fp8-bf16-breakable-mtp-off | 4 | 236.9 (236.4/237.4) | 1720 | 305/662/728 | 14.11/14.72 | 69.8 | pass |
| fp8-bf16-breakable-mtp-off | 8 | 350.1 (350.2/350.1) | 2543 | 563/1160/1177 | 17.47/19.36 | 55.7 | pass |
| fp8-bf16-breakable-mtp-off | 16 | 543.1 (542.0/544.3) | 3944 | 810/1296/1580 | 22.74/24.29 | 42.4 | pass |
| fp8-bf16-breakable-mtp-off | 32 | 760.5 (761.8/759.2) | 5523 | 1577/1977/2249 | 29.81/34.88 | 32.0 | pass |
| fp8-bf16-breakable-mtp-off | 64 | 1026.7 (1025.0/1028.4) | 7456 | 2963/3578/3641 | 38.47/50.15 | 25.1 | fail |
| fp8-fp8_e4m3-breakable-mtp-natural | 1 | 141.1 (141.8/140.4) | 1025 | 121/129/177 | 6.00/8.05 | 126.4 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 4 | 302.4 (302.0/302.8) | 2196 | 152/222/605 | 11.35/14.83 | 42.9 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 8 | 423.5 (414.7/432.4) | 3076 | 185/1038/1054 | 16.05/21.09 | 33.3 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 16 | 590.5 (595.9/585.1) | 4288 | 239/1413/1455 | 23.47/31.76 | 23.3 | fail |
| fp8-fp8_e4m3-breakable-mtp-natural | 32 | 810.8 (810.4/811.1) | 5888 | 279/1989/2054 | 34.73/46.73 | 14.8 | fail |
| fp8-fp8_e4m3-breakable-mtp-natural | 64 | 1113.2 (1118.8/1107.6) | 8084 | 388/2793/3321 | 51.34/69.62 | 9.3 | fail |
| fp8-fp8_e4m3-breakable-mtp-off | 1 | 86.3 (85.9/86.7) | 627 | 108/116/174 | 10.76/11.78 | 92.0 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 4 | 234.2 (233.1/235.3) | 1701 | 273/487/566 | 14.72/15.43 | 66.9 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 8 | 360.1 (365.7/354.5) | 2615 | 456/962/1032 | 18.10/19.91 | 53.9 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 16 | 536.4 (536.8/536.0) | 3895 | 729/1092/1356 | 23.84/25.36 | 40.4 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 32 | 794.5 (795.9/793.0) | 5769 | 1381/1690/1973 | 29.54/32.90 | 32.4 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 64 | 1114.6 (1114.3/1114.9) | 8094 | 2601/2926/3182 | 37.14/46.60 | 26.0 | fail |
| nvfp4-bf16-breakable-mtp-natural | 1 | 70.8 (70.6/71.0) | 514 | 116/123/173 | 13.28/14.59 | 73.7 | pass |
| nvfp4-bf16-breakable-mtp-natural | 4 | 186.7 (185.5/187.9) | 1356 | 209/319/610 | 19.81/21.48 | 52.1 | pass |
| nvfp4-bf16-breakable-mtp-natural | 8 | 274.6 (277.2/272.0) | 1994 | 280/981/992 | 26.19/29.84 | 40.7 | pass |
| nvfp4-bf16-breakable-mtp-natural | 16 | 422.2 (422.7/421.8) | 3066 | 431/1313/1356 | 34.42/37.61 | 32.3 | pass |
| nvfp4-bf16-breakable-mtp-natural | 32 | 638.9 (634.9/642.9) | 4639 | 533/1887/1950 | 45.71/51.58 | 26.9 | fail |
| nvfp4-bf16-breakable-mtp-natural | 64 | 905.6 (898.0/913.3) | 6577 | 1128/2819/3189 | 60.68/73.39 | 20.9 | fail |
| nvfp4-bf16-breakable-mtp-off | 1 | 96.2 (95.8/96.6) | 699 | 100/108/191 | 9.60/10.45 | 103.0 | pass |
| nvfp4-bf16-breakable-mtp-off | 4 | 269.8 (270.3/269.3) | 1959 | 265/499/574 | 12.48/13.17 | 79.2 | pass |
| nvfp4-bf16-breakable-mtp-off | 8 | 421.6 (408.3/434.9) | 3062 | 518/903/966 | 14.73/16.39 | 66.6 | pass |
| nvfp4-bf16-breakable-mtp-off | 16 | 668.2 (665.4/671.0) | 4853 | 695/1222/1370 | 18.10/19.29 | 53.7 | pass |
| nvfp4-bf16-breakable-mtp-off | 32 | 944.8 (945.4/944.2) | 6861 | 1324/1676/1869 | 23.39/26.88 | 41.7 | pass |
| nvfp4-bf16-breakable-mtp-off | 64 | 1292.4 (1295.0/1289.8) | 9386 | 2457/2756/3076 | 29.70/39.14 | 33.0 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 1 | 67.8 (67.7/67.8) | 492 | 116/122/142 | 13.96/14.66 | 70.5 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 4 | 180.6 (180.4/180.7) | 1311 | 264/376/474 | 20.01/21.39 | 49.1 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 8 | 292.0 (295.6/288.4) | 2121 | 380/842/887 | 23.67/26.27 | 41.6 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 16 | 453.9 (450.0/457.8) | 3296 | 401/1142/1184 | 31.99/35.35 | 33.6 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 32 | 691.1 (690.1/692.1) | 5019 | 593/1629/1720 | 41.49/45.59 | 27.9 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 64 | 985.4 (982.6/988.3) | 7157 | 887/2297/2735 | 58.47/65.29 | 21.9 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-off | 1 | 90.8 (90.5/91.2) | 660 | 103/108/135 | 10.23/11.01 | 96.7 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 4 | 264.9 (264.2/265.7) | 1924 | 242/374/459 | 13.06/13.68 | 75.5 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 8 | 416.7 (415.5/417.8) | 3026 | 438/800/824 | 15.26/16.90 | 64.2 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 16 | 654.2 (654.9/653.6) | 4751 | 635/892/1113 | 19.30/20.52 | 50.4 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 32 | 999.4 (1000.8/997.9) | 7257 | 1166/1455/1624 | 22.82/25.27 | 42.7 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 64 | 1398.8 (1397.3/1400.4) | 10159 | 2203/2460/2635 | 28.27/36.54 | 34.6 | pass |
