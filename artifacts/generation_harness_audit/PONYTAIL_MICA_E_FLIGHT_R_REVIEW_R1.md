# MICA E / run / flight_r — independent Ponytail FULL review R1

- Reviewer: `/root/ponytail_motion_audit`.
- Reviewed UTC: **2026-09-07 15:00:50** (2026-09-08 00:00:50 KST).
- Exact subject: `40864dab9b047b08f2b2152c03bd9a0c07f04732371cba1f5b888c2befc6cdbb`.
- Overall verdict: **FAIL_NOT_PROMOTABLE — do not seal a frame receipt**.
- Skill used: `sable-motion-production`, applying Ponytail FULL semantics and the ImageGen-visible-art / Blender+UAL-motion boundary.

## What was actually inspected

Personally opened the raw ImageGen image, exact-green image, actual subject mask, both 1920×1080 review boards, annotations, request/prompt, manifest, normalization QA and source receipt R7. The approved MICA source and exact E weapon reference had also been personally inspected in this review sequence. I opened the exact bound Blender/UAL guide `frames/000.png` and read its capture metadata rather than inferring its pose from the filename.

A read-only recalculation of `visible_frame_harness.audit_frame(FRAME_MANIFEST.json)` exactly matched the supplied audit: `errors=[]`, same subject. This proves current bindings and the implemented technical checks, **not visual correctness**. No generation, render, full test matrix, image edit, source edit or promotion was performed. Only this report is written.

