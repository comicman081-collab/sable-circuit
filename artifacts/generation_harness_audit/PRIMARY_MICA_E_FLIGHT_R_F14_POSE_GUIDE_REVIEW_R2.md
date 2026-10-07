# Primary visual review — MICA E/run/flight_r pose guide R2

- Reviewer: Codex Astra primary visual review
- Reviewed: 2026-09-08T00:30:41+09:00
- Pose-guide subject SHA-256: `e46992745f157975b88170a9eb947bd2c946ac93ef31e47092bc7441001435c0`
- Verdict: **PASS — lower-body pose guide only**

The bound Seed-san/UAL image is not MICA artwork and is not permitted to supply
visible pixels, costume, identity, weapon, arms, hands, equipment, or material.
It is approved only as a geometric lower-body reference for one built-in
ImageGen request.

## Checks

| Check | Verdict | Evidence |
| --- | --- | --- |
| exact_direction | PASS | In native frame 014, head, pelvis, knees and foot travel form a coherent screen-right/E profile. |
| action_identity | PASS | The bound capture and retarget result identify `Sprint_Loop`; the full 17-frame cycle shows alternating airborne sprint phases. |
| phase_support_mapping | PASS | Under the support-foot convention, F14 occurs after the right low-sole window; the left leg leads and both feet are airborne, matching `flight_r`. |
| feet_and_ankles | PASS | Both complete foot silhouettes are visible. Left/right sole clearances are 192.17 mm and 225.42 mm above the diagnostic baseline; no sideways 90-degree ankle is visible. |
| torso_silhouette | PASS | Pelvis and spine form one continuous forward-running silhouette without a 90-degree waist turn. Exact sprint arm pose and torso lean are explicitly excluded. |
| full_body_visibility | PASS | The human guide body and both feet fit the 1920x1920 native frame. No human limb is cropped. |
| pose_guide_only_boundary | PASS | Only direction, airborne phase, left-leading/right-trailing leg ordering, knee bend and broad stride may be transferred. Generic appearance and robot appendages must be ignored. |

This PASS does not approve the ImageGen result, MICA appearance continuity,
ground contact, the other six gait phases, temporal animation, firing, runtime,
HTML, or Luna reproduction. Those remain gated separately.
