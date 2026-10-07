# Animation Source Notes — Pilot Hold

> **Superseded operationally by `ASTER_ANIMATION_NOTES.md`.** The source
> restriction remains valid, while the active path is now Blender pose/depth
> guides plus controlled high-resolution 2.5D sprite authoring after the
> ASTER static master passes.

Only the already-present Quaternius Universal Animation Library 1 and 2 FREE
Standard files were inspected:

- `assets/external/quaternius/ual1/UAL1_Standard.glb`
- `assets/external/quaternius/ual2/UAL2_Standard.glb`

Their meshes are not visual authority and were not copied into the project.
No Universal Base Character, mannequin, paid model, Pro, Source, or other
external character visual asset was accessed or promoted.

Actual motion-reference mapping for the non-final, mesh-free Blender 360 pose
driver:

| SABLE action | UAL reference |
| --- | --- |
| idle | UAL1 `Idle_Loop` |
| locomotion | UAL1 `Jog_Fwd_Loop` |
| fire | UAL1 `Pistol_Shoot` with ASTER rifle-specific cleanup |
| reload / hit / downed | not selected; out of this visual-gated pilot |
| shield special | not selected; out of ASTER pilot scope |

The custom ASTER driver actions are timing and pose construction only: no UAL
mesh was retained or rendered. High-quality sprite authoring and runtime
retarget/export remain gated on a reviewed fire/static visual authority. This
preserves the requested motion-source constraint while avoiding a low-quality
final body.

## ASTER UAL V5 promoted pilot slice

The current ASTER-only locomotion slice now uses UAL1 `Jog_Fwd_Loop` as actual
timing/joint-curve authority: 24 normalized samples, 15 joints, two planted-foot
contact windows, and verified root-motion evidence. Blender 5.2.1 extracted the
curves headlessly; no UAL mesh was rendered or exported. The resulting ASTER
raster atlases remain the only visible runtime body.

UAL1 and UAL2 action inventories were also checked for a dedicated tactical
strafe or backpedal loop. Neither installed FREE Standard pack contains one.
The V5 pilot therefore keeps the approved forward-jog curve, advances it during
moving fire for every move/aim relative angle, and scales playback cadence from
actual ground speed. It does not invent or falsely attribute an unavailable UAL
strafe action. A bespoke ASTER strafe/backpedal family requires separately
authored sprite poses after this bounded pilot review.
