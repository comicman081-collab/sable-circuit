# SITE-7 enemy facing: visible front, emitter and warning

## No humanoid enemies — latest user scope, 2026-09-19

Read `data/art_profiles/site7_enemy_body_plan.json`. The rifle trooper is
retired along with ALL humanoid enemies. Do not spend further source-generation,
gait or promotion work on them. Only playable characters use human gait.
The shield role becomes a low tracked shield vehicle; the legacy aberrant role
becomes a legless hover-charge robot. Keep the accepted recon drone and anchor.
Do not generate their human or four-legged walk/run cycles. Do not disguise a
second humanoid as a robot by putting armor on human legs. Keep existing role
remaining warnings and rewards. The current runtime includes BULWARK tracked
shield crawlers (mission 1), CINDER hover rams (mission 2), and VESPER fixed
vertical mortars (mission 3), alongside the accepted drone and anchor. Their
versioned bundles are under `assets/enemies/{bulwark,cinder_ram,vesper_mortar}`;
do not replace them all with the drone. Old humanoid placeholders stay disconnected.
Retain retired humanoid sources/provenance without regenerating them.

New-robot evidence: `qa/stage_enemies_20260919/`. Source alpha/provenance,
candidate rendering and app-registry checks remain separate. Current helper
`tests/render/site7_new_robots_check.gd` reads only the app registry (its candidate mode was retired on 2026-09-28):
it tests the real registry, locked warnings, emitted bullets, front/side/rear
damage, actual ram-wall collision, mortar arrival damage/avoidance and death.
Its tactics dt matrix is 30/60/120; native collision/flight runs at 60Hz. Never
describe this as a 120Hz physics or independent GPT/Luna reproduction result.

For stationary mortar placement, a free floor spawn and an abstract navigation
path are insufficient: verify reachable firing positions with the player's
actual authored muzzle. The first mission-3 mortar slot, inherited from a
moving drone, was overly screened by cover; the reviewed mission data moves
it into the accessible nearer slot. Preserve counts and per-enemy HP when
changing placement. Do not disable cover or grant damage cheats to pass a run.
The full-operation test bot uses reachable firing-lane goals, rejects goals
inside the weapon solver's nonconvergent range and commits aim before testing
the muzzle ray. This is test-input policy, not an automatic player movement change.

Tracked/hover machines need correct visible facing, root contact/hover height,
rigid-body movement, readable attack windup, emitter continuity and death QA.
Do not rotate perspective art in screen space to fake yaw, call one front image
omnidirectional, or borrow rifle feet. A master is not an eight-yaw package.

Use for the current `site7_machine_sprite.gd` and enemy combat integration.
The 2026-09-13 user screenshot exposed a front-facing drone illustration being
reused while firing toward the opposite side. An omni **emitter** does not make
the whole vehicle's visible front omnidirectional. Do not repeat that shortcut.

- Flying drones use eight separately authored yaw views (`authored_yaw8`),
  exact texture hashes and per-view root/emitter coordinates. The runtime
  rejects missing views and repeated file OR visible-RGBA hashes before publishing
  the node. Metadata and RGB hidden under alpha=0 do not create new views.
  Hash uniqueness cannot judge whether the paintings show the correct angles.
- Use the ImageGen appearance authority; do not roll a 2D three-quarter picture
  around the screen or mirror asymmetric sensors to manufacture all views.
  Inspect front versus rear surfaces, appendage count, native alpha and the
  original-scale visible emitter. The separate three-sensor cluster is not the
  lower magenta firing orb. Preserve rejected four-thruster/mirrored-lens art.
- `resolve_target` selects an authored pose and solves that pose's actual
  emitter ray together. It evaluates candidates without committing eight
  texture changes per tick. The initial frame uses the actor's current aim.
  Movement velocity may oppose aim; orbiting does not turn the gun away.
- A nearest-angle result is not automatically valid: targets inside all gun
  offsets can leave every candidate pointing backward. `Vector2.INF` is an
  explicit invalid aim, not a shot direction. Keep the prior pose and reposition;
  do not enter WINDUP, fire a zero/non-finite ray, or invent a forward target.
- At WINDUP entry, stop/bank first and freeze pose plus aim. WINDUP/BURST/LUNGE
  must not resolve a fresh target or home the advertised attack. Recovery may
  respond to the new target immediately. This is intentionally different from
  the player's latest-pointer-input behavior.
