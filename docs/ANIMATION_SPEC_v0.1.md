# SABLE CIRCUIT — Animation Specification v0.1

## Goal
3–4-head-tall operators must visibly locomote and fight in both map traversal and combat. There is no static map token substitute.

## Character visual contract

Every playable character uses a direction-compatible rig naming contract. Recommended semantic bones/parts:
- root / pelvis / torso
- head / hair_front / hair_back
- upper_arm_L/R / lower_arm_L/R / hand_L/R
- thigh_L/R / shin_L/R / foot_L/R
- weapon_root / weapon_support
- optional accessory bones
- muzzle_socket / hand_support_socket / fx_root

Exact visual decomposition may vary, but semantic sockets cannot vary arbitrarily across characters.

## Direction policy

### Exploration
Facing follows last meaningful movement direction. Eight visual sectors are supported.

### Combat
Facing is driven primarily by aim direction. Movement animation is calculated relative to aim:
- forward
- backpedal
- strafe left
- strafe right
- diagonals are blended/interpreted between those bases

When aim crosses a facing-sector threshold, the direction presentation switches/crossfades without changing world-space aim.

## Minimum operator clip set

### Traversal
IdleExplore, Walk, Run, StartMove, StopMove, Turn, Interact, Pickup.

### Combat
CombatIdle, Aim, MoveForward, StrafeL, StrafeR, Backpedal, FireSingle, FireBurst, Reload, Evade, Skill1, Skill2, Ultimate, HitLight, HitHeavy, Knockback, Downed, Revive, Extract.

### Quality gates
- feet do not visibly slide at nominal movement speeds
- weapon muzzle follows authoritative muzzle socket
- support hand does not visibly detach from two-handed weapons except during authored reload/skill states
- aim and projectile direction agree within defined tolerance
- no torso-only aiming that leaves arms/weapon disconnected
- no invalid limb stretching during sector changes
- hit/evade/ultimate full-body overrides cannot mix with incompatible locomotion layers

## Animation runtime inputs

The controller exposes at minimum:
- `speed_norm`
- `move_world`
- `aim_world`
- `move_relative`
- `facing_sector`
- `is_combat`
- `is_grounded` (reserved if verticality is later added)
- `fire_request`
- `reload_request`
- `skill_request`
- `hit_request`

## MVP animation acceptance test

A test arena must demonstrate, for all 3 MVP operators:
1. idle → walk → run → stop
2. full 360° movement with valid facing sectors
3. aim held right while moving left/right/forward/back
4. continuous fire while strafing where weapon permits
5. reload while stationary and while permitted locomotion continues
6. evade cancels/blocks incompatible fire state
7. swap player control between all three operators without visual reset
8. down/revive sequence
9. interaction and extraction sequence
