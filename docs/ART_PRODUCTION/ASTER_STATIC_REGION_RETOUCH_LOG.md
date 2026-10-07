# ASTER static-region retouch log

This log records controlled, local Qwen Image Edit 2511 refinements made against
the immutable 2048 working base.  It is not a Static Master approval record.
No patch may be merged into the canonical master or used by runtime until the
user reviews the candidate and the complete Static Visual Gate is passed.

## Candidate: boots v1 / seed 251140

- Status: `USER_REVIEW_REQUIRED`.
- Role: one local lower-leg / boot material-and-construction refinement; not a
  full-character regeneration and not a runtime asset.
- Canonical base: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/ASTER_STATIC_MASTER_2048_WORKING_GREEN.png`
- Candidate: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/boots_v1_seed251140/candidate/ASTER_STATIC_MASTER_2048_BOOTS_PATCH_GREEN.png`
- Raw local model patch: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/boots_v1_seed251140/candidate/ASTER_2048_BOOTS_QWEN_RAW.png`
- Seed / steps: `251140` / `32`.
- Execution: 289.367 seconds, batch 1, local loopback only.

### Hard technical checks

- Qwen 2511 INT8 diffusion, Qwen2.5-VL FP8 text encoder, and Qwen Image VAE
  were recognized by the isolated local ComfyUI runtime.
- `changed_pixels_within_region`: `71,600`.
- `changed_pixels_outside_region`: `0`.
- Source exterior remains exact `#00FF00`; the paired binary mask is retained.
- Cloud inference calls: `0`; Krea/Krea2 calls: `0`.
- No Base Characters, mannequin, UAL mesh, paid, or Photoshop source was used.

### Human visual assessment before user review

The patch replaces the smooth, generic boot blocks with more readable cuff,
lace, toe-box, sole, and navy/white/cyan/gold material separation while keeping
the original silhouette and all non-boot pixels locked.  It is a localized
improvement only; it does **not** establish the ASTER Static Master as a whole.
Global body quality and the final Static Visual Gate remain pending.

### Reproducibility

- Background launcher: `tools/qwen_image_edit_2511/start_aster_static_region_retouch.ps1`
- Locked local-region runner: `tools/qwen_image_edit_2511/run_aster_static_region_retouch.py`
- Candidate provenance and SHA-256 values:
  `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/boots_v1_seed251140/ASTER_STATIC_REGION_RETOUCH_PROVENANCE.json`

## Rejected candidate: hands/rifle v1 / seed 251143

- Technical execution: completed locally with the approved Qwen 2511 weights,
  no OOM, `changed_pixels_outside_region: 0`, cloud calls `0`, and Krea calls
  `0`.
- Visual gate: **FAIL**. Although one rifle and two hands remained visible, the
  rifle's upper assembly became materially wider and heavier, introducing an
  oversized top mass and changing the locked ASTER rifle family/silhouette.
  The result does not satisfy the exact weapon proportion and two-hand-contact
  contract.
- Disposition: delete the complete `hands_rifle_v1_seed251143` candidate
  (source crop, raw model image, flattened patch, mask, provenance) and its
  temporary ComfyUI workspace. The accepted chain tip reverts to the retained
  `torso_garment_v1_seed251142` candidate, whose original rifle and hands are
  still locked.

## Current static-chain review candidate

- Review image (left: locked canonical base; right: candidate):
  `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/reviews/ASTER_STATIC_MASTER_CHAIN_REVIEW_GREEN.png`
- Candidate tip: `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/retouch_candidates/torso_garment_v1_seed251142/candidate/ASTER_STATIC_MASTER_2048_TORSO_GARMENT_PATCH_GREEN.png`
- Preserved local edits, in order: boots (`251140`), face/hair (`251141`),
  torso/garment (`251142`). The rifle/hands remain the locked visual-basis
  construction because their attempted edit was rejected and deleted.
- Independent chain QA:
  `art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1/reviews/ASTER_STATIC_MASTER_CHAIN_QA.json`
  reports `TECHNICAL_PASS__USER_REVIEW_REQUIRED`, `region_overlap_pixels: 0`,
  `changed_pixels_outside_union: 0`, and exact green exterior preservation.
- This remains **non-final**. No Static Master user gate, runtime promotion,
  atlas generation, or Idle/Move/Fire image expansion has occurred.
