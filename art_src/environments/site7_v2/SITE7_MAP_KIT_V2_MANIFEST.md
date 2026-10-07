# SITE-7 Map Kit V2 — stage 0 pilot and mission 1 stage 1

2026-09-27. User instructed continuation after the initial three-attempt HOLD. The initial pilot integrated S1_R02, S1_C01 and S1_C06. A later user instruction authorized replacing mission 1's remaining 12 plates to resolve its 21 v1 audit failures. The initial receipt remains in STAGE0_INITIAL_HOLD_HISTORY.md and the original QA folder.

Built-in ImageGen only, sequential attempts and inspection. Raw masters are preserved byte-for-byte. No local generation, painting, stretching, rotation, mirroring, source compositing, cropping or resizing of the selected sources. Each GAME receives exactly one uniform RGB exposure gain, recorded below. Every rejected candidate remains in quarantine. Per the latest user correction, working/staging images remain until the entire task is complete.

The returned art is native 1672×941 (R02), 1402×1122 (C01) and 1254×1254 (C06); these are not claimed as 1920×1080-authored masters. Review evidence is native 1920×1080 Godot, including 1 source pixel per screen pixel views. Runtime scale is 1.0. Numeric audit PASS is not user visual approval.

Geometry diagrams archived in references/ are input constraints only; their pixels are never used in runtime artwork. Earlier generation log paths use archived exact-byte copies of those references.

## Operation 6 A0 pilot (2026-09-29)

The user approved the A0 plates `S6_R02`, `S6_C01`, and `S6_C06` for integration without regeneration. Their full final prompts, per-attempt status, references, native dimensions, RAW/MASTER/GAME hashes, and global exposure factors are recorded in [SITE7_OP6_A0_MANIFEST.md](SITE7_OP6_A0_MANIFEST.md). The native 1920×1080 S3 comparison sheets and 1:1 source-pixel crops are in `qa/site7_ops_6_10_plates_20260929/a0/`.

The A0 trio was approved by the user on 2026-09-29 and entered stage A unchanged. The remaining twelve stage-6 plates and their exact prompts, references, attempted variants, hashes, dimensions and exposure factors are documented in [SITE7_OP6_STAGE_A_MANIFEST.md](SITE7_OP6_STAGE_A_MANIFEST.md). Technical evidence is under `qa/site7_ops_6_10_plates_20260929/stage_a/`. Campaign deployability remains disabled.

## S1_R02
- Selected attempt: 9; all earlier failures retained.
- Native: [1672, 941]; MASTER/GAME: [1672, 941]; crop: [0, 0, 1672, 941].
- RAW SHA-256: `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
- MASTER SHA-256: `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
- GAME SHA-256: `dc5e092e34e409ca552a3759710c1e6737dac3202e88c5343e734d26bfa59ed5`
- Single uniform sRGB multiplier: 0.79; log2 gain -0.34007544. No white-balance change.
- Final references: [{"archived_path": "art_src/environments/site7_v2/_quarantine/S1_R02/attempt08/S1_R02_RAW_NATIVE.png", "sha256": "4cfecbf426566f101003d6a499877d37e541d95094a516ee9bf9cff25c7cdc3d"}]

Final prompt (verbatim):

```text
Keep this exact room. WIDEN ONLY THE NE (upper-right) DOOR OPENING BY FIFTY PERCENT: keep the left jamb fixed, move the right jamb to the right/down along the wall by one full large wall panel, and lengthen the overhead lintel to reach it. The resulting clear opening must be the same width as the broad SW foreground opening. Continue the flat floor apron behind it at the same full width with parallel edges, exactly level with the room floor. Do not add steps, ramps, a shelf, a door leaf, extra doors or text. Preserve the SW opening, camera, scale, room perimeter, entire floor, wall materials, lighting and all other details. One opaque RGB PNG.
```

## S1_C01
- Selected attempt: 4; all earlier failures retained.
- Native: [1402, 1122]; MASTER/GAME: [1402, 1122]; crop: [0, 0, 1402, 1122].
- RAW SHA-256: `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`
- MASTER SHA-256: `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`
- GAME SHA-256: `188c404c4ae1aed772a52a5a7cdffb4e531913cf02a1edce5c95d9c3e2b71b59`
- Single uniform sRGB multiplier: 0.86; log2 gain -0.21759144. No white-balance change.
- Final references: [{"archived_path": "art_src/environments/site7_v2/references/S1_C01_geometry_v2.png", "sha256": "7531ea5fd8159929e54917c961b4a5903da21b5bbfdcf558ac1c6576ff07b310"}]

Final prompt (verbatim):

```text
Paint this exact geometric corridor blueprint into a richly detailed SABLE CIRCUIT industrial sci-fi game environment. Preserve its floor footprint exactly. Output landscape 5:4 (not 4:3, not 16:9).
The long neutral-grey floor has a 2:1 diagonal rising from lower-left to upper-right, floor width 285 pixels perpendicular to that axis at native 1402x1122 size. BOTH full-width floor ends cross the vertical left and right borders. A visible strip of black remains BELOW the bottom left deck corner. The top-right floor corner remains below the top border. Keep these positions from the blueprint.
Render detailed steel wall panels, exposed pipe manifolds, decon nozzles and structural ribs on the dark strip above the floor. Small amber wall practicals on left half gradually change to cyan wall practicals on right half. Keep accents entirely on walls. Low waist-high railing follows the light front-edge line. The entire grey strip is clear walkable floor.
Premium painterly hard-surface realism, precise bolted metal, matte gunmetal plates with fine panel seams at 26.6 degrees in both dimetric directions, light wear. Even neutral-white ambient floor lighting, dark neutral RGB51/52/53 floor. No hot spots, vignette, coloured floor glow, puddles, props or fog. Flat #07090D void outside. Longitudinal edges strictly parallel with no perspective convergence. Both ends open with no endwall, cap, doorway or terminating platform. No text, symbols, annotations, humans, robots, UI. One opaque RGB PNG.
```

## S1_C06
- Selected attempt: 7; all earlier failures retained.
- Native: [1254, 1254]; MASTER/GAME: [1254, 1254]; crop: [0, 0, 1254, 1254].
- RAW SHA-256: `6d3f8eebc0d22e9d91f1498691f690e312b250f3409f5a23d72759e1be34cba5`
- MASTER SHA-256: `6d3f8eebc0d22e9d91f1498691f690e312b250f3409f5a23d72759e1be34cba5`
- GAME SHA-256: `415535173950d878d2f050abf61f8d9e6f6264a735c16a3faead2a1a21e43113`
- Single uniform sRGB multiplier: 0.82; log2 gain -0.28630419. No white-balance change.
- Final references: [{"archived_path": "art_src/environments/site7_v2/references/S1_C06_square.png", "sha256": "0abb1991b32c1ae701a0ffd97284f87e243c2e8633792b48b34078088d280c83"}]

Final prompt (verbatim):

```text
Render this exact geometry diagram as a premium detailed 2.5D sci-fi tactical game corridor for SABLE CIRCUIT. Output a SQUARE image. Preserve the full-width open cuts through both left and right image borders and the generous black space below the corridor. The two long edges of the grey walking deck are exactly PARALLEL, a constant-width strip going from UPPER LEFT to LOWER RIGHT at 26.6 degrees. Do not introduce taper, convergence, bulging or any widening toward the right. The broad walking floor is about 300 pixels wide perpendicular to its axis at 1254px native canvas scale; about 2.3 standing adult heights across.
The darker strip above the floor is a 190px-high industrial back wall: dense steel panels, recessed scanner and archive housings, pipes and machined struts at upper-left, transitioning to secure supply-wall fixtures at lower-right. Small teal lights on the upper-left wall gradually transition to small amber lights on the lower-right wall. Below the floor, place a waist-high simple steel railing along the guide line. No end walls or end caps: architecture and floor continue completely beyond both vertical image borders.
Floor is empty, matte neutral dark gunmetal steel, EVEN neutral-white ambient illumination, RGB51/52/53, subtle material wear and fine 2:1 panel seams. Wall lights do not spill onto the floor. No hotspots, glossy reflections, black floor patches, fog or vignette. Outside architecture is flat #07090D. Rich premium hard-surface painted game art, crisp bevels, no vector/low-poly/diagram look. No text, symbols, people, robots, weapons, boxes, props, labels or HUD. Opaque RGB PNG.
```

## Attempt history

Exact prompts, references, source dimensions, SHA-256 and rejection reasons are in stage01/generation_log.json and each candidate folder. Attempts R02 1–3 retain their original rejection receipts. Total: R02 9; C01 4; C06 7.

Generated candidates and technical captures are not human gameplay or final art approval. The old C02 and the other v1 plates retain their older palette, framing and seam defects during this deliberately partial pilot.

## Stage 1 — mission MIS_CH01_01 remaining 12 plates (2026-09-27)

The user's follow-up authorized resolving the 21 remaining v1 plate/seam audit failures. This batch changes only mission 1 and stops after its verification. Built-in ImageGen authored all selected opaque RGB sources; source and MASTER bytes are unchanged. GAME receives one whole-image uniform sRGB gain, with no local repaint, resampling, mirror, crop, hue shift or white-balance shift. The complete 14-attempt ledger, including rejected prompts and source hashes, is in `stage01/stage1_generation_log.json`. Rejected source copies remain in `_quarantine/` and original working copies remain in `stage01/`. Native captures and audit are technical evidence, not user visual approval.

### S1_R01

- Selected attempt: 1 of 2 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `242053dde48cab9462277bc71269c1e166c00d5d03ad776066096dd60fcee6d4`
- MASTER SHA-256: `242053dde48cab9462277bc71269c1e166c00d5d03ad776066096dd60fcee6d4`
- GAME SHA-256: `4d12293b266cff0856e29ee57f4e6fd2ff2c95a2e8b0a2c9a197749c9a42e585`
- One uniform sRGB multiplier: 0.754; log2 gain -0.40736357.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_R02/S1_R02_MASTER.png` — `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
  - `assets/environments/site7/outer_gate/01_OUTER_GATE_CONTINUITY.png` — `2b78b71625223a2feaed85f72b6522372a341068ca01a85fa1d5d0cd146fa78b`
- Rejected attempt 2: NE apron is shorter and less clearly coplanar than attempt 01; less even floor illumination; SHA-256 `398a422f7d10e5fea5c6f852a449816ef8618ccf286bfd3e5735c5f2ca925d14`; retained under `_quarantine/S1_R01/attempt02/`.

Final prompt (verbatim):

```text
Use case: stylized-concept. Asset: one opaque RGB environment room plate for the SITE-7 tactical game. Create a new S1_R01 Outer Gate room using image 1 as the approved production camera, floor material, lighting, wall/railing quality and scale reference, and image 2 solely for the outer security gate identity. Do not copy the decontamination room identity from image 1 or the lighting/geometry from image 2. Fixed near-orthographic 3/4 top-down dimetric view, both floor diagonal axes 2:1 (26.6 degrees), no perspective convergence. A large open dimetric floor footprint at least 1000 by 560 pixels with neutral dark gunmetal steel deck, uniformly lit by neutral white ceiling lighting, same apparent floor brightness and fine square seams as image 1. Back walls only on NW and NE edges, foreground SW and SE edges low railing/lip. Exactly ONE doorway: a broad OPEN heavy-frame threshold in the NE upper-right back wall, ~300px wide, no door leaf. Extend full-width unobstructed flat grey deck apron 195px beyond the NE threshold under the doorway at same level, uniform width and brightness. No doorway or gap anywhere else. Identity: massive reinforced security gateway, blast-door ribs and access terminal structures built into the rear walls, restrained amber wall lamps; all amber color stays off the neutral grey walking floor, especially at the doorway. Floor occupies at least 30% of image, remains at least 8% from border. Flat near-black #07090D outside architecture. Premium crisp painterly hard-surface realism. No letters, signs, digits, symbols, characters, robots, props on floor, UI, haze, vignette, glowing floor pools, dark floor holes, black frame. Preserve room scale and art style of image 1. This image must be a standalone room plate, not a corridor or composite. No text.
```

