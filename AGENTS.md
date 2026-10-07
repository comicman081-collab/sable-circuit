# SABLE CIRCUIT project-wide production constraints

## Regression runner and local-only storage — user instruction 2026-09-25

- Commit only to this repository on the D: drive. Do not write backups,
  clones, caches or temporary files to the C: drive; use the git-ignored
  `.cache/` inside the project. No GitHub push, PR, Pages or Actions work.
- Run regressions with `python tools/maintenance/run_regression_suite.py`
  (quick: 58 tests, about 10 minutes) or `--suite full` (90 tests, about 90
  minutes: a solo playthrough per playable operation plus the Motion Studio
  Python/JS suites). Outputs go to the git-ignored
  `qa/regression_runs/<stamp>/`; the run FAILS if any existing file under
  `qa/` or `motion_lab_v1/qa/` changes, disappears or is added. `--selftest`
  proves script errors, hangs and record writes are caught.
- A test that writes files must take `--out` (see `tests/support/test_output.gd`)
  and be registered in the runner. Never point a regression run at a dated QA
  record folder.
- Playing from the project folder writes one balance record per operation to
  the git-ignored `playtest_logs/` (`scripts/core/play_session_log.gd`); web,
  headless and `-s` test-script runs write none. F9 shows FPS and live /
  attacking hostiles. These records are one person's play, not balance approval.
- Combat VFX are code-drawn only, through `scripts/vfx/vfx_painter.gd`: each
  layer of an effect sends at most two triangle arrays per frame. Glows, dots
  and puffs are one quad over a procedural alpha-profile atlas; lines, rings and
  fragments are vertex-alpha triangles. Per-shape `draw_circle` /
  `draw_colored_polygon` calls halved native combat FPS (`qa/vfx_perf_20260925/`);
  never go back to them. The shapes are rebuilt in GDScript every frame, so CPU
  is the cost: keep per-particle work small, read noise from `Painter.noise()`,
  and profile with a same-session A/B before adding particles. Impacts
  and hurt reactions: `combat_hit_vfx.gd` (a family per weapon and robot, see
  `hit_vfx_profile`; an armour deflect or boss guard replaces the weapon's
  impact rather than stacking a second one; past six live impacts new ones thin
  their particles); muzzle flashes (one per shooter per physics tick, riding
  the shooter) and robot wind-up charges: `combat_muzzle_vfx.gd`; robot and
  boss destruction, mortar/slam/lane/elite blasts, smoulder below 40 % health,
  the CINDER ram trail and floor scorch: `combat_explosion_vfx.gd`, always at
  the radius the gameplay caller damages with; skills and buff auras:
  `operator_skill_vfx.gd`; projectile bodies: `prototype_projectile.gd`. Light
  is additive; fire, smoke, dust and debris are normal-blend puffs in a layer
  behind it. Robot art is never tinted: the blast draws over it. Lights are
  desktop only. `combat_vfx_overhaul_smoke.gd` guards families, dedupe,
  triangle budgets and self-freeing; `tests/render/combat_vfx_showcase_capture.gd`
  renders the 1080p review frames (`qa/combat_vfx_overhaul_20260926/`).
  Compare FPS only in same-session rotated
  A/B runs; this PC's load varies. Camera shake is kicked
  only by heavy hits, downs and blasts through `SquadCameraPresentation.kick`
  and obeys the player's `GameSettings.screen_shake`. Tests change that setting
  in memory only; never save the player's settings from a test.
- Elite variants are data on existing robots: an encounter row's `"affix"`
  (`data/progression/elite_affixes.json`, `scripts/combat/elite_affix.gd`).
  They are marked only by the code-drawn floor ring and overhead name/barrier
  bar; never tint or alter robot art for them, and keep bosses unaffixed.
- Room hazards are data too: a room's `"hazards"` rows
  (`data/progression/zone_hazards.json`, `scripts/combat/zone_hazard.gd`) are
  placed by `site7_battlefield.gd` `hazard_points()` on open floor clear of
  cover, the squad start and first-wave spawns. They are code-drawn, telegraph
  before damage, hit robots as well as operators, and stay out of boss rooms.
  AI followers route through `ZoneHazard.steer` so they never park on a vent
  and step off one before it discharges; the controlled operator is the
  player's to move.
- Robot spawns must not stall combat (`qa/spawn_hitch_20260925/`). Reviewed
  machine specs and view sources are hash-verified once per run
  (`EnemyActor.reviewed_machine_spec`, `Site7MachineSprite._verified_size`);
  every robot type a mission can spawn is decoded while it loads
  (`StoryStage01._warm_enemy_art`), and robot textures stay resident through
  `EnemyActor.cached_texture`. The firing-lane search
  (`Site7EnemyTactics.LaneRoutes`) is one resumable search that must give each
  candidate exactly the route length `CoverNavigation._plan` would; change it
  with `_plan` (nodes, edge test, tie-break, `MAX_GRAPH_EDGE`).
  `tests/smoke/firing_lane_search_smoke.gd` guards that equivalence.
- Operators and robots are grounded-mode `CharacterBody2D`s, so a body touched
  from its north side counts as floor. Both set `platform_floor_layers` and
  `platform_wall_layers` to 0 so neither rides the other as a moving platform;
  a robot's velocity after a reposition threw an operator 200 px
  (`tests/smoke/actor_platform_carry_smoke.gd`). Keep them 0. In normal play a
  moving robot carried an operator standing against its north side all the way
  (`tests/smoke/actor_contact_carry_smoke.gd`, `qa/actor_contact_carry_20260925/`).
  Keep grounded mode and its 1 px floor snap: floating mode or a zero snap
  changed cover sliding in 161 and 23 of 242 measured approaches.
- DEPLOY must not stall on loading. `scripts/core/deploy_warmer.gd` loads it
  behind the menus: title and base queue the next mission's robot art, the
  briefing adds its room plates, cover props and the squad's atlases. Native
  decodes on `WorkerThreadPool`; web builds have no threads and run one job per
  frame, on base and briefing only. Plates and atlases are handed over once
  (`BattleTextureLibrary` / `MotionLabCharacterRuntime` prepared textures) and
  dropped when the player backs out; robot art and props stay cached for the
  run. Only the `prepare_*` / `decode_*` statics run on workers and they touch
  no shared state; adoption and texture creation stay on the main thread. The
  stage's own loads remain the fallback (`tests/smoke/deploy_warmer_smoke.gd`).

## Map connections, wall collision and ASTER gait — user instruction 2026-09-25

- The SITE-7 v2 map kit supplies 15 authored plates for each of missions 1–5.
  Missions 4 and 5 use dedicated room and connector plates; no plate is shared
  between missions. The geometry smoke checks that each plate belongs to exactly
  one mission. Its contract is
  `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`. Every mission's strict
  audit must pass 15 plates and 14 seams. Its floor-axis limit is 22.5-30.5
  degrees; only the down-right branch connectors whose id ends C06 or C07 may
  reach 32.5 (user approval 2026-10-01; 31.5 on 2026-09-30, but ImageGen drew
  those decks 30.7-33.5 whatever the prompt asked, and the decks of operations
  4-6 are painted at 30-35 degrees with an untraced standard outline).
  `plate_axis` in the quick suite
  (`tests/test_site7_plate_lighting_axis.py`) guards both limits. The audit reads
  the raw plates, before the runtime seam light (`site7_seam_light.json`) corrects
  a deck toward its room. Three operation-8 seams (S8_C01 with R01_GATE, S8_C03
  with R04_JUNCTION, S8_C05 with R05_TERMINAL) are waived by name in
  `SEAM_WAIVERS` (user approval 2026-09-30, chosen instead of regenerating the
  decks): each has its own raw limits a little above what was measured, holds only
  while the shipped seam light brings that seam inside the normal targets (1.41x,
  1.28x and 1.27x, at most 0.04 stops), and never waives hue. `seam_waiver`
  (`tests/test_site7_plate_lighting_seam_waiver.py`) guards it and fails a stale
  waiver; `qa/site7_op8_preenable_20260930/` has the record. Mission 3's unused room doors are
  closed by code-drawn bulkheads with collision; the stage-4/5 room art has
  only each mission's actual doors. Explicit `deck` values select authored ascending/descending art
  without a mirror. Missing `deck` keeps legacy v1 branch mirroring. Room `doors`
  in `site7_plate_floors.json` bind connector end centres to painted thresholds;
  legacy rooms still use the lit-floor fit. The alignment test limits authored
  door error to 0.5 px and still drives real WASD crossings in both directions.
  V2 connectors use per-plate end fades (ascending 10%, descending 7.5%) over
  their coplanar aprons; v1 remains at 12%. Keep source/game scale 1.0 and the
  existing actor size.
- User correction 2026-09-27: retain generated working images, including managed
  staging copies, throughout the task. Do not delete them immediately after
  intake. Cleanup is deferred until the whole task is finished; rejected source
  candidates remain subject to the quarantine preservation rule.
