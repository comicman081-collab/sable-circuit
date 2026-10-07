# Rapid aim response — observed ROOK repair, 2026-09-13

Preserve user-accepted gait and source bytes when repairing aiming. This is
the shared Motion Studio route, not permission to recreate art or a controller.

## Diagnose the three different clocks

1. Input-to-aim: compare immediately inside the pointer event's turn, before
   waiting for physics or another animation frame. The previous runtime stored
   coordinates only; the next fixed step consumed them about one frame later.
2. Aim-to-visible pose: inspect the FIRST rendered frame and its actual muzzle
   over the current camera, including frames with no fixed physics update.
3. Aim-to-next projectile: inspect the FIRST eligible shot, accounting separately
   for remaining cooldown/reload. ROOK's .42-second interval is not input lag.

Use `applyPointerAim` in `public/combat-aim.js` through `studio.js`'s
`syncPointerAim`. Call it on pointer move/down, after actor/camera updates before
emission, and immediately before combat rendering. Body and projectile share
that solution. Never add aim interpolation, a sample queue, or a gait-clock gate.
Existing bullets keep their original velocity: turning the gun does not home
already-fired projectiles. Do not lower cooldown, increase projectile speed,
drop old bullets, or reset recoil/phase to make this test look responsive.

## Required regression

Follow `browser-check.md`. `runCombatChecks` now produces the original 17 cases
PLUS a mandatory 16-row `rapidAim` matrix: eight directions each stationary and
moving, a multi-sample reversal burst, immediate ray error, first-frame ray
error, first-eligible-shot timing, actual travel and unchanged old velocities.
The real mouse stays held; synthetic DOM events exercise the actual handler.
No ammo refill or weapon-speed override is allowed. Use the bounded free lane.
The synchronous three-sample burst budget is 8.33 ms; the first render must be
observed within 50 ms. Record actual times, not these limits as measurements.
`character_workflow.py` rejects old 17-only reports, stale hashes, eventual-only
success, false movement coverage, delayed shots and non-finite measurements.

The report now retains all three reversal samples, before/after locomotion
state and old projectile velocities. Eligibility is recalculated from the
observed initial ammo/cooldown/reload and current weapon recipe; the reporter
must retain reload in the before/after Actor snapshot. Capture the requested
world target BEFORE dispatching each pointer event; compare that independent
request to the observed target and actor-relative sector. Three changed sector
labels with an unchanged coherent muzzle/target/angle snapshot are not reversals.
Do not force the muzzle angle to equal the sector angle: the muzzle has an offset.
The observed muzzle is XYZ (three finite numbers), not an XY pair; check its Z
against the character weapon height while the requested target remains XY. A
real correct runtime report must pass as well as the negative fixtures.
The reporter cannot enlarge its own allowed delay. Old summary-only reports need an actual
rerun, not manually inserted sample arrays. Keep NPC telegraph-locked aim
separate: enemies must not home their announced lunge onto new player input.

Node tests independently cover 30/60/120 Hz reversals, unchanged accepted gait,
ammo/recoil/cadence, latest-sample emission and non-homing flight. Retain the 40
locomotion cases and exact-build native temporal review for delivery. Preserve
prior accepted art/cycle reviews; new runtime bytes need new runtime evidence.

This repair and its tests are reusable by Luna, not an actual Luna reproduction
or a guarantee that every future character will pass without inspection.
