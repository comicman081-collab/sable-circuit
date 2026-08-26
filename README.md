# SABLE CIRCUIT

**Status:** M3 unique high-resolution 2.5D art runtime  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable flow

**TITLE → OPERATIONS BASE → CH01 BRIEFING → STORY STAGE 01 → RESULTS → OPERATIONS BASE**

Chapter 01 is **BLACKOUT AT SITE-7** with six required authored rooms plus two optional rooms. Required progress is gated and cannot be skipped.

### M3 art/runtime direction

The three playable operators now have separate original high-resolution master art and separate **2048×2048 layered SVG rig sheets**. The shared Skeleton2D names are only infrastructure; visible art and motion personality are identity-specific.

- **ASTER** — narrow forward precision silhouette, comet ponytail, asymmetric shoulder, coil AR; fast restrained gait and sharp recoil recovery.
- **ROOK** — broad weighted mantle/gauntlet silhouette, magnetic scattergun; heel-heavy gait and deep full-torso recoil.
- **MICA** — long tech coat, sensor fins, side braid, circular-emitter carbine; glide-like locomotion and delayed secondary motion.

Stage 01 authored enemies also use unique high-resolution layered rigs rather than recolored target dummies:
- Site-7 Rifle Trooper
- Site-7 Shield Breacher
- Site-7 Recon Drone
- Site-7 Aberrant Runner
- Signal Anchor Guardian boss

The drone, aberrant and boss are not forced through a reused humanoid rig. Each has its own articulated hierarchy and movement grammar.

### Unique combat feedback

Projectile geometry, muzzle/fire identity, hit VFX and fire/impact SFX profiles are also unique per actor/enemy identity. Changing only color, pitch or EQ is forbidden by the M3 production contract.

`tools/validate_unique_art.py` rejects reused profile IDs, reused final paths and byte-identical master/rig assets via SHA-256 checks.

### Stage 01 authored encounter identities

1. Outer Gate — EVENT
2. Decon Corridor — Rifle Trooper + Recon Drone + Aberrant Runner
3. Archive Annex — RESEARCH
4. Containment Junction — Shield Breacher + Rifle support
5. Containment Core C — Signal Anchor Guardian
6. Emergency Lift — EXTRACTION

Optional: Emergency Stores and Signal Lab.

Current field controls: **WASD move · Shift run · mouse aim · LMB fire · R reload · Space evade · 1/2/3 swap · F interact**.

Enemy projectiles now damage operator health and trigger hit feedback. A downed controlled operator yields control to another living squad member.

## Frozen architecture rules

1. `project.godot` remains at repository root; a nested `game/` wrapper is forbidden.
2. Field traversal and combat use the same operator actor.
3. Movement and aim are independent.
4. Story/mission authority is data-driven under `data/story` and `data/missions`.
5. Required story rooms resolve in authored order.
6. **Systems may be shared; visible/audible final identity assets may not be reused across characters, enemy archetypes or bosses.**
7. Every combat identity owns unique visual, motion, projectile, hit-VFX, fire-SFX and impact-SFX profiles.
8. Master art and layered rig sheets are checked for byte-identical reuse.
9. Gameplay code authors damage/results; animation/VFX remain presentation.
10. CI uses exact SHA-pinned Godot 4.7.2 and retains M1/M2/M3 smoke coverage.
11. GitHub Pages/public deployment remains intentionally disabled until the game is complete.

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — animated combat prototype
- `docs/M2_STORY_VERTICAL_SLICE.md` — lobby/story-stage loop
- `docs/M3_UNIQUE_2P5D_ART_BIBLE.md` — non-reuse production art rules
- `docs/M3_HIGH_RES_UNIQUE_ART_RUNTIME.md` — implemented M3 runtime/art milestone
- `docs/ANIMATION_SPEC_v0.1.md` — animation contract
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data architecture
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI/external resource policy
