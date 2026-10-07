# M5 Actual Runtime Visual Baseline

M5 changes SABLE CIRCUIT's visual acceptance rule from code-only presentation checks to **actual Godot 4.7.2 GUI-render evidence**.

## Authority

- Engine: exact SHA-pinned Godot 4.7.2 stable.
- Renderer: Compatibility.
- Runtime screenshots are rendered by Godot under Xvfb at 1280×720.
- AI-generated concept images, mockups, composited illustrations, or non-runtime renders are **not valid runtime evidence**.
- Public deployment / Pages remains disabled.

## Actual evidence set

`tests/render/runtime_capture.gd` must produce exactly 24 PNG frames:

1. map movement
2. Decon Corridor combat
3. Signal Anchor Guardian Phase 3
4–11. all eight authored Stage-01 environments
12–19. ASTER facing sectors 0–7
20–24. Rifle / Shield / Drone / Aberrant / Boss death sequences

The Actions `runtime-capture` job rejects missing evidence or a capture count other than 24.

## M5 presentation baseline

### Tactical HUD

The Stage-01 HUD now contains:
- authored route minimap and enemy markers
- objective panel
- live ASTER / ROOK / MICA portrait cards and HP
- active weapon and ammunition
- ENERGY bar
- Q/E/R action slots
- story/status strips

HUD typography uses **Rajdhani Medium v1.201**, fetched from the exact Google Fonts revision
`9d1ce2fc3c335cca32b6db00c19f55d57b0a68fe`.
The file is declared in `assets/external/manifest.json`, verified against SHA-256
`12ff7dcfe4c206e3875ac53b1762eab57de6a2fa7f5a86c26b97b88d6591eac2`,
and licensed under SIL OFL 1.1. `m5_font_smoke.gd` verifies that Godot actually selects the bundled font rather than a system fallback.

### Site-7 depth and lighting language

M5 retains the eight unique room effects from M4 and adds:
- metallic raised room shells
- top / side wall faces
- lower deck lips and cast shadows
- structural braces and luminous room insets
- recessed floor plates and deck seams
- cinematic screen-edge attenuation, subtle scan texture, and corner light blooms

`Site7DepthPass.debug_room_depth_count()` must report all eight authored environments.

### Player presentation

- ASTER: silver/cool ponytail, navy/cyan precision identity.
- ROOK: white hair, charcoal/bronze heavy identity.
- MICA: ash-brown braid, dark/teal sensor identity.

The live squad formation uses a wider echelon so all three silhouettes remain readable in traversal and combat.
Every operator has an identity-colored contact shadow / active-control ring beneath the high-resolution rig.

### Enemy presentation

Each unique enemy keeps the M3 no-reuse contract and adds:
- contact shadow appropriate to ground / flying / boss mass
- segmented overhead health / threat marker
- boss marker response to HP phase

Projectile and hit presentation is more readable while remaining identity-specific:
- ASTER — precision coil dart
- ROOK — broad magnetic pressure wake
- MICA — sensor pulse packet
- Rifle — red/white segmented tracer
- Shield — amber heavy slug
- Drone — magenta/cyan packet
- Aberrant — organic purple bolt
- Signal Anchor Guardian — violet/magenta phase lance

The associated hit VFX retain separate silhouettes and timing.

## Runtime acceptance

A M5 change is not acceptable unless all of the following pass on the same branch head:

- repository contract
- unique-art ID/path/SHA validation
- M5 presentation contract
- Godot import / parse
- M1 playable squad smoke
- M2 story-flow smoke
- M3 unique-art runtime smoke
- M4 premium motion/environment smoke
- M5 bundled font + depth + shadow + overhead UI smoke
- 24-frame actual GUI runtime capture

## Quality status

M5 is the **actual-runtime visual baseline**, not final production-art completion. It replaces the earlier developer-looking screen with a coherent tactical HUD, reproducible tech typography, Site-7 depth language, contact grounding, and readable combat feedback while preserving the verified 8-direction / face / death / boss / environment systems.

Further character/enemy illustration refinement can raise material rendering and animation nuance without changing these frozen runtime contracts.
