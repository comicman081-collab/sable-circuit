# Site-7 background source record — V1

Generation date: 2026-08-29 (Asia/Seoul)  
Generation method: OpenAI native image generation in Codex/ChatGPT  
Native OpenAI generation used: **YES**  
Local Qwen: **NO** · ComfyUI: **NO** · Krea2: **NO** · local Stable Diffusion: **NO** · paid/external image service: **NO**

`IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` was supplied by the user and used only as a visual-quality/camera/material authority. It is not a runtime asset and no UI, character, or text from it was copied.

## Shared generation prompt contract

High-end empty 2.5D tactical sci-fi action-game environment for SABLE CIRCUIT; elevated top-down three-quarter camera; premium underground Site-7 industrial research facility; hard-surface wall thickness, layered decks, recessed floor panels, structural supports, cast contact shadows, physically credible steel/composite materials, controlled practical lighting, and a clear open combat floor. Detail stays at the perimeter. No characters, enemies, HUD, text, signage, projectiles, or explosions. Premium stylized realism only: no low-poly, flat vector, generic neon cyberpunk, or blurry painterly concept art.

The eight room masters retain their original 1536×1024 native source and 2304×1536 derivative contract. The seven continuous-route connector masters use their native OpenAI source, a uniform centered crop/upscale to 2048×1536, and a `GAME` derivative made from the native framing by uniform crop/scale to 1600×900. No derivative uses non-uniform stretch. `PREVIEW` is 1280×720. Runtime scales are recorded in `data/visual/site7_room_art.json`.

| Room | Prompt delta / final edit direction | Native result | Runtime scale |
|---|---|---|---:|
| 01 Outer Gate | Massive reinforced security gateway; blast-door ribs, access terminal structures, amber practicals and hazard-floor language. | `exec-2ed6c316-e15a-4a78-86f3-b20cc390150a.png` | 0.88 |
| 02 Decon Corridor | Final edit: cold cyan decon arches, continuous service walls, wet steel, controlled haze, and perimeter-only deck lip/guardrail; central 65% remains flat and fully walkable. | `exec-8e3895ed-9c2d-42cb-895f-e3f5d1509b14.png` | 0.88 |
| 03 Archive Annex | Physical archive chamber; data shelving, secure storage systems, teal scanning fixtures and organized research-storage machinery. | `exec-b1403a4e-ca29-4f8d-b7d5-bcfb310bef89.png` | 0.88 |
| 04 Containment Junction | Reinforced emergency bulkheads, breach barriers, perimeter barricade language, controlled damage and orange-red alarms. | `exec-7488f7f8-2c2e-4994-90bf-7ea7d2782f18.png` | 0.88 |
| 05 Core C | Final edit: monumental upper-wall iris reactor, violet energy housings, concentric outer deck and lower foreground rim; central 60% remains a flat open boss arena. | `exec-bbc2fc16-f9df-47c0-8472-ae8eaf3ec804.png` | 1.00 |
| 06 Emergency Lift | Industrial lift terminal, vertical guide rails and shaft cues, transport machinery and green emergency guidance. | `exec-4dbe26c5-b14c-4ade-a9e3-8632e63a1a8c.png` | 0.88 |
| 07 Emergency Stores | Secure logistics room, armored supply cases, rack language at the perimeter and amber utility light. | `exec-3fd20c6d-6256-46d0-8136-969d29eaa741.png` | 0.82 |
| 08 Signal Lab | Signal-analysis laboratory with sensor arrays, scanner hardware, waveform structures and teal/cyan practical lighting. | `exec-5aff560b-b92b-4619-9e2e-5a50dc2714c6.png` | 0.82 |

## Asset hashes

