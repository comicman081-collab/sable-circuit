# Ponytail FULL — actual MICA E/run/flight_l profile repair R3

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review UTC: **2026-09-07T16:59:29Z** (2026-09-08 01:59:29 KST).
- Exact frame subject: **`d2c7a34c8f6e72168ee988647200bb75ef17457d1f8d92d8ad6d73d26dc07e20`**.
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`.
- Overall verdict: **HOLD_NOT_PROMOTABLE. Do not seal a PASS frame receipt.**
- Applied: Ponytail FULL and `sable-motion-production`. This report is the only written artifact; no production code/assets, generation, rendering, runtime, promotion or Luna work was performed.

## Evidence actually inspected

I directly opened the actual 1254×1254 raw, normalized green master, runtime RGBA and edge mask, both native 1920×1310 green/dark review boards, and the approved S neutral source. I read the actual frame manifest, annotations, normalization/runtime QA, final request, permit and exact frame audit. The unchanged prompt and exact scope references had also been read in the immediately preceding R3 target-scope review.

I independently hashed all **27** audit bindings: **0 mismatches**. Recalculating the canonical binding digest returned the exact subject above. I independently decoded and compared the raw/master/runtime/review-board pixels. The 1080p validator was run read-only on both boards at 2026-09-07T16:55:38Z: container/decode PASS with `quality_claim=false`. This is not a visual or motion PASS.

The boards show the complete original 1254×1254 source at 1:1 with offset `(333,28)`. Their embedded green image matches the normalized master exactly, and visible dark-board pixels match the actual RGBA exactly. This is not an enlarged thumbnail presented as native character detail.

## Seven exact frame checks

| Check | Verdict | Observed evidence and limitation |
| --- | --- | --- |
| `identity_and_costume` | PASS, static appearance only | The face, brown right-side braid, navy patterned long coat, beige edging, teal lining, thigh equipment, guards, boots, cyan hardware and rifle remain recognizably MICA. No generic guide-model appearance or extra costume replacement is evident. Runtime edge uncertainty is separately held below. |
| `anatomy_and_limb_count` | PASS, this frame only | Two coherent arms and legs, two boots, one head. No obvious extra hand, crossed/merged legs, detached waist, balloon calf or disconnected knee is visible. This does not prove temporal deformation quality. |
| `whole_body_direction` | **HOLD** | Head, rifle and leg travel read screen-right, and the old gross 90-degree waist snap is absent. However the chest front/placket/zipper and pelvis still read as a three-quarter presentation rather than unambiguous strict E profile. The torso-front strip between collar, weapon and belt remains visible toward the viewer; the facing of the gun alone cannot establish ribcage/pelvis orientation. The annotation claiming complete E alignment is not independent proof. No numeric yaw angle is invented from this raster. |
| `phase_and_stride` | PASS, static phase depiction only | The beige vertical-plate anatomical RIGHT thigh is now on the forward leg, connected through the screen-right knee to the leading boot. The plate-free LEFT leg trails. The broad, uncrossed, airborne-looking stride is consistent with the requested F6/flight_l depiction and no longer has the previous reversed lead relation. Prior toe-off and a full support cycle remain outside this one-frame evidence. |
| `feet_ankles_and_contact` | PASS, isolated airborne silhouette only | The leading boot follows the leading shin; the trailing boot pitches downward in the running plane. No obvious 90-degree sideways ankle yaw, barrel calf or foot merge is visible. Neither boot is claimed planted. No actual ground, contact drift, foot height over time or root speed is validated. |
| `weapon_hands_and_visible_muzzle` | PASS, static image/annotation only | Two-hand grip is coherent, with one visible main horizontal barrel tip distinct from the lower auxiliary cylinder. The annotated axis `(1092,385)`→`(1158,385)` lies on the actual main barrel; both points are opaque character pixels and the tip is visually consistent with the endpoint. No real projectile, recoil or moving-fire socket is tested. |
| `matte_edges_and_subject_preservation` | **HOLD** | Broad green background and closed trigger/weapon gaps are removed; main cyan/teal lights and coat lining remain visible and retained RGB is byte-exact. However the narrow exposed cyan strip on the right-hand back device loses eight cyan-family edge pixels identified below. They may include mixed-background antialiasing, so I do not assert definitive subject deletion; I also cannot certify that this light-edge removal is harmless from the current semantic evidence. A zero strong-green boundary count does not settle this ambiguity. |

Result: **five narrowly scoped static PASS checks and two HOLD checks**. The candidate does not receive full-frame approval.

## What improved, and what did not pass

The anatomical laterality repair is a real improvement. In this new raw the beige plate is around x668–711/y638–692 on the leading thigh, rather than on the rear thigh as in the failed flight_l attempts. The annotated leading boot `(944,1082)` and trailing boot `(227,960)` agree with the visible connected legs. The stride is visibly broad, not a small pixel shuffle. These findings are not inherited from the target-scope PASS.

The central requested profile edit remains unresolved. A coherent body with no gross waist kink is not automatically strict side profile. The remaining three-quarter chest/pelvis reading must be resolved without swapping the now-correct marked leg or reauthoring the costume. Do not label the whole-body direction PASS solely because the head, toes and gun point right.

## Independent pixel checks and matte HOLD

- Runtime alpha: **1,273,299 pixels at 0**, **299,217 at 255**, no intermediate alpha values.
- Visible runtime RGB differences from raw: **0**.
- Raw→normalized RGB changes inside the provided retained mask: **0**.
- Opaque pixels on the outside border: **0**.
- Current connected-chroma family matches: **90 interior pixels**, **0 on the four-neighbour alpha boundary**, independently matching the QA. Those interior colored pixels are not automatically background.
- Green-board embedded master pixel mismatches: **0**; dark-board visible RGBA pixel mismatches: **0**.

Examples actually preserved as opaque with exact raw RGB include forearm light `(630,423)=(246,251,253)`, coat light `(496,639)=(90,204,231)`, leading-shin light `(786,879)=(251,253,254)`, back light `(516,266)=(190,245,247)` and teal lining `(435,718)=(9,44,43)`.

The following selected pixels lie along the thin cyan/white illuminated edge of the right-hand back device. They remain RGB-identical in the normalized master and have source mask 255, but become `(0,0,0,0)` in runtime:

| Pixel `(x,y)` | Raw/master RGB |
| --- | --- |
| `(564,185)` | `(129,239,210)` |
| `(563,192)` | `(133,230,211)` |
| `(562,199)` | `(106,225,204)` |
| `(561,205)` | `(117,231,211)` |
| `(560,211)` | `(117,227,198)` |
| `(560,212)` | `(140,233,217)` |
| `(559,218)` | `(120,228,205)` |
| `(558,222)` | `(39,175,154)` |

For context, at y212 the neighbouring strip core `(561,212)=(255,255,255)` and `(562,212)=(230,250,251)` remain opaque. This is a narrow edge case, **not evidence that the entire device or light vanished**. The eight-count is a selected diagnostic predicate within that device region, not a certified total deleted-subject count. The mixed edge may contain green-screen contribution; distinguishing that from legitimate luminous coverage is the unresolved part. Do not blindly restore green contamination or erase all cyan-like boundaries to force a number to zero.

The earlier connected-matte mechanism review was explicitly limited to another raw and its observed regions. It cannot settle this new raw's device-edge ambiguity. Retained-RGB equality also says nothing about legitimate pixels assigned alpha 0.

## Exact hashes

Candidate directory: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r3_e_flight_l_profile_repair/`.

