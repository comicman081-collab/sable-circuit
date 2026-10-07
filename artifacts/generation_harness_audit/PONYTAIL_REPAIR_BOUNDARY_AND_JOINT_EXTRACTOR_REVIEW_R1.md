# Ponytail FULL — repair execution boundary and projected-joint review R1

- Reviewer: `/root/ponytail_motion_audit` (independent Ponytail FULL).
- Evidence inspected: 2026-09-07T20:39:13Z; report authored 2026-09-08 KST.
- Verdict: **FAIL_IMPLEMENTATION_NOT_CLOSED**. The current joint artifact is **HOLD_NOT_CAPTURE_ALIGNED**.
- Scope: read-only implementation/provenance review, one stdout-only Python counterexample diagnostic, and the existing 10-test file. No image generation, Blender/render execution, production mutation, promotion, or disposal occurred. Only this report was written.
- Applied: project AGENTS, `sable-motion-production`, its art/motion-boundary reference, and the mandatory generation/motion documents. Source-art authority remains ImageGen; Blender/UAL geometry is pose guidance only.

## Requested checks

| Check | Verdict | Direct evidence |
| --- | --- | --- |
| Reference-only editing is actually blocked | FAIL | The official current `reserve` route does not invoke the new boundary validator. |
| Boundary JSON cannot substitute for capability proof | FAIL | Missing `reviews` plus two true booleans and the PASS string was accepted by the actual validator in an in-memory counterexample. |
| Binary mask/native size/target/generator closure | FAIL | Target subject, generator string and dimensions are checked, but only the decoded red channel is tested; all-white and nonbinary other-channel masks were accepted. Boundary/mask contents are absent from downstream exact-ref closure. |
| Exact geometry/capture provenance | FAIL | Existing file hashes and phase rows agree, but actual joint pixels use a different orthographic scale from the attached guide images. Capture rows and evaluated scene state are not verified by the extractor. |
| Blender appearance remains outside visible art | PASS_BOUNDARY_ONLY | Extractor writes numerical JSON and image references, not rendered pixels, an atlas, a profile or a runtime pointer. Its status/limitations explicitly deny production authority. |
| Regressions exercise the claimed boundary | FAIL_COVERAGE | Existing 10 tests passed; the new test merely searches strings. It does not call the validator, official reservation path, or joint extractor. |

## P1 — official reservation bypasses the new boundary

`visible_frame_harness_current.py:174–178` patches only `_audit_pose_guide` and dispatches `reserve` directly to `frozen.reserve`. The latter calls `audit_request` at `visible_frame_harness.py:330–347`. That repair audit validates old scope reviews but never reads `repair_execution_boundary` or `repair_change_mask`.

Consequently, a new otherwise-valid `repair_failed_frame` request can omit both fields and still reach permit creation through the prescribed current CLI. This is a real caller omission, not a prohibited direct call to the frozen CLI. Request/frame/sequence recursion also does not gain the new check. The exact-ref list at `visible_frame_harness.py:304–315` omits the execution contract, boundary and mask content. Even a finalizer-created request binds only their strings indirectly through its own JSON; a changed external boundary/mask file is not re-resolved downstream.

Minimum closure: enforce the check in the shared current request audit used by reserve and downstream verification, before any permit write. Preserve historical receipt verification deliberately, without leaving new reservations on the historical path. For the presently unsupported built-in hard-mask interface, reject new local-repair reservations outright; no speculative capability infrastructure is needed to express that HOLD.

## P1 — declarations are accepted as proof; reviews can be synthesized

`finalize_reviewed_visible_frame_repair_request.py:24–59` verifies exact contract ref, equal generator string, exact target-scope subject, two boolean declarations and a verdict. It does not inspect the contract's required review roles, a reviewer bundle, executable implementation, actual mask-consuming call, immutable-output evidence, or single-use execution capability.

I called the actual function with stdout-only in-memory filesystem/dependency substitutes, leaving its validation logic intact. These three inputs all returned successfully:

1. Native-size binary mask, **no `reviews` field**.
2. Native-size entirely white mask, **no protected pixels** and no reviews.
3. Binary red channel but G=127, B=33, A=71 throughout, **not a genuine opaque binary mask**, and no reviews.

All three declared `generator=built_in_ImageGen`, both booleans true, and the prescribed PASS string. No counterfeit evidence or request was saved. This demonstrates that the currently unproven tool can be represented as capable by boundary JSON alone.

The finalizer also manufactures two all-PASS review objects at lines 62–95. It accepts any evidence text containing `PASS_REPAIR_TARGET_SCOPE_ONLY`, stamps the current subject/date, and attributes one review to this reviewer. It never checks the evidence's actual subject or seven/six-check outcome. A different subject's old PASS, or a HOLD report quoting that token, is sufficient. `generation_harness.verify_reviews` checks the synthesized fields and merely nonempty referenced evidence; it does not repair this misattribution.

Minimum closure: consume exact independently authored structured reviews rather than create PASS values from substring presence. Bind the real execution implementation/tool capability, target, prompt/scope and mask to the reviewed subject. Require a truly binary mask with both editable and protected regions, unambiguous channel/alpha interpretation, and its independently reviewed spatial scope. Do not admit built-in reference-only editing until hard-mask execution is actually supported and demonstrated.

## P1 — actual joint coordinates do not align with their guide images

The actual artifact SHA is `64669f3e202955ad807840ce112e44db703eff04ea50d98d6a2266f3896c7122`. All four top-level blend/calibration/capture/extractor refs resolve to their stated bytes. All eight phase/sample/frame/image refs match the capture and the calibration's phase candidates. Capture sole arrays also equal their corresponding calibration arrays. Those are real positive provenance observations, not visual approval.

