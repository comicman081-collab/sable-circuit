# SABLE CIRCUIT

**Status:** M5 actual Godot runtime visual baseline  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable flow

**TITLE → OPERATIONS BASE → CH01 BRIEFING → STORY STAGE 01 → RESULTS → OPERATIONS BASE**

Chapter 01 is **BLACKOUT AT SITE-7** with six required authored rooms plus two optional rooms. Required progress is gated and cannot be skipped.

## M5 actual-runtime visual baseline

M5 makes **real Godot GUI rendering** part of visual acceptance. AI-generated concepts or mockups are not valid implementation evidence.

GitHub Actions launches exact SHA-pinned Godot 4.7.2 under Xvfb at 1280×720 and must render exactly 24 PNG evidence frames:
- traversal / map movement
- Decon Corridor combat
- Signal Anchor Guardian Phase 3
- all eight Stage-01 environment styles
- ASTER facing sectors 0–7
- unique Rifle / Shield / Drone / Aberrant / Boss death frames

### Tactical HUD and typography

The field HUD now includes a route minimap, objective panel, live ASTER / ROOK / MICA portrait cards and HP, ammunition / weapon panel, ENERGY and Q/E/R slots.

HUD typography is **Rajdhani Medium v1.201** from pinned Google Fonts revision `9d1ce2fc3c335cca32b6db00c19f55d57b0a68fe`. The font is declared in `assets/external/manifest.json`, fetched through `tools/fetch_external_assets.py`, verified against SHA-256, and licensed under SIL OFL 1.1. CI verifies Godot actually selects the bundled font instead of a system fallback.

### Site-7 2.5D field presentation

M4's eight unique room identities remain intact. M5 adds a consistent facility-depth pass:
- raised metallic room shells
- top / side wall faces
- deck lips and cast shadows
- structural braces and luminous insets
- recessed floor plates and deck seams
- cinematic edge attenuation, scan texture and subtle cool / amber blooms

### Operators

All three keep independent high-resolution rigs and art identities:
- **ASTER** — silver/cool ponytail, navy/cyan precision silhouette.
- **ROOK** — white hair, charcoal/bronze heavy silhouette.
- **MICA** — ash-brown braid, dark/teal sensor silhouette.

The live formation is widened for on-field readability. Each operator has contact grounding and the selected operator has a subtle identity-colored control ring.

### Enemy and combat feedback

Every unique enemy keeps its own rig and motion grammar, with contact shadows and segmented overhead health/threat UI.

Projectile and impact presentation remains identity-specific rather than recolored reuse:
- ASTER — precision coil dart
- ROOK — magnetic pressure wake
- MICA — sensor pulse packet
- Rifle — red/white segmented tracer
- Shield — amber heavy slug
- Drone — magenta/cyan packet
- Aberrant — organic purple bolt
- Signal Anchor Guardian — violet/magenta phase lance

Associated hit VFX retain separate shapes, timing and motion.

## M4 systems preserved and runtime-verified

### Eight-sector character presentation

ASTER / ROOK / MICA resolve all eight facing sectors. Sector changes affect front/rear depth, head/torso perspective, arm/weapon z-order and rear shading rather than rotating only the weapon.

Rear-facing sectors hide the facial overlay; front/side sectors show an identity-specific facial micro rig with blinking, eye aim, brow shape and hit expression.

### Identity-specific secondary motion

Hair, coat and accessories use acceleration/aim-turn spring motion:
- ASTER — quick, sharp trailing response.
- ROOK — heavier, strongly damped mantle response.
- MICA — soft long-delay coat/sensor response.

### Unique enemy hit and death presentation

- Rifle Trooper — shoulder/weapon kick + metal fragment tumble.
- Shield Breacher — shield-first recoil + heavy slab collapse.
- Recon Drone — bank/sensor reaction + spiral electronic breakup.
- Aberrant Runner — elastic skull/torso/tail reaction + organic contraction/tear breakup.
- Signal Anchor Guardian — iris/arm reaction + ring/pylon collapse.

Visible death is detached from the authoritative enemy transaction, so destruction can finish after gameplay defeat resolves exactly once.

### Signal Anchor Guardian phases

- **Phase 1:** >66% HP — base orbital behavior.
- **Phase 2:** 34–66% — expanded ring/pylon motion and additional angled lance pattern.
- **Phase 3:** <=33% — unstable iris/arms, increased attack pressure and five-way lance pattern.

### Stage 01 authored environment identities

1. Outer Gate — structural ribs + amber terminal.
2. Decon Corridor — cyan strips + animated decon mist.
3. Archive Annex — shelves + scanning hologram.
4. Containment Junction — red alarm field + barricades.
5. Core C — violet iris rings + boss-reactive energy columns.
6. Emergency Lift — animated green lift rails.
7. Emergency Stores — amber supply-crate language.
8. Signal Lab — live teal waveform + scanner arcs.

## Unique-art rules

The three playable operators and five Stage-01 enemy identities each own separate high-resolution master SVGs and separate 2048×2048 rig sheets. Systems and semantic bone interfaces may be shared; visible/audible final identity assets may not be reused.

Projectile geometry, hit VFX, fire SFX and impact SFX profiles remain identity-specific. `tools/validate_unique_art.py` rejects reused IDs/paths and byte-identical master or rig assets through SHA-256 checks.

Current field controls: **WASD move · Shift run · mouse aim · LMB fire · R reload · Space evade · 1/2/3 swap · F interact**.

## Frozen architecture rules

1. `project.godot` stays at repository root; nested `game/` is forbidden.
2. Field traversal and combat use the same operator actor.
3. Movement and aim are independent.
4. Story/mission authority is data-driven under `data/story` and `data/missions`.
5. Required story rooms resolve in authored order.
6. Systems may be shared; visible/audible final identity assets may not be reused.
7. Every combat identity owns unique visual, motion, projectile, hit-VFX, fire-SFX and impact-SFX profiles.
8. Master art and layered rig sheets are checked against byte-identical reuse.
9. Animation/VFX are presentation; gameplay code authors results.
10. M4 premium presentation preserves eight sectors, identity secondary motion, unique enemy death, boss phases and eight unique Stage-01 room signatures.
11. M5 adds pinned typography, facility depth, field grounding, overhead combat UI and actual-runtime screenshot evidence.
12. CI uses exact SHA-pinned Godot 4.7.2 and retains M1/M2/M3/M4/M5 smoke coverage.
13. **GitHub Pages/public deployment remains intentionally disabled until the game is complete.**

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — animated combat prototype
- `docs/M2_STORY_VERTICAL_SLICE.md` — lobby/story-stage loop
- `docs/M3_UNIQUE_2P5D_ART_BIBLE.md` — non-reuse production-art rules
- `docs/M3_HIGH_RES_UNIQUE_ART_RUNTIME.md` — M3 high-resolution runtime
- `docs/M4_PREMIUM_MOTION_ENVIRONMENT.md` — M4 direction/motion/reaction/boss/environment contract
- `docs/M5_ACTUAL_RUNTIME_VISUAL_BASELINE.md` — real-render visual evidence, HUD/font/depth baseline
- `docs/ANIMATION_SPEC_v0.1.md` — animation contract
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data architecture
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI/external-resource policy