| Room | MASTER SHA-256 | GAME SHA-256 | CONTINUITY SHA-256 |
|---|---|---|---|
| 01 Outer Gate | `87b7084fa35edaffd75e760dabbfa9eb876f8cd4275da2d6efd81596e543fae9` | `6969cbb944aa5e578b0e1e6627155ee7a9411f80d291c7c8f403ec5c3c936a12` | `2b78b71625223a2feaed85f72b6522372a341068ca01a85fa1d5d0cd146fa78b` |
| 02 Decon Corridor | `3a5576b071347fc7ff6c2199e1dcc96a4c2ca6a9c8672f561df7b19383a5808e` | `78a76336cd0469ad61c626663e134032d0e269f3f794fc4ec8baa423b0802690` | `5799a43bb237c709003db6943f89adbe343f56dbb03638e32fcf6db7726d2600` |
| 03 Archive Annex | `a9c8ce8c2df2aa760a2d349205e1c30b57aa38b0553ae7e60b6fdcceef25e403` | `8e430c8d31ed884ff810cc14b3f561fb45f8e925eeeee33de5b443207d6a4dc9` | `8bc9ddf916deea6a2f30074d9e2d263af024f67d74aaf3376d638fe46ff8be27` |
| 04 Containment Junction | `b42f40d3ea71aba3618abc7e6bc63ea23e5272c34265e45d39ce5e806af910b8` | `fd4be3c8415e9ac028a0a472271ed4fa79540a21178cf34f8f4189eab9b1a925` | `1112f618a91bc99fa142addde2fee183ccadf61182a6d579090137d5798270cb` |
| 05 Core C | `661daf2254beb3b8be20ff096724f39e94774a0ed233e560fb363e9ea6330299` | `546be65192213a779df231990aa0931fcea9a4823a20c5465f63109420ef1392` | `6c6b71ae22e82c23689022ea7df7ff8774890ebf48007cb82d7ea216e52d202f` |
| 06 Emergency Lift | `ddf66e31634aa8e83ed5a7652da4e3f1ae3d1d779092f65f68b3e4b1dab804ea` | `9384a21c95b3283dc08a971d3427f89d320fff1f94b721cad035188cbf5951de` | `858571506541cf4c31381d0b5612dd8f736f685fc3eee9674c1b00148f6ed617` |
| 07 Emergency Stores | `1bd414bc69bac0613869ae4ed31bac8233bfe5961135b217ff0c2e0f5ee4baa2` | `41eed4625cf12f0984c0c85a9290712dfc5a48282d7180efa400e4e24bc5cec8` | `3261ac8b12c978e4e1a8be9fe40237db60b4885634fb6d77fb7a77a3d6e56f94` |
| 08 Signal Lab | `c255d2ebdb32132b03ecb100cc1f0801e3bd09f3151eeb7a36570c9a70a31359` | `8b3892e5cbadcb0909c45a324042eef1d06e47db24173f87c9a0bc14db9265ae` | `fa00960565c90a84e3ad4a7b5e582fd75432a64a6bdadff7e0dd17af91f23f95` |

The original native result for 02 and 05 was superseded by the listed final edit; discarded duplicate native outputs were removed after final source replacement.

## Continuous-world connector set

Stage 01 is a single continuous WASD traversal/combat map, so this set adds seven opaque, world-coordinate transition plates. Exactly one nearest world segment is visible at a time; mission `current_step` is not used to select its visual. This deliberately replaces the rejected two-plate alpha blend, which made rails and floor seams ghost.

Shared connector prompt additions: same IMAGE_A camera/material authority; a broad empty central tactical lane; dense physical structures constrained to the perimeter; each connector explicitly forbids translucent/doubled/floating geometry, text, HUD, characters, central collision obstacles, black void, borders, low-poly and generic neon. Native OpenAI generation used: **YES**. Local Qwen / ComfyUI / Krea2 / LocalForge: **NO**.

| Connector | Identity / native result | Runtime asset / scale |
|---|---|---:|
| 09 Gate → Decon | Final opaque v2 edit; amber armored threshold becoming cyan decon airlock. `exec-4e4b4ad9-85a7-41fb-b4fe-177e65b4ec14.png` | `09_GATE_DECON_CONNECTOR_GAME.png` / 0.84 |
| 10 Decon → Archive | Cyan decon arch becoming teal archive cabinets/scanners. `exec-dc5bda9d-70bb-45ad-a8dd-13474dad96b2.png` | `10_DECON_ARCHIVE_CONNECTOR_GAME.png` / 0.84 |
| 11 Archive → Containment | Archive racks becoming red reinforced containment bulkheads. `exec-d8b57e6f-d495-4dff-a1e4-9f80e138c6ce.png` | `11_ARCHIVE_CONTAINMENT_CONNECTOR_GAME.png` / 0.84 |
| 12 Containment → Core | Alert bulkheads becoming violet Core C energy housings. `exec-3cdcad8e-b032-45fe-b68d-6b1275e3c21a.png` | `12_CONTAINMENT_CORE_CONNECTOR_GAME.png` / 0.84 |
| 13 Core → Lift | Violet core support language becoming green lift rail/shaft architecture. `exec-3129cfa9-e9c9-495c-926a-847a5695e17b.png` | `13_CORE_LIFT_CONNECTOR_GAME.png` / 0.84 |
| 14 Archive → Stores | Teal archive equipment becoming amber logistics racks/cases. `exec-dc6bce47-6d95-4f4c-8bd5-2ff258cda8f2.png` | `14_ARCHIVE_STORES_CONNECTOR_GAME.png` / 0.84 |
| 15 Containment → Signal | Red containment structures becoming cyan signal analyzers/sensor housings. `exec-75eeb279-e01e-4f88-9fe7-70fbd91d5be8.png` | `15_CONTAINMENT_SIGNAL_CONNECTOR_GAME.png` / 0.84 |

