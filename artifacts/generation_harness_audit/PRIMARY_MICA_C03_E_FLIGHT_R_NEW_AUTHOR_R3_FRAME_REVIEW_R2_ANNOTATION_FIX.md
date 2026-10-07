# Primary visual review — MICA C03 E/run/flight_r new-author R3 annotation fix R2

- Reviewer: Codex Astra primary visual review
- Review UTC: 2026-09-07T18:15:15Z
- Exact frame subject: `23e725b3da510e1711acbc5ee4669a8c0016e64cdb7525b913f63e1550a2ea31`
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`
- Scope: one static ImageGen-authored visible frame only
- Overall verdict: `PASS_ONE_FRAME_VISUAL_REVIEW_ONLY`

## Change from the held subject

The ImageGen-authored raw image, exact-green master, subject mask, and runtime RGBA are byte-identical to the previously reviewed subject. The only change is the main-rifle `muzzle_tip` annotation, corrected from the interior point `(1128,376)` to the independently observed last opaque outer-edge pixel `(1132,376)`. The manifest and exact-content subject were rehashed; the old subject and Ponytail HOLD report remain preserved.

## Seven required checks

| Check | Verdict | Direct observation |
| --- | --- | --- |
| `identity_and_costume` | PASS | Face, brown braid, navy patterned long coat, pale trim, teal lining, asymmetric thigh equipment, guards, boots, cyan devices and rifle remain MICA. No Blender/UAL guide-model appearance is visible. |
| `anatomy_and_limb_count` | PASS | One head, two coherent arms/hands and two connected legs/boots. No extra limb, fused knee, crossed shin, detached waist/coat panel, inflated calf or gross proportion jump. |
| `whole_body_direction` | PASS | Head, shoulder/ribcage silhouette, pelvis, both leg chains, boots, rifle and barrel agree on strict screen-right E travel. No frontal pelvis or 90-degree waist kink is visible. |
| `phase_and_stride` | PASS | The plate-free anatomical LEFT leg leads screen-right; the beige-plate anatomical RIGHT leg trails screen-left. Both legs form a broad uncrossed airborne sprint split consistent with F14 `flight_r`, not a tiny step or high-knee march. This is static phase depiction only. |
| `feet_ankles_and_contact` | PASS | Both boots connect coherently to their shins and pitch in the running plane without sideways 90-degree ankle rotation. Neither foot is claimed planted. Temporal contact remains untested. |
| `weapon_hands_and_visible_muzzle` | PASS | Trigger and support hands form one coherent hold. The main barrel endpoint is visible and distinct from the lower auxiliary cylinder; corrected `(1080,376)` to `(1132,376)` annotation follows the main barrel and terminates at its last opaque outer-edge pixel. |
| `matte_edges_and_subject_preservation` | PASS | Ratio-aware connected chroma removes the background and closed gaps while retaining hair, coat/boot silhouettes, cyan devices and teal lining. Visible RGB is byte-exact, outer border transparent, and strong-green alpha-boundary residual is zero. |

## Exact evidence

- Frame audit: `artifacts/generation_harness_audit/MICA_C03_E_FLIGHT_R_NEW_AUTHOR_R3_FRAME_AUDIT_R2_ANNOTATION_FIX.json`
- Frame-audit SHA-256: `904961a6c8ed29cbe56d4ffcb719e3d0a27c6e899c55127695de801c3a501795`
- Corrected annotations SHA-256: `d4cd5c566c7cfcc16fbdb72320d95c8775d2336e1eaeeaad0cce417f2f0db0b3`
- Corrected frame-manifest SHA-256: `911e01c0741e66e51535849da55423ee9ddec5b643b559f6222b07f009adc6d9`

## Limit of approval

This approves only the exact static `E/run/flight_r` frame subject. It does not approve temporal gait/contact/root speed, firing/recoil/projectiles, the six remaining E phases, other directions, runtime matrices, HTML parity, promotion, or Luna readiness.
