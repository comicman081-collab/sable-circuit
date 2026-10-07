# Continuous-map connector correction — 2026-09-23

Cause: the closed-wall room plates overlapped each connector by only 118 px,
and every main connector was painted rising left-to-right even when the next
room descended. The walkable capsule followed the mismatched connector, so a
player holding right hit a painted door/floor edge at `(4623.753, 309.263)`.
The earlier full-operation bot navigated around that point; it did not prove
the direct player input path.

Fix: main connectors now overlap the rooms by 246 px, mirror horizontally for
descending links, and route their two endpoints to the corresponding open
deck ends. Both optional branch connectors rotate into north/south passages.
The collision floor uses those same transformed plates. The R03/R04 cover
props that blocked branch mouths were moved inside their rooms, and cover
navigation now plans with 12 px of corner clearance rather than an unusable
1 px tangent. Room and connector source PNGs are unchanged. The same runtime
placement rule is applied to all five operations.

Checks:

- Normal D+Shift input from Stage 1 entry: `(1680,470)` to `(5403.395,389.751)`
  after 900 physics ticks, crossing the previous stop. `DIRECT_ENTRY_D_SMOKE: PASS`.
- Stage 1 full authored operation: ten hostiles defeated, route completion and
  extraction without teleport or forced step advance. `SITE7_FULL_OPERATION_SMOKE: PASS`.
- Five operations × five main links × entry/exit input crossings: all passed
  after neutralizing *test-fixture-only* frozen enemy colliders. This does not
  disable enemy collision in the game. `SITE7_CONNECTOR_ALIGNMENT PASS`.
- Five operations × two optional branches × entry/exit WASD crossings: all
  passed in that same connector test. A second regression starts at each
  branch parent and uses the actual cover-aware navigation; all ten branch
  destinations were reached. `SITE7_BRANCH_NAVIGATION PASS`.
- `COVER_NAVIGATION_SMOKE: PASS / 15 checks` after the corner-clearance repair.
- Native 1920×1080 captures `hold_d_660_native.png`, `hold_d_840_native.png`,
  and representative Stage 1/2/5 main and branch connector captures passed
  container decode and resolution validation. Container PASS is not an art-quality
  claim. Some off-path branch edges still reveal black void / plate seams.
- Web export succeeded, and public Site version 11 deployed from source commit
  `d0db763c719390c71f27f6e007279b885989b2d1`.
- Public browser: title and normal Operation 1 deployment loaded, three
  hostiles visible, no captured console warnings/errors. Extended held-key
  browser traversal was not run because this browser control route does not
  support held key-down; native Godot tests provide the movement proof.
- Test-only in-app browser tab was closed after verification.

This is a scoped passage/traversal repair, not a complete human playtest or
approval of unrelated combat, art, performance, or missions 2–5 end-to-end.
