# SABLE CIRCUIT — Technical Architecture v0.1

## 1. Baseline

- Godot 4.7.2 stable
- GDScript only for web compatibility
- Compatibility renderer / WebGL 2.0 target
- `project.godot` at repository root
- 60 Hz physics target
- Web build is future CI work; Pages deployment is intentionally not enabled yet

## 2. Runtime scene architecture

### Bootstrap
`Bootstrap.tscn`
- App state
- DataRegistry
- SaveService
- AudioService
- SceneRouter
- Debug/telemetry hooks

### Mission runtime
`MissionRuntime.tscn`
- World root
- NavigationRegion2D
- EncounterDirector
- SquadController
- CameraController
- LootDirector
- MissionState
- HUD

### Playable actor
`OperatorActor.tscn`
- CharacterBody2D
- CollisionShape2D
- NavigationAgent2D (AI-controlled companions only when not active)
- ActorStateMachine
- CombatComponent
- WeaponController
- HealthComponent
- SkillController
- InteractionComponent
- VisualRoot
  - DirectionRigController
  - Skeleton2D/visual parts
  - AnimationPlayer
  - AnimationTree
  - WeaponSocket / MuzzleSocket / FX sockets

The same actor scene is used during traversal and combat. Combat toggles state and UI; it does not replace the actor with a second representation.

## 3. Animation architecture

### Why hybrid skeletal 2D
A pure frame-by-frame set explodes with direction × character × weapon × state. A single rotatable cutout looks cheap at large angle changes. The selected compromise is:

- authored 8-sector facing presentation
- common bone-name contract
- Skeleton2D for deform/part motion
- AnimationPlayer stores clips
- AnimationTree blends locomotion and overlays actions
- filtered upper-body layers for firing/reload where valid
- sector switching keeps 2D perspective believable

### Aim/movement decoupling
- `move_vec_world`: continuous movement vector
- `aim_vec_world`: continuous aim vector
- `facing_sector`: 0–7 from aim when in combat, otherwise movement
- `move_relative_to_aim`: forward / back / left / right blend values
- locomotion state is derived from relative movement, not simply from world direction

This directly supports moving left while firing right, backpedaling while tracking a target, and circle-strafing.

### AnimationTree policy
- locomotion: BlendSpace2D or state-machine subgraph
- fire/reload/hit/skills: OneShot or filtered blend layer
- actions that require full-body commitment (evade, knockback, downed, ultimate if authored that way) suppress incompatible upper-body overlays

## 4. Gameplay authority

Visual animation never decides damage. Recommended flow:

Input/AI intent → actor state validation → weapon/skill transaction → hit/projectile authority → gameplay result → event log → animation/VFX/audio response.

Muzzle sockets inform projectile origin, but visual FX do not author hit results.

## 5. Data authority

Source-of-truth balancing/content data is UTF-8 JSON in `/data`, with stable IDs:
- `CHR_*`
- `WPN_*`
- `SKL_*`
- `ENM_*`
- `MIS_*`
- `LOT_*`

Schemas and validators reject duplicate IDs, missing references and invalid numeric ranges before builds.

Godot scenes contain presentation/configuration references but do not become the sole authority for balance tables.

## 6. AI architecture

### Companion AI
- follow formation slot
- preserve minimum spacing
- choose safe fire position
- obey focus target/ping
- avoid blocking player
- use skills from explicit policies, not hidden cheats
- hand off immediately when player swaps into that operator

### Enemy AI
Perception → target selection → tactical state → navigation/attack. NavigationAgent2D is a helper, while encounter authority remains in script-level state machines.

## 7. Mission/world architecture

Rooms are authored scenes with metadata rather than fully random geometry. A mission assembles a validated graph of room modules. This gives replayability without sacrificing encounter composition or navigation reliability.

Room contract:
- entrance/exit sockets
- navigation connectivity
- spawn groups
- cover/obstacle tags
- loot anchors
- interaction anchors
- camera bounds
- encounter metadata

## 8. Save model

- versioned save schema
- write temp → validate → replace canonical save
- run state and permanent meta progression separated
- extraction is a transaction boundary
- migration functions required when schema version changes

## 9. Performance budget direction

Browser-first constraints require conservative 2D effects:
- pooled projectiles/VFX
- capped simultaneous particles
- atlas textures where practical
- compressed OGG for runtime audio
- avoid dynamic 2D lights for every muzzle flash; use additive sprite effects where visually sufficient
- no required native extension/GDExtension for core gameplay

## 10. CI architecture

Phase 0 (enabled now):
- machine-readable repository layout validation
- external asset manifest validation
- accidental Pages workflow guard
- download the exact Godot 4.7.2 Linux editor archive
- verify the frozen SHA-256 before execution
- headless editor import/parse
- headless bootstrap smoke run

Phase 1, after gameplay code starts:
- unit/integration/smoke suites for actor, combat, data and save contracts
- deterministic encounter regression fixtures

Phase 2:
- Web export artifact
- browser smoke test

Phase 3, only when explicitly approved:
- GitHub Pages deployment or other hosting

## 11. Dependency policy

- Prefer built-in Godot systems and official GitHub actions.
- Third-party actions/plugins must be justified and version-pinned.
- External runtime assets are stored in-repo when reasonable.
- Assets fetched by CI require whitelist entry, exact version/origin, license metadata and SHA-256.
- No "latest.zip" style mutable dependency is allowed in reproducible builds.
