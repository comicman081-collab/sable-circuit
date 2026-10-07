# ASTER 360-degree combat-sprite pipeline

## Gate status

`5dbae66` remains **VISUAL FAIL / technical QA PASS / production HOLD**.
The user approved the existing Qwen-derived 1024px candidate as an ASTER
visual basis. It remains nonpromoted—not an accepted 2048px Static Master—so
it does not yet authorize animation work or combat deployment.

The isolated `PRE_GATE / NONPROMOTED / STATIC_PREVIEW` scene exists only to
compare scale and background integration. It is not an `OperatorActor`, has
no collision, input, targeting, combat, skeletal setup, or animation.

## Required production order

```text
locked ASTER_VISUAL_BASIS_V1 (style/identity only; never a fire-pose authority)
  -> Blender 5.2.1 headless 360 motion guide (idle/move/fire + ASTER rifle/grip reconstruction)
  -> one bounded local-Qwen SE fire-pose visual candidate (USER_REVIEW_REQUIRED only)
  -> 2048px manual ASTER Static Master, exact #00FF00 source + binary mask
  -> explicit user visual PASS
  -> eight-direction identity/body lock (E, SE, S, SW, W, NW, N, NE)
  -> manual SABLE 2D keyframe authoring for every direction
  -> green/mask QA, RGBA derivation, keyframe consistency QA
  -> atlas/state manifest
  -> isolated runtime proof, then production `OperatorActor` integration
```

No step may skip directly from a single static frame to combat deployment.

## Authorities and prohibitions

- Visual authority: ASTER identity lock, Image A 2.5D combat quality, and an
  approved 2048px manual SABLE body draw-over.
- The 1024px basis locks style and identity only. Its passive rifle pose is
  not a final fire stance; Blender reconstructs movement/fire timing and
  direction while the manual redraw supplies the visible body.
- Motion authority: only existing UAL1/UAL2 FREE Standard action timing and
  poses. Their meshes are transient Blender input only and never final art.
- Blender: `tools/blender/5.2.1/blender.exe --background` only. It produces
  pose/camera/timing guides; it is never the final character body renderer.
- Qwen Image Edit 2511: a bounded local visual-authoring assistant. It may
  create one pose-specific review candidate from the immutable style basis and
  its matching Blender guide; it cannot batch-generate frames, promote a final
  master, create a runtime export, or authorize animation expansion. The prior
  uncontrolled static-authoring graph is closed.
- For Qwen frames, the authoring backdrop is normalized using an
  edge-median green-chroma matte before exact `#00FF00` is written. SAM2
  semantic separation is not accepted as the default because it can amputate
  visually valid operator pixels; the matching binary mask must preserve the
  full raw body before a frame is eligible for review.
- Exact source background: every authoring frame is opaque RGB `#00FF00`.
  A runtime RGBA frame is mechanically derived from that frame's matching
  binary subject mask; transparent authoring source is forbidden.
- Krea/Krea2, cloud inference, Base Characters, mannequins, paid assets, and
  low-poly/block final bodies are prohibited.

## 360-degree contract

The runtime sector order remains the existing actor convention:

| Sector | Direction | Aim vector |
| ---: | --- | --- |
| 0 | E | `(1, 0)` |
| 1 | SE | `(.7071, .7071)` |
| 2 | S | `(0, 1)` |
| 3 | SW | `(-.7071, .7071)` |
| 4 | W | `(-1, 0)` |
| 5 | NW | `(-.7071, -.7071)` |
| 6 | N | `(0, -1)` |
| 7 | NE | `(.7071, -.7071)` |

All eight directions require independently authored body, rifle, ponytail,
jacket asymmetry, hand/grip, and feet. Mirroring cannot replace directions
where ASTER's identity-critical asymmetric gear, hair, and rifle side change.

| State | Keyframes per direction | Source timing | Total frames |
| --- | ---: | --- | ---: |
| Idle / aim-ready | 4 | UAL1 `Idle_Loop` timing | 32 |
| Locomotion | 8 | UAL1 `Jog_Fwd_Loop` timing | 64 |
| Fire | 6 | UAL1 `Pistol_Shoot` timing + ASTER two-hand rifle retarget | 48 |
| **Total** | **18** |  | **144** |

This is actual 360-degree combat coverage, not a static 8-cell atlas with a
procedural bob. Reload, hit, skill, and downed remain outside this first
production slice and are blocked until idle/move/fire pass their gates.

## Source and export paths

```text
art_src/pilot_v2/aster_v2/animation_360/
  source/{idle,move,fire}/ASTER_{state}_{direction}_{key}_GREEN.png
  masks/{idle,move,fire}/ASTER_{state}_{direction}_{key}_MASK.png
  guides/ASTER_360_UAL_ACTION_AUDIT.json
  guides/blender_360/ASTER_360_MOTION_GUIDE_MANIFEST.json
  guides/blender_360/ASTER_360_POSE_DRIVER__NONFINAL.blend
  guides/blender_360/ASTER_360_POSE_DRIVER_MANIFEST.json
  guides/blender_360/ASTER_360_POSE_DRIVER_QA.json
  guides/blender_360/poses/{idle,move,fire}/ASTER_GUIDE_{state}_{direction}_{key}_GREEN.png
  guides/blender_360/previews/ASTER_360_{STATE}_GUIDE_CONTACT_GREEN.png
  ASTER_360_PIPELINE_PRECHECK.json

assets/units/operators/aster/v2_360/
  {idle,move,fire}/ASTER_{state}_{direction}_{key}_RGBA.png
  ASTER_360_ATLAS_MANIFEST.json
```