### S1_R03

- Selected attempt: 1 of 1 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `e2a5c58bb5292c2b2b5726598c97bd3d6c26f0114be74de55952039e231d1b5c`
- MASTER SHA-256: `e2a5c58bb5292c2b2b5726598c97bd3d6c26f0114be74de55952039e231d1b5c`
- GAME SHA-256: `22200971ee413d4c0593c4f2d37b29a24e113ba4e4b1c396f4ae6d3f1ffee5be`
- One uniform sRGB multiplier: 0.757; log2 gain -0.40163479.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_R02/S1_R02_MASTER.png` — `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
  - `assets/environments/site7/archive_annex/03_ARCHIVE_ANNEX_CONTINUITY.png` — `8bc9ddf916deea6a2f30074d9e2d263af024f67d74aaf3376d638fe46ff8be27`

Final prompt (verbatim):

```text
Use case: stylized-concept. One opaque RGB SITE-7 game room plate, S1_R03 Archive Annex. Reference image 1 defines the exact approved 3/4 top-down dimetric camera, scale, hard-surface quality, neutral dark steel floor and even lighting. Reference image 2 supplies ONLY archive room identity. Make an expansive physical archive chamber, with tall secure data shelving and scanner fixtures built against the NW and NE back walls, restrained teal lamps on walls only. Same neutral gunmetal deck and neutral white lighting as image 1, not teal on the floor. Floor is open and walkable, >1000x560 native pixels, at least 30% of canvas; seams trace both diagonal 2:1 axes (26.6 degrees), no perspective convergence. Exactly THREE unobstructed doorways: SW foreground low railing gap, NE upper-right heavy-frame open wall portal, and SE foreground/right low railing gap. No fourth opening. Each gap is roughly 300px wide, with same coplanar full-width steel deck apron extending ~195px through the threshold at the same brightness, especially NE portal. Back walls only NW and NE; SW and SE low lip/railing, no walls hiding floor. Put architecture at least 8% inside image borders, flat near-black #07090D void outside. Maintain crisp premium painterly metal materials, no floor props, boxes, clutter, characters, machines in walking area, lettering, signage, numbers, logos, UI, smoke, vignette, black border, bright or dark floor spots. One standalone room plate.
```

### S1_R04

- Selected attempt: 1 of 1 generated candidates; native RGB: 1774×887; GAME scale 1.0 and native size.
- RAW SHA-256: `c49ac9abb79dbd2b2da74637dc02b59146a6943d4b70d795b78754902dd85352`
- MASTER SHA-256: `c49ac9abb79dbd2b2da74637dc02b59146a6943d4b70d795b78754902dd85352`
- GAME SHA-256: `5e361e7b97389afce6cc76b595271af9c92023e289bd578ae4106eca7607c2f7`
- One uniform sRGB multiplier: 0.798; log2 gain -0.32553935.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_R02/S1_R02_MASTER.png` — `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
  - `assets/environments/site7/containment_junction/04_CONTAINMENT_JUNCTION_CONTINUITY.png` — `1112f618a91bc99fa142addde2fee183ccadf61182a6d579090137d5798270cb`

Final prompt (verbatim):

```text
Use case: stylized-concept. One opaque RGB SITE-7 game room plate, S1_R04 Containment Junction, a broad combat hallway. Match reference image 1's exact fixed near-orthographic 3/4 top-down 2:1 dimetric camera, neutral steel floor texture, white floor lighting, scale and premium hard-surface render. Reference image 2 is ONLY containment identity. Create reinforced emergency bulkheads, controlled damage and breach barriers built into the perimeter back walls, orange-red alarm beacons on the walls; absolutely no orange/red light spill onto neutral dark gunmetal walkable floor. Floor is long and broad, at least 1300px long by 380px short, open with no central props, at least 30% canvas, 2:1 diagonal seams at 26.6 degrees, no convergence. Exactly THREE accessible doorway aprons: SW front-left railing gap, NE upper-right open steel wall frame, SE front-right railing gap. Every opening about 300px wide and extends 195px in a coplanar full-width steel floor apron beyond threshold. Doorways are open and unobstructed, no leaf, no shutter, no steps. Back walls only NW and NE, no tall wall in SW/SE foreground. Room outline 8% inward from image borders and flat #07090D outside. Same neutral floor brightness all over and through each apron, no hot spots, dark holes, haze, vignette, reflected alarm color or clutter. Crisp painterly architectural details. No text, numerals, logos, signs, characters, enemies, weapons, UI, props on floor or black frame. One standalone room image.
```

### S1_R05

- Selected attempt: 1 of 1 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `7b19e7a66f91558eb2c6483f0c84717a44aedde4c8e45b85ea21fca17ec297c2`
- MASTER SHA-256: `7b19e7a66f91558eb2c6483f0c84717a44aedde4c8e45b85ea21fca17ec297c2`
- GAME SHA-256: `089667385bd7d68595ebcab4f01045dbd8aad04453ee0c076d30f2788e9ef9e5`
- One uniform sRGB multiplier: 0.749; log2 gain -0.41696238.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_R02/S1_R02_MASTER.png` — `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
  - `assets/environments/site7/core_c/05_CORE_C_CONTINUITY.png` — `6c6b71ae22e82c23689022ea7df7ff8774890ebf48007cb82d7ea216e52d202f`

Final prompt (verbatim):

```text
Use case: stylized-concept. One opaque RGB SITE-7 game room plate, S1_R05 Core C boss arena. Match reference image 1's fixed near-orthographic three-quarter top-down dimetric 2:1 camera, precise diagonal panel seams (26.6 degrees), realistic hard-surface authored style, floor scale and neutral white lighting. Reference image 2 is ONLY for the monumental iris reactor identity. Build a spacious open arena floor at least 1100x520 native pixels and 30% canvas, matte dark neutral gunmetal steel, uniformly lit (same tone as image 1); no equipment, iris or platform in the walking floor. Monumental violet reactor iris, thick energy housings and concentric outer rim are mounted HIGH on the NW back wall at the upper perimeter, leaving the entire center open. Restrained violet accent on walls only; no violet cast on floor or door aprons. Back walls only NW and NE; foreground SW and SE low waist-high railings/lips. Exactly TWO open doorways: SW foreground left railing gap and NE upper-right heavy-frame wall opening, each about 300px clear with 195px coplanar full-width steel deck apron beyond the threshold. No other opening, no shutter, door leaf, steps or obstruction. Architecture remains 8% inward from image borders, outside is flat #07090D. No perspective convergence, hot/cold floor spots, dark holes, floor glow, fog, vignette, text, signs, numbers, logos, humans, robots, weapons, props in the arena, UI or black frame. Crisp premium painterly metal detail. One standalone boss-room image.
```

### S1_R06

- Selected attempt: 1 of 1 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `ff89515898ae085ab01068e43183d2750daba5a3d7e49991f4b73165957d67e0`
- MASTER SHA-256: `ff89515898ae085ab01068e43183d2750daba5a3d7e49991f4b73165957d67e0`
- GAME SHA-256: `deefbd0ff4e65bab4fc1f8508a6f831ae2e05056f0874d1ef196e736036cdf6a`
- One uniform sRGB multiplier: 0.792; log2 gain -0.33642766.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_R02/S1_R02_MASTER.png` — `f27502ae170c7b04ff9ed91cc785231099676c5f68bb048c60f350bd4374e5ca`
  - `assets/environments/site7/emergency_lift/06_EMERGENCY_LIFT_CONTINUITY.png` — `858571506541cf4c31381d0b5612dd8f736f685fc3eee9674c1b00148f6ed617`

Final prompt (verbatim):

```text
Use case: stylized-concept. One opaque RGB SITE-7 game room plate, S1_R06 Emergency Lift extraction terminal. Reference image 1 is the production camera, neutral dark steel deck, wall/railing quality, floor lighting and size standard. Reference image 2 is solely the vertical lift terminal identity. Fixed near-orthographic 3/4 top-down dimetric view, 2:1 floor axes at 26.6 degrees, no perspective convergence. Large open walkable gunmetal steel floor >850x450px and >=30% image, same neutral white even lighting and floor color as reference 1. Rear NW and NE back walls carry deep vertical guide rails, shaft machinery and restrained green practical lamps; no green color on floor. Exactly one doorway: broad SW lower-left foreground gap in low steel railing, ~300px wide and continuing in a full-width 195px coplanar floor apron beyond threshold. No NE or SE door, no other gap. Back walls NW and NE only, SW and SE low waist-high railing. Floor and architecture 8% from image edge, outside flat near-black #07090D. No shutters, door leaf, step, lift platform raised above walkable floor, central props, people, robots, weapons, text, numbers, signs, logos, UI, haze, vignette, hot/dark floor spots, colored floor reflections or black frame. Premium crisp painterly hard-surface metal detail. Standalone room image.
```

### S1_O01

- Selected attempt: 2 of 2 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `b61a83322a26e515fe0a7eb952185db1766b98295d9f949ae8b9a2c19b696185`
- MASTER SHA-256: `b61a83322a26e515fe0a7eb952185db1766b98295d9f949ae8b9a2c19b696185`
- GAME SHA-256: `a530ad4a8f39b0d963251472b591dec58293790ad0352b7dbba40fc156e50f74`
- One uniform sRGB multiplier: 0.669; log2 gain -0.57992188.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_O01/S1_O01_attempt01_RAW_NATIVE.png` — `c0e09956c616a14adaf2e1efaf3a35e93b9fb4da3e7dd5f2b77c1f9aa5bb90fc`
- Rejected attempt 1: unrequested SW foreground opening in addition to the required NW door; SHA-256 `c0e09956c616a14adaf2e1efaf3a35e93b9fb4da3e7dd5f2b77c1f9aa5bb90fc`; retained under `_quarantine/S1_O01/attempt01/`.

Final prompt (verbatim):

```text
Precise-object-edit of this S1_O01 supply room plate. The NW upper-left back-wall doorway is correct and must remain fully open with its matching floor apron. CLOSE AND REMOVE ONLY the unwanted SW lower-left foreground gap and its large outside floor extension. Continue the same waist-high metal railing/lip seamlessly across the entire SW front-left edge, matching all neighboring railing posts and perspective. Replace the outside apron area with the same flat near-black void #07090D as the background. Preserve every other pixel conceptually: exact NW doorway, shelf units, room walls, same dimetric camera and floor outline, neutral steel floor panel seams and even lighting, scale, palette, right railing, no text or characters. No additional entrances. One opaque RGB room image.
```

### S1_O02

