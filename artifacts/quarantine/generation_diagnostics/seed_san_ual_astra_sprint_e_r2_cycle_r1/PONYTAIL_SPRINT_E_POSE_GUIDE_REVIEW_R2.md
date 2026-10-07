# Ponytail FULL — Sprint_Loop E pose-guide review R2

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL reviewer.
- Reviewed at: 2026-09-07T15:27:20Z (2026-09-08 00:27:20 KST).
- Applied skill: `sable-motion-production`, including its rig/motion and art-authority boundaries.
- Scope: existing Seed-san + UAL Sprint_Loop E diagnostic, 17 captured frames (16 unique times plus wrap). No code edits, rendering, generation, runtime launch, asset promotion, or Luna work performed.
- Overall verdict: **HOLD — the complete eight-phase production guide set is not approved.** Two isolated airborne lower-body pose guides receive the narrow PASS below. This is not MICA appearance, temporal gait, grounding, firing, HTML, or production approval.

## Exact evidence and direct inspection

The following paths are relative to this report unless stated otherwise.

| Evidence | SHA-256 |
| --- | --- |
| `capture.json` | `eec3c9042567b131d3fb35e1e3943283d4352706517a06ae305067282d0a0283` |
| `../seed_san_ual_astra_sprint_e_r2/retarget_result.json` | `0c4157663e34052e9699f38830b8147bb62e32d5b75c564264ba6a47d6b8d6a3` |
| `../seed_san_ual_astra_sprint_e_r2/SeedSan_UAL_Sprint_Loop_DIAGNOSTIC.blend` | `4e56ff8c5a4127753ac4de2ebd9aa1d9d3751da9684e1b2007ea7ac8d5db101c` |
| `SPRINT_E_CYCLE_CONTACT_SHEET_1920X1080.png` | `eee6375df296ed6f863f8d925f3463234a37b307f923d1b7acfb071ff1139aef` |
| `contact_sheet_manifest.json` | `c68d260fae25d0b433df1187df25baaa9fc00ea2d713e055902f9601bc0e9edf` |
| `video_manifest.json` | `26126542a682276101d7df3e2eef8a59796d5797e53c0200a2d267b8ff37a4ef` |
| `ASTRA_VRM_UAL_SPRINT_LOOP_E_DIAGNOSTIC_NATIVE.mp4` | `c5dd1be7b714f9a61b57873b981ad17919ef789c09df202d3800ee3d00d8611c` |
| Project `tools/character_pipeline/probe_vrm_ual_retarget.py` | `2a4010ad5c91248c49bc91f250d3420391a5c5207fff359cc66460c1cd21ec8f` |
| Project `tools/character_pipeline/capture_vrm_diagnostic_cycle.py` | `dbf803202fce0040b8d13cda1e4f0dd2ba560d72948ad84861ae181a0db84d00` |
| Project `tools/character_pipeline/visible_frame_contract.json` | `cc4c0b8b4992be69078f41d6873d7eeeb37e69b73b46da48a251ac1c32675df8` |

I personally opened the R2 sheet and every individual R2 native frame `000.png` through `016.png`, not only the sheet. Files are native 1920×1920; the tool displayed the individual frames at 1600×1600, so this is not a claim of exhaustive one-pixel edge inspection. The sheet is native 1920×1080 but individually fits each subject into its small cell: it cannot prove common scale, root anchoring, or a common floor. The original captures and actual world sole vertices are the basis for this review. I inspected the video manifest, not real-time playback of the video.

All 17 frame-file hashes match their entries in `capture.json`. R2 model/input blend/output blend/generator/UAL/license/capture-generator references were independently hashed and match. R2 camera matrix and all recorded sole vertex coordinates at all 17 capture times equal R1, but PNG file hashes differ; R2 was therefore opened independently rather than silently inheriting R1 visual approval. R1 remains historical evidence, not the binding for this report.

Source time is preserved: UAL frames 0–16 at 24 fps and baked frames 0–16 at 24 fps both span 0.6666666667 s. At the nine common times between the 25-row baked playback and 17-row capture, both feet's evaluated vertex arrays match exactly. Wrap frame 16 equals frame 0 for all measured sole vertices. The two-second video is this single cycle played three times, not three independently evaluated cycles or a world-ground locomotion test.

## Eight-phase mapping and verdicts

