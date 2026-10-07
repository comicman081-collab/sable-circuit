# Ponytail FULL — MICA E/run/flight_r new-author R3

Reviewer: `/root/ponytail_motion_audit` (independent Ponytail FULL). Reviewed at **2026-09-07T18:10:43Z** using `sable-motion-production` and the current project instructions.

**Verdict: HOLD_SINGLE_STATIC_FRAME — 6 PASS, 1 HOLD.** This review is bound only to subject `2e3e4f28276d97d7cee4916ced052bca17edca57cb52c26537f0ec56271781d0`. Do not seal this subject as all-checks PASS. The remaining issue is the bound muzzle-tip annotation, not a request to regenerate the artwork.

## Direct evidence and identity

I inspected the native 1254×1254 ImageGen raw, exact-green/edge-mask/RGBA evidence, the native green and dark review boards, REQUEST/PROMPT/permit, FRAME_MANIFEST, ANNOTATIONS and both QA records. I compared the approved neutral and true-E source art, the reviewed F14 lower-body guide evidence and the previous R2 wrong-leading-leg rejection. This request is `author_new_frame`; its ordered ImageGen references are neutral identity, true-E source and F14 pose guide, not the rejected R2 raw.

All **25 audit bindings** were independently hashed with **0 mismatches**. Canonical binding digest reproduced the exact subject above. Audit file SHA-256: `85f4d62ad58acafe128ed39ab00c797517222c3bbe98a9780b4541bdd26f62a3`.

| Required check | Verdict | Direct finding |
| --- | --- | --- |
| `identity_and_costume` | PASS | Brown hair/right-side braid, face profile, dark patterned long coat, beige trim, teal lining, two back devices, thigh equipment, guards, boots and two-tone cyan-core rifle remain recognizable against the approved sources. The beige vertical thigh plate is on the trailing near/right thigh. The far/left outer-thigh equipment is partly occluded in this profile; it is not replaced with a second beige plate. No obvious local-art reconstruction seam is visible. |
| `anatomy_and_limb_count` | PASS | One head, two arms and hands, two continuous legs and two complete boots. Knees and calves follow their respective thighs; no crossed shins, barrel-shaped calf swelling or detached lower-body cutouts are visible at native scale. |
| `whole_body_direction` | PASS | Head, near shoulder, ribcage, pelvis, thighs, knees and boots coherently face screen-right/E. The approved true-E source itself shows a narrow garment placket; the candidate's narrow trim is not, by itself, evidence of torso yaw. No visible waist kink or front-facing pelvis combined with side-facing legs was found. This is a visual profile judgment, not a measured 3D yaw claim. |
| `phase_and_stride` | PASS | The plate-free anatomical **LEFT leg leads screen-right**; the anatomical **RIGHT leg with beige vertical plate trails screen-left**. This is the required `flight_r` relation and reverses the prior R2 error. The broad fore/aft split reads as a running flight pose, not narrow stepping or crossed-leg motion. |
| `feet_ankles_and_contact` | PASS | Both boots are fully visible and unplanted in this isolated flight drawing. Leading and trailing ankle articulation follows the leg's sagittal direction; the trailing plantar-flexion is not a 90-degree sideways ankle rotation. This approves only static airborne anatomy: the green background provides no independently measured ground plane, clearance, landing contact or temporal toe-off proof. |
| `weapon_hands_and_visible_muzzle` | **HOLD** | Two-hand grip and the main horizontal barrel are visually coherent; the lower cylindrical attachment is distinguishable from the main muzzle. However, ANNOTATIONS binds `muzzle_tip=[1128,376]`. On that same row, clear barrel pixels continue through x=1131 and the opaque outer-edge pixel is x=1132. The declared tip is 3–4 source pixels inside the visible end. An opaque point on the barrel is not sufficient evidence of the actual barrel tip. Correct the annotation and re-audit/review its new subject; artwork generation is unnecessary for this issue. |
| `matte_edges_and_subject_preservation` | PASS | Native raw/RGBA and the dark board show no obvious lost costume light, cyan/teal deletion, closed bright-green hole or strong-green silhouette halo. The cyan forearm/coat/shin lights and teal lining remain present. Independent pixel checks below support, but do not substitute for, that visual judgment. |

## Independent pixel and container checks

- Raw/master changes inside the provided subject mask: **0**. Surviving RGBA RGB changes against raw: **0**.
- Alpha is binary: **300,230 opaque**, **1,272,286 transparent** pixels. An independent synchronous four-neighbor reconstruction of the current ratio-aware chroma rule reached the same mask after five growth rounds: **0 differing pixels**.
- Strong-green family residual: **24 interior pixels**, **0 alpha-boundary pixels**. Thus this is not a claim that every green-like material pixel was erased. Zero boundary count alone would not prove semantic preservation.
- Preserved opaque, raw-RGB-exact samples include forearm `(681,433)=[244,248,249]`, coat light `(462,673)=[222,255,255]`, leading shin light `(846,778)=[119,207,207]`, lining `(559,847)=[14,70,57]` and both back-device light samples `(458,127)`, `(483,148)`.
- Muzzle samples: `(1128,376)=[57,47,53,255]`, `(1130,376)=[59,53,58,255]`, `(1131,376)=[40,19,44,255]`, `(1132,376)=[28,50,40,255]`. Rows 371–377 all retain x=1132 at the outer edge; the current annotation is not the last barrel-edge location.
- The visual-evidence validator independently decoded both boards as **1920×1310**, despite their `1920x1080` filenames. The 1254-pixel source is presented at scale 1.0. Container PASS is resolution/decoding only and is not animation or visual-quality approval.

## Exact artifact hashes

Candidate directory: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r3_e_flight_r_new_author/`.

| Artifact | SHA-256 |
| --- | --- |
| ImageGen raw | `5d1dc992e662e29b5354ecae3a7cac69b5ba24da2d498f4e165a7a0fa1b7a4a8` |
| Exact-green master | `d8d88c0906ac82145fa33499ff6ce013a70f9fa7d16c137e83b0116d5af43178` |
| Edge mask | `243aa2b1a6bfe67db9ff687b3ce22d93b4835f2cc72fff8d89a202aaf887a5fe` |
| Runtime RGBA | `18570cea5cc1b4584ae8d1befd4e13fd0ad675dfbd2da9d44ac7baf405cd6503` |
| ANNOTATIONS.json | `3cf3d98a2da6d32c720a320cb7e802f272b1e646cab92c5dee64a503d8d1d6e2` |
| FRAME_MANIFEST.json | `cf29b60a9c7e766354494f96852b7ff02801874b0e7f2ab39cf8384b456e9079` |
| Green board | `7b068d4de19ea871521bb4e517fec25fcc574470a674883f69770563a54b47ad` |
| Dark board | `53c2aa92adc0caa5eb68efd210a4421526e962bbcf45c2cdd7339b6d911b3257` |
| Approved neutral source | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| Approved true-E source | `7ece6e83561bf3c9ee720b4c5a1f75820f73ae4afce95b895fe9b38d3299f4a1` |
| SOURCE_RECEIPT_R7.json | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |

The static PASS items do not establish frame-to-frame continuity, gait speed, grounding, collision response, projectile birth, 8-direction movement/aim, playable HTML or Luna reproduction. No production code, artwork or receipt was modified by this reviewer.
