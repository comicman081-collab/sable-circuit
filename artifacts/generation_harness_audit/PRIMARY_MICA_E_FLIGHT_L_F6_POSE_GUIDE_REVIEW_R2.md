# Primary visual review — MICA E/run/flight_l pose guide R2

- Reviewer: Codex Astra primary visual review
- Reviewed: 2026-09-08T00:54:00+09:00
- Pose-guide subject SHA-256: `0546412aec71c1c8486454852fe6e07b916aed8c8f25f74f2354ffba1b7c14e9`
- Verdict: **PASS — lower-body pose guide only**

The bound Seed-san/UAL image is not MICA artwork. It may supply only E-facing
lower-body geometry for one built-in ImageGen request; its robot equipment,
appearance, clothes, bare-foot shape, hands, arms and exact torso lean are
excluded.

| Check | Verdict | Evidence |
| --- | --- | --- |
| exact_direction | PASS | Head, pelvis, knees and foot travel read as one screen-right/E profile. |
| action_identity | PASS | The exact capture and retarget bind `Sprint_Loop`; the full cycle visibly alternates sprint flight. |
| phase_support_mapping | PASS | F6 follows the left low-sole window; anatomical right leg leads and left leg trails, matching support-convention `flight_l`. |
| feet_and_ankles | PASS | Both complete foot silhouettes are airborne and remain aligned in the sagittal running plane without sideways ankle yaw. |
| torso_silhouette | PASS | The human pelvis/spine silhouette is continuous and directionally coherent; exact arm swing and lean are excluded. |
| full_body_visibility | PASS | The human body and both feet are inside the native 1920x1920 frame. |
| pose_guide_only_boundary | PASS | Only direction, airborne phase, right-leading/left-trailing order, knee bend and broad stride may transfer to ImageGen. |

This is not approval of contact, grounding, MICA artwork, another phase,
temporal gait, firing, runtime, HTML or Luna.