Use the current **support-block** convention: `flight_l` follows left toe-off and has the right leg leading; `flight_r` follows right toe-off and has the left leg leading. `passing_l/r` are the contract's exact names for the requested pass phases. Left/right here are anatomical labels from the bound bone/sole mapping, not screen-left/right. Do not reverse this convention in ImageGen prompts.

| Requested phase | Best existing candidate | Verdict | Direct reason and permitted use |
| --- | --- | --- | --- |
| `contact_l` | F1, following descending F0 | HOLD | Left leg is ahead, but its lowest measured sole is 16.66 mm above the diagnostic baseline. Initial ground crossing/heel or forefoot strike is not established. Do not use as an approved contact guide. |
| `down_l` | F2 | HOLD | Bent stance-like left leg and forward swing progression are visible; the sole is 21.73 mm above the baseline, and actual pelvis lowering/load is not recorded. A bent knee alone does not prove the down phase. |
| `passing_l` | F2–F3 transition, nearest captured F3 | HOLD | Right swing leg passes forward while the left foot has already moved behind the body. F3 sole clearance is 1.73 mm, but contact duration and exact passing event remain uncalibrated. F3 is not a substitute for initial contact. |
| `flight_l` | **F6** | **PASS — LOWER-BODY POSE GUIDE ONLY** | After the left low-sole window, right leg leads and left leg trails. Both measured soles are well clear (303.77/229.43 mm); visible hip–knee–ankle chains have a broad sprint split, not tiny taps or a sideways ankle. This is not approval of absolute jump height, arm pose, or world grounding. |
| `contact_r` | F9–F10 descent, nearest low captured F10 | HOLD | Right leg is ahead, but its lowest sole is 21.85 mm above the baseline. No independent contact onset is demonstrated. |
| `down_r` | F10–F11 interval; no separately verified captured loading event | HOLD | The integer samples pass rapidly from the forward low leg to the passing configuration. Neither a distinct lowest-pelvis/load sample nor actual planted support is established. Do not duplicate F10 under another label to claim eight distinct approved phases. |
| `passing_r` | F11 | HOLD | Left swing leg is coming forward and right foot is behind. Right sole is still 23.86 mm above the baseline; F12 is already rising/toe-off-like (66.37 mm), not a grounded passing replacement. |
| `flight_r` | **F14 — priority next single-frame guide** | **PASS — LOWER-BODY POSE GUIDE ONLY** | After the right low-sole window, **left leg leads and right leg trails**. Both soles are airborne (192.17/225.42 mm), with a clear wide front/back leg split, coherent knees and ankle silhouettes, and intact framing. Appropriate as one E airborne lower-body pose reference, not a completed animation. |

Only F6 and F14 receive guide-use PASS in this report. Other frames remain unapproved for phase-specific generation; F7/F8 additionally FAIL as complete framed guides because the auxiliary robot hand is cut at the right boundary. Their human legs are intact, but the crop must not be described as a clean full-subject capture.

Exact approved guide image bindings:

- Priority `frames/014.png`, frame 14, t=0.5833333333 s, E/run/flight_r: `f8297a11abbb149edbd14ff1bfb76104c15d559bbb986994d5a0ff6b070a70d5`.
- `frames/006.png`, frame 6, t=0.25 s, E/run/flight_l: `b5b2769d207106dd00cce4a171c133eb4088dcc031303e8945530a803ba19988`.

## Sole measurements across the complete capture

These are recomputed lowest actual `wear` sole vertices, not generator IK targets or sockets. Clearances are relative to the probe's **motion-derived** `global_ground_z_m=-0.0321567431`, not an independently placed/collision-tested floor. Horizontal separation is the left-minus-right sole-centre distance along camera screen-right, not actor travel or a calibrated step length.

| F | Left clearance mm | Right clearance mm | Left minus right screen-forward separation m |
| --- | ---: | ---: | ---: |
| 0 | 80.39 | 239.15 | +0.951 |
| 1 | 16.66 | 239.65 | +0.693 |
| 2 | 21.73 | 227.55 | +0.276 |
| 3 | 1.73 | 203.63 | -0.216 |
| 4 | 73.99 | 194.13 | -0.594 |
| 5 | 237.90 | 214.66 | -0.960 |
| 6 | 303.77 | 229.43 | -1.109 |
| 7 | 342.63 | 185.11 | -1.086 |
| 8 | 362.00 | 111.52 | -0.932 |
| 9 | 358.50 | 90.56 | -0.790 |
| 10 | 284.74 | 21.85 | -0.414 |
| 11 | 201.90 | 23.86 | +0.152 |
| 12 | 200.67 | 66.37 | +0.704 |
| 13 | 229.42 | 123.44 | +0.994 |
| 14 | 192.17 | 225.42 | +1.135 |
| 15 | 129.26 | 236.34 | +1.047 |
| 16 | 80.39 | 239.15 | +0.951 |

