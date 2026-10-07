# Per-operation FPS survey

commit `39176d13` (4 changed files), 4.7.1-stable (official), NVIDIA GeForce RTX 4070 SUPER, 4 rounds x 10 operations x 3 rooms, 6.0 s samples after 3.0 s warm-up, 1080p, vsync off, screen 1.
CPU load before each round (%): [15.0, 5.0, 26.0, 10.0]. Median operation frame time 4.709 ms; HEAVY = above 1.25x that, NOISY = per-round spread above 15% of the mean. Flags ask for a closer look, not a verdict.

## Per operation (all rooms, all rounds)

| op | n | fps | frame ms | round sd ms | vs median | p99 ms (worst) | max ms | gpu ms | process max/s ms | draws | primitives | video MB | cold load ms | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 12 | 204.3 | 4.920 | 0.180 | +4.5% | 9.09 (10.63) | 13.11 | 1.596 | 8.371 | 390 | 14059 | 1009 | 1668 | - |
| 02 | 12 | 218.6 | 4.649 | 0.080 | -1.3% | 9.21 (11.56) | 17.11 | 1.657 | 8.314 | 390 | 13930 | 996 | 1452 | - |
| 03 | 12 | 204.6 | 4.964 | 0.338 | +5.4% | 9.58 (11.21) | 14.29 | 1.794 | 8.629 | 409 | 15221 | 998 | 1757 | - |
| 04 | 12 | 233.2 | 4.367 | 0.256 | -7.3% | 8.76 (11.73) | 13.77 | 1.657 | 7.435 | 386 | 13793 | 1082 | 1423 | - |
| 05 | 12 | 251.3 | 4.009 | 0.118 | -14.9% | 8.05 (11.07) | 20.20 | 1.582 | 7.235 | 381 | 13497 | 1086 | 1363 | - |
| 06 | 12 | 208.8 | 4.811 | 0.206 | +2.2% | 9.84 (11.91) | 14.17 | 1.647 | 8.427 | 398 | 14318 | 1082 | 1316 | - |
| 07 | 12 | 216.7 | 4.730 | 0.402 | +0.4% | 9.12 (12.53) | 15.76 | 1.667 | 8.056 | 393 | 14023 | 1040 | 1863 | - |
| 08 | 12 | 214.3 | 4.688 | 0.223 | -0.4% | 8.67 (10.24) | 12.88 | 1.613 | 7.987 | 387 | 14012 | 1048 | 1375 | - |
| 09 | 12 | 195.0 | 5.187 | 0.308 | +10.1% | 9.43 (12.13) | 14.69 | 1.721 | 8.683 | 407 | 14718 | 1041 | 1907 | - |
| 10 | 12 | 219.4 | 4.648 | 0.085 | -1.3% | 8.83 (11.10) | 13.01 | 1.656 | 8.138 | 400 | 14016 | 1082 | 1420 | - |

## Per operation and room

