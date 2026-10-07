# Ponytail FULL — build-plan code review R1

Reviewer: `/root/ponytail_motion_audit` — independent Ponytail FULL.  
Date: 2026-09-07.  
Verdict: **HOLD_IMPLEMENTATION — close the three construction boundaries below before production execution.**

This is read-only code review, not source-art, first-pose, motion, or MICA production approval. Only this report was written. No ImageGen call, Blender/Godot run, test execution, asset mutation, or Luna task was performed. The main agent's reported 40 passing existing tests were not independently rerun here.

## Reviewed snapshot and actual callers

The findings below refer to these observed bytes, not a later concurrently edited revision:

- `tools/character_pipeline/generation_harness.py`: `1ab07b437a276ce331ee7e90f4225f8b4557e3518407dc9833116eb3bf3f37ad`.
- `tools/character_pipeline/generation_contract.json`: `da9ce074cdc1abf34ae888b29b5a895a9e3fcf5b4767c40805fcc5ee8d517d81`.
- `tools/character_pipeline/collect_generation_mesh_preflight.py`: `6d540f387cc3e93780ecfdd8795e7e127317f26985e486a40ca1fe10864b6805` — unchanged, as requested.
- Existing `run_mica_skinned_pilot.py`: `9523a207887d2ac9b5f128b2c88dc7346b9e6992f297321b65e18a9b8bb88afd`.
- Existing `build_mica_skinned_pilot.py`: `b7e06e868db792fb3e425abcbc7c0d0e0ae12a460252c411af266e024549d07c`.
- `check_build_handoff.py`: `f999ae4593afa55691d57522ccbd517d60c8140f29ebc3098f7e55b79e924444`.

I traced source authority → build-plan audit/seal/verification → attempt reservation → authorization → actual runner/direct builder → collector → first-pose approval → animation authorization → motion-build receipt closure. No existing caller at this snapshot supplies the new `build_receipt` argument, and the old handoff checker still considers only source bindings. The main agent is separately implementing the new real mesh builder; it is not assumed complete by this review.

## P1-1: omitting construction skips the new authority boundary

Locations: `generation_harness.py:548` (`construction_binding`), line 549 (`if construction_binding`), and `next_action` lines 804–814.

The collector stores the scene's contract as supplied; `validate_collected` checks actual anatomy/UV/sole data but does not require `contract.construction`. Consequently a technically valid scene with that key omitted, null, or `{}` skips every build-plan and attempt check in `audit_pose_bundle`. The job router also skips plan and receipt verification whenever `mesh_preflight` is already present. A job can omit its build receipt, or disagree with the actual pose's build receipt, and proceed to first-pose review through this branch.

Structural counterexample: keep a valid source, actual mesh preflight and native first pose, but leave `contract.construction` and the pose bundle's construction reference absent. Add that preflight to a job with no `build_plan`/`build_receipt`. Neither conditional reaches the new build-plan review requirements. Later `verify_receipt(first_pose)` and `motion_build_bindings` reuse this same audit and therefore do not restore the omitted authority.

Minimal correction: require a nonempty, fully validated construction binding for production first-pose evidence. If old synthetic tests need an exception, recognize only explicit content-bound, project-isolated fixture provenance; do not infer an exception from a missing construction field. Validate the job's selected plan/receipt against actual construction on every post-source route, including when a mesh or pose already exists. If a legacy production path is retained, it needs a distinct positive proof of the exact source-bound builder, not an absence-based fallback.

Required negative regression: missing/null/empty construction, missing job plan with a present mesh, stale job build receipt after mesh creation, and a valid pose made under plan A presented by a job selecting plan B. Each must fail before animation authorization, not merely before final promotion.

## P1-2: actual construction input/output scope is not fully bound

Locations: `generation_harness.py:543`–546 (charts against all source regions), lines 552–558 (construction comparisons), and `authorize_build` lines 497–502.

The launch API compares its supplied `out` and `images` with the plan, but the independent first-pose gate does not verify the actual collected files against those same limits:

- A plan approved for output directory A can be paired with a construction record, `.blend`, collector preflight and native pose stored in B. Matching `construction.blend` to `collected.blend` is not proof that either is under A. There is no path-containment check for the blend, mesh preflight, native image, render receipt, or construction record against `plan.output_root`.
- If a source set contains approved S and E images but the plan lists only S in `source_images`, a collected chart using E still passes the existing chart check because that check uses the whole source authority, not the narrower plan. The collector already reports actual material images; these can be compared directly with the approved plan.

These are structural counterexamples identified by inspection; I did not fabricate or render replacement evidence to exercise them.

