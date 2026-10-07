# Ponytail FULL — actual MICA E/run/flight_l R4 frame

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- UTC: **2026-09-07T17:39:18Z** (2026-09-08 02:39:18 KST).
- Exact frame subject: **`55cbf6239a0d1f9ded3fd842037df8d9f8cb9bbecafd3835162617c4382ecdc3`**.
- Actor/costume: `CHR_PROTO_03` / `MICA_RECON_C03`.
- Verdict: **PASS — SINGLE STATIC VISIBLE FRAME REVIEW ONLY**, seven checks below.
- Applied: Ponytail FULL and `sable-motion-production`.

This is not temporal gait, actual ground contact, movement/fire runtime, sequence, HTML, Luna or production-promotion approval. No production asset/code was edited and no image generation, Blender render or runtime was launched. Only this signed report was written.

## Actual evidence inspected

I directly opened the new raw, normalized master, subject mask and RGBA at their native **1254×1254** size; both complete **1920×1310** 1:1 review boards; the actual approved true-E source; and the approved neutral S source. I read the exact request, frame manifest, annotations, one-attempt permit, normalization/runtime QA and audit. The prompt and source R7 receipt were also inspected during the immediately preceding exact R4 scope review; their hashes remain unchanged.

Independent file hashing verified **all 26 audit bindings with zero mismatches**. Independent canonical hashing of those bindings returned the exact subject above. Both review boards embed the source at scale **1.0**, offset **(333,28)**: green-board master mismatch **0**, dark-board visible RGBA mismatch **0**. Although their filenames end in `1920x1080`, actual decoding and their manifest correctly show **1920×1310**. I reran the 1080p validator read-only at **2026-09-07T17:36:57Z**: both containers/decode PASS, `quality_claim=false`. This was not a dynamic capture test.

## Seven contract checks

| Check | Verdict | Direct visual evidence and limitation |
| --- | --- | --- |
| `identity_and_costume` | PASS | MICA's recognizable face and brown right-side braid, navy patterned long coat, beige piping, teal lining, asymmetric thigh equipment, guards/boots, cyan devices and the established rifle remain present. The image does not substitute the generic pose-guide model's appearance. This evaluates the visible authored frame, not unseen costume surfaces. |
| `anatomy_and_limb_count` | PASS | One head, two coherent arms/hands and two separated connected legs/boots. No visible extra limb, merged leg, detached waist, rectangular coat reconstruction or inflated barrel-shaped calf. The garment overlaps read as connected cloth, not detached panels. Temporal deformation is not established. |
| `whole_body_direction` | PASS, static E depiction | The head is in right-facing profile; the near shoulder/upper arm is foreground and the far arm reaches forward around the rifle rather than presenting a second frontal shoulder. The ribcage side contour and hip/leading-thigh connection remain coherent with the right-facing knee/boot and weapon axes. There is no visible right-angle waist kink or pelvis facing against the leg travel. The narrow visible garment/placket edge is also present in the actual true-E source; its visibility alone is not evidence of torso yaw. This is the judgment of the whole pose against that reference, not a numerical 3D yaw measurement inferred from one strip of clothing. |
| `phase_and_stride` | PASS, static phase depiction | The beige vertical-plate anatomical RIGHT thigh connects to the forward screen-right knee and boot. The plate-free anatomical LEFT leg trails. The legs are broadly separated and uncrossed; this is a flight-like sprint pose, not a tiny shuffle or high-knee march. It agrees with the requested F6/`flight_l` depiction. One raster cannot prove that left toe-off preceded it or that later contact occurs correctly. |
| `feet_ankles_and_contact` | PASS, isolated airborne pose | Leading shin/boot alignment is coherent; the trailing boot is plantar-flexed in the running plane rather than yawed sideways by 90 degrees. Neither foot is represented as planted, and no crossing/duck-foot contradiction is visible. No actual floor height, sole clearance over time, contact slip or world speed is validated. |
| `weapon_hands_and_visible_muzzle` | PASS, static image/annotation | The two-hand grip is coherent, with the trigger hand at the receiver and support hand beneath the fore-end. The main barrel points right, with a visible endpoint separate from the lower auxiliary cylinder. The annotated `(1092,385)`→`(1158,385)` axis lies on that actual barrel; both samples are opaque, and the endpoint matches the visible far-right barrel tip. No projectile, recoil or moving-fire socket has been exercised. |
| `matte_edges_and_subject_preservation` | PASS, this exact derivative | Hair, garment/boot silhouettes, main cyan lights and teal lining survive native master/RGBA/dark-board comparison without an obvious missing subject chunk or unmistakable green halo. Closed weapon gaps are transparent. Independent checks confirm retained RGB equality and zero strong-green alpha-boundary residue. Four selected low-chroma removed edge samples were inspected locally and did not establish deletion of a cyan light core or other legitimate subject region; details below. This is not a universal claim about every future matte. |

