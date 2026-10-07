# SMOKE FAST — built-in ImageGen source-art handoff

This request is for Codex built-in ImageGen. Do not use ComfyUI, a local
diffusion model, local inpainting, ControlNet, LoRA, or another generator.

## Immutable identity and costume lock

- actorId: `CHR_SMOKE_FAST`
- adult: `true`
- role: `QA`
- faction: `QA`
- body type: `athletic adult`
- mature face read: `mature adult`
- weapon class: `rifle`
- combat role: `pipeline test`
- costumeId: `SMOKE_FAST_C01`
- palette placement: `#1E3752, #EBBE5A, #E8F2F6`
- silhouette modules: `QA body, QA rifle`
- exposure coverage: `full QA coverage`
- accessories: `none`
- readable weapon/grip zones: `trigger, support`
- prohibited features: `none beyond the global project rules`

## Generation contract

Create one native 1024px-or-larger full-body combat authority master first, followed
by eight independently authored direction masters in this exact order:
`E, SE, S, SW, W, NW, N, NE`. Preserve identity, costume modules, handedness,
weapon length, grip, and palette placement in every direction. Do not mirror an
asymmetric costume or weapon.

Every source uses one perfectly flat `#00FF00` background with no gradient,
floor, cast shadow, scenery, text, glow, reflected spill, or transparency.
Keep the subject completely inside frame, including hair and weapon.

Save selected current sources below:
`artifacts/character_pipeline_smoke/run_560d10028dea44b78cc5752eace67ede/work/imagegen/current`

Keep exactly one prior accepted candidate in `imagegen/previous`; remove older
rejected candidates only after the replacement is copied and hash-verified.

## Required review gate

Before motion work, create a labeled 1920×1080 contact sheet and record
`COSTUME_CONTINUITY_PASS` or `COSTUME_DRIFT_FAIL`, alpha-readiness, scale, and
weapon-grip readability. Only a PASS may enter Blender+UAL.
