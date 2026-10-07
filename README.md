# SABLE CIRCUIT

**Status (2026-10-02):** Ten-operation local demo, intro and keyboard/touch controls integrated; unused assets retired and the project committed locally. Not yet published; see `docs/DEMO_20260920.md` for scope.

**Checks:** `python tools/maintenance/run_regression_suite.py` runs the quick suite (44 tests, 7-9 minutes), `--suite full` everything (73 tests, about 90 minutes); results go to `qa/regression_runs/` and existing QA records are guarded. **Playtest:** playing from the project folder writes a balance record per operation to `playtest_logs/` (room time, damage taken by enemy type, downs, revives, skills, hits, kills, extraction choice); F9 shows FPS and live / attacking hostiles.

**Engine:** Godot 4.x · GDScript · Compatibility renderer; this batch verified with installed Godot 4.7.1.

**Genre:** Top-down real-time 3-operator squad action RPG + extraction roguelite + base progression

## Current playable flow

TITLE → INTRO (SKIPPABLE) → OPERATIONS BASE → SELECT OPERATION → BRIEFING → FIELD → RESULTS → REFIT / NEXT OPERATION

Chapter 01 now connects **Blackout at Site-7 → Recovery Sweep → Core Pressure → Forge Descent → Offshore Null → Verdant Lock → Cold Storage → Switchyard → Memory Vault → Zero Point**.
Each operation has six main rooms, two optional rooms and a boss encounter.
All ten operations are playable: operations 6-10 opened one at a time, in
order, once their 15 map plates and boss were in (Zero Point on 2026-10-02),
and clearing Zero Point completes the chapter.
See `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`.
Full extraction unlocks the next operation; early extraction preserves secured
cargo but does not unlock it. Save schema 4 preserves existing upgrades,
equipment and resources. All cleared operations can be replayed.

Current actors use the accepted Motion Studio ASTER / ROOK / MICA at 1.8x scale.
Enemy variety now expands by operation: BULWARK shield crawlers in 1, CINDER
hover rams in 2, and VESPER vertical mortars in 3, mixed with earlier robots.
The reviewed recon drone and fixed anchor remain; humanoid enemies are retired.
Licensed kArchive cover blocks both sides' bullets in all three missions.
See `qa/stage_enemies_20260919/RESULT_KO.md` for current enemy integration and
`qa/campaign_20260919/RESULT_KO.md` for the earlier campaign batch.

Combat feedback: code-drawn hit impacts and hurt reactions, with optional screen
shake on heavy hits (settings). Each operation's elite room adds SHIELDED,
OVERCHARGED or VOLATILE variants of existing robots, marked by a floor ring and
overhead name; from operation 3, ARC VENT floor grates telegraph and then
discharge into operators and robots standing on them. See
`qa/elite_affix_20260925/` and `qa/zone_hazard_20260925/`.

## Historical notes below — not current production authority

The M7 vector, staged-raster and humanoid descriptions below are retained history.
Do not use them to replace current Motion Studio actors or restore retired enemies.

## M7 current runtime baseline

M7 keeps **real Godot GUI rendering** as the visual acceptance authority. AI concepts, isolated mockups and metadata-only asset presence are not implementation evidence.

The current validated runtime adds:
- true eight-sector operator evidence for **ASTER / ROOK / MICA**, with all three operators visible in each direction capture,
- dedicated side-profile and rear identity plates instead of treating a compressed frontal paper-doll as a side/rear view,
- frontal head/torso suppression in exact side and rear sectors so baked facial/chest art cannot leak through,
- normalized profile/rear head scale to prevent visible size pumping during direction changes,
- independent movement and aim with non-accumulating diagonal locomotion offsets,
- target-aware squad camera framing,
- a dedicated **Signal Anchor Guardian** boss camera that remains authoritative while Phase 3 temporarily removes the boss from the combat-target group,
- Phase-3 giant-boss zoom-out (`1.02` versus normal `1.46`) so the boss ring and all four pylons remain inside the 1280×720 safe frame,
- Core C floor-plane telegraphs behind combatants rather than painting over the boss body.

