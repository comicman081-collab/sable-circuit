# M1 — Playable Squad Prototype

## Scope implemented

This milestone turns the pre-production scaffold into a directly controllable combat sandbox without enabling public deployment.

### Three animated 3–4-head operators
- one shared `OperatorActor.tscn` runtime actor
- three prototype operators: ASTER, ROOK, MICA
- runtime `Skeleton2D` + semantic `Bone2D` hierarchy
- `AnimationPlayer` + active `AnimationTree` nodes are present on every operator
- procedural placeholder locomotion drives pelvis bob, alternating thighs/shins, torso/head counter-motion
- aim drives both arm chains plus `weapon_root`; muzzle follows `muzzle_socket`
- recoil, reload fold and evade deformation are visible runtime states

The placeholder geometry is intentionally engine-native and contains no production art dependency. Production art can replace polygon parts without changing gameplay actor or semantic bone/socket names.

### Player controls
- WASD: move
- Shift: run
- mouse: continuous world-space aim
- left mouse: fire
- R: reload
- Space: evade/dash
- 1/2/3: instant controlled-operator swap

### Three-operator squad
Only one operator receives direct player movement. The other two remain the same actor type, switch to companion AI, maintain a rear-side formation, acquire prototype targets and fire autonomously. Control swaps do not replace or respawn actors.

### Combat sandbox
`PrototypeArena.tscn` provides a grid test floor, visual obstacles, three target dummies, camera tracking, HUD and projectile transactions. Projectiles originate from the visual muzzle socket but damage is authored by projectile/gameplay code rather than VFX.

## Acceptance gates

GitHub Actions must pass:
1. repository contract validator
2. Godot 4.7.2 SHA-pinned editor download/version check
3. headless editor import/parse
4. normal bootstrap headless run
5. `tests/smoke/prototype_smoke.gd`

The prototype smoke verifies:
- exactly 3 operators
- control transfer to operator 3 and back
- `Skeleton2D` with at least 12 registered bones for every operator
- `AnimationPlayer` and active `AnimationTree` for every operator
- muzzle socket presence
- a fire transaction consumes exactly one round
- reload state begins
- exactly 3 target dummies exist

## Deliberately not claimed yet
- production character artwork
- authored eight-sector character art
- final foot-contact animation polish
- cover system
- skill/ultimate gameplay
- enemy tactical AI
- extraction/meta progression
- mobile touch controls
- Web export or Pages deployment
