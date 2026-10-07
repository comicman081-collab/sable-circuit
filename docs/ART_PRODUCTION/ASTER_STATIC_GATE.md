# ASTER Static Master Gate — V2 Sprite Pipeline

## Fixed failure baseline

`5dbae66` is the unchangeable baseline:

- ASTER pilot visual result: **FAIL**
- pipeline technical QA: **PASS**
- production expansion: **HOLD**

The earlier direct-Blender low-poly/block body route is retired. Technical
build or matte checks do not make a valid combat body, and all rejected route
artifacts have been purged.

## New construction rule

The final in-game body is a SABLE-exclusive high-resolution 2.5D sprite. Its
authoring contract is:

`UAL motion source -> Blender pose/depth guide -> locked ASTER authority -> controlled Qwen Image Edit 2511 authoring -> RGBA runtime export`

Blender proxy geometry is a pose/camera/depth diagram only. It must never be
shown as a final character body. UAL meshes are never visual authority.

## Authority package prepared

`art_src/pilot_v2/aster_v2/static_master/ASTER_STATIC_MASTER_AUTHORITY/`
contains the three separately scoped, SHA-256-locked inputs:

| Input | Controls | Does not control |
| --- | --- | --- |
| `01_aster_identity_authority.svg` | ASTER face, adult identity, silver ponytail, navy asymmetric jacket, cyan/gold accents, narrow coil rifle | camera, pose, depth |
| `02_image_a_render_reference.png` | quarter-view 2.5D finish, material separation, cool environment / warm weapon lighting, combat readability | ASTER design or anatomy |
| `03_aster_pose_depth_authority_green.png` | fixed silhouette, rifle axis, two-hand grips, depth, feet | all surface design and low-poly geometry |

`AUTHORITY_LOCK.json` records file hashes, camera preset
`ASTER_StaticMaster_CombatCamera_v2_LOCKED`, a 4.8–5.2-head target, anchor
coordinates, and rejection invariants. The pose guide has a source-only exact
`#00FF00` matte; the final runtime asset will be RGBA.

## Approved local authoring runtime

The project-local installation target is `tools/qwen_image_edit_2511/runtime/`.
It may contain only the pinned Apache-2.0 Qwen Image Edit 2511 INT8 ConvRot
diffusion, Qwen 2.5 VL FP8 text encoder, and Qwen Image VAE. A separately
installed local runtime may also be read as a source through the explicit Qwen
runtime environment variables. In either case, it must have no
`extra_model_paths.yaml`, Krea model path, or cloud endpoint; generated input,
output, temp, and user files remain beneath the project. See
`tools/licenses/qwen_image_edit_2511/MODEL_INVENTORY.json` for immutable
source revisions and SHA-256 values.

## Current gate result

| Static master criterion | Current result |
| --- | --- |
| A high-quality actual ASTER body sprite exists | **NO** |
| Connected head/neck/ribcage/waist/pelvis | **NOT AUTHORED** |
| Real two-hand rifle grip | **NOT AUTHORED** |
| Hair/skin/fabric/armour/metal/emissive separation | **NOT AUTHORED** |
| Exact-green source-cutout requirement | required for source work; no candidate retained |
| Background-quality parity and combat readability | **NOT EVALUABLE** |

`ASTER STATIC VISUAL GATE: FAIL`

The bounded Qwen graph route did not produce an acceptable ASTER static
master. It is closed and its failed artifacts were deleted, so it cannot be
reopened by a seed, prompt, denoise, or slot-order sweep. Idle, move, fire
production and Godot promotion remain forbidden until a different approved
authoring route genuinely passes explicit static visual review.