| Connector | RAW SHA-256 | MASTER SHA-256 | GAME SHA-256 | CONTINUITY SHA-256 |
|---|---|---|---|---|
| 09 | `8928329c99e707b9ac13cf1913d2871041c6ba04a36786ead33416eebbf6c893` | `88acf0317e9c07b1e3f87f2cd1aa36aa7c3b067f01d7fa78b59f9dd56f77b15c` | `08a6d9ae487cb90daa2e60062947ffda6e3f645a36c17908713e227454e1095a` | `88acf0317e9c07b1e3f87f2cd1aa36aa7c3b067f01d7fa78b59f9dd56f77b15c` |
| 10 | `d56f2e758c3f4b97ae4f828957e8ec27abbe003b5780e4650a3a640a5e8c0262` | `d7dd9cc5d44b98db407f91361c9313f3afde329ccfb5d4abee791eb1e0cb93df` | `d37449e87634bc2d481b75fc07102bae31d913d672fd55f468e142291c2228af` | `d7dd9cc5d44b98db407f91361c9313f3afde329ccfb5d4abee791eb1e0cb93df` |
| 11 | `819c3958feb6d370668d8ebe847614259bbe7249311b4946c790222a2031a2fb` | `6c61fc1fc5dcf48d054ec0221be0361afca6e1bb3bb5c097b58a93e5fee8627d` | `a28445db4b846434e85cc72153a3011bdb756f1f9143133e06eb9e205d56da22` | `6c61fc1fc5dcf48d054ec0221be0361afca6e1bb3bb5c097b58a93e5fee8627d` |
| 12 | `5d9ec56540ad7a24a99ac14cfd3468d22c00a114248d7716f2fa797990325266` | `75b135ea9b7ec451b414f878469bdd1faec5d0ac0c19aeb97205405db7b239ba` | `6f3889abb386ff767d6fdb8bfbbd0a1ed33909df3c5c871e68e86002968592bc` | `75b135ea9b7ec451b414f878469bdd1faec5d0ac0c19aeb97205405db7b239ba` |
| 13 | `1b462dd8fa757c81999074250865be8a4a5c9d0523db3b7663cce3e38cbd2000` | `2e8db9a288eb0aaf7d4785c3e5cc7b43e62cb895a144ae68e10b34e2df7d82d8` | `ea7e752a3a36f9dd6b2185824ac938731040448c5b123bcdf0126b2553b44b4d` | `2e8db9a288eb0aaf7d4785c3e5cc7b43e62cb895a144ae68e10b34e2df7d82d8` |
| 14 | `54fb71216816194029079ea65f96150d5920fc03dbd5ea978d54f88807133029` | `02eaa31e8dc2b5acdfd767e82d3d388752a86fd3cc62006c19c9710744425d90` | `cb969e6476766d86ec27282db93b5ade27e73f4180ceb3629238dc8e80804855` | `02eaa31e8dc2b5acdfd767e82d3d388752a86fd3cc62006c19c9710744425d90` |
| 15 | `226e8aea155d14aedcb1a71b28e74cb21ae1a125960870b76b5b530c0309355d` | `33553224c1da9e2d4c280e4a57331c106cce65a8b5035a137ad408f1e59078ed` | `b46610376e5533bdb73b75b1c67cb7802703ff08745b49e9c67929fbe328d00c` | `33553224c1da9e2d4c280e4a57331c106cce65a8b5035a137ad408f1e59078ed` |

Native source dimensions: connector 09 is 1448×1086; connectors 10–15 are 1672×941. All connector `MASTER`s are 2048×1536; runtime `GAME`s are 1600×900. Generation date: 2026-08-29 (Asia/Seoul). Seeds are not recorded because the native generator did not provide them.
