# Repository Folder Structure — Frozen Baseline v0.1

The machine-readable authority for the layout is `schemas/repository_layout.json`. Git does not store empty directories, so a frozen directory may not appear in the GitHub tree until it contains its first real file; `.gitkeep` files are intentionally not used as structural authority.

```text
sable-circuit/
├─ project.godot                 # Godot project root (no nested game/ wrapper)
├─ README.md
├─ .gitignore
├─ .gitattributes
├─ .github/
│  └─ workflows/
│     └─ validate.yml            # contract + pinned Godot headless validation
├─ assets/
│  ├─ characters/
│  │  ├─ common_rig/
│  │  └─ playable/
│  ├─ enemies/
│  ├─ weapons/
│  ├─ environments/
│  ├─ vfx/
│  ├─ ui/
│  ├─ audio/{bgm,sfx,voice}/
│  ├─ fonts/
│  └─ external/manifest.json
├─ data/
│  ├─ characters/
│  ├─ enemies/
│  ├─ weapons/
│  ├─ skills/
│  ├─ missions/
│  ├─ loot/
│  ├─ progression/
│  └─ localization/
├─ schemas/
│  └─ repository_layout.json
├─ scenes/
│  ├─ bootstrap/
│  ├─ base/
│  ├─ mission/
│  ├─ actors/{player,companion,enemy}/
│  ├─ world/
│  └─ ui/
├─ scripts/
│  ├─ core/
│  ├─ actors/
│  ├─ animation/
│  ├─ combat/
│  ├─ ai/
│  ├─ navigation/
│  ├─ missions/
│  ├─ meta/
│  ├─ save/
│  ├─ ui/
│  └─ data/
├─ tests/{unit,integration,smoke}/
├─ tools/
└─ docs/
```

## Why this is frozen

The earlier `game/` wrapper proposal was rejected because this repository is one Godot project. Keeping `project.godot` at root simplifies editor opening, `res://` paths, headless CI invocation and export tooling.

## Folder ownership rules

- `assets/`: runtime media, not gameplay authority.
- `data/`: balance/content authority in reviewable text.
- `schemas/`: machine-readable validation contracts.
- `scenes/`: Godot composition.
- `scripts/`: behavior/runtime authority.
- `tests/`: executable regressions only.
- `tools/`: build/import/validation helpers; no hidden gameplay authority.
- `docs/`: design/architecture/production rules.
