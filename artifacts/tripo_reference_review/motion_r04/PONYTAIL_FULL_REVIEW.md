# Independent Ponytail FULL review: anatomical labels for E/contact_l

Verdict: **PASS for the three exact E/run/contact_l pose-guide subjects below**, with no MICA raster, runtime, firing, complete-cycle or production-pointer approval. This is one independent reviewer, `/root/tripo_intake_review`, supplying the Ponytail FULL role. The visual role must be separately authored.

Current base guide: `pose_guide_r02/E_CONTACT_L_GUIDE_DRAFT_R2.json`. Semantic draft: `pose_guide_r02/SEMANTIC_GUIDE_DRAFT.json`. Exact subjects are those in `REVIEW_SUBJECTS_R2.json`:

- Pose: `2d5c8df78af88510944e566ee1b037448dc3b1f56d83d32ae5ad01d0b53e82dc`.
- Contact: `e3240a575f47d02779b16dbb727edfbfadd355c64df8f6587151a722a9ff6fa0`.
- Semantic labels: `eec2a89035fd0fd94305325639f1bdfec817aa0c13015b2fe2fbc96339f66f02`.

I recomputed all three subjects against the current files. The current visible-frame gate SHA256 is `7d4a7660afa321e457bc9bc11d1c6d7113d12e96dd7efec967c1ee7a72ffd4fe`, and semantic gate SHA256 is `9ce419f7901f8b6f224660d0130bea7f4d79e91b93bd17db3b576b002920bf05`. Earlier hashes and reviews remain historical; this review does not silently reuse them.

## What was independently checked

I read the actual annotation builder, semantic audit, current entrypoint branch and shared review format. The annotation builder opens the exact licensed target blend, verifies the exact source result/calibration, uses the original named skin groups to label polygons, and changes only in-memory materials/camera for reference rendering. It does not save or reconstruct a character mesh. The current child explicitly compares CLI result/calibration, current builder and helper against INPUTS before an exclusive execution claim. The actual INPUTS and claim match. All output/cache/log paths stay project-local.

I directly opened `ANNOTATED_CONTACT_L_1920.png` at native 1920×1080. The blue leg is the forward supporting leg and the orange leg trails with its foot raised. The two leader lines end on the corresponding actual knees. Text is legible, no sole is obscured, the body is contained, and the fixed-floor line remains visible. The image explicitly states that limb colors are labels and are not costume/runtime pixels. Its SHA256 is `c479c10cc4a38c36967b783aa7ab94a00098d89b307befea7412c2b8d1992946`.

I also executed one separately owned read-only Blender 5.2.1 probe against the saved source blend. It rendered nothing and saved no blend. The probe's native output and log are `NATIVE_MAPPING_QA.json` and `native_mapping_blender.log` in this directory. It independently verified:

- Left deform groups are thigh_l/calf_l/foot_l/ball_l, indices 14–17; right groups are their `_r` counterparts, indices 18–21.
- Averaging actual leg-chain weights over each existing polygon reproduces exactly 1,780 left, 1,775 right and 7,035 neutral polygons. A label requires dominant mean chain weight greater than 0.25; no manually drawn replacement limb determines membership.
- All 211 left and 213 right sole vertices have at least 0.9999999702 own-chain weight and zero opposite-chain weight. The two label assignments are therefore unambiguous at the measured feet.
- Actual neutral REST sole arrays equal the calibration's arrays and reproduce the same floor, -4.290452437771819e-9 m. All 49 evaluated action sole arrays exactly equal the saved calibration. The exact contact row also equals the semantic geometry report.
- Independently read pose-bone heads agree with the named calibration joints. Recomputing the orthographic projection from actual whole-cycle bounds gives maximum joint error 0.000175 px, sole error 0.000201 px and floor-line error 0.000106 px relative to the annotation geometry. Leader-line target positions are not guessed from silhouette pixels.
- The input blend SHA256 remained `4a41f38bed059b3c8f0283d62c666ef8786e3f2e711897a818466b7564cd9c72` before and after the probe.

