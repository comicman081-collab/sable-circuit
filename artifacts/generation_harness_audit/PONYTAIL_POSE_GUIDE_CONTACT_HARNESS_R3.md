# Ponytail FULL — R12 E/Sprint pose-guide re-review

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Reviewed UTC: **2026-09-07T19:26:48Z**.
- Verdict: **PASS_STATIC_EIGHT_PHASE_POSE_GUIDES_ONLY** for the exact eight lower-body poses below. **Temporal motion, MICA appearance, runtime, firing, HTML and Luna remain unapproved.**
- This new report does not change the previous R2 HOLD or approve its old images. Only this report was written; no code, asset, model, prior report, or receipt was changed. No rendering or generation was run by this reviewer.

## What I directly checked

I read current AGENTS, the production skill and relevant motion/art-boundary instructions, the current visible-frame gate, both contact contracts, and the actual R12 refinement implementation. I opened every native 1920×1920 R12 frame and the labeled 1920×1080 sheet. The tool automatically displays square frames at 1600×1600; I additionally examined original-scale contact-foot crops, without writing new image files. Those inspection crops were display-only JPEGs, not replacement evidence assets.

I resolved the actual calibration/capture/input-result/blend/generator/contract refs, independently recalculated clearance from the stored evaluated sole vertices and fixed floor for all 49 samples, reran phase classification, and compared every captured sole array with its exact calibration sample. Maximum clearance recalculation error: **0.0 m**. Maximum capture-versus-calibration vertex difference: **0.0 m in all eight frames**. The wrap sole arrays equal the first sample's arrays.

The repository visual-evidence validator decoded all eight native frames and the labeled sheet as native-1080p containers. This is only a resolution/decode check. I reran `python -B -m unittest tests.test_pose_guide_contact_harness -v`: **5/5 PASS**; the parent's broader 14-test result is not claimed as my independent execution.

## Previous HOLDs: actual change, not a relabel

**Left contact:** measured sole clearance is now **1.999989 mm**, down from 10.876 mm in the rejected guide. The original-scale foot view no longer shows the previous obvious floating gap. The leg leads, the foot is near the unchanged ground plane, and the succeeding down pose visibly bends under load.

**Right contact/down:** contact is now actual sample **26**, not old sample 29. The new contact has a much straighter leading leg and a near-ground heel; sample 30 has an obviously flexed supporting knee and lower pelvis. The measured contact-to-down pelvis drop is **22.622049 mm**, not approximately 29 mm. Left drop is **22.733450 mm**. The stale ~29 mm comment in the refinement source is not used as evidence; its saved result and actual calibration contain the correct 22.622 mm difference. Both exceed the new 15 mm requirement.

Ground authority is unchanged: **Z = 0.0005453864578157663 m**, linked to the original neutral REST-sole calibration. The refinement changes existing diagnostic foot-IK target Z keys, not per-frame root position or the floor. The new independent calibration and actual capture, rather than desired IK positions, establish the final contact measurements. Visible MICA artwork is not edited or produced by this operation.

## Eight individual static judgments

All PASS entries mean **generic lower-body pose-guide use only**, with the phase/laterality shown. They do not approve copying the generic model's face, clothing, bare-foot appearance, mechanical arms, backpack, materials, or hand pose. They do not establish physical contact forces or continuous motion quality.

