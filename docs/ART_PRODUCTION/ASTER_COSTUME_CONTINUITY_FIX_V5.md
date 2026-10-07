# ASTER Composite Fire Costume Continuity Fix V5

Status: `COSTUME_CONTINUITY_PASS` (pixel/structure QA), visual promotion remains `USER_REVIEW_REQUIRED`.

## Reproduced defect

- Read-only recording: `C:\Users\AAA\Videos\화면 녹화\화면 녹화 중 2026-08-30 141411.mp4`
- Recording SHA-256: `c56a78ff015e6fde4ed8c866ab2197452d1e8795e0f972f1612fa4e4ef888b84`
- Sampled evidence: `artifacts/aster_costume_drift_141411/ASTER_COSTUME_DRIFT_VIDEO_F068_F081_CONTACT.png`
- Reproduction: W / about 189 degrees, `IDLE + FIRE`.  The anatomical-left white/cyan thigh panel disappears during affected Fire upper frames and returns when the full idle body resumes.

The defect was in derived split masks, not in ASTER's approved outfit.  `costumeId` remains `ASTER_COMBAT_SUIT_C01`; identity, garment layout, palette placement, rifle, and gameplay role did not change.

## Root cause

1. The old builder reused approximate runtime-local muzzle offsets as a raster-space weapon corridor.  Its W corridor ran from the pelvis through the thigh instead of following the visible barrel.
2. The old connected-silver-hair detector extended below the pelvis.  Antialiasing and morphological closing allowed the white thigh panel to join the ponytail component.
3. The lower mask then removed the panel while Fire upper frames supplied inconsistent trouser pixels.  The previous seam QA checked only alpha continuity and could not detect costume replacement or a missing panel region.

## Fixed ownership contract

- Pelvis, waist, thigh, legs, boots, white anatomical panels, and cyan lower-body piping are owned by the currently active idle/move lower frame.
- Fire upper owns torso, arms, hands, rifle, head, and hair/recoil above the waist.
- The only exception through the hard lower lock is the calibrated visible rifle corridor from `assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json` (`barrel_inner_xy -> muzzle_xy`).
- Head-connected hair preservation is bounded above the waist.  It cannot classify a pants/leg panel as hair.
- Muzzle VFX remains separate and is not baked into character frames.
- Runtime atlases remain lossless RGBA; green matte is source-generation provenance only.

Builder:

```text
tools/art_pipeline/build_aster_composite_fire_v5.py
SHA-256 3e0fd5a9b1ab9a073bbfdec2fcd23b692850dcd791f1d73bdd26aab77ad5b55f
```

The builder accepts `--generation v5|v6`.  V6 can be generated after the final `move_360_ual_v6` family is atomically promoted:

```powershell
C:\AI_ENVS\ComfyUI_windows_portable\python_embeded\python.exe tools\art_pipeline\build_aster_composite_fire_v5.py --generation v6
```

## V5 outputs and visual evidence

- Runtime family: `assets/units/operators/aster/composite_fire_v5/`
- Runtime manifest SHA-256: `632ac78bf77e07b28d8a59a1dfd7e27dd5e04375f876235e7bc2fac7ac9113f6`
- Main contact: `art_src/pilot_v2/aster_v2/animation_360/composite_fire_v5/ASTER_COMPOSITE_FIRE_V5_CONTACT.png`
- Main contact SHA-256: `e5163a58fc5f76c96682e827abbfbf7cf58a4b4f7fb8a112f88aba10086c71f9`
- Before / all six Fire frames / after regression contact: `art_src/pilot_v2/aster_v2/animation_360/composite_fire_v5/ASTER_COMPOSITE_FIRE_V5_COSTUME_REGRESSION_CONTACT.png`
- Regression contact SHA-256: `f84569854908089ab8d2de3f167c50adb2ced4198cda41c969558d9fa8b4bf56`
- Rejected-before / fixed-after W six-frame comparison: `artifacts/aster_costume_drift_141411/ASTER_W_FIRE_COSTUME_BEFORE_AFTER.png`
- W comparison SHA-256: `c7ac98b17ef09d03c207877c87e7d0874e28c401e42fc51609f2a688521fee60`

The regression contact contains 16 rows for each of the eight directions:

- MOVE before, MOVE + Fire F0-F5, MOVE after
- IDLE before, IDLE + Fire F0-F5, IDLE after

Direct visual inspection confirms that W's white/cyan anatomical-left thigh panel remains present in every Fire frame.  No waist gap, green fragment, duplicate lower body, or baked muzzle flash was observed in the full sheet.

## Automated QA

Validator:

```text
tools/art_pipeline/validate_aster_composite_costume_continuity.py
SHA-256 0c9abc5f3b68f4eb5e77f1a9b5ff565d58f59d917fb6ee9d43e1316d1143da45
```

Result file: `artifacts/aster_costume_drift_141411/ASTER_COSTUME_CONTINUITY_V5_QA.json`

- QA result: `PASS`
- Directions: 8/8
- MOVE pairs: 8 directions x 24 lower frames x 6 Fire upper frames = 1,152
- IDLE pairs: 8 directions x 4 lower frames x 6 Fire upper frames = 192
- Total frame pairs: 1,344/1,344
- Minimum hard lower-costume exact retention: 1.0
- Minimum white/cyan exact retention: 1.0
- Lower-costume mismatch pixels: 0
- Missing lower-costume hole pixels/components: 0
- Disconnected lower ownership pairs: 0

This QA compares each composite against the exact current lower source pixels inside the locked garment region.  It is not a color-area-only check; overwritten pixels and missing panel holes both fail the gate.

## V6 application

After `move_360_ual_v6` was atomically promoted, the same split/identity contract was applied without changing V5 or its rejected immediate previous candidate.

- Runtime family: `assets/units/operators/aster/composite_fire_v6/`
- Runtime/authoring manifest SHA-256: `874b7eae72be2dc39c01528290d753a89889b03c4d7592b6db5c2859a016d599`
- Main contact: `art_src/pilot_v2/aster_v2/animation_360/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_CONTACT.png`
- Main contact SHA-256: `deeb4c0dcb49fb22d412cf53c69c8b912b647a2d0be41c105ee6bdc9b71c396f`
- Full 8-direction regression contact: `art_src/pilot_v2/aster_v2/animation_360/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_COSTUME_REGRESSION_CONTACT.png`
- Regression contact SHA-256: `4b0289bbc7139cd32d5ba751ed2c66313f0ac3f90ee91fce98a934a7674a3208`
- W high-resolution before / Fire F0-F5 / after: `artifacts/aster_costume_drift_141411/ASTER_W_COSTUME_V6_BEFORE_FIRE_AFTER.png`
- W high-resolution contact SHA-256: `d287a2aa802430a8b8b0e60cad002060831cba30c338567d8b53db065ab3aa23`
- Independent QA: `artifacts/aster_costume_drift_141411/ASTER_COSTUME_CONTINUITY_V6_QA.json`
- Independent QA SHA-256: `6adfdf3edf997aa063b607bea2422cf81ad2e0aa7ef9bfa988eff9d1676bdfbc`

V6 QA result:

- 1,344/1,344 frame pairs scanned
- Minimum hard lower-costume exact retention: 1.0
- Minimum white/cyan exact retention: 1.0
- Mismatch pixels: 0
- Missing panel hole pixels/components: 0
- Disconnected lower ownership pairs: 0
- W MOVE and IDLE white/cyan retention: 1.0 across all six Fire upper frames
- Visual inspection: W thigh/boot panel remains stable before, throughout, and after Fire; no green fragment, duplicated pelvis, or waist hole observed

## Game SD costume identity lock — V6

This V6 change is a continuity correction for the same approved outfit, not a redesign.  No explicit costume ID existed in the repository before the composite-fire V5 correction; `ASTER_COMBAT_SUIT_C01` was introduced there only as a stable name for the already user-approved ASTER combat suit.  It does not authorize a new design, coverage change, identity change, mirrored asymmetry, or weapon replacement.

Canonical approval authority:

- User gate: `docs/ART_PRODUCTION/ASTER_STATIC_MASTER_USER_GATE.json`
  - SHA-256: `3a82211c1de7b3df956b19bc42b4f82979ebde1d6309da9a6a810b4cce1d585a`
  - Decision: `PASS`; approved by the user on 2026-08-29 for ASTER eight-direction high-fidelity key-pose authoring.
- Approved static master: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/torso_garment_v1_seed251142/candidate/ASTER_STATIC_MASTER_2048_TORSO_GARMENT_PATCH_GREEN.png`
  - SHA-256: `c68bb47e4354ca7ef564c3a730a8ef17a1f3180db3b494b233470114816fa2ea`
  - 2048 x 2048 source-authority image on `#00FF00`; it is not a runtime asset.
