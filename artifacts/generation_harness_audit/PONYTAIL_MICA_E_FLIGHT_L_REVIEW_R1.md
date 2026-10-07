# Ponytail FULL — MICA E/run/flight_l independent frame review R1

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Reviewed UTC: 2026-09-07T16:09:19Z (2026-09-08 01:09:19 KST).
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`.
- Exact raw SHA-256: `548872ee7d748d738ca6deb0bebe0bb5f3b42e948d91c9bf78cb8535fed9d692`.
- Request subject, not a completed frame-audit subject: `351824a4e446bba31c0c5135dd6d0786ba4e18034a4429f6aaa4872ea31fea2f`.
- Overall verdict: **FAIL_NOT_PROMOTABLE. Do not seal a PASS frame receipt.**
- Applied: Ponytail FULL and `sable-motion-production`. Only this report was written; no source/code edits, ImageGen, rendering, promotion, runtime or Luna execution was performed.

## Evidence actually inspected

I directly opened the new 1254×1254 RGB ImageGen raw, the approved 1024×1536 S neutral MICA master, the supplied older E direction master, the exact F6/006.png Sprint_Loop guide, and the later-added 1254×1254 `RUNTIME_RGBA_THRESHOLD_R2.png`. I read the request, prompt, single-attempt permit, current phase/check contract, source receipt, F6 guide review bundle, previous R2 failure report/quarantine manifest, and both runtime derivation QA revisions. I independently decoded raw/master/mask/old-RGBA/new-RGBA pixels and verified the request's nine path/hash references; every referenced hash matched.

The complete 17-frame R2 guide cycle was previously directly inspected in my separately hashed `PONYTAIL_SPRINT_E_POSE_GUIDE_REVIEW_R2.md`. F6 is approved only as an E/right-leading lower-body flight guide. Its generic model is not authority for final MICA appearance, upper-body aiming, or real contact.

No native 1920×1080-or-larger review board for this new frame was present at review time. These original-scale inspections are sufficient to identify and reject the defects below, but are **not** a passed 1080p evidence-container gate. No final frame annotation/audit/receipt was supplied. No claim is made that the raw is transparent: it is RGB, and conversion to RGBA gives alpha 255 for all 1,572,516 pixels.

## Seven required verdicts

| Contract check | Verdict | Actual observation and limit |
| --- | --- | --- |
| `identity_and_costume` | PASS, static appearance only | Face, brown right-side braid, navy patterned coat, beige edging, teal lining, cyan equipment, pouches, knee/shin guards, boots and weapon remain recognizably MICA. The distinctive beige-plate right-thigh pouch is present. Its side identity exposes the phase error rather than validating the requested lead leg. No generic guide-model robot limbs or costume were copied. |
| `anatomy_and_limb_count` | PASS, one frame only | Two coherent human legs, two arms, two boots and one head. No extra knee/hand, detached waist, calf ballooning or clearly crossed legs is visible. This does not establish deformation over time. |
| `whole_body_direction` | HOLD | Head, rifle, knees and boot travel read screen-right, without the old gross 90-degree waist kink. The chest/lapels/zipper and pelvis nevertheless remain a three-quarter presentation, not an unambiguous strict E profile of the whole body. The older E reference already has this limitation and cannot supply the missing proof. No numeric body yaw is inferred from one raster. |
| `phase_and_stride` | **FAIL** | The stride is broad and visibly running-like rather than a tiny shuffle. However the beige-plate **anatomical RIGHT** thigh is on the **trailing** leg. The plate-free left leg leads. This directly contradicts `flight_l` = flight after left toe-off, **right leg leading**, neither foot supporting. |
| `feet_ankles_and_contact` | PASS, isolated airborne silhouette only | The front boot follows its shin; the rear boot pitches down along the running plane. No obvious 90-degree sideways ankle yaw, barrel calf, inward crossed boots or foot merge is visible. Neither foot is depicted as planted. Prior support, actual ground clearance and contact continuity remain unverified and are not approved by this static PASS. |
| `weapon_hands_and_visible_muzzle` | PASS, static appearance only | The rear hand grips the trigger area and the front hand supports the fore-end. The main right-facing barrel has a visible tip, distinct from the lower auxiliary cylinder. No obvious ghost hand or broken barrel is present. No projectile, per-frame socket, recoil or moving-fire alignment was tested. |
| `matte_edges_and_subject_preservation` | **FAIL**, current THRESHOLD_R2 derivative | The revised derivative restores real teal/cyan pixels erased by the first threshold result and keeps retained RGB byte-exact, but still leaves fully opaque, nearly pure dark-green boundary pixels around the weapon and coat. A zero count under the same removal predicate is not independent proof of clean edges. Exact samples are recorded below. |

Four narrowly scoped static PASS checks, one HOLD and two FAIL checks do not constitute frame approval.

## Anatomical-side contradiction

The approved frontal S source places the beige vertical-plate pouch on screen-left, the character's anatomical right thigh. The other thigh has dark equipment without that beige front plate. The request and prompt explicitly preserve this distinction.

In the new raw, the beige front plate is visible at approximately **x530–552, y699–762**. That thigh continues to the bent rear knee/shin and the boot at screen-left, approximately x150–320, y940–1140. The leading leg instead extends to the screen-right knee and boot, with the front boot approximately x910–1105, y1040–1152. It is the plate-free side. The requested anatomical right leg has therefore not moved into the leading role.

This is not repaired by naming the leading foot `right` in an annotation. If the forward leg were insisted to be anatomical right, then the immutable right-thigh plate has migrated to the other leg and costume continuity fails instead. Neither interpretation permits all seven gates to pass.

The previous `flight_r` R2 failed because its right leg led when the left was required. This new `flight_l` fails because its left leg leads when the right is required. They are different images with opposite actual lead legs, but the same failure category: **the requested phase's anatomical laterality was not preserved**. The F6 pose-guide contract is correct. The failure is in the output, not permission to redefine the shared phase convention. Reference competition may be a contributing mechanism; a particular internal ImageGen cause has not been proven.

## Matte R2: improvement is not completion

I independently measured the actual new RGBA rather than accepting the QA labels:

- Alpha 0: **1,203,623** pixels; alpha 255: **368,893**; no intermediate alpha values.
- New visible RGB differences from the raw: **0**.
- Raw-to-master differences inside the supplied retained mask: **0**.
- Compared with the first, failed `RUNTIME_RGBA.png`: **2,930 pixels restored**, **1 additional pixel removed**, net visible gain 2,929.
- Example real light restored: `(577,423)`, raw RGB `(46,198,189)`; `(576,424)`, raw RGB `(79,222,209)`. Both were transparent in the first derivative and visible in THRESHOLD_R2. This confirms that broad low channel-separation thresholding had erased cyan/teal content.

Current THRESHOLD_R2 still retains these original-scale pixels at an actual alpha boundary:

| Pixel `(x,y)` | Actual RGBA | Region |
| --- | --- | --- |
| `(831,317)` | `(7,28,7,255)` | Scope boundary |
| `(832,320)` | `(5,32,5,255)` | Scope lower boundary |
| `(905,328)` | `(1,35,7,255)` | Scope / upper receiver boundary |
| `(1156,388)` | `(7,38,8,255)` | Main muzzle lower edge |
| `(448,750)` | `(7,24,5,255)` | Coat edge |
| `(446,753)` | `(6,31,6,255)` | Adjacent coat edge |

They are dark but opaque green-dominant colors, not transparency. The current code requires `G>=20` and both green-channel differences to be at least 32; these examples fall below the latter threshold. The independent boundary search found 97 nearly pure dark-green candidates (`R/B<=10`, `G>=20`, channel differences >=8). A broader search found 2,121 candidates, **not a certified whole-image defect count** because legitimate shaded material can satisfy broader predicates. The concrete nearly pure samples, their boundary positions and direct image inspection suffice to reject a clean-edge claim.

Do not return to the old global delta>=8 rule: the measured cyan-light deletion is its counterexample. Retained-RGB equality alone also cannot prove that legitimate pixels were not made transparent. Source-region/edge classification must distinguish that deletion case from dark chroma retention before another matte revision can pass.

## Exact bindings

Candidate root: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r1_e_flight_l/`.

