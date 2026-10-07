# Operators and robots carried as moving floors (2026-09-25)

Follow-up to `qa/web_perf_20260925/cover_ai_teleport_ride.txt` (branch
`claude/jovial-sammet-5a160f`), which found the cause while fixing a test fixture and left
the gameplay side open. The game-code fix landed in parallel from another session as
5fde08edb; this record confirms the carry in normal play, compares the fix candidates, and
checks the landed fix. It changes no game code.

## Cause

`OperatorActor` and `EnemyActor` are `CharacterBody2D`s with no `motion_mode` set, so they
use Godot's grounded mode with `up_direction` (0, -1), although the game is top-down. A
contact whose normal points up (the body is north of the other one) is a floor, and the
other body becomes the platform. At the start of the next `move_and_slide`, the body is
moved by the platform's physics-server velocity (its displacement over the last step), and
`PLATFORM_ON_LEAVE_ADD_VELOCITY` adds it again when contact ends. Operators (layer 4) and
robots (layer 2) collide with each other, so each can be the other's platform. Robots do
not collide with robots, and cover is a StaticBody2D with zero velocity.

## 1. Normal play: confirmed

`tests/smoke/actor_contact_carry_smoke.gd` (runner: `contact_carry`, quick suite, `--out`)
uses the app's own operator and robot bodies on the MIS_CH01_02 battle floor. Each robot
moves east at a gameplay speed through its own `move_and_slide`, and a rider stands against
its north side. The bodies are placed apart, and the server settles for three ticks before
any contact, so no teleport is involved.

| scenario (60 Hz) | robot moved | 95efd37ad (unmodified) | with the fix |
|---|---:|---:|---:|
| BULWARK crawl 62 px/s, 90 ticks, controlled operator | 93 px | carried 92.1 px | 0.00 px |
| BULWARK crawl, AI follower holding its post | 93 px | 18.4 px (then walks back) | 0.00 px |
| CINDER approach 112 px/s, 60 ticks, controlled operator | 112 px | carried 110.2 px | 0.00 px |
| CINDER approach, AI follower | 112 px | 18.7 px | 0.00 px |
| CINDER charge 360 px/s, 25 ticks, controlled operator | 150 px | carried 144.0 px | 0.00 px |
| CINDER charge, AI follower | 150 px | 31.4 px | 0.00 px |
| operator walks 1 s out from under a BULWARK touching it from the north | — | robot dragged 165 px | 0.00 px |
| same with a CINDER | — | robot dragged 165 px | 0.00 px |

Data: `contact_carry_head.json` (95efd37ad), `contact_carry_fix.json` (the variant measured
here), `contact_carry_landed_5fde08e.json` (the landed fix).

How often this happens in the five technical playthroughs: `tools/contact_census.gd` wraps
`site7_full_operation_smoke.gd` unchanged. On every tick, it records each actor whose last
move ended on another actor's north side, along with that floor body's server velocity.
Three unmodified runs of all five missions covered about 115,600 ticks (32 minutes of play),
and all were EXTRACTED:

- Actor-on-actor floor contact occurred on 38 ticks, all in MIS_CH01_04. Seven were a
  follower against a CINDER. On the other 31, robots were against a standing follower,
  which has no velocity and so carries nothing.
- The follower was carried on 3 ticks, 25.7 px in total. One tick moved it 23.2 px at
  once, because the CINDER's body had moved at 1,392 px/s the tick before.
- No robot was carried during an attack warning.

The bot holds 290 px from the nearest robot, so a player who closes in touches robots more
often than this. Data: `census_head.json` (first run, per rider), `census_ab.json` (all
runs).

The original finding reproduces here: `tests/render/site7_cover_ai_check.gd` at
`--fixed-fps 60` fails on 95efd37ad with "Follower bypasses cover ... gap=201.18", because
the follower rides the drone's teleport. With the fix it passes 46/46, without the fixture
wait.

## 2. Fix

The smallest fix is to make the actors ignore other bodies as moving floors. It landed on
`integrate/site7-demo-20260924` as 5fde08edb:
- `OperatorActor._ready` and `EnemyActor._ready` set `platform_floor_layers = 0`.
- They also set `platform_wall_layers = 0`, which is already the default.

The variant measured here (`measured_variant.patch`, against 95efd37ad) also set
`platform_on_leave = PLATFORM_ON_LEAVE_DO_NOTHING`. That line is redundant: with the floor
layers at 0, the platform velocity is zeroed before the on-leave step. The test output on
5fde08edb is identical to this variant's, apart from the recorded body settings and time.

Floating mode was not chosen. Cover sliding was compared over 242 approaches in MIS_CH01_02
and MIS_CH01_04 (`tools/cover_slide_probe.gd`, `--fixed-fps 60`):
- Each setup used the same operator, props and inputs.
- Approaches came from 16 sides, each straight on and at 20 and 40 degrees, for 75 ticks.

| setup | end point equal to shipped | largest difference |
|---|---:|---:|
| shipped, run again (noise) | 242 / 242 | 0 px |
| platform floor layers 0 + DO_NOTHING (the fix) | 242 / 242 | 0 px |
| the fix + `floor_snap_length = 0` | 219 / 242 | 159 px |
| `MOTION_MODE_FLOATING` | 81 / 242 (161 differ > 1 px) | 180 px; path 0.4x to 9.3x |