- Paired working mask: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/ASTER_STATIC_MASTER_2048_WORKING_MASK.png`
  - SHA-256: `91a2b6910734127e81cce84fb5db8614a5294c1d915f1489969219b80ad993a6`
- Visual-basis lock: `art_src/pilot_v2/aster_v2/visual_basis/ASTER_QWEN_V3_USER_VISUAL_BASIS_LOCK.json`
  - SHA-256: `75855bb3c6ad353d8b3f7ba4302e16a09f67610afb3fb7e3ba9d9216b916eff7`
  - Approved source SHA-256 recorded by that lock: `1e7a117a68e77bcac7cf7a3840cc425dc0976edde5b8ddfa4e0465325d104366`
- Identity-control sheet manifest/image SHA-256: `5766c4ec96cdb985723308a131189b04154db46fb2c63067e545e7538d9b0606` / `846089cb6802b03e2f1338349b2ab8e9fd3054d6a08f28d5564228934080e3dc`

V6 runtime source authority:

- Move lower manifest SHA-256: `c733a679808643e303c4f37212c79136aec3f34344bc2d270daa2ee818f1cc8c`
- Idle lower manifest SHA-256: `aae7db949870b6362127b2c7ce9bf3c6bab8ace84d483ad2fc8ee69c1930dda8`
- Fire upper manifest SHA-256: `4f117e4520527adb9de8bc831c432cdd32aa5ea6aa0a641a91a9b72c8926eadf`
- Per-direction source SHA-256 values are recorded under `directions_output.<direction>.layers.<layer>.source_sha256` in the V6 manifest.

Locked fingerprint:

- Identity/silhouette: adult stylized tactical woman; mature face and teal eyes; silver split-comet high ponytail; lean non-chibi form; one canonical-side shoulder plate; long narrow precision coil rifle with an open-frame muzzle cage; direction-specific asymmetry is never mirrored.
- Garment: navy high-collar asymmetric fitted jacket/body suit; continuous ribcage-waist-pelvis construction; canonical white right-shoulder plate with cyan bar and restrained gold hardware; anatomical-left white thigh-to-shin panel with cyan edge; opposite thigh straps and side pouch; integrated navy-white lace boots; full tactical coverage unchanged.
- Palette: silver hair `#B8C9D4`, navy cloth `#26324C`, white armor `#DDE4E8`, cyan `#43E6FF`, gold hardware `#CDA15B`, dark rifle `#28383D`, skin `#E7B3A6`.
- Accessories/grip: cyan piping, shoulder fasteners, thigh straps/pouch, gold-ringed optic and restrained rifle hardware; exactly one rifle, trigger hand on pistol grip, support hand under fore-end, credible two-hand contact and barrel axis retained.

Alpha and scale audit:

- 24 V6 runtime files decoded as lossless RGBA WebP; alpha extrema are `[0, 255]`, and fully transparent pixels with non-zero RGB are `0`.
- Cell size is 384 x 384.  Per-direction atlases are 384 x 9216 for 24 move frames, 384 x 1536 for four idle frames, and 384 x 2304 for six Fire frames across eight directions.
- Light/dark-background inspection confirms readable true-alpha cutouts, but also reveals visible green edge spill.  The heuristic counted 1,007,966 semi-transparent edge pixels and 119,933 green-dominant candidates.  Therefore alpha/chroma promotion is explicitly `ALPHA_EXTREMA_AND_TRANSPARENCY_PASS__CHROMA_EDGE_CLEANUP_HOLD`; this report does not mislabel the edge cleanup as complete.

Costume gate result: `COSTUME_CONTINUITY_PASS`.  The V6 validator scanned 1,344/1,344 composite pairs with minimum locked lower-garment retention 1.0, minimum white/cyan panel retention 1.0, and zero mismatches, missing-panel holes, or disconnected lower-ownership pairs.  This PASS is limited to outfit/identity continuity; it is not an overall visual-promotion or alpha-edge PASS.  The complete rejected immediate-previous V5 drift candidate remains preserved below for comparison and rollback.

## Immediate previous candidate retention

The rejected pre-fix V5 remains available for visual comparison and exact rollback:

- Runtime atlases: `assets/units/operators/aster/composite_fire_v5_costume_drift_prev/`
- Review/manifest: `art_src/pilot_v2/aster_v2/animation_360/composite_fire_v5_costume_drift_prev/`
- Preservation manifest SHA-256: `a08b1bb154b57b60056f5e193d6ba130e22cc408da8e92017cdd651ce2ddc455`
- 24/24 reconstructed runtime atlases match the immediate previous manifest SHA-256 byte-for-byte.
- `runtime_eligible`: `false`

No older rejected composite family was promoted or retained by this fix.

## Integration boundary

This task did not modify the HTML preview or `scripts/animation/aster_v4_locomotion_preview.gd`.  Runtime/HTML switching to the fixed V5 or future V6 family is handled separately so muzzle/projectile alignment work is not overwritten.