The E-direction judgment is not a claim that a large measured yaw correction occurred between R3 and R4. It is a fresh judgment of these exact R4 pixels using all body cues and the actual reference. Earlier quarantined R3 bytes/reviews are not retroactively promoted or rewritten by this result.

## Independent matte and pixel findings

- Alpha: **1,273,250 at 0**, **299,266 at 255**, no intermediate alpha.
- Raw→normalized changes inside the retained source mask: **0**.
- Visible runtime RGB differences from raw: **0**; runtime pixels outside source mask: **0**.
- Opaque outer-border pixels: **0**.
- Strong-green family: **91 retained interior matches, zero alpha-boundary matches**, independently agreeing with QA.
- Independent synchronous four-neighbour reconstruction, without calling the producer's mask function: **zero saved-alpha mismatches**, converging in three expansion rounds.
- Actual inclusive visible bbox: **(161,104)–(1158,1121)**.

The strong-green predicate is `G>=12`, `G-R>=16`, `G-B>=16`, `4G>=5R`, `4G>=5B`; the boundary is four-neighbour visible/transparent adjacency. Zero boundary residue is partly an algorithmic consequence of connected growth, so it is not used alone as visual proof.

All eight previously examined back-device edge coordinates remain opaque with exact **this-R4-raw** RGB: `(564,185)`, `(563,192)`, `(562,199)`, `(561,205)`, `(560,211)`, `(560,212)`, `(559,218)`, `(558,222)`. The old frame's color values are not copied as a new-frame requirement. Examples in R4 include `(564,185)=(107,226,194,255)` and `(558,222)=(26,153,127,255)`.

Additional native interior patches were fully preserved, with zero transparent pixels and zero RGB changes: forearm-light core `(621,421)–(677,426)` **280 pixels**, teal lining `(425,706)–(445,724)` **360 pixels**, face `(756,207)–(768,231)` **288 pixels**, and right beige plate `(679,656)–(687,675)` **152 pixels** (half-open bounds). A fixed axis-aligned rectangle around the slanting back-device light also includes real background; its transparent pixels are not treated as deleted light by assumption.

A deliberately broad cyan-family diagnostic selected four removed source-mask pixels: `(517,196)=(28,139,111)`, `(972,358)=(89,134,106)`, `(1118,412)=(104,132,104)`, `(887,938)=(100,139,110)`. Original-scale local raw/RGBA comparisons place them on the back-device, upper weapon, lower cylinder and boot-edge mixed-background boundaries, respectively. No missing luminous core or new silhouette chunk was visible there. This diagnostic predicate is not a semantic subject mask or a certified defect count. Small diagnostic crops were examined in memory only; no additional image artifacts were written.

## Exact content hashes

Candidate: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r4_e_flight_l_strict_profile_repair/`.

| Artifact | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_L_STRICT_PROFILE_REPAIR_R4_IMAGEGEN_RAW.png` | `1dff009ab14bffa419c42d2ee335d954d15af5f3025019f99cc089f4cea9955c` |
| `...EXACT_GREEN.png` | `2b34d1610b27a364d2a847b055b4be9a3bab1e74ed4fbf6dbf129adcce99f50a` |
| `...EDGE_MASK.png` | `411e53846e12731b1d24ab96637a407ccded4ec4bb6d7e1c7245cfde6344609b` |
| `...RUNTIME_RGBA.png` | `559a816b2c4c29669685eb515ae8cdc42bc9d156fd6740215914018a304f27e2` |
| `FRAME_MANIFEST.json` | `1f0ddd3b2f4fa11e865a04a0107c28797eb3246768d3c1833f2995407f285939` |
| `ANNOTATIONS.json` | `bb1cdeee8129625f9cc2e7887ce927b54edf2018486462d2e133b8f2dba75743` |
| Exact frame audit | `aeb5d7727e7ea3d4487889f07779a9ec6093a39da36e15a3fc18614ac187178f` |
| Green native review board | `b083dc31579d9a174cf4969ba194afaa2a98255d2c47e27c31638d4850c39394` |
| Dark native review board | `02dab1908b30e5bfd5dc6351f57d58dfb5eeff2b13b81180720ab3026f992073` |
| Review manifest | `42aeee7b8f94a734926d3922ee1112fa25b0f1dad0f3285edf233b1d4d8397c2` |
| Actual true-E source | `7ece6e83561bf3c9ee720b4c5a1f75820f73ae4afce95b895fe9b38d3299f4a1` |
| Approved S neutral source | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| Source R7 receipt | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |

Only this exact E/run/flight_l static frame receives the seven-check visual PASS. Sequence continuity, all other phases/directions, actual contact/cadence/speed, 8×8 movement/aim firing, 30/60/120Hz runtime, interactive HTML and final independent/web promotion gates remain separate and unapproved by this report. Failed assets stay quarantined under the user's retention rule.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent actual-frame review.
