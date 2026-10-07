# Ponytail FULL — MICA R3 exact repair-target scope review

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Reviewed UTC: **2026-09-07T16:41:25Z** (2026-09-08 01:41:25 KST).
- Exact reviewed subject: **`a909013d02e763d9c58abb03c746be8e6f597943684313443262e61a9cf9103a`**.
- Verdict: **PASS_REPAIR_TARGET_SCOPE_ONLY**, all six requested scope checks.
- This is not a frame, source, animation, runtime or promotion approval. The old target remains FAIL_NOT_PROMOTABLE.
- Applied: Ponytail FULL and `sable-motion-production`. I wrote only this report; no production code or assets were modified and no ImageGen, Blender, runtime, promotion or Luna execution occurred.

## Evidence and binding verified

I read the complete R3 `REQUEST.json` and `PROMPT.txt`, directly opened the exact quarantined target at its original 1254×1254 size, and directly opened the approved S neutral MICA source at its original 1024×1536 size. I inspected the selected target's own quarantine manifest, independently hashed every request path reference, and checked the target's exact membership in that manifest's file inventory. All references matched. The target actor/costume equals the request's `CHR_PROTO_03` / `MICA_RECON_C03`.

The latest subject function now binds the exact prompt, source receipt and latest previous failure in addition to the target, target's own quarantine manifest, phase, anatomical anchors, preserve/change lists and ImageGen input order. I independently reconstructed its canonical JSON hash and obtained the exact subject above. The earlier proposed subject `eac8901ca982432ab4d5cab417e3092e59d548c681b40bc83255cd1e5ebca3cf`, which omitted those prompt/source/latest-failure bindings, is **not approved by this report**.

The new expected output did not exist at review time. No new generated result is being reviewed. The complete licensed F6 Sprint_Loop guide was independently reviewed earlier as lower-body pose-guide evidence only; the current request binds that same exact guide and reviews. No full gait/contact conclusion is inferred from the target's one still image.

## Six exact scope checks

| Check | Verdict | Independent evidence |
| --- | --- | --- |
| `exact_failed_target_hash` | PASS | The primary target is the actual flight_r R2 raw with SHA `2c2cca4bcf5a806ba315810fc88367d2481d62418d464033903bdab40bff53f8`. It resolves beneath its recorded quarantine root and matches exactly one raw inventory entry in the target's own manifest SHA `8eb42d673915860d222ad6b42f9679fde60bdf72e4f5961b46c1d477cc9b576c`. It is not the latest wrong-laterality flight_l repair disguised as this target. |
| `requested_phase_laterality_already_present` | PASS, visible side relation only | The approved S source establishes the beige vertical thigh plate on anatomical right. In the selected target that plate is visibly on the forward thigh, approximately x626–671/y649–704, leading through the screen-right knee to the forward boot. The plate-free opposite leg trails toward screen-left. Thus the requested `flight_l` right-leading relation is already present, although this same relation was wrong for the target's original `flight_r` request. The still image does not prove preceding toe-off or a real support cycle. |
| `preserve_scope_is_visually_present` | PASS | The target visibly contains all five preservation groups: the marked right-leading/plate-free left-trailing relationship; a broad, uncrossed, airborne-looking sprint stride with coherent boot axes; recognizable MICA identity/costume; the same rifle with coherent two-hand grip and visible right-facing main muzzle; and full-body scale with all extremities inside the canvas. These are existing content to preserve, not absent anatomy to invent. |
| `change_scope_is_explicit_and_minimal` | PASS, scope only | The sole listed visible change is to align ribcage and pelvis to coherent strict E profile, without changing lower-body laterality or stride. The prompt explicitly rejects the current residual three-quarter/frontal torso and pelvis while preserving the marked leg relation, weapon and scale. This addresses the independently observed remaining profile problem and avoids another request to swap the target's legs. It is not proof that ImageGen will perform the edit successfully. No unrelated face/costume redesign is authorized. |
| `failed_target_remains_non_promotable` | PASS | The selected target's own manifest still records original phase `flight_r`, FAIL_NOT_PROMOTABLE status, `promotion_pointer_removed=true` and `disposal_allowed=false`. The request binds that manifest separately from the latest failed flight_l retry and requires a fresh project-local raw. The prompt expressly forbids renaming/repackaging the old target. This scope approval does not alter its historical rejection. |
| `imagegen_only_visible_art_boundary` | PASS | The request uses `generator=built_in_ImageGen` and `operation=repair_failed_frame`. Its explicit two-image order is the failed raster as primary edit target, then the approved neutral MICA image for identity/costume. Blender/UAL remains separately bound pose-guide evidence and is prohibited from supplying final face/body/costume/material/raster appearance. No local redraw or generic 3D appearance substitution is permitted. |