- `_enter` invalidates the Tactics CanvasItem's own cached draw commands.
  Stagger skips `step`, so redrawing only EnemyActor leaves the old warning line.
  Check the native before/after warning pixels while stagger is still active.
- Legacy mock rifle/pistol/arm pixels already rotate around their bones to
  world aim. Applying `flip_h` to them again reverses the barrel. Keep those
  pixels unflipped while that mock remains; it is not an eight-view humanoid
  appearance solution and must not replace the pending authored biped cycle.
- Anchored machines retain their own stationary emitter/root contract. Do not
  force humanoid footsteps or a yawing chassis onto the stationary boss.

Current executable checks: `tests/smoke/site7_enemy_facing_smoke.gd` exercises
8 target directions at 30/60/120Hz, opposite movement, first-frame facing,
locked warnings, real projectile creation and opposite-target recovery. It also
rejects incomplete/duplicate views and checks actual mock barrel transforms.
`site7_machine_source_smoke.gd` checks actual image binding, transformed muzzle,
hit bounds, anchor stability and death presentation. Count actual projectile
objects/emission events, not all root children (audio is a separate child).

## Cover-aware combat — 2026-09-19

The app now uses licensed kArchive props as real cover. Reuse
`scripts/combat/cover_navigation.gd`: movement follows streamed ground footprints
inflated by the actual collider offset/extents, whereas bullets and line-of-fire
checks use the visible alpha. Never replace either with the entire sprite box.
An obstacle behind the target's first damage intersection is not blocked aim.

Followers navigate around props and do not spend ammo on an occluded target;
the final check follows movement/gait/muzzle commit. The controlled player keeps
the choice to shoot at a wall. Drones with blocked aim reposition/flank BEFORE
entering a fresh WINDUP. They must not bend an announced shot around the wall,
teleport, shoot through it, or keep trying an unreachable side indefinitely.
Collision/floor correction during an announced drone shot cancels that warning.
The fixed boss remains fixed; its damaging floor AoE is not stopped by cover.
Its original eight-second final-phase guard still excludes automatic targeting,
but the machine remains a physical projectile obstruction via
`site7_guarded_targets`. Shield impacts must not grant damage/hit bonuses or
pass through to targets behind it. The health bar identifies `CORE SHIELDED`;
`tests/render/site7_boss_guard_check.gd` covers absorption and expiry.

Run `tests/smoke/cover_navigation_smoke.gd`,
`tests/render/site7_cover_ai_check.gd` (native for images), and
`tests/render/site7_environment_props_check.gd`. The latter introduces cover
AFTER a genuine warning to prove actual projectile absorption; suppression of
shot creation is not collision proof. Run the normal drone/anchor/player and
full-operation checks after shared runtime changes. Current scoped evidence
lives under `qa/cover_ai_20260919/`; no Luna or external-review approval is implied.

`tests/render/site7_machine_edge_case_smoke.gd` and its synthetic PNG fixtures
were retired on 2026-09-28 at the user's order. Its R6 close-target,
hidden-RGB duplicate and interrupted-warning cases are no longer tested; the
quick-suite `site7_enemy_facing_smoke.gd` still rejects missing, duplicate and
single-view sets.

Run native 1920x1080 captures in the real game scene and inspect all affected
view transitions. A test PASS or source contact sheet is not runtime visual
approval. `prepare_drone_directions.py` only produces isolated candidates/specs;
the app registry must not point at an unreviewed QA candidate automatically.
Keep player art, gait, 1.8x display scale and weapon timing unchanged.

## Current local app connection

The reviewed drone is now bound by `data/art_profiles/enemy_profiles.json`
to `assets/enemies/recon_drone/authored_yaw8_v1/spec.json`, with byte-identical
copies of the selected images. The app loader validates identity/spec hash and
each texture before hiding the existing visual. A failed candidate does not
erase the current visible node. Repeated configure and wrong-role intake fail.

Run `tests/smoke/site7_drone_app_smoke.gd` without disabling app intake. Unlike
the candidate smokes, it starts the normal registry path and advances actual
WINDUP-to-emission transitions at 30/60/120Hz. Capture the app path using
`tests/render/site7_enemy_facing_capture.gd -- --app-registry`. Retain the
candidate-only tests too; they still cover deliberately invalid input.

GPT 6 Pro round 7 closed the three R6 counterexamples by code/test comparison
and its own synthetic pixel/math checks. It did not run Godot, inspect the
drone art or certify this registry connection. Keep those scopes separate.

