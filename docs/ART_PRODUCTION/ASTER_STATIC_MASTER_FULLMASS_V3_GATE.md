# ASTER Static Master full-mass V3 gate

## Scope

This document records one user-approved visual basis only. It is not a runtime
export, animation keyframe, combat-scene integration, or approval for
production expansion.

- Candidate: `art_src/pilot_v2/aster_v2/qwen_edits/qwen_static_master_fullmass_v3_seed251114/candidate/ASTER_STATIC_MASTER_QWEN_GREEN.png`
- Exact-green source QA: `candidate/ASTER_STATIC_MASTER_QWEN_GREEN_QA.json`
- Image A scale proof: `previews/ASTER_STATIC_MASTER_V3_IMAGE_A_SCALE_MOCKUP_NOT_RUNTIME.png`
- Blender guide: `art_src/pilot_v2/aster_v2/pose_guides/static_master_fullmass_v1/`
- Qwen runtime: read-only `C:\AI_ENVS\ComfyUI_windows_portable\SableQwen2511`

## Self QA

| Criterion | Result | Evidence |
| --- | --- | --- |
| No box torso / tube limbs / exposed joints | pass | Continuous torso, arms, legs, hands, and boots in the 1024 source. |
| Adult female operator read | visual basis approved | Mature face, full body, tactical stance, and non-chibi body mass are retained as the user-approved direction for the 2048 master. |
| ASTER property lock | visual basis approved | Silver ponytail, navy asymmetric jacket, right shoulder plate, white/cyan/gold accents, and precision-rifle role are locked for the next master. |
| Rifle and two-hand contact | pass | Trigger and forward support hands are both visibly attached to one rifle. |
| Material separation | pass | Hair, skin, navy fabric, armor, metal, gold hardware, and cyan emissive details are distinct. |
| Top-down combat read | provisional pass | The Image A scale mockup remains legible; it is only a static comparison, not runtime proof. |
| Exact green exterior source | pass | RGB `#00FF00` exterior ratio `1.0`; opaque-green foreground pixels `0`. |
| Image A quality gap | basis accepted, final gate pending | The user selected this candidate as the visual basis. The 2048 canonical master and controlled local-retouch gate remain required before a production visual PASS. |

## Gate result

```text
VISUAL BASIS: USER APPROVED / NONPROMOTED
2048 STATIC MASTER / RUNTIME / ANIMATION / PRODUCTION EXPANSION: HOLD
```

The current source is preserved as the user-approved visual basis. Do not use
it directly as an animation frame or runtime asset; the next artifact is the
locked 2048 canonical master plus controlled local retouches derived from this
basis. If the user later withdraws
the basis approval, delete its entire candidate directory (including green
source, mask, preview, and manifest) before another route begins.

The current review candidate is
`art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/torso_garment_v1_seed251142/candidate/ASTER_STATIC_MASTER_2048_TORSO_GARMENT_PATCH_GREEN.png`.
Its deterministic before/after review sheet and technical-chain QA are under
`art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/reviews/`.

## User Static Master decision — 2026-08-29

The user accepted the controlled static-chain candidate as sufficient. Its
exact source SHA-256 is locked in
`docs/ART_PRODUCTION/ASTER_STATIC_MASTER_USER_GATE.json`.

```text
ASTER STATIC MASTER: PASS (user visual decision + 2048px SHA lock)
NEXT SCOPE: ASTER-only 8-direction high-fidelity key-pose authoring
ROOK / MICA / ENEMY EXPANSION: HOLD
RUNTIME PROMOTION: HOLD until directional keyframe and motion gates pass
```

## Rejected authoring route — `static_authoring_v1`

- A headless Blender 5.2.1 trial built a SABLE-owned continuous-torso body,
  tapered limbs, garment shells, hair masses, and a custom rifle without any
  external character mesh, mannequin, or UAL visual mesh.
- Technical render/export: **PASS**. The source was 1024px with an exact
  opaque `#00FF00` exterior.
- Visual gate: **FAIL**. Inspection showed a toy/figure result: an oversized
  smooth head, exposed-looking round forms, simplified hands and rifle, and
  proportions materially below the locked ASTER basis and Image A target.
- Disposition: discard the exact generated `.blend`, PNG, manifest, and its
  procedural authoring script. It must not become a static master, rig source,
  animation frame, or runtime export. The replacement route must begin from
  the locked high-resolution ASTER visual basis rather than procedural
  primitive-body construction.

## Rejected authoring route — repository SVG body render

- The existing `assets/characters/playable/aster/aster_master.svg` was
  rendered headlessly in Blender as a controlled source-binding test. This
  used only repository-owned ASTER art and an exact green exterior.
- Visual gate: **FAIL**. The raster shows flat separated planes, oversized
  arm/hand treatment, paper-doll overlap, and no Image A-level integrated
  anatomy or material depth.
- Disposition: keep the original SVG only as identity/property reference
  (hair, palette, jacket asymmetry, rifle concept). Delete the test raster,
  `.blend`, manifest, and the SVG-render experiment code. Do not use the SVG
  body as a final combat source or a 360° body-construction shortcut.

## Superseded duplicate cleanup — `manual_2048`

- The former `static_master/manual_2048` underlay and its generator were an
  exact image-and-mask duplicate of the retained canonical 2048 working base.
- It had no consumers outside its own manifest, was explicitly non-final, and
  could not contribute to the new controlled local-retouch pipeline.
- Disposition: remove the duplicate three-file set and its generator to avoid
  retaining superseded SSD-consuming source. The retained canonical base is
  `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/`.
