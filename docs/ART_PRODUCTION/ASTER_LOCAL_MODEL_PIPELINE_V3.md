# ASTER local-model pipeline v3

## Decision

`5dbae66` remains the failure baseline: its ASTER body construction is
**VISUAL FAIL**, while its technical pipeline QA is **PASS** and production
expansion is **HOLD**. The later Blender-only V1 also failed visual review and
its source, previews, report, and dedicated scripts have been removed from the
working tree. They remain recoverable only through Git history.

The historical replacement began from one user-approved visual basis. That
Qwen/ComfyUI authoring route is now retired and must not be relaunched. The
current Fire16 repair uses locked native source art, human-verified semantic
masks, and deterministic project-local assembly:

```text
locked 1254px native direction master + approved subject mask
  -> human-verified semantic part masks
  -> one rigid rifle/hands/forearms similarity cluster
  -> exact #00FF00 native source + deterministic RGBA derivative
  -> human midpoint review
```

Blender contributes only camera, depth, rifle axis, two-hand grip anchors, and
foot placement. No Blender proxy, UAL mesh, mannequin, or base character is a
candidate for final visual output.

## Local model eligibility

| Component | Local state | License status | Role | Decision |
| --- | --- | --- | --- | --- |
| Blender `5.2.1` | project-local portable install | software tool; no character assets | headless pose/camera guide | use |
| Qwen Image Edit 2511 | historical read-only installation; no active production invocation | historical Apache-2.0 evidence retained | provenance only | retired; do not launch |
| SDXL Base 1.0 | installed read-only at `C:\AI_MODELS\sdxl-base-1.0` | CreativeML Open RAIL++-M; output use permitted subject to restrictions | first depth-control authoring test | tested, visually failed; candidate and route-specific code removed |
| SDXL Depth ControlNet | installed read-only at `C:\AI_MODELS\controlnet-sdxl\controlnet-depth-sdxl-1.0` | OpenRAIL++; use subject to restrictions | first depth-control authoring test | tested, visually failed; candidate and route-specific code removed |
| CLIPSeg + SAM2 | installed read-only at `C:\AI_MODELS\auto-mask` | Apache-2.0 | historical automatic semantic-mask attempt | retired for Fire16 after visual FAIL; do not use for this repair |
| Krea2 | installed but prohibited for SABLE | user policy excludes it | none | never use |
| OpenPose ControlNet | installed | local card does not establish a usable commercial license | none | exclude |
| DreamShaper/other LoRA/inpaint/IP Adapter | installed | commercial provenance not yet established for this production route | none | exclude |

All model paths outside this repository are read-only dependencies. Every
generated file, temporary mask, log, and candidate is written under this
project only.

`C:\AI_MODELS` and `C:\AI_ENVS` are immutable local-model sources. This
pipeline may read their weights and executables but must never download into,
modify, move, rename, or delete anything below either path. In particular,
ComfyUI is launched with its input, output, temporary, user, and log paths
under `D:\AI 종합 폴더\Games\Sable-circuit`.

## Hard gates

1. The 1024px visual-basis candidate is an authoring reference only; it cannot reach gameplay or
   production runtime assets. A separately named mask-derived RGBA texture may
   appear only in the isolated `PRE_GATE / NONPROMOTED / STATIC_PREVIEW` QA
   scene to collect scale evidence; it never attaches to `OperatorActor`.
2. Background exterior must be exact RGB `#00FF00`, not transparent.
3. Any toy/block/mannequin result, generic identity, invalid grip, or weak
small-scale read is a visual failure. Delete the entire candidate directory.
4. No animation, runtime export, ROOK, MICA, or enemy work may start before a
human accepts one ASTER Static Master.

## Attempt record

- Qwen from the stick pose guide: **FAIL**. It produced a high-quality but
  front-facing generic riflewoman, not the locked combat camera or ASTER
  identity. Candidate, input, and workspace output were deleted.
- SDXL Base + Depth ControlNet from that stick guide: **FAIL**. It produced a
  metallic mannequin and failed the matte gate. Candidate and route script
  were deleted.
- Qwen from the Blender full-mass guide: **USER-APPROVED VISUAL BASIS /
  NONPROMOTED**. The user approved its visible ASTER direction—quarter camera,
  adult tactical read, two-hand rifle contact, silver ponytail,
  navy/white/cyan palette, right shoulder plate, and boots—as the basis for
  subsequent work. Its exact-green source and binary mask are retained as an
  identity/surface reference only. It is 1024px, not the final Static Master,
  not a runtime asset, has no animation, and does not authorize production
  expansion. The next artifact is a 2048px manual master with a separate user
  SHA-locked PASS.

## Historical authoring control — disabled

`tools/art_pipeline/Invoke-AsterStaticMasterPipeline.ps1` is retained only as
historical provenance for the accepted Static Master chain. Do not invoke its
`Author` command or use it to launch Blender, ComfyUI, or Qwen. A future need to
re-author the Static Master requires a new versioned pipeline and an explicit
current authorization; the historical launcher is not an active production
entry point.

The old runbook remains evidence of how the accepted source was produced, not
permission to rerun it. Current Fire16 work must follow the active repair
contract and project-local retention policy.
