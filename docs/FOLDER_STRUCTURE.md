# Repository Folder Structure — Frozen Through M3

The machine-readable authority is `schemas/repository_layout.json`. `project.godot` remains at repository root.

```text
sable-circuit/
├─ project.godot
├─ .github/workflows/validate.yml
├─ assets/
│  ├─ characters/
│  │  ├─ common_rig/             # semantic/system references only; no shared final skins
│  │  └─ playable/
│  │     ├─ aster/{aster_master.svg,aster_rig_sheet.svg}
│  │     ├─ rook/{rook_master.svg,rook_rig_sheet.svg}
│  │     └─ mica/{mica_master.svg,mica_rig_sheet.svg}
│  ├─ enemies/
│  │  ├─ rifle_trooper/{rifle_trooper_master.svg,rifle_trooper_rig_sheet.svg}
│  │  ├─ shield_breacher/{shield_breacher_master.svg,shield_breacher_rig_sheet.svg}
│  │  ├─ recon_drone/{recon_drone_master.svg,recon_drone_rig_sheet.svg}
│  │  ├─ aberrant_melee/{aberrant_melee_master.svg,aberrant_melee_rig_sheet.svg}
│  │  └─ signal_anchor_guardian/{signal_anchor_guardian_master.svg,signal_anchor_guardian_rig_sheet.svg}
│  ├─ weapons/
│  ├─ environments/
│  ├─ vfx/
│  ├─ ui/
│  ├─ audio/{bgm,sfx,voice}/
│  ├─ fonts/
│  └─ external/manifest.json
├─ data/
│  ├─ art_profiles/              # unique visual/motion/projectile/VFX/SFX identity contracts
│  ├─ characters/
│  ├─ enemies/
│  ├─ weapons/
│  ├─ skills/
│  ├─ missions/                  # authored stage graph + exact encounter identities
│  ├─ story/
│  ├─ loot/
│  ├─ progression/
│  └─ localization/
├─ scenes/
│  ├─ bootstrap/
│  ├─ base/
│  ├─ mission/
│  ├─ story/
│  ├─ actors/{player,companion,enemy}/
│  ├─ world/
│  └─ ui/
├─ scripts/
│  ├─ core/
│  ├─ actors/
│  ├─ animation/
│  ├─ combat/
│  ├─ vfx/                       # identity-routed hit presentation
│  ├─ audio/                     # identity-routed combat sound presentation
│  ├─ ai/
│  ├─ navigation/
│  ├─ missions/
│  ├─ meta/
│  ├─ save/
│  ├─ ui/
│  └─ data/
├─ schemas/
├─ tests/{unit,integration,smoke}/
├─ tools/
└─ docs/
```

## Ownership rules

- `assets/`: visible/audible runtime content. M3 forbids final identity reuse across characters/enemy archetypes/bosses.
- `data/art_profiles/`: maps every combat identity to its own visual, motion, projectile, hit-VFX, fire-SFX and impact-SFX contract.
- `data/missions/`: stage topology and exact authored encounter composition.
- `data/story/`: narrative/briefing authority.
- `scripts/animation/`, `scripts/vfx/`, `scripts/audio/`: shared systems are allowed; their outputs are driven by unique identity data.
- `tools/validate_unique_art.py`: rejects reused profile IDs, paths and byte-identical master/rig assets.
- `schemas/repository_layout.json`: machine-readable directory authority.

The earlier nested `game/` wrapper remains forbidden. Public Pages/deployment workflows remain forbidden until explicit completion approval.
