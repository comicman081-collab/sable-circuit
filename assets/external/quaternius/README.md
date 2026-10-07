# Quaternius Universal Animation Libraries

This directory contains only the free Standard animation-library deliverables
approved for SABLE CIRCUIT. Existing SABLE characters (including ASTER, ROOK,
and MICA) and the existing gameplay/animation logic are unchanged.

## License and upstream verification

- Creator: Quaternius
- Official UAL1 page: https://quaternius.com/packs/universalanimationlibrary.html
- Official UAL2 page: https://quaternius.com/packs/universalanimationlibrary2.html
- Official UAL1 download page: https://quaternius.itch.io/universal-animation-library
- Official UAL2 download page: https://quaternius.itch.io/universal-animation-library-2
- License authority: https://quaternius.com/faq.html and https://creativecommons.org/publicdomain/zero/1.0/
- Download date: 2026-08-28 (Asia/Seoul)
- Tier: FREE / Standard only
- License: CC0 1.0
- Commercial game use: allowed
- Modification: allowed
- Redistribution/bundling with the game: allowed
- Attribution: not required by the creator's FAQ, although this record names Quaternius

The official pages distinguish the free Standard archive from paid Pro/Source
archives. No mirror was used, so a Git commit SHA is not applicable. Instead,
each item is pinned to its official itch.io upload ID and archive SHA-256 in
`assets/external/manifest.json`.

The downloaded Standard archives were used as transient source packages only.
The official archive's preview mannequin/mesh data was not retained. Each GLB
below is an animation-only derivative: the animation accessors and target node
hierarchy remain, while mesh, material, and texture data are removed. The
technical skin/joint metadata is retained only so Godot can recognize a
Skeleton3D; no character geometry is stored.

## UAL1 — Universal Animation Library

- Official version/changelog: v3.0; the official changelog records root motion
  added to locomotion/movement in v3.0.
- Official Standard upload: `17958403`
- Archive: `Universal Animation Library[Standard].zip`
- Archive size: `15,904,933` bytes
- Archive SHA-256: `CC73FC4E495B82958207316596317A3F40B9FA38065BDE1027937452DA537724`
- Source GLB entry: `Unreal-Godot/UAL1_Standard.glb` (the `_RM` entry is its
  root-motion counterpart)
- Animation count: 43 in each form

| File | Root motion | Size | SHA-256 | Git blob SHA-1 |
| --- | --- | ---: | --- | --- |
| `ual1/UAL1_Standard.glb` | disabled / in-place | 7,018,888 | `d68996d486d8d08cad5d603932d42fab6de9eddb19640e6a9ff9fdf92c8fca15` | `8cfb6cc05ec35ca48b177165d0eebd6851ed9a57` |
| `ual1/UAL1_Standard_RM.glb` | baked root motion | 7,020,956 | `3c45746c9dc9831f61a42af6b1d5c6fbebf9deb23c1a8991c8456958143cb0da` | `a31887ff12a11e9f6a5417db74efcebe16ed1ec0` |

Actual animation names:

`A_TPose`, `Crouch_Fwd_Loop`, `Crouch_Idle_Loop`, `Dance_Loop`, `Death01`,
`Driving_Loop`, `Fixing_Kneeling`, `Hit_Chest`, `Hit_Head`, `Idle_Loop`,
`Idle_Talking_Loop`, `Idle_Torch_Loop`, `Interact`, `Jog_Fwd_Loop`,
`Jump_Land`, `Jump_Loop`, `Jump_Start`, `PickUp_Table`, `Pistol_Aim_Down`,
`Pistol_Aim_Neutral`, `Pistol_Aim_Up`, `Pistol_Idle_Loop`, `Pistol_Reload`,
`Pistol_Shoot`, `Punch_Cross`, `Punch_Jab`, `Push_Loop`, `Roll`,
`Sitting_Enter`, `Sitting_Exit`, `Sitting_Idle_Loop`, `Sitting_Talking_Loop`,
`Spell_Simple_Enter`, `Spell_Simple_Exit`, `Spell_Simple_Idle_Loop`,
`Spell_Simple_Shoot`, `Sprint_Loop`, `Swim_Fwd_Loop`, `Swim_Idle_Loop`,
`Sword_Attack`, `Sword_Idle`, `Walk_Formal_Loop`, `Walk_Loop`

Godot 4.7.2 import result (same for the `_RM` file; Godot normalizes some
`_Loop` suffixes): 43 animations and 1 `Skeleton3D`.