GitHub Actions launches exact SHA-pinned Godot 4.7.2 under Xvfb at 1280×720 and must render exactly **24 PNG evidence frames**:
- traversal / map movement,
- Decon Corridor combat,
- Signal Anchor Guardian Phase 3,
- all eight Stage-01 environment styles,
- eight directional frames with ASTER / ROOK / MICA shown together,
- unique Rifle / Shield / Drone / Aberrant / Boss death frames.

### Authored raster promotion gate

M7 contains a staging loader for future authored 4×2 / eight-direction raster atlases, but **raster is not currently the authoritative live operator presentation**.

Current repository state:
- **ASTER:** staged payload is incomplete — `15,000 / 94,718 bytes` (`15.84%`) and is automatically quarantined before the WebP decoder is invoked.
- **ROOK:** raster atlas payload not present.
- **MICA:** raster atlas payload not present.
- Therefore the validated M7 directional vector/rig presentation remains authoritative for all three operators.

`tools/validate_m7_raster_payloads.py` verifies chunk ordering, base64 integrity and RIFF/WebP declared length. A valid staged prefix may report `PARTIAL_QUARANTINED`; malformed, over-length or broken chunk payloads fail CI. Runtime promotion occurs only after the full RIFF payload is present, WebP decode succeeds and atlas dimensions are valid. Partial raster data can never hide the validated vector fallback.

## M5 foundation retained

M5 established actual-runtime screenshot acceptance, the tactical HUD, pinned typography and Site-7 facility-depth presentation. These remain retained contracts under M7.

### Tactical HUD and typography

The field HUD includes a route minimap, objective panel, live ASTER / ROOK / MICA portrait cards and HP, ammunition / weapon panel, ENERGY and Q/E/R slots.

HUD typography is **Rajdhani Medium v1.201** from pinned Google Fonts revision `9d1ce2fc3c335cca32b6db00c19f55d57b0a68fe`. The font is declared in `assets/external/manifest.json`, fetched through `tools/fetch_external_assets.py`, verified against SHA-256, and licensed under SIL OFL 1.1. CI verifies Godot actually selects the bundled font instead of a system fallback.

### Site-7 2.5D field presentation

The eight unique room identities remain intact with a consistent facility-depth pass:
- raised metallic room shells,
- top / side wall faces,
- deck lips and cast shadows,
- structural braces and luminous insets,
- recessed floor plates and deck seams,
- cinematic edge attenuation, scan texture and subtle cool / amber blooms.

### Operators

All three keep independent high-resolution rigs and art identities:
- **ASTER** — silver/cool ponytail, navy/cyan precision silhouette.
- **ROOK** — white hair, charcoal/bronze heavy silhouette.
- **MICA** — ash-brown braid, dark/teal sensor silhouette.

The live formation is widened for on-field readability. Each operator has contact grounding and the selected operator has a subtle identity-colored control ring.

### Enemy and combat feedback

Every unique enemy keeps its own rig and motion grammar, with contact shadows and segmented overhead health/threat UI.

Projectile and impact presentation remains identity-specific rather than recolored reuse:
- ASTER — precision coil dart,
- ROOK — magnetic pressure wake,
- MICA — sensor pulse packet,
- Rifle — red/white segmented tracer,
- Shield — amber heavy slug,
- Drone — magenta/cyan packet,
- Aberrant — organic purple bolt,
- Signal Anchor Guardian — violet/magenta phase lance.

Associated hit VFX retain separate shapes, timing and motion.

## Premium motion and environment contracts

### Eight-sector character presentation

ASTER / ROOK / MICA resolve all eight facing sectors. Side sectors now use authored profile identity plates; rear sectors use authored rear hair/back-armor identity plates. Arms, legs, weapon sockets and weapon IK remain on the authoritative articulated rig.

Rear-facing sectors contain no baked face. Front-facing sectors restore the authored frontal head and facial micro rig. Forward diagonals retain controlled perspective compression without replacing the authoritative front identity art.

### Identity-specific secondary motion

Hair, coat and accessories use acceleration/aim-turn spring motion:
- ASTER — quick, sharp trailing response.
- ROOK — heavier, strongly damped mantle response.
- MICA — soft long-delay coat/sensor response.

### Unique enemy hit and death presentation

- Rifle Trooper — shoulder/weapon kick + metal fragment tumble.
- Shield Breacher — shield-first recoil + heavy slab collapse.
- Recon Drone — bank/sensor reaction + spiral electronic breakup.
- Aberrant Runner — elastic skull/torso/tail reaction + organic contraction/tear breakup.
- Signal Anchor Guardian — iris/arm reaction + ring/pylon collapse.

