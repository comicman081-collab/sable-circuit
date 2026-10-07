# MICA S neutral source — Ponytail FULL review R7

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- UTC: **2026-09-07 14:43:23**.
- Verdict: **PASS_SOURCE_ONLY** for the seven checks below and this exact subject only.
- Subject SHA-256: `25abad5e19751b485935047a1036fea62ad887e9858dcf9590cffd66b8d5eff2`.
- Actor / costume / view: `CHR_PROTO_03` / `MICA_RECON_C03` / S neutral rig pose.
- Skill applied: `sable-motion-production`, with the ImageGen-art / Blender+UAL-motion authority boundary.

## Exact evidence and verification

The original source, the R3 native annotation/mask board and the request's identity/costume references were personally opened and visually compared during this review sequence. R7 does not introduce another image: the original artwork, masks, annotations, request and attempt permit are unchanged. After code freeze, I independently recalculated `audit_source(SOURCE_MANIFEST_R3.json)`. It exactly matched `MICA_SOURCE_R7_AUDIT.json`, with `errors=[]` and the subject above. Numerical validation supplements, rather than substitutes for, the visual judgments below.

| Evidence | SHA-256 |
| --- | --- |
| `SOURCE_MANIFEST_R3.json` | `9ca441c64f705a1f1ac4d621879ce4a1e8a87c132097af558bd179504e2fc1f2` |
| `MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png` | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| `SOURCE_REVIEW_R3_NATIVE_2304x1920.png` | `6c01683ef81ca66e8f819e9b991ab829fbf2623edcd435b4a4d2a42e1bf898f9` |
| `S_LANDMARKS_R3.json` | `0cede9deaf7ee1b926283578f3dcb309610bcb8857e524aeac4228e574716c5a` |
| `artifacts/generation_harness_audit/MICA_SOURCE_R7_AUDIT.json` | `34d2c63609c580ef7d61da084911b0d461ba71bbb2e73a5d65693421e53b96e8` |
| `tools/character_pipeline/generation_harness.py` | `0c5aaccff0d0805d447b8193dcae739818c61823eb9bf76d21ffc4788a10abb9` |

The audit also resolves and binds the actual four R3 masks, original prompt/request/permit, the two identity/costume references and the unchanged consuming collector. Older R5/R6 subjects are not silently edited or treated as this approval.

## Seven independent source checks

| Contract check | Verdict | Actual visual basis and scope |
| --- | --- | --- |
| `identity_and_costume` | PASS | Recognizable MICA face and brown side braid; dark navy tactical coat, beige binding, teal lining, twin rear cyan-lit equipment, pouches, knee protection and boot design are continuous with the supplied references. No duplicate face/eyes or foreign body parts are apparent in this source. |
| `true_body_facing` | PASS | Head, shoulders, torso, pelvis, knees and boot fronts coherently face the viewer in the requested S neutral A-pose. This is not merely a turned head or gun over a different-facing pelvis. It does not approve any E/W or diagonal view. |
| `shared_scale_and_ground` | PASS | The single source panel has consistent body proportions and a common visible bottom baseline; both boot fronts fit with margin, and the annotated head/ground points agree with the picture. The 1.72 m-derived scale is an authoring convention, not independently measured anatomical height. Heels are occluded by the opaque boots and their annotations remain approximate construction landmarks, never sole-contact evidence. |
| `unoccluded_texture_regions` | PASS | The selected central face, visible coat strips/chest region, short trouser patches above thigh equipment and boot fronts are visible in the original image. The short R3 trouser patches avoid the long strap-containing regions rejected earlier. These are conservative visible patches, not complete texture coverage. |
| `no_foreign_parts_in_uv_masks` | PASS | Comparing the actual R3 mask overlays to the original, the selected material patches do not include unrelated hands, hair, thigh straps or green background. The coat's own seam/zipper details remain coat content, not a promise of a uniform fabric swatch. Mask validity does not authorize tiling a small patch across a new garment or reconstructing a face. |
| `native_source_resolution` | PASS | The original is native 1024×1536, with approximately 1382 px between the annotated head top and baseline. The review board is native 2304×1920; the original image was also inspected directly. No enlarged thumbnail is used as native-detail proof. |
| `clean_subject_separation` | PASS | Within source scope, the green field is visually even, the subject silhouette is intact, and there is no obvious floor shadow, scene object or broad green contamination in the selected source regions. This approves the green master only. No actual keyed derivative, native-alpha result or final runtime alpha-edge quality is approved by this check. |

## Non-transferable limitations

- This is a **source-art approval only**, not build-plan, local appearance reconstruction, mesh, first-pose, animation, world-grounding, muzzle, runtime, HTML or final-character approval.
- The original green source stays immutable. Its region labels do not authorize Blender to invent or replace visible face, hair, costume, boots or weapon pixels. Missing visible content remains ImageGen work under the user's authority boundary.
- The E contact R4 derivative with 244 deleted forearm-light pixels remains **FAIL_NOT_PROMOTABLE**. It is a different image and does not inherit this source approval.
- Actual eight-direction walk/run, independent movement×aim firing, grounding, 30/60/120Hz runtime parity and independent final reviews remain outstanding. This report does not authorize Luna reproduction or production promotion.
- No generation, rendering, process launch, source edit, deletion or promotion was performed for this report. Only read-only audit/image verification and this new evidence document were produced.