`A_TPose`, `Crouch_Fwd`, `Crouch_Idle`, `Dance`, `Death01`, `Driving`,
`Fixing_Kneeling`, `Hit_Chest`, `Hit_Head`, `Idle`, `Idle_Talking`,
`Idle_Torch`, `Interact`, `Jog_Fwd`, `Jump`, `Jump_Land`, `Jump_Start`,
`PickUp_Table`, `Pistol_Aim_Down`, `Pistol_Aim_Neutral`, `Pistol_Aim_Up`,
`Pistol_Idle`, `Pistol_Reload`, `Pistol_Shoot`, `Punch_Cross`, `Punch_Jab`,
`Push`, `Roll`, `Sitting_Enter`, `Sitting_Exit`, `Sitting_Idle`,
`Sitting_Talking`, `Spell_Simple_Enter`, `Spell_Simple_Exit`,
`Spell_Simple_Idle`, `Spell_Simple_Shoot`, `Sprint`, `Swim_Fwd`,
`Swim_Idle`, `Sword_Attack`, `Sword_Idle`, `Walk`, `Walk_Formal`

Observed categories from the names above:

- idle: `Crouch_Idle_Loop`, `Idle_Loop`, `Idle_Talking_Loop`,
  `Idle_Torch_Loop`, `Pistol_Idle_Loop`, `Sitting_Idle_Loop`,
  `Spell_Simple_Idle_Loop`, `Swim_Idle_Loop`, `Sword_Idle`
- walk: `Crouch_Fwd_Loop`, `Walk_Formal_Loop`, `Walk_Loop`
- run: `Jog_Fwd_Loop`, `Sprint_Loop`
- strafe: none present
- crouch: `Crouch_Fwd_Loop`, `Crouch_Idle_Loop`
- jump: `Jump_Land`, `Jump_Loop`, `Jump_Start`
- dodge / roll: `Roll`
- hit / reaction: `Hit_Chest`, `Hit_Head`
- death: `Death01`
- melee: `Punch_Cross`, `Punch_Jab`, `Sword_Attack`
- combat: `Pistol_Aim_Down`, `Pistol_Aim_Neutral`, `Pistol_Aim_Up`,
  `Pistol_Reload`, `Pistol_Shoot`, `Punch_Cross`, `Punch_Jab`,
  `Sword_Attack`
- weapon-related: `Pistol_*`, `Sword_Attack`, `Sword_Idle`
- parkour: none present
- other: `A_TPose`, `Dance_Loop`, `Driving_Loop`, `Fixing_Kneeling`,
  `Interact`, `PickUp_Table`, `Push_Loop`, `Sitting_*`, `Spell_Simple_*`,
  `Swim_Fwd_Loop`

## UAL2 — Universal Animation Library 2

- Official version/changelog: v2.1; the official changelog records the `Fall`
  animation rename in v2.1 to avoid a duplicate Godot warning. The current
  Standard GLB is post-fix: its parsed names contain no `Fall` entry and no
  duplicate animation names.
- Official Standard upload: `17958478`
- Archive: `Universal Animation Library 2[Standard].zip`
- Archive size: `18,735,003` bytes
- Archive SHA-256: `4008EA208A604773A2B2177D965F0F5D3195498B5BF838C3F5785D68E95F2A68`
- Source GLB entry: `Unreal-Godot/UAL2_Standard.glb` (the `_RM` entry is its
  root-motion counterpart)
- Animation count: 43 in each form

| File | Root motion | Size | SHA-256 | Git blob SHA-1 |
| --- | --- | ---: | --- | --- |
| `ual2/UAL2_Standard.glb` | disabled / in-place | 7,490,888 | `74000de9d6f4f7b45f7a2f857159a3a5214d40b121d06f2b09581d5345aa3b33` | `cb63d084e1f7dbddbadbbe040c201c04a2e44483` |
| `ual2/UAL2_Standard_RM.glb` | baked root motion | 7,495,380 | `ba33e14d974f8df697c69738b1772e9c1d0eb62b278d4b6c71ef3955844128f8` | `64ccbca3d7e906b543c5f7f0773a84368e4b5de6` |

Actual animation names:

`A_TPose`, `Chest_Open`, `ClimbUp_1m`, `Consume`, `Farm_Harvest`,
`Farm_PlantSeed`, `Farm_Watering`, `Hit_Knockback`, `Idle_FoldArms_Loop`,
`Idle_Lantern_Loop`, `Idle_No_Loop`, `Idle_Rail_Call`, `Idle_Rail_Loop`,
`Idle_Shield_Break`, `Idle_Shield_Loop`, `Idle_TalkingPhone_Loop`, `LayToIdle`,
`Melee_Hook`, `Melee_Hook_Rec`, `NinjaJump_Idle_Loop`, `NinjaJump_Land`,
`NinjaJump_Start`, `OverhandThrow`, `Shield_Dash`, `Shield_OneShot`,
`Slide_Exit`, `Slide_Loop`, `Slide_Start`, `Sword_Block`, `Sword_Dash`,
`Sword_Heavy_Combo`, `Sword_Regular_A`, `Sword_Regular_A_Rec`,
`Sword_Regular_B`, `Sword_Regular_B_Rec`, `Sword_Regular_C`,
`Sword_Regular_Combo`, `TreeChopping_Loop`, `Walk_Carry_Loop`, `Yes`,
`Zombie_Idle_Loop`, `Zombie_Scratch`, `Zombie_Walk_Fwd_Loop`

Godot 4.7.2 import result (same for the `_RM` file; Godot normalizes some
`_Loop` suffixes): 43 animations and 1 `Skeleton3D`.

`A_TPose`, `Chest_Open`, `ClimbUp_1m`, `Consume`, `Farm_Harvest`,
`Farm_PlantSeed`, `Farm_Watering`, `Hit_Knockback`, `Idle_FoldArms`,
`Idle_Lantern`, `Idle_No`, `Idle_Rail`, `Idle_Rail_Call`, `Idle_Shield`,
`Idle_Shield_Break`, `Idle_TalkingPhone`, `LayToIdle`, `Melee_Hook`,
`Melee_Hook_Rec`, `NinjaJump_Idle`, `NinjaJump_Land`, `NinjaJump_Start`,
`OverhandThrow`, `Shield_Dash`, `Shield_OneShot`, `Slide`, `Slide_Exit`,
`Slide_Start`, `Sword_Block`, `Sword_Dash`, `Sword_Heavy_Combo`,
`Sword_Regular_A`, `Sword_Regular_A_Rec`, `Sword_Regular_B`,
`Sword_Regular_B_Rec`, `Sword_Regular_C`, `Sword_Regular_Combo`,
`TreeChopping`, `Walk_Carry`, `Yes`, `Zombie_Idle`, `Zombie_Scratch`,
`Zombie_Walk_Fwd`

Observed categories from the names above:

- idle: `Idle_FoldArms_Loop`, `Idle_Lantern_Loop`, `Idle_No_Loop`,
  `Idle_Rail_Call`, `Idle_Rail_Loop`, `Idle_Shield_Break`,
  `Idle_Shield_Loop`, `Idle_TalkingPhone_Loop`, `NinjaJump_Idle_Loop`,
  `Zombie_Idle_Loop`
- walk: `Walk_Carry_Loop`, `Zombie_Walk_Fwd_Loop`
- run: none present
- strafe: none present
- crouch: none present
- jump: `NinjaJump_Idle_Loop`, `NinjaJump_Land`, `NinjaJump_Start`
- dodge / roll: none present
- hit / reaction: `Hit_Knockback`, `Melee_Hook_Rec`, `Sword_Regular_A_Rec`,
  `Sword_Regular_B_Rec`
- death: none present
- melee: `Melee_Hook`, `Melee_Hook_Rec`, `Sword_Regular_A`,
  `Sword_Regular_A_Rec`, `Sword_Regular_B`, `Sword_Regular_B_Rec`,
  `Sword_Regular_C`, `Sword_Regular_Combo`, `Sword_Heavy_Combo`
- combat: `Hit_Knockback`, `OverhandThrow`, `Shield_Dash`, `Shield_OneShot`,
  `Sword_Block`, `Sword_Dash`, `Sword_Heavy_Combo`, `Sword_Regular_*`
- weapon-related: `Shield_*`, `Sword_*`, `OverhandThrow`
- parkour: `ClimbUp_1m`, `Slide_Exit`, `Slide_Loop`, `Slide_Start`
- other: `A_TPose`, `Chest_Open`, `Consume`, `Farm_*`, `LayToIdle`, `Yes`,
  `TreeChopping_Loop`, `Zombie_Scratch`

## Exclusion gate

Universal Base Characters were not used. No Universal Base Characters,
mannequin files, character/base-model files, textures, hair/face models, Pro,
Source, Premium, paid, Patreon-only, `.blend`, or FBX files are stored in this
directory. The UAL2 Standard archive did contain a `Female Mannequin` preview
folder; it was explicitly skipped and was not copied to the project.

The assets are prepared as an animation source only. No retargeting, existing
character replacement, gameplay change, combat-timing change, save/data change,
main-branch merge, or deployment was performed.
