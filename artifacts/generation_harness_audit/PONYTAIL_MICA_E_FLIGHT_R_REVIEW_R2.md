# Ponytail FULL — MICA E/run/flight_r visible-frame review R2

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review timestamp: 2026-09-07T15:51:32Z (2026-09-08 00:51:32 KST).
- Exact audit subject: `0bdb336f805665955d182df2df4ff10b4bd6a3c829a57d80b7b574b596376c5b`.
- Actor/costume: `CHR_PROTO_03` / `MICA_RECON_C03`.
- Verdict: **FAIL_NOT_PROMOTABLE. Do not seal a PASS frame receipt.**
- Applied: Ponytail FULL and `sable-motion-production`. Scope is this one ImageGen frame. No source/code edits, rendering, generation, registration, promotion, runtime launch or Luna work was performed.

## What I actually inspected

I directly opened the 1254×1254 raw ImageGen image, preserved exact-green master, edge mask and actual runtime RGBA; the 1920×1310 green/dark review boards; the approved S neutral MICA master and the supplied older E master. The raw/runtime images were displayed at their original 1254-pixel scale. I read the exact request, prompt, annotations, frame manifest, normalization/runtime QA, attempt permit, frame audit, review manifest, source receipt and source left/right landmarks. The bound Sprint_Loop E F14 guide and complete 17-frame cycle had already been directly inspected in my separately hashed R2 guide review.

I independently hashed every binding in `MICA_C03_E_FLIGHT_R_FRAME_AUDIT_R2.json`: no mismatches. I also decoded the raw/master/mask/runtime pixels and compared retained RGB. These checks establish the evidence identity, not its visual approval. The 1080p validator was run read-only on both current boards at 2026-09-07T15:50:25Z: container/decode PASS, `quality_claim=false`. Neither that result nor `errors=[]` passes the visual defects below.

## Seven required verdicts

| Contract check | Verdict | Observed evidence |
| --- | --- | --- |
| `identity_and_costume` | PASS, static appearance only | Face, brown side braid, dark patterned tactical coat, beige edging, teal lining, cyan back equipment, fitted trousers, guards, pouches and boots remain recognizably the approved MICA design. No generic Seed-san robot arms, short hair or bare feet were copied. The distinctive right-thigh pouch is retained; its placement identifies the phase conflict below rather than validating the declared left-leading label. |
| `anatomy_and_limb_count` | PASS, this frame only | Two coherent human arms and legs, one head, two boots. No duplicate knee, ghost hand, disconnected waist, merged feet or apparent barrel-shaped calf deformation is visible. This does not establish temporal deformation quality. |
| `whole_body_direction` | HOLD | Head, gun, knee travel and boot toes read screen-right, and the old gross 90-degree waist snap is not present. However the chest/zipper/lapels and pelvis remain a three-quarter presentation rather than the requested unambiguous strict E body profile. Both the older E reference's frontal torso and this frame must not be treated as proof of strict full-body profile. Exact body alignment needs resolution before PASS; no numeric body-yaw angle is fabricated from this raster. |
| `phase_and_stride` | **FAIL** | The stride is visibly broad, not a tiny shuffle. But the leg carrying the approved **right-thigh beige vertical-plate pouch** is the forward leg. The near-side right trigger arm and right-side braid agree with that laterality. The picture therefore reads as right-leg-leading, contradicting `flight_r` = flight after right support/toe-off with **left leg leading**. An annotation naming the forward boot `foot_left` cannot reverse the drawing's anatomy/equipment continuity. |
| `feet_ankles_and_contact` | PASS, isolated airborne silhouette only | The leading boot follows its shin, and the rear boot pitches downward in the sagittal running plane. No visible 90-degree sideways ankle yaw, inward crossed boots or swollen calf is present. Neither foot is visually claimed planted; no independent ground/contact or time sequence is approved. This PASS does not cure the wrong anatomical lead leg. |
| `weapon_hands_and_visible_muzzle` | PASS, static image/socket annotation only | The rear hand grips the trigger area and the front hand wraps the fore-end without a visible extra hand. Main barrel and separate lower auxiliary cylinder remain legible. The annotated main muzzle near `(1154,384)`, using `(1088,384)` for the local barrel axis, is consistent with the visible horizontal main barrel rather than the lower device. No actual projectile, recoil, moving socket or firing runtime has been tested here. |
| `matte_edges_and_subject_preservation` | **FAIL** | The runtime removed the conspicuous bright green holes and preserves every retained visible RGB byte. It nevertheless retains opaque dark-green halo pixels along gun, coat and boot boundaries. A strong-green count of zero only means the image no longer meets that particular threshold; it does not prove clean separation. Concrete original-scale samples follow. |

Result: four narrowly scoped static PASS checks, one HOLD, two FAIL checks. The frame as a whole fails.

## Anatomical laterality: the concrete contradiction

The approved S image is frontal. Its `S_LANDMARKS_R3.json` explicitly places anatomical right hip at `(448,651)` and left hip at `(570,651)`. In that source, the pouch with the conspicuous beige vertical front plate is on the screen-left/anatomical-right thigh (approximately x380–430, y730–840); the opposite thigh pouch has a different dark face. The source braid is also over the anatomical right side.

In this candidate, the matching beige-plate thigh pouch sits on the leg running from the foreground hip through the forward knee to the boot at approximately `(919,1100)`. The other boot trails near `(226,965)`. The source right-side asymmetry and occlusion order contradict the annotations' `foot_left` naming. If one insists the drawn forward leg is anatomical left, then the right-specific equipment has migrated to the opposite leg and costume continuity fails instead. **Neither interpretation permits all seven checks to pass.**