| op | room | enemies | hazards | fps (mean +- sd over rounds) | frame ms | p99 ms | gpu ms | draws | primitives | live vfx | max live vfx |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | R02_CORRIDOR | 4 | - | 192.4 +- 6.2 | 5.202 | 9.58 | 1.657 | 401 | 14173 | 16.2 | 28 |
| 01 | R04_CONTAINMENT | 4 | - | 219.5 +- 7.5 | 4.561 | 8.34 | 1.494 | 378 | 13605 | 9.9 | 19 |
| 01 | R05_CORE | 3 | - | 201.1 +- 16.0 | 4.997 | 9.35 | 1.636 | 390 | 14400 | 11.3 | 19 |
| 02 | R02_MAINTENANCE | 4 | - | 192.5 +- 12.1 | 5.209 | 10.30 | 1.696 | 392 | 13827 | 13.9 | 25 |
| 02 | R04_QUARANTINE | 4 | - | 254.8 +- 10.9 | 3.931 | 8.09 | 1.631 | 376 | 13264 | 2.0 | 4 |
| 02 | R05_RELAY | 3 | - | 208.4 +- 10.5 | 4.807 | 9.24 | 1.642 | 403 | 14699 | 9.3 | 17 |
| 03 | R02_DEFENSE | 4 | ARC_VENT | 229.7 +- 12.9 | 4.363 | 8.32 | 1.814 | 422 | 15495 | 4.7 | 9 |
| 03 | R04_BULKHEAD | 4 | - | 179.5 +- 8.9 | 5.580 | 11.06 | 1.907 | 418 | 15830 | 10.0 | 19 |
| 03 | R05_ANCHOR | 3 | - | 204.4 +- 24.0 | 4.949 | 9.36 | 1.662 | 386 | 14338 | 7.0 | 12 |
| 04 | R02_GATE | 4 | ARC_VENT | 255.7 +- 34.2 | 3.963 | 8.03 | 1.651 | 378 | 13199 | 1.2 | 3 |
| 04 | R04_LINE | 4 | ARC_VENT | 243.0 +- 13.0 | 4.124 | 8.08 | 1.666 | 392 | 13756 | 4.7 | 8 |
| 04 | R05_WARDEN | 3 | - | 200.9 +- 20.2 | 5.014 | 10.16 | 1.654 | 387 | 14423 | 12.6 | 22 |
| 05 | R02_DEFENSE | 4 | ARC_VENT | 252.5 +- 16.9 | 3.974 | 7.74 | 1.597 | 389 | 13598 | 3.0 | 6 |
| 05 | R04_ARRAY | 4 | ARC_VENT | 227.2 +- 8.1 | 4.406 | 9.07 | 1.645 | 411 | 14405 | 5.8 | 11 |
| 05 | R05_CARRIER | 3 | - | 274.3 +- 7.3 | 3.647 | 7.34 | 1.503 | 344 | 12489 | 1.1 | 3 |
| 06 | R02_GALLERY | 4 | ARC_VENT,SPORE_CLOUD | 212.3 +- 18.3 | 4.737 | 9.27 | 1.611 | 386 | 13841 | 5.4 | 10 |
| 06 | R04_PUMPS | 4 | ARC_VENT,SPORE_CLOUD | 214.1 +- 14.2 | 4.688 | 10.55 | 1.678 | 412 | 14463 | 5.7 | 11 |
| 06 | R05_ATRIUM | 3 | - | 200.2 +- 11.9 | 5.008 | 9.68 | 1.651 | 397 | 14649 | 10.7 | 19 |
| 07 | R02_FREEZE | 4 | ARC_VENT,FROST_PLATE | 209.4 +- 14.3 | 4.792 | 9.44 | 1.564 | 387 | 13655 | 8.2 | 15 |
| 07 | R04_COMPRESSORS | 4 | ARC_VENT,FROST_PLATE | 252.8 +- 18.2 | 3.970 | 7.57 | 1.663 | 392 | 13739 | 1.2 | 3 |
| 07 | R05_VAULT | 3 | - | 188.0 +- 29.5 | 5.428 | 10.36 | 1.774 | 400 | 14674 | 13.2 | 22 |
| 08 | R02_MARSHALLING | 4 | ARC_VENT,RAIL_LANE | 213.2 +- 19.7 | 4.719 | 8.78 | 1.597 | 376 | 13615 | 6.5 | 13 |
| 08 | R04_JUNCTION | 4 | ARC_VENT,RAIL_LANE | 209.3 +- 11.7 | 4.789 | 8.77 | 1.639 | 392 | 13954 | 9.3 | 17 |
| 08 | R05_TERMINAL | 3 | - | 220.3 +- 15.7 | 4.557 | 8.46 | 1.603 | 392 | 14466 | 8.7 | 14 |
| 09 | R02_NAVE | 5 | ARC_VENT | 174.5 +- 14.0 | 5.759 | 10.58 | 1.851 | 422 | 14828 | 16.8 | 29 |
| 09 | R04_GALLERY | 4 | ARC_VENT | 199.8 +- 21.4 | 5.048 | 9.17 | 1.710 | 405 | 14596 | 8.9 | 18 |
| 09 | R05_STACKS | 3 | - | 210.9 +- 12.1 | 4.754 | 8.54 | 1.601 | 395 | 14731 | 12.1 | 20 |
| 10 | R02_RELAY | 5 | ARC_VENT | 216.8 +- 3.1 | 4.613 | 8.76 | 1.571 | 406 | 13979 | 8.9 | 15 |
| 10 | R04_GALLERY | 5 | ARC_VENT | 184.8 +- 12.7 | 5.430 | 10.22 | 1.778 | 422 | 14656 | 10.7 | 19 |
| 10 | R05_CORE | 3 | - | 256.5 +- 7.1 | 3.901 | 7.52 | 1.619 | 374 | 13412 | 2.6 | 6 |

## Drift: by round and by place in the session

A round whose mean sits far from 100 % means the PC itself was busier or quieter that round; a place that sits far from 100 % means the order matters.

| round | mean frame ms | vs all |
|---|---|---|
| 1 | 4.658 | 99.2% |
| 2 | 4.745 | 101.0% |
| 3 | 4.612 | 98.2% |
| 4 | 4.774 | 101.6% |

| place in round | mean frame ms | vs all |
|---|---|---|
| 1 | 4.900 | 104.3% |
| 2 | 4.635 | 98.7% |
| 3 | 4.965 | 105.7% |
| 4 | 4.446 | 94.6% |
| 5 | 4.528 | 96.4% |
| 6 | 4.768 | 101.5% |
| 7 | 5.013 | 106.7% |
| 8 | 4.676 | 99.6% |
| 9 | 4.404 | 93.8% |
| 10 | 4.638 | 98.7% |

The first room measured after a stage loads can run slower while its textures settle; every operation gets the same share of first rooms.

| room measured n-th in its stage | mean frame ms | vs all |
|---|---|---|
| 1 | 4.745 | 101.0% |
| 2 | 4.653 | 99.0% |
| 3 | 4.694 | 99.9% |

Frame times come from a fixed-actor preview fixture (frozen enemy AI, real autofire and hazards, no reinforcement waves, no HUD refresh): they rank the operations against each other on this PC and are not an in-play frame rate or a statement about slower machines. "process max/s" is Godot's TIME_PROCESS monitor, which reads above the mean frame time here (it looks like the worst frame of the previous second, refreshed about once a second), so treat it as a spike indicator, not a mean.