Source and masks are not deleted until their corresponding runtime RGBA,
hashes, and human QA verdict have been recorded. Rejected candidates are
deleted as exact candidate sets under this project only; `C:\AI_MODELS` and
`C:\AI_ENVS` remain read-only.

## Reproducible checks

```powershell
# Always safe: this writes only the project-local preflight report.
& 'C:\AI_ENVS\ComfyUI_windows_portable\python_embeded\python.exe' -B `
  tools\art_pipeline\validate_aster_360_combat_pipeline.py

# Headless Blender audit only; no render, Blend save, or final character mesh.
& tools\blender\5.2.1\blender.exe --background --python `
  art_src\pilot_v2\blender\inspect_aster_ual_360_motion_sources.py -- `
  --output art_src\pilot_v2\aster_v2\animation_360\guides\ASTER_360_UAL_ACTION_AUDIT.json

# Actual motion-guide construction: 144 exact-green pose/depth/rifle guides
# plus a nonfinal, mesh-free Blender scene. This never exports final ASTER art.
& tools\blender\5.2.1\blender.exe --background --python `
  art_src\pilot_v2\blender\build_aster_360_motion_guides.py -- `
  --output art_src\pilot_v2\aster_v2\animation_360\guides\blender_360

# Deterministically repair Blender's near-green display rounding on the
# edge-connected exterior only, validate all 144 guides, and build contacts.
python tools\art_pipeline\normalize_aster_360_guide_green_matte.py
python tools\art_pipeline\validate_aster_360_motion_guides.py
python tools\art_pipeline\build_aster_360_motion_contact_sheets.py

# Mesh-free ASTER-specific Blender motion driver: 8 directions ×
# idle/move/fire, with two-hand rifle contacts and fire event markers.
# It is timing/pose evidence only; it contains no final body mesh or render.
& tools\blender\5.2.1\blender.exe --background --python `
  art_src\pilot_v2\blender\build_aster_360_pose_driver.py -- `
  --output art_src\pilot_v2\aster_v2\animation_360\guides\blender_360
& tools\blender\5.2.1\blender.exe --background `
  art_src\pilot_v2\aster_v2\animation_360\guides\blender_360\ASTER_360_POSE_DRIVER__NONFINAL.blend `
  --python tools\art_pipeline\validate_aster_360_pose_driver.py -- `
  --guide-root art_src\pilot_v2\aster_v2\animation_360\guides\blender_360

# One local Qwen fire-pose candidate only after a high-fidelity pose guide has
# passed its own review. C: runtime/models are read-only; all candidate files
# are project-local. It remains USER_REVIEW_REQUIRED.
& tools\art_pipeline\Invoke-AsterFirePoseCandidate.ps1 `
  -CandidateId qwen_fire_pose_se_muzzle_candidate_review `
  -Seed 251131 -Steps 32 `
  -PoseGuide art_src\pilot_v2\aster_v2\animation_360\guides\<approved_pose_guide>.png `
  -PoseAnchor
```

`--require-static-pass` is intentionally expected to fail today. It proves
that the 360-degree export/animation stage cannot begin without an executable
user gate at `docs/ART_PRODUCTION/ASTER_STATIC_MASTER_USER_GATE.json`.
That file must contain all of the following—not just a prose PASS:

```json
{
  "status": "PASS",
  "decision": "PASS",
  "approved_by": "user",
  "user_visual_approval": true,
  "approved_master_path": "art_src/.../ASTER_STATIC_MASTER_GREEN.png",
  "approved_master_sha256": "exact current SHA-256"
}
```

The pipeline refuses authoring/export when any flag is false, the source is
missing, its SHA differs from the approved SHA, or it is not 2048×2048. The
user-approved Qwen 1024 source is permitted only as the visual-basis reference;
it is explicitly nonpromotable as the static master. The agent must only create
the user gate after an explicit user visual decision; it must never synthesize
one.

After that decision and only after all 144 manual source/mask pairs exist,
the deterministic exporter is:

```powershell
& 'C:\AI_ENVS\ComfyUI_windows_portable\python_embeded\python.exe' -B `
  tools\art_pipeline\build_aster_360_sprite_atlases.py --dry-run
```

The build generates per-state/per-direction lossless WebP atlases at 384px
cells from 2048px source frames with premultiplied-alpha downsampling. This
prevents `#00FF00` fringe while avoiding a giant raw 144-frame export. It
refuses to overwrite an existing export and is not connected to the existing
static atlas presentation until motion QA passes.

The current 16-direction upper-body repair is additionally governed by
`docs/ART_PRODUCTION/ASTER_FIRE_UPPER_16_REPAIR_CONTRACT.md`.  All new visual
evidence follows `docs/ART_PRODUCTION/GLOBAL_1080P_VISUAL_EVIDENCE_CONTRACT.md`;
historical sub-1080 captures cannot support the current promotion decision.
