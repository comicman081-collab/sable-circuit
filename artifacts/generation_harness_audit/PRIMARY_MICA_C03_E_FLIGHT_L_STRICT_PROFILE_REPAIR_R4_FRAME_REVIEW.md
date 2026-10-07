# Primary visual review — MICA C03 E/run/flight_l strict-profile repair R4

- Reviewer: Codex Astra primary visual review
- Review UTC: 2026-09-07T17:34:00Z
- Exact frame subject: `55cbf6239a0d1f9ded3fd842037df8d9f8cb9bbecafd3835162617c4382ecdc3`
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`
- Scope: one static ImageGen-authored visible frame only
- Overall verdict: `PASS_ONE_FRAME_VISUAL_REVIEW_ONLY`

## Evidence inspected

The actual 1254×1254 raw ImageGen result, exact-green master, subject mask, runtime RGBA, annotations, frame manifest, normalization/runtime QA, exact request/permit, native 1920×1310 green and dark review boards, approved neutral source, approved true-E profile source, F6 UAL/Blender pose-guide evidence, and the preceding R3 HOLD report were inspected. The 1080p validator passes both review boards for native container resolution and decoding only; it is not treated as a visual-quality verdict.

The approved true-E source itself exposes a narrow front garment placket because of coat construction. Therefore that feature alone is not treated as evidence of torso yaw. R4 was judged from the aligned head, shoulder line, ribcage silhouette, belt/pelvis plane, knees, boots, and weapon axis together.

## Seven required checks

| Check | Verdict | Direct observation |
| --- | --- | --- |
| `identity_and_costume` | PASS | MICA's face, brown braid, dark patterned long coat, pale trim, teal lining, thigh equipment, guards, boots, cyan devices and rifle remain coherent with the approved sources. No visible Blender/VRoid guide appearance replaced the ImageGen-authored art. |
| `anatomy_and_limb_count` | PASS | One head, two connected arms/hands, and two connected legs/boots are visible. No duplicate limb, fused knee, crossed shins, detached waist, balloon calf or gross proportion discontinuity is visible. |
| `whole_body_direction` | PASS | Head, shoulders, ribcage, pelvis, both leg chains, boots, rifle and visible barrel point screen-right as an E profile. The prior 90-degree waist twist is absent. The narrow coat placket is consistent with the approved true-E source and does not override the side silhouette. |
| `phase_and_stride` | PASS | The anatomical RIGHT leg, identified by the beige vertical thigh plate, leads screen-right; the plate-free LEFT leg trails. The legs are uncrossed and form a broad airborne run stride consistent with F6 `flight_l`. This is static phase validation, not cycle timing. |
| `feet_ankles_and_contact` | PASS | Both boots connect continuously through the shins; neither ankle turns sideways. The trailing boot is lifted and pitched naturally, while the leading boot follows its shin without the previously rejected 90-degree ankle rotation. No planted-foot or temporal-contact claim is made for this flight frame. |
| `weapon_hands_and_visible_muzzle` | PASS | The two-hand hold is coherent. The main horizontal barrel tip is visibly distinct from the lower auxiliary cylinder, and the annotated muzzle axis `(1092,385)` to `(1158,385)` lies on that main barrel and points screen-right. No firing/runtime claim is made. |
| `matte_edges_and_subject_preservation` | PASS | The ratio-aware connected-chroma derivative removes the background while retaining the cyan/teal costume and device edges that R3 ambiguously deleted. Visible RGB is byte-exact, the outer border is transparent, and the runtime QA records zero strong-green pixels on the alpha boundary. |

## Limit of this approval

This approval covers only the exact R4 static `E/run/flight_l` frame subject above. It does not approve temporal gait, actual contact, root translation, speed, firing alignment over time, the remaining 63 frames, the 8-direction sequence, runtime matrices, HTML parity, promotion, or Luna readiness. Those remain gated separately.

