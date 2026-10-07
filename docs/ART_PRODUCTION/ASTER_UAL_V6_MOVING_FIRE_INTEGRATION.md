# ASTER UAL V6 locomotion and moving-fire integration

## Gate status

- Failure baseline commit `5dbae66` remains **VISUAL FAIL / technical QA PASS / production HOLD**. The low-poly/block-body result is not rehabilitated by this work.
- Move V5 remains **VISUAL FAIL** for leg amplitude. Its frame cursor advanced technically, but the legs read as fixed/skating at gameplay scale.
- Move V6 visible-leg metric gate: **PASS** across all eight authored facing directions.
- Composite Fire V6 costume-continuity gate: **PASS**.
- V7 muzzle/socket technical gate: **PASS** in Godot and HTML evidence.
- Historical Godot moving-fire behavior capture: **PASS** for the bounded eight-sector runtime contract, but its 1280×720 frames and sub-1080 contacts are no longer current visual evidence.
- Current native-1080 evidence gate: **HOLD** until the updated 1920×1080 capture harness regenerates the runtime frames and contacts.
- True aim-relative strafe/backpedal: **HOLD_NOT_PROVEN**.
- Human visual review: **REQUIRED**.
- ASTER Pilot and production expansion: **HOLD** until human review; the technical and metric passes below are not a production visual PASS.

## Authorities and prohibited dependencies

Character identity, costume, rifle, and material authority remain the accepted SABLE ASTER raster sources. Motion authority is only the installed Quaternius UAL1 FREE Standard `Jog_Fwd_Loop`. V6 consumes the 24-sample headless Blender curve export already established by V5:

```text
art_src/pilot_v2/aster_v2/animation_360/ual_locomotion_v5/ASTER_UAL1_LOCOMOTION_CURVES_V5.json
```

UAL2 is not used by this slice. No UAL preview mesh, Universal Base Character, mannequin, base-character pack, paid/Pro/Source model, Krea/Krea2 asset, or Photoshop asset is introduced. V6 invokes no cloud generation and deforms the already accepted raster authority rather than generating a replacement body. Blender is a headless motion/pose-data tool here; no Blender UI operation or Blender preview body is exposed as the final character.

## Move V6 assets

Runtime atlases:

```text
assets/units/operators/aster/move_360_ual_v6/{D}/ASTER_MOVE_{D}_360_UAL_V6_ATLAS.webp
assets/units/operators/aster/move_360_ual_v6/{D}/ASTER_MOVE_{D}_360_UAL_V6_MANIFEST.json
```

Authoring evidence:

```text
art_src/pilot_v2/aster_v2/animation_360/move_360_ual_v6/
art_src/pilot_v2/aster_v2/animation_360/move_360_ual_v6/ASTER_MOVE_360_UAL_V6_MANIFEST.json
art_src/pilot_v2/aster_v2/animation_360/move_360_ual_v6/ASTER_MOVE_360_UAL_V6_MOTION_CONTACT.png
```

Asset contract:

- Directions: `E, SE, S, SW, W, NW, N, NE`
- Frames: 24 per direction
- Playback: 24 fps
- Cell: 384 x 384
- Atlas: 384 x 9216 lossless RGBA WebP per direction
- Adjacent-frame runtime alpha crossfade: disabled
- UAL source: UAL1 Standard `Jog_Fwd_Loop`
- Lower construction: audited ASTER-specific hip/knee/ankle/toe landmarks, isolated left/right chains, two-bone IK, UAL contact/lift and boot-pitch data
- Upper construction: rigid ASTER raster authority; hands/rifle/muzzle are excluded from lower-body deformation

Key hashes:

```text
V6 root manifest  c733a679808643e303c4f37212c79136aec3f34344bc2d270daa2ee818f1cc8c
V6 contact sheet  495393fcf5c2262af889ea3caa65fdd6aeb3f8429d42501717bf1a2be9f63991
V6 generator      9ad99b737cb44836e1dd610d9e48365dce5bfc61941946cbd45c1cc70c32be0f
```

V5 and the immediate previous V6 candidate remain comparison/rollback evidence. They are not selected when the complete V6 bundle is valid.

## Visible-leg QA

Independent decoded-atlas audit:

```text
artifacts/aster_ual_v6_visible_leg_audit/ASTER_MOVE_360_UAL_V6_VISIBLE_MOTION_QA.json
artifacts/aster_ual_v6_visible_leg_audit/ASTER_MOVE_360_UAL_V6_VISIBLE_MOTION_CONTACT_PASSING_UP_MONTAGE.png
```