- Selected attempt: 1 of 1 generated candidates; native RGB: 1672×941; GAME scale 1.0 and native size.
- RAW SHA-256: `559e8f355c357842a1914fd24a9a46b69a93eb935b9dc9473ef51076cfae6f62`
- MASTER SHA-256: `559e8f355c357842a1914fd24a9a46b69a93eb935b9dc9473ef51076cfae6f62`
- GAME SHA-256: `aaf196e50587c8f32b207bf9744823a1fb94c1b09085e587eddb19d66e144cc4`
- One uniform sRGB multiplier: 0.643; log2 gain -0.63710936.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_O01/S1_O01_attempt02_RAW_NATIVE.png` — `b61a83322a26e515fe0a7eb952185db1766b98295d9f949ae8b9a2c19b696185`
  - `assets/environments/site7/signal_lab/08_SIGNAL_LAB_CONTINUITY.png` — `fa00960565c90a84e3ad4a7b5e582fd75432a64a6bdadff7e0dd17af91f23f95`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Transform image 1's S1_O01 supply room into the distinct S1_O02 Signal Lab room, taking only signal-analysis identity from image 2. Keep the EXACT fixed near-orthographic 3/4 top-down 2:1 dimetric camera, same open NW upper-left back-wall doorway and its full-width level neutral floor apron, same perimeter, NO other doors, same low foreground railing, same image proportions, same evenly lit neutral dark gunmetal floor color and fine panel seams. Replace all storage cases/racks in the back walls with built-in sensor arrays, scanning equipment, oscillation instrument housings and signal-analysis consoles. Change small amber wall practical lamps to restrained teal-cyan lamps. Keep their colored light entirely on the walls; the walkable floor and NW door apron remain exactly neutral dark grey, white-lit, no colored spill. Floor remains >850x450px, clear of equipment/props and at least 30% image. Premium hard-surface painterly architectural quality, flat near-black exterior. No text, numerals, symbols, labels, people, robots, weapons, UI, fog, vignette, floor hotspots/dark patches, black frame. Opaque RGB standalone plate. Preserve door geometry and floor continuity exactly.
```

### S1_C02

- Selected attempt: 1 of 1 generated candidates; native RGB: 1402×1122; GAME scale 1.0 and native size.
- RAW SHA-256: `c7069e8aa0a6b04bf6af8c6279e412ea7dcdc8f495ad92b0363533926f3ab2ef`
- MASTER SHA-256: `c7069e8aa0a6b04bf6af8c6279e412ea7dcdc8f495ad92b0363533926f3ab2ef`
- GAME SHA-256: `6cf78161953a276c48c6962a9e815e66ca66de863734470060e4b8783917b143`
- One uniform sRGB multiplier: 0.769; log2 gain -0.37894450.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_C01/S1_C01_MASTER.png` — `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Create the distinct S1_C02 decontamination-to-archive connector from this approved S1_C01 ascending corridor plate. Preserve the exact long NE-ascending 2:1 diagonal geometry, constant ~280px floor width, both full-width open floor cuts through LEFT and RIGHT image borders, NO end wall/cap/door/fade, empty neutral dark gunmetal deck, 26.6-degree dimetric panel seams, neutral even floor lighting, premium hard-surface texture, upper-left steel back wall, lower-right waist-high railing, flat near-black void and image proportions. Change ONLY wall-side fixtures and wall lighting: cold cyan decontamination spray manifolds and wet steel wall panels at the lower-left start gradually become teal secure archive shelves/scanner housings at the upper-right end. Accents remain only on wall, no cyan/teal spill onto the floor. Both endpoint deck sections must match the reference floor brightness and color identically. No perspective convergence, taper, bulges, platforms, floor props, writing, signs, digits, characters, enemies, UI, fog, vignette, dark or bright floor patches, black frame. Opaque RGB standalone corridor plate, not room.
```

### S1_C03

- Selected attempt: 1 of 1 generated candidates; native RGB: 1402×1122; GAME scale 1.0 and native size.
- RAW SHA-256: `e1ae9520bc7b91d6e280bd7cbaab456b28c02eb336286ef2c7aa88e3a25977a4`
- MASTER SHA-256: `e1ae9520bc7b91d6e280bd7cbaab456b28c02eb336286ef2c7aa88e3a25977a4`
- GAME SHA-256: `e43ae0928d1c1417f12b53219c2ba649677090b514e220f5e26d2981721cd16f`
- One uniform sRGB multiplier: 0.757; log2 gain -0.40163479.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_C01/S1_C01_MASTER.png` — `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Produce S1_C03 Archive Annex to Containment Junction connector from this approved ascending SITE-7 corridor. Preserve exact camera and floor footprint: straight lower-left to upper-right 2:1 diagonal with constant ~280px deck width and BOTH full-width open cuts at left and right image borders, no end walls, doors, caps, fades or narrowed ends. Floor remains clear neutral dark gunmetal steel, fine 26.6-degree dimetric seams, evenly neutral-white lit at both ends, no colored cast or stains. Upper-left back wall and lower-right waist-high railing remain continuous and same scale. Change wall-side architecture from secure archive shelf/scanner modules with restrained teal practicals at LEFT lower end to reinforced containment bulkhead ribs, breach barrier housings and orange-red warning beacons at RIGHT upper end; transition in middle. The orange/red light must remain on walls only and not spill onto deck. Flat near-black void outside. Premium crisp painterly hard-surface realism. No people, robots, props on deck, text, symbols, signs, numbers, logos, UI, fog, vignette, floor holes/hotspots, black frame or perspective taper. One standalone opaque RGB corridor plate.
```

### S1_C04

