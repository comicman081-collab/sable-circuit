# Primary visual review — MICA C03 E/run/flight_r new-author R3

- Reviewer: Codex Astra primary visual review
- Review UTC: 2026-09-07T18:05:00Z
- Exact frame subject: `2e3e4f28276d97d7cee4916ced052bca17edca57cb52c26537f0ec56271781d0`
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`
- Scope: one static ImageGen-authored visible frame only
- Overall verdict: `PASS_ONE_FRAME_VISUAL_REVIEW_ONLY`

## Evidence inspected

The actual 1254×1254 raw ImageGen result, exact-green master, mask, runtime RGBA, annotations, manifest, request/permit, normalization/runtime QA, both native 1920×1310 review boards, approved neutral and true-E sources, approved F14 pose-guide review and the preceding R2 failure evidence were inspected. The 1080p validator PASS proves only native container resolution and decoding.

## Seven required checks

| Check | Verdict | Direct observation |
| --- | --- | --- |
| `identity_and_costume` | PASS | Face, brown braid, navy patterned long coat, pale trim, teal lining, asymmetric thigh equipment, guards, boots, cyan devices and rifle remain MICA. No generic F14 guide-model appearance is visible. |
| `anatomy_and_limb_count` | PASS | One head, two coherent arms/hands and two connected legs/boots. No extra limb, fused knee, crossed shin, detached waist/coat panel, inflated calf or gross proportion jump. |
| `whole_body_direction` | PASS | Head, shoulder/ribcage silhouette, pelvis, both leg chains, boots, rifle and barrel agree on strict screen-right E travel. No frontal pelvis or 90-degree waist kink is visible. |
| `phase_and_stride` | PASS | The plate-free anatomical LEFT leg leads screen-right; the beige-plate anatomical RIGHT leg trails screen-left. Both legs form a broad uncrossed airborne sprint split consistent with F14 `flight_r`, not a tiny step or high-knee march. This is static phase depiction only. |
| `feet_ankles_and_contact` | PASS | Both boots connect coherently to their shins and pitch in the running plane without sideways 90-degree ankle rotation. Neither foot is claimed planted. Temporal contact remains untested. |
| `weapon_hands_and_visible_muzzle` | PASS | Trigger and support hands form one coherent hold. The main barrel endpoint is visible and distinct from the lower auxiliary cylinder; annotated `(1080,376)`→`(1128,376)` points are opaque and follow the main barrel screen-right. |
| `matte_edges_and_subject_preservation` | PASS | Ratio-aware connected chroma removes the background and closed gaps while retaining hair, coat/boot silhouettes, cyan devices and teal lining. Visible RGB is byte-exact, outer border transparent, and strong-green alpha-boundary residual is zero. |

## Limit of approval

This approves only the exact static `E/run/flight_r` frame subject. It does not approve temporal gait/contact/root speed, firing/recoil/projectiles, the six remaining E phases, other directions, runtime matrices, HTML parity, promotion, or Luna readiness.

