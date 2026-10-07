# Executable reuse and Luna handoff

Use the current Motion Studio. This procedure incorporates tested ROOK R3
mechanics without treating its failed high-resolution art or performance as an
approved production recipe. It does not start a model, generation or deployment.

## Resume from actual files

Run from `motion_lab_v1`, using the installed Python below as read-only input.
Create a task-local folder below `qa/`, set TEMP/TMP there, and set
`PYTHONDONTWRITEBYTECODE=1`. No source-art API is called by these commands.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py handoff --character rook
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-handoff --packet 'ACTUAL_PRINTED_PACKET_PATH'
```

Replace `rook` with the requested existing character, and the packet argument
with the real first command's output. Do not execute the placeholder literally.
The output names a precise failed/review/missing slot, reference, recipe and
existing commands. A packet with `READY_TO_RESUME` is NOT ready for delivery.
Changed source bytes, a newly supplied missing slot, overrides, review evidence,
runtime code or skill instructions invalidate it. Regenerate it after changes.
The harness prioritizes actual `repair` verdicts before producing other views.
This includes cycle-only source rejections outside E: `REPAIR_REPORTED_CYCLE_SOURCE`
names the failed slot even if its isolated source review was approved. After
replacement, finish/review that complete cycle before filling another direction.
Timing/preview/annotation rejections request cycle work, not new source art.
After explicit source repairs and incomplete E sources, an unreviewed/stale
E/walk cycle must be resolved before non-E cycle repairs. Approved E source
images do not preserve a stale E whole-cycle approval. The selected action
also travels through both preview/prepare commands: a separate `run` cycle
must emit `--action run`; an idle source maps to the following walk review.
Regression tests execute the real CLI parser with an artifact-only callback,
not just a string/hash comparison. A self-consistent wrong command can still
pass handoff byte verification, so that alone is not semantic validation.
It now prioritizes a runtime visual rejection even when individual source
slots are approved. Use [the enforced cycle gate](cycle-review.md); exact-byte
handoffs and R3 packing checks never substitute for that cycle approval.

For a genuinely new character, use `new_character.py` with the actual user's
reference first. Its copied camera/gameplay defaults are scaffolding: inspect
the character's real weapon, magazine, cadence and movement units before
integration. In particular ROOK's art scaffold is not its 10-round/.42s/1.38s
game scattergun. The packet flags this known unresolved gap; it does not silently
adjust production Actor values. Never convert another character's pixels into
the new one to make an incomplete source set build.

## Tested mechanics and where they belong

| Mechanic | Reuse location | Boundary |
|---|---|---|
| Shared mouse/key aim and same whole-body movement/fire phase | `public/keyboard-input.js`, `combat-aim.js`, `simulation.js`, `atlas-renderer.js` | Default new-character route; retain existing tests |
| Exact deduplication with explicit cell rectangles and timing aliases | `compact_atlas.py` | Existing vertical RGBA FastRuntime descriptor imports only; not a replacement authored-frame compiler |
| Selected cell committed before synchronous fire; preserved stationary recoil | R3 `pilot_runtime.gd` | Isolated Godot FastRuntime reference; not a browser script or a production-approved replacement |
| Single resident page per direction; candidate chosen before initial load | R3 loader/test scene | Never load old and new textures together in comparison |
| Exclusive bounded batch, code hashes, same scene population | R3 `run_pilot.py` | Capture and benchmark must not overlap; keep all declared repetitions |
| Native returned RGBA admission, alpha 0..255 | `source_alpha_policy.py` + source intake/review | New originals only; format PASS still requires visual inspection. Existing green provenance remains verifiable, new chroma intake is retired. |

The frozen R3 runtime uses its original descriptor timing and art. No new
character should copy its ROOK path constants. For a real FastRuntime migration,
make a separate candidate, adapt its exact descriptor/manifest path and rerun
actual runtime/temporal/performance evidence. Do not relabel the old receipt.

Verify the reference before relying on its claims:

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-improvements
```

This independently compares all 272 stored timing cells with the current
original RGBA, verifies pinned evidence/code hashes, and recalculates the
declared 10/11/12 performance repeats. Expected historical result:
`VERIFIED_LIMITED_REUSE`, controller 216/216, temporal 32/32,
**performance FAIL, sourceVisualStatus HOLD, productionPromotion false**.
That successful verification means the limitations were preserved, not waived.
Missing/stale evidence fails closed; never regenerate retired assets just to
make an old reference path exist.

## Optional lossless atlas import

The new project adapter has no provider dependency and never alters its input.
It preserves decoded RGBA including RGB under alpha=0, frame order, durations,
display offsets/scale and muzzle metadata. Verification reads both original
and packed cells; it does not trust an old `checks: PASS` label.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py pack --descriptor '../data/character_pipeline/rook_runtime.json' --output 'qa/atlas_candidates/ACTUAL_NEW_CANDIDATE_NAME'
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py verify --manifest 'ACTUAL_PRINTED_MANIFEST_PATH'
```

Use a fresh named candidate path, not the literal placeholder. No automatic
overwrite, cleanup, production pointer change or deployment occurs. The input
must be an existing regular descriptor-sized vertical sheet, not a failed
generated row that is being disguised by equal slicing. Missing/invalid alpha,
rectangles, original hashes, order and timing are errors. Memory estimates are
not GPU measurements. Packing fewer unique cells does not shorten the loop.

## Art and delivery constraints still apply

- Inspect native RGBA alpha 0..255 and light/dark edges; painted checkerboard is
  not transparency. Preserve failed sources. The user's 2026-09-13 correction
  forbids green generation/fallback and local alpha clamping/keying for new
  masters. Read ImageGen/identity instructions when doing
  actual art work; these harness utilities do not grant a provider switch.
- Trace each leg from hip to boot with that character's own asymmetric markers.
  Guide colors are not clothing. A neutral guide only avoids color copying;
  it does not prove the opposite support or correct foot contact.
- Inspect the compiled chronological cycle as well as isolated originals.
  Different source framing can change body/weapon proportions after normalizing.
  Keep a valid half of a pair via the existing `intake_pair.py --side` mechanism;
  do not approve the failed half with it.
- Distinguish 8x8 dispatch from authored strafe, speed-up walk from authored
  sprint, and ammo/reload logic from reload-hand art. Stationary recoil should
  preserve verified planted feet; do not discard a valid recoil clip merely
  to force an idle frame.
- Follow `authoring.md` and `browser-check.md` for build and delivery. Full
  strides, native 1080p video, selected-renderer evidence and actual visual
  observations remain mandatory. Static/technical tests cannot approve gait.

## Regression commands

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.js
```

The new tests exercise corrupt pixels, timing/order changes, missing repeats,
non-finite performance values, stale/tampered handoffs and known-repair priority.
They are local technical fixtures, not a Luna character-generation run. Do not
claim Luna end-to-end success without that separately authorized actual run.