- Selected attempt: 1 of 1 generated candidates; native RGB: 1402×1122; GAME scale 1.0 and native size.
- RAW SHA-256: `5a3e36835d878958de941934958ec00182582efb0c5978ceb9f109d12cabc7e0`
- MASTER SHA-256: `5a3e36835d878958de941934958ec00182582efb0c5978ceb9f109d12cabc7e0`
- GAME SHA-256: `1fa63248c60f1339ba9f293cbbaac0bf1cfa6637e62cf3e1e9f96dec2971783d`
- One uniform sRGB multiplier: 0.746; log2 gain -0.42275246.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_C01/S1_C01_MASTER.png` — `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Produce S1_C04 Containment Junction to Core C connector from this approved SITE-7 ascending corridor. Preserve exact fixed near-orthographic 3/4 top-down 2:1 camera, straight lower-left to upper-right 26.6-degree axis, same constant ~280px wide uninterrupted deck, both full-width floor ends crossing LEFT and RIGHT image edges at full brightness, no end caps, doors or fades. Preserve the even neutral-white light and matte dark neutral-grey gunmetal floor with fine seams, no red/violet cast, no floor objects or dark holes. Change wall-side architecture only: heavy containment bulkheads, controlled breached steel and small orange-red alarm wall lamps at lower-left; gradually transition to monumental reactor energy housings, large concentric casing details and small violet practical lamps at upper-right. All colored accents remain on back wall and structural fixtures, never illuminate deck. Continue upper-left back wall and lower-right waist-high metal railing at unchanged scale; outside flat #07090D void. Premium crisp hard-surface painted game asset. No perspective convergence, taper, widened end, platform, obstruction, text, signs, digits, logos, actors, robots, weapons, UI, fog, vignette, black border. Opaque RGB single corridor plate.
```

### S1_C05

- Selected attempt: 1 of 1 generated candidates; native RGB: 1402×1122; GAME scale 1.0 and native size.
- RAW SHA-256: `ad4944ab2de20d288311c5fddec1a8de7d61f8981261fce818884911415ef46e`
- MASTER SHA-256: `ad4944ab2de20d288311c5fddec1a8de7d61f8981261fce818884911415ef46e`
- GAME SHA-256: `ab6d78f95ef7adb98a48fd9487d83315fe7cacba975bf68f4a813bcc56f5667b`
- One uniform sRGB multiplier: 0.672; log2 gain -0.57346686.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_C01/S1_C01_MASTER.png` — `6caaf7fab42c6a589e4b36064710eab4c10e184bf14c72e854fe682f3272229b`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Produce S1_C05 Core C to Emergency Lift connector from this approved ascending SITE-7 corridor plate. Preserve exact fixed orthographic-like 3/4 top-down dimetric 2:1 projection, lower-left to upper-right straight diagonal at 26.6 degrees, identical constant ~280px width of open neutral dark steel deck, full-width bright floor cuts through LEFT and RIGHT edges, no door/cap/endwall/fade at either end, same even neutral-white floor lighting and fine floor panel seams. Upper-left back wall and lower-right waist-high railing continue across whole image at unchanged scale, outside flat near-black void. Change ONLY back-wall equipment and small lamps: reactor conduit rings and restrained violet fixtures near lower-left transition to industrial lift guide rails/shaft machinery with restrained green fixtures near upper-right. The walking deck at both ends and middle stays neutral dark grey, with no violet/green light spill or reflection. Rich crisp painterly steel construction, no taper or perspective convergence, floor obstacles, props, humans, robots, UI, writing, signs, numbers, logos, smoke, vignette, floor hotspots/black holes or black border. One opaque RGB standalone corridor image.
```

### S1_C07

- Selected attempt: 1 of 1 generated candidates; native RGB: 1254×1254; GAME scale 1.0 and native size.
- RAW SHA-256: `941ce2715bacf23e180d39a02f62ae0592d68548d2e3cce5693054068ea5b865`
- MASTER SHA-256: `941ce2715bacf23e180d39a02f62ae0592d68548d2e3cce5693054068ea5b865`
- GAME SHA-256: `d201c8273053020284cd11011a8e04e0bf8392ebff5a433b4cd054b9488fbb0a`
- One uniform sRGB multiplier: 0.782; log2 gain -0.35475949.
- Exact reference images and SHA-256:
  - `art_src/environments/site7_v2/stage01/S1_C06/S1_C06_MASTER.png` — `6d3f8eebc0d22e9d91f1498691f690e312b250f3409f5a23d72759e1be34cba5`

Final prompt (verbatim):

```text
Use case: precise-object-edit. Produce S1_C07 Containment Junction to Signal Lab descending branch corridor from this approved S1_C06 descending corridor. Preserve EXACT camera, native square proportions, floor footprint, 2:1 diagonal descending UPPER LEFT to LOWER RIGHT at 26.6 degrees, constant ~290px deck width and both FULL-WIDTH open cuts through left and right image borders; no end wall, end cap, door, fade, narrowing, taper or mirrored image. Preserve the same even neutral-white-lit dark neutral gunmetal steel floor at both ends, fine dimetric panel seams, continuous upper-right back wall and lower-left waist-high railing. Change wall features only: reinforced containment bulkhead ribs with small orange-red alarm wall lamps near UPPER-LEFT start transition to built-in signal-analysis arrays, antenna/scanner housings and small teal-cyan wall lamps near LOWER-RIGHT finish. Colored lamps stay on wall; no red or cyan tint/glow on floor. Empty floor, flat near-black exterior, premium crisp painterly hard-surface realism, unchanged scale. No perspective convergence, bulging, floor props, text, symbols, signage, digits, logo, people, robots, weapons, UI, haze, vignette, floor hotspots/holes, black frame. One opaque RGB standalone corridor plate.
```

## Stage 4 — dedicated mission 4 and 5 rooms (2026-09-27)

All 16 selected plates are opaque RGB native ImageGen outputs. RAW and MASTER are byte-identical. GAME keeps the native dimensions and applies one whole-image sRGB multiplication (and the recorded uniform per-channel white balance where listed). Runtime scale is 1.0. No crop, resize, flip or localized paint was applied. The two rejected first candidates remain in quarantine. The prompt text below was recovered from this task's ImageGen invocation record, including the expanded common template.

### S4_R01

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R01/S4_R01_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R01/S4_R01_RAW_NATIVE.png` — `77b6deb06ec74da4b96c42918ef12b0e6968bafb21fc6bc99f15b03849b594a3`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R01/S4_R01_MASTER.png` — `77b6deb06ec74da4b96c42918ef12b0e6968bafb21fc6bc99f15b03849b594a3`
- GAME: `assets/environments/site7_v2/stage04/S4_R01/S4_R01_GAME.png` — `91096c9bf1da1bb4d38b239ebf52be7924805e2f14f62d5f053805da0db47d02`
- Whole-image sRGB factor: 0.616 (log2 -0.698998 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R06/S3_R06_MASTER.png` — `dc2c95cefbebcdfed940697ecb61c80ff4d1054e57e6456a67abf303fdda93dc`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: opaque RGB standalone SITE-7 stage 4 environment ROOM plate S4_R01 Thermal Spine for a 2.5D tactical game. Reference image 1 (D:\AI 종합 폴더\Games\Sable-circuit\\art_src\\environments\\site7_v2\\stage03\\S3_R06\\S3_R06_MASTER.png) is ONLY the camera, scale, neutral deck material, and doorway/apron geometry baseline; reference image 2 (D:\AI 종합 폴더\Games\Sable-circuit\\art_src\\environments\\site7\\references\\IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png) is ONLY the premium hard-surface material/detail quality, never copy its UI, characters or text. Create wholly NEW wall silhouette and machinery, not a recolor or duplication of image 1. Fixed near-orthographic 3/4 top-down dimetric camera; floor seams and wall bases exactly 2:1 diagonal (26.6 degrees), no convergence. The sole walkable floor is a generous uncluttered elongated hexagonal dark gunmetal standard steel deck, at least as large as image 1, at least 8 percent inward from all image edges. One and ONLY one OPEN doorway on the SW lower-left foreground perimeter, 300 px wide at this scale, with uninterrupted level standard-deck apron extending 195 px each side of threshold. No doors/openings on NE, NW, SE. NW and NE sides have back walls; SW and SE sides have low waist-high metal lip/rail and no tall wall to hide floor. Architectural identity: THERMAL SPINE. A massive insulated vertical heat-exchange column and asymmetric pressure manifold towers BUILT INTO the far back wall, layered heat-shield cladding and industrial coolant routing around the wall perimeter. Distinct complex vertical silhouette unlike the reference escape shaft. Small restrained amber practical wall lamps only. Floor is evenly lit by a single neutral-white 6000K overhead source, neutral grey with mean sRGB brightness near 0.20, no amber tint/spill on floor, no spotlight pools, no dark holes, no vignette or fog, including the SW apron. Outside all architecture: uniform flat #07090D. Premium crisp painterly stylized realism, thick cast-metal structure, recessed panels, dimensional contact shadows. No free-standing equipment on floor. NO text, letters, numerals, symbols, signs, logos, characters, enemies, weapons, UI, arrows, fog, smoke, glare, black frame, translucent or doubled geometry.
```

### S4_R02

- Selected: attempt 1 of 1; native RGB 1774×887; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R02/S4_R02_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R02/S4_R02_RAW_NATIVE.png` — `8eb68007583a5e50594c2d82cb27378845109e5eb2b966c1504cd2684724ccfa`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R02/S4_R02_MASTER.png` — `8eb68007583a5e50594c2d82cb27378845109e5eb2b966c1504cd2684724ccfa`
- GAME: `assets/environments/site7_v2/stage04/S4_R02/S4_R02_GAME.png` — `336be8401335b7c7b0fef434bd9c6f89002ac17063d55f26af1a68980483acd9`
- Whole-image sRGB factor: 0.725 (log2 -0.463947 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R04/S3_R04_MASTER.png` — `aa3169b38f8ee095744873cc02646040b05983f2309fb844940c111d434505b5`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: opaque RGB standalone SITE-7 stage-4 ROOM plate S4_R02 Forge Gate. Image 1 is S3_R04_MASTER solely for fixed 2:1 dimetric top-down camera, scale, neutral steel floor material, open NE upper-right back-wall threshold and SW lower-left foreground threshold with 300px widths and 195px coplanar aprons. Image 2 is IMAGE_A quality reference solely for premium hard-surface craft, never copy its UI, actors or text. Rebuild a wholly NEW room architectural silhouette, not the damaged bulkhead appearance of image 1. Forge Gate identity: immense stepped forge blast-gate frames built INTO the far NW/NE perimeter walls, deep ribbed refractory bulkheads, riveted heat shields and ingot-transfer rails strictly along wall bases. Strong visual asymmetry with one tall industrial gate tower and smaller opposite shield panels; wall accents ember-orange only, tiny practical lamps. One broad clear walkable elongated hexagonal dark gunmetal SITE-7 deck at least as broad as reference, at least 8% inside every border, 2:1 floor seams at 26.6 degrees; neutral 6000K light uniformly across floor at ~0.20 sRGB brightness. NW/NE back walls, SW/SE only low lip/rail so floor unobscured. Exactly TWO open doorways, NE upper-right in back wall and SW lower-left in rail. No SE or NW openings. Both doors and aprons same neutral deck, no wall blocking threshold. Flat uniform near-black #07090D outside. Do not put any equipment or debris on open floor. No hot spots, color cast, floor shadows/holes, vignette, haze, smoke, text, signage, letters, digits, logos, symbols, arrows, characters, robots, weapons, HUD, UI, translucent/doubled geometry, image border. Crisp richly textured painterly stylized realism, no perspective convergence.
```

### S4_R03

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_RAW_NATIVE.png` — `24195ae066513443ffdbd759e553a6f98f648870c0dfbf6645247a4feacc0c54`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_MASTER.png` — `24195ae066513443ffdbd759e553a6f98f648870c0dfbf6645247a4feacc0c54`
- GAME: `assets/environments/site7_v2/stage04/S4_R03/S4_R03_GAME.png` — `75be4f3f1b42d2f10a7e8c0e873ecdfad20e70c6540ab3aca45d6b618d2e2b7f`
- Whole-image sRGB factor: 0.551 (log2 -0.859876 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R01/S3_R01_MASTER.png` — `2e7561080c39716accd142f3d0a6cca75589d06844069abb2fb0ea2991a5225b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S4_R03. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S4_R03 HEAT-MAP TRACE: noncombat research room. Exactly THREE doors: NE upper-right back wall, SW lower-left lip, SE lower-right lip; NO NW door. Invent an asymmetrical architectural silhouette of stepped thermal-survey console banks, heat-map scanner arrays, heat-probe gantries and angled sensor shutters built into the upper back walls. Red-orange restrained instrument lamps on the walls only. The wall readout surfaces are abstract unlabeled light, NO characters, letters, numerals or maps on walkable floor. Floor footprint can be a broad asymmetric diamond with three fully clear 300px doorway mouths. Distinct from reference pressure-breach wall silhouette and from other forge rooms.
```

### S4_R04

