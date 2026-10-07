# Per-operation FPS survey

commit `39176d13` (4 changed files), 4.7.1-stable (official), NVIDIA GeForce RTX 4070 SUPER, 1 rounds x 2 operations x 2 rooms, 2.0 s samples after 1.0 s warm-up, 1080p, vsync off, screen 1.
CPU load before each round (%): [5.0]. Median operation frame time 6.775 ms; HEAVY = above 1.25x that, NOISY = per-round spread above 15% of the mean. Flags ask for a closer look, not a verdict.

## Per operation (all rooms, all rounds)

| op | n | fps | frame ms | round sd ms | vs median | p99 ms (worst) | max ms | gpu ms | process max/s ms | draws | primitives | video MB | cold load ms | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 2 | 134.4 | 7.609 | 0.000 | +12.3% | 12.21 (12.33) | 14.00 | 2.208 | 13.499 | 406 | 14300 | 877 | 2521 | - |
| 09 | 2 | 169.5 | 5.941 | 0.000 | -12.3% | 11.38 (12.23) | 14.01 | 1.886 | 15.411 | 426 | 15068 | 1044 | 2358 | - |

## Per operation and room

| op | room | enemies | hazards | fps (mean +- sd over rounds) | frame ms | p99 ms | gpu ms | draws | primitives | live vfx | max live vfx |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | R02_CORRIDOR | 4 | - | 154.6 +- 0.0 | 6.468 | 12.33 | 1.738 | 422 | 14722 | 21.4 | 29 |
| 01 | R04_CONTAINMENT | 4 | - | 114.3 +- 0.0 | 8.750 | 12.10 | 2.679 | 390 | 13878 | 12.9 | 19 |
| 09 | R02_NAVE | 5 | ARC_VENT | 155.3 +- 0.0 | 6.438 | 12.23 | 1.988 | 440 | 15306 | 22.1 | 28 |
| 09 | R04_GALLERY | 4 | ARC_VENT | 183.7 +- 0.0 | 5.444 | 10.54 | 1.784 | 412 | 14830 | 11.1 | 18 |

## Drift: by round and by place in the session

A round whose mean sits far from 100 % means the PC itself was busier or quieter that round; a place that sits far from 100 % means the order matters.

| round | mean frame ms | vs all |
|---|---|---|
| 1 | 6.775 | 100.0% |

| place in round | mean frame ms | vs all |
|---|---|---|
| 1 | 7.609 | 112.3% |
| 2 | 5.941 | 87.7% |

The first room measured after a stage loads can run slower while its textures settle; every operation gets the same share of first rooms.

| room measured n-th in its stage | mean frame ms | vs all |
|---|---|---|
| 1 | 6.453 | 95.2% |
| 2 | 7.097 | 104.8% |

## Engine messages (ERROR / WARNING lines Godot printed, per round)

Distinct lines and the most any one round printed them. They come from the real stage scene, so the same lines can appear in play; judge each one, do not count them.

| per round | message |
|---|---|
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/E.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/SE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/S.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/SW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/W.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/NW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/N.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/recon_drone/authored_yaw8_v1/NE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/E.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/SE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/S.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/SW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/W.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/NW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/N.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/bulwark/authored_yaw8_v1/NE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/signal_anchor_guardian/authored_core_v1/anchor.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/null_pylon/authored_core_v1/NULL_PYLON.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/E.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/SE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/S.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/SW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/W.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/NW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/N.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/prism_skimmer/authored_yaw8_v1/NE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/E.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/SE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/S.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/SW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/W.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/NW.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/N.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/cinder_ram/authored_yaw8_v1/NE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/vesper_mortar/authored_core_v1/ANCHORED.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: Loaded resource as image file, this will not work on export: 'res://assets/enemies/stage9_index_spire/authored_core_v1/INDEX_SPIRE.png'. Instead, import the image file as an Image resource and load it normally as a resource.` |
| 1 | `WARNING: 14 ObjectDB instances were leaked at exit (run with `--verbose` for details).` |
| 1 | `ERROR: 7 resources still in use at exit (run with --verbose for details).` |

Frame times come from a fixed-actor preview fixture (frozen enemy AI, real autofire and hazards, no reinforcement waves, no HUD refresh): they rank the operations against each other on this PC and are not an in-play frame rate or a statement about slower machines. "process max/s" is Godot's TIME_PROCESS monitor, which reads above the mean frame time here (it looks like the worst frame of the previous second, refreshed about once a second), so treat it as a spike indicator, not a mean.
