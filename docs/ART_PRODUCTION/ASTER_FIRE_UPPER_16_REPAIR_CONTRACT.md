# ASTER FIRE UPPER 16 — MIDPOINT REPAIR CONTRACT

Status: implementation gate, not visual approval.  The live 8-direction V6
fallback remains authoritative until every dependency below passes atomically.

## Rejected construction

The prior SSE, SSW, NNW, and NNE frames were made by shearing a 384px axial
upper.  They improved pixel connectivity but did not create a true 22.5-degree
view.  Body/head/hair anisotropy reached roughly 1.20, direction-boundary jumps
were strongly asymmetric, and SSE F00/F05 contained two muzzle-hardware
clusters.  This construction is non-promotable.

## Locked source and motion roles

- Visual identity/costume: native 1254px ASTER aim masters and
  `ASTER_COMBAT_SUIT_C01`.
- Pose/depth/occlusion: Blender 5.2.1 headless guide only.
- Motion timing: UAL1 `Jog_Fwd_Loop` remains the lower-body motion source.
- Qwen/ComfyUI repair route: retired for the active midpoint repair. Do not
  launch it or use it for any new frame. Deterministic source-art assembly and
  human-verified project-local masks remain the active path; any later local
  seam repair requires a separately recorded commercially eligible model gate.
  F01–F05 are never independently generated.
- Final runtime: deterministic RGBA frames and atlases derived from the locked
  static midpoint masters.

No Blender proxy or UAL preview mesh is visible in the final character.

## Four midpoint parents

| Direction | Geometry parents | Rigid rifle/hands parent | Solved rig yaw |
|---|---|---|---:|
| SSE | SE + S | SE | 342.7° |
| SSW | S + SW | SW | 287.3° |
| NNW | NW + N | NW | 162.7° |
| NNE | N + NE | NE | 107.3° |

The target screen angles are respectively 67.5°, 112.5°, 247.5°, and 292.5°.
The guide solver must record a screen-tangent error no greater than 0.1°.

## Native part and occlusion contract

All masks are native 1254×1254:

`SUBJECT`, `HAIR_BACK`, `BODY_CORE`, `HEAD_FACE`, `HAIR_FRONT`,
`ARM_TRIGGER_UPPER`, `ARM_SUPPORT_UPPER`, `RIFLE`,
`TRIGGER_FOREARM_HAND`, `SUPPORT_FOREARM_HAND`, `SHOULDER_PLATE`,
`ANATOMICAL_LEFT_WHITE_LEG_MODULE`, `OPPOSITE_STRAPS_POUCH_LEG`,
`BOOTS_ACCESSORIES`, `SHOULDER_ELBOW_SEAM_BRIDGE`, `TARGET_OCCLUDE`, and
`TARGET_REVEAL`.

`RIFLE | TRIGGER_FOREARM_HAND | SUPPORT_FOREARM_HAND` is one rigid similarity
cluster.  The gun, hands, and forearms may not be transformed independently.
Only the native 6–12px shoulder/elbow seam band may be locally repaired.
Anatomical-left/right costume modules never mirror by screen side.

Hair-back stays behind torso/head and hair-front stays in front of face/neck.
The rifle cluster is in front of the body for SSE/SSW and behind it for
NNW/NNE; internal hand/rifle ordering is inherited from the diagonal parent.

## Required lineage

The live build path must consume the native midpoint master records.  A helper
that is merely defined but not called is not evidence.  The manifest records,
for every direction:

- native visual-authority path, dimensions, and SHA-256;
- Blender guide/landmark/depth/occlusion paths and SHA-256;
- local-edit input/output paths and SHA-256 when Qwen was used;
- static-master path and SHA-256;
- deterministic F00–F05 derivation and hashes;
- runtime atlas and muzzle-alignment hashes;
- source, runtime-cell, gameplay-display, and review resolutions.

## Objective gate

- Four native midpoint static masters exist before phase expansion.
- Source/part masks are 1254×1254; no low-resolution upscale is accepted.
- Exact green source exterior is `#00FF00`; runtime output is genuine RGBA.
- Costume is `ASTER_COMBAT_SUIT_C01`; rifle count is exactly one.
- Part-mask union misses/overlaps zero subject pixels outside declared seam and
  occlusion bands.
- Mesh triangle flips: 0.
- Body/head/hair local anisotropy: at most 1.08.
- Rigid-cluster singular-value ratio: at most 1.02.
- All 48 midpoint phase frames have one connected hand→barrel→muzzle path.
- Muzzle-hardware cluster count: exactly 1.
- Barrel tangent residual: target at most 4°, hard limit 6°.
- Runtime 384px barrel centreline gap: at most 2px.
- Native/runtime barrel support: at least 0.85 / 0.75.
- F00 and F05 are byte-identical.
- Each midpoint's larger half-jump is at most 0.8× its former 45° jump, and
  half-jump imbalance is at most 1.4.
- At 131px gameplay scale the silhouette and single rifle remain legible.

Technical PASS does not grant visual PASS.  The final static/contact results
remain `USER_REVIEW_REQUIRED` until reviewed.

## Native visual evidence

Use a 1920×1440 review frame so the 1254×1254 source can be shown at 1:1:

- header: `(0, 0, 1920, 64)`;
- native source: `(24, 88, 1254, 1254)`;
- runtime 384px 1:1: `(1302, 88, 384, 384)`;
- gameplay 131px 1:1: `(1710, 88, 131, 131)`;
- metadata: `(1302, 496, 594, 846)`.

Every current contact/review frame and video must also pass
`tools/art_pipeline/validate_visual_evidence_1080p.py`.  A large review
container never converts an enlarged low-resolution source into quality proof.