- The user reported actors walking through walls, rooms joined upside down and
  ASTER's awkward walk. Plates now sit where `tools/environment/build_site7_world_layout.py`
  solves them (`data/visual/site7_world_layout.json`, read by `site7_world_layout.gd`):
  the main route climbs up-right (mission 4 walks it back down; see "Mission
  styles and route structure") and the two branches descend down-right. Legacy
  v1 branches mirror; authored v2 descending decks do not. No plate is rotated.
  Legacy deck ends reach into lit floor (15 % in from the plate border); authored
  door anchors use the painted coplanar apron instead.
  Rerun the tool after changing any floor, plate or scale; the quick suite's
  `world_layout` (`--check`) fails on a stale layout.
- Walkable ground is painted floor only. Route segments are navigation-only
  (half width 0); the old 100 px capsule from each combat room centre crossed
  painted walls. Room floors stop 7.5 % inside their plate border, where later
  plates draw over them, so decks own their ends. Corridor combat floors in
  `site7_battle_layouts.json` follow the painted walkway. Navigation waypoints
  split long route segments at no more than 760 px; one midpoint left the
  1,925 px stage-3 decks beyond `CoverNavigation.MAX_GRAPH_EDGE` (900 px).
- `Site7RoomArtLayer.apply_floor_masks` makes each plate transparent over the
  floors of plates drawn before it, fading out over the earlier plate's outer
  15 % (`MASK_EDGE_FADE`) so no plate's dark border shows through. Plate
  borders never cut straight: connectors fade their top and bottom 10 %
  (`CAP_FADE`) except on their own deck, and rooms fade every side 5 %
  (`ROOM_EDGE_FADE`, which must stay inside the 7.5 % floor inset;
  `site7_battle_geometry_smoke.gd` guards both, `qa/plate_seams_20260926/`).
  The layout tool's `--preview` mirrors both fades. Each plate was painted
  under its own light, so the tool also writes `data/visual/site7_seam_light.json`:
  per connector a grid of brightness gain and saturation that brings its deck
  to each room floor's brightness and saturation at the seam, applied in the
  plate shader. It never shifts hue (an orange deck pulled toward a cyan room
  turned green), off the deck it only darkens (lifting a deck also lifted R05's
  purple pillar glow), and it leaves lamps alone. `--check` allows one step per
  byte across numpy builds (`qa/plate_lighting_20260927/`). Body/cover
  depth is camera-relative (`site7_depth.gd`); a fixed origin only sorted y 0-1000.
- Covers stay 110 px off deck doors, with every deck mouth reachable. In combat
  rooms every enemy spawn slot must reach the squad around the cover and around
  robots standing on the first four slots (a mortar never leaves its slot), with
  a 20 px lane margin: robots are 4 px wider than the operator probe, and in
  corridor rooms a one-robot lane was plugged by a robot stopped to attack.
  Mission 5's long carrier boss room authors support `enemy_spawns` on the
  approach side; automatic farthest-point sampling put a robot in the exit
  apron and closed it while the boss lived. A robot
  that reaches a firing lane without a valid aim marks it spent
  (`Site7EnemyTactics._spent_lanes`) until it winds up or its target moves 85 px;
  a lane at the edge of the illustrated views otherwise circled a drone forever. Re-settle with
  `tools/environment/settle_cover_on_floor.gd -- --write` after moving floors
  or plates. `site7_connector_alignment_smoke.gd` and
  `site7_battle_geometry_smoke.gd` (full suite) guard orientation, deck continuity,
  painted walls and WASD crossings.
- Every operator walks one gait cycle per Studio `walkStride` × 100 map px.
  ASTER's height-scaled 120.6 px cycle drove 164 steps/min against MICA's 114.
  ASTER's walk frames shift per frame by `data/art_profiles/motion_lab_walk_registration.json`
  (`tools/character_pipeline/build_walk_torso_registration.py`, bound to each
  frame's source SHA-256) so her torso holds the cycle mean. Pixels, masters and
  muzzles are unchanged; muzzle and aim use the shifted sprite. MICA and ROOK
  keep their accepted hip placement. Evidence: `qa/map_gait_20260925/`.

## Mood light, void masks and abyss backdrop — user instruction 2026-09-27

- The user asked for lighting, brightness and saturation that give each room
  and stage its own atmosphere, and for no black background in game. The v2
  plates stay painted under one neutral light (their seams depend on it);
  mood is added at runtime by the plate shader in `site7_room_art_layer.gd`
  from `data/visual/site7_mood.json` (loader `scripts/missions/site7_mood.gd`).
  Per mission: a grade (exposure in stops, luminance-keeping tint, saturation)
  over every plate, and the abyss row. Per plate: its room grade, lamp pools,
  an optional overhead fill and extra lights. A connector turns from one
  room's grade to the other's between its deck doors. Pools are world-space
  floor ellipses (half as tall), may pulse, and emissive pixels keep their
  painted colour. Only plates take this light: never robot, operator, elite
  or prop art.
- `tools/environment/build_site7_mood_light.py` finds each listed plate's
  painted lamps (`site7_mood_lamps.json`) and its flat, border-connected outer
  void (`site7_void_masks.json`, see-through in the shader; a mission's
  `abyss.void_fill_px` also drops narrow dark pockets, see "Operation 10 void
  lit"). Rerun it after
  changing any listed plate or `site7_mood.json`'s plate list; the quick
  suite's `mood_light` (`--check`) fails on stale data. A new v2 stage needs a
  mission row plus a row per plate, then the tool.
- Behind the plates `scripts/missions/site7_abyss_backdrop.gd` draws the shaft
  the level hangs over: one code-drawn quad (no painted art) with parallax
  fog, each plate's lamp colour in the haze, dimetric girders with work
  lights and dust. Web builds use half the fog octaves. A mission without an
  abyss row gets none. All five missions now use v2 plates with void masks and
  the same fog and haze strength (1.0 / 0.2); legacy v1 plates have no void
  masks and would show their rectangles under that fog.
- `site7_battle_geometry_smoke.gd` guards that plates follow the mission row,
  that no light reaching a plate is dropped (24 per plate), void masks,
  connector axes and the backdrop. Evidence: `qa/site7_mood_light_20260927/`.
- Operations 6-8 add the abyss styles `spore` (VERDANT LOCK), `cryo` (COLD
  STORAGE) and `dawn` (SWITCHYARD, a bright cloud sea). Against the dawn haze
  the plates' dark edge pixels, just above the void threshold (`VOID_MAX` 12),
  were lifted into grey halos by the mission's shadows and contrast; a higher
  threshold ate wall rims, and an alpha feather (rejected) let the abyss show
  through dark wall recesses. Plate alpha and the threshold therefore stay
  untouched and the abyss darkens itself: the mission row's
  `contact_shadow_px` (24) and `contact_shadow_strength` (0.88) make
  `build_site7_mood_light.py` write one padded quarter-size field per plate
  (`data/visual/site7_contact_shadows.json`: 1 on the plate's opaque pixels,
  `exp(-(d / 24 px)^2)` into its void, 0 at its 72 px padding), and the dawn
  shader mixes the haze toward the abyss `base` colour by the strongest field at
  each pixel. The atlas is built once when the backdrop is set up
  (`MAX_CONTACTS` 15, which operation 8's 15 plates fill); the shader adds one
  loop over the plates' rectangles per pixel and GDScript does nothing per
  frame. It shades the abyss only, never a plate, actor or prop, and the field
  is not mirrored, so a mirrored dawn plate is refused. `mood_light` (`--check`)
  keeps the file fresh; it compares decoded pixels to one step
  (`same_contacts`), so another zlib or numpy build does not fail it, and
  `mood_contact` guards that comparison.
  `site7_battle_geometry_smoke.gd` needs a field for every dawn plate and none
  for another style, and reads the shader's own atlas mapping: opaque pixels
  along each plate's void edge read at least 0.95, and the same read fails once
  every field is shifted 12 px. Headless runs do not draw the shader, so judge
  the look on `tools/environment/capture_site7_plate_edges.gd -- --out=res://...`
  (six native 1080p cameras of operation 8), not on the smoke.
- S8_O02's GAME plate was re-exposed from factor 0.5396 to 0.5831 (registered
  floor luma 0.166 to 0.180): the same whole-image sRGB LUT over its unchanged
  RAW / MASTER (`95999fdb...`), nothing else; the previous GAME is kept under
  `art_src/environments/site7_v2/_quarantine/S8_O02/`. Its void mask, lamps and
  connector S8_C07's seam light were rebuilt; nothing of missions 1-7 changed.
  Records: `qa/site7_ops_6_10_plates_20260929/stage_c/finish_20260930/` and
  `qa/site7_op8_a1_a2_verified_20260930/`.

## Mission styles and route structure — user instruction 2026-09-27

- The user asked that missions 2-5 not feel repeated: change their structure,
  and keep lighting, saturation, brightness and style distinct per mission.
- Each mission row also sets `contrast` around `pivot` and a `shadows` colour
  lifted into the dark tones (after saturation, in the plate shader), and its
  abyss `style`: `shaft` (M1 girders and work lights), `flood` (M2 dark water
  with light reflections), `pressure` (M3 red strobes and steam), `forge` (M4
  a glowing cracked crust under the level and embers), `offshore` (M5 swell,
  rig beacons and rain). All stay one code-drawn quad; `style_color` and
  `style_strength` tint and scale the style layer. Mission 2's 15 v2 plates
  have their own rows (reentry cold and dim under a pulsing red beacon, so
  it does not repeat mission 1's amber entry; flooded maintenance cold teal,
  archive green data, quarantine sickly yellow-green, boss relay crimson
  pulse, lift warm white, cache orange, recorder blue-violet).
- Mission 3 retains its stage-3 room-specific `"plates"` rows. The eight new
  stage-4 and eight new stage-5 room grades live in the shared `"plates"` table;
  missions 4 and 5 have dedicated connectors too, so all 75 plates belong to
  one mission each. `site7_mood.gd` takes the mission id for every plate query,
  and the tool rejects a mission plate row for a plate outside the shared list.
  M3 CORE PRESSURE is dark crimson: a dim
  red emergency fill and a pulsing red alarm in every room, with the red lamps
  of S3_R01/R02 strobing and cool lamps dimmed. M4 FORGE DESCENT is amber and
  bright: heat from the crust below rises at each room's front edge and grows
  with depth, under a warm fill and steady lamps. M5 OFFSHORE NULL is cold
  grey-blue: dim warm lamps, a cold overhead fill and a slow rig beacon
  crossing each room, with only the carrier boss room's red lamps pulsing.
  The light differences for shared connectors and the dedicated room grades are
  checked in `site7_battle_geometry_smoke.gd`. Earlier shared-room evidence is
  in `qa/site7_stage3_mission_light_20260927/`.
- Route structure is data. An optional room's `"from"` (mission JSON) names
  the main room its branch leaves (default: the room two ahead of it, as in
  missions 1-2); read it through `StoryStage01.branch_parent`, never
  `main_route[index + 2]`. A connector row's `"reverse": true`
  (`site7_battle_art.json`) meets the room before it at the deck's upper-right
  end, so the route descends down and to the left; the solver writes it into
  the world layout and the battlefield picks the deck ends from it. v2 plates
  are bound to their painted doors, so missions 1-2 keep hubs R03/R04 and the
  climb. Mission 3 keeps its stage-3 room order with O02 off the boss hall.
  Mission 4 descends from the thermal spine through forge rooms; mission 5
  fights through offshore relay rooms. Both retain the stage-3 connector route
  structure, including mission 4's reversed main connectors. A room carries
  its own plate's combat floor and cover
  (plate coordinates). A room entered from its plate's upper right sets
  `spawn`, `enemy_spawns` and `boss_anchor` on the far side
  (`site7_battle_layouts.json`); a corridor boss stands at the exit end so no
  robot spawns behind it. After changing a structure rerun
  `build_site7_world_layout.py`, then `settle_cover_on_floor.gd -- --write`
  until a dry run moves nothing. `site7_connector_alignment_smoke.gd` checks
  climb or descent per connector.

## Boss robots and per-boss patterns — user instruction 2026-09-28

- Each mission has its own boss: M1 ANCHOR (`BOSS_SITE7_ANCHOR_01`, art and
  `anchor_iris` attack unchanged), M2 RELAY SENTINEL (`BOSS_SITE7_RELAY_01`,
  710 HP), M3 RESONANCE REMNANT (`BOSS_SITE7_REMNANT_01`, 820 HP), and M4
  FORGE and M5 CARRIER on their existing art. The attack is data:
  `boss_pattern` in `enemy_profiles.json` (`anchor_iris`, `relay_chain`,
  `resonance_lanes`, `forge_press`, `carrier_null`), with a different warning
  shape in each boss's three phases. `boss_brief` is the briefing line. The
  arena ring and pillars take `arena_accent`, else the second `palette` colour;
  CARRIER's violet repeated ANCHOR's arena, so it has cyan `#62c9eb`.
- Fairness limits (`site7_boss_pattern_smoke.gd`): at most 7 warnings per
  attack, each winding up for at least 1.0 s, warning damage at most 20,
  projectile damage at most 24, and within 300 px a gap 1.5 operators wide of
  painted floor that no warning covers. A duplicate pattern is the negative
  control. The boss attack WINDUP state lasts 1.1 s, except ANCHOR, which keeps
  its shipped 0.95 s and warning values. The quick suite
  runs `boss_registry`, `boss_pattern` and `robot_roster`; the full suite adds
  `boss_capture_geometry` (`tests/render/site7_boss_pattern_capture.gd`).
  Evidence: `qa/site7_boss_robots_20260928_final/`.
- Alpha 255: the user approved the native alpha-255 interiors of the two new
  boss masters, stating that 255 is better than 254, and then allowed 255 for
  every new asset (see "Existing asset-production rules"). The selected RELAY
  (`dd13595d…`) and REMNANT (`f5dd2d39…`) PNGs are byte-identical from source
  through MASTER to runtime (`boss_asset_gate.json`) and pass the general gate.
  Never clamp them to 254, key, crop or redraw them.

## Operations 6-10, held back for art — user instruction 2026-09-29

- The user asked to expand the campaign from five operations to ten.
  Operations 6-10 (VERDANT LOCK, COLD STORAGE, SWITCHYARD, MEMORY VAULT, ZERO
  POINT) are authored as data (`data/missions/MIS_CH01_06.json`-`10.json`, the
  campaign rows with briefing and debrief) but stay `"deployable": false` in
  `data/story/site7_campaign.json` until their 15 map plates exist (their
  bosses are registered, see "Bosses of operations 6-10"). No plate is shared
  between missions and all raster art comes from Codex's ImageGen, so the base
  lists them as IN PREPARATION. Never flip `deployable` early, borrow another
  mission's plates or boss art, or draw stand-ins; that needs the user's
  explicit exception. Enable one operation at a time, in order. Operations 6,
  7, 8, 9 and 10 were opened on the user's orders (see "Operation 6 enabled"
  to "Operation 10 enabled"); none is held back now, and the rule stands for
  any operation added later.
- Catalog rules (`scripts/core/site7_campaign.gd`): `available` needs
  `deployable` and a cleared predecessor; `next_after` is empty for a held-back
  successor; `recommended` skips held-back rows; `playable_ids()` are always
  the leading rows. `CampaignProgression.snapshot()["playable_complete"]` is
  "every deployable operation cleared"; `chapter_complete` stays "all ten
  cleared". An operation without its own `stage<N>` cue reuses the stage cues
  in order (`DemoMusic.stage_key`, `sound/README.md`).
- A held-back mission file carries a `staging` block (status `ART_PENDING`,
  plate prefix and folder, route structure, boss id, name, health and pattern);
  its boss row already names that registered boss (before 2026-09-29 it held
  the placeholder `BOSS_SITE7_CARRIER_01`; `motion_lab_v1/tests/test_enemy_body_plan.py`
  still requires every `enemy_id` in a mission file to be an active robot).
  Enabling follows `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md`
  section 6: wire the plates, then delete `staging`, `deployable: false` and
  `pending`, and announce the operation in the predecessor's COMMAND debrief.
  A held-back successor is never named or promised in story text.
- `tests/smoke/site7_campaign_data_smoke.gd` (quick `campaign_data`) gates all
  ten missions: density contract, staging or full integration data, boss
  uniqueness and rising boss health, route structures, story text, and the
  per-operation tests that still stop before the last deployable operation (a
  `range(1, N)` loop, a tuple, a list or a table that ends at an earlier
  mission; generic for any playable count, so each opening must widen them).
  It has negative controls and approves no art, balance or play.
- Work orders for Codex: `docs/production/SITE7_OPERATIONS_6_10_PLATES_CODEX_PROMPT_KO.md`
  (75 plates) and `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`
  (five bosses AERATOR, CRYO, GANTRY, ARCHIVE, ORIGIN and their patterns; Codex
  drew the masters, section 7 steps 2-4 were done by Claude, see below).
  For operations 9-10,
  `docs/production/SITE7_OPERATIONS_9_10_PRODUCTION_ORDER_KO.md` (2026-09-30) is
  the production order: their 30 plates, the wiring, what operations 6-8 taught
  (rejection causes, the down-right branch contour, boss arena size, lamp and
  abyss rules), what operation 9 added (section 4.7) and what Claude checks
  before and at enabling. Both are open (operation 9 on 2026-10-01, operation
  10 on 2026-10-02).

## Bosses of operations 6-10 — user instruction 2026-09-29

- The user gave the boss code and tests (work order section 7, steps 2-4) to
  Claude. AERATOR TOWER (`BOSS_SITE7_AERATOR_01`, operation 6, 1560 HP,
  `bloom_field`), CRYO COMPRESSOR (`BOSS_SITE7_CRYO_01`, 7, 1740, `frost_sweep`),
  SIGNAL GANTRY (`BOSS_SITE7_GANTRY_01`, 8, 1920, `rail_charge`), INDEX SPIRE
  (`BOSS_SITE7_ARCHIVE_01`, 9, 2100, `echo_copy`) and ORIGIN CORE
  (`BOSS_SITE7_ORIGIN_01`, 10, 2460, `null_convergence`) are profiles in
  `enemy_profiles.json` on the masters Codex returned, byte for byte from
  `motion_lab_v1/art/site7_enemies_raw/` to `assets/enemies/stage6_…stage10_…/
  authored_core_v1/` (`tools/environment/build_site7_boss_runtime.py`, `--check`;
  binding rows in `qa/site7_ops_6_10_boss_integration_20260929/runtime_binding.json`).
  Never clamp, key, crop or redraw them. Each mission row holds its own boss.
  That work left `deployable` and the `staging` blocks untouched; operations 6,
  7, 8 and 9 were opened afterwards (see "Operation 6 enabled", "Operation 7
  enabled", "Operation 8 enabled" and "Operation 9 enabled"), 10 is not
  playable yet, and no other mission's plates or boss art stand in for missing
  ones.
- A spec's optional `visible_rect_px` `[x0, y0, x1, y1]` is the machine's own mass
  in its picture (default: the whole picture). `Site7MachineSprite.visible_rect`
  drives the damage box (the shipped 76 x 70 % inset of it), the health bar
  (`EnemyOverheadUI.bar_y_local`, 12 px over the machine's top) and the size
  checks (`site7_boss_registry_smoke.gd`: each boss stands 220-270 px tall).
  Bosses draw at their native `display_height`; the ground ellipse under them
  (`EnemyGroundShadow`) is one fixed size for every boss.
- Patterns are `Site7EnemyTactics` attack functions; attack A is an odd
  `attack_serial`, B an even one, phases change at 66 % and 33 % health.
  `bloom_field`: spore circles on a ring round the target, its own ground
  blooms too from phase two, attack B turns the ring. `frost_sweep`: frost bars
  across the compressor-to-target line, 150 px apart from 130 px out, lighting
  in a wave (inward in the last phase's B); the last phase adds a 300 px axis
  lane from the compressor that stops at the second bar (a 900 px one left no
  gap on operation 7's narrow vault floor, see "Operation 7 enabled").
  `rail_charge`: rails cross where the
  target stands, then circles either side, then a star; the phase-two diagonal
  rails and the last phase's star and B circle wind up `GANTRY_LATE_WINDUP`
  (1.6 s; 1.4 s and 1.5 s failed 101 of 1,410 attacks on operation 8's terminal
  floor in `boss_room_fairness`, and `boss_pattern` pins 1.56 s as the floor) so
  the way out of the star stays reachable beside a wall.
  `echo_copy`: the target's own ground and the ground it stood on at its last
  attacks bloom (`ECHO_MEMORY` 3, kept across phases); the echoes wind up from
  `ECHO_WINDUP` (1.3 s, older ones 0.1 s later), then the target's ground (1.6 s)
  and the last phase's lane (1.7 s). A target standing still stacks every echo on
  its own spot, and the old 1.0 s left 0.13 s beside a wall on operation 9's
  stacks room (2 of 4,524 attacks in `boss_room_fairness`, which asks 0.25 s);
  `boss_pattern` pins 1.12 s as the floor. `null_convergence`:
  lanes converge on the target from every side while the core's ground closes;
  the last phase's lanes, core circle and target circle wind up
  `ORIGIN_LATE_WINDUP` (1.6 s). On operation 10's core room the old 1.2 s / 1.3 s
  left 0.11 s beside a wall (3 spots of 5,743 at a 10 px grid, all the last
  phase's second attack, nearest gap 150 px) where `boss_room_fairness` asks
  0.25 s; `boss_pattern` pins 1.56 s (a 180 px walk plus the margin) as the floor.
  Every boss's shots / circles / lanes per phase are frozen in
  `site7_boss_pattern_smoke.gd` (`SIGNATURES`; all ten bosses differ in every
  phase). Beyond the shared fairness limits that smoke checks each pattern's
  geometry and that, wherever the target stands (5 distances x 6 bearings x 6
  attacks), clear floor lies within 180 px and the slowest walk (138 px/s)
  reaches it 0.25 s before the warning on the target's spot goes off. Fit a
  pattern to those limits; never lower them.
- `tests/smoke/site7_boss_duel_smoke.gd` (quick `boss_duel`) is the live check
  of the boss fights alone, next to the `full_op_06` to `full_op_10`
  playthroughs (it was the only live check of a boss whose operation was not
  playable yet): all ten bosses run the real controller
  and warning loop against three
  stationary operators, six attacks each plus a damage flow (phase changes, the
  8 s core shield, the kill). Live shapes equal the frozen ones, the wind-up
  lasts 1.1 s (ANCHOR 0.95 s), cycles keep their timing, and damage lands only
  when a warning goes off (at least 0.95 s after it appeared) on exactly the
  operators inside it. It runs ten times faster by raising
  `Engine.physics_ticks_per_second` together with `Engine.time_scale`: Godot
  hands `_physics_process` a delta of tick x time scale, so a time scale alone
  would make every tick 10/60 s. Negative controls (a wrong pattern, a warning
  that goes off early, one that hits too hard) must be rejected. Bare scene, no
  plates: technical only.
- Effects stay code-drawn: each boss has its own muzzle flash
  (`combat_muzzle_vfx.gd`), hit family (`combat_hit_vfx.gd`) and projectile body
  (`PRJ_BOSS_*_01`, `prototype_projectile.gd`) in the accent colour of its
  profile's `arena_accent` (all ten arena colours differ, checked). Robot art
  is never tinted.
- Captures: `tests/render/site7_boss_pattern_capture.gd` shoots each boss of an
  open operation in its own room (AERATOR in R05_ATRIUM of operation 6, CRYO in
  R05_VAULT of operation 7, GANTRY in R05_TERMINAL of operation 8, INDEX SPIRE
  in R05_STACKS of operation 9, ORIGIN CORE in R05_CORE of operation 10). A
  boss whose room exists but whose operation is not open is staged in
  mission 3's boss hall, labelled a TEST BED: not a review of the boss's own
  room (`TEST_BED` is empty now that all ten are open). `tests/render/site7_boss_lineup_capture.gd`
  (`boss_lineup`) draws all ten bosses at one game scale. A test-bed boss's FPS,
  sound video and full playthrough need its operation to be playable. The
  registry smoke follows the campaign's `deployable` flag: once an operation
  opens, its boss is also spawned in the live stage and its `staging` block
  must be gone. Technical checks only: no art, balance or play approval.
  Evidence: `qa/site7_ops_6_10_boss_integration_20260929/`. Move the next
  boss's `TEST_BED` row into its own room (`FIRST_A_B_ROOM`) when its
  operation opens.

## Operation 6 enabled — user instruction 2026-09-29

- The user ordered operation 6 (VERDANT LOCK) turned on ("작전 6 켜라") once its
  15 plates (Codex) and its boss AERATOR TOWER were in. Following section 6 C of
  the design doc, its `staging` block, `deployable: false` and `pending` are
  gone, and operation 5's COMMAND debrief announces Verdant Lock. Operations 7-10
  stay held back: enable them one at a time, in order, the same way. The tests
  that looped over five operations cover six (`campaign_data`'s stale-loop gate
  names any that remain) and `full_op_06` joins the runner's solo playthroughs.
- Optional rooms are read by their `type`, not their id
  (`StoryStage01.optional_kind_of`: "SUPPLY", "RESEARCH", else the legacy ids
  O01_SUPPLY / O02_RESEARCH, else position). Operations 6-10 name them for the
  place (O01_STORES, O02_NURSERY), which the stage did not recognise: neither
  cache paid out, no run boost fired (`data/progression/run_modifiers.json`
  names its `source_room` by the legacy ids) and the `full_op_06` bot walked to
  the first room forever. `site7_campaign_progression_smoke.gd` now recovers
  both optional rooms through the real interaction in every playable operation.
- Operation 6 authors 11 cover props (operations 1-5 author 12-15). The
  progression smoke's floor is now one attached prop per room, which
  `campaign_data` already requires; every authored prop must still attach. More
  cover there is Codex's art work, only if the user wants it.
- `tests/smoke/site7_boss_room_fairness_smoke.gd` (quick `boss_room_fairness`)
  lays every attack of each newer boss on that boss's own room in each playable
  operation. From every spot an operator can stand on (painted floor, off the
  cover; 50 px grid, 150-800 px from the boss) a 1.5-operator-wide patch of
  uncovered floor lies within 180 px, a straight walk over floor and clear of
  cover reaches it, and the slowest walk (138 px/s) arrives 0.25 s before the
  warning on that spot goes off. A room-wide warning is the negative control.
  R05_ATRIUM passes at 100, 50 and 25 px grids (worst nearest clear floor 90
  px, tightest escape margin 1.05 s, 0 failing attacks of 3,720 at 25 px). Fit
  a boss or its room to these limits; never lower them.
- Technical checks only. Human play and balance, a same-session FPS A/B for
  operation 6 (no per-operation tool exists) and art approval of its plates and
  boss are the user's. The own-room captures, the 10 s game-sound clip
  (`SABLE_CAPTURE_MISSIONS=6 SABLE_CAPTURE_BOSS=1` with
  `record_stage_battle_with_audio.py`) and the run summaries are in
  `qa/site7_op6_enable_20260929/`.

## Operation 7 enabled — user instruction 2026-09-30

- The user ordered operation 7 (COLD STORAGE) turned on ("작전 7 켜라") once Codex
  finished its 15 plates and the mood, abyss and cover rows
  (`qa/site7_ops_6_10_plates_20260929/stage_b/`). Following section 6 C of the
  design doc its `staging` block, `deployable: false` and `pending` are gone and
  operation 6's COMMAND debrief announces Cold Storage. Operations 8-10 stay
  held back: enable them one at a time, in order, the same way. `full_op_07`
  joins the runner's solo playthroughs (bot, 221 s, extracted, no failures) and
  the live-entry smoke covers seven operations. The stale-loop gate in
  `site7_campaign_data_smoke.gd` is generic now and has controls for six, seven
  and eight playable operations.
- `boss_room_fairness` failed for the new room and the boss was fitted, not the
  limit. CRYO's last-phase axis lane ran 900 px along the line to the target; on
  R05_VAULT's narrow west ledge and door mouth it left no 1.5-operator gap of
  uncovered floor beside it (10 spots at a 25 px grid, 20 at 20 px). The lane is
  `FROST_AXIS_REACH` = 300 px now: it reaches the second bar and stops, and
  `boss_pattern` pins it (300, never above 340). Lane at 900 / 400 / 340 / 300 /
  none, 20 px grid: 20 / 14 / 0 / 0 / 0 failing attacks of 7,260. The limits (180
  px, 0.25 s) are unchanged. R05_VAULT passes at 100, 50 and 25 px grids (worst
  nearest clear floor 120 px, tightest escape margin 0.43 s, 0 failing attacks of
  4,680 at 25 px); R05_ATRIUM of operation 6 is unchanged. A new room can fail
  this test with a pattern that passed on the bare floor: fit the boss to it.
- R05_VAULT authors no cover (Codex's Stage B record: nothing in the middle of the
  room), the only room of operations 1-7 with an empty prop row; operation 7
  authors 9 cover props (operations 1-6: 11-15). `campaign_data` requires a row
  per room and the progression smoke at least one prop per room in total, so the
  empty row passes. Cover in the vault is Codex's art work, only if the user wants
  it, and it changes the room's fairness geometry: rerun `boss_room_fairness`.
- Technical checks only. Human play and balance, a same-session FPS A/B for
  operation 7 (no per-operation tool exists) and art approval of its plates and
  boss are the user's. The own-room captures, the 10 s game-sound clip
  (`SABLE_CAPTURE_MISSIONS=7 SABLE_CAPTURE_BOSS=1` with
  `record_stage_battle_with_audio.py`), the fairness grids and the run summaries
  are in `qa/site7_op7_enable_20260930/`.

## Operation 8 enabled — user instruction 2026-09-30

- The user ordered operation 8 (SWITCHYARD) turned on ("8 켜라") once Codex's
  finish work (`qa/site7_ops_6_10_plates_20260929/stage_c/finish_20260930/`:
  the S8_O02 exposure and the dawn contact shadow) had been verified
  (`qa/site7_op8_a1_a2_verified_20260930/`). Following section 6 C of the
  design doc its `staging` block, `deployable: false` and `pending` are gone
  and operation 7's COMMAND debrief announces Switchyard. Operations 9-10 stay
  held back: enable them one at a time, in order, the same way. The
  live-entry smoke covers eight operations. That smoke is not in the runner
  (run it with `-s`) and is now one of the stale-loop gate's
  `PER_OPERATION_FILES`, so a ninth operation cannot open with its
  `range(1, 9)` unseen; the gate also has controls for eight and nine
  playable operations.
- `full_op_08` joins the runner's solo playthroughs and is the most marginal
  of them, more than `full_op_03`: through the runner the bot extracted twice
  in five runs (196 s and 199 s, 24 kills each; the second was the full suite
  on the committed tip) and wiped three times (twice in R04_JUNCTION at
  74-76 s, once in the boss room at 139 s); a direct run before the opening
  extracted too (193.5 s). The traces show why. Operation 8 carries nine
  PRISMs, the most of any operation (operations 4-7: 7, 6, 6, 4), and PRISM
  is the largest damage source in every run (180-282 of 346-616 taken). Its
  supply branch O01_DEPOT hangs off the elite room R04_JUNCTION (operations
  5-7: R02, R01, R02), so the squad cannot heal before that room: R02 costs
  it 190-220 HP in every run and the lead operator enters R04 with 5-48 HP.
  A lone WIPED is not a regression: rerun with `--only full_op_08` as for
  `full_op_03`. A run that stops for another reason (route, rewards,
  extraction) is one. The numbers are unchanged. Retuning the elite room, the
  PRISM count or the supply branch, or letting the runner retry a WIPED
  playthrough, is balance and tooling policy for the user to decide.
- `boss_room_fairness` measures the real room and passes without a change to
  GANTRY: the late wind-ups (`GANTRY_LATE_WINDUP`, 1.6 s) had been fitted to
  a copy of R05_TERMINAL before the opening (see "Bosses of operations 6-10").
  50 px grid: 1,410 attacks, 0 failing, worst nearest clear floor 180 px (the
  limit itself), tightest escape margin 0.30 s (limit 0.25 s). A new room can
  still fail with a pattern that passed on the bare floor, and a held-back
  operation's boss room can be measured before it opens by running the smoke
  on a copy that forces the operation into its playable list.
- R05_TERMINAL authors no cover, like R05_VAULT (Codex: nothing in the middle
  of the room); operation 8 authors 11 cover props (operations 1-7: 9-15).
  Cover in the terminal is Codex's art work, only if the user wants it, and it
  changes the room's fairness geometry: rerun `boss_room_fairness`. The
  operation's three named seam waivers stay as recorded under "Map
  connections, wall collision and ASTER gait" (strict audit: 15 plates, 14
  seams).
- `record_stage_battle_with_audio.py` writes below `SABLE_CAPTURE_ROOT`,
  whose default is a dated QA record folder: point it at a scratch folder.
- Technical checks only. Human play and balance, a same-session FPS A/B for
  operation 8 (no per-operation tool exists), the look of the dawn backdrop and
  art approval of its plates and boss are the user's. The own-room captures,
  the 10 s game-sound clip (`SABLE_CAPTURE_MISSIONS=8 SABLE_CAPTURE_BOSS=1`
  with `record_stage_battle_with_audio.py`), the fairness grids and the run
  summaries are in `qa/site7_op8_enable_20260930/`.

## Operation 9 enabled — user instruction 2026-10-01

- The user ordered operation 9 (MEMORY VAULT) turned on ("작전 9 켜고") once
  Codex's stage D plates (`qa/site7_ops_6_10_plates_20260929/stage_d/`) had been
  verified (`qa/site7_op9_preenable_20261001/`). Following section 6 C of the
  design doc its `staging` block, `deployable: false` and `pending` are gone and
  operation 8's COMMAND debrief announces Memory Vault. Operation 10 stayed held
  back until the user ordered it ("작전 10 켜라", see "Operation 10 enabled").
  Its 15 plates and their wiring were in by then (Codex's stage E, commits
  `f2462d2e` and `e2ca52ed`, record
  `qa/site7_ops_6_10_plates_20260929/stage_e/finish_20261001/`; the user's
  decisions on `S10_R01` and `S10_R05` (the latter with one named waiver, its
  whole-floor short side of 547 px) and the left/right margin tolerance of 4.5 %
  main / 3.5 % whole floor for the remaining rooms are in sections 0, 4.8 and 5
  of `docs/production/SITE7_OPERATIONS_9_10_PRODUCTION_ORDER_KO.md`). Claude's
  check on that tip, with nothing blocking the opening, is
  `qa/site7_op10_preenable_20261002/` (plates re-measured, strict audit 15
  plates / 14 seams, quick 44/44, the real `R05_CORE` fairness grids, five bot
  playthroughs: four extracted, one wiped in the boss room). `full_op_09`
  joins the runner's solo playthroughs, the live-entry smoke covers nine
  operations and the stale-loop gate has controls for nine and ten playable
  operations (the live-entry smoke was on its watch list, so it was not missed
  this time).
- INDEX SPIRE was fitted to its own room before the opening (`e4a305d6`):
  `echo_copy` failed `boss_room_fairness` on R05_STACKS (2 of 4,524 attacks at a
  25 px grid), because a target standing still stacks every echo on its own spot
  and the old 1.0 s wind-up left 0.13 s beside a wall where the smoke asks 0.25 s.
  `ECHO_WINDUP` went from 1.0 to 1.3 s and `boss_pattern` pins 1.12 s as the
  floor; the limits (180 px, 0.25 s) are unchanged. The real room after the
  opening: 100 / 50 / 25 px grids, 258 / 1,134 / 4,524 attacks, 0 failing, worst
  nearest clear floor 90 / 120 / 120 px, tightest escape margin 0.65 / 0.43 /
  0.43 s. A new room can still fail with a pattern that passed on the bare floor:
  fit the boss, never the limit.
- R05_STACKS authors no cover, like R05_VAULT and R05_TERMINAL (Codex: nothing
  in the middle of the room); operation 9 authors 9 cover props (operations 1-8:
  9-15). Cover there is Codex's art work, only if the user wants it, and it
  changes the room's fairness geometry: rerun `boss_room_fairness`.
- R02_NAVE's NE door leaves a pocket about 69 px above the deck (the far edge of
  the apron is a vertical line). The alignment test passes, but a player holding
  W+D at that door can wedge in the corner and leaves with A or S. Re-tracing the
  apron outline is Codex's work (no ImageGen), only if the user wants it.
- Bot results: `full_op_09` extracted in 5 of 5 direct runs before the opening
  (161-166 s, 228-379 HP taken, 25 kills) and in the full suite on the committed
  tip (160.8 s, 25 kills, 326 HP, nobody down). Its supply branch O01_BLADES hangs
  off the elite room R04_GALLERY as in operation 8, but it carries 5 PRISMs
  against operation 8's 9 and DRONE is the largest damage source. Unlike
  operations 3 and 8, a WIPED or TIMEOUT there is not known noise.
- The full suite did not end 72/72 on the opening commit. The first run
  (`20261001_163637_full`) was 69/72: `traversal_audit` exited with code
  4294967295 (-1, which is what a killed process returns) after 764 s and passed
  twice on rerun (815 s direct, 809 s through the runner, 2,155 checks, cause of
  the first exit unproven); `full_op_07` was WIPED in R04_COMPRESSORS (140 s, its
  first loss in these records) and extracted on its rerun (220 s); `full_op_08`
  was WIPED in the boss room R05_TERMINAL in all four of that day's runs
  (139-149 s, GANTRY left at 431-629 of 1,920 HP). Nothing in the game code
  changed since the operation 8 opening reaches operation 8: the diff to the
  opening holds `_echo_copy_attack`, the `vault` abyss and operation 9's data
  (read from `git diff`, not rerun on the old tip). The user's 2026-09-30
  decision to leave operation 8 as it is stands; retuning it or letting the
  runner retry a WIPED playthrough is still the user's call.
- Technical checks only. Human play and balance, a same-session FPS A/B for
  operation 9 (no per-operation tool exists), the look of the dark `vault`
  abyss and art approval of its plates and boss are the user's. The own-room
  captures, the 10 s game-sound clip (`SABLE_CAPTURE_MISSIONS=9
  SABLE_CAPTURE_BOSS=1` with `record_stage_battle_with_audio.py`), the fairness
  grids and the run summaries are in `qa/site7_op9_enable_20261001/`.

## Operation 10 enabled — user instruction 2026-10-02

- The user ordered operation 10 (ZERO POINT) turned on ("작전 10 켜라") after
  Claude's pre-enable check of Codex's stage E plates
  (`qa/site7_op10_preenable_20261002/`, nothing blocking). Following section 6 C
  of the design doc its `staging` block, `deployable: false` and `pending` are
  gone and operation 9's COMMAND debrief announces Zero Point. All ten
  operations are playable: `playable_complete` and `chapter_complete` coincide
  and none is held back. The held-back rules above and their `campaign_data`
  controls stay for an operation added later; they run only while one is held
  back (292 checks with ten open, 297 with one held back). `full_op_10` joins
  the runner's solo playthroughs (73 tests: 44 quick, 29 full-only), the
  live-entry smoke covers ten operations (`range(1, 11)`), and the boss capture
  shoots ORIGIN CORE in its own room R05_CORE; `TEST_BED` is empty and its
  machinery stays for the next boss.
- ORIGIN CORE was fitted to its room before the opening (`749ff72b`,
  `ORIGIN_LATE_WINDUP` 1.6 s), so `boss_room_fairness` passed on the real room
  the day it opened: grids of 100 / 75 / 50 / 40 / 25 / 20 px, 330 / 654 / 1,386 /
  2,118 / 5,472 / 8,562 attacks, 0 failing, worst nearest clear floor 120-150 px
  (limit 180), tightest escape margin 0.33 s (limit 0.25 s). The smoke clamps
  `--grid` at 20 px; the 15 and 10 px grids of the pre-enable record (15,306 and
  34,458 attacks, 0 failing, 150 px, 0.33 s) ran on a scratch copy. The limits
  are unchanged. The margin is 0.08 s above the limit and the tightest spot is
  phase 2's second attack (120 px of floor in 0.87 s against a 1.2 s warning):
  change R05_CORE's floor or cover, or shorten ORIGIN's wind-ups, and this test
  fails first.
- R05_CORE authors no cover, like R05_VAULT, R05_TERMINAL and R05_STACKS (Codex:
  nothing in the middle of the room); operation 10 authors 9 cover props
  (operations 1-9: 9-15). Cover there is Codex's art work, only if the user
  wants it, and it changes the room's fairness geometry: rerun
  `boss_room_fairness`. The room is the narrow one (named waiver, whole-floor
  short side 547 px).
- Operation 10 is the heaviest: 27 robots (7 PRISM, 5 elites), `R02_RELAY`
  costs the bot 385-408 HP in every run, and the supply branch O01_VAULT hangs
  off the boss room, so the squad cannot heal before ORIGIN CORE.
- Bot results: `full_op_10` extracted in the full suite (231.2 s, 28 kills = 27
  robots and ORIGIN CORE, 696.5 HP taken: R02_RELAY 392.5, R04_GALLERY 58.4,
  R05_CORE 245.6; ROOK was down at the end; research 606, salvage 8, fragments 5,
  depth 6, the rewards of the five direct runs before the opening, four of which
  extracted (226-238 s) and one was wiped in the boss room). A lone WIPED there is
  expected, like operations 3 and 8: rerun `--only full_op_10`. A stop for another
  reason (route, rewards, extraction) is a defect. Retuning the waves, robot
  counts or the supply branch is balance for the user.
- The full suite did not end 73/73 on the opening tip (`20261002_134410_full`,
  `e77d42c5` plus the enabling edits, 5,421 s, 70/73, `qa/` guard clean; all 44
  quick tests passed inside it). `rook_app` failed one of its 1,895 checks
  ("Actual displacement retains game speed"; 103 s against 97.5-99.5 s in the
  eight earlier runs) and passed on rerun (98 s); the cause is unproven (the test
  is real-time physics and switches `Engine.physics_ticks_per_second` between 30,
  60 and 120). `full_op_01` was WIPED in the boss room (113 s, 17 kills, ANCHOR
  left at 204 HP, its first loss in 11 runs) and extracted on rerun (121 s; 7 of
  its 11 passes end with an operator at 5 HP or less). `full_op_07` was WIPED in
  R04_COMPRESSORS (143.6 s, as on 2026-10-01) and on the first rerun (155.1 s),
  then extracted twice (234 s, 242 s), so it lost 3 of its last 6 runs. Since its
  passes of 2026-09-30 (`c249af7d`) the only game code that changed is INDEX
  SPIRE's and ORIGIN's tactics and the abyss styles, the shared data only gained
  the rows of operations 9 and 10, and its first loss predates the operation 10
  edits: operation 7's bot is marginal on this PC like operations 3 and 8, and a
  lone WIPED there is not a regression (rerun `--only full_op_07`). No limit was
  lowered and no test was dropped.
- Technical checks only. Human play and balance and a same-session FPS A/B for
  operation 10 (no per-operation tool exists) are the user's. The `null` abyss
  read almost black on the opening day; it was lifted the same day and the user
  approved that look, and then the art of its plates and boss (see "Operation
  10 void lit" and "Operation 10 art approved"). The own-room captures, the 10 s game-sound clip (`SABLE_CAPTURE_MISSIONS=10
  SABLE_CAPTURE_BOSS=1` with `record_stage_battle_with_audio.py`), the fairness
  grids and the run summaries are in `qa/site7_op10_enable_20261002/`.

## Operation 10 void lit — user instruction 2026-10-02

- The user saw operation 10's `null` abyss as almost black and asked again for
  no black background (see "Mood light"). Its row in `site7_mood.json` is lit
  now: base [0.065, 0.08, 0.112], fog [0.11, 0.135, 0.185] at 0.85, haze 0.1 (it
  was base ~0.013, fog 0.1, haze 0.045), and the style-9 block draws the grid
  line at 0.2 and its halo at 0.045 (was 0.085 / 0.012) and the red nodes
  larger and at 0.8. Measured on the six plate-edge views of
  `tools/environment/capture_site7_plate_edges.gd` (a scratch variant in the
  record also hides the plates in a second pass, to find the visible void, and
  pins the backdrop's camera so two runs are bit-identical): mean luma of the
  see-through void 0.025 -> 0.124 (per view 0.017-0.031 -> 0.094-0.158);
  operations 1-7 and 9 measure 0.062-0.107 and operation 8's dawn sea 0.175.
  The first room (R01) of operations 1-7 and 9 reads 0.028-0.046 on that scale
  and was not changed. Never return the row to near-black; `NullAbyssLit` in
  `tests/test_site7_mood_contact_compare.py` (quick `mood_contact`) pins the
  numbers that made it black, with the old row as its negative control. It
  guards numbers, not pixels: judge the look on a real frame.
- A lit abyss exposed a mask leak. The void rule (a pixel no brighter than
  `VOID_MAX`, joined to the image border) also reaches through narrow dark
  gaps into near-black walls, so the dark recesses between their pipes and
  pillars were see-through and showed the abyss as blue-grey patches (against
  black nobody could see them; 4-5 % of the void of operations 4, 5 and 10).
  An abyss row's `void_fill_px` (operation 10: 28) keeps void that does not
  reach the border through a passage wider than twice that opaque
  (`outer_void` in `build_site7_mood_light.py`): only operation 10's 15 masks
  changed (the other 135 are byte-identical), the plate pixels, the threshold
  and every other mission are untouched, and the wall renders as painted. The
  dawn contact field (`contact_shadow_px`) stays the answer for a bright sea.
  `VoidFill` in the same test has a synthetic plate with a negative control and
  checks that operation 10's stored masks hold no such pocket while operation
  5's plain masks do. A mission whose abyss is lifted later needs the same look
  at its walls.
- Same-session rotated FPS A/B of the abyss quad alone (HEAD shader and row
  against the new ones, one window at 1080p, vsync off, RTX 4070 SUPER,
  `gl_compatibility`, 5 rounds x 2 views x 3 s): 213.1 against 214.8 fps and
  2.153 against 2.147 ms of GPU time, no difference. It is the abyss only, not
  an operation's FPS. Numbers, tools and the before/after views are in
  `qa/site7_null_abyss_20261002/`.
- User approval 2026-10-02: after the report and the before/after sheet
  (`qa/site7_null_abyss_20261002/before_after_sheet_1920x1684.png`) the user
  answered "승인한다". It approves the lit look of operation 10's `null` void
  as measured above, and nothing else: not the first rooms of operations 1-7
  and 9, not balance or play (the plates and boss were approved by a second
  reply, see "Operation 10 art approved"). A later change to the row's colours
  or to the style-9 constants is the user's to see again; the tests still guard
  numbers, not pixels.

## Operation 10 art approved — user approval 2026-10-02

- The report after the void approval named operation 10's 15 plates and the
  ORIGIN CORE art as not yet approved; the user answered "판·보스 그림까지
  승인". The approval is for the art as it was in the game at `312c18fb`, bound
  by SHA-256 in `qa/site7_op10_art_approval_20261002/approved_art.json` (17
  files): the 15 GAME plates `assets/environments/site7_v2/stage10/S10_*/
  S10_*_GAME.png` (rooms R01-R06, O01, O02, connectors C01-C07) and
  `assets/enemies/stage10_origin_core/authored_core_v1/ORIGIN_CORE.png`, which is
  byte-identical to `motion_lab_v1/art/site7_enemies_raw/origin_core_master.png`.
- It is not an approval of balance or play, of the cover props, of robots shared
  with other operations, of the code-drawn effects, or of any other operation's
  plates, bosses or first-room void. The mood rows are runtime data over the
  plates and were seen as they stood at that commit.
- A plate or master that is regenerated, re-exposed (S8_O02 was, on 2026-09-30)
  or edited is new art the user has not seen: the approval no longer covers that
  file and the user sees it again. `python
  qa/site7_op10_art_approval_20261002/tools/verify_hashes.py` reads the 17 files
  and names any that changed (exit 1; a changed file is not a game error).
  Codex's records of "plates adopted" or "ImageGen attempt" stay what they were
  and do not replace this approval.

## Expansion after operation 10 — user instruction 2026-10-03

- The user gave items 1-3 of the 2026-10-03 expansion recommendation to Codex and
  limited Claude to review ("1-3번 작업도 코덱스 시킬꺼야. 넌 검수만 해"): (1) a
  variety pack of new room hazards and elite variants, their themed placement in
  operations 6-10 and an optional room rule; (2) the run contract made visible
  and choosable at the briefing, plus a REDLINE replay tier for cleared
  operations; (3) the five new bosses' intel opening analyses, modules and
  weapons. Work order and acceptance criteria (ids C-, V-, K-, L-):
  `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md`. Base commit
  `dca7ef20`; the items go in order 1, 2, 3, each reported, reviewed, then
  followed by the next.
- Claude's review is reading, re-running, independent measurement, breaking each
  new rule on a scratch copy and a PASS/HOLD per criterion with numbers. Defects
  go back to Codex; Claude writes no feature code. Claude still writes the
  measurement and audit instruments (a per-operation same-session rotated FPS
  A/B, hazard escape grids, the run-contract golden compare), its own tests, the
  docs and this file.
- No new art: all three items are code, data and UI. Anything that needs a
  picture stops and goes to ImageGen under its own order. The 17 approved
  operation 10 files stay byte-identical (`verify_hashes.py`).
- The limits stay: boss fairness and the pinned wind-up floors,
  `upgrade_economy`'s bands and `LEGACY` prices, the x2 clamps, "telegraph before
  damage" for hazards and elites, robot art never tinted. Expected counts in
  existing tests may be widened, never reduced, and every changed constant is
  listed in the item's report.
- Placing new hazards and variants in operations 6-10 is a difficulty change:
  it lands as one commit of its own so a single revert restores today's
  difficulty, and operation 10 gets nothing new by default. REDLINE's
  multipliers and rewards and the new modules' and weapons' numbers are
  proposals for the user; no human play is recorded on this PC
  (`playtest_logs/` is empty). A technical PASS approves no art, balance or play.
- `m11_run_contract_smoke.gd` was not in the runner at `dca7ef20` (it passes in
  10 s run alone); item 2 registers it as `run_contract`. The save schema rises
  once per item that changes saved fields (4, then 5, then 6) and every older
  save, including the player's schema 3, must still load.
- Item 1 (variety pack) was built by Codex (`602162a0` elite variants BROODING
  and BEACON, `50a9dc9b` hazards SPORE_CLOUD, FROST_PLATE and RAIL_LANE,
  `5cb3e012` the placement, `36ccff9a` escape grids and captures, `a6eb1d35` its
  report) and reviewed by Claude on 2026-10-03:
  `qa/expansion_item1_review_20261003/REVIEW_KO.md`. The placement commit
  touches only `data/missions/MIS_CH01_06.json` to `09.json` (operations 6-9;
  1-5 and 10 are unchanged), so reverting that one commit restores the
  difficulty before item 1. The first review was HOLD on two defects in Codex's
  tests, not in the rules: `elite_expansion` compared only `Sprite2D`
  descendants, so a tint on the root actor or on `HighResVisualRoot` went
  unseen (3 of 3 such mutations missed, 3 of 3 sprite mutations caught), and
  `variety_placement` compared against `dca7ef20`, so any legitimate later edit
  to a mission file failed it (shown with a +1 health edit to operation 3).
  Codex fixed both in `753cf029` (the two tests, three `.gd.uid` files and
  `hazard_expansion` moved into the quick suite, now 47 quick + 30 full-only;
  no game code or data) and Claude broke them again on a scratch copy: all 19
  elite mutations are caught (the three ancestor tints now fail 170-180 checks
  each) and the placement test behaves in 14 of 14 cases (later health, asset
  or themed-hazard edits pass; real violations and other commit pairs fail; a
  missing commit skips only the history class). V-02, V-08 and V-30 are PASS and
  item 1 is a technical PASS (the whole suite was run once when the
  navigation fix landed: see the next bullet). Everything else passed at `a6eb1d35`: quick 46/46,
  full-only 21/21, hazard escape grids 0 failing (tightest spot SPORE_CLOUD
  0.37 s at a 10 px grid, limit 0.25 s), 17/17 art hashes, 20 paired bot runs
  with no new failure kind and no damage from the new hazards (bots are not a
  balance judge). Open and non-blocking: the placement test prints its skip
  reason only with `-v` and names the commit by 8 hex digits (order section
  9.7). No art, balance or play approval, and keeping or reverting the
  placement, SPORE_CLOUD's pale ring and the next items are the user's calls.
- Navigation dead ends (found in that review, older than item 1; fixed by Codex in
  `48a0bd28`, reviewed 2026-10-03, `qa/nav_pockets_review_20261003/REVIEW_KO.md`):
  70 floor cells in 4 combat rooms (operation 1 R02_CORRIDOR 23, operation 5
  R05_CARRIER 9, operation 9 R04_GALLERY 23, operation 10 R04_GALLERY 15) where
  `CoverNavigation.direction` returned a zero vector, because `_fixed_nodes`
  dropped cover-corner nodes that fell off the floor and left no node in a wedge
  thinner than an operator. An AI follower or the full-operation bot standing there
  never moved; a player on WASD walked out. It was the cause of the baseline
  `full_op_09` 600 s stall Codex recorded. The fix changes what blocks a route:
  the inflated cover AABBs are now only a broad phase, and a segment that clips
  one is asked of the physics world (`_physics_ground_clear`: the actor's own
  collider, `GROUND_MARGIN` 3 px, collision layer 1 = cover props and sealed
  bulkheads, answers cached per canonical endpoint pair), then the exact floor
  test; `_fixed_nodes` keeps a floor-projected escape node for an off-floor padded
  corner, and `LaneRoutes` takes its nodes from `_fixed_nodes` so it still gives
  `_plan`'s route lengths. **An obstacle list passed to `_clear_ground` is no
  longer authoritative:** a rectangle that exists in no physics body blocks
  nothing (game callers always pass `ground_obstacles(actor)`; a test needs a real
  body, or an actor without a collider / off a battle floor, which keeps the box
  check). Visibility is a strict superset of before: 26 of 30 combat rooms route
  differently, 7.5 % of the operator cells (12 px grid) turn more than 2 degrees,
  8,309 cells get shorter by 8.7 px on average and none longer (robots, whose
  collider is 4 px wider, the same), spawn slots and hazard escape grids are
  unchanged; the planner alone costs x1.34-1.37 (about +45 us per plan, audit
  x1.05-1.12). Robots and followers therefore turn cover corners a little closer
  than before: a difficulty change nobody has played. Bots, alternating serial
  pairs (`qa/nav_pockets_review_20261003/`): operation 6 extracted 4/5 before the
  fix and 3/5 after it, operation 10 1/3 and 0/3, which is within noise (the
  same pre-fix planner extracted operation 10 in 4 of 4 runs of the item 1
  review and in 1 of 6 in this one: this PC's load moves bot outcomes more than
  the fix does). The bot never stalled (0 `NAV_ZERO_STALL` in 31 runs).
  `tools/environment/audit_nav_pockets.gd` (runner `nav_pockets`, full-only, solo,
  400 s; 12 and 8 px both 0 cells, 70 on a copy with the fix reverted) keeps it
  fixed. Review result: N-01 to N-07 met, but the fix turned two quick tests red
  because they were pinned to the old planner, not because of the game:
  `combat_query_fastpath`'s frozen reference planner (`ref_plan`) and
  `hazard_expansion`'s negative control that passed a synthetic 1000 x 1000 box
  (order sections 9.8 and 9.9, B-3 and B-4). Whole suite at `4e3ac9e6`: 74/78
  (`20261003_170533_full`, 5,202 s, `qa/` guard clean): those two plus
  `full_op_06` and `full_op_08` WIPED once in their boss rooms, both extracted
  on a `--only` rerun. Codex repaired the two test files in `89d30934`: the
  reference planner follows the new rules (an independent copy that reads only
  `CORNER_CLEARANCE` and `MAX_GRAPH_EDGE`; 324 of 324 plans bit for bit), the
  old one stays as `ref_old_*` with a "new route no longer than the old one"
  check (31 -> 34 checks), and the control stands a real layer-1 `StaticBody2D`
  up while it asks. Claude re-checked it on 2026-10-04 (`REVIEW_KO.md` section
  9): whole quick suite 47/47; breaking the planner on a scratch copy turns
  `combat_query_fastpath` red for 5 of 7 variants (reverting the fix included),
  and `hazard_expansion` goes red again without the body. **N-1 is a technical
  PASS and item 2 may start.** Reverting `48a0bd28` alone would now turn quick
  red: revert the two tests with it. Open and non-blocking test notes: N-9 (the
  control's box covers every candidate of 26 of 28 hazards, so only the two frost
  plates depend on the body), N-6 (the `LaneRoutes` edit is unguarded), N-7
  (`noswap` survives), N-4 and N-5 (order sections 9.7 and 9.9).
- Item 2 (run contract choice + REDLINE) was built by Codex (`e091e25f`
  implementation, `b4aa2ae0` record, `qa/expansion_item2_20261004/`) and reviewed
  by Claude on 2026-10-04 (`qa/expansion_item2_review_20261004/REVIEW_KO.md`,
  order section 9.10). `RunContract.offers(run_id, mission_id)` returns the
  shipped default (`build(run_id)`, byte-identical to `7b26a152` for 472 run ids)
  plus two other hazard cards on the same opportunity; `redline(run_id)` is a
  fourth choice offered only on a cleared operation (HP x1.35, damage x1.25, speed
  x1.12, attack gap x0.85, all three rewards x2.40; bosses keep their movement and
  warning timing; Codex shipped the upper end of every proposed range, see below).
  The contract is still never saved; `redline_cleared` is (schema
  5, sanitised on load, v3 and v4 saves load unchanged). The briefing shows the
  choice in place of the COMMS panel and DEPLOY with no input deploys the default.
  Technical results: whole quick 52/52 (579 s), a flow audit over all ten
  operations (1,473 checks), 3,640 offer cells without a violation, five saves
  read the same by old and new code, `boss_duel` with REDLINE damage on unchanged
  shapes and wind-ups, 40 of 46 broken copies of the new rules caught (one of the
  other six is harmless, five are test gaps whose rules are correct). **HOLD on one
  defect (B-1):** `GameFlow.deploy_mission` dropped `last_run_contract["mission_id"]`
  and the full-only `campaign` test reads it
  (`site7_campaign_progression_smoke.gd:60`), so it stopped with a script error that
  the quick suite cannot see. Codex fixed it in `125be138` (the restored line; the
  three `contract_ui` checks still compare whole dictionaries, with `mission_id`
  added); `campaign` (235 checks) and `contract_ui` (484) pass, K-01 is PASS, and
  K-13 (the full suite on the final tip) is open. REDLINE numbers (order section
  9.11): the user delegated them on 2026-10-04 ("네가 알아서 해줘") and then told
  Claude to make the edit itself ("수정부터 해"), the one place in items 1-3 where
  Claude edited game code: HP x1.35, damage x1.25, speed x1.12, gap x0.85 (Codex
  shipped x1.5, x1.35, x1.15, x0.8), rewards unchanged at x2.40, in a commit of its
  own (`4158aaaa`; revert it to restore the earlier setting). Reason: the standard
  cards pay 0.53-0.72 hazard reward per unit of added hit intake (HP x damage /
  gap) and REDLINE paid 0.39; it pays 0.61 now. The boss warning hit is 25 (standard
  worst 24, earlier 27); the hits that bring a squad member down are unchanged
  (ASTER 4, ROOK 6, MICA 5). Research payout at maximum lab stays x4.13 against
  x2.73. The three offers still differ only by hazard card (research reward spread
  3-6.5 %), by design (one recovery priority across the cards), and are left as is.
  Bots on operation 1 are not a scale: the earlier values extracted 0 of 3 in one
  session and 2 of 2 in the next (no upgrades), and the other settings tried
  extracted 9 of 9 (11 runs, stopped when the user needed Godot for another job;
  `qa/expansion_item2_review_20261004/redline_numbers/`). Open and non-blocking:
  legacy `tools/validate_m11_run_contract.py` (not in the runner) fails on the
  literal `run_contract` in `campaign_progression.gd`, and five test gaps (order
  section 9.10, N-A and N-B). **K-13 is met and item 2 is a technical PASS**
  (2026-10-05, `04eba6c3`, order section 9.12,
  `qa/expansion_item2_review_20261004/full_suite_final/`): 81 of the 83 tests
  pass, in three runs: the first (`--suite full`) was stopped after 53 tests
  because the user needed Godot for another session, the second ran the 30 that
  had not finished (28 pass), the third reran the two failures (both fail again).
  The seven Godot tests that had been waiting (`battle_flow`, `combat_entry`,
  `deploy_warmer`, `hazard_expansion`, `m13_campaign`, `m13_migration`,
  `m13_runtime`) all pass, the `qa/` guard found 0 changes in runs 2 and 3, and
  the first run has no guard or exit codes (its 53 passes are read from the
  logs). The two failures are `full_op_06` and `full_op_10`, bots wiped in the
  boss room twice each (ORIGIN CORE left at 811 and 981 of 2,460 HP after 27 and
  25 robots, AERATOR TOWER at 504 and 512 of 1,560). All ten playthroughs ran on
  an empty contract (technical run ids), and the only combat-side lines item 2
  added pass a neutral contract through unchanged (`RunContract.enemy_modifiers`,
  `EnemyActor.apply_run_modifiers` reads four multipliers), so item 2 does not
  reach these bots. Since the navigation fix they have won 3 of 7 (operation 6)
  and 0 of 5 (operation 10) on this PC, against 4/5 and 1/3 before it, but bot
  results swing with PC load (the same planner won 4 of 4 in one session and 1 of
  6 in another), so whether the cause is the navigation fix, item 1's placement
  in operation 6 or load is unmeasured. Retuning them, or letting the runner
  retry a WIPED playthrough, is the user's call. No art, balance or play
  approval; the numbers stay provisional until a person plays REDLINE.
- Item 3 (boss intel becomes equipment) was released to Codex on 2026-10-06
  (the user asked for its prompt); the paste-ready message, the corrections to
  the first spec and the recommended content are order section 9.13. Two things
  in the first spec were wrong and the code rules: samples come out when a robot
  is *defeated* (`_award_enemy_intel`, once per `enemy_id` per run, key picked by
  substring), so the five new bosses' keys must be tested before `"BOSS"`; and the
  three intel keys are spelled out in about a dozen places (`campaign_progression.gd`,
  `story_stage_01.gd`, whose `lost_intel_samples` sums three literal keys, the
  stage HUD, the results screen and the lobby). Modules stay one slot per
  operator (the save shape gains five sample keys and more analysis rows, no
  more). Weapons are stat rows whose effect families come from the operator's
  art profile, so a new weapon needs a row-level `projectile_profile` /
  `hit_vfx_profile` and an id with no existing family token (`ASTER` would pull
  in ASTER's authored projectile). The recommended content is a proposal for the
  user: five analyses (research 140 / 160 / 180 / 200 / 220, sum 900 of the 952
  headroom, one sample each) opening five time-type modules (SPORE FILTER, FROST
  LENS, RAIL SPOOL, ECHO RELAY, NULL ANCHOR) and two weapons (RAIL CARBINE, NULL
  BREACHER; at most 100 burst / 78 sustained DPS, never above the operator's best
  sustained). Save schema 5 -> 6 with a v5 fixture written from `381ef0fb`
  before the bump; `contract_save`, `m10_persistence`, `m13_migration` and
  `m13_loadout` pin the old shapes and are widened, never loosened. Same rules
  as items 1-2: Codex builds, Claude reviews, no new art or sound, no limit
  lowered, one whole quick run at the end plus `--only m10_intel,m13_loadout,
  campaign`, and Claude runs the full suite. No art, balance or play approval.
- Item 3 was built by Codex (`4d0a63f2` the schema 5 fixture, `fb8a5ca8` eight
  sample keys + five analyses + schema 6, `4ab13d7a` five modules, `c83ddf6c`
  two weapons with their code-drawn families, `d6094211` the paged lab and one
  module slot per operator, `98292b3d` its report `qa/expansion_item3_20261006/`)
  and got Claude's first review on 2026-10-06 (static, no Godot:
  `qa/expansion_item3_review_20261006/REVIEW_KO.md`, order section 9.14):
  **no HOLD reason, a technical PASS candidate; the verdict waited for Claude's
  own whole quick run, break-it table and full suite (now 88 tests = 56 quick +
  32 full-only) and is final in the next bullet.** Read and measured: `IntelSamples` (`scripts/core/intel_samples.gd`) is the one key
  authority (8 keys); the key of the 16 `enemy_id`s of operations 1-10 differs
  from before only for the five new bosses, and a generic `"BOSS"` test placed
  first turns all five into ANCHOR. The modules change only cooldown, duration
  and distance (-20 %, +1.0 to +2.0 s, +50 px; RAIL SPOOL's distance and ECHO
  RELAY's duration sit exactly on the +50 px / +2.0 s caps) and are read through
  `has_module` on every cast. The weapons are 57.9 / 44.3 (RAIL CARBINE) and
  96.0 / 54.5 (NULL BREACHER) burst / sustained DPS against the 100 / 78
  envelope. The new analyses cost 900 of the 952 research headroom (sink 6,080 =
  1.4873x of income 4,088, band 0.9-1.5, so a further +52 research is the most
  they can take; `upgrade_economy` is unchanged, 225 checks). The v5 fixture was
  written by the unchanged `381ef0fb` writer (git blob `cbd6062f`). Codex's runs
  on `d6094211`: quick 56/56 (494 s) and `m10_intel` 39 / `m13_loadout` 53 /
  `campaign` 235, guard clean; no check was removed (five replaced lines were
  widened, listed in its constants table) and the five boss tests keep their
  counts (163 / 978 / 2,184 / 21 / 302). Protected paths, the 17 approved art
  files and the player's save are untouched. Open non-blocking notes T-1 to T-8
  (the results screen's INTEL line touches the COMMAND bar, the VFX captures
  aim at the cursor, no minimum-font check, a per-shot profile copy, ...; the
  paste-ready polish message is order section 9.14). `sound/music/originals/
  fps_bgm_06_sniper_ridge.wav` is MP3 data named .wav since `34344749`: not item
  3's (its import sidecar was set to `keep` afterwards, see the T-5, T-6 and T-7
  bullet). No art, balance or play approval; the module, weapon and
  research numbers are proposals nobody has played.
- Item 3 verification (2026-10-06 evening, Claude; order section 9.15,
  `qa/expansion_item3_review_20261006/REVIEW_KO.md` section 8): the user closed
  Codex ("코덱스 종료다"), gave the Godot signal ("godot 돌려") and then asked for
  the code fixes first ("돌리기 전에 코드 수정할꺼 해라"), so Claude made the
  polish edits itself, the second time in items 1-3 that Claude edited game-side
  code after REDLINE `4158aaaa`: `4fd9d502` and `0a14d5b6` (T-1 results rail at
  y 416 / height 82, T-2 and T-8 captures, T-3 minimum-font check, T-4 a
  per-weapon cache of the shot profile; no rule, number, art or sound changed;
  T-5, T-6 and T-7 untouched). Outside `qa/` the tip Claude verified differs
  from Codex's `98292b3d` by 5 code files, +50 -9, and only `operator_actor.gd`
  and `mission_results.gd` of them reach the game. On the clean tip: whole quick
  56/56 (621 s); the four item-3 full-only tests (39 / 53 / 235 / 5); a
  27-mutant break-it table (all 26 real breaks caught, 25 by runner tests and
  the T-8 wait only by the native 1080p capture; the +52 research boundary,
  exactly 1.5x, stays green and +53 turns `upgrade_economy` red; the
  sample-key rules are guarded by `intel_supply` alone and each module hook by
  one check of `module_expansion`); save probes (v3, v4 and v5 read by
  `381ef0fb` and by the new code differ only in the schema number and the new
  sample keys, analyses and weapons, and round trips are stable); 0.27-0.34 us
  against 5.0-5.9 us per shot-profile call (function cost only, no FPS claim).
  Full suite on `ccfaa96e` (code identical to `0a14d5b6`; `20261006_185434_full`,
  5,268 s, guard 0/0/0): **87 of 88 pass**, and the 56 quick tests keep the check
  counts of the quick run. The one failure is the `full_op_08` bot, wiped in the
  boss room R05_TERMINAL (GANTRY left at 1,448 of 1,920 HP; the `--only` rerun
  was wiped too, at 632): two runs, two losses. Item 3 does not reach it by code
  (the playthrough starts from an empty campaign with no module, analysis or
  unlock, so every `has_module` is false) and the bot's runner record before
  this tip is 2 wins in 9, but the cause (load, item 1's placement in operation
  8, the navigation fix) was not measured and no A/B against the old tip was
  run: a few pairs of a bot that wins about one run in four cannot tell two
  codes apart. Retuning operation 8 or retrying a WIPED playthrough in the
  runner stays the user's call (2026-09-30). The bots of operations 6 and 10
  extracted on their first run this time. **Item 3 is a technical PASS**; it
  approves no art, balance or play, the module, weapon and research numbers
  stay proposals nobody has played, and no per-operation FPS A/B was run. Open:
  T-5, T-6, T-7 (closed in the next bullet) and items 4, 5 and 1D.
- Item 3 notes T-5, T-6 and T-7 closed (2026-10-06 night, Claude; order section
  9.16, `qa/expansion_item3_review_20261006/REVIEW_KO.md` section 9): the user
  asked what was left to polish ("다듬을 점이 뭐야?"), then "다 고쳐", and left
  T-6's design to Claude ("T6도 네가 알아서"), so Claude edited game-side code a
  third time in items 1-3 (after REDLINE `4158aaaa` and the polish `4fd9d502` /
  `0a14d5b6`); no rule, number, art or sound changed, and each fix is its own
  commit. T-5 (`92cc7eb3`): the stage HUD's `_intel_label` box is (924, 82)
  332 x 16 instead of (616, 82) 640 x 16, so it no longer overlaps the
  transmission panel (x 360-920, y 70-118) and still holds the 324 px worst-case
  text; the HUD's `_cargo_label` and `_optional_label` boxes also overlap that
  panel (and touch the intel box by 1 px) but predate item 3 and stay. T-6
  (`4d0ae528`): the lobby SAMPLES line shows the eight full key names again
  (`IntelSamples.named_counts`; 543 px at 12 px in its 570 px box), and an
  operator with unlocked modules gets a second 10 px line
  (`ModuleChoices_<operator>`) naming all of them with the equipped one in
  brackets; locked rows, the cycle button and the 1224 x 202 panel are unchanged.
  It is Claude's design: reverting that one commit restores the earlier lab text
  and its checks (the tree without it runs `lab_geometry` at 4,007 checks, PASS).
  T-7 (`cfcb065a`): `fps_bgm_06_sniper_ridge.wav.import` is `importer="keep"`, so
  the import step no longer logs "Not a WAV file" for the MP3 data named .wav
  (3 error lines in each of 58 earlier runner import logs, 0 in the 2 after);
  the file's name, content and the
  `qa/music_integration_20260920/source_retirement.json` record are untouched,
  and what to do with the file is item 6's. `lab_geometry` runs 5,089 checks
  (was 4,005). Nine break-it variants on the real tree: eight caught (1-42
  failing checks), the ninth (a 250 px HUD box) is an equivalent mutant because a
  Label never shrinks below its text. Whole quick 56/56 (`20261006_210605_quick`,
  531 s, guard 0/0/0; only `lab_geometry`'s check count differs from the earlier
  quick run; the five files in the tree were byte-identical to the commits) and
  the four item-3 full-only tests 39 / 53 / 235 / 5; seven native 1080p captures
  pass the validator and three were viewed. A technical check: no art, balance or
  play approval. Open: items 4, 5 and 1D, the operation 8 bot (the user keeps it
  as is) and a per-operation FPS A/B.

## Title bar, per-operation FPS and the orders for items 4 and 5 — user instruction 2026-10-06

- The user asked for the remaining items ("남은것들 해") and, in the same turn,
  whether the game is fit to hand out. Claude's verdict: a closed test for a few
  acquaintances, not yet a public release (no human play is recorded in
  `playtest_logs/`, only operation 10's art is approved, no exported build had been
  tried; one was built that night, see "Room rules and the Windows test build").
  Uploads stay blocked by the first section of this file.
- Title screen: the campaign bar placed its segments 60 px apart from x 916, so
  operations 7-10 lay past the 1280 px canvas while the counter read "10 / 10"
  (found by reading the layout, then confirmed on a native 1080p frame: 4 of 10
  segments outside). `TitleScreen.campaign_segments` now fits any campaign length
  into the bar's own 300 px box and keeps the old 60 px step up to five
  operations. `title_geometry` (quick, 116 checks) tests lengths 1-20 and the live
  title with nothing and with everything cleared; the old layout is its negative
  control (33 of 116 checks fail on it). Operation 11 needs no further change
  here.
- Per-operation FPS: `tools/maintenance/per_operation_fps.py` (driver) and
  `per_operation_fps_probe.gd` (inside Godot) measure each operation's three
  combat rooms (R02, R04 and the boss room R05) in the preview fixture: fixed
  enemies, real autofire and room hazards, no waves, no HUD refresh. A native
  1080p window on the second monitor, vsync off, and the operation order rotates
  every round so the PC's drift spreads. It refuses to start while another Godot
  or the regression runner is alive and writes to `.cache/fps_survey/`. The
  older lines above that say "no per-operation tool exists" predate it; its
  1-10 limit needs widening when operation 11 opens. Result
  (`qa/per_operation_fps_20261006/`, 4 rounds x 10 operations x 3 rooms on
  `39176d13`): 195-251 fps per operation, none flagged HEAVY or NOISY, the slowest
  (operation 9) 10 % over the median frame time and the slowest sample 148.5 fps.
  Frame time follows the number of live effects (r 0.89 over the 30 rooms, about
  0.11 ms each), not the enemy count (r 0.16). It ranks operations on this PC
  only: it is not an in-play frame rate and says nothing about slower PCs.
- Export: running from the project folder prints "Loaded resource as image file,
  this will not work on export" for every robot PNG that `Image.load_from_file`
  reads (44-46 lines a run, `site7_machine_sprite.gd:127`). A build needs the raw
  PNG, WEBP, JPG and MP3 files inside the pack. `include_filter` alone does not put
  them there (Godot packs only the imported copy of an imported file, never its
  source): they are staged with `importer="keep"`, as
  `tools/environment/build_sites_demo.py` does for the web demo, and the tool in
  the next section does the same for the Windows build. Never export with the
  default filter and without that.
- Orders for items 4 and 5 (written, nothing started; whether and when is the
  user's call): `docs/production/SITE7_EXPANSION_4_NEW_ROBOTS_CODEX_ORDER_KO.md`
  (two new regular robots, LANCER and TENDER: Codex draws the eight-yaw art,
  Claude registers them and tests the rules; placing them in an operation is a
  separate single commit and a difficulty decision) and
  `docs/production/SITE7_EXPANSION_5_OPERATION_11_ORDER_KO.md` (operation 11
  UPLINK ARRAY with the boss ZENITH ARRAY). Operation 11 keeps the id
  `MIS_CH01_11`: 32 test and tool files build ids with `%02d`, eight screen
  places read the number with `right(2)`, and the chapter is a data field
  (`chapter_id`). Its campaign row lands together with the art, not as a
  held-back row ahead of it, because a held-back row would turn the finished
  campaign's "CH01 COMPLETE" into "in preparation". Claude recommends playing the
  ten operations once before either order starts.

## Room rules and the Windows test build — user instruction 2026-10-06

- The same "남은것들 해" turn. Room rules are item 1D of the expansion order (section 3.5 of
  `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md`, review table in its section 9.17,
  record `qa/expansion_1d_room_rule_20261006/`). Built by Claude in `25fc3c31` (Codex is
  closed): the smallest reading of 1D, a pacing rule on the existing combat rooms. The
  order's own example (hold 30 seconds in the research room) needs new battle floors,
  cover and spawn rows and was not built.
- A combat room may declare `"rule": {"type": "OVERRUN", "seconds": n}` on its row, next
  to `encounter`, `reinforcements` and `hazards` (`data/progression/room_rules.json`,
  `scripts/combat/room_rule.gd`, hooks in `story_stage_01.gd` and `story_stage_hud.gd`).
  OVERRUN calls the next reinforcement wave n seconds (20-120, default 45) after the
  previous wave was called, whether or not the wave on the floor is thinned out to
  `reinforce_at`. The call is the stage's own: `_call_reinforcements()` holds the four
  lines that `_on_story_enemy_defeated` always ran (same 1.4 / 2.2 s wait, same marked
  entry points, same objective text), so a room thinned out first still calls its wave
  the old way and restarts the timer. The HUD counts down under the intel line
  (`story_stage_hud.gd` `_rule_label`, x 924-1256, y 100-118, red; hidden while a wave
  is on its way in and when none is left) and the briefing line explains the rule. A
  rule adds no damage, never touches robot art and does not change a reward.
- Boss rooms, the training simulator (`battle_preview`) and every room without the key
  behave exactly as before. A rule the stage cannot run (not an object, unknown type,
  boss room, a room with no reinforcement wave, seconds outside 20-120 or not a number)
  is logged with `push_error` and the room runs without it. **No room declared a rule
  until 2026-10-07; three do now (see "Room rules placed, art approved, Windows build
  postponed").** Placing one is a difficulty change nobody has played: it lands as one
  commit of its own (edit the mission row, nothing else) so a single revert restores the
  difficulty before it, operation 10 gets nothing by default, and which rooms and how
  many seconds is the user's decision.
- `room_rule` (quick, `tests/smoke/room_rule_smoke.gd`, 87 checks): the table and its
  limits, the validator with nine refusals, the pure timer and HUD-line helpers, every
  mission file's 80 rooms, and a live stage (the timer at its exact second, the
  thinned-out path, a room with no rule over 120 s, a two-wave room that counts from
  the wave called last, five refusals, the simulator, a room change, the HUD rectangle
  against four neighbours). It found one real defect while it was written: the
  countdown stayed one frame stale after a thinned-out call. A matrix of 27 one-line
  breaks of the mechanism (the timer's boundary, wait and reset, the tick, the
  refusals, the HUD rectangle, the data limits, mission rows with a bad rule) turns it
  red for all 26 real breaks, 11 of them through a single check, and keeps the
  legitimate placement green; the files were restored byte for byte
  (`records/mutants.jsonl`, `tools/mutate_room_rule.py` in the record).
- Windows test build (`tools/environment/build_windows_test_build.py`,
  `tools/environment/export_pack_audit.gd`; record `qa/export_trial_20261006/`, output
  in the git-ignored `.cache/export_trial/`): a staged copy of the runtime folders,
  official Godot 4.7.1 release templates (copied read only, SHA-256 checked), no
  upload, no signing. Result at `25fc3c31`: 572,173,900 B (exe 109 MB + pck 463 MB,
  726 files in the pack, 95 s to build); title, the ten battle previews and the deploy
  path boot with 0 script errors and hold 60 FPS under vsync; uncapped medians 152-221
  fps (an earlier build of the same night read 213-292: PC load, not compared); the
  pack audit finds none of 374 raw files and 278 resources missing and decodes 84/84
  images; the three native frames are exactly 1920 x 1080 and were looked at. Traps found, all
  handled in the tool: Godot packs only the imported copy of an imported file, never
  its source, and this game reads PNG, WEBP, JPG and MP3 as raw bytes, so those are
  staged with `importer="keep"`; the release template ignores `-s`, so the pack audit
  runs through the editor binary with `--main-pack` and FPS comes from `--print-fps`;
  a full-screen Godot window is 2 px taller than its monitor, so the native frames are
  grabbed as the monitor's pixels (1920 x 1082 before that fix, kept in the record).
  A closed test also needs the two files together, a SmartScreen "more info, run
  anyway" click (no signature), and the tester's
  `%APPDATA%\Godot\app_userdata\SABLE CIRCUIT\playtest_logs\` sent back, because that
  is the only balance record there is. The exit-time "ObjectDB instances were leaked"
  and "resources still in use" lines appear in project and exported runs alike.
  Technical only: no art, balance, play or release approval, nothing uploaded, no other
  PC tried.

## Room rules placed, art approved, Windows build postponed — user instruction 2026-10-07

- The user answered the room-rule recommendation, the test-build question, the art
  report and the release question in one message: "방규칙은 그대로 넣고 아직 윈도우 앱은
  안 만들꺼야. 그림은 승인할께 우선 여기까지 만하고 깃허브에 배포해줘. 이미 배포주소는
  있어".
- Room rules placed (`8218ee76`, three mission rows and nothing else): OVERRUN on the
  first combat room, R02, of operation 2 (`R02_MAINTENANCE`, 60 s), operation 5
  (`R02_DEFENSE`, 45 s) and operation 9 (`R02_NAVE`, 45 s). They were read off the bot
  traces in `qa/regression_runs/*_full/out/full_op_XX/full_operation.json`: in those
  rooms the bot clears the floor in 17-30 s and its first wave is called after 10-20 s,
  so 45 s bites only a slower player (each room has one wave, and the rule ends with it);
  the squad loses a median of 60 / 93 / 116 of its ~346 HP there (operations 6, 7 and
  10: 226 / 419 / 343); and the bots of operations 2, 5 and 9 had extracted in 11 of
  11, 11 of 11 and 4 of 4 recorded runs. Operations 1, 3, 4, 6, 7, 8 and 10 get nothing
  (the bots of 3, 6, 7, 8 and 10 are marginal on this PC), and no elite room, boss room
  or second wave carries a rule, so the rules are spread through the campaign and a
  further placement is a new difficulty decision for the user. `git revert 8218ee76`
  restores the difficulty before it. Nobody has played the placement: rooms and seconds
  are proposals the user may change.
- Checks on the placement: the 58 quick tests plus `full_op_02`, `full_op_05`,
  `full_op_09` and `campaign`, 62 of 62 PASS (`20261007_174753_custom`, 1,085 s, `qa/`
  guard 0 changes; `room_rule` 87 checks unchanged, `campaign` 235). The three bots
  extracted (wall time 122 s, 159 s and 172 s) while a Godot 4.7.2 of another job ran
  beside them part of the time. A bot never meets the rule (it thins each floor out
  first), so this proves the data loads and nothing regresses, not that the countdown
  feels right.
- Art approved (`qa/art_approval_20261007/`): the user answered the report that named
  operation 10 as the only recorded art approval with "그림은 승인할께". The scope was not
  listed, so it is read as every raster picture the game draws: the 251 tracked PNG and
  WebP files under `assets/` and `motion_lab_v1/public/assets/atlas/` (the 150 GAME
  plates of operations 1-10, the ten bosses, 34 regular-robot views, the 51 atlases of
  ASTER, MICA and ROOK, five cover and lobby props, the ASTER projectile), bound by
  SHA-256 as they were at `8218ee76` in `approved_art.json`. `python
  qa/art_approval_20261007/tools/verify_hashes.py` reads them and names any that
  changed (exit 1; a changed file is new art the user has not seen, not a game error)
  and lists pictures added since as NEW (not a failure); it reads 251 of 251 unchanged
  today, and its three negative controls (a flipped hash, a missing file, a dropped row)
  behave as written. The 16 runtime files of operation 10's record are inside with the
  same hashes; that record and its 17th file (the ORIGIN CORE source master) stay as
  they are (17 of 17 unchanged). This is not an approval of balance or play, sound,
  music or the intro video, code-drawn effects, SVG icons, source and working pictures
  the game does not draw (`art_src/`, `motion_lab_v1/art`, the `qa/` evidence images),
  or any picture added or changed after `8218ee76`. If the user meant fewer pictures,
  the record is cut down to them.
- Windows build postponed: the user will not build or hand out the Windows app yet. The
  tool, the record and the git-ignored `.cache/export_trial/` output stay; nothing was
  deleted, uploaded or given to anyone.
- GitHub, named by the user the same day ("comicman081-collab/sable-circuit 여기에 올리고
  공개로 바꿔줘", then "액션 최소화하고 pages 에 용량 찌꺼기 남기면 안된다"): the first
  section's "No GitHub push, PR, Pages or Actions work" is lifted for exactly this
  repository and the actions recorded in the GitHub bullets below; it stays in force for
  everything else (a new push, another branch, a PR, a workflow, Pages). First upload: seven
  root-less snapshot commits (`d3bbb838` to `3aab19cd`, authored with the GitHub noreply
  address) pushed one after another to the NEW branch `release/2026-10-07` of
  `comicman081-collab/sable-circuit`, 22-42 s each
  (`.cache/claude_scratch/place_rules/build_public_snapshot.py` and `push_chain.sh`); the tree
  is 3.21 GiB, over GitHub's 2 GB per push, hence five parts, and the last two carry the
  records. The local history ends in a shallow root (`9bf6487f7`, parent pruned), which is why
  snapshot commits are pushed instead of the commits. GitHub warned that the two intro videos
  (52.3 and 53.1 MiB) pass the recommended 50 MiB; nothing was rejected. The user then asked
  for the warning to go (next bullet), so that chain is on no branch any more.
- Re-upload below the recommendation — user instruction 2026-10-07 ("괜히 경고 받지 말고 권장
  이하로 압축해서 다시 올리고 이 전 건 지워. 그리고 첫화면은 바꿔줘."), asked after Claude had
  answered that a file over 50 MiB is only a warning and costs nothing (100 MiB is the hard
  stop; no Git LFS is used here). Only the public copy changed: `assets/cinematics/sable_intro.ogv`
  went from 52.31 to 45.82 MiB and `sable_intro_original_bgm.ogv` (the file `demo_intro.gd`
  plays) from 53.07 to 46.57 MiB. Video: Theora by libtheora (ffmpeg 7.1 of the `imageio-ffmpeg`
  package), two passes, 6,500 kbit/s, keyframe distance 48 (the originals: about 7.3 Mbit/s and
  a keyframe every 12 frames), 1920x1080, 24 fps, yuv420p, 1,440 frames, 60.0 s as before.
  Against the originals over all 1,440 frames: PSNR 46.97 dB (worst frame 43.58 dB), SSIM 0.9907
  (worst 0.9809), and three side-by-side views looked at (a whole frame, two 1:1 crops) showed no
  visible difference. The BGM file's Vorbis stream is the original's, packet for packet (equal
  bytes, sample count and RMS), and its video packets equal the plain file's. At this rate
  libtheora codes nothing in the near-black end hold (frames 1437-1439 differ from frame 1436 by
  at most 2 levels), writes zero-length duplicate packets for them, and ffmpeg's libtheora wrapper
  drops those, so a plain encode ended at 1,437 frames (59.875 s; padding the input changed
  nothing). The original's own three tiny packets for those frames (158, 70 and 52 bytes) were
  appended instead: frame 1436 is a keyframe in both streams, so they refer to the same picture.
  The files under `assets/cinematics/` in this working tree are the unchanged originals (the tools
  that build or read the intro still use them); the public tree is this tree except for those two
  files, so a hash of them taken from a clone differs from the local one. Whether the game itself
  should ship the smaller files is a separate decision (the intro video is outside the art
  approval of 2026-10-07). Scripts, logs and checks (`verify_public_videos.py`, 17 checks, all
  PASS; `quality_check.py`; `stitch_tail.py`; `verify_remote.py`) are in the git-ignored
  `.cache/claude_scratch/intro_public/`.
- The replacement: root commit `0d798557` (tree `564a28ad`: the local `b5751520` tree with the two
  videos swapped) went first to a temporary branch `release/2026-10-07-staging` (about 46 MiB of
  upload, because the shallow local repository sends only objects the old tip does not hold; no
  large-file warning), then `release/2026-10-07` was moved onto it with `--force-with-lease`
  against `3aab19cd` (the one forced update of this work, ordered by the user with "이 전 건
  지워"), and the staging branch was deleted. Read back through the API: tip, tree, no parent,
  both files under 50 MiB. The seven earlier snapshot commits are on no branch any more; GitHub
  keeps commits that nothing references reachable by their hash until its own cleanup, and only
  GitHub support can purge them sooner (not requested). `main` (`743af6b0`) and the 21 other
  branches were not touched. One small snapshot commit with this record sits on top of it (a
  fast-forward). Later changes go out only when the user asks, again as one small commit on top;
  replacing the branch again needs the user's order again.
- The four kArchive props taken out — user instruction 2026-10-07 ("빼줘", the answer to Claude's
  offer to upload again without them, made after the kArchive question in the last bullet).
  The public copy no longer holds
  `third_party/karchive/site7_props_20260919/{barrier,cabinet,crate,generator}.glb`; their
  `ATTRIBUTION.txt`, `WEB_TERMS_20260919.txt`, `bundled_LICENSE.txt` and
  `model-license-manifest.json` stay in it. The local files stay too and nothing in the working
  tree changed: `tools/environment/render_karchive_props.py` and `prepare_karchive_props.py`
  read the GLBs and the manifest binds their hashes (a search of `scripts`, `scenes`, `data`,
  `tests`, `tools` and `docs` finds no other reader; the game draws only the renders in
  `assets/environments/site7/karchive_props_v1/`, which stay public). The five other `.glb`
  paths (the Tripo reference and Quaternius UAL 1 and 2) stay public: the order named only the
  four. Method as in "The replacement": `.cache/claude_scratch/intro_public/
  build_public_snapshot_v3.py r1` built the root commit `c6d8782d` (tree `c57b49c4`: the tree
  of the local `a54442a2` with the two re-encoded videos and exactly those four paths deleted;
  no parent, so the removed blobs are not in the new history; its diff to the previous
  snapshot's tree `32fac9ca` is the four `D` lines, and none of the four blob ids occurs
  anywhere in the new tree). A thin shallow pack against the old tip is 893 bytes. It went first
  to the temporary branch `release/2026-10-07-staging` (no large-file warning) and was read
  back from GitHub (`verify_remote_v3.py`: tip, tree, no parent, the kArchive folder holding
  only the four text files, five `.glb` paths left, none of the four blob ids among the 11,327
  tree entries); then `release/2026-10-07` was moved onto it with `--force-with-lease` against
  `fafcad70` (the second forced update of this work, ordered by "빼줘") and the staging branch
  was deleted. The default branch showed the complete copy until that one ref update, so the
  public copy could be cloned and downloaded throughout. Read back afterwards: public, default
  branch `release/2026-10-07`, intro videos 48,041,680 and 48,834,408 bytes (under 50 MiB),
  `main` (`743af6b0`) and the 21 other branches untouched, 0 forks, stars and watchers, 7 open
  items (the August pull requests), Actions 0 runs / 0 artifacts / 2 workflows, no deployment,
  release or environment, and the Pages API and `comicman081-collab.github.io/sable-circuit/`
  both 404. The seven first snapshot commits, `0d798557` and `fafcad70` are on no branch and
  still hold the four files: GitHub keeps commits that nothing references reachable by their
  hash until its own cleanup, and only GitHub support can purge them sooner (not requested).
  The web demo on ChatGPT Sites never held the files: `tools/environment/build_sites_demo.py`
  stages only `scripts`, `scenes`, `data`, `assets`, `sound/music/runtime`, the motion atlas
  folder and `project.godot`. One small snapshot commit with this record goes on top (a
  fast-forward); replacing the branch again needs the user's order again.
- Playable link — the user asked on 2026-10-07 for the game-run link ("게임 실행 링크로 줘").
  The repository is source, not a playable site (Pages stays off), so the link is the ChatGPT
  Sites web demo `https://sable-circuit-demo.comicman081.chatgpt.site`, public since the user's
  choice of 2026-09-20 (`qa/demo_web_20260920/deployment.json`,
  `qa/music_integration_20260920/deployment.json`). It answered HTTP 200 on 2026-10-07 and its
  loading text reads "five-operation demo". The local Sites checkout `web_demo` was last
  committed on 2026-09-23; its `dist/` holds a later build of 2026-09-25 that is uncommitted,
  and operations 6-10 opened from 2026-09-29, so the last web build recorded in the repository
  (`qa/web_build_20260925`) predates them. A new web build and publish
  (`tools/environment/build_sites_demo.py`, `docs/WEB_DEMO_20260920.md`, 256 MiB archive limit,
  reuse `web_demo/.openai/hosting.json`) is an outward action for the user to order; never
  through GitHub Pages.
- First screen: since 2026-10-07 the default branch is `release/2026-10-07`, switched in the
  user's own signed-in in-app browser on the user's order (Settings > General > Default branch >
  switch > "I understand, update the default branch."; GitHub answered "Default branch changed to
  release/2026-10-07"; nothing else was touched). `main` is unchanged and keeps the August state;
  replacing `main` with this tree was not done and is a separate yes.
- Actions and Pages follow `docs/GITHUB_ACTIONS_POLICY.md`: both workflows trigger only on
  `main`, `feat/**` and pull requests (`validate.yml` also by hand, `workflow_dispatch`; neither
  has a `schedule`), so the pushes started no run, and no workflow, artifact upload, Pages
  workflow, `gh-pages` branch or `.nojekyll` was added or touched. Read before the change and left
  as they were: Pages not enabled (the settings page says "Upgrade or make this repository public
  to enable Pages"), artifact and log retention 1 day (set 2026-09-10), workflows from fork pull
  requests off, default workflow permission read-only. Never enable Pages, upload artifacts or
  dispatch a workflow for this repository without the user's explicit order. Since the switch the
  two workflows sit on the default branch and GitHub lists them (2 workflows); read back that
  day through the API afterwards: 0 runs, 0 artifacts, 0 deployments, 0 releases, 0
  environments, and the Pages API and `comicman081-collab.github.io/sable-circuit/` both answer
  404.
- Visibility: Claude changed the repository to public on 2026-10-07, on the user's order, in the
  user's own signed-in in-app browser (Settings > General > Danger Zone > Change visibility:
  three confirmation clicks, no password prompt; no other setting was touched). Read afterwards
  without a login: `private` false, nothing on GitHub that could hold Pages or Actions capacity.
  The Actions settings page after the change: all actions allowed, retention 1 day, read-only
  token permissions, and fork pull request workflows now need approval only for first-time
  contributors (the public default; before the change they were off). Nothing there was changed;
  "Disable actions" or "Require approval for all external contributors" would be stricter and is
  the user's call.
- Public with it: the 21 older branches besides `main` and the seven open August pull
  requests. Their author address is `comicman081@gmail.com` in 430 of the 437 commits (the
  user's older public repos show it too; the snapshot commits use the noreply address).
  Secret check of that history on the same day (`.cache/claude_scratch/place_rules/
  public_check/`, a partial fetch of all 23 branches that skips blobs over 1 MiB): 7,088
  blobs, 6,212 of them text and 381 of them only in the older branches, plus the 437 commit
  messages. None matches an access key, token, private key, JWT or assigned-secret
  pattern; a synthetic repository with seven fake secrets is the control and all seven were
  caught. GitHub's own secret scanning shows "Disabled" in the repository's settings; it
  was not turned on (the user's call).
- Third-party originals in the public tree: `Seed-san.vrm` (VRM Public License 1.0,
  redistribution with notice), CC0 sets (Quaternius UAL 1 and 2, Blender Studio human base
  meshes) and one Tripo motion reference
  (`art_src/motion_reference/tripo_run_20260908/source/ORIGINAL_Run.glb`, 2 MB, called
  licensed in the project's documents; its terms were not re-read for public hosting; it stays
  public because the user's order named only the four kArchive props). Those four props
  (`third_party/karchive/site7_props_20260919/*.glb`) were in the public tree until the removal
  above: the bundled licence allows use and modification in personal and commercial projects
  with credit and forbids AI training, the web terms forbid reselling the originals, and
  neither names public hosting.
  The user asked on 2026-10-07 whether the four props may stay because they are not modified
  separately, not used for training and not resold ("상관 없지?"). Claude's reading was yes: the
  game draws only renders made from them, nothing was trained on them, nothing is sold, and the
  credit ("자료: kArchive / 출처: 쓰레드 dogfooter" with the licence line) is in the title
  screen's credits (`scripts/ui/title_screen.gd`). The one point neither text covers in words is
  handing the unmodified original files out for free in a public repository: not a resale, but
  not named as allowed either. This is a reading of the texts, not legal advice. Claude offered
  to leave them out and the user ordered it ("빼줘"); the licence, credit and manifest texts
  still sit in the public tree beside the gap. Taking the Tripo file out too would mean
  rewriting the branch again, which only the user can order.

## Upgrade economy — user instruction 2026-09-29

- The user asked to raise the upgrade cap or add sinks so the rewards of operations 6-10 can be spent
  (before: 1,820 research of sink against 4,088 authored by operations 1-10, and 6 salvage / 3 signal
  fragments against 56 / 28). ARMORY_CALIBRATION and LAB_SIGNAL_ANALYSIS now run to six levels. Prices and
  caps are data (`data/progression/upgrades.json`, read through `CampaignProgression.max_level`,
  `upgrade_table` and `get_upgrade_cost`); the effect stays +8 % damage and +12 % secured research per level
  in code, and both multipliers must stay inside the x2 clamp that `StoryStage01`, `GameFlow` and
  `OperatorActor` apply. Levels 1-3 keep the prices saves paid; levels 4-6 also cost salvage and signal
  fragments.
- `tests/smoke/upgrade_economy_smoke.gd` (quick `upgrade_economy`) buys every level through the real purchase
  path, checks saves written at the old cap, and keeps the whole sink (upgrades and the three analyses: 5,180
  research, 36 salvage, 18 fragments) at 0.9-1.5x (research) and 0.5-1.5x (salvage, fragments) of what
  operations 1-10 author, so changing loot or prices is deliberate. The lobby prints the next price in the
  facility button and a price too wide for it shrinks the font (`BaseLobby._fit_upgrade_button`, never below
  14 px in the test). `tools/maintenance/upgrade_economy_sim.py` models a buyer over ten operations. This is
  data sanity, not balance approval.
- No new kind of sink (armour, weapon fabrication) was added: each needs an effect, lobby space (the facility
  panel holds three buttons) and the user's decision.

## Explicit cleanup — user instruction 2026-09-28

- The user ordered every unneeded asset and test copy removed, QA videos and
  the Motion Studio test fixtures included. `tools/maintenance/retire_20260928.py`
  moved 21.4 GB into the git-ignored `_retired_20260928/`; the user deletes
  that folder. Rows are in `qa/asset_cleanup_20260928/retirement_manifest.jsonl`
  (SHA-256 per file; file count and bytes per scratch folder).
- Retired: `.cache/` scratch except `Godot/`, `tmp/`, `sites_tmp/` and Codex's
  live `diag/`; the three idle Claude worktrees (their branches stay); regression
  runs; QA captures, videos and review HTML (JSON/Markdown records and audio
  stay, as does a capture a doc cites); the Motion Studio candidate images and
  fixture specs under `motion_lab_v1/qa/`, with the two fixture-only render
  tests; v2 plate generation attempts and quarantined or superseded plate
  images; the v1 plate images and their sources. Missions 1-5 draw only v2
  plates. The base lobby's v1 plate (S02_07 continuity), the v1 props, room
  outlines, `karchive_props_v1` and the IMAGE_A quality reference stay; the v1
  rows in `site7_plate_floors.json` and `site7_room_art.json` are unused data.
- `site7_enemy_facing_smoke.gd`, `site7_machine_source_smoke.gd` and the capture
  helpers now bind the registry's reviewed spec
  (`EnemyActor.reviewed_machine_spec`) instead of the 2026-09-13 candidates.
  Tools that read retired payloads (such as `verify_stage_enemy_delivery.py`)
  are historical. Do not regenerate retired payloads to satisfy old paths.
- Git (same day, "delete everything old"): 68 old refs removed (August feature
  branches, `main`, `claude/*`, GitHub remote-tracking refs, archive tags, old
  Codex checkpoints), reflogs expired and unreachable objects dropped. History
  now starts at the 2026-09-24 cleanup commit `9bf6487f7` (`.git/shallow`);
  later hashes are unchanged. `.git` went from 6.8 GB to 2.7 GB. The full
  pre-prune database is hard-linked in `_retired_20260928/git_before_prune/`
  (`git --git-dir=` reads it) until the user deletes that folder. Details:
  `qa/asset_cleanup_20260928/README_KO.md`.

## Explicit project cleanup — user instruction 2026-09-24

- The user ordered the project committed and every asset that is no longer
  needed removed, including replaced original art; among non-runtime material
  only sound and intro-video sources are kept. Verification recordings and
  intermediate work products are removed.
- Retired payloads were moved to `_retired_20260924/` (git-ignored) with a
  per-file SHA-256 row in `qa/asset_cleanup_20260924/retirement_manifest.jsonl`.
  The user performs the final permanent deletion of that folder. Scope and
  post-cleanup verification: `qa/asset_cleanup_20260924/README_KO.md`.
- Removed: QA and Motion Studio captures/videos/review HTML, site archives,
  temp folders and `.cache/`; the old nested worktrees; Motion Studio pilots,
  dist and standalone builds; retired humanoid (rifle/shield/aberrant) art;
  replaced candidates (`art/rook/previous`, superseded drone views, loose ASTER
  identity copies); `art_src/characters` (ROOK/MICA fast pipelines),
  `art_src/pilot_v2` (ASTER local pipeline), `art_src/motion_reference` (Tripo),
  environment PREVIEW/CONTINUITY/comparison renders; `artifacts/` payloads; and
  `assets/units` except the active ASTER coil projectile.
- Kept: the runtime (`scripts`, `scenes`, `data`, `assets`, `sound`,
  `motion_lab_v1/public/assets`); current source masters with their native
  ImageGen outputs (`motion_lab_v1/art/{aster,mica,rook}` including `gait_v8`,
  `stage_enemies_20260919`, current drone/anchor raws, environment
  MASTER/RAW_NATIVE/GAME plates); sound and intro sources (`art_src/audio`,
  `sound`, `assets/audio`, `assets/cinematics`, `motion_lab_v1/cinematics`,
  QA audio); JSON/Markdown records and rejection manifests; test fixtures,
  tools and licenses.
- For the removed items this supersedes older lines below that say to preserve
  failed, retired or previous payloads. Do not regenerate removed payloads to
  satisfy historical paths. Legacy tools/tests that read removed data (ASTER
  pilot_v2 builders, Tripo, ROOK C02 and MICA fast-pipeline tools,
  `aster_v4_locomotion_preview_smoke`, `aster_sse_v2_candidate_smoke`) are
  historical. This cleanup approves no art.

## Explicit Stage 4/5 alpha override — user instruction 2026-09-20

- The user explicitly accepts the native alpha-255 interiors returned for the
  Stage 4/5 robot and boss masters. Treat these exact generated candidates as
  runtime-approved for this Stage 4/5 batch; do not clamp, key, redraw or alter
  their source bytes. This is a narrow exception for
  `qa/stage45_implementation_20260919/stage45_asset_gate.json` and the bound
  Stage 4/5 robot paths only; it does not weaken the general alpha policy for
  future characters or assets. Since 2026-09-28 the general policy itself
  allows alpha 255, so this exception no longer marks anything special.

## Enemy navigation and video delivery — user correction 2026-09-19

- Mobile enemies must complete real movement around active cover. Keep a flank
  goal across physics ticks; validate a reachable firing lane and reselect stale
  or stalled goals. Do not pass a corner before the next segment is clear from
  the actual position. Limit the last step to the waypoint distance. Narrow
  passages must remain traversable using the real collider's clearance.
  Route-edge floor checks are exact (`site7_battlefield.gd` `segment_walkable`,
  guarded by `tests/smoke/floor_segment_smoke.gd`); a sampled check let edges
  clip floor-hole corners and livelock actors. Do not return to sampling.
- CINDER must navigate to a clear ground approach before winding up a charge;
  being within attack radius across cover is not permission to stop navigating.
  Keep collision cancellation for obstacles introduced after its warning.
- Future combat videos include the actual game sound. Use
  `tools/environment/record_stage_battle_with_audio.py`: native 1080p viewport
  frames and synchronized Godot AudioServer mix. Validate 600 frames, 10 seconds,
  and a non-silent audio stream; do not deliver a silent technical clip by default.
- The regression at `tests/render/enemy_cover_navigation_regression.gd` drives
  real actor physics in all six normal combat rooms. Controlled fixtures and
  scripted video input do not imply human playtest or performance approval.
  Current repair evidence is under `qa/enemy_cover_repair_20260919/`.

## Current campaign continuation — 2026-09-19

- Stage 1 is not the development endpoint. The normal base/briefing flow now
  deploys all three authored Chapter 01 missions in order via
  `scripts/core/site7_campaign.gd` / `data/story/site7_campaign.json`.
  Assign mission ID BEFORE entering the tree so art, floor, cover, encounter,
  story and reward data agree. Do not restore `deploy_stage_01` as the only path.
- Save schema 4 preserves prior resources/loadouts. Only a full EXTRACTED run
  unlocks the successor; early extraction, wipe, preview, duplicate or locked
  mission results must not unlock/reward incorrectly. Replays remain available.
- Keep the approved 1.8x actors. All three now share current portrait references
  between base and combat. Mission 2/3 use their authored loot, not Stage 1
  fallback quantities. Robot research supplies ROOK's mechanical stress sample
  under the legacy ABERRANT save key; no retired humanoid spawn is needed.
- Every new cover placement must leave player/enemy spawns clear AND allow
  an actual around-cover route on that room's floor. A free spawn or floor-bound
  anchor alone does not prove accessibility. Preserve the measured prop size.
- `site7_full_operation_smoke.gd -- --mission=MIS_CH01_0N --out=res://qa/...`
  now obeys real weapon cooldown (`_try_fire(false)`) and the normal held-F
  revive transaction. It casts skills through real Q/E/X key presses (not
  ASTER's E dash) and logs damage by source and skill casts. Do not use
  `debug_fire_once()` as playthrough proof: it bypasses cadence and is only
  for explicitly isolated single-shot fixtures.
- Current campaign tests/evidence are under `qa/campaign_20260919/`. The legacy
  persistence tests now use unique project-local saves, never the player's save.
  This is a three-operation campaign integration, not full-game, new-art,
  Luna reproduction, external GPT-review or deployment approval.

## Enemy body-plan limit — user instruction 2026-09-19 (supersedes 2026-09-13)

- ZERO humanoid enemies. The user cancelled the rifle trooper and all humanoid
  enemies to stop spending generation resources. Humanoids are playable
  characters only. Do not resume, repair, review for promotion, build or connect
  `site7_rifle` / `site7_shield`; preserve their sources and history as retired.
- Active robot roster now includes recon drone, anchored boss, BULWARK tracked
  shield crawler (introduced in mission 1), CINDER hover ram (mission 2), and
  VESPER fixed vertical mortar (mission 3). Preserve these distinct silhouettes
  and attack roles; do not replace every normal encounter slot with a drone.
  Mobile newcomers have eight separately authored native-alpha views. Mortar
  uses one fixed vertical barrel and locked floor landing point, not fake yaw.
  New bundle/provenance and native checks are in `qa/stage_enemies_20260919/`.
- All other enemies must be non-humanoid robots. Preserve existing drone and
  anchored boss artwork. Convert the shield role to a compact tracked shield
  vehicle and the old aberrant/melee role to a legless hover-charge robot.
  No extra bipeds, quadruped gait, humanoid robot knees/feet or procedural legs.
- Keep remaining enemy warnings and rewards compatible. `ENM_SITE7_ABERRANT_01`
  is a retired legacy gameplay key, not organic-art
  authority. A visible-front robot still requires correct authored facing;
  one front image cannot be treated as an omnidirectional vehicle to save work.
- The old `site7_shield` humanoid recipe is retired from production. Preserve
  its sources/provenance; do not resume its missing gait frames. Follow
  `data/art_profiles/site7_enemy_body_plan.json` and the current Studio skill.
  This restriction applies to Luna and other models alike. Players are unchanged.

## User-authorized kArchive environment assets — 2026-09-19

- Use suitable terrain/props from `C:/ai_asset/karchive/2026-09-19` as read-only
  source assets. Copy selected GLBs into this project, bind their hashes and
  licenses, and create every conversion/cache/render here. This specific user
  authorization permits environment model use/derived prop renders; it does
  not replace character appearance authority or authorize AI training.
- Credit `자료: kArchive` and `출처: 쓰레드 dogfooter` in the app. The bundled
  license permits commercial project use/modification but forbids AI training;
  preserve that restriction despite conflicting website training wording.
- Props must be meaningful cover at the unchanged 1.8x character scale, not
  tiny decorative props. Preserve ground-only actor collision, alpha-silhouette
  projectile blocking for BOTH sides, clear bypass paths, room streaming and
  actor-compatible depth sorting. Area-of-effect boss attacks are separate;
  ordinary cover must not silently make the player immune to explosions.
- Reuse `scripts/combat/cover_navigation.gd` for cover-aware AI: followers
  bypass the actual ground footprint, drones flank before fresh telegraphs,
  and followers check the actual committed muzzle before spending ammo.
  The controlled player may still fire into cover. Preserve locked announced
  rays and projectile absorption when cover is introduced after a warning.
  `tests/render/site7_cover_ai_check.gd` and `tests/smoke/cover_navigation_smoke.gd`
  cover these behaviors; neither grants art approval or a Luna generation claim.

## Current SITE-7 drone facing repair — 2026-09-13

- `data/art_profiles/enemy_profiles.json` now binds the reviewed eight-view
  drone through `machine_asset` to `assets/enemies/recon_drone/authored_yaw8_v1/spec.json`.
  `scripts/animation/site7_machine_sprite.gd` selects the authored front and
  its illustrated emitter together. Never restore the single front illustration
  as an omnidirectional chassis, mirror asymmetric sensors, or use a QA path
  as an active app texture. Player appearance, gait and 1.8x scale are unchanged.
- Read the current Studio skill's `references/enemy-facing.md`. NPC attack
  warnings lock pose/aim through emission, unlike immediate player pointer aim.
  Invalid close-target aim must reposition, not choose a backwards shot.
  Stagger clears the warning CanvasItem itself; duplicate visible RGBA cannot
  masquerade as eight unique views merely through metadata or hidden RGB.
- App-path proof is `tests/smoke/site7_drone_app_smoke.gd`; native app captures
  use `tests/render/site7_enemy_facing_capture.gd -- --app-registry`. The
  synthetic edge-case fixtures and `site7_machine_edge_case_smoke.gd` were
  retired on 2026-09-28.
  Actual scoped observations and tests are in `qa/stage1_implementation_20260913/`.
- GPT 6 Pro round 7 confirmed the R6 three code defects were blocked after
  examining code and synthetic inputs, not by running Godot or viewing art.
  Do not describe that as full MVP, art, deployment or Luna reproduction approval.
  Rifle, shield and aberrant asset completion remain separate work.
- The stationary anchor boss now uses the reviewed central-iris artwork at
  `assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json`. Preserve
  its fixed root and central emission; this is not four independently aimed
  arm weapons. `site7_anchor_app_smoke.gd` and the `--app-registry` native
  anchor capture cover the app connection. Full-art overhead bounds are
  separate from inset damage bounds. See `ANCHOR_VISUAL_REVIEW.md` and the
  post-app capture under the current Stage 1 QA directory.
- The user-rejected rifle SE/walk/3 with a third knee/shin branch is preserved
  in `motion_lab_v1/qa/site7_rifle/quarantine/9df8e882aa9ff1b074ab4a517a6b32f210c80408a94c9ee84507f2ed7cfc94be/`.
  Its reviewed two-chain source replacement is not complete-cycle approval
  and must not activate the incomplete rifle atlas.

## Current ROOK app connection — user instruction 2026-09-13

- ROOK now joins ASTER and MICA through `scripts/animation/motion_lab_character_runtime.gd`.
  `data/art_profiles/playable_profiles.json` selects `motion_lab_character_id: rook`
  at the accepted 129.6px (original map scale × 1.8) subject height.
- ROOK's current Motion Studio portrait is shared by battle HUD and base lobby
  through the registry's `portrait_asset` / `portrait_region`. Do not restore
  the old green-keyed SE idle thumbnail or the ROOK / TEMP label.
- Keep gameplay values separate from Studio metre units: ROOK retains its
  app's 138/205 walk/run speeds, 10 rounds, .42s cadence, 1.38s reload and five
  pellets per trigger. Preserve distance-driven frame timing and reverse-walk
  selection, and refresh the authored muzzle/aim together before emission.
- Current app checks are `motion_lab_character_runtime_smoke.gd` and
  `rook_motion_lab_app_smoke.gd`; the old C02 FastRuntime smoke is historical,
  not a reason to restore the retired pointer. Evidence is under
  `qa/rook_app_integration_20260913/`. This connection grants no remote deployment
  and does not convert future Studio candidates into approved app updates.

## Explicit unused-data retirement — user instruction 2026-09-11

- The user explicitly requested quarantine and deletion of project data that is
  disconnected and will not be connected in future. The exact one-off scope,
  pre-deletion hashes and verification results are in
  `qa/asset_cleanup_20260911/`. Consult `purged_verification.json` for completed
  disposal, not the earlier planning receipt.
- Retired legacy captures, rejected production outputs and disposable fixtures
  must not be regenerated merely to satisfy old historical paths. The current
  app, Motion Studio character sources, provenance, licensed references, tools,
  and other active Git worktrees remain protected.
- This explicit retirement does not turn any historical FAIL/HOLD into PASS,
  authorize promotion, or grant blanket permission to delete future failures.
  Preserve rejection hashes and retirement manifests even after payload disposal.
- The user subsequently authorized deeper cleanup, including unreachable Git
  objects. Additional file disposal is recorded in
  `qa/asset_cleanup_20260911_additional_files/`; Git object retirement and intact
  branch/reflog/index verification are in `qa/asset_cleanup_20260911_additional/`.
  Historical diagnostic-report reference cycles are not current build dependencies.
  The rejected `assets/units/operators/mica/fast_runtime_v1` bundle is retired;
  current MICA uses `motion_lab_v1/public/assets/atlas/mica`.
  Keep live preview-server logs. No branch, reflog, or reachable history was deleted.

## Current character workflow — user instruction 2026-09-10

- New character creation, source-art repair and movement/fire fixes use the implemented `motion_lab_v1` Motion Studio route and `.agents/skills/sable-character-studio/SKILL.md`. Read its folder instructions before work, including when the task starts at this repository root.
- The user accepted the existing MICA motion prototype, requested the moving-fire facing fix, then requested a reusable system for subsequent Luna character work. Do not restart the former production harness, old MICA builders or unfinished historical jobs for these tasks. The older harness-invocation requirements below apply to explicitly requested legacy audits, not this current route.
- Keep ImageGen appearance authority, read-only local tools/models, licensing and failed-asset preservation rules. This routing update does not authorize deployments, new services, global model changes, or unrequested character generation.
- Use `motion_lab_v1/character_workflow.py` for exact source-slot status, scoped builds and current runtime/delivery checks. A receipt must match current bytes. Do not claim Luna end-to-end generation success without an actual Luna run; technical fixtures and the successful MICA implementation are not that result.

## ImageGen appearance / Blender motion boundary — user correction 2026-09-07

- ImageGen authors and repairs every visible character appearance: face, hair,
  clothing, footwear and weapon artwork. Blender/UAL are restricted to rigging,
  skin weights, pose transfer, retargeting and movement implementation while
  preserving that approved appearance. Motion-frame export is not permission
  to rebuild the character's appearance from primitives or constant materials.
- Do not use Blender to sculpt/reconstruct a replacement face, eyes, hairstyle,
  coat, boots or equipment and claim that sampling a small ImageGen patch makes
  the replacement ImageGen-authored. Missing artwork goes back to ImageGen.
- VRoid/CC0 body intake is optional motion/rig reference, not authority to turn
  its appearance into MICA or manufacture MICA's costume in Blender.
- The anatomical/skinned MICA pilot builders and runners are retired. Their
  historical build receipts do not authorize execution. Use the code-level
  `art_authority.py` policy gate; a renamed copy or `diagnostic` flag does not
  restore authority. An unimplemented source-preserving adapter stays HOLD.
- `imagegen_art_preservation` is a separate mandatory implementation/Ponytail
  check. Source SHA, commercial license and closed geometry are not substitutes.
  No existing failed source-plane/segmented gait is restored as a shortcut.
- This correction supersedes earlier construction scopes and skill examples
  that recommended fitted replacement costume, scalp or shoe geometry.

## Mandatory generation gates and reusable skill (2026-09-07)

- For character generation, repair, rigging, or motion resumption, read and use
  `.agents/skills/sable-motion-production/SKILL.md` and
  `docs/production/GENERATION_GATES_2026-09-07.md` before producing assets.
- Maintain an exact-content job and run `generation_harness.py next` before
  advancing. A valid request permits one source attempt, not an unreviewed batch.
  Source approval, actual mesh preflight, one native first pose, first-pose
  review, motion and runtime approval are distinct non-substitutable stages.
- Do not manufacture review replies or reinterpret HOLD as PASS. Apply the same
  gates with 5.6 Luna or any other model. Missing adapters are implementation work,
  not permission to fall back to warped leg images or the rejected pilot builder.
- Astra must first generate and implement a real candidate and pass the required
  generation, motion, runtime and independent reviews. Only then freeze that
  successful procedure into the harness/skill and run Luna reproduction tests.
  Do not run Luna generation or further forward tests ahead of that milestone.
  Earlier read-only routing tests are not generation or implementation success.
  Exception: the user's explicit 2026-09-13 "이제 루나로 해라" instruction
  authorizes one bounded Luna Max attempt for the named S/walk/0 repair; it
  does not waive the source gate, reference guard, quarantine or review rules.
- VRoid is user-authorized as an optional body/rig source alongside Blender+UAL.
  Keep ImageGen authority for original/repair raster art. Before using a VRM,
  check actual humanoid/skin data and exact commercial/derivative/item licenses.
  Authorized downloads stay project-local; original installed tools remain read-only.
- Bind all eight first-pose receipts and their dependency hashes into final motion
  packaging. No generation-only receipt may change production pointers.

## Mandatory motion production harness (2026-09-05)

- Read `docs/production/MOTION_PIPELINE_REBUILD_2026-09-05.md` before authoring,
  packaging, reviewing, or promoting new character motion. Use
  `tools/character_pipeline/motion_harness.py` and its versioned contract.
- `build`/`all` are candidate-only. Production pointer replacement and profile
  registration require a freshly verified, exact-content all-gate receipt.
  Neither a static atlas test nor a contact-sheet PASS authorizes promotion.
- Measure actual actor position differences, independently specified walk/run
  speed, anatomical/evaluated foot vertices, and visible barrel tips. Do not
  use the generator's foot targets, declared velocity, or socket table as their
  own visual ground truth. Missing independent evidence means HOLD.
- Before any Blender+UAL contact/down/passing pose is admitted to an ImageGen
  request, run `tools/character_pipeline/calibrate_vrm_ual_ground_contact.py`
  on the exact retarget result. Its floor must be fixed from the licensed
  target's actual neutral REST-pose sole vertices before UAL evaluation. Floor
  penetration, sideways foot-axis yaw, duplicate phase samples, or a missing
  distinct support transition is HOLD. Never use the action's global minimum
  sole height or a per-frame root correction to manufacture contact.
- Technical 18 mm phase discovery does not authorize visible-frame use. Bind
  `pose_guide_visual_promotion_contract.json` and require each actual support
  sole at no more than 4 mm above the fixed floor plus at least 15 mm evaluated
  pelvis drop from same-side contact to down. Bind the exact current gate,
  contracts, calibrator, sampled rows, capture rows, sole arrays and floor;
  another valid JSON/script is not interchangeable. Numeric PASS still needs
  independent visual and Ponytail FULL contact review.
- Use `tools/character_pipeline/visible_frame_harness_current.py` for every new
  visible-frame request and every downstream reserve/frame/seal/verify/sequence
  call. The older `visible_frame_harness.py` is frozen for existing airborne
  receipt reproducibility and must not be used directly for new production.
- A Blender/VRM render is pose/contact geometry evidence only. It must never be
  used as SABLE source illustration, visible atlas pixels, an HTML character
  layer, or runtime appearance. Every visible original/repair frame remains a
  built-in ImageGen artifact with exact project-local provenance and review.
- A prompt-only ImageGen edit cannot claim pixel-local repair. New
  `repair_failed_frame` reservations require the exact
  `imagegen_repair_execution_contract.json`, a native-size nonempty binary
  change mask, demonstrated hard-mask consumption and byte-immutable pixels
  outside that mask, plus independent implementation and Ponytail FULL review.
  Supplying a mask as another visual reference is advisory and does not satisfy
  this gate. If the selected tool exposes no enforced mask interface, keep the
  repair HOLD and change the mechanism instead of repeating the prompt.
- Required runtime matrix: 8-direction walk/run, 8x8 movement/aim firing,
  stop/resume, adjacent/opposite turns, speed switch, reload, collision/bounds,
  at 30/60/120Hz. HTML needs live input parity with the same reviewed runtime.
- The user-rejected R4 segmented MICA frames and the R22 repackage are
  FAIL_NOT_PROMOTABLE. Their rejection is recorded in
  `artifacts/quarantine/motion_rejections.json`. Do not rename/repackage them
  as a repair. The legacy MICA source-plane renderer and independent HTML
  movement template are diagnostic-only, not the production route.
- Retain all failed assets and evidence. No cleanup tool may delete rejected
  candidates merely because another build exists. Quarantine and preserve
  provenance until the existing global disposal conditions are satisfied.
- Run only bounded, owned diagnostic children with project-local output/cache
  paths; do not start repeated background render/export loops. A review HOLD
  blocks promotion, not independent diagnostic/test work.

These user-approved constraints apply to every art, animation, integration,
capture, QA, and documentation task in this repository.

## 1080p visual evidence floor

- Produce review images, contact sheets, interactive-review canvases, runtime
  screenshots, and review videos at a native minimum of **1920×1080**.
- Do not upscale a low-resolution render and present it as quality evidence.
  Record the native render/capture resolution in manifests and QA evidence.
- Runtime sprite cells may remain engine-appropriate when required for memory
  and frame-time budgets, but they must be derived from a higher-resolution
  source/master and reviewed at actual game scale inside a native 1080p frame.
- A visual gate cannot PASS from thumbnails alone.  Preserve an original-scale
  crop or panel for anatomy, hands, weapon continuity, material separation, and
  alpha-edge inspection.
- Run `tools/art_pipeline/validate_visual_evidence_1080p.py` on every current
  review image, video, and interactive HTML before submitting visual evidence.
  Its PASS verifies the container and decoding only, never visual quality.
- An HTML source by itself can only receive `PASS_STATIC_CONFIG_ONLY`.  A live
  interactive-review claim must also pass the validator with
  `--require-dynamic-capture` and a native 1920×1080 browser capture or video.

## Existing asset-production rules

- User correction (2026-09-13): every newly generated/repaired SABLE subject
  master must be an actual RGBA PNG with background alpha 0 and visible alpha
  1..255 with opaque interiors. User instruction 2026-09-28: alpha 255 is
  allowed by default ("255 is better than 254"); the old 1..254 cap and its
  per-batch alpha-255 exceptions are superseded, and nothing is clamped to 254.
  Do not generate green/chroma backgrounds,
  retry on green after transparency failure, or clamp/key a returned image to
  make it appear to satisfy native-alpha generation. Inspect
  hair, garment/boot edges and interior opacity at original scale over light
  and dark backgrounds; a PNG extension or painted checkerboard is not alpha.
  Use `background: transparent_alpha` in the exact generation request and run
  the source gate. A failed alpha/separation probe stays HOLD/FAIL, not silently
  accepted or keyed from a fake backdrop. Existing approved green masters and
  their provenance remain intact and retain exact-content historical reviews.
  Unapproved green candidates remain repair-only. New intake is enforced by
  `motion_lab_v1/source_alpha_policy.py`; the retired derivative importer only
  verifies historical provenance and rejects new chroma-source intake.
  Generation requests may reference only files already inside this SABLE
  repository. The same policy helper rejects other-project images, Codex
  managed staging, clipboard captures and locked legacy-tool paths; a managed
  staging path is accepted only for the newly returned output before it is
  copied and hash-bound into the project.
  Runtime exports always use genuine RGBA transparency. This SABLE correction
  supersedes all older green/fallback source rules for this project only.
  User-authorized exception (2026-09-13): when a bounded Luna native-alpha
  attempt has failed, one retained green/near-green result may be recorded by
  `motion_lab_v1/web_alpha_bridge.py` as `WEB_ALPHA_BRIDGE_ONLY` and sent to
  the existing GPT web conversation for matte removal. The bridge never keys,
  crops, redraws or intakes its source. Preserve the actual web response and
  run the same native RGBA alpha gate on the returned PNG before any source
  approval or runtime use; a failed web return remains quarantine HOLD.
- Outputs and generated work belong below this repository.  Existing tools and
  models outside it may be read and executed only under the user's stated
  read-only/local-model rules.
- Keep the current candidate and exactly one immediately previous candidate for
  the active review line. Any FAIL/FAIL_NOT_PROMOTABLE/rejected candidate is
  additionally retained in the project quarantine area until a completed final
  replacement exists and every required visual, Ponytail FULL, runtime,
  technical, and pointer/promotion gate has passed; only then may it be
  disposed under the global failed-asset quarantine and retirement-manifest
  rule.
- Do not promote technical QA as visual PASS.  Respect explicit visual HOLD and
  user-review gates.

## SABLE CIRCUIT source-art authority (2026-08-30 user correction)

- Codex must author and repair SABLE CIRCUIT source illustrations with its
  built-in ImageGen workflow.  This includes character masters, pose masters,
  missing-pixel restoration, backgrounds, and other original raster artwork.
- Do not use a locally installed diffusion/image model, ComfyUI pipeline, local
  inpainting model, adapter, LoRA, ControlNet, or similar local generator for
  SABLE CIRCUIT source art or visual repair.
- Blender and UAL are the permitted local authoring tools only for movement,
  rigging, pose transfer, and animation implementation based on approved source
  art.  They do not replace Codex-authored original art.  Godot remains the
  runtime integration and validation target.
- Move every selected built-in ImageGen result into this repository before it
  is referenced by the project.  After the project copy and hash are verified,
  remove the corresponding managed staging copy so generated project art is
  not left in Codex's default generated-image directory.
- Keep the selected current source-art candidate and one immediately previous
  candidate in the active line. Failed/rejected assets are retained in quarantine;
  the later global completed-replacement disposal gate overrides immediate deletion.

## ASTER shoulder-costume correction (2026-08-30 user correction)

- ASTER must not have a white shoulder armor/pauldron on either shoulder.
- Do not add a cyan shoulder stripe, gold top plate, round gold shoulder
  fasteners, underside tabs, fins, brackets, badges, studs, or replacement
  shoulder armor.  Both shoulders use the dark navy tactical fabric and the
  established suit seams only.
- Any older C01 image or manifest that shows the white asymmetric shoulder
  plate is retired as authority for the shoulder region.  It may remain a
  reference for identity and all unaffected costume regions, but the explicit
  no-shoulder-armor rule above takes precedence in every new source image,
  repair, animation candidate, runtime derivative, review, and promotion gate.
