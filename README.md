# SABLE CIRCUIT

**Status:** M1 playable squad prototype  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable milestone

The repository now boots directly into an internal prototype arena with three **3–4-head-tall animated operators**. One operator is player-controlled while two use companion formation AI; control can be swapped instantly with 1/2/3.

Current controls: **WASD move · Shift run · mouse aim · LMB fire · R reload · Space evade · 1/2/3 swap**.

Every prototype operator uses the same runtime actor for traversal and combat and contains a `Skeleton2D`/`Bone2D` semantic rig, `AnimationPlayer`, active `AnimationTree`, coherent arm/weapon aiming, muzzle socket, locomotion motion, recoil and reload presentation. The current body parts are engine-native placeholder polygons, not production artwork.

## Frozen architecture rules

1. `project.godot` remains at repository root; a nested `game/` wrapper is forbidden.
2. Field traversal and combat use the same operator actor.
3. Movement and aim are independent; locomotion continues while aim tracks another direction.
4. Gameplay code authors damage/results; VFX and animation do not.
5. External resources require source/version/license/destination/SHA-256 metadata.
6. CI uses the exact SHA-pinned Godot 4.7.2 editor and runs real headless smoke tests.
7. GitHub Pages/public deployment remains intentionally disabled.

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data/AI/save architecture
- `docs/ANIMATION_SPEC_v0.1.md` — operator animation contract
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — implemented playable milestone and acceptance gates
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI and external-resource policy