The finer 25-row baked sample minimum is left F2.6667 at 0.00 mm (by definition of the chosen baseline), versus right F11.3333 at **12.61 mm** above that same baseline. A single global offset therefore does not establish bilateral planted contact. The low windows are asymmetric; this does not invalidate the two isolated airborne silhouettes, but blocks contact/grounding PASS.

## Independent visual/mechanism findings

1. **Wide alternating stride is real in this diagnostic.** The leading leg changes twice, with about 1.109 m and 1.135 m opposite-sign sole-centre separations at F6/F14. It is not the earlier barely moving ankle/calf cutout. Those separations must not be substituted for measured runtime displacement, desired MICA speed, or a production stride target.
2. **No visible 90-degree foot yaw or barrel-shaped calf popping in these 17 frames.** The feet pitch down in the trailing swing and return forward for the lead leg. The shapes remain coherent with this particular generic model. A near-vertical trailing foot is sagittal plantar flexion, not evidence of a 90-degree sideways ankle twist. This is visual assessment, not an ankle-bone-angle measurement or all-mesh collision proof.
3. **No measured foot lane swap.** All captured left sole vertices stay on positive world X, right sole vertices on negative world X; their sets do not cross the lateral centreline. Side-projection overlap at F2/F3/F11 is consistent with passing legs, not by itself a crossed-leg defect. Knee/calf self-collision is not fully measured by the available sole-only data and remains outside this approval.
4. **E alignment is coherent for the lower-body guides.** Head, pelvis, knee travel and toes point screen-right; this is not a head/gun-only turn over a frontal lower body. The camera is a fixed near-side orthographic view with slight downward angle. The shoulders rotate with an unarmed sprint and the body leans forward substantially; neither this arm swing nor exact torso lean is an approved armed MICA stance. The file records no per-frame anatomical torso-axis angles, so I do not invent numeric lean measurements.
5. **Framing defect confirmed:** the F7/F8 robot hand runs beyond the right canvas; F6 retains it but with very little right margin. `native_pose` fits the camera to one pose, not the full action envelope. The two selected lower-body silhouettes are intact. All references contain the generic model's extra robot arms, pack, cable, short hair and costume; those must explicitly be ignored as appearance/limb-count sources.
6. **R1's erroneous contact label is repaired, not grounding itself.** In `probe_vrm_ual_retarget.py` around lines 168–175, the minimum-sole window and maximum separation within it still select F2.6667. R2 correctly calls this `unclassified_grounded_window`. Low sole height alone cannot distinguish initial contact, down, passing, or toe-off. The current contract explicitly states support-based phase semantics, closing the former flight-name reversal. The lack of independent ground/contact calibration remains.

## Use boundary and remaining work

For a single ImageGen pose request, F14 may supply **E lower-body direction, left-leading/right-trailing airborne phase and wide front/back limb arrangement only**. F6 may supply the corresponding opposite airborne phase. Their generic visible pixels must never be copied into MICA output, atlas, or HTML. The approved MICA ImageGen identity/costume/weapon references remain the sole appearance authority; robot appendages, bare-foot shape, sprint hand swing and diagnostic material must not be inherited. Resulting ImageGen pixels require a new exact frame audit and independent visual review, particularly waist coherence, calf shape, ankle orientation, weapon/hands, muzzle and matte edges.

Before using the remaining six named phases, establish a fixed independent ground/body frame, record hip/knee/ankle/toe/heel trajectories and actual support transitions, and inspect appropriately timed samples around both loading windows. Do not weaken thresholds, relabel an airborne frame as planted, duplicate a frame to fill a phase, or treat the auto-selected low-sole window as contact. Retain this raw diagnostic for comparison. MICA temporal continuity, eight directions, movement × aim firing, speed/root/ground coupling, 30/60/120 Hz and playable HTML all remain HOLD.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent review; **two pose-guide-only PASS decisions, not production PASS**.