| Bound evidence | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_R_IMAGEGEN_RAW.png` | `d7e4288745dd52a532c81e2115d5da1732ff724c90a6cf85c715de99a0de4018` |
| `MICA_C03_E_RUN_FLIGHT_R_EXACT_GREEN.png` | `133c0f8f174e7674e61a9ad5e476696e6c32af3fcadb11e54db52dd41a5a76c5` |
| `MICA_C03_E_RUN_FLIGHT_R_MASK.png` | `dbee3cc4fdb2bc664c3ddefe2b820c8f98c6a986edc88a8200b77a17181c0fb7` |
| `ANNOTATIONS.json` | `f56ca9b84535d661a8b38db9dd66e1fd1b6e3d7c900040e76fe253d017596330` |
| `SOURCE_RECEIPT_R7.json` | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |
| `MICA_C03_E_FLIGHT_R_GREEN_1920X1080.png` | `9d7d668af1396054ec375f0f4cffd329128bf6f14453fd5c59c6bd26b22e7666` |
| `MICA_C03_E_FLIGHT_R_DARK_1920X1080.png` | `6775d3f1767d958f0ddd37205b2eb488858b5fae9e32fa1aedcd329ffb0f8f8a` |
| `MICA_C03_E_FLIGHT_R_FRAME_AUDIT_R1.json` | `75a48a495f2cd1c4c005be25f5b6ba6cf214dfb55dd19658239a40b6c98846ac` |

The first four files are under `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r1_e_flight_r/`; the review boards/audit are under `artifacts/generation_harness_audit/`. The source receipt is in `art_src/characters/mica/rigged_v2/source_front_r1/`.

## Seven independent judgments

| Check | Verdict | Actual finding |
| --- | --- | --- |
| `identity_and_costume` | **PASS, static frame only** | MICA's face, brown side braid, navy tactical clothing, beige coat binding, teal lining, paired back equipment, knee protection and rifle are recognizable and broadly continuous with the actual references. The forearm light is visibly intact in this version. This does not certify continuity with nonexistent adjacent frames. |
| `anatomy_and_limb_count` | **PASS, static major anatomy only** | Two arms/hands and two connected legs/boots are visible. No extra limb, crossed-leg knot, obvious detached waist or ghost hand is apparent. The calves taper toward the ankles; I do not see the earlier barrel-like swelling failure in this single image. Temporal volume stability is untested. |
| `whole_body_direction` | **HOLD** | Travel, face and rifle clearly point screen-right, but the torso/pelvis still expose a substantial three-quarter front view. This does not establish the prompt's strict common E profile of rib cage, pelvis, knees and feet. There is no obvious 90-degree waist discontinuity, but its absence is weaker than passing strict E alignment. |
| `phase_and_stride` | **HOLD** | The broad front/back stride is clearly visible; narrow shuffling is not this frame's defect. However the exact anatomical-right `flight_r` assignment is stated from the prompt, not independently established. The actual bound guide is a left-facing in-place **walk** diagnostic, not a matching E run-flight phase. A split-leg picture and a minimum foot-distance test cannot establish the intended cycle phase. |
| `feet_ankles_and_contact` | **HOLD** | I see no clear 90-degree out-of-plane ankle rotation, duck-foot yaw or leg crossing. The forward boot is dorsiflexed and the rear boot points downward/backward, which must not be confused automatically with the earlier wrong-axis ankle bug. Neither sole is claimed planted, so raised feet alone are not a failure of a flight frame. But correct anatomical laterality, common-ground clearance and correspondence to the requested run phase are not supplied by the actual guide or the two point labels. No contact/grounding PASS is issued. |
| `weapon_hands_and_visible_muzzle` | **PASS, static image only** | Two plausible continuous grips hold the established carbine, with the main upper barrel's terminal tip visible and pointing east. The lower attachment is distinguishable from that barrel. The annotated base-to-tip segment follows the visible terminal barrel area. This does not approve a runtime socket, an actual shot or muzzle continuity over motion. |
| `matte_edges_and_subject_preservation` | **FAIL** | The dark board visibly retains large green background islands between the hands/arms and rifle, plus green fringe around hair, equipment, weapon and garment/boot edges. The mask classifies those interior gaps as subject. Retained-pixel equality is true but does not make the matte correct. The prior forearm-light deletion is not the newly observed failure here. |

## Hard matte failure: actual pixels, not a thumbnail impression

The source is native **1536×1024**, displayed 1:1 in each native **1920×1080** board at offset `(192,28)`. The mask retains **285,384** pixels. Raw versus normalized comparison found **zero changed pixels within that retained mask**.

Nevertheless, **4,031 retained-mask pixels** satisfy the strong green-dominance test `G >= R+80 and G >= B+80`. This count is a diagnostic, not a declaration that every green pixel is expendable. Two visually unambiguous interior background components account for **1,478** of them:

- **1,174 pixels**, source bbox `(910,273)`–`(955,322)`: green gap below the receiver and between the gripping arms/weapon.
- **304 pixels**, source bbox `(904,272)`–`(935,290)`: adjacent enclosed green gap in the hand/trigger area.

Concrete source-coordinate samples:

| Pixel | Raw RGB | Exact-green derivative | Mask | Dark board at offset `(192,28)` |
| --- | --- | --- | --- | --- |
| `(932,320)` | `[10,223,22]` | `[10,223,22]` | subject | `[10,223,22]` |
| `(945,299)` | `[15,227,18]` | `[15,227,18]` | subject | `[15,227,18]` |

These are unchanged **background pixels wrongly retained**, not deleted bright costume pixels. The board faithfully exposes the bad mask; it is not an evidence substitution. Thin visible green outlines also remain after the exterior flood, including around the head, sensor fins, rifle rail and coat.

`normalize_imagegen_chroma.py:42` computes only green pixels connected to the canvas border; `candidate` is restricted by a colour-distance threshold. It cannot reach closed background holes and leaves contaminated edge samples outside that threshold. The emitted `alpha_ready: true` at line 112 is therefore not supported by this image. `visible_frame_harness.py:195` reproduces the same mask and line 201 checks surviving-pixel equality, so this bad matte correctly reaches only `HOLD_VISIBLE_FRAME_REVIEW`, not independent visual PASS.

Do not repair this by restoring the old “large bright component means background” heuristic, globally deleting every green-looking costume pixel, or locally repainting subject edges. The correction must preserve ImageGen-visible artwork and obtain an independently reviewed clean matte; contaminated/ambiguous visible pixels remain ImageGen repair work.

## Phase evidence mismatch

The exact guide image SHA is `a7638470574cd5d0bd52cf410839728fcc657a3ec3064273ff54341e73955d19`. Its capture states:

- `scope: SINGLE_LICENSED_MODEL_IN_PLACE_WALK_DIAGNOSTIC`;
- `SeedSan_UAL_Walk_DIAGNOSTIC.blend`;
- frame `0`, time `0.0`, cycle `1.3333333333333333` seconds;
- `production_ready: false`.

Visually, that guide faces screen-left and is not the generated shouldered E run-flight silhouette. `_audit_pose_guide` checks license, hash and capture membership, but membership is not direction/run/phase correspondence. `ANNOTATIONS.json` explicitly derives right-leg laterality from what the prompt requested. That is an intention, not independent observation. This mismatch must be resolved before calling the frame a verified Blender+UAL phase transfer or expanding it into a cycle.

## Required disposition

Retain this failed image, its raw original, masks, permit, hashes, annotations and review evidence in project quarantine; do not seal a frame receipt or produce the remaining phases from an assumed PASS. The S source receipt remains a separate unchanged source approval. A narrowly corrected frame must use a correct actual direction/phase guide, preserve identity/costume, and independently pass the matte/edge review at native scale.

This report approves neither a full gait nor real grounding, move×aim firing, 30/60/120Hz behavior, playable HTML, Luna reproduction or production promotion. The 1080p container PASS and empty technical error list do not change this **FAIL_NOT_PROMOTABLE** verdict.
