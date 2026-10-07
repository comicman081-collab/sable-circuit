# Ponytail FULL — fixed-floor pose-guide contact harness R1

Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
Review UTC: **2026-09-07T18:36:58Z**.
Instructions applied: current `AGENTS.md`, `sable-motion-production`, generation/motion documentation and rig/art-boundary references.

**Implementation verdict: HOLD — two P1 gaps remain. Actual R6 diagnostic verdict: HOLD is correct and independently reproduced.** No character, motion, source-art, runtime or HTML completion is approved.

## P1 findings

### 1. Calibration HOLD is not wired into the actual ImageGen request gate

`visible_frame_harness.py:78–136` verifies the guide capture, source provenance, phase text and independent reviews, but does not require or examine a contact-calibration report. Its `pose_guide_subject` at lines 39–55 does not bind calibration/contract/code, and request bindings at lines 293–306 omit them. `reserve()` at lines 330–333 therefore has no executable condition that rejects a contact/down/passing request because its calibration is absent, stale or HOLD. The new instructions are correct, but are currently stronger than the consuming code.

Concrete route: an otherwise valid independently reviewed contact/down/passing guide can reach `audit_request`/`reserve` without any calibration field. Adding a HOLD calibration field cannot affect this decision because no caller reads it. This is not a claim that independent reviews themselves can be skipped; it is the missing new prerequisite before those requests proceed.

Minimum repair: require the exact fresh calibration for the affected support phases; bind its report, exact retarget/blend, contract and generator into guide/request subjects; reject HOLD/errors, wrong direction/action/frame, stale bindings and a phase sample not matching the requested capture. Add caller-level negative tests for absent/HOLD/stale/wrong-sample calibration. Do not silently reinterpret older approved airborne guides as support-phase approval.

### 2. Eight unique labels do not establish an ordered contact/down/passing cycle

`calibrate_vrm_ual_ground_contact.py:105–109` selects contact by minimum clearance, down by minimum pelvis height among later-numbered support candidates, and passing by smallest absolute travel difference within the same leading-foot candidate set. It does not detect descending contact-band entry, a continuous support interval, swing-leg passage across the support leg, or cyclic contact→down→passing→toe-off→flight order. Flights at lines 116–128 need only bilateral clearance and leading sign, not occurrence after the appropriate support/toe-off.

I reproduced a false technical PASS by calling the actual `_classify` function, without Blender or file modification. Reorder the existing valid fixture rows as `[0,3,2,1,4,7,6,5]`, renumber samples 0–7 and append an exact wrap. The function returns:

```text
contact_l=0, down_l=3, passing_l=2, flight_l=1
contact_r=4, down_r=7, passing_r=6, flight_r=5
errors=[]
```

Thus flight can occur before passing/down and still satisfy all eight unique labels. The fixture and its current two tests do not cover this defect.

Minimum repair: classify temporally connected support episodes against the fixed floor, detect descending contact entry and ordered loading/passage/toe-off events with circular wrap handling, and require each corresponding flight after toe-off. Keep HOLD when a distinct event cannot be resolved; do not substitute the minimum frame or another phase. Add the above permutation and missing/incorrect crossing/order regressions.

## Requested mechanism checks

| Area | Finding |
| --- | --- |
| Fixed neutral REST floor | **PASS for the inspected exact R6 provenance, limited to measurement mechanism.** The calibrator loads the hash-verified saved blend, sets the bound target rig to REST, and samples depsgraph-evaluated mesh vertices in world coordinates once at lines 182–190. The selected foot IDs originate from the original imported mesh's >0.5 foot-group weights and lowest 12mm band in `probe_vrm_ual_retarget.py:110–117`, before retarget keyframes. The calibrator then holds one floor for the entire cycle. |
| No motion-derived floor or per-frame root correction | **PASS for this implementation.** Calibration never reads the older retarget report's `global_ground_z_m`. Its loop at lines 209–235 only changes the evaluated frame and collects soles/joint positions. It does not move the root, invoke IK, write target transforms, rebuild a mesh or manufacture a contact flag. The input blend already contains UAL animation; “before evaluation” means before this calibration's posed sampling, not that the saved file has never previously evaluated an action. |
| Penetration, sideways yaw, duplicate labels, missing bilateral flight | **Partially implemented, not an all-phase PASS.** The fixed contract checks penetration beyond 5mm and sideways undirected foot-axis yaw beyond 35 degrees, rejects reused samples and missing left/right flight windows. R6 triggers the first three. A separate missing-flight fixture correctly returns `DISTINCT_BILATERAL_FLIGHT_WINDOW_REQUIRED_FLIGHT_R`. Temporal support transitions remain the P1 gap above. |
| Visible-art boundary | **PASS for the new helper's output responsibility only.** The helper has no render, image-generation, atlas, HTML or runtime-pointer operation. Its normal runner restricts fresh outputs to project quarantine, routes cache/TEMP there, starts one bounded 2-thread/180-second child and writes JSON/log/completion only. The report explicitly remains `production_ready=false` and pose-geometry-only. AGENTS/skill prohibit copying VRM appearance and reserve all visible original/repair art for ImageGen. This is not a proof that arbitrary external copying or every other producer is impossible. |
| R6 actual status | **HOLD confirmed.** The measured floor/clearance and all seven reported errors reproduce exactly; the existing result must not admit the support-pose candidates to an ImageGen request. |

