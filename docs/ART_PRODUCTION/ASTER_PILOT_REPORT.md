# SABLE ASTER Art Pipeline V2 — Current Checkpoint

## Status

The project now has a reproducible source-side V2 *pre-authoring* pipeline:
Blender 5.2.1 Portable is locked and validated; UAL motion is inventoried;
and ASTER identity, Image A render language, and combat pose/depth are isolated
into a hash-locked authority package. It does **not** yet have an ASTER static
master or runtime replacement.

## Why the prior route was retired

The earlier final-body route constructed the visible combat body from boxes,
primitive limbs, exposed joint-like forms, and uniform glossy materials. It
reads as a block/action-figure rather than a connected adult tactical operator:
the torso-to-pelvis gesture, hands on rifle, garment layering, material
separation, and in-game finish all fail the Image A quality bar. That route is
retired and its artifacts have been purged under `ASSET_RETIREMENT_POLICY.md`.

## V2 assets prepared

- `art_src/pilot_v2/aster_v2/static_master/ASTER_STATIC_MASTER_AUTHORITY/`
  — three-input authority pack and `AUTHORITY_LOCK.json`.
- `art_src/pilot_v2/aster_v2/pose_guides/static_aim_v3_cleaned/`
  — Blender camera/depth guide with RGBA and required green source-cutout
  versions; not a final visual.
- `art_src/pilot_v2/blender/validate_blender_5_ual.py`
  — repeatable Blender/UAL validation.

## Local-Qwen authoring evidence

Qwen Image Edit 2511 is now installed as an isolated, official, Apache-2.0
local production tool. The approved INT8 diffusion, FP8 text encoder, and VAE
were integrity-checked, discovered by ComfyUI, and produced a genuine local
technical edit. No Krea model/path/API, cloud inference, base character pack,
paid model, BF16 diffusion, or Lightning LoRA was used.

The bounded ASTER static experiment failed its visual gate and the graph route
is closed rather than being falsely tuned into a PASS. Its failed outputs,
input copies, and route-specific scripts were deleted; none is a master asset
or runtime body.

## Required next checkpoint

Do not begin Idle, Move, Fire, UAL retarget, enemy work, or runtime integration
from this route. Select and prove a new visual-authoring route with one ASTER
static master before reopening the pilot.