| Artifact | SHA-256 |
| --- | --- |
| Raw `MICA_C03_E_RUN_FLIGHT_L_PROFILE_REPAIR_R3_IMAGEGEN_RAW.png` | `274d14d3e1fc45718b099447d087404063cdbea09eb3d3f4b1fccdb5857ff82c` |
| Normalized `...EXACT_GREEN.png` | `0248c794186c4513b3907f3f41d2e8d14703c6a664e921be7dbe0a1deb65978d` |
| `...EDGE_MASK.png` | `48faa3257a56b3442662c066e2c5bb11fdc960cf8a5274cf2cfd5c2bc1f51184` |
| `...RUNTIME_RGBA.png` | `647fb840cb287a4705cd8f2c44563b6333cf8e813f0c91241923b7fa58a1516e` |
| `...NORMALIZATION_QA.json` | `89864ecd4554478890f113074283c51ccf9e17f342e939daf093405c9766703c` |
| `...RUNTIME_RGBA_QA.json` | `795d24a1b3a5738a3d7293bfab06b5770ad95a1fecf9e8041a887a416bf72676` |
| `ANNOTATIONS.json` | `0011164f97c17162ff47fcdf7f6237a2cf0e22289ef99178e90dd3ae92b448e6` |
| `FRAME_MANIFEST.json` | `ead25068c78893d3c155f9345615159b3dc7d2aacdb2523180ec423911054882` |
| Final `REQUEST.json` | `e7919ba077d9cf91f6c08ee6675fb0998821cf9b6ac2220223847fd4d068e28a` |
| Exact single-attempt permit | `c7ef736ebfb322b5fbeb78346dfdef3ceb52de53c290dcd40a45b999235b00f3` |
| `MICA_C03_E_FLIGHT_L_PROFILE_REPAIR_R3_FRAME_AUDIT.json` | `dad67abc13bc44a6ee2cac56b15234f8f0d5ab1bedc9298df621ca1f76fc750e` |
| Review directory `REVIEW_MANIFEST.json` | `577d5d8c653ac614f09c37eb6511de115505e1bee6f993963c3403e89db8613f` |
| `MICA_E_FLIGHT_L_R3_GREEN_REVIEW.png` | `b1a3555acd582db137f4356ec5c892d1b6b1fb164815fc1926ea2e9428b4f919` |
| `MICA_E_FLIGHT_L_R3_DARK_REVIEW.png` | `7d8ddf0d831b3c85cc45041fbc23a69d024f24e86735da2012774a4a5cfef229` |
| Approved S neutral source | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |

## Disposition

Keep the frame and all source/derived evidence out of promotion while either HOLD remains. Preserve it under the project's candidate/quarantine retention rules if another scoped repair supersedes it; do not delete it or rewrite this review into PASS. The correct right-leading relationship is a property worth preserving, not permission to ignore strict E or edge preservation.

No temporal walk/run, actual ground contact, root speed, 8×8 movement/aim firing, 30/60/120Hz runtime, interactive HTML or Luna readiness approval is given.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent actual-frame review.
