# Current resume — 2026-09-19

SUPERSEDED later on 2026-09-19: the user cancelled all humanoid enemies,
including the rifle. Do NOT continue the rifle work described below. Its
sources/receipts are retained history. Current implementation removes those
runtime bindings and uses reviewed drones/boss plus licensed kArchive props.
See `qa/enemy_retirement_20260919/` and `qa/karchive_props_20260919/`.

## Completed local implementation

R04 SFX are integrated into the actual Godot combat path, not just a web demo.
Read `qa/sfx_integration_20260919/RESULT_KO.md`. 24 selected variants / 12 cues,
scene-scoped voice/priority/limiter handling, boss telegraph/damage/death hooks,
and literal source/license credits are in place. Actual engine mix and 1080p
viewport evidence are retained. No remote deployment and no subjective
listening approval was claimed. Shared enemy/player regressions passed.

## Rifle remains the active asset priority

14/56 rifle slots (E and SE cycles) remain approved; no incomplete atlas was
activated. New S/walk/0 attempt and actual tool response are retained under
`motion_lab_v1/qa/resume_enemies_20260919/` and the hash-named quarantine.
The returned master is genuinely RGBA alpha 0..254, with clean native-scale
light/dark separation. It is still HOLD: head and rifle face sideways rather
than the required S front. Do not retry as though native alpha failed, or
approve it because it has only two leg chains. Existing active source unchanged.
Its verified duplicate managed staging file was removed; the original bytes
and actual provenance remain in the project's quarantine.

## New user-authorized optional tools

Read `motion_lab_v1/pilots/kimodo_vrm_20260919/RESULT_KO.md` and the Studio
skill's `references/local-motion-assistance.md` before using the new option.
Actual local Kimodo run: one 4-second CPU skeletal sample, 120 frames / 30Hz,
NPZ/BVH/native 1080p diagnostics, exact license/input binding, 9 tests passed.
No local image-generation model or external generation service was used.

The raw motion alternates steps at stable 1.1-second same-leg intervals but
holds the imaginary prop with the opposite hand ordering. It is NOT approved
as a rifle guide or app motion. 21 Seed-san VRM bones are mapped, but no VRoid
launch/skin retarget/sole-contact validation was completed. A stable cadence,
one mapping receipt, or a native video container cannot stand in for those gates.

Continue the existing rifle repair route. Use Kimodo/VRM only where a scoped
comparison proves useful; do not restart accepted player gaits, invent another
humanoid enemy, or promote generic body geometry as SABLE appearance.
