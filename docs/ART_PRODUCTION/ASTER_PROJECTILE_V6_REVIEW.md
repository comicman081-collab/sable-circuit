# ASTER Projectile V6 Review

## Scope and disposition

- Asset scope: ASTER airborne projectile VFX only.
- V5 disposition: visual FAIL; retained as the one immediate previous comparison.
- V6 asset disposition: retained as the current projectile candidate; direct user visual approval is not yet recorded.
- Evidence disposition after the 2026-08-30 project-wide 1080p contract: the old 1280×420 contact and 1280×720 runtime captures are historical FAIL/HOLD evidence. Native 1920×1080 recapture is required before promotion can be claimed again.
- Production expansion: HOLD. This review does not approve other operators, enemies, or full VFX production.
- Character frames remain clean: no muzzle flash, projectile, or impact is baked into ASTER source art.

## Generation authority

- V6 was authored with Codex built-in image generation, explicitly requested by the user, as a controlled edit of V5.
- Krea/Krea2 used: NO.
- Local model used for this projectile asset: NO.
- V5 prompt and V6 edit prompt are preserved beside their source images as `IMAGEGEN_PROMPT.txt` and `IMAGEGEN_EDIT_PROMPT.txt`.
- Green is used only for separable source/contact review. Runtime export is lossless RGBA WebP.

## Current and previous files

Current V6:

- Source: `art_src/pilot_v2/aster_v2/vfx/coil_projectile_v6_imagegen/source/ASTER_COIL_PROJECTILE_V6_IMAGEGEN_GREEN.png`
- Source SHA-256: `1cee454f40c65a2e05308a49bd3c8432dd6e46a464e04b4e91472af2a11960f1`
- Runtime: `assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V6_RGBA.webp`
- Runtime SHA-256: `de1c55f99f65b5a06e19b3261fec2a4e44bfaa2de0e697e38ed8e1613f5498cb`
- Runtime resolution: 768 x 192, lossless WebP RGBA.
- Tip anchor: normalized `(0.862, 0.5)`, measured from the visible alpha right edge at alpha greater than 6.
- The anchor was corrected from the pre-review nominal value `0.947`; all eight native directions were recaptured after correction.
- Recommended Godot world scale: `0.102`.
- Visible green-dominant pixels after strict despill: `0`.

Immediate previous V5:

- Runtime: `assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V5_RGBA.webp`
- Runtime SHA-256: `30e1815be79d90307ee4b41c529973146ad9a56c5e3b18b082e29bfffa99e7ce`
- Disposition: visual FAIL because the spear/missile silhouette, rings, and scale were too dominant.

## Runtime integration

- `scripts/combat/prototype_projectile.gd` loads V6 only for ASTER projectile profiles.
- The authored sprite is aligned to the existing collision tip without changing speed, damage, lifetime, or collision authority.
- Two restrained opacity-stepped trailing duplicates and a local cyan/amber light are runtime layers.
- The former procedural ASTER body remains only as a load-failure fallback.
- `CombatFeedback.spawn_hit(...)` remains the contact authority.
- Projectile code never calls `spawn_hurt`; accepted-damage actor code owns hurt feedback.

## Evidence and tests

- Green separation contact: `art_src/pilot_v2/aster_v2/vfx/coil_projectile_v6_imagegen/ASTER_COIL_PROJECTILE_V6_GREEN_CONTACT.png`
- Native eight-direction contact: `artifacts/aster_projectile_v6_runtime_capture/ASTER_PROJECTILE_V6_8_DIRECTION_NATIVE_CONTACT.png`
- Native captures: E, SE, S, SW, W, NW, N, and NE under `artifacts/aster_projectile_v6_runtime_capture/`.
- Interactive click/touch preview: `art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html`. This is interaction proof, not pixel-identical native rendering.
- `tests/smoke/aster_projectile_v6_smoke.gd`: PASS.
- `tests/smoke/aster_v4_locomotion_preview_smoke.gd`: PASS.
- `tests/smoke/m7_authored_visual_smoke.gd`: PASS.

## Historical external review gate

ChatGPT web review: <https://chatgpt.com/c/6a939c99-57a8-83e9-8d1e-f4c35581ca1f>

- Source visual: PASS.
- Runtime scale/readability: PASS.
- Eight-direction rotation/anchor: PASS.
- Premium 2.5D++ quality: PASS.
- Blockers: none.
- Non-blocking polish: slightly more irregular front capsule, stronger diagonal cyan-coil contrast, and fewer finest tail filaments.
- Historical verdict before the 1080p evidence floor: PILOT PROMOTION PASS.
- Current promotion verdict: HOLD — regenerate the separation contact and all eight runtime captures at native 1920×1080, then repeat visual review.
- Production expansion: HOLD.
- Direct user visual approval: NOT RECORDED.

## Deferred hit/hurt integration contract

- Confirmed external VFX lineage commit: `9c6d311 feat: replace linear hit cues with volumetric combat VFX`.
- Do not cherry-pick it into this dirty branch as part of the projectile pilot.
- Integrate the complete hit/hurt lineage first. After that, extend only the projectile contact call with the optional fifth argument `direction.normalized()`.
- Do not add `spawn_hurt` to projectile code; that would duplicate actor-owned accepted-damage feedback.

## Gate

`ASTER_PROJECTILE_V6_PILOT_GATE: HOLD_1080P_RECAPTURE_REQUIRED`

`PRODUCTION_EXPANSION: HOLD`
