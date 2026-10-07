# Primary visual review — MICA C03 E/run/flight_r R2

- Reviewer: Codex Astra primary visual review
- Reviewed: 2026-09-08T00:46:00+09:00
- Exact frame-audit subject: `0bdb336f805665955d182df2df4ff10b4bd6a3c829a57d80b7b574b596376c5b`
- Verdict: **PASS_ONE_VISIBLE_FRAME_ONLY** for the seven checks below

I directly compared the approved MICA S source, approved E direction master,
ImageGen raw image, exact-green preserved master, runtime RGBA, and the native
1:1 green/dark review canvases. This review does not approve temporal gait,
another phase/direction, firing animation, runtime, HTML, or Luna.

| Contract check | Verdict | Actual visual basis |
| --- | --- | --- |
| identity_and_costume | PASS | MICA's face, long brown side braid, dark navy patterned tactical coat, beige edging, teal lining, fitted trousers, knee protection, boots, pouches, gloves, cyan-lit twin back equipment and white/dark/cyan rifle remain recognizable and coherent with the approved source/E reference. No gray guide appearance or robot appendage was inherited. |
| anatomy_and_limb_count | PASS | One head, two arms, two hands and two legs are present. Pelvis, thighs, knees, calves, ankles and boots connect continuously; there is no duplicate joint, merged leg, swollen calf, detached foot or extra human limb. |
| whole_body_direction | PASS | Face, shoulders, chest, pelvis, knee travel, boots, hands and rifle all form one screen-right/E profile. The waist is not rotated 90 degrees and the lower body is not front-facing. |
| phase_and_stride | PASS | The frame visibly reads as an airborne sprint with a broad front/back split. Under the bound support-foot convention, anatomical left leads and anatomical right trails after right toe-off, matching `flight_r`; it is not a tiny shuffle, high-knee march, idle pose or skate. |
| feet_ankles_and_contact | PASS | Both complete boots are visible and airborne. The lead boot follows the lead shin; the trailing foot plantar-flexes in the sagittal running plane without sideways 90-degree yaw. No planted-foot claim is made for this flight frame. |
| weapon_hands_and_visible_muzzle | PASS | Both gloved hands visibly grip the rifle; the main barrel extends to a visible rightmost muzzle tip. The annotation uses that main barrel axis, not the lower auxiliary cylinder, and points right. No flash/projectile is painted into the frame. |
| matte_edges_and_subject_preservation | PASS | The exact-green master remains preserved. The separately derived RGBA has transparent borders and closed gaps around the weapon/hands/limbs; QA reports 4,580 non-exact strong-green pixels removed, zero strong-green residual visible pixels and byte-exact retained RGB. The 1:1 dark review shows no material green fringe or body hole. |

The generated 1254×1254 image is shown at 1:1 inside native 1920×1310 review
containers; it was not upscaled. The automated 1080p evidence validator passed
container/decode checks, which supplement but do not replace this visual review.
