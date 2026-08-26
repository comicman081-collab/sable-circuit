# SABLE CIRCUIT

**Status:** M2 lobby + story-stage vertical slice  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable flow

The game now starts at a real title screen and runs through the first authored story loop:

**TITLE → OPERATIONS BASE → CH01 BRIEFING → STORY STAGE 01 → RESULTS → OPERATIONS BASE**

The Operations Base contains Command, Armory and Lab facility panels, the current ASTER / ROOK / MICA squad and the Chapter 01 mission card.

Chapter 01 is **BLACKOUT AT SITE-7**. Its first mission uses six required story rooms in fixed narrative order plus two optional side rooms. Progression is gated by interaction or combat completion, so later rooms cannot be completed out of order.

### Stage 01 route

1. Outer Gate — EVENT
2. Decon Corridor — COMBAT
3. Archive Annex — RESEARCH
4. Containment Junction — ELITE
5. Containment Core C — BOSS
6. Emergency Lift — EXTRACTION

Optional: Emergency Stores and Signal Lab.

The three M1 **3–4-head-tall animated operators** remain the same runtime actors for map traversal and combat. One is directly controlled, two use companion formation AI, and control can be swapped instantly with 1/2/3.

Current field controls: **WASD move · Shift run · mouse aim · LMB fire · R reload · Space evade · 1/2/3 swap · F interact**.

Every prototype operator contains a `Skeleton2D`/`Bone2D` semantic rig, `AnimationPlayer`, active `AnimationTree`, coherent arm/weapon aiming, muzzle socket, locomotion motion, recoil and reload presentation. Current body parts and environment geometry remain engine-native placeholder art.

## Frozen architecture rules

1. `project.godot` remains at repository root; a nested `game/` wrapper is forbidden.
2. Field traversal and combat use the same operator actor.
3. Movement and aim are independent; locomotion continues while aim tracks another direction.
4. Story/mission authority is data-driven JSON under `data/story` and `data/missions`.
5. Required story rooms resolve in authored order; optional rooms may branch without bypassing required gates.
6. Gameplay code authors damage/results; VFX and animation do not.
7. External resources require source/version/license/destination/SHA-256 metadata.
8. CI uses the exact SHA-pinned Godot 4.7.2 editor and runs M1 combat plus M2 story-flow headless smoke tests.
9. GitHub Pages/public deployment remains intentionally disabled.

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data/AI/save architecture
- `docs/ANIMATION_SPEC_v0.1.md` — operator animation contract
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — animated 3-operator combat milestone
- `docs/M2_STORY_VERTICAL_SLICE.md` — title/lobby/story-stage/result vertical slice
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI and external-resource policy
