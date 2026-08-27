# M5 — Actual Runtime Visual Validation

M5 closes the gap between implementation claims and what the game actually renders.

## Evidence rule

Generated concept art, mockups, edited screenshots and AI-generated images are **not** runtime evidence. M5 evidence is accepted only when the PNG is captured from Godot 4.7.2 running the repository scene under the same committed code/assets being validated.

GitHub Actions runs Godot through Xvfb at 1280×720 with the Compatibility renderer and executes `tests/render/runtime_capture.gd`. The resulting PNG files are uploaded as the `sable-circuit-runtime-captures` workflow artifact.

## Required runtime captures

The capture job must create exactly 24 PNG files:

- `01_map_movement.png` — three-operator traversal/formation state.
- `02_combat_decon.png` — authored Decon Corridor Rifle/Drone/Aberrant combat.
- `03_boss_phase3.png` — Signal Anchor Guardian below 33% HP in Phase 3.
- `04_room_outer_gate.png` through `11_room_signal_lab.png` — the eight authored Stage 01 visual environments.
- `12_direction_sector_0.png` through `19_direction_sector_7.png` — all eight ASTER facing sectors, including front/side/rear face visibility behavior.
- `20_death_rifle.png` through `24_death_boss.png` — identity-specific death presentation for Rifle, Shield, Drone, Aberrant and Signal Anchor Guardian.

CI fails if key files are missing or the total count is not exactly 24.

## M5 presentation direction

The production target is a premium dark sci-fi 2.5D tactical-action presentation rather than a debug arena.

### HUD

`StoryStageHUD` now uses a tactical layout with:

- live authored-route minimap and enemy contacts,
- current room and mission objective,
- three unique operator portrait cards with runtime HP,
- active weapon and ammunition,
- energy and skill-key regions,
- condensed technical system-font stack: Rajdhani → Bahnschrift SemiCondensed → Arial Narrow → DejaVu Sans Condensed → Liberation Sans.

The stack avoids bundling a mutable or unlicensed font binary while preserving the intended condensed technical typography on supported systems.

### Site-7 architecture

`Site7FacilityArchitecture` is rendered below the existing eight room-specific M4 effects. It supplies a full dark world background, metal corridor deck, wall mass, room shells, inset floor panels, bulkheads, cable runs, hazard strips and embedded room lighting so camera edges no longer expose a debug clear color.

### Playable identity refinement

The same no-reuse rule remains mandatory. M5 refines the actual master/rig SVGs rather than swapping them for a shared skin:

- ASTER — silver comet ponytail, navy/cyan precision armor, gold precision hardware.
- ROOK — white hair, charcoal heavy mantle/armor, bronze breach hardware and scattergun.
- MICA — ash-brown side braid, dark technical coat, teal sensor fins and circular emitter carbine.

Their semantic rig infrastructure remains shared, but visible final art remains identity-owned and SHA-checked.

## Validation gate

M5 is not mergeable unless all of the following pass on the same branch head:

1. repository contract,
2. unique-art/path/SHA contract,
3. pinned Godot 4.7.2 import/parse,
4. M1 combat regression,
5. M2 lobby/story regression,
6. M3 unique-art runtime regression,
7. M4 premium motion/environment regression,
8. M5 24-image actual GUI-render capture.

Public deployment / GitHub Pages remains disabled.