The fixed boss is also connected through the registry, at
`assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json`. Its central
iris emits; the four arm housings do not acquire independent yaw. Keep the
body/root stationary. `site7_anchor_app_smoke.gd` exercises normal app loading
and actual locked emissions. `site7_anchor_candidate_capture.gd -- --app-registry`
captures all three phases through real Tactics time advancement, with explicitly
controlled HP/attack serial fixtures; this is not a whole-operation playthrough.

For anchored-boss captures, frame the real `home_position`: the boss anchor
component restores it after an attempted fixture relocation. Require the
visible iris on-screen, not merely a decoded 1080p screenshot. The first
offscreen capture is retained as VISUAL_HOLD. Machine overhead bars use the
full transformed artwork corners, not inset damage bounds; the pylon otherwise
overlaps its health bar. `site7_machine_source_smoke.gd` covers these corners
under scaled/rotated transforms. Do not change damage bounds to fix a UI overlap.

Round8 capture regressions use `tests/render/site7_anchor_capture_smoke.gd`:
reject hidden artwork even with an on-screen iris; collect only this actor's
actual warning objects (phase2: one circle; phase3: one circle and four lanes).
Capture elapsed/windup/fired during the visible warning and impact window and
record real in-zone damage. Zero projectiles plus RECOVER does not prove a
ground attack happened. Do not label fixed-delay after-effects as a visible hit.
App-mode capture must not read a QA candidate spec; bind the normal registry's
actual spec hash. Candidate mode still explicitly rejects missing/malformed
JSON. The test-only no-warning subclass must never enter a runtime registry.
Visibility/geometry/clock checks do not replace observing the native pictures.

## Retired authored biped bridge — historical only, do not resume

The user cancelled all humanoid enemies on 2026-09-19. EnemyActor rejects biped
intake and the Studio blocks their recipes. The following describes historical
evidence only, not current production steps or a reason to regenerate fixtures.

`scripts/animation/site7_biped_sprite.gd` accepts complete eight-view Motion
Studio walk/idle profiles for the rifle role only. It validates profile
and atlas hashes (including duplicate used-frame RGBA sequence rejection), geometry,
finite muzzle coordinates and six phase starts
before publishing the visual. A spec or test fixture is not an approval receipt.
Every used idle/walk cell must contain visible alpha. Hash the ordered used
cells independent of atlas columns and unused padding, canonicalizing invisible
RGB; include cell/columns/frame count in any interpretation cache key. A valid
file hash or a nonempty whole page does not prove each displayed cell exists.
Reject nonfinite/zero derived render scales and cycle distances before creating
the visible node; finite scalar inputs can still overflow during conversion.
The unfinished rifle still has **no** `biped_asset` production registry pointer.
Do not activate its E/SE-only sources, reuse one view eight times, borrow player
pixels, or use these technical checks as the missing cycle/runtime visual gate.

The NPC metre conversion is `walkStride * displayHeightPx / heightMetres`.
For this rifle that is 100.213953px per cycle, not the player's 160px cycle or
Studio weapon timing. `EnemyActor` commits actual global displacement AFTER
`move_and_slide` and stage constraints; zero displacement selects planted idle
without advancing phase. Reverse travel changes authored phase selection, not
body parts. At warning entry, select the stopped idle pose and its muzzle
together. Preserve both through WINDUP and the actual three-round burst; the
player's immediate retargeting policy must not home an enemy's announced shot.
If a real collision/stage position correction moves the emitter during
WINDUP/BURST, cancel that announced attack through Tactics and require a fresh
normal warning later. Keep the actual correction and distance accounting;
do not keep shooting from an old position or silently retarget the old warning.

`tests/smoke/site7_biped_bridge_smoke.gd` uses explicitly synthetic coloured
cells, not production art. It exercises the 8x8 movement/aim matrix at
30/60/120Hz, real Tactics/projectile emissions at those rates, malformed/partial
intake, reverse phase, a real collision wall and the actual stage-boundary
clamp. The real collision-wall case runs at default60Hz; explicit stage
corrections during WINDUP and transition to BURST run at30/60/120Hz. Preserve
that distinction from the all-rate movement/emission tests. It checks that the
production registry stays byte-unchanged. Also rerun the normal drone, boss,
machine and player Motion Studio smokes after changing shared EnemyActor code.