| Phase | Sample / frame | Time s | L / R sole clearance mm | Verdict | Direct observations |
|---|---:|---:|---:|---|---|
| contact_l | 2 / 0.666667 | 0.027778 | 2.000 / 238.042 | PASS | Left leads screen-right, near-flat foot meets the ground tolerance; no prior conspicuous floating gap. Knee is not visibly reversed, and the next down pose is distinct. |
| down_l | 6 / 2.000000 | 0.083333 | 1.000 / 226.928 | PASS | Left stance knee visibly flexes and pelvis lowers 22.733 mm; right recovery leg folds behind. Forefoot is near the plane, without a sideways ankle. |
| passing_l | 8 / 2.666667 | 0.111111 | 1.000 / 210.934 | PASS | Right swing leg passes the left stance leg in travel projection. Their projected overlap is a passing silhouette, not visible pretzel-like twisting. Left foot keeps its forward axis. |
| flight_l | 17 / 5.666667 | 0.236111 | 282.307 / 239.258 | PASS | Right leg leads after left support; left leg trails. Broad airborne split, two coherent leg chains, no leading knee raised above the pelvis or sideways 90° ankle. |
| contact_r | 26 / 8.666667 | 0.361111 | 365.938 / 2.595 | PASS | Right leg leads with near-ground heel and raised toes; this is visibly distinct from down_r. The plantar/dorsiflexion seen in profile is not a sideways foot-axis rotation. |
| down_r | 30 / 10.000000 | 0.416667 | 284.132 / 1.000 | PASS | Right knee visibly bends beneath the body after the straighter contact pose. Actual pelvis drop is 22.622 mm, closing the previous near-duplicate-loading HOLD. |
| passing_r | 32 / 10.666667 | 0.444444 | 224.088 / 1.000 | PASS | Left swing leg approaches/crosses the right stance leg's travel position; the stored neighboring samples bracket the crossing. Right forefoot stays near the plane, without an obvious yaw kink. |
| flight_r | 41 / 13.666667 | 0.569444 | 211.911 / 209.375 | PASS | Left leads after right support and right trails. Broad uncrossed airborne stride; no barrel-shaped calf expansion, grotesque knee lift, or 90° ankle/waist bend observed. |

Head, pelvis and feet remain generally E-facing; the forward sprint lean is coherent across the eight inspected poses. All character extremities and accessories remain inside the native frames. No obvious calf inflation or lateral 90° waist twist is present in this sample set. This generic free-arm sprint is **not** proof of an armed MICA torso/weapon pose or independent aim.

The sampled pelvis rises/falls through 0.734011–0.841886 m over the action. I have not observed a continuous playback of this revised motion, so I do **not** approve its perceived body bob, interpolation, support sliding or loop smoothness. Foot-axis maxima over the sampled cycle are left **2.270602°**, right **0.371414°**. Actual lowest sole clearances are approximately **0.999987 / 0.999927 mm**. These are numerical observations, not a completed-run quality claim.

## Current gate recheck

The current gate requires an exact `visual_promotion_contract` reference and includes it in the contact-review subject. The new contract limits selected support-sole clearance to **4 mm** and down-phase pelvis drop from its corresponding contact to at least **15 mm**. Existing exact gate/calibrator/technical-contract, report/capture/blend/phase/image/sole/floor binding and two-role review checks remain in the current request→reserve→frame→seal→verify→sequence path.

I exercised the actual data without fabricating a review bundle:

- All six R12 support phases pass the data, geometry and new numerical checks; they stop on the intentionally missing independent contact-review bundle.
- The previous R6 `contact_l` is now rejected with `VISUAL_SUPPORT_SOLE_CLEARANCE_EXCEEDED`.
- The previous R6 `down_r` is now rejected with `CONTACT_TO_DOWN_PELVIS_DROP_INSUFFICIENT`.
- Airborne phases still use their separate exact pose-review path; the helper's empty error list for flight is not permission to skip that review.

For the six exact support subjects listed below, my independent contact-review check verdicts are:

| Exact check | Verdict |
|---|---|
| exact_current_gate_and_contract | PASS |
| exact_calibration_report_and_capture | PASS |
| independent_sole_vertices_match | PASS |
| fixed_floor_contact_and_phase_semantics | PASS, static guide scope |
| feet_ankles_pelvis_visual_distinction | PASS, selected poses only |
| pose_guide_only_boundary | PASS, no appearance promotion |

No actual request, permit, frame receipt or sequence was reserved/sealed here. A production caller must assemble and verify the required exact visual and Ponytail review bundle; this Markdown is evidence, not a substitute for executing that gate. The old frozen direct-creation CLI remains outside the permitted current workflow.

## Exact content bindings

Root of the evidence below: `artifacts/quarantine/generation_diagnostics/`.

