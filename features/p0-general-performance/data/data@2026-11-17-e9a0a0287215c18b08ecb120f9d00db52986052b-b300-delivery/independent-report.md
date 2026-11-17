# B300 performance sweep — independent report

Source `e9a0a0287215c18b08ecb120f9d00db52986052b`; 8 GPUs; measured 96/96 points, 17408 responses, 0 errors, 0 empty, 0 failures. Median of two repeats per row. SLO: TTFT p90 ≤ 3 s, interactivity p90 ≥ 30 tok/s.

| Configuration | Conc | Output tok/s (r1/r2) | Total tok/s/GPU | TTFT p50/p90/p99 ms | TPOT p50/p99 ms | Interactivity p90 | SLO |
|---|---:|---:|---:|---:|---:|---:|---|
| fp8-dep8-fp8kv-eager-mtp-natural | 1 | 89.8 (90.3/89.4) | 326 | 373/404/480 | 8.07/10.32 | 97.8 | pass |
| fp8-dep8-fp8kv-eager-mtp-natural | 4 | 198.9 (197.8/200.0) | 722 | 396/522/673 | 16.71/21.76 | 40.7 | pass |
| fp8-dep8-fp8kv-eager-mtp-natural | 8 | 272.6 (272.6/272.7) | 990 | 428/662/902 | 25.24/36.41 | 16.2 | fail |
| fp8-dep8-fp8kv-eager-mtp-natural | 16 | 351.3 (350.7/352.0) | 1276 | 568/1097/1213 | 40.75/59.09 | 10.7 | fail |
| fp8-dep8-fp8kv-eager-mtp-natural | 32 | 452.1 (439.2/465.0) | 1642 | 700/1775/1893 | 64.97/94.26 | 5.8 | fail |
| fp8-dep8-fp8kv-eager-mtp-natural | 64 | 596.1 (616.4/575.9) | 2164 | 1047/2800/3868 | 99.00/147.16 | 3.7 | fail |
| fp8-dep8-fp8kv-eager-mtp-off | 1 | 48.1 (47.7/48.5) | 175 | 353/394/746 | 18.03/18.76 | 53.7 | pass |
| fp8-dep8-fp8kv-eager-mtp-off | 4 | 166.2 (165.6/166.7) | 603 | 697/723/734 | 18.96/19.50 | 51.1 | pass |
| fp8-dep8-fp8kv-eager-mtp-off | 8 | 333.7 (331.7/335.8) | 1212 | 713/789/798 | 18.90/19.64 | 50.6 | pass |
| fp8-dep8-fp8kv-eager-mtp-off | 16 | 532.6 (535.9/529.4) | 1934 | 978/1231/1249 | 22.62/24.15 | 41.9 | pass |
| fp8-dep8-fp8kv-eager-mtp-off | 32 | 839.6 (843.7/835.6) | 3049 | 1776/1931/1960 | 25.95/29.75 | 36.1 | pass |
| fp8-dep8-fp8kv-eager-mtp-off | 64 | 1265.1 (1258.6/1271.7) | 4594 | 2642/3318/3363 | 31.22/39.52 | 30.2 | fail |
| fp8-tp8-fp8kv-eager-mtp-natural | 1 | 128.3 (130.3/126.3) | 466 | 370/379/410 | 4.90/6.23 | 158.6 | pass |
| fp8-tp8-fp8kv-eager-mtp-natural | 4 | 231.5 (228.5/234.6) | 841 | 347/649/747 | 14.05/18.76 | 51.7 | pass |
| fp8-tp8-fp8kv-eager-mtp-natural | 8 | 319.9 (321.8/318.0) | 1162 | 357/966/998 | 21.53/29.45 | 28.1 | fail |
| fp8-tp8-fp8kv-eager-mtp-natural | 16 | 391.1 (385.1/397.1) | 1420 | 619/1596/1928 | 36.21/51.27 | 10.0 | fail |
| fp8-tp8-fp8kv-eager-mtp-natural | 32 | 477.7 (448.2/507.3) | 1735 | 685/1896/3156 | 61.35/86.85 | 6.3 | fail |
| fp8-tp8-fp8kv-eager-mtp-natural | 64 | 692.4 (695.3/689.5) | 2514 | 716/3200/4051 | 84.75/120.63 | 4.5 | fail |
| fp8-tp8-fp8kv-eager-mtp-off | 1 | 83.3 (83.3/83.3) | 302 | 320/324/360 | 9.57/9.64 | 101.8 | pass |
| fp8-tp8-fp8kv-eager-mtp-off | 4 | 246.6 (246.5/246.8) | 895 | 628/670/701 | 11.47/11.61 | 85.0 | pass |
| fp8-tp8-fp8kv-eager-mtp-off | 8 | 394.9 (393.5/396.3) | 1434 | 674/952/971 | 14.76/15.09 | 66.3 | pass |
| fp8-tp8-fp8kv-eager-mtp-off | 16 | 613.2 (618.7/607.7) | 2226 | 867/1382/1873 | 18.55/21.98 | 52.3 | pass |
| fp8-tp8-fp8kv-eager-mtp-off | 32 | 940.1 (936.5/943.6) | 3414 | 1461/2184/2865 | 21.35/30.75 | 45.4 | pass |
| fp8-tp8-fp8kv-eager-mtp-off | 64 | 1347.3 (1356.3/1338.2) | 4892 | 2524/3056/3832 | 26.19/38.96 | 37.0 | fail |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 1 | 93.9 (94.9/92.8) | 341 | 378/414/673 | 7.30/9.86 | 103.5 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 4 | 212.5 (215.5/209.5) | 772 | 395/610/782 | 15.46/20.74 | 41.1 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 8 | 287.3 (286.8/287.7) | 1043 | 413/756/946 | 24.07/33.60 | 16.0 | fail |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 16 | 371.9 (374.7/369.0) | 1350 | 553/809/1078 | 39.06/57.65 | 10.7 | fail |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 32 | 464.9 (463.9/465.9) | 1688 | 708/1678/1776 | 63.98/92.52 | 5.7 | fail |
| nvfp4-dep8-fp8kv-eager-mtp-natural | 64 | 587.1 (598.1/576.0) | 2132 | 1079/2608/4359 | 100.20/147.55 | 3.7 | fail |
| nvfp4-dep8-fp8kv-eager-mtp-off | 1 | 51.2 (50.9/51.6) | 186 | 360/411/751 | 16.68/17.17 | 58.3 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-off | 4 | 177.4 (177.2/177.7) | 644 | 704/730/768 | 17.23/17.85 | 56.1 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-off | 8 | 355.7 (353.4/357.9) | 1292 | 701/777/806 | 17.25/17.72 | 55.5 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-off | 16 | 587.7 (584.8/590.6) | 2134 | 972/1159/1174 | 19.83/20.50 | 47.8 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-off | 32 | 939.1 (939.2/939.0) | 3410 | 1763/1849/1902 | 21.86/24.35 | 42.6 | pass |
| nvfp4-dep8-fp8kv-eager-mtp-off | 64 | 1395.0 (1390.6/1399.5) | 5065 | 2619/3322/3373 | 25.99/34.23 | 34.6 | fail |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 1 | 132.4 (130.2/134.7) | 481 | 339/347/368 | 4.80/6.42 | 160.1 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 4 | 240.0 (245.9/234.1) | 872 | 355/657/727 | 13.55/18.20 | 56.9 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 8 | 321.4 (314.2/328.6) | 1167 | 357/814/914 | 21.05/29.88 | 22.5 | fail |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 16 | 396.0 (395.8/396.2) | 1438 | 511/1298/1736 | 36.08/50.42 | 9.7 | fail |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 32 | 491.3 (500.6/482.0) | 1784 | 678/1796/2746 | 60.79/86.11 | 6.3 | fail |
| nvfp4-tp8-fp8kv-eager-mtp-natural | 64 | 669.8 (671.1/668.6) | 2432 | 721/2568/3548 | 88.94/130.81 | 4.3 | fail |
| nvfp4-tp8-fp8kv-eager-mtp-off | 1 | 84.2 (84.4/84.0) | 306 | 331/338/382 | 9.34/9.42 | 104.1 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-off | 4 | 251.2 (248.8/253.6) | 912 | 659/670/680 | 11.12/11.22 | 87.7 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-off | 8 | 412.4 (411.0/413.9) | 1497 | 697/922/934 | 13.72/13.96 | 71.1 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-off | 16 | 668.3 (676.7/659.8) | 2427 | 820/1282/1686 | 16.74/19.50 | 58.3 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-off | 32 | 1031.5 (1032.6/1030.3) | 3745 | 1394/1965/2551 | 19.14/26.68 | 50.9 | pass |
| nvfp4-tp8-fp8kv-eager-mtp-off | 64 | 1488.7 (1486.7/1490.7) | 5406 | 2348/2759/3460 | 23.15/35.93 | 42.3 | pass |
