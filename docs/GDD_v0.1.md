# SABLE CIRCUIT — Game Design Document v0.1

## 1. Product definition

**Working/foundation title:** SABLE CIRCUIT  
**Genre:** top-down real-time squad action RPG / extraction roguelite / base progression  
**Perspective:** 2D/2.5D top-down three-quarter view  
**Party:** 3 operators deployed at once; one directly controlled, two AI companions; instant character swap  
**Primary targets:** PC browser first, mobile browser second, native desktop/Android later  
**Engine:** Godot 4.7.2 stable, GDScript, Compatibility renderer

### One-line pitch
Lead a three-operator animated squad into unstable research zones, fight in real time, recover anomalous technology and evidence, decide when to extract, and turn recovered knowledge into permanent tactical growth.

## 2. Design pillars

### P1 — The characters must visibly *play* the game
The 3–4-head-tall characters are not static portraits or map icons. The field actor and combat actor are the same object. Traversal, aiming, fire, reload, evasion, skills, interaction, damage, downed state, revive and extraction are animated.

### P2 — Movement and aim are independent
The player can move one way while aiming another. A character can strafe, retreat while firing, or advance while tracking an off-axis target. This is required both mechanically and visually.

### P3 — Three-character squad synergy
Characters are built around role interaction rather than isolated DPS. Status setup, exploit, protection, energy economy, crowd control, targeting and recovery form team cycles.

### P4 — Extraction creates meaningful risk
A run should repeatedly ask: keep exploring for a better reward, or extract now and secure what was found? Failure must hurt, but must not erase all long-term progress.

### P5 — Discovery feeds progression
Recovered logs, samples and devices are not just collectibles. Analysis reveals enemy weaknesses, mission branches, new modules and story information.

## 3. Player loop

### Base loop
Command → squad selection → loadout → deployment → exploration/combat → loot/intel → extract or push deeper → debrief → research/upgrade/craft → next deployment.

### Field loop
1. Traverse a connected room/zone graph.
2. Detect threats and points of interest.
3. Enter combat in-place, without scene-swapping to a separate battle board.
4. Recover loot, samples, keys or evidence.
5. Resolve a route choice, event or risk gate.
6. Reach an extraction point or continue deeper.

## 4. Direct control

### PC baseline
- WASD: movement
- Mouse: aim
- Left mouse: primary fire
- Space: evade
- Q / E: Skill 1 / Skill 2
- R: reload
- 1 / 2 / 3: switch active operator
- F: interact
- Ultimate: dedicated key after meter requirement

### Mobile baseline
- Left virtual stick: movement
- Right drag/aim region: aim vector
- Fire / evade / skills / swap / interact as explicit touch controls
- Aim assist is configurable and never replaces the underlying aim vector

## 5. Squad roles

MVP roles:
- **Assault:** reliable ranged damage, mark exploit
- **Breach:** close-range disruption, armor/door break
- **Support/Recon hybrid:** scan, shield/recovery, information advantage

Post-MVP roles can expand to Control, Heavy, Specialist and Drone operator.

## 6. Combat model

### Required runtime properties
- fixed physics simulation
- explicit actor state machine
- independent movement vector and aim vector
- weapon fire authority separated from visual muzzle flash
- projectile/hitscan results recorded before cosmetic VFX
- skill effects data-driven
- deterministic-enough encounter debug logs for regression tests

### Example synergy
Recon applies `EXPOSED` → Assault gains weak-point multiplier → Breach consumes `EXPOSED` to stagger armor → staggered target grants squad energy.

## 7. Animation as gameplay

### Exploration states
IdleExplore, Walk, Run, StartMove, StopMove, Turn, Interact, Pickup.

### Combat states
CombatIdle, Aim, RunForward, StrafeLeft, StrafeRight, Backpedal, Fire, BurstFire, Reload, Evade, Skill1, Skill2, Ultimate, HitReact, Knockback, Downed, Revive, Extract.

### Direction model
- Visual facing is quantized into 8 sectors for high-quality 2D presentation.
- Movement remains continuous.
- In combat, facing follows aim; locomotion is selected relative to aim (forward/strafe/backpedal).
- Upper-body fire/reload/skill layers can be filtered over locomotion where the action permits it.
- Direction-specific art can share a bone-name contract, but asymmetrical designs may not be blindly mirrored.

## 8. Mission structure

### MVP environment
One abandoned research complex assembled from 12–15 authored room modules.

### Room families
Combat, Security, Supply, Event, Research, Elite, Extraction, Boss.

### Encounter escalation
Patrol → alerted pack → elite modifier → zone hazard → boss/optional deep objective.

## 9. Extraction rules

- Common recovered resources: mostly retained on failure.
- Run-only tactical boosts: always lost after run.
- High-value unsecured loot: lost or partially lost on wipe.
- Story-critical evidence: policy is explicit per item, never silently discarded.
- Extraction secures all currently carried loot and commits run progress transactionally.

## 10. Base facilities

MVP:
1. **Command** — mission selection, story, zone access.
2. **Armory** — weapons/modules/loadouts.
3. **Lab** — analyze samples, unlock weaknesses and research.

Post-MVP:
4. Barracks — character progression.
5. Workshop — craft consumables, drones and special ammo.

## 11. MVP scope

### Playable
3 operators, each with unique primary weapon class, passive, Skill 1, Skill 2 and Ultimate.

### Weapons
2 AR, 1 SMG, 1 shotgun, 1 LMG, 1 launcher/special weapon.

### Enemies
6 normal archetypes, 2 elites, 1 boss.

### Content
1 research-complex tileset, 12–15 room modules, 1 extraction ruleset, 1 story slice.

### Acceptance target
A player can start at base, deploy three animated operators, explore continuously, fight, swap characters, collect loot, choose to extract, return to base and spend recovered resources without debug intervention.

## 12. Explicit non-goals for MVP

- PvP / networking
- open world
- dozens of characters
- procedural animation generation at runtime
- native monetization/gacha
- live service backend
- separate combat scene transition
- full voice acting

## 13. Expansion path

After vertical slice validation: additional zones, 6–9 operators, more enemy factions, research branches, relationship/story scenes, difficulty modifiers, optional challenge extraction contracts and native Android build.