Floating mode slides along walls at full speed on the first slide and stops head-on within
`wall_min_slide_angle` (15 degrees). It would change how every operator and robot moves
along cover. Data: `cover_slide_MIS_CH01_02.json`, `cover_slide_MIS_CH01_04.json`.

## Gameplay effect

- An operator standing against a robot's north side now stays put when the robot moves.
  Before, it travelled with the robot. A standing operator went the whole distance. An AI
  follower went up to its 18 px post tolerance and then walked back.
- A robot touching an operator's north side is no longer dragged when the operator walks
  away. Before, the dragged robot's own move counted as displacement, which cancelled any
  attack warning or burst it was in (`EnemyActor._physics_process`). The census saw no
  such case.
- One-tick throws when the robot underneath jumps are gone. Examples are the 23 px follower
  throw and the 200 px teleport ride.
- Unchanged:
  - Cover and floor-edge sliding (242/242 identical).
  - Robots never push operators.
  - Moving into a robot still stops at its body.
- Left as is: grounded mode's 1 px floor snap. When a round robot slides out from under a
  standing operator, the snap lowers the operator along the robot's side:
  - up to 8.9 px for a BULWARK crawl
  - 3.7 px for a CINDER approach
  - 0.6 px for a CINDER charge

  The test records this as `rider_moved_across_px`. Turning the snap off would change
  cover sliding (above).

## 3. Regressions

The full suite ran on 95efd37ad with the new test, once unmodified and once with the
measured variant. Both runs used the same machine, one after the other (`suite_compare.json`,
`tools/compare_runs.py`).

| | unmodified | fix |
|---|---|---|
| quick | — | 26 / 26 PASS |
| full | 43 / 45: `contact_carry` FAIL (expected), `full_op_03` WIPED | 45 / 45 PASS |

- Every other test had the same status and check count in both runs, and the QA guard was
  clean in both.
- The `full_op_03` wipe happened in the boss room at 120.7 s. On the same build, MIS_CH01_03
  was EXTRACTED in all three census runs, and the census never saw actor-on-actor contact
  in that mission. The wipe reflects the bot's balance margin, not the carry.
- `enemy_cover_nav` (`tests/render/enemy_cover_navigation_regression.gd`): all 29 cases
  were identical in end point, path length, time and lane reached.
- `cover_ai` at the runner's rates:
  - Follower paths were identical at 30/60/120 Hz.
  - Drone-flank displacement was identical at 60 and 120 Hz.
  - At 30 Hz it was 189.7 px unmodified vs 221.2 px with the fix. In earlier runs of one
    build, this value varied from 188 to 220 px.
- `cover_navigation` passed 15/15 in both runs, and `floor_segment` passed 13/13.

Playthrough outcome and damage come from a rotated real-time A/B in one session
(`census_ab.json`, `tools/census_ab_summary.py`):
- Four rounds ran in the order unmodified, fix, fix, unmodified, each with the five missions
  in parallel.
- The first census run and the two suite runs are added to the totals.

| | unmodified | fix |
|---|---:|---:|
| playthroughs | 20 | 15 |
| EXTRACTED | 19 (the wipe above) | 15 |
| squad damage per extracted run, all samples | 353.8 ± 45.6 | 366.6 ± 57.9 |
| same, rotated rounds only (10 vs 10) | 357.7 ± 51.3 | 346.2 ± 57.0 |
| mean time to extract | 127.1 s | 127.7 s |

The fix's suite run took more damage than the unmodified suite run in 3 of 5 missions, but
in the rotated rounds it took less on average. The per-mission damage ranges of the two
builds overlap in all five missions. Both differences are inside run-to-run spread. The two fix census rounds had no actor-on-actor floor contact at all, so they add
nothing either way; the test above covers the fix.

On this branch (3937cb88f, with 5fde08edb, plus the new test and this record):
- quick passed 29 / 29, with `contact_carry` at 27 checks. Its output matches
  `contact_carry_landed_5fde08e.json` except that one snap residue differs by 0.01 px.
- full passed 47 / 48, with a clean QA guard.
  - `full_op_01` WIPED in the boss room at 119.0 s (19 hostiles, 439.6 damage). This is
    the same kind of loss as the unmodified `full_op_03` above; each build now has one wipe
    in 20 playthroughs.
  - Run again twice with `--only full_op_01`, it EXTRACTED both times (278.5 and
    309.6 damage).
  - The other four playthroughs were EXTRACTED with 321.3–532.5 damage.
  - `platform_carry`, `enemy_cover_nav`, `cover_ai` (46 checks), `cover_navigation` and
    `floor_segment` passed.

## Files

- `contact_carry_*.json`: test output per build (see section 1).
- `census_head.json`: the first unmodified census, per rider and longest rides.
- `census_ab.json`: every playthrough sample with outcome, damage and census totals.
- `cover_slide_MIS_CH01_0{2,4}.json`: cover-sliding end points per setup.
- `suite_compare.json`: full-suite comparison, unmodified vs fix.
- `measured_variant.patch`: the variant measured here, against 95efd37ad.
- `tools/`:
  - `contact_census.gd` and `cover_slide_probe.gd`. `qa/` is `.gdignore`'d, so copy them
    to `.cache/probe/` to run them.
  - `compare_runs.py` and `census_ab_summary.py`.
