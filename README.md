# SABLE CIRCUIT

**Status:** Pre-production / repository baseline v0.1  
**Engine:** Godot 4.7.2 stable · GDScript · Compatibility renderer  
**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Core promise

SABLE CIRCUIT is built around fully animated **3–4-head-tall operators** using the **same runtime actor for field traversal and combat**. Characters walk, run, turn, strafe, backpedal, aim, fire, reload, evade, use skills, interact, get hit, go down, revive and extract without changing into a static map token or a separate battle-only representation.

Movement and aim are independent: the lower body follows locomotion while facing/upper-body combat presentation follows the aim vector through a coherent torso–arm–hand–weapon chain.

## Baseline decisions

1. `project.godot` is at repository root; a nested `game/` wrapper is forbidden.
2. Three operators deploy together; one is directly controlled and can be swapped instantly.
3. Field traversal and combat happen in the same mission space.
4. Gameplay authority is data-driven and auditable; visuals do not author damage results.
5. External resources fetched by CI require explicit source/version/license/destination/SHA-256 metadata.
6. CI validates repository structure and performs a **real pinned Godot 4.7.2 headless import/smoke run**.
7. GitHub Pages/public deployment is intentionally disabled during pre-production.

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data/AI/save architecture
- `docs/ANIMATION_SPEC_v0.1.md` — mandatory operator animation contract
- `docs/FOLDER_STRUCTURE.md` — frozen repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI and external-resource policy
- `docs/VALIDATION_REPORT.md` — validation status and remaining risks
