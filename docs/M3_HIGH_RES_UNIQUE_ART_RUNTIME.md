# M3 — High-Resolution Unique 2.5D Art Runtime

## Goal
Replace shared-looking prototype presentation with production-direction art architecture where every playable identity and enemy archetype owns a unique visible and audible combat identity.

## Implemented playable identities
- ASTER — precision/velocity silhouette, comet hair, asymmetric shoulder, coil rifle
- ROOK — broad weighted silhouette, mantle, heavy gauntlet, magnetic scattergun
- MICA — long coat, sensor fins, side braid, circular-emitter carbine

Each owns:
- a unique full-resolution master SVG
- a unique 2048×2048 layered SVG rig sheet
- a unique motion profile
- projectile geometry/signature
- hit VFX profile
- fire SFX profile
- impact SFX profile

The runtime `OperatorVisual` retains a common semantic Skeleton2D contract but uses different high-resolution SVG layers and different authored motion coefficients. Shared bones are infrastructure, not reused visual content.

## Implemented enemy identities
- Site-7 Rifle Trooper — human tactical strafe/burst rig
- Site-7 Shield Breacher — asymmetric shield/hydraulic elite rig
- Site-7 Recon Drone — non-humanoid hover/sensor/thruster rig
- Site-7 Aberrant Runner — organic skull/forelimb/tail rig
- Signal Anchor Guardian — non-humanoid ring/iris/four-arm/pylon boss rig

All five use separate master art and separate rig sheets. No normal-enemy body is reused for the boss.

## Chapter 01 integration
StoryStage01 encounter authority now comes from `MIS_CH01_01.json`:
- Decon Corridor: Rifle Trooper + Recon Drone + Aberrant Runner
- Containment Junction: Shield Breacher + Rifle support
- Core C: Signal Anchor Guardian only

The stage no longer uses recolored target dummies for authored encounters. `TargetDummy` remains only as an isolated M1 regression fixture.

## Combat feedback identity
`prototype_projectile.gd`, `combat_hit_vfx.gd` and `procedural_combat_sfx.gd` route feedback by identity profile.

Examples:
- ASTER: segmented cyan needle / prism split / short coil snap
- ROOK: spread amber chunks / pressure-ring crush / low chamber impact
- MICA: hollow telemetry pulse / hex scan bloom / sonar-like electronic shot
- Rifle Trooper: broken red-white tracer / small metal fork / dry mechanical crack
- Shield Breacher: blocky brass slug / angled plate scrape / piston-heavy report
- Recon Drone: dotted magenta packets / cyan arc discharge / high servo-laser chirp
- Aberrant: violet bio glob / membrane tear / wet fibrous impact
- Anchor Guardian: wide rift lance / iris rupture / layered spatial crack

The current synthesized SFX are identity-specific runtime proof assets. Their profile IDs are permanent contracts; final produced audio may replace the synthesis but may not collapse identities into shared samples or pitch/EQ-only variants.

## Player damage loop
Enemy projectiles target the `operators` group. Operators now expose health, high-resolution hit flash response and downed state. If the controlled operator goes down, SquadController transfers control to another living operator.

## Anti-reuse enforcement
`tools/validate_unique_art.py` checks:
- unique master-art paths and SHA-256 hashes
- unique rig-sheet paths and SHA-256 hashes
- unique visual/motion/projectile/hit-VFX/fire-SFX/impact-SFX IDs
- unique identity signature strings
- presence/importability of all declared assets

`tools/validate_project.py` freezes the exact Chapter 01 enemy composition and M3 runtime file set.

## M3 acceptance gate
M3 is acceptable only when GitHub Actions passes all of the following on the exact branch/main commit:
1. repository contract
2. unique-art SHA/profile validation
3. Godot 4.7.2 headless import/parse including all SVGs
4. M1 combat regression smoke
5. M2 story-flow regression smoke
6. M3 unique-art smoke:
   - all 8 identities load unique art/profile assets
   - playable characters render 15+ high-resolution articulated SVG layers
   - enemies render multi-layer identity-specific Skeleton2D rigs
   - enemy profile projectile damages operator health
   - StoryStage01 spawns the authored distinct normal/elite/boss sets

## Still later
M3 establishes the high-resolution 2.5D production architecture and first unique assets. Further polish can add more authored facial animation, direction-specific perspective redraws, richer secondary deformation, dedicated production sound recordings, environment art, VFX texture atlases and boss phase animation without weakening the no-reuse rule.
