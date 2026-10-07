# R6-01/02/03 concrete fixes, not art or complete-MVP approval

Please narrowly recheck the three named R6 defects against the exact code below.
Actual locally executed Godot (not Python reimplementations):
- 46 checks in native-rendering site7_machine_edge_case_smoke.gd: eight distinct
  1536x1024 synthetic views accepted; metadata-only and hidden-RGB-only duplicates
  rejected while preserving the previous visible body; root-coincident invalid
  aim holds REPOSITION with no warning/attack/emission at 30/60/120Hz; all 8 distant
  targets remain valid; actual Tactics draw signal and native pixels show the
  cached line disappearing after stagger without calling step or queue_redraw in
  the test. Native before/after evidence was observed locally, not attached here.
- After adding the app-loader hook, facing 240 and machine source 388 pass again.
- Native 1920x1080 actual-scene facing captures advance WINDUP->BURST normally
  and record real emitted projectile events in 8 directions. They do not claim
  human-input gameplay. Recovery smoke now really sets RECOVER, not REPOSITION.

R6-01: invalid solve returns Vector2.INF, preserves selected view, and tactics
continues normal repositioning instead of advertising/firing an invalid ray.
Both tactics emission and the actor's actual creation boundary reject non-finite
or zero vectors. No forced forward target or homing bullets.
R6-02: every _enter queues redraw on the Tactics CanvasItem itself.
R6-03: file hashes remain required; decoded size+RGBA hashes also reject duplicate
visible art. RGB under alpha=0 is canonicalized only in a comparison buffer, not
in the displayed texture or the source. Cache is keyed by the verified file SHA.

Additional small app-integration safeguards: immutable configure rejects reuse,
kind must match the exact actor role, reconfiguration hides/disconnects an old
machine visual, and app spec loading checks path prefix, hash and enemy identity.
App profiles are not switched by QA capture. Please distinguish these from the
three requested R6 closures and do not invent art approval or Godot execution.

Existing accepted playable art, gait, 1.8 scale, cadence and damage are unchanged.
This is not a claim of independent sprint art or a completed Luna reproduction.