QA JSON SHA-256:

```text
498964787664ceb4294f0fe6d6456faf44bda01f70e277281f002b9f3413091d
```

The validator registers out rigid upper-body displacement and measures the actual decoded lower-body alpha components at runtime display scale `0.34`; it does not infer motion from frame indices. Final V6 results:

- Eight directions present: PASS
- Visible-leg primary gate: PASS
- Auxiliary costume/weapon gate: PASS
- Combined visible-asset gate: PASS
- Failed directions: none
- Generated-control boot trajectories: 14.92-25.39 runtime px
- Generated-control knee trajectories: 9.53-18.28 runtime px
- Median adjacent boot motion: 0.89-2.04 runtime px
- Toe clearance: 8.55-9.37 runtime px
- Rifle core drift: RGB 0, alpha at most 1
- Visible green spill pixels: 0
- Full silhouette area drift: 2.75%-6.17%
- Complementary pre-deformation partition error: premultiplied RGB at most `1.53e-5`, alpha 0

The sampled contact frames `F00/F04/F08/F12/F16/F20` visibly expose contact, passing, swing/lift, and alternating knee flex. These metric gates reject the V5 frozen-leg failure, but the audit still records `human_visual_review: REQUIRED_AFTER_METRIC_GATE` and `production_expansion: HOLD`.

## Composite Fire V6 and costume lock

Moving fire uses a continuously advancing V6 lower layer and the accepted six-frame fire upper layer:

```text
assets/units/operators/aster/composite_fire_v6/
  move_lower/{D}/ASTER_MOVE_{D}_LOWER_V6_ATLAS.webp
  idle_lower/{D}/ASTER_IDLE_{D}_LOWER_V6_ATLAS.webp
  fire_upper/{D}/ASTER_FIRE_{D}_UPPER_V6_ATLAS.webp
assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json
```

Evidence:

```text
art_src/pilot_v2/aster_v2/animation_360/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_CONTACT.png
art_src/pilot_v2/aster_v2/animation_360/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_COSTUME_REGRESSION_CONTACT.png
artifacts/aster_costume_drift_141411/ASTER_COSTUME_CONTINUITY_V6_QA.json
artifacts/aster_costume_drift_141411/ASTER_W_COSTUME_V6_BEFORE_FIRE_AFTER.png
```

- Composite manifest SHA-256: `907a535b0ae28311078b5f521a5115a92724f864398c5528f010ce81b79bf01b`
- Costume QA SHA-256: `6adfdf3edf997aa063b607bea2422cf81ad2e0aa7ef9bfa988eff9d1676bdfbc`
- 1,344/1,344 lower/upper frame pairs scanned
- Hard lower-costume exact retention: 1.0
- White/cyan exact retention: 1.0
- Mismatch, missing-panel, and disconnected-ownership failures: 0
- W anatomical-left white/cyan thigh/boot panel remains present before, during, and after Fire
- S downward rifle/muzzle cage remains upper-authority geometry; no green shard, waist hole, or duplicated pelvis is accepted

Muzzle flash is a separate runtime VFX. It is never baked into idle, move, or base fire body frames.

## V7 muzzle and projectile alignment

Shared authority:

```text
assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json
```

SHA-256:

```text
b90e83776d27f4bc4c2811d0426da8ad38eaf65b340aac1a1e04e53b3c042e14
```

The contract records the visible muzzle point and barrel tangent from Fire contact frame `2` (`recoil_contact_clean`) for all eight directions. Godot and the interactive HTML load this same JSON. The character raster remains in its authored sector; the projectile, tracer, and flash preserve continuous gameplay aim.

At fire time, the runtime snapshots the authored socket, sector, and continuous aim. Flash appears immediately for 60 ms and projectile birth uses the same socket. Post-shot aim changes do not teleport an existing burst. The V7 evidence passed both Godot-side geometry validation and an eight-direction HTML runtime capture:

```text
artifacts/aster_muzzle_alignment_v7/ASTER_MUZZLE_ALIGNMENT_V7_EVIDENCE.json
artifacts/aster_muzzle_alignment_v7/ASTER_MUZZLE_ALIGNMENT_V7_CONTACT.png
artifacts/aster_muzzle_alignment_v7/ASTER_HTML_MUZZLE_ALIGNMENT_V7_EVIDENCE.json
```

## Godot runtime integration

Relevant paths:

```text
project.godot
scenes/actors/player/OperatorActor.tscn
scripts/animation/aster_v4_locomotion_preview.gd
scripts/actors/operator_actor.gd
scripts/combat/prototype_projectile.gd
```

- `project.godot` enables `sable_visuals/aster_v4_locomotion_preview`.
- `OperatorActor.tscn` owns the `AsterV4LocomotionPreview` node.
- `aster_v4_locomotion_preview.gd` loads all eight Move V6, Idle-lower V6, Move-lower V6, and Fire-upper V6 atlases as one atomic bundle.
- A partial V6 set is never mixed with V5. If the complete V6 bundle is unavailable or invalid, the loader falls back coherently to V5, then the V4 fallback family.
- When V6 is valid, the runtime contract reports `move_360_ual_v6` and `composite_fire_v6`.
- During moving fire, the 24-frame lower cursor continues while the six-frame upper fire sequence starts at contact/recoil.
- `operator_actor.gd` resolves the shot sector from current aim in the firing tick and uses the preview's authored global muzzle position for projectile birth.
- Projectile collision, damage, speed, lifetime, cadence, gameplay aim, save, progression, and combat-rule authority are unchanged.
- Projectile contact continues to own `CombatFeedback.spawn_hit(...)`; projectile code must not call `spawn_hurt(...)`.

QA entry points:

```text
tests/smoke/aster_v4_locomotion_preview_smoke.gd
tests/render/aster_ual_v6_moving_fire_capture.gd
```

Non-headless Godot evidence:

```text
artifacts/aster_ual_v6_moving_fire_capture/ASTER_UAL_V6_8_DIRECTION_LEG_PHASE_CONTACT.png
artifacts/aster_ual_v6_moving_fire_capture/ASTER_UAL_V6_8_DIRECTION_MOVING_FIRE_CONTACT.png
artifacts/aster_ual_v6_moving_fire_capture/ASTER_UAL_V6_8_DIRECTION_SOCKET_BIRTH_CONTACT.png
artifacts/aster_ual_v6_moving_fire_capture/ASTER_UAL_V6_OFF_AXIS_BOUNDARY_PAIRED_CONTACT.png
artifacts/aster_ual_v6_moving_fire_capture/ASTER_UAL_V6_MOVING_FIRE_EVIDENCE.json
```

The historical behavior result is PASS; all centered and off-axis cases advanced the lower body, matched the visible shot socket, preserved continuous aim, and retained the immutable shot snapshot. Evidence JSON SHA-256: `306d1ece418baeaf65e0e2224605793f33f3009b0d69be5b8632e8d9a230c49e`. Those captures predate the project-wide native-1920×1080 floor and are therefore historical only; they cannot promote current visual quality until regenerated.

## Interactive HTML integration

```text
art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html
```

HTML SHA-256:

```text
a42e6d97928251890447f046dfaaa1891ba594653356a29aab55528167ec22f7
```

The page loads Move V6 and Composite Fire V6 directly from the runtime asset root, loads the shared V7 muzzle JSON, and exposes click/touch aim and fire. It displays 24 discrete locomotion frames at 24 fps without adjacent-frame alpha crossfade. A moving shot keeps the lower cursor advancing while the Fire upper sequence and independent muzzle/projectile burst play from the snapshotted V7 socket.

## Unproven movement-relative scope

The current lower atlas is chosen from the character aim/facing sector. It does not select a distinct lower-body gait from the velocity sector. Therefore, for example, moving east while aiming north still uses the north-facing forward gait; it proves articulated legs during moving fire, not a physically authored north-facing east strafe.

No 64-way aim x move family and no bounded four-relative-family strafe/backpedal set has been authored or validated. Cross-direction upper/lower raster splicing remains prohibited because it produces waist holes, costume discontinuity, and mismatched anatomy.

Final bounded verdict:

```text
V5_VISUAL_LEG_GATE: FAIL
V6_VISIBLE_LEG_METRIC_GATE: PASS
V6_COSTUME_CONTINUITY_GATE: PASS
V7_MUZZLE_RUNTIME_GATE: PASS
GLOBAL_1080P_DYNAMIC_CAPTURE_GATE: HOLD_RECAPTURE_REQUIRED
TRUE_AIM_RELATIVE_STRAFE_BACKPEDAL: HOLD_NOT_PROVEN
HUMAN_VISUAL_REVIEW: REQUIRED
ASTER_PILOT: HOLD
PRODUCTION_EXPANSION: HOLD
```
