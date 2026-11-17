# GB300 performance sweep — independent report

Source `e9a0a0287215c18b08ecb120f9d00db52986052b`; 4 GPUs; measured 48/48 points, 8704 responses, 0 errors, 0 empty, 0 failures. Median of two repeats per row. SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s.

| Configuration | Conc | Output tok/s (r1/r2) | Total tok/s/GPU | TTFT p50/p90/p99 ms | TPOT p50/p99 ms | Interactivity p90 | SLO |
|---|---:|---:|---:|---:|---:|---:|---|
| fp8-fp8_e4m3-breakable-mtp-natural | 1 | 136.1 (135.6/136.6) | 988 | 121/130/172 | 6.30/8.17 | 125.6 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 4 | 280.8 (273.7/287.8) | 2039 | 151/236/1020 | 11.86/17.54 | 41.1 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 8 | 411.4 (393.9/429.0) | 2988 | 195/878/1260 | 15.86/24.08 | 33.0 | pass |
| fp8-fp8_e4m3-breakable-mtp-natural | 16 | 569.0 (553.6/584.3) | 4132 | 242/1278/2090 | 23.54/32.32 | 21.7 | fail |
| fp8-fp8_e4m3-breakable-mtp-natural | 32 | 785.1 (762.8/807.4) | 5702 | 298/1718/2580 | 34.80/47.37 | 14.9 | fail |
| fp8-fp8_e4m3-breakable-mtp-natural | 64 | 1067.3 (1046.3/1088.3) | 7751 | 400/2497/3863 | 52.72/69.87 | 9.1 | fail |
| fp8-fp8_e4m3-breakable-mtp-off | 1 | 86.7 (86.6/86.8) | 630 | 108/116/171 | 10.74/11.07 | 92.1 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 4 | 234.1 (233.6/234.6) | 1700 | 271/507/594 | 14.74/15.42 | 66.9 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 8 | 366.9 (368.0/365.7) | 2664 | 443/686/997 | 18.01/20.12 | 54.2 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 16 | 520.6 (521.2/519.9) | 3780 | 797/1143/1543 | 23.76/27.93 | 40.6 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 32 | 771.8 (769.5/774.1) | 5605 | 1446/1896/2165 | 29.76/37.37 | 32.5 | pass |
| fp8-fp8_e4m3-breakable-mtp-off | 64 | 1073.8 (1075.8/1071.9) | 7798 | 2809/3407/3508 | 37.26/55.39 | 26.1 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 1 | 152.0 (151.8/152.3) | 1104 | 113/122/148 | 5.60/7.42 | 140.1 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 4 | 353.2 (355.4/351.0) | 2565 | 132/224/485 | 9.63/12.96 | 49.4 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 8 | 502.6 (499.0/506.1) | 3650 | 148/687/855 | 13.37/16.71 | 40.8 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 16 | 726.2 (729.9/722.6) | 5274 | 205/924/1431 | 18.67/25.03 | 29.6 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 32 | 1006.0 (1001.4/1010.6) | 7306 | 247/1474/1938 | 27.41/38.11 | 19.2 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-natural | 64 | 1337.0 (1338.1/1336.0) | 9710 | 315/1851/3046 | 41.58/58.52 | 11.1 | fail |
| nvfp4-fp8_e4m3-breakable-mtp-off | 1 | 91.2 (91.2/91.2) | 663 | 104/110/138 | 10.22/10.27 | 96.8 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 4 | 264.6 (264.1/265.2) | 1922 | 243/400/453 | 13.10/13.72 | 75.3 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 8 | 430.2 (430.9/429.6) | 3124 | 379/556/747 | 15.35/17.36 | 64.1 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 16 | 635.7 (637.5/633.9) | 4617 | 704/943/1164 | 19.32/22.71 | 50.7 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 32 | 966.6 (967.2/966.0) | 7019 | 1224/1578/1756 | 23.05/30.13 | 42.5 | pass |
| nvfp4-fp8_e4m3-breakable-mtp-off | 64 | 1357.1 (1361.9/1352.3) | 9856 | 2311/2760/2887 | 28.47/43.50 | 34.6 | pass |