## Required check judgments

All seven base pose checks PASS for this exact guide. `exact_direction` is E in the fixed side camera; `action_identity` is the explicitly derived Tripo reference action; `phase_support_mapping` is anatomical left support and right trailing at sample 23/frame 7.1875; `feet_and_ankles` are visible and follow the actual named chains; `torso_silhouette` supplies direction/load context only; `full_body_visibility` is supported by the native image and whole-cycle camera fit; `pose_guide_only_boundary` excludes generic body/arm appearance and all guide pixels from MICA artwork/runtime. Prior directly inspected base phase images are unchanged and remain evidence for distinction, not blanket approval of other ImageGen phase requests.

All six contact checks PASS for this exact guide. `exact_current_gate_and_contract` uses the fresh current-gate ref and recomputed subject. `exact_calibration_report_and_capture` retains the identical result/blend/calibration/capture graph. `independent_sole_vertices_match` is now additionally confirmed by the separate native reopen. `fixed_floor_contact_and_phase_semantics` retains the actual REST floor, left contact clearance 1.999999 mm, eight distinct calibrated phase samples and left/right contact-to-down pelvis drops of 27.929/25.680 mm. `feet_ankles_pelvis_visual_distinction` agrees with the unchanged native contact/down/passing evidence. `pose_guide_only_boundary` retains the same lower-body-only restriction.

All four semantic checks PASS. `exact_anatomical_deform_group_mapping` is supported by the independent group/weight/polygon audit above. `unchanged_evaluated_pose_and_fixed_floor` is supported by exact native REST and all49 action sole equality. `native_annotations_match_actual_limbs` is supported by native visual inspection and independent projected-joint calculations. `geometry_only_no_sable_appearance` is supported by the unmodified saved mesh, label-only materials and explicit reference boundary. Blue means anatomical LEFT geometry; orange means anatomical RIGHT geometry. Neither color is an approved MICA costume change.

## Current gate delta and regression checks

The current request branch detects the semantic manifest or its designated input role, requires the exact E/run/contact_l reviewed manifest, and requires exactly one tool input resolving to the manifest's exact annotated image. Its bindings include the actual annotation, source geometry, generator and review evidence. Existing source authority and base pose/contact audits remain in the shared request/reserve/frame/seal/verify/sequence path.

The initial semantic gate incorrectly treated inline review objects as path/SHA references after calling the shared review verifier. I reported that defect before approval. The author corrected the loop to resolve each actual `reply_evidence`, and added a positive-path isolated mock test. That test does not create production replies. The first fresh guide draft also retained the old current-gate field; the author preserved it and created `E_CONTACT_L_GUIDE_DRAFT_R2.json` with the actual current ref. I verified the corrected delta and subjects, rather than approving the stale files.

Fourteen relevant tests passed on the current implementation: five semantic-label tests, four Tripo pose-guide tests and five shared contact-harness tests. They cover missing independent reviews, changed actual soles, incompatible phase/direction/action, paid-license substitution, dependency closure, inline evidence handling, invalid phase timing, penetration and foot yaw. The separate Blender probe exited zero and confirmed actual saved geometry; unit tests alone are not the basis of this PASS.

The annotation is a concrete correspondence change after the two failed raster attempts: it makes actual bone-chain identity visible. It is not proof that a future ImageGen output will preserve laterality. A fresh exact request/permit and an actual independently reviewed output remain required. The failed R4/R5 artwork stays quarantined; this review approves no relabeling, equipment swap, localized repair or hard-mask claim.

Existing limits remain: the source 1.25 s Run is not reclassified as one native cycle; the 0.625 s derivative is explicit. A single stance anchor does not prove zero slip for every deforming sole vertex. No new multirate runtime, game-scale speed, other-direction or firing result is issued here. The older shared calibrator's UAL wording is historical metadata; the bound source here is explicitly Tripo+CC0. The current video has been reported as 383 frames/about 4.98 s; no eight-complete-loop visual claim is made by this review.
