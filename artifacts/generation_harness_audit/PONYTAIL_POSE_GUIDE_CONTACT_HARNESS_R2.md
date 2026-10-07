# Ponytail FULL — pose-guide contact harness R2

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review timestamp: 2026-09-07T19:14:04Z (2026-09-08 KST).
- Overall verdict: **HOLD — the complete eight-phase guide set is not visually approved.**
- Scope: current request/guide gating, fixed-floor calibration, generic Blender+UAL motion repair, and the eight actual E/Sprint pose captures. This is not MICA art, animation, runtime, firing, HTML, or Luna approval.
- Previous `PONYTAIL_POSE_GUIDE_CONTACT_HARNESS_R1.md` remains unchanged. No production code, source art, candidate, or receipt was edited by this reviewer. No Blender, ImageGen, game, or render process was launched.

## Evidence actually inspected

I read the owning calibrator, repairer, capture writer, current gate, frozen downstream consumer, contact contract, relevant tests, AGENTS, and `sable-motion-production` instructions. I opened all eight individual native 1920×1920 images in both capture revisions, and the 1920×1080 overview. The image tool displayed the square images at 1600×1600 after its automatic resize; the files themselves are native 1920×1920. The overview is an index, not original-scale anatomy evidence.

I independently compared the R2 capture's evaluated sole arrays with the matching calibration rows: maximum coordinate difference is **0.0 m for every one of the eight phases**. R1→R2 pixels differ by 0–12 pixels per image, with no pose change observed. R2 is the final capture subject of this report. Its `capture_generator` reference now satisfies the existing consumer schema.

Directly rerun here: `python -B -m unittest tests.test_pose_guide_contact_harness -v`: **5/5 PASS**. I did not independently rerun the parent's combined 14-test suite. The repository visual-evidence validator's inspection path decoded the overview and all eight R2 frames successfully with native-1080p containers. Container success does not imply visual quality.

## Implementation findings

| Check | Verdict within this review | Direct basis |
|---|---|---|
| Fixed floor is independent of animated targets | PASS, limited | `calibrate_vrm_ual_ground_contact.py:239–256` samples evaluated soles in REST and preserves the pre-repair REST floor through `motion_repair.input_calibration`. Current floor is 0.0005453864578157663 m, not the corrected action minimum. |
| No per-frame root correction used as contact evidence | PASS, limited | `repair_vrm_ual_pose_guide_motion.py:71–78` applies one constant 0.034702129567 m armature-object lift. The code does use the previous action's worst penetration to choose that one offset; it does **not** redefine the floor from it. Actual leg IK targets at 123–138 alter the pose, but the later calibrator and capture sample the evaluated mesh, not those targets, as evidence. Original animated pelvis motion remains. |
| Descending contact, real passing, complete cyclic phase order | PASS_TECHNICAL_CANDIDATES_ONLY | Calibrator 94–188 requires descending entry into the contact band, contiguous support through a travel-order crossing, distinct down/passing frames, both flight sides, and the cyclic contact→down→passing→flight order. Reclassifying the actual 49 rows reproduced all eight distinct candidates with no errors. Scrambled-order and penetration/yaw counterexamples fail. |
| Exact current code/contract/calibration/capture closure | PASS for the current entrypoint | `visible_frame_harness_current.py:65–98` now requires the exact current gate, contract, and calibrator refs, rejects a different valid-JSON generator/contract, matches input result/blend/calibration, and reruns the classifier. Lines 103–131 bind the selected row, image, actual sole arrays, fixed floor, and two-role contact review to an exact subject. |
| Actual current capture schema | PASS after the last code correction | Capture R2 contains `capture_generator`. The initially incorrect row-level floor lookup was corrected to the actual top-level `capture.fixed_floor_world_z_m` at current gate line 120. A read-only invocation with the actual R2 data now reports only the intentionally absent contact-review bundle as invalid, not a geometry/schema mismatch. |
| No generic VRM pixels promoted to MICA | PASS as a scoped boundary, not an art approval | Repair/capture outputs are quarantine diagnostics; their roles remain `pose_geometry_guide_only`, `built_in_ImageGen_only`, `production_ready: false`. They contain no MICA atlas/runtime/HTML export. The generic character, bare feet, robot arms, backpack, plug, costume, and free-hand pose are not MICA appearance or weapon authority. |