Visible death is detached from the authoritative enemy transaction, so destruction can finish after gameplay defeat resolves exactly once.

### Signal Anchor Guardian phases

- **Phase 1:** >66% HP — base orbital behavior.
- **Phase 2:** 34–66% — expanded ring/pylon motion and additional angled lance pattern.
- **Phase 3:** <=33% — unstable iris/arms, increased attack pressure and five-way lance pattern.

Phase 3 temporarily suspends combat targetability during its transition guard, but camera focus is deliberately independent from that gameplay group and continues tracking the authoritative live boss through `m3_enemies`.

### Stage 01 authored environment identities

1. Outer Gate — structural ribs + amber terminal.
2. Decon Corridor — cyan strips + animated decon mist.
3. Archive Annex — shelves + scanning hologram.
4. Containment Junction — red alarm field + barricades.
5. Core C — violet iris rings + boss-reactive energy columns.
6. Emergency Lift — animated green lift rails.
7. Emergency Stores — amber supply-crate language.
8. Signal Lab — live teal waveform + scanner arcs.

## Unique-art rules

The three playable operators and five Stage-01 enemy identities each own separate high-resolution master SVGs and separate 2048×2048 rig sheets. Systems and semantic bone interfaces may be shared; visible/audible final identity assets may not be reused.

Projectile geometry, hit VFX, fire SFX and impact SFX profiles remain identity-specific. `tools/validate_unique_art.py` rejects reused IDs/paths and byte-identical master or rig assets through SHA-256 checks.

Current field controls: **WASD move · Shift run · mouse aim · LMB fire · R reload · Space evade · 1/2/3 swap · F interact**.

## Frozen architecture rules

1. `project.godot` stays at repository root; nested `game/` is forbidden.
2. Field traversal and combat use the same operator actor.
3. Movement and aim are independent.
4. Story/mission authority is data-driven under `data/story` and `data/missions`.
5. Required story rooms resolve in authored order.
6. Systems may be shared; visible/audible final identity assets may not be reused.
7. Every combat identity owns unique visual, motion, projectile, hit-VFX, fire-SFX and impact-SFX profiles.
8. Master art and layered rig sheets are checked against byte-identical reuse.
9. Animation/VFX are presentation; gameplay code authors results.
10. M4 premium presentation preserves identity secondary motion, unique enemy death, boss phases and eight unique Stage-01 room signatures.
11. M5 retains pinned typography, facility depth, field grounding, overhead combat UI and actual-runtime screenshot evidence.
12. M6/M7 retain independent diagonal movement/aim, true profile/rear operator presentation, target-aware camera framing and authored Site-7 visual identities.
13. M7 boss camera authority is independent from temporary combat-targetability state.
14. Incomplete raster staging can never replace or hide the validated vector presentation.
15. CI uses exact SHA-pinned Godot 4.7.2 and retains M1 through M7 smoke coverage plus 24 actual-runtime screenshots.
16. **GitHub Pages/public deployment remains intentionally disabled until the game is complete.**

## Start here

- `docs/GDD_v0.1.md` — game design baseline
- `docs/M1_PLAYABLE_SQUAD_PROTOTYPE.md` — animated combat prototype
- `docs/M2_STORY_VERTICAL_SLICE.md` — lobby/story-stage loop
- `docs/M3_UNIQUE_2P5D_ART_BIBLE.md` — non-reuse production-art rules
- `docs/M3_HIGH_RES_UNIQUE_ART_RUNTIME.md` — M3 high-resolution runtime
- `docs/M4_PREMIUM_MOTION_ENVIRONMENT.md` — direction/motion/reaction/boss/environment contract
- `docs/M5_ACTUAL_RUNTIME_VISUAL_BASELINE.md` — real-render visual evidence, HUD/font/depth baseline
- `docs/ANIMATION_SPEC_v0.1.md` — animation contract
- `docs/TECH_ARCHITECTURE_v0.1.md` — runtime/data architecture
- `docs/FOLDER_STRUCTURE.md` — repository ownership/layout
- `docs/GITHUB_ACTIONS_POLICY.md` — CI/external-resource policy
