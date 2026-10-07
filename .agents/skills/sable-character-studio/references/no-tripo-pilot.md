# No-Tripo pipeline comparison: tested scope, not a new production default

Use this route when the user explicitly requests pipeline research/comparison or
a No-Tripo pilot. Ordinary character work still follows `authoring.md` and the
implemented Motion Studio. No delegation/model switch is implied.

## Actual reproducible case

`motion_lab_v1/pilots/no_tripo_rook_20260911/` contains the ROOK comparison,
source/protected-file hashes, local SpriteGen import, isolated Godot experiment,
72-row matrix, repeated performance and native evidence. Read its `REPORT_KO.md`
and `results.json` before using its result. A missing report or a conditional
result is not permission to promote its candidate runtime.

- Source-art approval is not motion approval. ROOK's costume receipt says PASS
  within a source-only scope; its pipeline state still awaited motion review.
- Count actual pixel-distinct poses. The legacy E walk has 24 timing cells but
  only 12 unique RGBA frames; four idle cells contain one unique pose.
- Observe the selected runtime. ROOK's legacy `_process` enters the fire clip,
  returns without advancing walk, and resets `_cursor` after fire. Compare
  before/after the actual `primary_fired` event and a complete temporal cycle.
- Do not infer stationary-foot motion from a changing full-body frame index.
  The final ROOK test composites the selected lower-leg/foot pixels onto a fixed
  background and hashes visible output. All eight legacy stationary recoil
  clips had stable feet. R2 preserves those working clips; only moving fire is
  kept on the independent gait. The earlier frame-index-only test produced
  eight false positives and was replaced, not recorded as an existing art bug.
  `stationary_feet.json` also checks all idle/fire source silhouettes: lighting
  changes in RGB did not move the foot alpha geometry. Do not use lighting
  variation, hidden transparent RGB, or a frame ID as geometry ground truth.
- Movement/aim dispatch can pass all 72 rows while 56 cross-direction cases
  still lack real strafe art. Keep technical and anatomical/appearance status
  separate for EACH row. Holding idle feet is not authored recoil completion;
  preserve independently verified existing recoil instead of dropping it.
- Do not replace the real whole-body artwork with split legs or procedural
  costume reconstruction merely to satisfy a frame-count test.

## SpriteGen utility contract demonstrated on Windows

The tested installation was 2.1.0 at
`C:/Users/AAA/.codex/skills/sprite-gen`, with its own
`.venv/Scripts/sprite-gen.exe` and `.venv/Scripts/python.exe` (Python 3.11.9).
Resolve the current installation and read its SKILL/help before future use.
Do not upgrade or mutate that installed environment as a side effect.

- `cutout --key green` was tested on one native 1024x1536 ROOK master.
  Preserve the green original; inspect the RGBA derivative on light/dark at
  native scale. Unmix/despill can change RGB; do not promise immutable RGB.
- `unpack-atlas --pngs-dir` and `compose-atlas` executed successfully here.
  That proves these CLI paths, NOT every Windows lock/concurrency scenario.
- These inputs were explicitly imported regular, descriptor-sized cells, not
  generated-row extraction. Never use grid slicing to conceal failed extraction.
- The importer defaulted to **2 fps, non-looping stills**. Set the requested
  timing explicitly, recompose, and verify every `durations_ms`/loop flag.
  Here 24 fps became 42 ms per frame (1008 ms/cycle); the engine follows that
  explicit timing, not an assumed exact one-second loop. Repacking normalized
  RGB under alpha=0: visible RGB and alpha matched all 24 inputs, but whole
  RGBA bytes did not. Report those two checks separately.
- Imported runs may report `raw missing / stale kept`. This means they cannot
  re-extract a generated raw row; do not mislabel the import as generated.
- Runtime animation consumes composed `manifest.frame_layout` rectangles and
  timing, not a guessed grid. Verify output cell pixels against the imports.
  Godot required a small explicit adapter; format export alone was not game QA.
- No provider calls are required for these utilities. This is not authorization
  to send references to Grok, Gemini, another provider, or a paid endpoint.

## Comparison and evidence boundaries

Compare 3D-to-2D, realtime 3D, split 2D, and whole-body raster hybrid before
selecting a pilot. Installed Blender/VRoid or generic licensed motion meshes
do not establish an identity-matched ROOK 3D model. Record an honest untested
alternative instead of manufacturing a quick primitive replacement.

Predeclare scope, budget, same scene/scale/population, frame-time targets and
promotion blockers. Measure baseline/candidate sequentially, repeat at least
three times, and keep native capture work out of performance runs. Preserve
population throughout the comparison, not just at startup. PNG file size is
not VRAM; distinguish process working set, engine counters and estimates.
The final ROOK R2 did NOT pass its predeclared performance gate. Retain the
failed repetitions; do not substitute better R1 timings for the final code.
Its runtime is an unpromoted experiment, even though 72 controller rows passed.

Validate the **decoded** video size. In this pilot Godot's movie writer kept
the project's startup 1280x720 target despite a later 1920x1080 viewport and
`--resolution`. Such movies remain rejected evidence. Actual 1080p viewport
readbacks can be encoded locally without scaling; preserve provenance and
original-scale PNG samples. Resolution validation is never visual approval.

For inaccessible videos, record the exact URL and access result; never turn
search snippets or this prompt's principles into claims of having watched a
video. “Learning” means evidence-backed reusable instructions, not model/LoRA
training. Do not claim a Luna reproduction without an authorized actual run.

## ROOK R3 follow-through

For executable reuse and packet verification, follow
[the current handoff procedure](reuse-improvements.md). Keep this case as
evidence, not a copy-pasted per-character production runtime.

`motion_lab_v1/pilots/rook_completion_v3/` contains the follow-up. Read its
current `results.json` and `source_review.json`; it is not an approved full
character merely because a compact atlas runs. New E sources and existing-art
runtime optimization are separate candidates and must not be conflated.

- Exact whole-cell deduplication preserves all 272 timing slots and decoded
  RGBA bytes while reducing source base-level texture estimates from 153 to
  90 MiB. Do not shorten the loop when removing stored duplicate pixels.
  The four-column page layout has explicit rectangles and a 1920px max edge;
  it is a project adapter, not an invented SpriteGen exporter feature.
- Commit the selected frame with the distance phase before synchronous fire.
  R3a deferred this until render processing, causing fire to flush a stale
  frame. Phase unchanged is not enough; inspect actual selected cells too.
- Select the isolated candidate before its first texture load; loading both
  old and new runtimes biases load/memory comparisons. Bind code hashes at
  run start/end. The runner now exclusively locks the batch so readback video
  capture and performance cannot overlap. Retain contaminated runs as such.
- A historical native-alpha request returned an RGB checkerboard image and
  the pilot used a separately keyed green master. The user's 2026-09-13 rule
  supersedes that fallback: new masters require native RGBA alpha (0..255 since 2026-09-28).
  Inspect actual channels and retain failures; do not generate another green master.
  Pose pairs can repeat support legs; colored guides can contaminate clothing.
  A neutral guide prevents color copying, not all anatomical/phase errors.
  Compile and inspect a chronological E cycle before expanding other views.