Minimal correction: after resolving the exact approved plan, require every construction/first-pose product to resolve beneath its approved output root. Compare every actual collected chart/material source image with the exact approved `source_images`; retain the existing finer region/purpose/allowed-part check. Compare actual direction with the plan both before first render and in the independently collected evidence. Reuse project path/hash helpers rather than adding a second path-validation layer. Logs/cache locations may be separate project-local paths only if explicitly covered by the reviewed runner's bounded execution scope.

Required negative regression: an otherwise valid pose bundle relocated outside the approved output root with internally consistent new references; an approved-but-not-selected texture from a composed source set; and a non-approved probe direction. Reject these even when the general source review is valid.

## P1-3: one-attempt authorization is not yet an execution boundary

Locations: `generation_harness.py:469`–484, `authorize_build` lines 495–503, existing runner line 21/direct builder line 569, and current `check_build_handoff.py:21`–26.

`reserve_build_attempt` publishes a unique reservation tied to the receipt and a fresh output root. This is useful, but `authorize_build(build_receipt=...)` accepts the plan without receiving/verifying an attempt. `verify_build_attempt` checks a deterministic record and path; it does not consume a one-time execution claim. The same valid reservation can be presented again. Output-exists checks in individual builders help, but moving a failed candidate to quarantine must not implicitly reauthorize the same consumed plan/attempt.

The actual existing runner/direct-builder CLIs do not carry `build_receipt`, `build_attempt`, or the plan's direction/limits. The old handoff checker rejects a new builder before considering any valid new build receipt. Therefore the newly added helper functions alone do not yet constitute a usable production path. This does not mean the old diagnostic builder should be extended or promoted; the new production entrypoints can own this small integration.

Minimal correction: make the reviewed runner validate the plan and reserve an attempt; make the direct builder verify that exact attempt and atomically claim execution before changing its candidate directory or rendering. A second builder invocation with the same claim must fail, including after quarantine relocation. The runner should verify/pass the plan's actual direction, thread/time/render budget, source images and input files; the builder should revalidate its own entrypoint and supplied values. Update the handoff check to understand the approved plan, or remove it from the required production route once an equivalent mandatory integrated check exists. Do not advertise a reservation as completed execution.

Required negative regression: direct build with a plan but no attempt, mismatched attempt/receipt/output/direction, duplicate/concurrent execution claims, replay after candidate quarantine, and a changed builder or dependency after plan approval. Add one bounded normal caller-path test proving a valid plan reaches construction without changing any ImageGen request or permit.

## What is already correct and should be retained

- A separate build-plan stage is the right minimal boundary. It binds source identity, selected source images, exact builder/runner/helpers, input assets/licenses, written scope and bounded limits without pretending they were part of the original ImageGen request.
- `seal_build_plan` recomputes the plan audit and requires all implementation and Ponytail FULL checks. `verify_build_plan` reseals from the bound review bundle and compares the entire receipt, preventing a hand-edited hash table or changed plan from inheriting approval.
- The collector remains unchanged. Actual topology, volume, weights, UV interiors, body frame and visible sole checks are not weakened by the new stage.
- Where construction is present, its plan bindings and both review replies enter the first-pose subject. Existing `verify_receipt`, `authorize_animation`, `motion_build_bindings`, and `motion_harness.validate_geometry_generation` then preserve that closure. Fixing mandatory entry and actual scope in the shared pose audit is preferable to adding separate downstream wrappers.
- Read-only input files are rehashed by plan verification. The post-build `readonly_inputs_after` comparison should remain supplemental evidence, not replace actual file hashing.
- A nonempty license document is only a technical prerequisite, not a commercial license verdict. The specific model/rig and planned modification/distribution rights still need the explicit `licensed_readonly_inputs` review; no production model use is approved here.

## Source review revision and final decision

`source_bindings` includes the harness and generation contract in `CODE`. Their changed hashes intentionally make the previous source approval stale under the new implementation. A fresh source audit/review revision of the **same unchanged image, masks, original request and original attempt permit** is therefore appropriate. It is not another ImageGen attempt. Preserve the R3 evidence as history; do not rewrite its reviewer result or issue a fake replacement permit.

This report approves neither that new source revision nor any build plan's particular MICA adapter. It concludes that the separate-plan design is sound, but this code snapshot remains **HOLD_IMPLEMENTATION** until mandatory construction, actual input/output scope, and one-time real caller execution are closed and regression-tested. Source art, first-pose appearance, gait, full runtime/HTML and Astra-before-Luna milestones remain separate gates.

Applied skills/semantics: `sable-motion-production` and Ponytail FULL. The shared harness is the correct owning implementation; no additional service, framework, alternate collector, new image generation, or modification of old source authority is needed to address these findings.
