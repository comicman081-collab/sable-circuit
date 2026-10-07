# M2 — Lobby + Story Stage Vertical Slice

## Runtime flow

`TITLE → OPERATIONS BASE → CH01 BRIEFING → STORY STAGE 01 → RESULTS → OPERATIONS BASE`

The game no longer boots directly into the M1 combat sandbox. `Bootstrap.tscn` creates a persistent `GameFlow`, and the initial active view is `TitleScreen.tscn`.

## Operations Base lobby

The M2 lobby is `scenes/base/BaseLobby.tscn` and contains three MVP facilities:

- **COMMAND** — mission/story/zone routing.
- **ARMORY** — loadout presentation for ASTER / ROOK / MICA.
- **LAB** — recovered signal/sample analysis presentation.

The lobby also presents the active three-operator squad and Chapter 01 mission card.

## Chapter 01 — BLACKOUT AT SITE-7

Scenario authority: `data/story/chapter_01.json`.

A sealed research site stops transmitting after a containment alarm. The team must recover the missing personnel ledger, identify the source of an unknown carrier signal and extract before auxiliary power collapses.

Pre-deployment briefing includes authored dialogue for COMMAND, MICA, ROOK and ASTER. Mission results include a short post-operation story beat that reveals the blackout originated inside Containment Core C and that the carrier signal remains active.

## Stage 01 authored route

Mission authority: `data/missions/MIS_CH01_01.json`.

Main route is fixed in scenario order:

1. **Outer Gate** — EVENT / interact.
2. **Decon Corridor** — COMBAT.
3. **Archive Annex** — RESEARCH / recover story-critical ledger.
4. **Containment Junction** — ELITE combat.
5. **Containment Core C** — BOSS / signal anchor.
6. **Emergency Lift** — EXTRACTION / interact.

Optional side rooms:

- **Emergency Stores** — optional field-supply recovery.
- **Signal Lab** — optional carrier-fragment recovery and story clue.

## Progression authority

The stage does not allow progression to be completed out of order. Operator movement bounds expand as each required story room is resolved. Combat rooms unlock only after every spawned hostile is defeated. EVENT / RESEARCH / EXTRACTION rooms require explicit `F` interaction.

Optional rooms do not gate the main route, but their recovered state changes the result summary and secured research value.

## Integration with M1 combat

The three animated M1 operators remain the field and combat actors. No scene swap creates replacement battle units.

Story-stage enemies use the existing prototype target actor with persistent defeat enabled. The M1 sandbox retains reset-on-zero behavior for regression testing.

## CI acceptance

`tests/smoke/m2_story_flow_smoke.gd` verifies:

- scenario and mission JSON exist and parse;
- main route is exactly six ordered room types;
- two optional rooms exist;
- boot state is TITLE, not PrototypeArena;
- Title → Base → Briefing → Stage transition;
- StoryStage01 deploys all three operators;
- stage runtime loads 6 main + 2 optional rooms;
- completing a story step expands movement bounds;
- result summary preserves story-critical and optional recovery state;
- Results returns to Base.

The existing M1 combat/skeleton smoke remains mandatory and must also pass.

## Still out of scope

- production lobby/environment art;
- final enemy art and tactical enemy AI;
- full character skill/ultimate gameplay;
- permanent save/meta upgrade economy;
- Chapters 02+;
- Web export and GitHub Pages deployment.