The two P1 mechanisms reported earlier are closed **in the reviewed current CLI path**. `main()` patches the frozen pose-guide audit before request, reserve, frame, seal, receipt verification, and sequence operations; those downstream functions resolve that audit dynamically. This is not a claim that arbitrary direct imports or the historical raw CLI are globally impossible. The older module still physically has legacy command functions; AGENTS/skill require every new operation to use the current entrypoint. Do not treat this report as authorization to call the older creation/sealing path.

No actual new support-phase request was reserved or sealed during this review. Missing independent contact review remains a hard block. A unit test whose name mentions reserve exercises the helper, not a full successful production reservation.

## Actual geometry and static phase review

The repaired calibration's minimum clearances over its 49 samples are left **0.995319 mm**, right **1.171037 mm**; maximum measured horizontal foot-axis yaw is **2.270602° / 0.371414°**. These close the prior penetration/sideways-axis diagnostic at those samples. They do not establish horizontal planted-foot locking: the repair explicitly records `horizontal_support_lock: false`.

All phase verdicts below are **lower-body static guide judgments only**. A PASS here is not an ImageGen permit or a completed cycle approval. Generic body accessories and free hands must not be copied into MICA.

| Phase | Sample / Blender frame | Time (s) | L / R sole clearance (mm) | Verdict | Direct visual and measured reason |
|---|---:|---:|---:|---|---|
| contact_l | 2 / 0.666667 | 0.027778 | 10.876 / 238.042 | **HOLD** | Left leg leads and is descending, but the supporting-looking foot is visibly above the plane. Entering an 18 mm proximity band is not visible foot contact. Do not use this as an approved contact pose. |
| down_l | 6 / 2.000000 | 0.083333 | 1.328 / 226.928 | PASS, static lower-body candidate | Left knee visibly loads, right leg folds behind, and the left forefoot is near the fixed plane. Pelvis falls 22.733 mm from the selected left contact. It is visibly distinct from that earlier pose. |
| passing_l | 8 / 2.666667 | 0.111111 | 0.995 / 210.934 | PASS, static lower-body candidate | Swing leg passes beside the stance leg; travel-order sign crosses near this frame. Screen overlap does not itself demonstrate a world-space leg collision. No sideways 90° ankle or barrel-shaped calf was observed. |
| flight_l | 17 / 5.666667 | 0.236111 | 282.307 / 239.258 | PASS, static lower-body candidate | Anatomical right leg leads screen-right after left support; left leg trails. Both feet are airborne, stride is broad, knees bend coherently, and the leading knee is not raised above the pelvis. |
| contact_r | 29 / 9.666667 | 0.402778 | 311.808 / 3.247 | PASS, near-contact static candidate only | Right leg leads and its forefoot is near the plane. The pose is already flexed; this does not establish a distinct impact→loading transition or exact zero-clearance physical contact. |
| down_r | 30 / 10.000000 | 0.416667 | 284.132 / 2.477 | **HOLD** | The pelvis is only 1.249 mm below the selected contact_r, and the visible stance/load change is very small. Distinct sample IDs do not prove a perceptibly distinct down phase. Do not approve this pair as a satisfactory loading transition. |
| passing_r | 32 / 10.666667 | 0.444444 | 224.088 / 1.546 | PASS, static lower-body candidate | Left swing leg reaches the right stance leg's travel position; the crossing is bracketed by the stored samples. Near-plane right forefoot and forward-facing foot axis are coherent. No visible 90° waist or ankle kink. |
| flight_r | 41 / 13.666667 | 0.569444 | 211.911 / 209.375 | PASS, static lower-body candidate | Anatomical left leg leads screen-right, right leg trails; a broad uncrossed airborne split is visible. No high-knee marching pose or sideways ankle axis was observed. |

The head, shoulders, pelvis and legs face generally E with a consistent forward sprint lean, rather than a lateral 90° waist fold. Head, hands, feet and the generic model's accessories stay within all eight native frames. These observations do not validate rifle posture or independent aim: this model has no MICA carbine and visibly has extra mechanical arms.

The overview's title says `COMPLETE CAPTURED CYCLE`, but there are only **eight selected visual samples**, not a visually reviewed continuous 49-sample cycle. Their times are nonuniform. Replaying these eight poses at equal durations would change the captured phase timing. The original 0–16 frame Sprint cycle at 24 fps is approximately 0.666667 s; the next stage must preserve or explicitly validate cadence rather than infer it from the contact sheet.

## Required disposition