| Artifact | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_L_IMAGEGEN_RAW.png` | `548872ee7d748d738ca6deb0bebe0bb5f3b42e948d91c9bf78cb8535fed9d692` |
| `MICA_C03_E_RUN_FLIGHT_L_EXACT_GREEN.png` | `94c150e0b05d1005f4e8704490028c29cd6b2dcc1a54869a84d8ad6862064edd` |
| `MICA_C03_E_RUN_FLIGHT_L_EDGE_MASK.png` | `0b68dde1d3d0323952e43038b5f62522ee311c5ec53fe729f13fa0723d36f4dd` |
| First failed `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA.png` | `0abcb8748b3fedf89e3a84c52abf70b9a57c741d3e9a7a9845b2960260c800a9` |
| Current `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_THRESHOLD_R2.png` | `9cbeb1a42da2f3489b8e2d4fd4484acd79c5e91f9fe998ca6f65903993cb97c7` |
| Current `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_THRESHOLD_R2_QA.json` | `b32cb434b112330490d4a7ddf9c401ac3fd4155b8352d601135a19c25e421af6` |
| `REQUEST.json` | `6863932462076303b7d2208ad0b7451ee711b0a70e3447c91baf3f4ac5ce1aa9` |
| `PROMPT.txt` | `70be9fbe5cd4a1dfb17a44b36acf57c30666484990d2eaa62623cc3dfa938e0d` |
| Single-attempt permit | `6d3fc8546d491feece29b94ac73dbf06fccf6c5da9408583f8e16b5baeed4e97` |
| Approved S neutral image | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| `SOURCE_RECEIPT_R7.json` | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |
| Supplied E reference | `57f13ac47daa5b4b786ad8ae69e57eb79baeb4d75593e5146899cdb0b4468584` |
| F6 `006.png` | `b5b2769d207106dd00cce4a171c133eb4088dcc031303e8945530a803ba19988` |
| F6 guide review bundle | `4e391f2742d34ffd46c4621854475b64400b9ea0a29089e71f3af35573ea7e0b` |
| Previous flight_r R2 quarantine manifest | `8eb42d673915860d222ad6b42f9679fde60bdf72e4f5961b46c1d477cc9b576c` |
| Previous Ponytail flight_r R2 review | `8bbbbe29cee1b4cdf786d2defeb234c3d40698a858fe5974b92596d3d3be144c` |
| `visible_frame_contract.json` | `cc4c0b8b4992be69078f41d6873d7eeeb37e69b73b46da48a251ac1c32675df8` |
| Inspected `derive_chroma_runtime_rgba.py` | `d4f2c323bb7445227be0c3ce78da77c4b2a7556d6e18bee913d0ec31e8e92a04` |

## Disposition

Retain this failed raw and every derived result, permit, request, mask, QA and review in project quarantine with exact path/hash provenance. Do not rename it into another phase, forge laterality annotations or produce a PASS receipt. Do not regenerate the good approved source master.

The skill's repeated-failure boundary now applies to phase/laterality: stop further generic pose variants, preserve a small explicit diagnostic comparing the two asymmetric thigh markers against the requested support phase, and obtain an independently reviewed mechanism change before the next production attempt. A correctly bound, explicit ImageGen repair of the failed target is a possible scope-compliant next mechanism, not an automatic approval. Do not locally repaint the equipment or substitute a Blender-rebuilt character. Independent harness/edge diagnostics can continue; this is not an instruction to abandon the project.

No temporal gait, actual ground contact, eight-direction walk/run, movement×aim firing, 30/60/120Hz runtime, HTML or Luna-readiness approval is given.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent frame review.
