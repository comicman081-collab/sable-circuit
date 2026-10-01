# Impact Feel — camera shake and hit-stop

Presentation-only hit feedback. It follows frozen rule 9: animation/VFX are presentation, gameplay code authors results. Nothing in `scripts/vfx/impact_feel.gd` changes damage, health, cooldowns, AI or story state; it only nudges `Camera2D.offset` and briefly scales `Engine.time_scale`.

## Where the numbers come from

**Camera shake** follows the `camera-shake` card of [gongnyang/awesome-ai-motion](https://github.com/gongnyang/awesome-ai-motion) (MIT):

| Card value | Used as |
|---|---|
| 300 ms, 6 px translation (1080p) | defaults at strength 0.5; strength 0..1 spans the card ranges 150–450 ms and 2–10 px |
| decay `exp(-5p)·(1-p)` | `SHAKE_DECAY`, identical envelope |
| y = 4/6 of x, 1.7x y frequency | `SHAKE_Y_RATIO`, `SHAKE_Y_FREQ` |
| 12π phase over 300 ms | `SHAKE_HZ = 20`, so frequency stays 20 Hz at any duration |
| px are 1080p | multiplied by `REF_SCALE = 720/1080` for this 1280×720 project |

Not used: the card's 0.6° rotation (it would need `ignore_rotation = false` on every camera) and its 2% crop margin.

**Hit-stop** is SABLE tuning. The catalog has no hit-stop card; its `stamp-impact` card only contributes the rule "impact once, hold, don't repeat".

## Events

Shake strength maps to px/duration as above. Hit-stop is real time (`Time.get_ticks_usec`), so a freeze always ends even though `Engine.time_scale` drops to 0.05 while it runs.

| Event | Strength | Shake @720p | Duration | Hit-stop |
|---|---|---|---|---|
| ASTER / MICA projectile hit | 0.00 | none | - | - |
| ROOK pellet hit | 0.30 | 2.9 px | 240 ms | 33 ms |
| Rifle shot hit | 0.25 | 2.7 px | 225 ms | - |
| Drone shot hit | 0.20 | 2.4 px | 210 ms | - |
| Aberrant bolt hit | 0.38 | 3.4 px | 264 ms | 38 ms |
| Shield slug hit | 0.45 | 3.7 px | 285 ms | 42 ms |
| Guardian lance hit | 0.65 | 4.8 px | 345 ms | 54 ms |
| Enemy defeated | 0.45 | 3.7 px | 285 ms | 60 ms |
| Shield Breacher defeated | 0.60 | 4.5 px | 330 ms | 80 ms |
| Signal Anchor Guardian defeated | 0.95 | 6.4 px | 435 ms | 120 ms |
| Operator downed | 0.70 | 5.1 px | 360 ms | 90 ms |
| Boss phase 2 | 0.70 | 5.1 px | 360 ms | 60 ms |
| Boss phase 3 | 0.90 | 6.1 px | 420 ms | 60 ms |

Projectile rows are the per-identity `impact_weight` in `PrototypeProjectile._apply_profile_tuning`, applied to hits dealt and hits taken alike. A weight below `HIT_STOP_MIN_WEIGHT` (0.28) never freezes. ASTER and MICA fire too fast for per-hit shake, so their feel comes from kills.

Hooks (all presentation layer):

- `PrototypeProjectile._physics_process` → `ImpactFeel.projectile_hit`
- `PremiumEnemyPresentation._on_defeated` → `ImpactFeel.enemy_defeated`
- `PremiumEnemyPresentation._update_boss_phase` → `ImpactFeel.boss_phase_changed`
- `PremiumOperatorPresentation._on_actor_downed` → `ImpactFeel.operator_downed`

## Safety rules

1. A weaker shake never replaces a stronger live one, so ROOK's five pellets and simultaneous events become one shake.
2. Hit-stop is capped at `HIT_STOP_MAX_SEC` (0.12 s), extends but never stacks, and a `HIT_STOP_COOLDOWN_SEC` (0.10 s) gap follows each freeze so sustained fire cannot lock the game.
3. The camera offset is captured when a shake starts and restored exactly when it ends or the camera changes; `_exit_tree` restores both the offset and `Engine.time_scale`.
4. HUD lives on `CanvasLayer`s and does not shake (card rule: keep text outside the shaking world).

## Switches

```gdscript
ImpactFeel.shake_scale = 0.0        # 0 disables shake, 0..1 scales amplitude
ImpactFeel.hit_stop_enabled = false # disables freezes
```

`tests/render/runtime_capture.gd` turns both off so the 24 evidence frames stay deterministic. There is no in-game settings screen yet; wire these two values to one when options exist.

## Tuning

Change `impact_weight` per projectile identity, or the numbers in `ImpactFeel.enemy_defeated`, `operator_downed` and `boss_phase_changed`. Keep within the card limits: no more than 12 px at 1080p (8 px here) for a routine hit and 400 ms for a non-boss event.

## Verification

```bash
godot --headless --path . --script res://tests/smoke/m6_impact_feel_smoke.gd
```

The smoke test checks amplitude bounds, exact return to rest, stronger-wins stacking, the hit-stop cap, cooldown, both switches, and each gameplay hook (projectile hit, enemy defeat, boss phase 3, operator down). It places enemies beyond ally auto-fire range so only the asserted event fires.