The floor mechanism is not yet a general guarantee for arbitrary retarget scenes: REST suppresses target pose deformation, not arbitrary object animation, other modifiers or a changed world-unit basis. These are not shown to affect this exact R6 input, but do not describe this one diagnostic as universal neutral-scene validation. The yaw metric uses an undirected axis (lines 56–58), so its PASS would not independently prove anatomical toes-forward rather than backward. No new Blender run was performed by this reviewer.

## Actual R6 evidence independently recomputed

Report: `artifacts/quarantine/generation_diagnostics/seed_san_ual_astra_sprint_e_r2_contact_calibration_r6/contact_calibration.json`.

- 49 samples including wrap; 54 actual selected sole vertices per side.
- Neutral REST floor: **0.0005453864578157663m**, recomputed from the stored actual neutral vertices; neutral side difference **4.598405212163925e-9m**.
- Recomputing every clearance from each sample's actual world-space vertices and that fixed floor gives maximum discrepancy **0.0m**.
- Left minimum clearance **−0.03270212956704199m** at sample 8; right **−0.020088553661480546m** at sample 34. Both violate the −0.005m limit.
- Maximum foot-axis yaw: left **59.657586°**, right **82.239796°**; both exceed 35°.
- Candidate collisions: left contact/down/passing all sample **7**; right contact/down both **31**, passing **32**. Flights at **17** and **41** do not cure those failures.
- Re-executing the actual classifier on the stored rows reproduces all seven errors exactly: both penetration errors, both yaw errors, both distinct-support-phase errors and reused-phase-sample error.
- `completion.json` reports HOLD and an exited owned child; the stored Blender log ends with `Blender quit`. This reviewer did not launch or monitor that child.

## Verification and exact hashes

I ran the existing **2 unit tests: PASS**. I additionally ran the read-only phase-order counterexample above (**false PASS reproduced**) and a missing-flight counterexample (**correctly rejected**). These synthetic rows test classification logic, not real human motion. No renders, generation, runtime tests or code/asset edits occurred.

All four refs embedded in R6 (`input_result`, `input_blend`, `contract`, `generator`) matched their current bytes at review time.

| Artifact | SHA-256 |
| --- | --- |
| R6 contact_calibration.json | `b73523a98a96ff99e092bcd0ef2c604f361901d612a1cc896e12d36a0aa56caa` |
| calibrate_vrm_ual_ground_contact.py | `8ce2126df299df43accbefe2100083d36a4f42711b6a9474b74257427c5a9dc7` |
| pose_guide_contact_contract.json | `43b852f62935b960294e7f137095306aa8d41a4da0cf5018dc1c0ce3635dd10f` |
| tests/test_pose_guide_contact_harness.py | `969fdc91f30d4fa66d0a84e2d68ea49bc4977ae65c74aeed3ea31dfea064e043` |
| Consuming visible_frame_harness.py | `a24dbf646b4906645912639cc99397240e454c2d8fe7ec0d07b41149f118658a` |
| Input retarget_result.json | `0c4157663e34052e9699f38830b8147bb62e32d5b75c564264ba6a47d6b8d6a3` |
| Input retarget blend | `4e56ff8c5a4127753ac4de2ebd9aa1d9d3751da9684e1b2007ea7ac8d5db101c` |
| sable-motion-production/SKILL.md | `d0248a6a87f0f55eacf0217e66a03aa66813c6645f403c66aeb420984f1914a1` |
| AGENTS.md | `7070737634e20ceda671d06553751a731cf6ce45c31a1b4b0ccbb1f2ff62b667` |

Only this report was created. These conclusions are bound to the above code/evidence bytes and require fresh review after repair. Neither technical checks nor existing static MICA flight-frame approval establish natural whole-cycle gait, ground contact, runtime motion/firing, 8 directions, HTML or Luna readiness.
