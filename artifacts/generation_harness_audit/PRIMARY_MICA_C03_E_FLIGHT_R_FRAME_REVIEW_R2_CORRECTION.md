# Primary visual review correction — MICA C03 E/run/flight_r R2

- Reviewer: Codex Astra primary visual review
- Corrected: 2026-09-08T00:50:00+09:00
- Exact frame-audit subject: `0bdb336f805665955d182df2df4ff10b4bd6a3c829a57d80b7b574b596376c5b`
- Verdict: **FAIL_NOT_PROMOTABLE**

This correction supersedes my preliminary
`PRIMARY_MICA_C03_E_FLIGHT_R_FRAME_REVIEW_R2.md` judgment. That earlier file is
retained as failed-review provenance and must not be used as PASS evidence.

The approved front source provides an independent laterality marker: the
beige vertical plate on the thigh pouch belongs to MICA's anatomical right leg
(screen-left in the front source). In the generated E frame that same marked
leg is the forward/leading leg. The visible result therefore reads as
**anatomical right leg leading**, while the bound `flight_r` contract requires
flight after right toe-off with **anatomical left leg leading**.

| Contract check | Corrected verdict | Reason |
| --- | --- | --- |
| identity_and_costume | HOLD | Overall identity is strong, but the asymmetric thigh marker proves laterality relevant to the requested phase. |
| anatomy_and_limb_count | PASS | Limb count and joint continuity remain visually coherent. |
| whole_body_direction | PASS | The body remains a coherent E profile without a 90-degree waist turn. |
| phase_and_stride | FAIL | Broad airborne stride is present, but the leading anatomical leg is the opposite of the requested phase. |
| feet_ankles_and_contact | HOLD | Both feet are airborne and visually coherent, but the left/right phase assignment is wrong. |
| weapon_hands_and_visible_muzzle | PASS | Both hands grip the rifle and the main muzzle is visible. |
| matte_edges_and_subject_preservation | PASS | Runtime RGBA derivation is reproducible and the native dark review shows clean separation. |

Required mechanism change: future prompts and reviews must bind anatomical
laterality to immutable costume markers, not infer left/right from screen
position or text labels. For `flight_r`, the forward leg must carry MICA's
anatomical-left dark thigh equipment while the beige vertical plate remains on
the anatomical-right trailing leg. The failed image may not be renamed or
reclassified as `flight_l`; it remains tied to its original request and permit.