## Limits that remain in force

The new target selection removes one explicit contradiction in the previous edit setup: its primary image already contains the required leading-side relationship. This is a defensible scope change, not proof of an internal ImageGen attention mechanism or a guarantee of success.

Strict E profile is **not already approved**. A later output must actually correct chest and pelvis coherently without regressing knee/boot alignment, waist attachment, asymmetric costume markers or the gun/hands. It cannot pass by merely describing the unchanged three-quarter target as profile. The preservation lists mean preservation of the stated visual features and pose; they do not excuse a hidden leg swap or imply that a future generated raster is automatically byte-identical.

The raw target still has the previously failed background/edge history. Its old matte, previous frame reviews and phase annotations do not become approved by selecting it for editing. The newly generated raw will need its own preserved master, current reproducible RGBA, edge/subject-preservation evidence and fresh seven-check visual/Ponytail frame reviews. No 1080p final review-container, complete-frame, temporal grounding, full eight-direction movement, firing, runtime-rate, HTML or Luna gate is passed here.

The actual one-output generation permit and full request gate must still be valid before execution. This report is one independent scope-review input, not a standalone instruction to run generation. A changed prompt, source receipt, target, target failure inventory, input order or preserve/change contract requires a new matching scope subject/review. All existing failed outputs remain quarantined.

## Exact artifact hashes

R3 request directory: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r3_e_flight_l_profile_repair/`.

| Artifact | SHA-256 |
| --- | --- |
| Exact `REQUEST.json` inspected before review-bundle attachment | `587c7f8cd43970f5c0805feb37446bfea3b9ef59f701569f3926cce145f9c294` |
| `PROMPT.txt` | `db0866c27806479c15cf58b77383ad64f42879d85d6a5660b2f08c105a3d1275` |
| Primary quarantined flight_r R2 raw | `2c2cca4bcf5a806ba315810fc88367d2481d62418d464033903bdab40bff53f8` |
| Target's own quarantine manifest | `8eb42d673915860d222ad6b42f9679fde60bdf72e4f5961b46c1d477cc9b576c` |
| Latest previous-failure manifest, flight_l repair R2 | `9ba8114c9122289af9240e97bef879d83b05f09431dcbe42c94ef5d6335c1861` |
| Approved S neutral source image | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| Approved source receipt R7 | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |
| F6 guide image | `b5b2769d207106dd00cce4a171c133eb4088dcc031303e8945530a803ba19988` |
| F6 guide review bundle | `4e391f2742d34ffd46c4621854475b64400b9ea0a29089e71f3af35573ea7e0b` |
| Inspected `visible_frame_harness.py` subject-binding revision | `8413c3f8274b7ca2ff6684ed88ea1350536b61327bbcaa0f56baed1b36e4b0c6` |

Adding the independently verified scope-review bundle reference changes the encompassing request file hash; the final single-attempt audit/permit must bind that final request. It must not change the scope subject reviewed here. This report itself does not reserve an attempt or seal a frame receipt.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL, exact repair-target scope only.