- Selected: attempt 1 of 1; native RGB 1670×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_RAW_NATIVE.png` — `abcb62ad188f4860163fec2c7c0c6d8b8041dd64ba17ed84cfa6a0ca23cc8c24`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_MASTER.png` — `abcb62ad188f4860163fec2c7c0c6d8b8041dd64ba17ed84cfa6a0ca23cc8c24`
- GAME: `assets/environments/site7_v2/stage04/S4_R04/S4_R04_GAME.png` — `f806081c98668d8bb95ff7deac6824cba2962a69456364b3c7a73ca3e3f96479`
- Whole-image sRGB factor: 0.684 (log2 -0.547932 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R02/S3_R02_MASTER.png` — `5b50b42a70d47a19ac3a975a7ae08442ed7e55fab1663f380d6d220b40d4d5e6`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S4_R04. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S4_R04 COOLING LINE elite combat room. Exactly THREE doors: NE upper-right back wall, SW lower-left lip, SE lower-right lip; NO NW door. New wall silhouette of staggered coolant pipe galleries, oversized condensation tanks recessed behind the back walls, a continuous comb of thick heat-exchanger fins and dripping steel wall channels. Pale coolant blue light on the wall fixtures only, no blue tint on the standard steel floor. Asymmetric long hexagonal open arena at least as large as reference, broad enough for enemies to route around cover. NOT a red defense barrier room, no copied panel sequence from image 1. All three door mouths and neutral aprons entirely unobstructed.
```

### S4_R05

- Selected: attempt 2 of 2; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R05/S4_R05_attempt02_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R05/S4_R05_RAW_NATIVE.png` — `612923ba1c4f63d06d4ecbba6427a08bdf71a850caa94d29618d990063d293ac`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R05/S4_R05_MASTER.png` — `612923ba1c4f63d06d4ecbba6427a08bdf71a850caa94d29618d990063d293ac`
- GAME: `assets/environments/site7_v2/stage04/S4_R05/S4_R05_GAME.png` — `0613dabcb2108cebe3f9eae1387bae454ec2941cdad0b551d12efec267b3340c`
- Whole-image sRGB factor: 0.620 (log2 -0.689660 stops); uniform white balance: [0.9800000190734863, 1.0, 1.0199999809265137].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R05/S3_R05_MASTER.png` — `c3a1f3674ac4991efdf75586f58ad09ec0e2af4f8d21bd508cffe84760afa053`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`
- Rejected first candidate retained: `art_src/environments/site7_v2/stage04/_quarantine/S4_R05/S4_R05_attempt01_REJECTED.png` — `c7e394a86d8c2451c40371a983ebf8f1da5f0bf4000c81842f08f5252c8c193a`. Replaced after visual contract review; no rejected pixels were promoted.

Final ImageGen prompt:

```text
Use case: precise-object-edit. Asset type: S4_R05 FORGE WARDEN boss room plate. Image 1 S3_R05 gives ONLY fixed camera, floor scale, standard steel deck and neutral apron proportions. Image 2 IMAGE_A gives material quality only. Image 3 is the rejected forge-press candidate; preserve its new monumental forge press and crucible machinery, orange-white wall lamps, open central floor, crisp dimetric steel material, and its TWO real doorways: SW lower-left and NE upper-right. CRITICAL CORRECTION: image 3 mistakenly shows an extra SE lower-right foreground doorway and protruding deck apron. REMOVE THAT ENTIRE SE DOOR AND EXTERNAL PLATFORM. The entire SE lower-right perimeter must be a single CONTINUOUS waist-high steel railing/lip with no gap and no exit deck beyond it. Exactly TWO open doors remain, SW and NE, each wide with level neutral apron. Do not change their geometry. No NW doorway. Keep complete floor at least 1100x520, evenly lit neutral grey with no orange spill, no floor props. Outside flat #07090D. No text, signs, numbers, symbols, UI, actors, robots, weapons, fog, vignette, black frame. Opaque RGB standalone plate.
```

### S4_R06

- Selected: attempt 2 of 2; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_R06/S4_R06_attempt02_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_R06/S4_R06_RAW_NATIVE.png` — `d80f30d446b1447403de614e8af5800941e8d6c1ffdfbd1e987535c9d5c93cf7`
- MASTER: `art_src/environments/site7_v2/stage04/S4_R06/S4_R06_MASTER.png` — `d80f30d446b1447403de614e8af5800941e8d6c1ffdfbd1e987535c9d5c93cf7`
- GAME: `assets/environments/site7_v2/stage04/S4_R06/S4_R06_GAME.png` — `751b9d8b8e71aeb056265eb565be8726726f37bce478d32915390992abcd4582`
- Whole-image sRGB factor: 0.551 (log2 -0.859876 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R03/S3_R03_MASTER.png` — `65761de9a3486f66efd26831a1745481115a8c961997829ccd50cec9f10a3097`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`
- Rejected first candidate retained: `art_src/environments/site7_v2/stage04/_quarantine/S4_R06/S4_R06_attempt01_REJECTED.png` — `80e7213527f81af0a943fae5a59fcc040fff22dd5058bf1b87813d4eb37501ba`. Replaced after visual contract review; no rejected pixels were promoted.

Final ImageGen prompt:

```text
Use case: precise-object-edit. Asset type: S4_R06 SITE-7 SERVICE LOCK room. Image 1 S3_R03 is the camera, scale and neutral steel floor baseline; image 2 IMAGE_A is material quality only; image 3 is the rejected first candidate to repair. Create a replacement original plate that keeps image 3's excellent green service-airlock wall machinery, its fixed 2:1 dimetric camera, neutral steel floor, and SINGLE open NE upper-right framed back-wall doorway with coplanar neutral apron. CRITICAL CORRECTION: image 3 erroneously has two extra foreground doorways/platform aprons at SW lower-left and SE lower-right. REMOVE BOTH entirely: SW and SE foreground perimeter must each be a SINGLE UNBROKEN CONTINUOUS low steel railing/lip across the whole side, with no gaps, no aprons extending outward, no floor outside the perimeter. DO NOT place a SW or SE door. Do not invent another door on NW. Exactly one NE open door remains. Maintain broad clear >=850x450 floor, even neutral 6000K light across floor, uniform flat near-black outer void. Wall green light stays on wall; no green spill on floor. No text, signs, digits, symbols, UI, actors, robots, floor props, fog, vignette, black frame. Opaque RGB standalone environment plate, not a map layout sheet.
```

### S4_O01

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_O01/S4_O01_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_O01/S4_O01_RAW_NATIVE.png` — `8522e79ae96b18f851cc76abf29e577f963e2479612ac05876eca5f0fd806a07`
- MASTER: `art_src/environments/site7_v2/stage04/S4_O01/S4_O01_MASTER.png` — `8522e79ae96b18f851cc76abf29e577f963e2479612ac05876eca5f0fd806a07`
- GAME: `assets/environments/site7_v2/stage04/S4_O01/S4_O01_GAME.png` — `33c2bb71721ee258785021acf5f396c09b3c0b627997e702003f488cf4c174de`
- Whole-image sRGB factor: 0.558 (log2 -0.841663 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_O01/S3_O01_MASTER.png` — `29e752a322dc6505db685782d4feed59630a408d17e4c143b6b9896754cd480b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S4_O01. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S4_O01 COOLANT CACHE optional noncombat room. Exactly ONE open doorway on NW upper-left BACK WALL, with 300px width and neutral 195px apron; NO NE, SW or SE opening; continuous low front lip on SW and SE. New unusual wall silhouette: sealed vertical coolant canister racks, tall insulated cryo cabinets and manifold refrigeration headers recessed in the back walls, not an armory and no generic crates. Coolant cyan small wall lamps, frosty detail confined to machinery, absolutely no ice or water on the walkable neutral grey steel floor. Spacious clear floor at least 850x450, at least as large as reference, perhaps a clipped asymmetric diamond. Make it visibly different from S3_O01 breached armory and every other stage-4 room.
```

### S4_O02

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage04/S4_O02/S4_O02_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage04/S4_O02/S4_O02_RAW_NATIVE.png` — `40070ad883079929449566244fb1c03ac6189c6543bc47e9e569b7c0d3e70d42`
- MASTER: `art_src/environments/site7_v2/stage04/S4_O02/S4_O02_MASTER.png` — `40070ad883079929449566244fb1c03ac6189c6543bc47e9e569b7c0d3e70d42`
- GAME: `assets/environments/site7_v2/stage04/S4_O02/S4_O02_GAME.png` — `79729573d46b11f267853ef60929bb0349d6d1bfbb89b25edce521769e33e67a`
- Whole-image sRGB factor: 0.587 (log2 -0.768568 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_O02/S3_O02_MASTER.png` — `f7012dae168d513b8a43a692f8eed94c4c699aae5dac9e78338bf92313a7bd9b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S4_O02. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S4_O02 THERMAL OBSERVATORY optional noncombat room. Exactly ONE open doorway in NW upper-left back wall; NO NE, SW or SE door, with continuous front low rail. Entirely NEW back-wall architecture: huge thermal-observation instrument housings, pyrometer arrays with slender optical barrels, large analog recording drums and calibrated heat-exchanger test panels embedded around the back perimeter. No written measurements or numbers anywhere. Amber-white tiny wall lamps and instrument glow only, even neutral deck unaffected. Broad clear floor at least 850x450 and no smaller than reference, more elongated hexagonal footprint and visibly unlike S3_O02 teal resonance-room walls. Keep the NW door and its neutral apron open and obvious.
```

### S5_R01

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R01/S5_R01_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R01/S5_R01_RAW_NATIVE.png` — `94bb303eb5a53d1405ec256e8cdcf3431a85807aa449029b3274a6e082759df3`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R01/S5_R01_MASTER.png` — `94bb303eb5a53d1405ec256e8cdcf3431a85807aa449029b3274a6e082759df3`
- GAME: `assets/environments/site7_v2/stage05/S5_R01/S5_R01_GAME.png` — `58cc684e44461a9ff22ae842b22a8565e51550a7045003ee3638d6a1e55ee952`
- Whole-image sRGB factor: 0.510 (log2 -0.971431 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R01/S3_R01_MASTER.png` — `2e7561080c39716accd142f3d0a6cca75589d06844069abb2fb0ea2991a5225b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R01. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R01 OFFSHORE RELAY noncombat entry. EXACTLY ONE OPEN doorway: NE upper-right back wall with neutral standard-deck 300px mouth and 195px apron. SW and SE foreground edges are unbroken continuous low railings without a gap or external platform, NW back wall is unbroken except wall equipment. New weathered offshore-rig silhouette: salt-streaked bulkheads, large cable drums built into the back walls, angular relay mast bases and shipyard conduit towers along the perimeter. Cold-white tiny wall lamps. No water, puddles or wave pattern on the walking floor; floor remains neutral grey deck under even 6000K light. Open floor at least 850x450 and no smaller than S3_R01. Distinct from S3 pressure-breach red walls, no copied machinery. Uniform flat black outside.
```

### S5_R02

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_RAW_NATIVE.png` — `ae412057c3b8171affcacbb9e7a471bf2e2f0b1ea3eefc2bbf5bdda709f4cffa`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_MASTER.png` — `ae412057c3b8171affcacbb9e7a471bf2e2f0b1ea3eefc2bbf5bdda709f4cffa`
- GAME: `assets/environments/site7_v2/stage05/S5_R02/S5_R02_GAME.png` — `85e95f0dc96f259684ab83661c7b7c5c55a5f0227eb7a2fbcfe1409d78dbf0e9`
- Whole-image sRGB factor: 0.641 (log2 -0.641604 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R05/S3_R05_MASTER.png` — `c3a1f3674ac4991efdf75586f58ad09ec0e2af4f8d21bd508cffe84760afa053`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R02. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R02 RELAY DEFENSE combat arena. Exactly THREE open doors: SW lower-left rail, NE upper-right back wall, SE lower-right rail; NO NW doorway. New architecture of colossal armoured relay pylons and densely banked signal cabinets embedded into the back walls, angular antenna-armor profiles. Cyan restrained practical lights on walls only. Broad open battle floor >=1000x560 and at least as large as reference, three unblocked neutral door aprons. NO round purple iris or anchor machine, no copying image-1 silhouette. The pylons rise from walls and do not occupy central floor; every route can wind around runtime cover. Unique stretched irregular hexagon deck shape, premium hard-surface offshore facility, no painted text.
```

### S5_R03

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R03/S5_R03_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R03/S5_R03_RAW_NATIVE.png` — `60b578a1146b455b65abef8e699225e4bd0ad101010ddaf43e8ec656a4808b86`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R03/S5_R03_MASTER.png` — `60b578a1146b455b65abef8e699225e4bd0ad101010ddaf43e8ec656a4808b86`
- GAME: `assets/environments/site7_v2/stage05/S5_R03/S5_R03_GAME.png` — `726924bbecc2e100af400c4665852d342c56e33ecd69e42eb01c289e176d1d6c`
- Whole-image sRGB factor: 0.715 (log2 -0.483985 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R03/S3_R03_MASTER.png` — `65761de9a3486f66efd26831a1745481115a8c961997829ccd50cec9f10a3097`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R03. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R03 NULL CARRIER TRACE noncombat research room. Exactly TWO open doors: SW lower-left railing and NE upper-right back wall, each 300px wide with neutral 195px apron. SE foreground railing must remain unbroken continuous with NO SE door/platform; NW wall has NO doorway. Fresh asymmetric wall silhouette: carrier-trace signal consoles, large analog oscilloscope banks and angled antenna-feed waveguide boxes arrayed along back walls, all integrated into perimeter. Small pale-violet practical wall lights only, no violet or teal cast on grey floor. Floor open at least 850x450 and at least as large as image 1, elongated diagonal-hexagon shape. Not the same wall panel geometry as S3 carrier lab, no bright teal displays, no painted letters or numbers.
```

### S5_R04

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_RAW_NATIVE.png` — `820864a37d96d22ea7fb28c7c1d29348d7984e7cf682511dbc6f1531d03d5511`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_MASTER.png` — `820864a37d96d22ea7fb28c7c1d29348d7984e7cf682511dbc6f1531d03d5511`
- GAME: `assets/environments/site7_v2/stage05/S5_R04/S5_R04_GAME.png` — `a1602e1ecfab0b9815a8a6fb31e90d4a60588d3d200ba318fa5fb024b6a2a262`
- Whole-image sRGB factor: 0.620 (log2 -0.689660 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R04/S3_R04_MASTER.png` — `aa3169b38f8ee095744873cc02646040b05983f2309fb844940c111d434505b5`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R04. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R04 JAMMER ARRAY elite combat room. Exactly THREE open doors: SW lower-left lip, NE upper-right back wall, SE lower-right lip; NO NW door. New distinctive wall silhouette: ranks of oversized jammer emitter dishes, angular parabolic antenna racks, stacked phase-shift modules and thick signal conduits ONLY along the far back walls, each dish mounted above floor outside the fighting lane. Blue-white small wall practical lamps. Neutral uninterrupted battle floor >=1000x560 and no smaller than reference, all three doors with unobstructed 300px mouths and 195px neutral aprons. Unlike S3_R04 collapsed bulkhead and unlike cyan relay defense, this is a clear antenna-array room. No electronic markings or text on floor.
```

### S5_R05

- Selected: attempt 1 of 1; native RGB 1670×942; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R05/S5_R05_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R05/S5_R05_RAW_NATIVE.png` — `72955052a8cd46657eefc8d8d54b94e57759a20710b55b40889199c3055a8aca`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R05/S5_R05_MASTER.png` — `72955052a8cd46657eefc8d8d54b94e57759a20710b55b40889199c3055a8aca`
- GAME: `assets/environments/site7_v2/stage05/S5_R05/S5_R05_GAME.png` — `433a6b45e1d17999835f7e641062705efe0810a0ec956939a5032df465d127b9`
- Whole-image sRGB factor: 0.750 (log2 -0.415037 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R02/S3_R02_MASTER.png` — `5b50b42a70d47a19ac3a975a7ae08442ed7e55fab1663f380d6d220b40d4d5e6`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R05. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R05 CARRIER NULL boss DEFENSE CORRIDOR. Exactly TWO open doors: SW lower-left foreground entry and NE upper-right back-wall exit; NO SE or NW opening. Unlike the wide diamond room of image 1, make an ELONGATED long defense-line hexagonal corridor along the SW-to-NE dimetric axis, walkable neutral floor at least 1300px long by 380px wide at native scale, wide enough for two operators and enemy flanking, clear all the way to the far NE boss end. Monumental RECTANGULAR framed carrier-aperture machine of STACKED emitter rings (rectilinear array, NOT circular iris) integrated into the far back wall near the NE end, with angular radiation shielding and signal pylons against wall. Red warning practical lamps in the walls only, no red floor cast. NE doorway remains unobstructed beside the aperture. Boss stands at far end in runtime; DO NOT paint boss or any actor. Crisp orthographic 2:1 axes, no perspective taper, no floor markings/text, complete 195px level aprons at both doors, no extra ramps or walls on floor.
```

### S5_R06

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_R06/S5_R06_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_R06/S5_R06_RAW_NATIVE.png` — `2b3be22c936e7c903183538a76d4f1ee1e0d64e94c341aa5c578a636ab1e959c`
- MASTER: `art_src/environments/site7_v2/stage05/S5_R06/S5_R06_MASTER.png` — `2b3be22c936e7c903183538a76d4f1ee1e0d64e94c341aa5c578a636ab1e959c`
- GAME: `assets/environments/site7_v2/stage05/S5_R06/S5_R06_GAME.png` — `04c13dc4c42d476c11040dc4dabbbdb0c6ad438966aaafc015a9ec2f25d85e6d`
- Whole-image sRGB factor: 0.617 (log2 -0.696658 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_R06/S3_R06_MASTER.png` — `dc2c95cefbebcdfed940697ecb61c80ff4d1054e57e6456a67abf303fdda93dc`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_R06. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_R06 TRANSIT ESCAPE terminal. EXACTLY ONE open doorway: SW lower-left foreground railing gap with full neutral 300px mouth and 195px coplanar apron. NO NE doorway: the entire upper-right back wall is SOLID, visibly filled with a sealed transit-capsule berth and aligned guide rails. NO NW or SE doorway; all remaining foreground rail continuous. New dramatic wall silhouette: elongated capsule docking socket sealed in the NE wall, thick vertical guide rails, heavy steel dock clamp machinery, cable hoists and pressure-lock framing, not the green emergency shaft of image 1. Small green practical wall lights only. Broad clear 850x450 neutral deck at least as large as reference. Floor even neutral white, no green cast, floor objects, signs or labels.
```

### S5_O01

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_O01/S5_O01_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_O01/S5_O01_RAW_NATIVE.png` — `ddb5ce9d8f3dd9b0fa47b76d941f71ed16fd84e7688757e8a093813e40a84a56`
- MASTER: `art_src/environments/site7_v2/stage05/S5_O01/S5_O01_MASTER.png` — `ddb5ce9d8f3dd9b0fa47b76d941f71ed16fd84e7688757e8a093813e40a84a56`
- GAME: `assets/environments/site7_v2/stage05/S5_O01/S5_O01_GAME.png` — `cd24c74b88050a8f32d5f83d950a3b29c2b30dec44f662d22e4a2b415d43fdf8`
- Whole-image sRGB factor: 0.612 (log2 -0.708396 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_O01/S3_O01_MASTER.png` — `29e752a322dc6505db685782d4feed59630a408d17e4c143b6b9896754cd480b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_O01. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_O01 TRANSIT STORES optional noncombat room. Exactly ONE open doorway on NW upper-left back wall with its 300px mouth and 195px neutral apron, no door or platform on NE, SW or SE; continuous front rail. New walls have offshore crew emergency lockers, hanging survival-gear racks, sealed life-support packs and foldaway rescue modules BUILT INTO wall bays, unlike breached armory from image 1 and unlike cryogenic coolant cache. Safety-orange small wall lamps and restrained colored accents on fixtures only. Walkable neutral gunmetal floor open, at least 850x450 and no smaller than reference; no free crates or gear on floor, no symbols, signage, words or numbers.
```

### S5_O02

- Selected: attempt 1 of 1; native RGB 1672×941; runtime scale 1.0.
- Source candidate: `art_src/environments/site7_v2/stage05/S5_O02/S5_O02_attempt01_RAW_NATIVE.png`
- RAW: `art_src/environments/site7_v2/stage05/S5_O02/S5_O02_RAW_NATIVE.png` — `51b032ed97eb0f3198b3dd1e2d36595e30cfdd19b62d4d80396d004ad57486d7`
- MASTER: `art_src/environments/site7_v2/stage05/S5_O02/S5_O02_MASTER.png` — `51b032ed97eb0f3198b3dd1e2d36595e30cfdd19b62d4d80396d004ad57486d7`
- GAME: `assets/environments/site7_v2/stage05/S5_O02/S5_O02_GAME.png` — `e057f7ef1ea8266e02159d9bb0f75ebe710d523d0c8e2df9354047a9cdd1ae76`
- Whole-image sRGB factor: 0.597 (log2 -0.744197 stops); uniform white balance: [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_O02/S3_O02_MASTER.png` — `f7012dae168d513b8a43a692f8eed94c4c699aae5dac9e78338bf92313a7bd9b`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Final ImageGen prompt:

```text
Use case: stylized-concept. Asset type: S5_O02. Opaque RGB standalone SITE-7 tactical sci-fi 2.5D ROOM plate. Image 1 is ONLY for camera, scale, neutral steel deck material, doorway/apron construction; DO NOT copy its wall structure, silhouette, equipment or layout. Image 2 is ONLY for premium material/detail quality, NEVER copy its text, UI, people or combat. Fixed near-orthographic three-quarter top-down dimetric 2:1 (26.6 degree) axes with no perspective convergence. NW and NE sides have back walls; SW and SE sides end in low waist-high rail/lip without obscuring floor. Broad completely clear standard dark gunmetal deck, at least as large as image 1 and 8% inward from all frame edges, fine 2:1 panel seams. Every indicated doorway is an open unobstructed 300px passage with a 195px coplanar standard-deck apron, neutral white light continuous through threshold. NO other doorway/opening. Entire walking floor and all door aprons uniformly lit by neutral white 6000K overhead light near 0.20 sRGB mean, neutral grey, NO colored floor cast, pools, hotspots, dark holes, vignette, fog, or props. Accent color is ONLY on wall machinery and small wall lamps; no spill within an adult height of doors. Outside architecture uniform flat near-black #07090D. Premium crisp painterly hard-surface stylized realism, thick industrial steel, dimensional contact shadows. NO text, numbers, letters, signage, logos, symbols, arrows, characters, robots, weapons, UI, HUD, projectiles, explosion, floor clutter, smoke, black frame, translucent or duplicated structures. Unique NEW wall silhouette distinct from image 1 and all other rooms. S5_O02 SIGNAL OBSERVATORY optional noncombat room. Exactly ONE open doorway on NW upper-left back wall, with 300px clear mouth and 195px neutral apron. NO NE, SW, SE doors or extruding platforms; continuous low rail on two front edges. New signature wall silhouette of large enclosed radar dishes, angular sensor-array consoles and protective rotating dish housings at perimeter, plus nested signal waveguide cabinets, unlike S3 teal resonance laboratory and unlike S5 jammer elite combat room. Teal small practical wall lamps; no colored floor spill. Open neutral steel floor at least 850x450 and at least as large as reference; no floor props or painted diagrams. Premium offshore rig research mood, still standard deck and flat near-black outer void.
```

## Stage 5 — dedicated mission 4/5 connectors and mission 2/3 boss replacements

Built-in Codex ImageGen was used for 16 selected plates. The prompt below records the complete normalized production specification and each plate-specific instruction. Candidate files are retained in the project; the earlier boss art and its SHA-256 are in `_superseded/stage5_replaced_boss_manifest.json`. No crop, resize, mirror, or local repaint was applied. GAME has one whole-image sRGB exposure factor and neutral white balance.

### S4_C01

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C01/S4_C01_RAW_NATIVE.png` — `591382b17fffefde7e409a9bb9ceb0c0d3446be30e4550fbe9001a3c4de345f8`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C01/S4_C01_MASTER.png` — `591382b17fffefde7e409a9bb9ceb0c0d3446be30e4550fbe9001a3c4de345f8`
- GAME: `assets/environments/site7_v2/stage04/S4_C01/S4_C01_GAME.png` — `707831dd4cb0f1237448d3fb231d8e7511be75b4d15bc58b9baa543894c95888`
- Whole-image sRGB factor: 0.581 (log2 -0.783390 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C01/S3_C01_MASTER.png` — `fd27acaf44d7f728683c66713427e10072bb2b934a14db0ff1d77eb24154f3bc`
  - `art_src/environments/site7_v2/stage04/S4_R02/S4_R02_MASTER.png` — `8eb68007583a5e50594c2d82cb27378845109e5eb2b966c1504cd2684724ccfa`
  - `art_src/environments/site7_v2/stage04/S4_R01/S4_R01_MASTER.png` — `77b6deb06ec74da4b96c42918ef12b0e6968bafb21fc6bc99f15b03849b594a3`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C01, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from forge blast-gate frames becoming thermal-spine heat-exchange columns, unlike the S3 connector and other new plates. LOWER-LEFT orange wall accent; UPPER-RIGHT amber wall accent. Mission 4 walks this ascending art backward from upper right to lower left.
```

### S4_C02

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C02/S4_C02_RAW_NATIVE.png` — `a92ee8e20a672eacbd16752eb1f712ade630a3d6cda81f7c9e6698b7e7087910`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C02/S4_C02_MASTER.png` — `a92ee8e20a672eacbd16752eb1f712ade630a3d6cda81f7c9e6698b7e7087910`
- GAME: `assets/environments/site7_v2/stage04/S4_C02/S4_C02_GAME.png` — `fbb78b2212989af75dbbcfe4cec04e256a219b7fe81d46c98b8ef74006093c01`
- Whole-image sRGB factor: 0.624 (log2 -0.680382 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C02/S3_C02_MASTER.png` — `095ca21a6544169def06c38356d968c78b67e759833c72fc2803fcccc0fa25fc`
  - `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_MASTER.png` — `24195ae066513443ffdbd759e553a6f98f648870c0dfbf6645247a4feacc0c54`
  - `art_src/environments/site7_v2/stage04/S4_R02/S4_R02_MASTER.png` — `8eb68007583a5e50594c2d82cb27378845109e5eb2b966c1504cd2684724ccfa`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C02, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from heat-map scanner banks becoming forge blast-gate frames, unlike the S3 connector and other new plates. LOWER-LEFT red-orange wall accent; UPPER-RIGHT orange wall accent. Mission 4 walks this ascending art backward from upper right to lower left.
```

### S4_C03

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C03/S4_C03_RAW_NATIVE.png` — `3b086bed37bc3e1a2fc55192298baff5f10f5206c8b04b0dda7594c5d579e573`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C03/S4_C03_MASTER.png` — `3b086bed37bc3e1a2fc55192298baff5f10f5206c8b04b0dda7594c5d579e573`
- GAME: `assets/environments/site7_v2/stage04/S4_C03/S4_C03_GAME.png` — `180a2c26d7539cc23bb223a98d8d8d95cf094846a1d4329cf69e9d812ad20e8b`
- Whole-image sRGB factor: 0.615 (log2 -0.701342 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C03/S3_C03_MASTER.png` — `1aea51af3183451071a467253565103db6608b157065d67f61efeef2972051fa`
  - `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_MASTER.png` — `abcb62ad188f4860163fec2c7c0c6d8b8041dd64ba17ed84cfa6a0ca23cc8c24`
  - `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_MASTER.png` — `24195ae066513443ffdbd759e553a6f98f648870c0dfbf6645247a4feacc0c54`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C03, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from coolant galleries becoming thermal-survey consoles, unlike the S3 connector and other new plates. LOWER-LEFT pale coolant blue wall accent; UPPER-RIGHT red-orange wall accent. Mission 4 walks this ascending art backward from upper right to lower left.
```

### S4_C04

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C04/S4_C04_RAW_NATIVE.png` — `3548c6d0b2166d8733d59598969c5ba2e641031cf509fa74cb56995ce3445664`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C04/S4_C04_MASTER.png` — `3548c6d0b2166d8733d59598969c5ba2e641031cf509fa74cb56995ce3445664`
- GAME: `assets/environments/site7_v2/stage04/S4_C04/S4_C04_GAME.png` — `b3f3a6d2a641302089941924739e5fd7583a2267d1b1d2a78889120fa6c4df31`
- Whole-image sRGB factor: 0.582 (log2 -0.780909 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C04/S3_C04_MASTER.png` — `803bc7f550883f1025e7101cddb7a37888d6592cf4495f9293a7aea0dc373a4e`
  - `art_src/environments/site7_v2/stage04/S4_R05/S4_R05_MASTER.png` — `612923ba1c4f63d06d4ecbba6427a08bdf71a850caa94d29618d990063d293ac`
  - `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_MASTER.png` — `abcb62ad188f4860163fec2c7c0c6d8b8041dd64ba17ed84cfa6a0ca23cc8c24`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C04, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from forge press and crucible feeders becoming coolant-pipe galleries, unlike the S3 connector and other new plates. LOWER-LEFT molten orange-white wall accent; UPPER-RIGHT pale coolant blue wall accent. Mission 4 walks this ascending art backward from upper right to lower left.
```

### S4_C05

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C05/S4_C05_RAW_NATIVE.png` — `a2d198b2f074b1288c67628010a319aa0b4c2331afbb3c97993e32ad9a622cfa`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C05/S4_C05_MASTER.png` — `a2d198b2f074b1288c67628010a319aa0b4c2331afbb3c97993e32ad9a622cfa`
- GAME: `assets/environments/site7_v2/stage04/S4_C05/S4_C05_GAME.png` — `a5ff622b031dbaee649c8bda433a130d94726e2f25487e9efc6857ca935e5a1c`
- Whole-image sRGB factor: 0.669 (log2 -0.579922 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C05/S3_C05_MASTER.png` — `d4db4d2f20f738e5ea850a5a7ab8ad4c99cba60420f0e6d70a42ecdc53755099`
  - `art_src/environments/site7_v2/stage04/S4_R06/S4_R06_MASTER.png` — `d80f30d446b1447403de614e8af5800941e8d6c1ffdfbd1e987535c9d5c93cf7`
  - `art_src/environments/site7_v2/stage04/S4_R05/S4_R05_MASTER.png` — `612923ba1c4f63d06d4ecbba6427a08bdf71a850caa94d29618d990063d293ac`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C05, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from service airlock lock-cycle frames becoming forge press machinery, unlike the S3 connector and other new plates. LOWER-LEFT green wall accent; UPPER-RIGHT molten orange-white wall accent. Mission 4 walks this ascending art backward from upper right to lower left.
```

### S4_C06

- Selected attempt: 1; native RGB 1254×1254; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C06/S4_C06_RAW_NATIVE.png` — `a79fc815baa9c0edb8c55c7192eda926a831de189ba5fde789aba037fff3e28d`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C06/S4_C06_MASTER.png` — `a79fc815baa9c0edb8c55c7192eda926a831de189ba5fde789aba037fff3e28d`
- GAME: `assets/environments/site7_v2/stage04/S4_C06/S4_C06_GAME.png` — `f562182a400d8b45270ef73fd6fe5c58fa651e92d2c36f57da6bcbec956eb70d`
- Whole-image sRGB factor: 0.654 (log2 -0.612637 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C06/S3_C06_MASTER.png` — `adde22992307bb811bf11f43028f9897bf0e46f339bee1728d25060f87c1c318`
  - `art_src/environments/site7_v2/stage04/S4_R03/S4_R03_MASTER.png` — `24195ae066513443ffdbd759e553a6f98f648870c0dfbf6645247a4feacc0c54`
  - `art_src/environments/site7_v2/stage04/S4_O01/S4_O01_MASTER.png` — `8522e79ae96b18f851cc76abf29e577f963e2479612ac05876eca5f0fd806a07`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C06, 1254×1254. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from upper-left to lower-right (descending), authored without mirroring, constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-right side and the waist-high railing is on the lower-left side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from heat-map scanner banks becoming sealed coolant canister and cryo racks, unlike the S3 connector and other new plates. UPPER-LEFT red-orange wall accent; LOWER-RIGHT coolant cyan wall accent.
```

### S4_C07

- Selected attempt: 1; native RGB 1254×1254; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage04/S4_C07/S4_C07_RAW_NATIVE.png` — `9846b46e846a01be8bd0c852a0938c2a91bb60c36794db0f252477b8de52748b`
- MASTER: `art_src/environments/site7_v2/stage04/S4_C07/S4_C07_MASTER.png` — `9846b46e846a01be8bd0c852a0938c2a91bb60c36794db0f252477b8de52748b`
- GAME: `assets/environments/site7_v2/stage04/S4_C07/S4_C07_GAME.png` — `734dde9432e8db7e087bd32337b36a99fbba535a17e99e67bf7e434d82b2afc7`
- Whole-image sRGB factor: 0.653 (log2 -0.614845 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C07/S3_C07_MASTER.png` — `2d80fc78b6b30fc011789ffac9a31f6172b68e5166b627aa7bd446351ab04c2e`
  - `art_src/environments/site7_v2/stage04/S4_R04/S4_R04_MASTER.png` — `abcb62ad188f4860163fec2c7c0c6d8b8041dd64ba17ed84cfa6a0ca23cc8c24`
  - `art_src/environments/site7_v2/stage04/S4_O02/S4_O02_MASTER.png` — `40070ad883079929449566244fb1c03ac6189c6543bc47e9e569b7c0d3e70d42`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S4_C07, 1254×1254. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from upper-left to lower-right (descending), authored without mirroring, constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-right side and the waist-high railing is on the lower-left side over the void. FORGE DESCENT: riveted heat-shield cladding, glowing slag channels behind heavy back-wall grilles, heat-exchanger ribs. Wall structures change from cooling pipe galleries becoming pyrometer arrays and recording drums, unlike the S3 connector and other new plates. UPPER-LEFT pale coolant blue wall accent; LOWER-RIGHT amber-white wall accent.
```

### S5_C01

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C01/S5_C01_RAW_NATIVE.png` — `0ef7f3c7788691a237cb094b86bd619533f1925e159de28a52c0c4b53ce9f85d`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C01/S5_C01_MASTER.png` — `0ef7f3c7788691a237cb094b86bd619533f1925e159de28a52c0c4b53ce9f85d`
- GAME: `assets/environments/site7_v2/stage05/S5_C01/S5_C01_GAME.png` — `96a40db99d3dcfd0b3e6b151382a50a125c7b6767eedd94e7325ecb62205601e`
- Whole-image sRGB factor: 0.565 (log2 -0.823677 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C01/S3_C01_MASTER.png` — `fd27acaf44d7f728683c66713427e10072bb2b934a14db0ff1d77eb24154f3bc`
  - `art_src/environments/site7_v2/stage05/S5_R01/S5_R01_MASTER.png` — `94bb303eb5a53d1405ec256e8cdcf3431a85807aa449029b3274a6e082759df3`
  - `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_MASTER.png` — `ae412057c3b8171affcacbb9e7a471bf2e2f0b1ea3eefc2bbf5bdda709f4cffa`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C01, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from offshore relay masts and cable drums becoming armored relay pylons, unlike the S3 connector and other new plates. LOWER-LEFT cold white wall accent; UPPER-RIGHT cyan wall accent.
```

### S5_C02

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C02/S5_C02_RAW_NATIVE.png` — `165ee7b9826c65d1d4fa655fd6a1785f3c141ba27de6dc384cfbf54a8817f69c`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C02/S5_C02_MASTER.png` — `165ee7b9826c65d1d4fa655fd6a1785f3c141ba27de6dc384cfbf54a8817f69c`
- GAME: `assets/environments/site7_v2/stage05/S5_C02/S5_C02_GAME.png` — `038503ba1c76d06f3f5ecee1884ea07553b7b2256848400c86832d13fad2e53f`
- Whole-image sRGB factor: 0.549 (log2 -0.865122 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C02/S3_C02_MASTER.png` — `095ca21a6544169def06c38356d968c78b67e759833c72fc2803fcccc0fa25fc`
  - `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_MASTER.png` — `ae412057c3b8171affcacbb9e7a471bf2e2f0b1ea3eefc2bbf5bdda709f4cffa`
  - `art_src/environments/site7_v2/stage05/S5_R03/S5_R03_MASTER.png` — `60b578a1146b455b65abef8e699225e4bd0ad101010ddaf43e8ec656a4808b86`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C02, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from armored relay cabinets becoming carrier-trace oscilloscope banks, unlike the S3 connector and other new plates. LOWER-LEFT cyan wall accent; UPPER-RIGHT pale violet wall accent.
```

### S5_C03

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C03/S5_C03_RAW_NATIVE.png` — `dc5e9ca9fa3bfbac579bcbe7624cadf756a3aeffbd0747ee11985173144633ad`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C03/S5_C03_MASTER.png` — `dc5e9ca9fa3bfbac579bcbe7624cadf756a3aeffbd0747ee11985173144633ad`
- GAME: `assets/environments/site7_v2/stage05/S5_C03/S5_C03_GAME.png` — `96b98d1460d606406cd97e0ec2e29ce420d481f255c036d65b25a53bc85afa8b`
- Whole-image sRGB factor: 0.620 (log2 -0.689660 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C03/S3_C03_MASTER.png` — `1aea51af3183451071a467253565103db6608b157065d67f61efeef2972051fa`
  - `art_src/environments/site7_v2/stage05/S5_R03/S5_R03_MASTER.png` — `60b578a1146b455b65abef8e699225e4bd0ad101010ddaf43e8ec656a4808b86`
  - `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_MASTER.png` — `820864a37d96d22ea7fb28c7c1d29348d7984e7cf682511dbc6f1531d03d5511`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C03, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from carrier-trace consoles becoming jammer emitter dishes, unlike the S3 connector and other new plates. LOWER-LEFT pale violet wall accent; UPPER-RIGHT blue-white wall accent.
```

### S5_C04

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C04/S5_C04_RAW_NATIVE.png` — `0b4311505479ae7cbbc734f4a997c14d39a74d731656b30f303aad635426e1e5`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C04/S5_C04_MASTER.png` — `0b4311505479ae7cbbc734f4a997c14d39a74d731656b30f303aad635426e1e5`
- GAME: `assets/environments/site7_v2/stage05/S5_C04/S5_C04_GAME.png` — `5edfc032d42507a740b233d99c87da9ceb79b908bd291491e18fc6272d009225`
- Whole-image sRGB factor: 0.542 (log2 -0.883635 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C04/S3_C04_MASTER.png` — `803bc7f550883f1025e7101cddb7a37888d6592cf4495f9293a7aea0dc373a4e`
  - `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_MASTER.png` — `820864a37d96d22ea7fb28c7c1d29348d7984e7cf682511dbc6f1531d03d5511`
  - `art_src/environments/site7_v2/stage05/S5_R05/S5_R05_MASTER.png` — `72955052a8cd46657eefc8d8d54b94e57759a20710b55b40889199c3055a8aca`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C04, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from jammer dishes becoming rectangular carrier-aperture feeder housings, unlike the S3 connector and other new plates. LOWER-LEFT blue-white wall accent; UPPER-RIGHT warning red wall accent.
```

### S5_C05

- Selected attempt: 1; native RGB 1774×887; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C05/S5_C05_RAW_NATIVE.png` — `956ed6a1569b80cdc2d1d25cca5e33306a0cafda419f52cbb0acdc7d996e813c`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C05/S5_C05_MASTER.png` — `956ed6a1569b80cdc2d1d25cca5e33306a0cafda419f52cbb0acdc7d996e813c`
- GAME: `assets/environments/site7_v2/stage05/S5_C05/S5_C05_GAME.png` — `8ec7e546bb97da35141bb20e8c897e671a79c6e67c751aa6a24322e758ea8541`
- Whole-image sRGB factor: 0.535 (log2 -0.902389 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C05/S3_C05_MASTER.png` — `d4db4d2f20f738e5ea850a5a7ab8ad4c99cba60420f0e6d70a42ecdc53755099`
  - `art_src/environments/site7_v2/stage05/S5_R05/S5_R05_MASTER.png` — `72955052a8cd46657eefc8d8d54b94e57759a20710b55b40889199c3055a8aca`
  - `art_src/environments/site7_v2/stage05/S5_R06/S5_R06_MASTER.png` — `2b3be22c936e7c903183538a76d4f1ee1e0d64e94c341aa5c578a636ab1e959c`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C05, 1774×887. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from lower-left to upper-right (ascending), constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-left side and the waist-high railing is on the lower-right side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from rectangular carrier-aperture feeders becoming transit-capsule escape rails, unlike the S3 connector and other new plates. LOWER-LEFT warning red wall accent; UPPER-RIGHT green wall accent.
```

### S5_C06

- Selected attempt: 1; native RGB 1254×1254; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C06/S5_C06_RAW_NATIVE.png` — `cc0705de0012f22ba1c7c3c7a32f05fd1c0934dd4d0443f13be45d64c3007af9`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C06/S5_C06_MASTER.png` — `cc0705de0012f22ba1c7c3c7a32f05fd1c0934dd4d0443f13be45d64c3007af9`
- GAME: `assets/environments/site7_v2/stage05/S5_C06/S5_C06_GAME.png` — `9118ecdca3118915357991963e6199d7d10ad62e339debe0e482150db38653c6`
- Whole-image sRGB factor: 0.620 (log2 -0.689660 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C06/S3_C06_MASTER.png` — `adde22992307bb811bf11f43028f9897bf0e46f339bee1728d25060f87c1c318`
  - `art_src/environments/site7_v2/stage05/S5_R02/S5_R02_MASTER.png` — `ae412057c3b8171affcacbb9e7a471bf2e2f0b1ea3eefc2bbf5bdda709f4cffa`
  - `art_src/environments/site7_v2/stage05/S5_O01/S5_O01_MASTER.png` — `ddb5ce9d8f3dd9b0fa47b76d941f71ed16fd84e7688757e8a093813e40a84a56`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C06, 1254×1254. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from upper-left to lower-right (descending), authored without mirroring, constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-right side and the waist-high railing is on the lower-left side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from relay-defense signal cabinets becoming offshore crew emergency lockers, unlike the S3 connector and other new plates. UPPER-LEFT cyan wall accent; LOWER-RIGHT safety orange wall accent.
```

### S5_C07

- Selected attempt: 1; native RGB 1254×1254; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage05/S5_C07/S5_C07_RAW_NATIVE.png` — `aacf9cc701248ad03f6fef981549e6c3cae1ce71d0a5e1c51e0e583cabc05847`
- MASTER: `art_src/environments/site7_v2/stage05/S5_C07/S5_C07_MASTER.png` — `aacf9cc701248ad03f6fef981549e6c3cae1ce71d0a5e1c51e0e583cabc05847`
- GAME: `assets/environments/site7_v2/stage05/S5_C07/S5_C07_GAME.png` — `436a0be048fd9802f8246dc8fab7694b1f69b2e6661e56c256b7c69feb6aa401`
- Whole-image sRGB factor: 0.656 (log2 -0.608232 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/stage03/S3_C07/S3_C07_MASTER.png` — `2d80fc78b6b30fc011789ffac9a31f6172b68e5166b627aa7bd446351ab04c2e`
  - `art_src/environments/site7_v2/stage05/S5_R04/S5_R04_MASTER.png` — `820864a37d96d22ea7fb28c7c1d29348d7984e7cf682511dbc6f1531d03d5511`
  - `art_src/environments/site7_v2/stage05/S5_O02/S5_O02_MASTER.png` — `51b032ed97eb0f3198b3dd1e2d36595e30cfdd19b62d4d80396d004ad57486d7`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished production connector plate S5_C07, 1254×1254. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only the exact canvas, camera, deck width/length, diagonal axis and clean edge cuts; do not copy its wall silhouette. Images 2 and 3 supply adjacent room door scale and wall identity; Image 4 supplies only finish quality. Draw ONE straight deck from upper-left to lower-right (descending), authored without mirroring, constant about 300px width, cut cleanly at both image edges at full brightness with no fade, end wall or door. The back wall is on the upper-right side and the waist-high railing is on the lower-left side over the void. OFFSHORE RIG GANGWAY: salt-streaked bulkheads, cable trays, storm louvres, caged rig lamps and an open-grate gangway railing. Wall structures change from jammer antenna racks becoming radar and sensor-array consoles, unlike the S3 connector and other new plates. UPPER-LEFT blue-white wall accent; LOWER-RIGHT teal wall accent.
```

### S2_R05

- Selected attempt: 2; native RGB 1672×941; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage02/S2_R05/S2_R05_RAW_NATIVE.png` — `505a18038c6259dadd96af38f6e002b6de2a87c5417c2f47d36bccf588f79e89`
- MASTER: `art_src/environments/site7_v2/stage02/S2_R05/S2_R05_MASTER.png` — `505a18038c6259dadd96af38f6e002b6de2a87c5417c2f47d36bccf588f79e89`
- GAME: `assets/environments/site7_v2/stage02/S2_R05/S2_R05_GAME.png` — `a5f2941fa725c6822fddae7ec919d17820bb6b8c5a4ce4099a19ac7848dd9224`
- Whole-image sRGB factor: 0.595 (log2 -0.749038 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/_superseded/S2_R05/S2_R05_MASTER.png` — `ef69ee88e99612c4c8eb7a5de8da79ea6e580168758a24854d32267c2f264017`
  - `art_src/environments/site7_v2/stage02/S2_R04/S2_R04_MASTER.png` — `7d15d22a6d734813f69fca8f398980650dc08a80f741220f709fed02bd3478fb`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished replacement boss room plate S2_R05, 1672×941. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only size, camera, standard open boss floor footprint, doorway positions and apron construction. Never copy its round violet iris, concentric rings, circular portal, wall machinery or silhouette. Image 2 supplies wall material and scale; Image 3 quality. NW and NE sides have back walls; SW and SE have only low railings so the floor stays visible. Sublevel Relay: sunken relay pit, tall rectangular relay-transformer stacks, cable risers and drained sump grilles set into the NW/NE back walls around a broad dry open arena; crimson perimeter wall lamps. Exactly two open doors SW and NE, each about 300px with a 195px coplanar neutral steel apron. Central floor stays completely open and unobstructed, at least 1100×520 runtime pixels. No round iris, concentric rings, radial hub, circular portal, closed door or shutter.
```

### S3_R05

- Selected attempt: 2; native RGB 1672×941; runtime scale 1.0.
- RAW: `art_src/environments/site7_v2/stage03/S3_R05/S3_R05_RAW_NATIVE.png` — `645d2dce5c824dc85e22e8aa6428a286e8b5c2f8a68139ac0666eefb6e438e50`
- MASTER: `art_src/environments/site7_v2/stage03/S3_R05/S3_R05_MASTER.png` — `645d2dce5c824dc85e22e8aa6428a286e8b5c2f8a68139ac0666eefb6e438e50`
- GAME: `assets/environments/site7_v2/stage03/S3_R05/S3_R05_GAME.png` — `3e603b0782db23faed94e2214166cef4aba0e0e85b30cd1e5210f1fa920a2b63`
- Whole-image sRGB factor: 0.666 (log2 -0.586406 stops); white balance [1.0, 1.0, 1.0].
- Reference images and SHA-256:
  - `art_src/environments/site7_v2/_superseded/S3_R05/S3_R05_MASTER.png` — `c3a1f3674ac4991efdf75586f58ad09ec0e2af4f8d21bd508cffe84760afa053`
  - `art_src/environments/site7_v2/stage03/S3_R04/S3_R04_MASTER.png` — `aa3169b38f8ee095744873cc02646040b05983f2309fb844940c111d434505b5`
  - `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png` — `435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de`

Full normalized ImageGen prompt:

```text
Use case: stylized-concept. Asset type: one finished replacement boss room plate S3_R05, 1672×941. Premium opaque RGB 2.5D tactical science-fiction SITE-7 environment plate for SABLE CIRCUIT. Fixed near-orthographic three-quarter top-down dimetric camera; floor seams and wall bases run at exactly 2:1 slope (26.6 degrees) in both directions, without perspective convergence. One continuous, empty standard dark gunmetal steel deck with fine square-panel seams, light wear, and uniform neutral-white overhead illumination. The walkable steel remains neutral grey with no tint, floor pools, dark holes, vignette, fog, water, or objects. Accent colours appear on perimeter walls, machinery, and small practical lamps only. Outside architecture is flat near-black #07090D. Hard-surface stylized realism with thick steel, dimensional detail and contact shadows. Exclude people, characters, robots, weapons, UI, HUD, text, letters, signage, numbers, logos, smoke, explosions, floor clutter, translucent/doubled geometry, and black frames. Image 1 supplies only size, camera, standard open boss floor footprint, doorway positions and apron construction. Never copy its round violet iris, concentric rings, circular portal, wall machinery or silhouette. Image 2 supplies wall material and scale; Image 3 quality. NW and NE sides have back walls; SW and SE have only low railings so the floor stays visible. Anchor Remnant: shattered giant signal-anchor mast stump, split angular armored housings, severed thick conduit bundles, emergency clamp frames and pressure-relief vents braced along the NW/NE back walls; ice-white arc lamps. Exactly three open doors SW, NE and SE, each about 300px with a 195px coplanar neutral steel apron. Central floor stays completely open and unobstructed, at least 1100×520 runtime pixels. No round iris, concentric rings, radial hub, circular portal, closed door or shutter.
```
