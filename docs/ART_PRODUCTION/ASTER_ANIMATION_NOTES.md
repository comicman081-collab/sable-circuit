# ASTER Animation Notes — V2 Gate Hold

## Approved motion sources

Only the existing free Standard libraries were inspected:

- `assets/external/quaternius/ual1/UAL1_Standard.glb`
- `assets/external/quaternius/ual2/UAL2_Standard.glb`

No UAL visual mesh, Universal Base Character, mannequin, paid/Pro/Source
asset, Krea asset, or external character model is used.

## Verified action shortlist

| ASTER action family | Pose/motion reference | Planned cleanup |
| --- | --- | --- |
| Idle | UAL1 `Idle_Loop` | combat-ready breathing and stable rifle aim |
| Locomotion | UAL1 `Jog_Fwd_Loop` | quarter-view contact/passing/up/down readability |
| Aim / Fire | UAL1 `Pistol_Shoot` | ASTER-specific rifle grip, pre-fire, recoil, recover |
| Reload / Hit reference | not selected in this pilot | only after the visual gate and user review |

UAL2 remains out of the ASTER pilot scope. No unavailable action name is a
pipeline dependency.

## Non-promotion rule

`ASTER_360_POSE_DRIVER__NONFINAL.blend` now contains 24 custom ASTER pose
actions (idle, move, and fire across eight directions), marker-timed from the
three verified UAL1 action categories. It contains zero renderable meshes and
is a headless Blender motion driver only. The 144 matching green-matte guides
and their contact sheets are motion construction evidence, not final sprite
art. No Godot runtime asset has been connected, and high-fidelity sprite-frame
authoring remains blocked until the ASTER visual gate and user review pass.

## V6 integration amendment — 2026-08-30

The preceding V2 text is retained as historical gate evidence; its statement
that no runtime asset is connected is no longer the current integration state.

- Failure baseline `5dbae66` remains **VISUAL FAIL / technical QA PASS /
  production HOLD**. Move V5 also remains a visual leg-amplitude FAIL.
- Current locomotion is `move_360_ual_v6`: eight directions, 24 frames per
  direction, 24 fps, derived from UAL1 Standard `Jog_Fwd_Loop` curves.
- The decoded-atlas visible-leg primary gate and auxiliary weapon/costume gate
  both pass. Human visual review is still required.
- Moving fire uses the atomically paired `composite_fire_v6` lower/upper family;
  its 1,344-pair costume QA passes with exact white/cyan panel retention.
- Godot and the interactive HTML consume the shared
  `assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json` contract.
- Godot runtime path: `scripts/animation/aster_v4_locomotion_preview.gd`, owned
  by `AsterV4LocomotionPreview` in `scenes/actors/player/OperatorActor.tscn`.
- Interactive path:
  `art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html`.
- True aim-relative strafe/backpedal remains **HOLD_NOT_PROVEN** because the
  lower atlas still follows aim/facing sector rather than a separate velocity
  sector. Cross-direction raster splicing is not an accepted substitute.
- ASTER Pilot and production expansion remain **HOLD** pending human review.

Full evidence and bounded verdict:

```text
docs/ART_PRODUCTION/ASTER_UAL_V6_MOVING_FIRE_INTEGRATION.md
```
