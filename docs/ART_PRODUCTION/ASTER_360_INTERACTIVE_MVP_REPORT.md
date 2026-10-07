# ASTER 360 Interactive MVP Report

## Scope completed in this pass

- Blender 5.2.1 was used **headlessly** to create source-art animation files; no Blender UI or UAL render mesh was used.
- UAL1 FREE Standard provides only timing evidence:
  - `Idle_Loop` for Idle cadence.
  - `Jog_Fwd_Loop` for locomotion cadence/contact timing.
  - `Pistol_Shoot` is retained by the existing Fire-360 MVP.
- Every UAL mesh is removed before any ASTER render. The visible character is ASTER-specific ImageGen-authored art plus paired masks.
- `#00FF00` remains the source-art backdrop. Browser and runtime-review atlases are derived RGBA assets.

## Generated animation evidence

| State | Direction coverage | Frames | Source status |
| --- | --- | ---: | --- |
| Idle | E, SE, S, SW, W, NW, N, NE | 4 each | clean, no-VFX direction masters mapped through Blender Idle timing |
| Move | E, SE, S, SW, W, NW, N, NE | E: 12; others: 8 each | **E V3** uses twelve distinct contact/down/push/passing/high/reach body keys at 12 FPS; other directions are clean-master Blender transform mappings pending their authored lower-body keys |
| Fire | E, SE, S, SW, W, NW, N, NE | 6 each | existing Fire-360 atlas; separate muzzle VFX only at `muzzle_contact` and `recoil_peak` |

Relevant source artifacts:

- `art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/ASTER_IMAGEGEN_IDLE_MOVE_360_MVP__NONFINAL.blend`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/ASTER_IMAGEGEN_IDLE_MOVE_360_MVP_GREEN_MASK_MANIFEST.json`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v1/ASTER_IMAGEGEN_MOVE_E_MVP__NONFINAL.blend`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v2/ASTER_IMAGEGEN_MOVE_E_MVP__NONFINAL.blend`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v2/ASTER_IMAGEGEN_MOVE_E_MVP_GREEN_MASK_MANIFEST.json`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v2/previews/ASTER_MOVE_E_V3_ALPHA_COMPOSITE_QA.png`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v3/ASTER_IMAGEGEN_MOVE_E_MVP__NONFINAL.blend`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v3/ASTER_IMAGEGEN_MOVE_E_MVP_GREEN_MASK_MANIFEST.json`
- `art_src/pilot_v2/aster_v2/animation_360/imagegen_move_e_mvp_v3/previews/ASTER_MOVE_E_V4_ALPHA_COMPOSITE_QA.png`
- `assets/units/operators/aster/idle_move_360_mvp_v1/ASTER_IDLE_MOVE_360_MVP_ATLAS_MANIFEST.json`
- `assets/units/operators/aster/move_e_mvp_v3/ASTER_MOVE_E_360_MVP_ATLAS_MANIFEST.json`
- `assets/units/operators/aster/move_e_mvp_v4/ASTER_MOVE_E_360_MVP_ATLAS_MANIFEST.json`
- `assets/units/operators/aster/fire_360_mvp_v3/ASTER_FIRE_360_MVP_ATLAS_MANIFEST.json`

## Interactive review

Open [ASTER_360_INTERACTIVE_AIM_REVIEW.html](../../art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html) locally.

- Click/touch inside the combat panel to select one of the eight aim directions and fire it.
- Use **Move loop** or `Space` to inspect locomotion; select **Idle loop** to restore idle.
- The page is entirely project-local HTML/JS and project-relative RGBA WebP. It makes no cloud or Krea/Krea2 request.

## QA outcome

- Headless Blender render: PASS (96 Idle/Move direction-key source renders).
- Exact green/mask conversion: PASS (96/96 source-mask pairs, each recorded at `exact_green_outside_ratio: 1.0`).
- East V2 source-key QA: PASS (8/8 exact-green source-mask pairs; no duplicated source art in the loop).
- East V3 source-key QA: PASS (12/12 exact-green source-mask pairs; no duplicated source art in the loop).
- East V4 atlas export: PASS (lossless RGBA WebP, 384x4608, chroma-green fringe alpha count 0 after packaging).
- Atlas export: PASS (16 legacy Idle/Move RGBA lossless WebP atlases, East V3 and V4 retained replacement atlases, and 8 existing Fire RGBA WebP atlases present).
- HTML parse and asset-path dependency check: PASS.
- Move-loop blank-frame regression (2026-08-30): FIXED. The East V4 atlas has 12 rows, while the seven legacy direction atlases have 8. The preview now resolves keys per direction and clamps the active frame index before sampling, preventing rows 8-11 from being sampled from an 8-row atlas.
- Godot runtime integration: NOT YET CONNECTED.

## Quality gate

This is a usable interaction and technical-pipeline MVP, not a claim of final visual promotion. The seven non-East Move directions still require authored lower-body pose art before they can pass the full visual-motion gate. Production expansion remains **HOLD** pending user review and those direction-specific movement keys.