- Keep the full eight-phase guide set on HOLD. In particular, `contact_l` and `down_r` do not receive visual PASS from the technical report.
- The scoped static PASS candidates above may be submitted to an exact per-frame guide review; they are not blanket permission to reserve new art, reuse the failed contact/down poses, or seal a sequence.
- Keep the original REST floor and evaluated-vertex evidence. Do not cure the remaining HOLD by changing labels, enlarging tolerances, shifting the ground, or declaring two nearly equal poses distinct solely because their frame IDs differ.
- No claim is made about continuous interpolation, horizontal contact slip, real world travel, other seven directions, walking, movement×aim firing, muzzle alignment, 30/60/120Hz runtime, HTML parity, MICA completion, or Luna readiness.

## Exact evidence bindings (SHA-256)

Project-relative code paths:

```text
tools/character_pipeline/visible_frame_harness_current.py
7f1590d6834338074b31b399a18f4601f3b399d166de6b94cc01f63de2655b59
tools/character_pipeline/calibrate_vrm_ual_ground_contact.py
d4ddcf486c8a2856e7803cb39b3eb0f7f62ce7ade140274ab9447b0bc9547955
tools/character_pipeline/repair_vrm_ual_pose_guide_motion.py
c7c9175b28e3de534e278da98b19d0d14c9b3290abdb2d07d1d181dba87c9433
tools/character_pipeline/capture_calibrated_pose_guides.py
0209af8e95af5dba15ca71400d61defc6ea588f5a5a24e5fe8feb2991cf9f7f8
tools/character_pipeline/pose_guide_contact_contract.json
43b852f62935b960294e7f137095306aa8d41a4da0cf5018dc1c0ce3635dd10f
tests/test_pose_guide_contact_harness.py
81a3a35cd5f54f231b471b419f0c6c5e60485d5016d27eebd017773b1e0649b1
AGENTS.md
3a5fed5da248ef08afd2acee5060764b3523c326e5643f40f1693442885bac34
.agents/skills/sable-motion-production/SKILL.md
47ee4e6c7e7d57a7b05959c5a555063fb91f020d0a87158fc7e1e52a94351f6c
```

All following evidence paths are beneath `artifacts/quarantine/generation_diagnostics/`:

```text
seed_san_ual_astra_sprint_e_contact_repair_r6/retarget_result.json
da5b258287f17e22b4f5c065056a78f70bae46a26a549e55f143f3eb38214276
seed_san_ual_astra_sprint_e_contact_repair_r6/SeedSan_UAL_Sprint_Loop_CONTACT_REPAIRED_DIAGNOSTIC.blend
e2af2119f7b081ff692773c2fe10b8a2215df51c0bea8dc9ff6b6da29199677c
seed_san_ual_astra_sprint_e_r2_contact_calibration_r7/contact_calibration.json
b2fd63d1318f0fac68dbaca9fd3c3af4e898ebc4e38e364157a33cb63eabc133
seed_san_ual_astra_sprint_e_contact_repair_r6_calibration_r1/contact_calibration.json
4629f1c4330b5fcd2b29feb28c8301e942bb0d7c4639070ddd82e26711e72881
seed_san_ual_astra_sprint_e_contact_repair_r6_guides_r2/capture.json
6df67df398cd1bb36cc485b74c7f577b1aaa6f09d22506f273c05cc95e0a58d3
seed_san_ual_astra_sprint_e_contact_repair_r6_guides_r2/POSE_GUIDES_8PHASE_1920X1080.png
495d4679d52d97c6c1cae9c7f78012e7a09bd5742af422e56eca5c2f16c48f7c
```

The final native images are under `seed_san_ual_astra_sprint_e_contact_repair_r6_guides_r2/frames/`:

```text
contact_l.png e6bcfd3ec0f27f8bc2ccc5bb937559844f0cbafcbb3cdf6b6cb215240a92b915
down_l.png 875c33a1ef70c701869f5d049ac14e0c61972796cc0e769fd30c34b5dd3ad449
passing_l.png 1645ba041ce0b31aa4d0d3b8490f95c627771059a2b337890485b085e56bc022
flight_l.png 145f6ca2f6feaa69246a2905ec837a105ab8ed9708c1f3b0b8485c449b4108e0
contact_r.png 785809d04c7beba041b184e6b598f0707bf4928125a68167234f2ce9b789c232
down_r.png 7cffe658e6e4373e913bad5c914df0e9c485d84b809df287c98025f8fa090f16
passing_r.png b489458191a4c52e62bbc9a4931398be9e63d91871de1ad441bf078eca8fc2f9
flight_r.png d41b6e851504a892ad2c2afa5a4b2ab4816e76cfa6d3cf6087e7c9cd65474040
```

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent review. **HOLD for the complete guide set; no production promotion authorization.**