```text
seed_san_ual_astra_sprint_e_contact_refine_r12/retarget_result.json
683f5ec796919420c439a6f2ba2415e831937ba04e3e69bc135dc7cc7e0d2ba3
seed_san_ual_astra_sprint_e_contact_refine_r12/SeedSan_UAL_Sprint_Loop_CONTACT_REFINED_DIAGNOSTIC.blend
7bd7442e5275d38c3ea870f072e777a64750b1eceaaa088348c90d9e983c8ccd
seed_san_ual_astra_sprint_e_contact_refine_r12_calibration_r1/contact_calibration.json
9cab39b65b10762cdb024c81a172c7d0a99b4a4d0a52a631a362bed48a0c3207
seed_san_ual_astra_sprint_e_contact_refine_r12_guides_r1/capture.json
75aa7582b5e1f389562ba0df75568fe11e6629fa4d31d47200fd3f7b610a92c3
seed_san_ual_astra_sprint_e_contact_refine_r12_guides_r1/POSE_GUIDES_8PHASE_LABELED_1920X1080.png
54a26b96a98226b8eda99193d4c0bf191f159f003013105c0b1953f42f01a5d8
```

Native images under `seed_san_ual_astra_sprint_e_contact_refine_r12_guides_r1/frames/`:

```text
contact_l.png a67d1f6aed89a12846318e10c83df09b285d2a876fb6ae6fed148a33d509a815
down_l.png 8d4120a656753536874412c34aa9d55f132bef3d7051bf2df554464d5298fd7a
passing_l.png bf7bf340cafe4e0197a8802e51dbac30fb44fd10d22512187e17ac77210cf383
flight_l.png 800db755ff39df3ad76b89acbb31224afa111cb7d6e0a14fcfdd2b22f0e96c60
contact_r.png 96cccfadaa9545d4c95c84c391142ce35c1dc8de94345e85e4d87ffeb8320bc4
down_r.png 60d13f5acf12b9799dee4ef3222580fdc9ad939c5cc91ed773ee489c1b9d790c
passing_r.png bef028e732fcf27b6efcb7c34b915fe0b159004e7a0828887d1eaee1fbbb6cc6
flight_r.png 043b0482934126254f017faf50837761ebd197c52b54a68f89d70b0488de765e
```

Code/contract SHA-256, project-relative paths:

```text
tools/character_pipeline/visible_frame_harness_current.py
cc16c88a5c1afe4156fed9ae983ce50f91ea6725c3149ef01218b8ba983d3e6d
tools/character_pipeline/pose_guide_visual_promotion_contract.json
1845f0dc3634b536e79ec732e1d42b59e68b55f9dc5421fa016912b899de8b99
tools/character_pipeline/pose_guide_contact_contract.json
43b852f62935b960294e7f137095306aa8d41a4da0cf5018dc1c0ce3635dd10f
tools/character_pipeline/calibrate_vrm_ual_ground_contact.py
d4ddcf486c8a2856e7803cb39b3eb0f7f62ce7ade140274ab9447b0bc9547955
tools/character_pipeline/capture_calibrated_pose_guides.py
0209af8e95af5dba15ca71400d61defc6ea588f5a5a24e5fe8feb2991cf9f7f8
tools/character_pipeline/refine_vrm_ual_pose_guide_contacts.py
472401a6637de3e14f98c0576183f867b5bf08d756c0a8370d299183e29471e2
tests/test_pose_guide_contact_harness.py
8eb9cd6e4605fe69d7f907aa97814ae43d12a17e9abdccac42787edeac14695f
```

Current contact-review subjects, independently computed from the exact code/contracts/calibration/capture and selected rows, with direction `E`, motion `run`:

```text
contact_l 2c76a3ea23b42d25ea6bd85bde88982c900d3d7367af50b11052d2cea11fbf36
down_l 2864b19b0bf2ef49b1a7c631c1af8f9ef845ac1f32414403006ee4bfac997683
passing_l c51fcc868b4650ce9e6913570225393e1beea3c930729a3e0563f3e08e61eefa
contact_r 896ed82148b5ef3ee808bab60218c667e3c39ebd2862a56eff73dc897d95f0d6
down_r 3f49d3f4a6467e16b59dfd81a680b7773a9a890dd472228744e507cfb07db818
passing_r 12d5448d21945d4c8275c5c8c340c0787d32f22a92c4617768b9d3de660d5abf
```

The eight labeled poses cover the selected contact/down/passing/flight events in order, not every rendered interpolation frame. Their timestamps are nonuniform and the source cycle remains 0.666667 s. Do not play the eight cells at equal durations and inherit a cadence PASS. Two genuine cycles, horizontal world contact, movement speed, armed body posture, other directions, 8×8 move/aim fire, runtime-rate and HTML tests remain separate required work.

Signed: `/root/ponytail_motion_audit` — **static pose-guide PASS only; no final-character or runtime approval.**