The request and F14 guide now use the correct support-foot phase definition; the remaining error is in the generated picture, not permission to silently rename it to another phase. The older E reference is useful for identity/weapon details but visibly has a frontal/three-quarter torso. Its entire silhouette is not authority for the requested strict E motion pose. Competing reference influence is a possible generation mechanism, not a proven claim about ImageGen internals.

## Runtime alpha: technical improvement but remaining halo

Independent pixel checks:

- Raw→normalized RGB changes inside the supplied retained mask: **0**.
- Runtime visible RGB differences from raw: **0**.
- Runtime alpha: **1,263,799 pixels at 0**, **308,717 pixels at 255**, no intermediate alpha.
- Runtime pixels meeting the current strong-green predicate (`G>=80`, `G-R>=45`, `G-B>=45`): **0**.
- The QA records removal of **4,580 non-exact strong-green pixels**. The obvious bright enclosed background gaps are no longer filled green in the RGBA.

The following are actual retained RGBA pixels, using the original 1254×1254 coordinates. Each has alpha **255**, not a translucent edge:

| Pixel `(x,y)` | RGB | Visible region |
| --- | --- | --- |
| `(1050,408)` | `(2,79,4)` | Fore-end / lower barrel boundary |
| `(873,479)` | `(1,76,0)` | Magazine lower boundary |
| `(623,749)` | `(2,76,0)` | Lower garment/leg boundary |
| `(619,751)` | `(5,77,6)` | Adjacent lower garment edge |
| `(905,1122)` | `(7,76,6)` | Forward boot/sole boundary |
| `(1154,380)` | `(13,78,11)` | Main muzzle outer edge |

These dark green-dominant samples miss the automatic key only because `G` is below 80. That boundary exists in `derive_chroma_runtime_rgba.py:background_mask`; it is not evidence that the retained color belongs to MICA. A broader diagnostic search (`G>=35`, `G-R>=8`, `G-B>=8`) finds 3,032 candidates, including 2,351 on the one-pixel visible silhouette boundary. **That whole candidate count is not a certified defect count**: some low-saturation material may legitimately fall into a broader color test. The specifically sampled nearly pure-green opaque edge pixels and the viewed dark composite are sufficient to fail clean matting.

The original source remains intact. Do not repaint character RGB, erase ambiguous teal lining/cyan lights, or delete the candidate to disguise this failure. A new reproducible matte revision may address only proven background contamination and must receive fresh edge review. Matting alone cannot repair the anatomical phase error.

## Exact artifact bindings

Candidate directory: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r2_e_flight_r/`.

| Artifact | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_R_IMAGEGEN_RAW.png` | `2c2cca4bcf5a806ba315810fc88367d2481d62418d464033903bdab40bff53f8` |
| `MICA_C03_E_RUN_FLIGHT_R_EXACT_GREEN.png` | `cfebf6576434fa226802342d95d08332c75386cd9fdc6ecd7103997d6183ac6a` |
| `MICA_C03_E_RUN_FLIGHT_R_RUNTIME_RGBA.png` | `8c20b05099e0ee14802af5e01e3e6e7475c0cf91260d0e14a4aa9edcc8cb46f4` |
| `MICA_C03_E_RUN_FLIGHT_R_EDGE_MASK.png` | `3673f2b9e4985e86441abfa561266ed088ce54f6cdd337402f0c3550403f66e3` |
| `FRAME_MANIFEST.json` | `625ecfe6b5178628fe158a254cb9cb5ac782ddd57463a5a249bfc6203cc2e432` |
| `REQUEST.json` | `c45b4f1b3724a170571ff944a90323ce697e7b9af56e1a890ae294ec8b3cb29b` |
| `ANNOTATIONS.json` | `83be0af262af9ab6429d1a58f4476ce2b6a3ee58184f251c3579f5e04a2bfd93` |
| Audit directory `MICA_C03_E_FLIGHT_R_FRAME_AUDIT_R2.json` | `33bd9d30d4c8e2d2d9b691df800eb7bd2329cd19ced0183b2b80de857822fe3a` |
| Audit directory `MICA_C03_E_FLIGHT_R_R2_REVIEW_MANIFEST.json` | `00da95f65af8d5582f2b1c5080e49af8f6ab9d39407b7226afdecacba52cc9e8` |
| Audit directory `MICA_C03_E_FLIGHT_R_R2_GREEN_1920X1310.png` | `3f8ff6a3c617ea2029efde93626b7f57e23e5f0abb7af3f106b1f35f5bcea9e4` |
| Audit directory `MICA_C03_E_FLIGHT_R_R2_DARK_1920X1310.png` | `9c36b067902463859c8b04b02f4b930922f1a3d939a324094d032fb15f3473fe` |
| Approved S neutral master | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| Supplied older E direction master | `57f13ac47daa5b4b786ad8ae69e57eb79baeb4d75593e5146899cdb0b4468584` |
| Reviewed Sprint_Loop E F14 guide | `f8297a11abbb149edbd14ff1bfb76104c15d559bbb986994d5a0ff6b070a70d5` |

## Disposition

Preserve the failed raw, derivatives, request, permit, annotations and review evidence under the project failed-asset policy. Do not seal this as an approved `flight_r`, relabel its annotations to overcome the visual verdict, or use it in an animation/HTML batch. The good source master remains valid; it is not a regeneration target. Resolve anatomical-side continuity and strict body direction before another pose request, and treat matte cleanup as an independent, evidence-bound operation. No full-cycle, eight-direction, firing, runtime-rate, HTML-parity or Luna readiness approval is given.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent frame review.