However, `capture_calibrated_pose_guides.py:52` widens the camera with `ortho_scale *= 1.28`, recording `locked_capture_ortho_scale=2.673755407333374`. The extractor uses the unmodified loaded blend camera at lines 70 and 86–95, without applying or checking that capture scale. Its JSON therefore attaches guide images made with a different projection.

Independent numerical check: invert the capture's locked camera world matrix, project the calibration's actual `pelvis_world_m` using its recorded orthographic scale and 1920-square dimensions, and compare to the extracted pelvis coordinates:

| Phase | Capture-coordinate pelvis (px) | Extracted pelvis (px) |
| --- | --- | --- |
| contact_l | (1023.691156, 964.951765) | (1041.524620, 966.338196) |
| down_l | (1024.209394, 981.761487) | (1042.188034, 987.854633) |
| flight_l | (1020.691384, 908.018523) | (1037.685013, 893.463593) |
| flight_r | (1020.998066, 906.093887) | (1038.077545, 891.000137) |

Across **all eight** rows, the coordinate distance from image center (960,960) is approximately **1.28 times** the capture-coordinate distance. This independently matches the omitted camera-scale change; it is not evidence that anatomy or the approved guide capture itself failed. The current extracted JSON must not be consumed as pixel-aligned guide geometry.

Additional causal closure missing in the same path:

- Lines 65–69 compare only calibration status/errors and a disk blend SHA. The file is not reloaded, so altered in-memory armature/action/camera state can be sampled while the unchanged disk hash is reported.
- Lines 80–108 trust capture phase/sample/frame/image fields. A different capture with canonical labels, duplicated frames, a substituted guide image, or a different calibration link is not rejected. Current actual rows match, but the extractor does not enforce that match.
- `point` includes resolution percentage, while `native_projection_size` at line 120 excludes it. Non-100% scenes would report a false coordinate canvas.

Minimum repair: resolve and cross-check the exact capture/calibration/blend/generator chain and phase rows, reload the approved blend, reproduce the exact recorded capture camera matrix/intrinsics and actual output dimensions, lock them for every sampled frame, and record them with finite world/projection values. Compare projected known pelvis points against capture-space geometry in a regression. Reuse existing exact-ref and camera-lock helpers rather than inventing another approval format. Toe/ankle bone endpoints remain joints, not independently evaluated visible sole contact.

## Regression assessment and permitted conclusion

Executed `python -B tests/test_visible_frame_harness.py`: **10/10 PASS**. The new test at lines 79–87 checks code text and contract labels only; it passes with all the defects above. Add behavioral negatives for missing/forged boundary reviews, official reserve without a boundary, changed boundary/mask after reservation, all-white/nonbinary masks, and stale/quoted reviewer evidence. Add exact-camera, substituted-capture and in-memory-scene negatives for extraction; no repeated full render is necessary for the first coordinate regression.

The geometry-only output does not itself violate the no-Blender-visible-art rule. That narrow PASS cannot override its projection error, cannot register a motion adapter, and cannot approve a gait, contact, MICA frame, weapon, runtime, HTML or Luna reproduction. No visible-art or motion production authorization is issued here.

## Exact inspected files

| Path | SHA-256 |
| --- | --- |
| `tools/character_pipeline/finalize_reviewed_visible_frame_repair_request.py` | `f41c6ccc62f5a25482f0e78ed73ee0aa28ba515bf9ab0aec41b5bf222d31bd02` |
| `tools/character_pipeline/imagegen_repair_execution_contract.json` | `887cc8551354d7ceadafcebff09491e2b422b2576e9dfe8a39425a0a02fbf8a5` |
| `tools/character_pipeline/extract_vrm_ual_projected_joints.py` | `fee38e2740cfb2d474da9e474409039d1916b0738843574709fe6d76624133cb` |
| `tools/character_pipeline/visible_frame_harness.py` | `a24dbf646b4906645912639cc99397240e454c2d8fe7ec0d07b41149f118658a` |
| `tools/character_pipeline/visible_frame_harness_current.py` | `cc16c88a5c1afe4156fed9ae983ce50f91ea6725c3149ef01218b8ba983d3e6d` |
| `tools/character_pipeline/capture_calibrated_pose_guides.py` | `0209af8e95af5dba15ca71400d61defc6ea588f5a5a24e5fe8feb2991cf9f7f8` |
| `tests/test_visible_frame_harness.py` | `b3a7384e8f64066c858e406d8ac1fb6aa2622b714e0e1ca8a9c41f3bdcb532c3` |
| `.agents/skills/sable-motion-production/SKILL.md` | `4be29e0c7df80df9d61dc4d3103367a65743039dde56fb0c19678e3d1d3e7563` |
| `AGENTS.md` | `d9bfc98fd6b4bfd337da1c1ff2fd1d04211d3002a4b1bfac316ddba75b154810` |
| `docs/production/GENERATION_GATES_2026-09-07.md` | `846e3ea7c9de91ae1e00e807e88d1910b651d7378b69c3a94347309e1e951390` |
| `artifacts/generation_harness_audit/source_preserving_adapter_astra_r1/R12_E_RUN_PROJECTED_JOINTS.json` | `64669f3e202955ad807840ce112e44db703eff04ea50d98d6a2266f3896c7122` |

The output's exact underlying blend/calibration/capture hashes verified in this review are respectively `7bd7442e5275d38c3ea870f072e777a64750b1eceaaa088348c90d9e983c8ccd`, `9cab39b65b10762cdb024c81a172c7d0a99b4a4d0a52a631a362bed48a0c3207`, and `75aa7582b5e1f389562ba0df75568fe11e6629fa4d31d47200fd3f7b610a92c3`.
