# ASTER Static Master reproducible pipeline

## Scope lock

This is an authoring and technical-validation pipeline for one ASTER Static
Master candidate. It does **not** authorize a sprite atlas, idle/move/fire
animation, Godot integration, ROOK, MICA, enemies, or production expansion.
Every successful author run ends at `USER_REVIEW_REQUIRED`.

`C:\AI_MODELS` and `C:\AI_ENVS` are immutable read-only dependencies. The
pipeline reads local Blender/Qwen/model files from those locations when
configured, but all generated images, masks, temporary Comfy folders,
previews, manifests, and logs are under this repository on D:.

## Commands

Validate the current source candidate without launching Blender or ComfyUI:

```powershell
pwsh -NoProfile -File tools/art_pipeline/Invoke-AsterStaticMasterPipeline.ps1 -Mode Validate
```

Author exactly one new pre-gate candidate only after the current candidate is
rejected and removed. The candidate ID is immutable: the command refuses to
overwrite it.

```powershell
pwsh -NoProfile -File tools/art_pipeline/Invoke-AsterStaticMasterPipeline.ps1 `
  -Mode Author -CandidateId qwen_static_master_fullmass_v4_seed251115 -Seed 251115 -Steps 32
```

The author sequence is fixed:

```text
Blender 5.2.1 --background spatial guide
  -> hidden local loopback ComfyUI/Qwen 2511 edit
  -> local SAM2/CLIPSeg exact #00FF00 matte
  -> Image A/gameplay-scale review previews
  -> manifest + technical validation
  -> USER_REVIEW_REQUIRED
```

No Krea model, registry, cloud API, network inference, Photoshop, or GUI
Blender session is part of that sequence. The only HTTP requests are to the
locally launched `127.0.0.1:8190` ComfyUI process.

## Failure and storage policy

The author command refuses to overwrite an existing candidate and, if any
stage fails, removes only the new candidate directory and its matching
temporary Blender-guide directory. It never removes C: model/environment
files. When a human rejects a candidate, remove it explicitly with the exact
candidate ID:

```powershell
pwsh -NoProfile -File tools/art_pipeline/Remove-AsterStaticMasterCandidate.ps1 `
  -CandidateId qwen_static_master_fullmass_v4_seed251115 -Confirm:$false
```

This deletes only:

- `art_src/pilot_v2/aster_v2/qwen_edits/<candidate-id>/`
- `art_src/pilot_v2/aster_v2/pose_guides/_aster_static_master_pipeline/<candidate-id>/`

The validated pre-gate candidate retains only its green source, binary mask,
matte QA, review previews, source manifest, and technical validation record.
Its raw Qwen image, copied input, Qwen provenance payload, and candidate-local
Comfy workspace are purged automatically after technical success.
