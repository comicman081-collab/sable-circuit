# SABLE CIRCUIT

**Status:** M4 premium directional 2.5D motion + Site-7 environment  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable flow

**TITLE → OPERATIONS BASE → CH01 BRIEFING → STORY STAGE 01 → RESULTS → OPERATIONS BASE**

Chapter 01 is **BLACKOUT AT SITE-7** with six required authored rooms plus two optional rooms. Required progress is gated and cannot be skipped.

## M4 premium visual runtime

M3's unique high-resolution identity assets remain authoritative. M4 adds a presentation layer without replacing gameplay authority or reusing visible identity assets.

### 1. Eight-sector character presentation

ASTER / ROOK / MICA retain the same high-resolution layered Skeleton2D actors but now resolve all eight facing sectors. Sector changes affect front/rear depth, head/torso perspective, arm/weapon z-order and rear shading rather than merely rotating one weapon.

Rear-facing sectors hide the facial overlay; front/side sectors show an identity-specific facial micro rig with blinking, eye aim, brow shape and hit expression.

### 2. Identity-specific secondary motion

Hair, coat and accessories use acceleration/aim-turn spring motion instead of one shared wobble:
- **ASTER** — quick, sharp trailing response.
- **ROOK** — heavier, strongly damped mantle response.
- **MICA** — soft long-delay coat/sensor response.

### 3. Enemy hit and death presentation

Each Site-7 enemy retains its own high-resolution rig and now has a different hit/death language:
- Rifle Trooper — shoulder/weapon kick + metal fragment tumble.
- Shield Breacher — shield-first recoil + heavy slab collapse.
- Recon Drone — bank/sensor reaction + spiral electronic breakup.
- Aberrant Runner — elastic skull/torso/tail reaction + organic contraction/tear breakup.
- Signal Anchor Guardian — iris/arm reaction + ring/pylon collapse.

Visible death is detached from the authoritative enemy transaction, so destruction can finish after gameplay defeat has resolved exactly once.

### 4. Signal Anchor Guardian phases

- **Phase 1:** >66% HP — base orbital behavior.
- **Phase 2:** 34–66% — expanded ring/pylon motion and additional angled lance pattern.
- **Phase 3:** <=33% — unstable iris/arms, increased attack pressure and five-way lance pattern.

### 5. Stage 01 premium environment identities

The eight authored rooms no longer share one generic gray presentation:
1. Outer Gate — structural ribs + amber terminal.
2. Decon Corridor — cyan strips + animated decon mist.
3. Archive Annex — shelves + scanning hologram.
4. Containment Junction — red alarm field + barricades.
5. Core C — violet iris rings + boss-reactive energy columns.
6. Emergency Lift — animated green lift rails.
7. Emergency Stores — amber supply-crate language.
8. Signal Lab — live teal waveform + scanner arcs.

Ambient floor detail, cables, glow layers and moving particles bind the rooms into one Site-7 location while keeping each room visually identifiable.

## Existing unique art rules

The three playable operators and five Stage-01 enemy identities each own separate high-resolution master SVGs and separate 2048×2048 rig sheets. Systems and bone-name interfaces may be shared; visible/audible final identity assets may not be reused.

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
10. M4 premium presentation must preserve eight sectors, identity secondary motion, unique enemy death, boss phases and eight unique Stage-01 room signatures.
11. CI uses exact SHA-pinned Godot 4.7.2 and retains M1/M2/M3/M4 smoke coverage.
12. GitHub Pages/public deployment remains intentionally disabled until the game is complete.

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — animated combat prototype
- `docs/M2_STORY_VERTICAL_SLICE.md` — lobby/story-stage loop
- `docs/M3_UNIQUE_2P5D_ART_BIBLE.md` — non-reuse production-art rules
- `docs/M3_HIGH_RES_UNIQUE_ART_RUNTIME.md` — M3 high-resolution runtime
- `docs/M4_PREMIUM_MOTION_ENVIRONMENT.md` — M4 direction/motion/reaction/boss/environment contract
- `docs/ANIMATION_SPEC_v0.1.md` — animation contract
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data architecture
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI/external-resource policy
