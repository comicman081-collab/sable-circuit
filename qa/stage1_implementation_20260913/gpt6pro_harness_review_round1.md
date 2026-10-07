# SABLE CIRCUIT actual harness/skill review — 2026-09-13

The user requests review in their existing GPT 6 Pro chat while local development continues.
Review the actual code below; do not claim to have run it or inspected unseen images/videos.
Deliver prioritized concrete defects with file/function, failure example, minimal fix and regression test.
Focus on weaker-model misuse paths, false visual approvals, repeated wrong support-leg sources,
stale evidence, provenance binding, movement/aim clock separation, and fitting humanoid rules
to new drones/anchored machines/quadrupeds. Distinguish definite code bugs from possible risks.

Non-negotiable constraints: preserve accepted ASTER/MICA/ROOK art and gait; visible source art
is built-in ImageGen only. No anatomical raster warping or primitive character replacement.
UAL/Blender guides are pose-only. Failed art is retained, no false review receipts. Native visual
evidence is >=1920x1080 with actual normal-speed temporal observation, not just still containers.
No universal success guarantee, no claim of actual Luna reproduction without a real authorized run.
Use current Motion Studio, NOT the retired legacy production harness. Do not propose broad cleanup,
new external services, global model changes or deployment. Technical tests are not visual approval.

Observed production failures, NOT hypothetical:
* Old ASTER renderer froze walk/run at frame 5 and swapped in unrelated leg-warp art during fire.
* Prior ROOK had distinct source hashes but repeated the same anatomical support leg. Cycle review
  was added; source completeness and selected-frame diversity cannot prove natural walking.
* In today's rifle-enemy pilot, two ImageGen opposite-pose pairs repeated the right planted leg in
  both figures, despite phase text. They remain unapproved. Changed to one pose per image with
  the exact colored UAL phase guide FIRST and appearance reference SECOND; E1/E2 now visually
  show the requested alternating anatomical roles. The whole cycle is NOT approved yet.
* One requested transparent image returned RGB painted checkerboard: rejected and retained.
* Current prepare_enemy_asset.py creates isolated candidates, but its tool-response validation
  appears too weak: it checks tool/result existence without binding the exact source bytes.
* New NPC tactics own attacks; an old premium boss presentation also emitted volleys. Duplicate
  old emissions were disabled after the attached technical playthrough; rerun is still pending.

Stage 1 status: 6 route rooms +2 optional, 2 reinforcement encounters, 3-phase anchor boss,
real projectile/ammo/collision bot playthrough to extraction passed with 10 kills. The attached
receipt is technical only; enemy raster assets have NOT been promoted. No visual MVP claim.

Please return (1) blocking defects, (2) minimal implementation/skill patches, (3) useful negative
tests, (4) explicit limits requiring human/observed visual judgment. Avoid generic praise or a
brand-new framework. We will apply justified changes and return actual regression results.

## FILE: .agents/skills/sable-character-studio/SKILL.md
SHA256: 8ac2d19b7ca4b13f397557aaac2f4c9b3b07c9d2b69fe1a53c7d3c3735249e08

```text
---
name: sable-character-studio
description: Create, repair, or resume SABLE CIRCUIT characters and their eight-direction movement and shooting in the working motion_lab_v1 Motion Studio. Use for MICA, ROOK, ASTER and subsequent characters, including Luna handoffs; not for legacy gate audits or other games.
---

# SABLE character studio

Use the actual implemented Motion Studio, not the retired production harness.
Read `motion_lab_v1/AGENTS.md` and the relevant sections of
`motion_lab_v1/README_KO.md` from the repository root. Run commands from
`motion_lab_v1`. The user's latest instructions take precedence over this skill.

## Choose the work, not a new pipeline

- **Explicit No-Tripo research or pipeline-comparison pilot:** read
  [the evidence-backed comparison route](references/no-tripo-pilot.md). Keep
  candidates isolated; a technical pilot does not authorize production swaps.
- **Movement, aim, firing or input bug:** repair the shared runtime in `public/`.
  `keyboard-input.js` stores physical codes. `combat-aim.js` owns the single aim
  used by facing and projectiles. `simulation.js` drives the actor;
  `atlas-renderer.js` displays the selected authored frame. Do not regenerate art
  or change character speed to hide an input/aim error.
  For slow rapid-turn response, follow [the aim latency contract](references/aim-response.md).
- **New character or source/pose/costume repair:** read
  [the authoring procedure](references/authoring.md). Use recipe data and the
  current per-slot status, not a copy of MICA's pixels or a new bespoke runtime.
- **Browser validation, packaging or handoff:** read
  [the browser procedure](references/browser-check.md). Test actual held firing
  and both mouse/keyboard direction changes, not only the Actor unit test.
- **Skating, fixed legs or legs thrashing during fire:** read
  [the gait repair procedure](references/gait-repair.md). Inspect the selected
  renderer and its actual textures before changing speed or generating art.
- **Any new/changed authored gait or delivery:** use the
  [enforced cycle gate](references/cycle-review.md). `prepare-cycle` creates
  review evidence, never approval. An approved E whole cycle is required before
  expanding sources; all affected cycles and timed runtime observations are
  required before active build and delivery.

## Keep the working invariants

- Latest directional input wins by default, even during held fire. Key repeat
  must not steal active mouse aim. Body and projectiles share one world-space
  aim. Resolve facing and the illustrated muzzle-to-cursor ray together before
  firing; never recompute a different bullet angle afterwards. Targets inside
  the weapon's reach use forward aim, not a backwards shot through the body.
  Commit pointer aim synchronously and refresh it after camera/pose changes,
  before emission and rendering. Do not couple it to gait or weapon cooldown.
- Visible new/repair artwork comes from built-in ImageGen. Blender/UAL guides
  provide pose/contact only. Keep original sources; inspect identity, anatomical
  left/right feet, weapon continuity and real alpha before accepting a frame.
- Never invent a tool result or visual approval. The workflow checks exact
  hashes and missing/duplicate inputs; it cannot judge anatomy or artistic
  continuity. Record real observations and evidence, not a technical PASS label.
- Modern compiled recipes use `animation.presentation: authored_frames` and
  the shared MICA renderer. Movement and moving fire use the SAME whole-body
  gait phase; stationary recoil never changes the feet. Do not reintroduce
  ASTER's retired `coherent/move` leg-warp bundle or a split upper/lower fallback.
- On failure, use the reported slot/check to repair the smallest affected part.
  Two same-category source failures require inspecting the source/guide/prompt
  and changing the failed approach before another attempt, not an indefinite
  generation loop. Keep failed inputs and their evidence.
- A complete staged build may replace its character's development atlas, with
  the prior atlas preserved. Standalone files/reports are character-specific.
  Do not use `--activate-preview` or touch another character's active preview
  unless that preview switch is part of the user's request. Never deploy as a
  side effect of generating or repairing a character.

## Luna handoff

For character creation/resumption or a Luna handoff, use the
[executable reuse and handoff procedure](references/reuse-improvements.md).
`character_workflow.py handoff --character ID` emits the current reference,
recipe, rejected/missing slots, runnable next commands and dependency hashes.
Verify the packet with `verify-handoff --packet PATH` before using it; rebuild
the packet after source/code/review changes. These commands never generate art
or activate another character. Do not ask Luna to reinvent the renderer.
Repair known rejected slots/cycles first. Establish E idle and the complete E
walk cycle; `review-cycle` must validate its observations before expanding the
requested slots. Runtime rejection takes priority in the handoff even if all
individual source slots have approvals.
Do not silently substitute a different model, start a new user-owned task, or
claim an unperformed Luna reproduction. Model selection or delegation requires
the current user's request to support that action.

The accepted MICA prototype has 48 walk and 8 idle frames. Running reuses walk
cadence unless separate run art is requested and supplied; strafing and reload
hand artwork are not automatically supplied by a controller test. Current
capability and validation results are recorded in
`motion_lab_v1/qa/WORKFLOW_READINESS_2026-09-10.md`.

```

## FILE: .agents/skills/sable-character-studio/references/authoring.md
SHA256: edfdc7a52d12bd83f349c2627c5d8d07594608e69184c609e1cd15b033aadbee

```text
# Authoring and repairing a character

All commands below run from `motion_lab_v1`; replace `ID` with the actual
requested character, never infer permission to start a different one. Use the
installed Python at `C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe`; it has
Pillow, NumPy and OpenCV. Do not modify that environment. Set `TEMP`, `TMP` and
any helper cache/output directories to a created directory below this lab;
set `PYTHONDONTWRITEBYTECODE=1` before executing installed Python tools.

## Create and advance

1. Inspect the supplied identity/master, including its original-scale costume
   markers and weapon. Use `new_character.py --id ID --name NAME --reference
   PATH` to copy that input and create the recipe plus exact request list. Add
   `--run-art` only when dedicated running art is requested. The scaffold never
   calls a generation service or copies MICA character pixels.
2. Read [the enforced cycle gate](cycle-review.md). Run `character_workflow.py handoff --character ID` and validate its printed
   packet with `verify-handoff --packet PATH`. `status` prioritizes known repair
   verdicts, then the complete E pilot before other directions. For a repair, existing
   exact-content approvals remain valid; only replaced/failed inputs need new
   review. Do not change frame counts or speed to make missing artwork pass.
3. Use the exact request's appearance reference and existing UAL pose guide in
   one built-in ImageGen attempt. Prefer one character per output. Native alpha
   must be genuine; inspect light/dark backgrounds and interior opacity. If it
   fails, a flat green master and separately keyed RGBA are the fallback.
4. Preserve the actual tool response metadata in a project-local JSON envelope:

   ```json
   {"tool":"image_gen.imagegen","returnedPath":"actual returned local file path","result":{"actual":"returned response metadata, not invented evidence"}}
   ```

   Replace the example contents with the real response. Import with:

   ```powershell
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' intake_frame.py --character ID --direction E --action idle --frame 0 --generated 'actual output.png' --tool-response 'qa/ID/actual-tool-response.json'
   ```

   The selected PNG must be native high resolution. Existing active overrides
   are replaced in their actual slot, not shadowed by an unused master. Prior
   files and provenance are retained. Verify the project copy/hash before any
   separately authorized managed-staging cleanup.

   If ImageGen returns a near-green RGB backdrop, do not edit the character or
   pretend the result has alpha. Copy the raw result into the lab, run the
   project-local `tools/character_pipeline/normalize_imagegen_chroma.py`, and
   import the exact-green derivative with `intake_derived_frame.py`. That
   importer binds the raw ImageGen copy, its untouched tool response, the
   normalization report and binary mask; it never labels the derivative as a
   new generation. Inspect the resulting RGBA candidate on light and dark
   backgrounds before source review.
5. Inspect the image and phase against the real reference and neighboring
   contact pose. A different hash is not proof of a different support leg.
   Record the actual review, using `approved` or `repair`:

   ```powershell
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py review-source --character ID --slot E/idle/0 --decision approved --evidence 'art/ID/E_idle_0_master.png' --reviewer 'actual reviewer' --notes 'Actual identity, limb, weapon and alpha observations'
   ```

   A repair verdict keeps a quarantine copy and blocks that slot. Re-run status
   and follow its next slot. Never record approval without viewing the evidence.
6. Prepare and approve the actual complete E cycle before expanding to the
   other directions; repeat the whole-cycle review for each authored walk/run
   direction. `sourcesReady` alone does not permit a build. When sources and
   cycles are reviewed:

   ```powershell
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py build --character ID
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' package_standalone.py --character ID
   ```

   Build outputs are staged. Missing sources and late compile failures leave
   the prior atlas intact; `--partial` on the lower-level compiler is always a
   retained diagnostic candidate and never activates a character. Review the
   actual `reviewPreviews` path printed by the completed build.
7. Follow the browser procedure, inspect source-scale frames plus native 1080p
   live gameplay, and record the actual runtime visual review:

   ```powershell
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py prepare-runtime-review --character ID --motion-evidence 'qa/ID_motion_native.webm'
   # Fill the actual returned observation file after viewing this video.
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py review-runtime --character ID --evidence 'qa/ID/runtime-native-1080p.png' --locomotion-report 'qa/ID_locomotion_browser.json' --motion-evidence 'qa/ID_motion_native.webm' --observations 'ACTUAL_FILLED_RUNTIME_OBSERVATIONS' --decision approved --reviewer 'actual reviewer' --notes 'Actual visual and temporal observations after watching the video, including remaining limitations'
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py deliver --character ID --browser-report 'qa/ID_combat_browser.json' --locomotion-report 'qa/ID_locomotion_browser.json'
   ```

   Delivery refuses stale or failed source/runtime reviews and binds the exact
   inputs. `dist/ID_Motion_Studio.html` is the standalone output;
   `dist/id.delivery.json` is its review/check record. Do not call a candidate
   file a reviewed delivery merely because packaging succeeded.

## Repairs and the existing MICA package

For a modern recipe, import only the repaired slot and repeat its review, build,
package and affected runtime checks. Original and unrelated slots stay intact.
Durable muzzle corrections belong in the recipe via `apply_muzzles.py`, not
only in the generated profile.

MICA's accepted historical paired-source package predates the per-source
ledger. `status` identifies it as `existing-runtime`; ordinary input/runtime
repairs use `verify-runtime` and do not regenerate its 56 frames. A future
source-art migration must retain its actual masters, pair provenance and user
acceptance; do not populate fictional historical ImageGen receipts or approve
every old frame automatically. Establish a real reference and repair scope
before migrating that existing source set.

```

## FILE: .agents/skills/sable-character-studio/references/gait-repair.md
SHA256: c80960c714d76dca2bcb0f746c12193a7dd548af896b053dd86995e37ccb4016

```text
# Diagnose the visible gait, not only actor position

The 2026-09-11 ASTER failure had three independent causes:

- `fullBodyFrame()` handled only `move` as locomotion. Newly added `walk` and
  `run` fell into recoil recovery and returned frame 5 for every phase.
- Firing switched from the new realistic walk art to an unrelated old 24-frame
  raster leg warp. More frame indices did not make that a real walk.
- The input QA ran only short moving-fire cases. Source hashes, distance and a
  static 1080p screenshot all passed while actual walking stayed frozen.

## Repair order

1. Record the selected action/texture and frame index over a complete stride,
   both firing and not firing. Use `atlas-renderer.test.js` and the live
   `motionDebug.current` state. A profile atlas is not evidence if another
   bundle overrides it in `AtlasRenderer.load()`.
2. Check source pixels using `gait_contract.py`: 0/3 opposite contacts,
   1/4 opposite swings behind and 2/5 opposite forward passing poses.
   Follow the anatomical leg by its costume
   marker: ASTER's LEFT white/cyan leg versus RIGHT thigh-pouch leg. Six new
   file hashes or six pictures of the same forward foot fail this check.
3. Preserve the approved whole-body look. For actual missing phases, ImageGen
   may use one native opposite-pose pair at a time: put the corresponding
   `reference/ual_guides/D_walk_pairN.png` first as CAMERA/POSE authority and
   the character's identity reference as APPEARANCE authority. Explicitly
   specify each leg's role in both figures. Inspect before the next attempt.
   A six-figure sheet copied EAST into SE and repeated S support legs; do not
   treat it as success. Use a direction-specific aimed reference if weapon
   foreshortening drifts. Do not fix missing leg poses with a raster warp.
4. A native 1536x1024 pair contains larger figures than a six-cell sheet.
   `intake_pair.py --character ID --direction D --pair N --generated PATH
   --tool-response PROOF` preserves the real master and separates complete
   connected figures without resizing. It imports phases N and N+3, preserves
   previous sources in quarantine and binds the exact tool response. Never
   pad/upscale a small six-cell output and call it a native high-res master.
5. Run `character_workflow.py prepare-cycle --character ID --direction D`.
   Follow [the enforced cycle gate](cycle-review.md). Inspect the generated
   native-scale light/dark pair panels AND the chronological cycle. Record
   `review-source` and the whole-cycle `review-cycle` only after actually viewing that evidence. Observe rifle
   axis/muzzle, identity, contacts, passing knees and alpha. The command does
   not approve or activate anything by itself.

## Source failure patterns actually observed

- A moving seed can preserve the same support leg despite opposite-leg text.
  Use the direction's reviewed planted aimed master to separate camera/weapon
  authority from the phase guide. Mannequin colors are labels, never costume.
- Follow the cyan leg from its anatomical hip through knee to boot. A cyan
  calf or white stripe on the other leg does not repair swapped hips. A third
  leg, missing panel or brown guide material on trousers is a source failure.
- Single portrait replacements can become thinner/longer than adjacent pair
  sources. Compare their normalized chronological cycle, not isolated beauty.
  The square SW replacement improved this observed proportion mismatch.
- When one half of a pair is valid, `intake_pair.py --side 0` or `--side 1`
  can retain just that observed half. The other half remains unapproved; the
  complete native master and failed-half evidence are retained.
- Low toe clearance is distinct from a high marching knee. Inspect the
  actual game-size moving cycle before expanding a pilot to all directions.

## Runtime invariants and evidence

### ROOK source repair findings (2026-09-13)

- ROOK's anatomical RIGHT thigh carries the paired black/gold cylinders; the
  LEFT forearm has the gold support gauntlet. Trace hip, knee and boot separately.
  In rear views right is screen-right; in front views it is screen-left. In
  three-quarter views a lifted boot crossing the silhouette does not change
  its anatomical side. A hidden cylinder alone cannot identify a passing leg.
- A whole moving-body reference repeatedly copied its old support pose into a
  requested opposite phase. Use the approved direction-specific upper-body
  crop as appearance/camera reference and the phase guide for the whole pose.
  This crop is a reference only: every accepted visible frame is newly authored
  whole-body art, never a runtime upper/lower cut-and-paste assembly.
- SW frame 4 and W frame 2 required a second repair after the chronological
  review exposed the wrong support leg. Inspect the actual recompiled frame,
  not the requested pose name or an earlier review packet. New source hashes
  require a fresh preview, annotations and whole-cycle review.
- Put observed hip/knee/sole points on the native compiled cell. If a landmark
  falls outside the silhouette, inspect the native grid before correcting it;
  do not move a point just to satisfy a threshold. State when a joint is partly
  occluded. On-subject points are a diagnostic, not an anatomy PASS.
- Straight front/rear muzzle heuristics can select hair or a hand. Annotate the
  visible muzzle in raw-source pixels per affected slot, then inspect its
  compiled location and live shot. Do not fix a bad socket by moving artwork.
- The cycle preview now uses VP8/WebM. OpenCV decoding of mp4v was insufficient:
  the Chromium review page could not play that codec. Check real browser
  playback at 1x as well as sequentially decoded samples. Preview videos remain
  source diagnostics, not delivered-runtime evidence.

- Preserve the working physical-code input and shared aim solution.
- The generic authored renderer selects walk/run by actual traveled-distance
  phase, independent of shot cadence. Fire applies the existing continuous
  upper-body recoil and uses the same transform for the muzzle. The lower body
  stays on the same gait; at rest it stays on the same planted idle source.
- Keep `runSpeed` and `walkSpeed` independent. Reusing the walk source with a
  faster distance cadence is the accepted MICA prototype capability, NOT a
  separately authored sprint clip. State this limit explicitly.
- Run the 17-case held-mouse input test AND the 40-case temporal locomotion
  test. The latter checks all eight directions for walk, run, moving fire and
  stationary fire, hashes the actual selected lower-body pixels, and rejects
  fixed/duplicate frames. It does not automatically judge anatomy or sliding.
- The report validator now checks chronological frame/phase agreement, increasing
  sample times, measured position deltas, shot counters and, with the current
  profile, phase-to-distance and speed bounds. A six-element set is insufficient.
- Watch native 1080p runtime video spanning complete strides, turns, stopping,
  speed change and fire transitions. Compare visible foot support to ground
  motion, not a speed HUD. A character at the world boundary is not running
  evidence. Still-image review alone cannot authorize `deliver`.
- Do not report a Luna reproduction unless a real authorized Luna run occurred.
  Regression tests prevent the reproduced bugs, not every possible future
  artistic or implementation error.
- `capture-motion.js` saves a sibling JSON binding the actual video hash,
  current build, capture script and time-stamped full cycles/transitions.
  `motion_evidence.py` rejects stale footage and missing phases. Never create
  that metadata by hand to rehabilitate unrelated footage. Review the video
  and its native decoded sequential frames; index-seeking an unindexed WebM
  can silently display a different moment (`inspect_video.py` decodes forward).
- A source or runtime rejection invalidates the current delivery JSON to HOLD
  while preserving its prior receipt. Never leave an older REVIEWED_DELIVERY
  label as the apparent current result of a failed repair.

```

## FILE: .agents/skills/sable-character-studio/references/cycle-review.md
SHA256: d3879926fb8afe339c771e5cf974be4a2d162cf276b2dcfe003623f801a55a20

```text
# Enforced whole-cycle review

This is the current repair for the 2026-09-12 ROOK false approval. Run commands
from `motion_lab_v1`. This gate applies to modern `workflowVersion: 1` recipes;
it does not invent historical MICA approvals. Read the actual output of `status`.

## Before expanding beyond E

Finish and review E idle and all six E walk sources. The authoritative phase
vocabulary is `gait_contract.py`: **0 left contact, 1 right swing behind,
2 right passing forward, 3 right contact, 4 left swing behind, 5 left passing
forward**. Anatomical left/right belongs to the character, never the screen.
The same definitions generate new requests and validate cycle observations.
New walk recipes retain the accepted contact-dwell starting schedule; adjust
it only against the observed new stride, not to hide missing poses.

Before another direction or authored run is imported or approved, E walk must
have an exact current whole-cycle approval. All three importers and the source
approval command enforce this. A few approved E poses are insufficient.
Existing non-E files remain preserved; do not regenerate them just to populate
new ledgers. View them and repair only what the actual cycle requires.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py status --character rook
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py prepare-cycle --character rook --direction E
```

`prepare-cycle` writes a fresh, isolated kit: native 1920×1080 three-loop video,
chronological source sheet, native source pair panels, local video-review HTML,
and **unreviewed** `cycle-observations.json`. The left video panel displays the
compiled cell at 1:1 pixels. The right displays a 270px character over ground
moving at the recipe velocity. This is source-cycle evidence, not the real
game controller. Nothing activates an atlas or sets an approval automatically.

Open the printed actual HTML/video and inspect at normal speed plus sequential
native decoded frames. Follow each actual leg from hip to knee to sole using
its costume/occlusion continuity. Do not assign left/right from the prompt or
move a pouch label mentally to make repeated limbs look like an opposite step.
Inspect all transitions, including 5→0, and ground-relative foot movement.

Fill the printed observation file using actual observations:

- `reviewer` and `decision`; a template remains unreviewed until inspected.
- `legMarkers.left/right`: how each actual anatomical leg was identified.
- Six `frames` in chronological order, with observed `support` and native
  **compiled cell** pixel coordinates for left/right hip, knee and sole.
  Coordinates are local to one 768×768 cell, not the six-cell page or raw master.
- `observations`: opposite contacts, passing/swing, loop seam, sliding, body and
  weapon continuity. Each needs an observed decision, concrete notes and at
  least two increasing video times in seconds. Generic test counts are not observations.

The validator checks exact source/recipe/contract/preview bindings, nonempty
timed observations, visible-pixel landmarks, connected vertical leg order and
opposite leading feet in the direction's projected ground axis. **Landmark labels
and artistic naturalness still need honest visual observation**; passing these
checks does not let a model invent anatomy or promise universal success.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py review-cycle --character rook --direction E --decision approved --packet 'ACTUAL_PRINTED_OBSERVATION_FILE'
```

On failure, use `--decision repair --evidence ACTUAL_LOCAL_EVIDENCE --reviewer
ACTUAL_REVIEWER --notes ACTUAL_FAILURE` instead. Prior records stay intact and
delivery becomes HOLD. A cycle rejected for its source art cannot be approved
again with the identical six source bindings by changing metadata or notes.
After a real source replacement, the whole affected cycle must be observed again.

Use the same procedure for the other directions and for separate run art when
present. `build_character.py` itself refuses an active modern build until all
source and cycle gates pass. Its `--partial` path is still an isolated diagnostic
candidate and does not bypass activation. Do not call the compiler directly to
get around a rejected cycle. Source completeness, active-build readiness and
runtime approval are distinct fields in `status`.

## Actual runtime review

After building, packaging and the existing live browser checks/capture:

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py prepare-runtime-review --character rook --motion-evidence 'ACTUAL_CAPTURE.webm'
```

Fill the returned runtime observation file after reviewing that exact video.
Each direction needs observed foot exchange, sliding and loop continuity for
walk and run, with two real times inside its captured segment. Turning,
speed changes, planted fire and resume also need time-specific observations.
The file identifies the video hash, build and actual reviewer. Pass it through
`review-runtime --observations ACTUAL_FILE` with the other existing arguments.
Final `deliver` revalidates this record and every cycle; a prose-only approval,
stale clip or unresolved visual rejection does not pass.

Handoffs prioritize `REPAIR_RUNTIME_VISUAL` when a runtime rejection exists.
Follow their `nextSource`/cycle command to resolve the source cause. Do not
approve the unchanged package to clear the label. The request to make this
workflow reliable is authorization to repair it, not evidence that the
character or an unperformed Luna run has succeeded.

```

## FILE: .agents/skills/sable-character-studio/references/aim-response.md
SHA256: 23086bd28ce73187ee0aa1d23814e3b1f73f763ced5b776b069b10f6b534b47a

```text
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

Node tests independently cover 30/60/120 Hz reversals, unchanged accepted gait,
ammo/recoil/cadence, latest-sample emission and non-homing flight. Retain the 40
locomotion cases and exact-build native temporal review for delivery. Preserve
prior accepted art/cycle reviews; new runtime bytes need new runtime evidence.

This repair and its tests are reusable by Luna, not an actual Luna reproduction
or a guarantee that every future character will pass without inspection.

```

## FILE: .agents/skills/sable-character-studio/references/browser-check.md
SHA256: 2cdc5890ee23b586a8cc930f9f91352173e7f8325be136b3074279a762729da6

```text
# Browser and package verification

Run from `motion_lab_v1`. Test the same package that will be handed over.

```powershell
node --test tests/*.test.js
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' -B -m unittest discover -s tests -p 'test_character_workflow.py' -v
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' package_standalone.py --character ID
```

Each character gets `dist/ID_Motion_Studio.html`, `dist/id.package.json` and
`public/standalone/id.html`. The shared `public/standalone.html` is changed only
with the explicit `--activate-preview` option. Previous HTML bytes are preserved
under `qa/package_history/ID`. An embedded `__MOTION_BUILD__` binds the actual
runtime, recipe and asset files; changed inputs require a new package and test.

## Live browser run

Use the available browser tool and its actual documented APIs; do not start a
separate browser automation backend. Reuse the lab's `serve.py` on loopback
14821 if it responds. A newly started owned server must use hidden windows and
project-local stdout/stderr logs so closing the launching terminal cannot leave
it serving broken responses. Do not kill unrelated processes by name.

Open `http://127.0.0.1:14821/standalone/id.html`. Use a native 1920×1080 viewport
for the review, and restore any temporary viewport override afterwards. Get
the actual canvas bounds and focus/state before input. Keep normal movement
facing enabled, action walk and time scale 1.00. Reset through the page control.

The browser capability `cdp` supports development inspection on this loopback
origin. After reading its documentation, press and hold the actual left mouse
button on the combat canvas using supported browser input (for example
`Input.dispatchMouseEvent` with `type: 'mousePressed'`). Do not replace a held
button with an instant click; `runCombatChecks` verifies `mouseDown` itself.

Start the dev-only runner through the page's JS development interface:

```js
window.__combatQA={status:'running'};
import('/qa/combat-checks.js')
  .then(m=>m.runCombatChecks())
  .then(report=>window.__combatQA={status:'complete',report})
  .catch(error=>window.__combatQA={status:'error',error:error.message});
```

Read completion in a later tool call; do not await this multi-second operation
inside a short-timeout CDP command. The runner covers 8 mouse facings, 8 fresh
movement-key facings while the real mouse button remains held, and key-repeat
parity, plus 16 immediate/first-frame/first-eligible-shot rapid-turn cases in
`rapidAim`. Read [the latency contract](aim-response.md) for their invariants.
Far-target cases also require the actual muzzle ray to converge on the
cursor; close-target cases reject backwards bullets. It uses synthetic DOM
direction events with the live fixed-step actor
and renderer, not physical Windows IME switching. Unit tests separately cover
IME-valued events and the 8×8 movement/aim matrix at 30/60/120 Hz.

Always release the actual mouse button in cleanup, including after failure.
Read the actual result, console errors and screenshots. Reject misaligned body,
visible muzzle/shot direction, stopped foot cycles or missing textures even if
the numeric runner passes. Frame cells are 8 directions, not continuous art.

Add the SHA-256 of the fetched `/qa/combat-checks.js` bytes as
`report.testScriptSHA256`; add the observed cross-origin resource URLs as
`report.externalResources` (an empty array only if actually empty). Save this
actual report via the existing project-only `POST /__qa/ID_combat_browser.json`
endpoint, or the file-writing tool. Do not author a passing report manually.
Save native screenshots with the browser's screenshot capability. Reload the
test page after inspecting/exporting evidence to remove temporary test state.

```powershell
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py verify-runtime --character ID --browser-report 'qa/ID_combat_browser.json'
```

This runs asset validation, all Node tests and embedded-JS parsing, then checks
the exact browser build digest, test script, all 17 + 16 rows, held-fire state,
movement, actual sprite direction, angular error and native review dimensions.
Without a browser report it returns technical-only status, never a live PASS.
Source and final visual review are separate from this runtime check.

That command alone now returns `PASS_INPUT_CHECKS_ONLY`. After releasing the
physical mouse, run `import('/qa/locomotion-checks.js').then(m=>m.runLocomotionChecks())`
through the same browser developer interface. Save the actual result as
`qa/ID_locomotion_browser.json`. The runner uses synthetic DOM chords with the
real actor/renderer in a bounded obstacle-free lane; it is not physical-key
coverage or an automatic anatomy judgment. Its 40 rows include non-firing walk
and run, moving fire, and fixed-feet stationary fire in every direction.

Use both reports for full runtime verification and delivery:

```powershell
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py verify-runtime --character ID --browser-report 'qa/ID_combat_browser.json' --locomotion-report 'qa/ID_locomotion_browser.json'
```

`review-runtime --decision approved` also requires `--locomotion-report` and
`--motion-evidence` with an actually watched, native 1920x1080 or larger video
spanning at least two seconds. Record the visual observations, not a numeric
PASS. `deliver` takes the same two reports and refuses a still-only, stale or
missing temporal review. See [gait repair](gait-repair.md) for source inspection.
It now also requires `--observations` from `prepare-runtime-review`, filled with
actual observations at video times for every direction and transition. Follow
[the cycle/runtime gate](cycle-review.md). Generic notes and video metadata
alone cannot create an approved delivery.

Validate each saved native capture with the repository's
`tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`
and a project-local `--output`. This checks dimensions and decoding, not artwork
quality. Do not change the responsive runtime or upscale a capture to manufacture
an evidence resolution.

For an in-scope user preview update, package with `--activate-preview`, reload
the already-open `/standalone.html`, verify it is the new build, and retain the
tab as the deliverable. Do not change GitHub, Pages or another character's
preview as a side effect of this local handoff.
# Temporal capture helper

The development-only `public/qa/capture-motion.js` exports
`captureMotion('ID_motion_native')`. Run it on the bound packaged page at a
native 1920x1080-or-larger viewport, with the physical mouse released. It records
the actual three live renderer canvases at 1:1 source pixels into a native
1920x1080 WebM, cycling through all eight walk/run directions, alternating
moving fire, stop transitions and stationary fire. It posts a bounded video
and its real build/phase/position observations to the local QA server.
Inspect the actual recording (and source-scale panels); its metadata explicitly
does not provide visual approval. It is never bundled into the delivered HTML.
Preserve the sibling JSON: review-runtime validates its video/build/script
hashes and recorded full cycles/transitions. Old footage cannot be relabeled
as evidence for a new package. Decode unindexed WebM sequentially with
`inspect_video.py`; do not trust seek indices or nominal WebM FPS metadata.

```

## FILE: .agents/skills/sable-character-studio/references/reuse-improvements.md
SHA256: f66a89c6b8f80ccaa23c789abc1dc3fd7f86718f4950e4230e7abe5fb2c6a0db

```text
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
| Exact-green normalization with raw-source/tool binding | `normalize_imagegen_chroma.py` + `intake_derived_frame.py` | Deterministic backdrop derivative only; never a new ImageGen claim or anatomy repair |

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

- Inspect native alpha channels and light/dark edges; painted checkerboard is
  not transparency. Preserve the failed source, then use a separately keyed
  green fallback when needed. Read ImageGen/identity instructions when doing
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

```

## FILE: motion_lab_v1/character_workflow.py
SHA256: 3fe7e4b449cc3adf8ab852f893e091b5189ef519ea2322e21db69a6cddc9fde6

```text
"""Small, local-only handoff workflow for the implemented Motion Studio route.

It inventories exact source slots, binds human/model visual observations to
their files, runs the real tests, and refuses stale or incomplete delivery.
It never calls an image API, fabricates reviews, or publishes a deployment.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']
PILOT=['E/idle/0','E/walk/0','E/walk/3','E/walk/1','E/walk/4','E/walk/2','E/walk/5']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(value):
    if not re.fullmatch(r'[a-z0-9_-]+',value):raise ValueError('Use an ASCII character id, not a path')
    return value
def local(value):
    path=(ROOT/value).resolve()
    if path==ROOT or not path.is_relative_to(ROOT):raise ValueError('Path must stay below motion_lab_v1')
    return path
def recipe(character):
    c=read(ROOT/'characters'/f'{ident(character)}.json')
    if c['id']!=character or local(c['source'])!=ROOT/'art'/character:raise ValueError('Recipe identity/source mismatch')
    if not {'walk','idle'}<=set(c['clips']) or set(c['clips'])-{'walk','idle','run'}:raise ValueError('Use explicit walk/idle and optional authored run clips')
    for clip in c['clips'].values():
        if type(clip.get('frames')) is not int or not 1<=clip['frames']<=24:raise ValueError('Invalid authored frame count')
        starts=clip.get('phaseStarts')
        if starts is not None and (not isinstance(starts,list) or len(starts)!=clip['frames'] or starts[0]!=0 or any(not isinstance(value,(int,float)) or isinstance(value,bool) or not 0<=value<1 for value in starts) or any(current<=previous for previous,current in zip(starts,starts[1:]))):raise ValueError('phaseStarts must begin at 0 and contain one increasing phase start per frame')
    if any(c['clips'][action]['frames']!=(1 if action=='idle' else 6) for action in c['clips']):raise ValueError('This six-phase workflow requires 6 walk/run frames and 1 idle frame per direction')
    return c
def slots(c):
    for direction in DIRECTIONS:
        for action,spec in c['clips'].items():
            for frame in range(spec['frames']):
                base=local(c['source'])/f'{direction}_{action}_{frame}'
                override=base.with_name(base.name+'_override.png')
                yield f'{direction}/{action}/{frame}',override if override.exists() else base.with_name(base.name+'_master.png')
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
def binding_valid(value):
    try:return sha(local(value['path']))==value['sha256']
    except (KeyError,ValueError,OSError,TypeError):return False

def invalidate_delivery(character,reason):
    """Keep prior evidence, but do not leave a rejected delivery as current."""
    path=ROOT/'dist'/f'{ident(character)}.delivery.json'
    if path.exists():
        previous=ROOT/'qa'/character/'delivery_history'/f'{sha(path)}.json'
        previous.parent.mkdir(parents=True,exist_ok=True)
        if not previous.exists():shutil.copy2(path,previous)
    package=ROOT/'dist'/f'{character}.package.json'
    write(path,{'recordedAt':stamp(),'character':character,'status':'HOLD_VISUAL_REPAIR','reason':reason,'package':binding(package) if package.exists() else None,'reviewedDelivery':False})

def source_status(character):
    c=recipe(character)
    if c.get('workflowVersion')!=1:
        return {'character':character,'ready':False,'mode':'existing-runtime','next':'Use verify-runtime for the accepted existing package. Start an explicit source migration before new art; do not invent historical source reviews.','slots':[],'errors':['Existing paired-source package has no new-workflow review ledger']}
    reference=local(c['identityReference']);errors=[]
    if not reference.exists() or sha(reference)!=c['referenceSHA256']:errors.append('Identity reference missing or changed')
    ledger=ROOT/'qa'/character/'source_reviews.json'
    reviews=read(ledger) if ledger.exists() else []
    rows=[];seen={}
    for name,path in slots(c):
        row={'slot':name,'path':path.relative_to(ROOT).as_posix(),'state':'missing'}
        if path.exists():
            digest=sha(path);row.update(sha256=digest,state='needs_review')
            receipt=path.with_suffix('.source.json')
            if not receipt.exists():row['state']='missing_provenance'
            else:
                r=read(receipt)
                if r.get('sha256')!=digest or r.get('generator')!='Codex built-in ImageGen' or not binding_valid(r.get('toolResponse')):row['state']='stale_provenance'
                if r.get('sourceMaster') and not binding_valid(r['sourceMaster']):row['state']='stale_provenance'
            if digest in seen:row['state']='duplicate_source';errors.append(f'{name}: same source as {seen[digest]}')
            seen[digest]=name
            current=[r for r in reviews if r['slot']==name]
            if row['state']=='needs_review' and current:
                review=current[-1]
                if review.get('sourceSHA256')==digest and review.get('referenceSHA256')==c['referenceSHA256'] and binding_valid(review.get('evidence')):
                    row['state']='approved' if review['decision']=='approved' else 'repair'
        rows.append(row)
    pending=[r for r in rows if r['state']!='approved']
    pilots=[r for slot in PILOT for r in pending if r['slot']==slot]
    repairs=[r for r in pending if r['state']=='repair']
    next_row=(repairs or pilots or pending or [None])[0]
    return {'character':character,'mode':'source-authoring','ready':not errors and not pending,'requiredFrames':len(rows),'approvedFrames':len(rows)-len(pending),'next':next_row or 'build','errors':errors,'slots':rows}

def review_source(character,slot,decision,evidence,notes,reviewer):
    c=recipe(character);path=dict(slots(c)).get(slot)
    if path is None or not path.exists():raise ValueError('Cannot review a missing source slot')
    if decision=='approved':
        from cycle_review import require_pilot
        direction,action,_=slot.split('/')
        require_pilot(character,direction,action)
    if not notes.strip() or not reviewer.strip():raise ValueError('Record the actual observation and reviewer')
    proof=local(evidence)
    if not proof.is_file():raise ValueError('Review evidence is missing')
    row={'recordedAt':stamp(),'slot':slot,'decision':decision,'reviewer':reviewer,'notes':notes,'sourceSHA256':sha(path),'referenceSHA256':c['referenceSHA256'],'evidence':binding(proof)}
    ledger=ROOT/'qa'/character/'source_reviews.json';reviews=read(ledger) if ledger.exists() else []
    reviews.append(row);write(ledger,reviews)
    if decision=='repair':
        quarantine=ROOT/'qa'/character/'quarantine'/sha(path);quarantine.mkdir(parents=True,exist_ok=True)
        for src in [path,path.with_suffix('.source.json'),proof]:
            if src.exists() and not (quarantine/src.name).exists():shutil.copy2(src,quarantine/src.name)
        write(quarantine/'review.json',row)
        invalidate_delivery(character,'Source rejected: '+slot+'; '+notes)
    return row

def workflow_status(character):
    """Source completeness is not cycle readiness or a runtime approval."""
    source=source_status(character)
    if source['mode']=='existing-runtime':return source
    from cycle_review import status as cycle_status
    cycles=cycle_status(character)
    runtime_path=ROOT/'qa'/character/'runtime_reviews.json'
    runtime=read(runtime_path)[-1] if runtime_path.exists() and read(runtime_path) else None
    rejected=runtime is not None and runtime.get('decision')=='repair'
    result=dict(source,sourcesReady=source['ready'],cycleStatus=cycles,runtimeRepairRequired=rejected,
                ready=source['ready'] and cycles['ready'] and not rejected,
                activeBuildReady=source['ready'] and cycles['ready'])
    pilot=next(r for r in cycles['cycles'] if r['direction']=='E' and r['action']=='walk')
    pilot_sources=[r for r in source['slots'] if r['slot'] in PILOT]
    pilot_sources_ready=len(pilot_sources)==len(PILOT) and all(r['state']=='approved' for r in pilot_sources)
    if pilot_sources_ready and pilot['state'] not in ('approved','missing_sources'):
        result['next']={'kind':'cycle-review',**pilot,'command':f'character_workflow.py prepare-cycle --character {character} --direction E'}
    elif source['ready'] and not cycles['ready']:
        pending=next(r for r in cycles['cycles'] if r['state']!='approved')
        result['next']={'kind':'cycle-review',**pending,'command':f'character_workflow.py prepare-cycle --character {character} --direction {pending["direction"]} --action {pending["action"]}'}
    elif source['ready'] and cycles['ready']:
        result['next']='repair-runtime-and-recapture' if rejected else 'build-reviewed-cycles'
    if rejected:result['runtimeRejection']=runtime
    return result

def check_package(character):
    from package_standalone import bundle_inputs
    report=read(ROOT/'dist'/f'{ident(character)}.package.json')
    current=bundle_inputs(character)
    if report['character']!=character or report['inputs']!=current:raise ValueError('Stale package: run package_standalone.py for this character')
    if report['inputSHA256']!=hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest():raise ValueError('Package input digest mismatch')
    destination=local(report['path'])
    if sha(destination)!=report['sha256'] or destination.stat().st_size!=report['bytes']:raise ValueError('Packaged HTML was changed')
    return report

def check_browser(character,path,package):
    report=read(local(path))
    expected={f'{mode}_{d}' for mode in ['mouse','keyboard'] for d in DIRECTIONS}|{'repeat_preserves_mouse'}
    rows=report.get('results',[])
    if report.get('kind')!='motion-studio-combat-browser' or report.get('character')!=character:raise ValueError('Wrong browser report')
    if report.get('build',{}).get('inputSHA256')!=package['inputSHA256']:raise ValueError('Browser report belongs to different source/runtime bytes')
    if report.get('testScriptSHA256')!=sha(ROOT/'public/qa/combat-checks.js'):raise ValueError('Browser test script changed; rerun it')
    if len(rows)!=17 or {r['name'] for r in rows}!=expected or report.get('pass') is not True:raise ValueError('Incomplete browser input matrix')
    for r in rows:
        facing='E' if r['name']=='repeat_preserves_mouse' else r['name'].split('_',1)[1]
        if r.get('pass') is not True or r.get('heldMouse') is not True or r.get('spriteDirection')!=facing or r.get('direction')!=facing or r.get('shotCount',0)<1 or r.get('observedShots')!=r.get('shotCount') or not r.get('travel',0)>.01 or not 0<=r.get('maxFacingErrorDegrees',999)<=24.51:
            raise ValueError('Browser case failed: '+r['name'])
        if r['name'] in ['mouse_E','mouse_S','mouse_W','mouse_N','repeat_preserves_mouse'] and (r.get('convergedShots',0)<1 or not 0<=r.get('maxCursorError',999)<1e-5):raise ValueError('Cursor convergence failed: '+r['name'])
    if report.get('externalResources')!=[]:raise ValueError('Standalone page used external resources or did not record them')
    if len(report.get('viewport',[]))!=2 or report['viewport'][0]<1920 or report['viewport'][1]<1080:raise ValueError('Use a native 1920x1080 or larger QA viewport')
    rapid=report.get('rapidAim',[])
    if len(rapid)!=16 or {r.get('name') for r in rapid}!={f'{mode}_{d}' for mode in ['stationary','moving'] for d in DIRECTIONS}:
        raise ValueError('Missing rapid aim latency matrix; eventual convergence is insufficient')
    import math
    for row in rapid:
        def finite(key):
            value=row.get(key)
            return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
        if any(row.get(k) is not True for k in ['pass','heldMouse','locomotionUnchanged','oldProjectileVelocityUnchanged']):raise ValueError('Rapid aim state failed: '+row['name'])
        if any(not finite(k) or row[k]>=1e-5 for k in ['immediateErrorDegrees','firstFrameErrorDegrees','shotErrorDegrees']):raise ValueError('Rapid aim used a stale input: '+row['name'])
        if any(not finite(k) for k in ['immediateMs','firstFrameMs','shotWaitSeconds','eligibleBudgetSeconds']):raise ValueError('Invalid aim timing')
        if row['immediateMs']>1000/120 or row['firstFrameMs']>50:raise ValueError('Aim response exceeds latency budget')
        if row['shotWaitSeconds']>row['eligibleBudgetSeconds']+1/120+1e-8 or row.get('shotCount',0)<1:raise ValueError('Projectile missed first eligible step')
        if not finite('travel') or (row['travel']<=.01 if row['name'].startswith('moving_') else row['travel']>=.01):raise ValueError('Rapid aim movement coverage missing')
    return binding(local(path))

def verify_runtime(character,browser_report=None,locomotion_report=None):
    package=check_package(character);out=ROOT/'qa'/character
    run=out/'checks'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');run.mkdir(parents=True)
    env=os.environ.copy();env.update(TEMP=str(run),TMP=str(run),PYTHONDONTWRITEBYTECODE='1')
    tests=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*.test.js'))
    commands=[[sys.executable,'-B','validate_character.py','--character',character],['node','--test',*tests],[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],['node','verify_bundle.mjs',str(local(package['path']))]]
    checks=[]
    for index,command in enumerate(commands):
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        log=run/f'{index}.log';log.write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        checks.append({'command':command,'exitCode':result.returncode,'log':binding(log)})
        if result.returncode:raise ValueError('Validation failed; inspect '+str(log.relative_to(ROOT)))
    browser=check_browser(character,browser_report,package) if browser_report else None
    from locomotion_review import check as check_locomotion
    locomotion=check_locomotion(ROOT,character,locomotion_report,package) if locomotion_report else None
    result={'recordedAt':stamp(),'character':character,'status':'PASS_RUNTIME_CHECKS' if browser and locomotion else 'PASS_INPUT_CHECKS_ONLY' if browser else 'PASS_TECHNICAL_ONLY','package':binding(ROOT/'dist'/f'{character}.package.json'),'inputSHA256':package['inputSHA256'],'checks':checks,'browser':browser,'locomotion':locomotion,'scope':'Input plus temporal selected-renderer checks when supplied; no automatic anatomy, foot-contact, visual approval or Luna generation claim'}
    write(run/'result.json',result);write(out/'latest_runtime_check.json',result)
    return result

def review_runtime(character,evidence,decision,notes,reviewer,locomotion_report=None,motion_evidence=None,observations=None):
    from PIL import Image
    package=check_package(character);path=local(evidence)
    with Image.open(path) as image:
        image.load();width,height=image.size
    if width<1920 or height<1080:raise ValueError('Runtime visual review needs native 1920x1080 evidence')
    if not notes.strip() or not reviewer.strip():raise ValueError('Record actual visual observations and reviewer')
    result={'recordedAt':stamp(),'character':character,'inputSHA256':package['inputSHA256'],'evidence':binding(path),'nativeDimensions':[width,height],'decision':decision,'notes':notes,'reviewer':reviewer}
    if decision=='approved':
        from cycle_review import require_build
        require_build(character)
        if not locomotion_report or not motion_evidence:raise ValueError('A still image cannot approve gait. Supply current --locomotion-report and native --motion-evidence video after watching it')
        from locomotion_review import check as check_locomotion
        result['locomotion']=check_locomotion(ROOT,character,locomotion_report,package)
        import cv2
        video=local(motion_evidence);cap=cv2.VideoCapture(str(video))
        w,h,frames,fps=[cap.get(k) for k in [cv2.CAP_PROP_FRAME_WIDTH,cv2.CAP_PROP_FRAME_HEIGHT,cv2.CAP_PROP_FRAME_COUNT,cv2.CAP_PROP_FPS]]
        ok,_=cap.read();cap.release()
        if not ok or w<1920 or h<1080 or fps<=0 or frames/fps<2:raise ValueError('Motion review requires a decodable native 1080p video spanning at least two seconds')
        result['motionEvidence']=binding(video)
        from motion_evidence import check as check_motion
        result['motionCapture']=check_motion(ROOT,video,package)
        if not observations:raise ValueError('Supply time-specific --observations; generic notes cannot approve gait')
        from runtime_observations import validate
        validate(read(local(observations)),character,package,read(video.with_suffix('.json')),reviewer)
        result['observations']=binding(local(observations))
    path=ROOT/'qa'/character/'runtime_reviews.json';history=read(path) if path.exists() else [];history.append(result);write(path,history)
    if decision!='approved':invalidate_delivery(character,'Runtime visual review requires repair: '+notes)
    return result

def deliver(character,browser_report,locomotion_report):
    from cycle_review import require_build
    cycle_checks=require_build(character)
    # Fail before expensive tests when a visible rejection is still current.
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json')
    if not reviews or reviews[-1].get('decision')!='approved':raise ValueError('Current runtime visual rejection/missing review must be resolved before delivery')
    status=source_status(character)
    if not status['ready']:raise ValueError('Source review is incomplete: '+json.dumps(status['next'],ensure_ascii=False))
    result=verify_runtime(character,browser_report,locomotion_report)
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json');review=reviews[-1]
    if review['decision']!='approved' or review['inputSHA256']!=result['inputSHA256'] or not binding_valid(review['evidence']) or not binding_valid(review.get('motionEvidence')) or not binding_valid(review.get('motionCapture')) or review.get('locomotion')!=result['locomotion']:raise ValueError('Current temporal/visual review is missing, failed, or stale')
    if not binding_valid(review.get('observations')):raise ValueError('Time-specific runtime visual observations are missing/stale')
    from runtime_observations import validate
    validate(read(local(review['observations']['path'])),character,check_package(character),read(local(review['motionCapture']['path'])),review['reviewer'])
    from motion_evidence import check as check_motion
    check_motion(ROOT,local(review['motionEvidence']['path']),check_package(character))
    result.update(status='REVIEWED_DELIVERY',sourceReviews=binding(ROOT/'qa'/character/'source_reviews.json'),runtimeReviews=binding(ROOT/'qa'/character/'runtime_reviews.json'),cycleReviews=binding(ROOT/'qa'/character/'cycle_reviews.json'),cycleChecks=cycle_checks)
    write(ROOT/'dist'/f'{character}.delivery.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['status','handoff','build','verify-runtime','deliver','review-source','review-runtime']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident)
        if name in ['verify-runtime','deliver']:s.add_argument('--browser-report',required=name=='deliver')
        if name in ['verify-runtime','deliver','review-runtime']:s.add_argument('--locomotion-report',required=name=='deliver')
        if name=='review-runtime':s.add_argument('--motion-evidence');s.add_argument('--observations')
        if name in ['review-source','review-runtime']:
            s.add_argument('--decision',choices=['approved','repair'],required=True);s.add_argument('--evidence',required=True);s.add_argument('--notes',required=True);s.add_argument('--reviewer',required=True)
        if name=='review-source':s.add_argument('--slot',required=True)
        if name=='handoff':s.add_argument('--output',help='New packet path below motion_lab_v1/qa; never overwritten')
    s=sub.add_parser('verify-handoff');s.add_argument('--packet',required=True)
    s=sub.add_parser('verify-improvements');s.add_argument('--output',help='Optional fresh QA receipt path')
    s=sub.add_parser('prepare-runtime-review');s.add_argument('--character',required=True,type=ident);s.add_argument('--motion-evidence',required=True)
    for name in ['prepare-cycle','review-cycle']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident);s.add_argument('--direction',required=True,choices=DIRECTIONS);s.add_argument('--action',default='walk',choices=['walk','run'])
        if name=='review-cycle':
            s.add_argument('--decision',required=True,choices=['approved','repair']);s.add_argument('--packet');s.add_argument('--evidence');s.add_argument('--notes');s.add_argument('--reviewer')
    a=p.parse_args()
    try:
        if a.command=='status':result=workflow_status(a.character)
        elif a.command=='prepare-cycle':
            from cycle_preview import prepare
            result=prepare(a.character,a.direction,a.action)
        elif a.command=='review-cycle':
            from cycle_review import record
            result=record(a.character,a.direction,a.action,a.decision,a.packet,a.evidence,a.notes,a.reviewer)
        elif a.command=='prepare-runtime-review':
            from motion_evidence import check as check_motion
            from runtime_observations import template
            package=check_package(a.character);video=local(a.motion_evidence);check_motion(ROOT,video,package)
            path=ROOT/'qa'/a.character/'runtime_observations'/f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json'
            write(path,template(a.character,package,read(video.with_suffix('.json'))))
            result={'status':'UNREVIEWED_RUNTIME_TEMPLATE','path':str(path)}
        elif a.command=='handoff':
            from character_handoff import make
            packet=make(a.character)
            path=local(a.output or f'qa/{a.character}/handoffs/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json')
            if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA packet path; prior handoffs are preserved')
            write(path,packet)
            result={'status':packet['status'],'packet':str(path),'nextAction':packet['nextAction'],'nextSource':packet['nextSource'],'warnings':packet['warnings'],'reviewedDelivery':False,'lunaGenerationTested':False}
        elif a.command=='verify-handoff':
            from character_handoff import verify
            result=verify(a.packet)
        elif a.command=='verify-improvements':
            from improvement_harness import verify_r3
            result=verify_r3(ROOT.parent)
            if a.output:
                path=local(a.output)
                if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA receipt path')
                write(path,result)
            result={k:v for k,v in result.items() if k!='inputs'}
        elif a.command=='build':
            status=source_status(a.character)
            if not status['ready']:raise ValueError('Resolve source status first: '+json.dumps(status['next'],ensure_ascii=False))
            from build_character import compile_character
            result=compile_character(ROOT/'characters'/f'{a.character}.json')
        elif a.command=='verify-runtime':result=verify_runtime(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='deliver':result=deliver(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='review-source':result=review_source(a.character,a.slot,a.decision,a.evidence,a.notes,a.reviewer)
        else:result=review_runtime(a.character,a.evidence,a.decision,a.notes,a.reviewer,a.locomotion_report,a.motion_evidence,a.observations)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'NEEDS_FIX','error':str(error)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())

```

## FILE: motion_lab_v1/cycle_review.py
SHA256: f30af549dc7097a296aa3c1f197fa5f4a586f995ece077f3c15cc712145292ab

```text
"""Whole-cycle review gate. Pixel/landmark checks do not replace actual observation.

Templates are deliberately incomplete. No automatic art approval or provider calls.
"""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import character_workflow as w
import gait_contract as contract

OBSERVATIONS = ('oppositeContacts', 'passingAndSwing', 'loopSeam', 'footSliding',
                'bodyContinuity', 'weaponContinuity')


def inputs(character, direction, action='walk'):
    c = w.recipe(character)
    if direction not in w.DIRECTIONS or action not in c['clips'] or action == 'idle':
        raise ValueError('Use an authored walk/run cycle and a valid direction')
    selected = dict(w.slots(c))
    names = [f'{direction}/{action}/{i}' for i in range(6)]
    files = [selected[name] for name in names]
    return {'character': character, 'direction': direction, 'action': action,
            'recipe': w.binding(w.ROOT / 'characters' / f'{character}.json'),
            'identity': w.binding(w.local(c['identityReference'])),
            'contractSHA256': contract.digest(),
            'compilerSHA256': w.sha(Path(__file__).with_name('build_atlas.py')),
            'reviewCodeSHA256': w.sha(Path(__file__)),
            'sources': [dict(slot=name, **w.binding(path)) for name, path in zip(names, files)]}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_content(value):
    return {row['slot']:row['sha256'] for row in value['sources']}


def ledger(character):
    path = w.ROOT / 'qa' / character / 'cycle_reviews.json'
    return w.read(path) if path.exists() else []


def current(character, direction, action='walk'):
    try:
        expected = inputs(character, direction, action)
    except (OSError, ValueError):
        return {'direction': direction, 'action': action, 'state': 'missing_sources'}
    rows = [r for r in ledger(character) if r['direction'] == direction and r['action'] == action]
    latest = rows[-1] if rows else None
    state = 'needs_cycle_review'
    if latest and latest['decision'] == 'repair':
        state = 'repair' if source_content(latest['inputs']) == source_content(expected) else 'needs_cycle_review'
    elif latest and latest.get('inputs') == expected:
        try:
            if not w.binding_valid(latest.get('packet')):
                raise ValueError('Changed cycle review packet')
            validate_packet(w.read(w.local(latest['packet']['path'])), expected)
            state = 'approved'
        except (OSError, ValueError, KeyError, TypeError):
            state = 'stale_cycle_review'
    return {'direction': direction, 'action': action, 'state': state,
            'inputSHA256': signature(expected)}


def status(character):
    c = w.recipe(character)
    if c.get('workflowVersion') != 1:
        return {'required': False, 'ready': True, 'cycles': []}
    rows = [current(character, d, a) for a in c['clips'] if a != 'idle' for d in w.DIRECTIONS]
    return {'required': True, 'ready': all(r['state'] == 'approved' for r in rows), 'cycles': rows}


def require_pilot(character, direction, action='walk'):
    c = w.recipe(character)
    if c.get('workflowVersion') != 1 or (direction == 'E' and action != 'run'):
        return
    pilot_sources=[r for r in w.source_status(character)['slots'] if r['slot'].startswith('E/walk/') or r['slot']=='E/idle/0']
    if current(character, 'E')['state'] != 'approved' or len(pilot_sources)!=7 or any(r['state']!='approved' for r in pilot_sources):
        raise ValueError('E full-cycle review required before expanding source art; run prepare-cycle --character ' + character + ' --direction E')


def require_build(character):
    if not w.source_status(character)['ready']:
        raise ValueError('Source approvals are incomplete')
    result = status(character)
    if not result['ready']:
        pending = next(r for r in result['cycles'] if r['state'] != 'approved')
        raise ValueError('Whole-cycle review required before active build: ' + pending['direction'] + '/' + pending['action'])
    return result


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


@lru_cache(maxsize=16)
def decoded_video(path, digest):
    """Cache only already hash-checked bytes, not caller-declared dimensions."""
    import cv2
    cap = cv2.VideoCapture(path)
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame.shape[:2] != (1080, 1920):
                raise ValueError('Cycle video is not native 1920x1080')
            frames += 1
        if not finite(fps) or fps <= 0 or frames == 0:
            raise ValueError('Cycle video must actually decode, not only have metadata')
        return frames, fps
    finally:
        cap.release()


def validate_landmarks(packet, clip, atlas):
    """Check observed anatomy labels against source pixels and opposite contacts."""
    import numpy as np
    frames = packet.get('frames', [])
    if len(frames) != 6 or [f.get('index') for f in frames] != list(range(6)):
        raise ValueError('Record all six chronological phases')
    markers = packet.get('legMarkers', {})
    if any(not isinstance(markers.get(side), str) or len(markers[side].strip()) < 8 for side in ('left', 'right')) or markers['left'] == markers['right']:
        raise ValueError('Identify each anatomical leg by actual costume/hip continuity')
    cw, ch = clip['cell']
    height = clip['height']
    theta = w.DIRECTIONS.index(packet['direction']) * math.pi / 4
    axis = [math.cos(theta), .5 * math.sin(theta)]
    norm = math.hypot(*axis)
    axis = [v / norm for v in axis]
    leads = []
    for i, row in enumerate(frames):
        phase = contract.PHASES[i]
        if row.get('phase') != phase['name'] or row.get('support') != phase['support']:
            raise ValueError('Observed support/phase differs from contract at frame ' + str(i))
        points = row.get('landmarks', {})
        for side in ('left', 'right'):
            for part in ('Hip', 'Knee', 'Sole'):
                point = points.get(side + part)
                if not isinstance(point, list) or len(point) != 2 or not all(finite(v) for v in point):
                    raise ValueError('Missing observed native-cell landmarks')
                x, y = point
                if not (0 <= x < cw and 0 <= y < ch):
                    raise ValueError('Landmark outside compiled cell')
                ox, oy = i % clip['columns'] * cw, i // clip['columns'] * ch
                region = atlas[oy + max(0, int(y)-5):oy + min(ch, int(y)+6),
                               ox + max(0, int(x)-5):ox + min(cw, int(x)+6), 3]
                if not np.any(region > 128):
                    raise ValueError('Landmark is not on visible subject pixels')
            hip, knee, sole = (points[side + p] for p in ('Hip', 'Knee', 'Sole'))
            if hip[1] >= knee[1] or knee[1] >= sole[1] or sole[1] - hip[1] < height * .18:
                raise ValueError('Trace the same connected leg from hip through knee to sole')
        left, right = points['leftSole'], points['rightSole']
        if math.dist(left, right) < height * .025:
            raise ValueError('Both leg labels point to the same foot')
        leads.append(sum((a-b)*d for a,b,d in zip(left, right, axis)))
    if leads[0] < height * .04 or leads[3] > -height * .04:
        raise ValueError('Opposite contacts do not exchange left/right leading feet')
    return True


def validate_packet(packet, expected):
    if packet.get('kind') != 'sable-cycle-observation' or packet.get('inputs') != expected:
        raise ValueError('Cycle review belongs to different sources, recipe or contract')
    if packet.get('character') != expected['character'] or packet.get('direction') != expected['direction'] or packet.get('action') != expected['action']:
        raise ValueError('Cycle identity mismatch')
    preview_binding = packet.get('preview')
    if not w.binding_valid(preview_binding):
        raise ValueError('Missing/stale complete-cycle preview')
    preview = w.read(w.local(preview_binding['path']))
    if preview.get('cycleInputs') != expected:
        raise ValueError('Preview does not match current source cycle')
    for key in ('video', 'atlas', 'contact'):
        if not w.binding_valid(preview.get(key)):
            raise ValueError('Changed cycle preview ' + key)
    if preview.get('nativeVideo') != [1920, 1080] or preview.get('cycles', 0) < 3:
        raise ValueError('Review three native 1080p cycles at recipe speed')
    if not finite(preview.get('durationSeconds')) or preview['durationSeconds'] < 2:
        raise ValueError('Missing cycle duration')
    frames, fps = decoded_video(str(w.local(preview['video']['path'])), preview['video']['sha256'])
    if abs(frames / fps - preview['durationSeconds']) > 1 / fps:
        raise ValueError('Cycle duration differs from decoded video')
    c = w.read(w.local(expected['recipe']['path']))
    action = expected['action']
    speed = c['locomotion'][action + 'Speed']
    stride = c['locomotion'][action + 'Stride']
    if not all(finite(v) and v > 0 for v in (speed, stride)) or frames / fps * speed / stride < 3 - 1e-6:
        raise ValueError('Decoded video does not span three cycles at recipe speed')
    if not isinstance(packet.get('reviewer'), str) or not packet['reviewer'].strip():
        raise ValueError('Record the actual reviewer')
    if packet.get('decision') != 'approved':
        raise ValueError('Unreviewed or rejected cycle')
    if not isinstance(packet.get('observations'), dict):
        raise ValueError('Missing timed visual observations')
    for name in OBSERVATIONS:
        row = packet['observations'].get(name, {})
        times = row.get('seconds', [])
        if (row.get('decision') != 'pass' or not isinstance(row.get('notes'), str) or len(row['notes'].strip()) < 12 or
                not isinstance(times, list) or len(times) < 2 or
                not all(finite(t) and 0 <= t <= preview['durationSeconds'] for t in times) or
                any(b <= a for a,b in zip(times, times[1:]))):
            raise ValueError('Record actual timed observations: ' + name)
    from PIL import Image
    import numpy as np
    with Image.open(w.local(preview['atlas']['path'])) as im:
        if im.mode != 'RGBA':
            raise ValueError('Cycle atlas needs real alpha')
        validate_landmarks(packet, preview['clip'], np.array(im))
    return True


def record(character, direction, action, decision, packet_path=None, evidence=None, notes=None, reviewer=None):
    expected = inputs(character, direction, action)
    digest = signature(expected)
    previous = ledger(character)
    row = dict(character=character, direction=direction, action=action, inputs=expected,
               inputSHA256=digest, recordedAt=w.stamp(), decision=decision)
    if decision == 'approved':
        require_pilot(character, direction, action)
        source_rows=[r for r in w.source_status(character)['slots'] if r['slot'].startswith(f'{direction}/{action}/')]
        if len(source_rows)!=6 or any(r['state']!='approved' for r in source_rows):
            raise ValueError('Review the six current source frames before approving their cycle')
        rejected_sources = [source_content(r['inputs']) for r in previous
                            if r['direction'] == direction and r['action'] == action and r['decision'] == 'repair']
        if source_content(expected) in rejected_sources:
            raise ValueError('Rejected cycle source bytes are unchanged; metadata edits cannot repair art')
        packet = w.read(w.local(packet_path))
        validate_packet(packet, expected)
        row.update(packet=w.binding(w.local(packet_path)), reviewer=packet['reviewer'])
    else:
        if not notes or not reviewer or not evidence or not w.local(evidence).is_file():
            raise ValueError('Record real rejection observations and evidence')
        row.update(notes=notes, reviewer=reviewer, evidence=w.binding(w.local(evidence)))
    previous.append(row)
    w.write(w.ROOT / 'qa' / character / 'cycle_reviews.json', previous)
    if decision != 'approved':
        w.invalidate_delivery(character, f'Cycle rejected: {direction}/{action}; {notes}')
    return row

```

## FILE: motion_lab_v1/gait_contract.py
SHA256: e297710d2fc2ecbf39f8e5920d1b31cb8e3cfd15d82b18cb79461b98c3c98a9a

```text
"""One maintained six-phase vocabulary for requests, previews and reviews."""
import hashlib
import json

VERSION = 1
PHASES = (
    {'index': 0, 'name': 'left_contact', 'support': 'double', 'lead': 'left',
     'prompt': 'right leg trailing / left forward contact'},
    {'index': 1, 'name': 'right_swing', 'support': 'left', 'lead': None,
     'prompt': 'right leg swings behind / left supports'},
    {'index': 2, 'name': 'right_passing', 'support': 'left', 'lead': None,
     'prompt': 'right knee passes forward / left supports'},
    {'index': 3, 'name': 'right_contact', 'support': 'double', 'lead': 'right',
     'prompt': 'left leg trailing / right forward contact'},
    {'index': 4, 'name': 'left_swing', 'support': 'right', 'lead': None,
     'prompt': 'left leg swings behind / right supports'},
    {'index': 5, 'name': 'left_passing', 'support': 'right', 'lead': None,
     'prompt': 'left knee passes forward / right supports'},
)
# Accepted ASTER contact-dwell starting point; visual calibration remains required.
WALK_PHASE_STARTS = [0, .2, .33, .5, .7, .83]


def digest():
    return hashlib.sha256(json.dumps({'version': VERSION, 'phases': PHASES,
        'walkPhaseStarts': WALK_PHASE_STARTS}, sort_keys=True).encode()).hexdigest()


def starts(spec):
    values = spec.get('phaseStarts', [i / 6 for i in range(6)])
    if (len(values) != 6 or values[0] != 0 or
            any(type(v) not in (int, float) or not 0 <= v < 1 for v in values) or
            any(b <= a for a, b in zip(values, values[1:]))):
        raise ValueError('Invalid six-phase timing')
    return values


def frame_at(phase, phase_starts):
    p = phase % 1
    return max(i for i, start in enumerate(phase_starts) if p >= start)

```

## FILE: motion_lab_v1/intake_frame.py
SHA256: 2b88be3cc3037a96861f6aa70d5cd6c849fe220a65f85656d4a94b67fb8da200

```text
"""Copy an actual selected ImageGen output into its recipe slot, preserving source."""
from pathlib import Path
import argparse,json,hashlib,shutil,datetime,re
from PIL import Image
ROOT=Path(__file__).resolve().parent

def intake(ident,direction,action,frame,source,tool_response=None):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):raise ValueError('Invalid character id')
    config=json.loads((ROOT/'characters'/f'{ident}.json').read_text(encoding='utf-8-sig'))
    if direction not in ['E','SE','S','SW','W','NW','N','NE'] or action not in config['clips'] or not 0<=frame<config['clips'][action]['frames']:raise ValueError('Invalid recipe slot')
    from cycle_review import require_pilot
    require_pilot(ident,direction,action)
    image=Image.open(source);image.verify()
    native=list(Image.open(source).size)
    if max(native)<1024:raise ValueError('A native high-resolution original is required')
    folder=(ROOT/config['source']).resolve()
    if folder!=ROOT/'art'/ident:raise ValueError('Source folder must be art/CHARACTER')
    if config.get('workflowVersion') and tool_response is None:raise ValueError('Supply --tool-response with the actual saved ImageGen tool response')
    proof=None
    if tool_response is not None:
        tool_response=tool_response.resolve()
        if not tool_response.is_relative_to(ROOT):raise ValueError('Copy the tool response into this lab first')
        raw=tool_response.read_text(encoding='utf-8-sig');response=json.loads(raw)
        if response.get('tool')!='image_gen.imagegen' or not response.get('result') or Path(response.get('returnedPath','')).resolve()!=source.resolve():
            raise ValueError('Tool response must identify the actual ImageGen result and returned file')
        proof={'path':tool_response.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(tool_response.read_bytes()).hexdigest()}
    target=folder/f'{direction}_{action}_{frame}_master.png'
    override=folder/f'{direction}_{action}_{frame}_override.png'
    if override.exists():target=override
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()==digest and target.with_suffix('.source.json').exists():return target
        history=folder/'previous';history.mkdir(exist_ok=True);old=hashlib.sha256(target.read_bytes()).hexdigest()[:12];shutil.copy2(target,history/(target.stem+'_'+old+target.suffix))
        previous_receipt=target.with_suffix('.source.json')
        if previous_receipt.exists():shutil.copy2(previous_receipt,history/(target.stem+'_'+old+'.source.json'))
    if source.resolve()!=target:shutil.copy2(source,target)
    receipt={'generator':'Codex built-in ImageGen','importedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source.resolve()),'native':native,'sha256':digest,'destination':target.relative_to(ROOT).as_posix()}
    if proof:receipt['toolResponse']=proof
    target.with_suffix('.source.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--generated',type=Path,required=True);p.add_argument('--tool-response',type=Path);a=p.parse_args();intake(a.character,a.direction,a.action,a.frame,a.generated,a.tool_response)

```

## FILE: motion_lab_v1/intake_pair.py
SHA256: 11f19d5501ed57daed2404adc8424e3726aba577ff70ed7221a9718c59b48e2d

```text
"""Import a real ImageGen opposite-pose pair, preserving the native green master.

Deterministic subject separation only: no resynthesis, limb warp, resizing or
upscaling. The exact generated pair and tool metadata remain the provenance.
"""
import argparse,json,hashlib,shutil,datetime
from pathlib import Path
from PIL import Image
from build_atlas import subjects
from character_workflow import ROOT,recipe,local,binding,write,sha,DIRECTIONS

def intake(character,direction,action,pair,generated,tool_response,side_filter=None):
    c=recipe(character);count=c['clips'][action]['frames']
    if direction not in DIRECTIONS or count!=6 or not 0<=pair<3:raise ValueError('Use an existing six-frame recipe and pair 0/1/2')
    from cycle_review import require_pilot
    require_pilot(character,direction,action)
    proof=local(tool_response);r=json.loads(proof.read_text(encoding='utf-8-sig'));generated=Path(generated).resolve()
    if r.get('tool')!='image_gen.imagegen' or not r.get('result') or Path(r.get('returnedPath','')).resolve()!=generated:raise ValueError('Must bind the actual ImageGen tool result')
    with Image.open(generated) as im:
        native=list(im.size)
        if min(native)<1024 or max(native)<1536:raise ValueError('Pair must be native 1536x1024 or larger')
    digest=sha(generated);masters=ROOT/'art'/character/'gait_v8'/'native_pairs';masters.mkdir(parents=True,exist_ok=True)
    master=masters/f'{direction}_{action}_pair{pair}_{digest[:12]}.png'
    if not master.exists():shutil.copy2(generated,master)
    if sha(master)!=digest:raise ValueError('Master copy hash mismatch')
    rows=[]
    for side,(im,box) in enumerate(subjects(master,2)):
        if side_filter is not None and side != side_filter:continue
        # Kept at original pixel density. A native image is not upscaled to
        # pretend that a low-resolution sheet cell was a high-resolution source.
        if im.height<800:raise ValueError('Subject is too small for the current 656px atlas; request a native pair')
        index=pair+side*3;folder=local(c['source']);target=folder/f'{direction}_{action}_{index}_master.png'
        override=folder/f'{direction}_{action}_{index}_override.png'
        if override.exists():target=override
        if target.exists():
            previous=ROOT/'qa'/character/'quarantine'/sha(target);previous.mkdir(parents=True,exist_ok=True)
            for old in [target,target.with_suffix('.source.json')]:
                if old.exists() and not (previous/old.name).exists():shutil.copy2(old,previous/old.name)
        im.save(target)
        receipt={'generator':'Codex built-in ImageGen','importedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'sha256':sha(target),'native':list(im.size),'destination':target.relative_to(ROOT).as_posix(),
                 'toolResponse':binding(proof),'sourceMaster':binding(master),'masterNative':native,
                 'derivation':{'kind':'chroma-key and connected-subject crop only','box':box,'resampling':False,'anatomicalWarp':False}}
        write(target.with_suffix('.source.json'),receipt);rows.append(receipt)
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',default='walk');p.add_argument('--pair',type=int,required=True);p.add_argument('--generated',required=True);p.add_argument('--tool-response',required=True)
    p.add_argument('--side',type=int,choices=[0,1],help='Import only an actually reviewed half; a failed partner is not promoted')
    a=p.parse_args();print(json.dumps(intake(a.character,a.direction,a.action,a.pair,a.generated,a.tool_response,a.side),ensure_ascii=False))

```

## FILE: motion_lab_v1/intake_derived_frame.py
SHA256: 39124e89fadd0407007d7ac5ec6b490dc28ff6f1833ba9d35240691f6044b202

```text
"""Import a deterministic source-art derivative without faking an ImageGen receipt.

The ImageGen result remains the appearance authority.  This importer is for a
project-local, byte-preserving matte normalization (for example, replacing a
near-green exterior with exact ``#00FF00``).  It binds the original generated
master, the untouched tool response, and the normalization report so a
derived frame cannot masquerade as a fresh generation result.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from character_workflow import DIRECTIONS, ROOT, binding, local, recipe, sha, slots, write


GREEN = (0, 255, 0)


def _path(value: str | Path, label: str) -> Path:
    path = Path(value).resolve()
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    return path


def _verify_derivative(derived: Path, source_master: Path, tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    if not source_master.is_relative_to(ROOT):
        raise ValueError("source master must be copied below motion_lab_v1")
    if not tool_response.is_relative_to(ROOT) or not report.is_relative_to(ROOT) or not mask.is_relative_to(ROOT):
        raise ValueError("provenance and QA files must be below motion_lab_v1")
    response = json.loads(tool_response.read_text(encoding="utf-8-sig"))
    if response.get("tool") != "image_gen.imagegen" or not response.get("result"):
        raise ValueError("tool response is not the actual ImageGen response")
    project_copy = response.get("projectCopy")
    if project_copy is None or local(project_copy) != source_master:
        raise ValueError("tool response must bind the project copy of the generated master")
    if response.get("projectCopySHA256") != sha(source_master):
        raise ValueError("generated master copy hash does not match tool response")

    normalize = json.loads(report.read_text(encoding="utf-8-sig"))
    if normalize.get("operation") != "edge-connected green matte normalization only; no source-art redraw":
        raise ValueError("unexpected normalization operation")
    if normalize.get("input_sha256") != sha(source_master):
        raise ValueError("normalization input is not the bound generated master")
    if normalize.get("output_sha256") != sha(derived):
        raise ValueError("normalization output hash is stale")
    if normalize.get("mask_sha256") != sha(mask) or normalize.get("subject_pixels_byte_exact") is not True:
        raise ValueError("normalization mask/report is stale")
    if normalize.get("alpha_ready") is not True:
        raise ValueError("normalization did not produce an alpha-ready source")

    with Image.open(derived) as image:
        image.load()
        if image.mode != "RGB":
            raise ValueError("normalized green source must remain RGB")
        if min(image.size) < 1024:
            raise ValueError("a native high-resolution source is required")
        rgb = np.asarray(image)
    with Image.open(mask) as mask_image:
        mask_image.load()
        mask_array = np.asarray(mask_image.convert("L"))
    if mask_array.shape != rgb.shape[:2] or not set(np.unique(mask_array)).issubset({0, 255}):
        raise ValueError("normalization mask must be native binary")
    background = mask_array == 0
    if not background.any() or not np.all(rgb[background] == np.asarray(GREEN, dtype=np.uint8)):
        raise ValueError("derived background is not exact uniform green")
    return {
        "toolResponse": binding(tool_response),
        "sourceMaster": binding(source_master),
        "normalization": binding(report),
        "mask": binding(mask),
        "native": [int(rgb.shape[1]), int(rgb.shape[0])],
        "backgroundPixels": int(background.sum()),
    }


def intake(character: str, direction: str, action: str, frame: int, derived: Path, source_master: Path,
           tool_response: Path, report: Path, mask: Path) -> dict[str, object]:
    config = recipe(character)
    if direction not in DIRECTIONS or action not in config["clips"]:
        raise ValueError("invalid recipe slot")
    if not 0 <= frame < config["clips"][action]["frames"]:
        raise ValueError("invalid recipe frame")
    from cycle_review import require_pilot
    require_pilot(character, direction, action)
    source_master = _path(source_master, "source master")
    derived = _path(derived, "derived frame")
    tool_response = _path(tool_response, "tool response")
    report = _path(report, "normalization report")
    mask = _path(mask, "normalization mask")
    provenance = _verify_derivative(derived, source_master, tool_response, report, mask)

    target = dict(slots(config))[(f"{direction}/{action}/{frame}")]
    if target.exists():
        old_hash = sha(target)
        previous = ROOT / "qa" / character / "quarantine" / old_hash
        previous.mkdir(parents=True, exist_ok=True)
        for old in (target, target.with_suffix(".source.json")):
            if old.exists() and not (previous / old.name).exists():
                shutil.copy2(old, previous / old.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(derived, target)
    digest = sha(target)
    if digest != sha(derived):
        raise ValueError("derived frame copy hash mismatch")
    receipt = {
        "generator": "Codex built-in ImageGen",
        "importedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sha256": digest,
        "native": provenance["native"],
        "destination": target.relative_to(ROOT).as_posix(),
        "toolResponse": provenance["toolResponse"],
        "sourceMaster": provenance["sourceMaster"],
        "derivation": {
            "kind": "edge-connected green matte normalization only; no source-art redraw",
            "normalization": provenance["normalization"],
            "mask": provenance["mask"],
            "resampling": False,
            "anatomicalWarp": False,
            "subjectPixelsByteExact": True,
            "backgroundPixels": provenance["backgroundPixels"],
        },
    }
    write(target.with_suffix(".source.json"), receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    parser.add_argument("--direction", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--frame", type=int, required=True)
    parser.add_argument("--derived", required=True)
    parser.add_argument("--source-master", required=True)
    parser.add_argument("--tool-response", required=True)
    parser.add_argument("--normalization-report", required=True)
    parser.add_argument("--mask", required=True)
    args = parser.parse_args()
    print(json.dumps(intake(args.character, args.direction, args.action, args.frame,
                            Path(args.derived), Path(args.source_master), Path(args.tool_response),
                            Path(args.normalization_report), Path(args.mask)), ensure_ascii=False))

```

## FILE: motion_lab_v1/prepare_enemy_asset.py
SHA256: 2f7afcdc35c989fe83f6550356f1543cc70162d2328f790c200917c98e499b61

```text
"""Deterministic enemy matte/crop and native QA. Never activates an app asset.

Uses the established model-free compiler. Source artwork stays byte-immutable.
No leg segmentation, anatomical warp, local model or synthetic missing pixels.
"""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageDraw
import numpy as np
from build_atlas import key_image

ROOT=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(ident, source, response):
    source=source.resolve(); response=response.resolve()
    if not source.is_relative_to(ROOT) or not response.is_relative_to(ROOT):
        raise ValueError('Project-local source and actual tool response required')
    proof=json.loads(response.read_text(encoding='utf-8'))
    if proof.get('tool')!='image_gen.imagegen' or not proof.get('result'):
        raise ValueError('Actual ImageGen metadata missing')
    out=ROOT/'qa/stage1_enemies_20260913'/ident/sha(source)[:12]
    out.mkdir(parents=True,exist_ok=True)
    raw=Image.open(source)
    rgba=key_image(source)
    yy,xx=np.where(rgba[:,:,3]>30)
    box=[max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(raw.width,int(xx.max())+13),min(raw.height,int(yy.max())+13)]
    cut=Image.fromarray(rgba).crop(box)
    target=out/'candidate_rgba.png'; cut.save(target)
    # A 1:1 native crop on each matte is deliberately separate from fit previews.
    for label,native in [('native',True),('full',False)]:
        board=Image.new('RGB',(1920,1080),'#15232b')
        for ox,color in [(0,'#eeeeee'),(960,'#15232b')]:
            panel=Image.new('RGBA',(960,1080),color)
            im=cut.copy()
            if native:
                left=max(0,(im.width-940)//2); top=max(0,(im.height-1040)//2)
                im=im.crop((left,top,min(im.width,left+940),min(im.height,top+1040)))
            else: im.thumbnail((930,1030),Image.Resampling.LANCZOS)
            panel.alpha_composite(im,((960-im.width)//2,(1080-im.height)//2))
            board.paste(panel.convert('RGB'),(ox,0))
        ImageDraw.Draw(board).text((16,16),ident+' / '+('1:1 ORIGINAL PIXEL CROP' if native else 'FULL SUBJECT FIT'),fill='#e5974d')
        board.save(out/f'{label}_1920x1080.png')
    report={'id':ident,'status':'CANDIDATE_NOT_REVIEWED','source':str(source.relative_to(ROOT)),
            'sourceSHA256':sha(source),'toolResponse':{'path':str(response.relative_to(ROOT)),'sha256':sha(response)},
            'sourceNative':[raw.width,raw.height],'box':box,'candidate':str(target.relative_to(ROOT)),
            'candidateSHA256':sha(target),'candidateNative':list(cut.size),'native_review':[1920,1080],
            'operation':'existing key_image chroma/alpha separation then native crop only',
            'resampling':False,'anatomicalWarp':False,'runtimePromotion':False}
    (out/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--tool-response',type=Path,required=True)
    a=p.parse_args();prepare(a.id,a.source,a.tool_response)

```

## FILE: motion_lab_v1/public/combat-aim.js
SHA256: 054597f908218d99e823045dda8ebcb3d67adedee7b93da585a86ed31a6cb707

```text
import {direction,wrap} from './simulation.js';

// Resolve cursor, authored facing and muzzle together before emitting a shot.
// The firing path must never compute a different angle behind the renderer.
export function aimAtTarget(position,target,fallback=0){
  const dx=target[0]-position[0],dy=target[1]-position[1];
  return Math.hypot(dx,dy)<1e-6?fallback:Math.atan2(dy,dx);
}

export function resolvePointerAim(actor,target,muzzleForDirection){
  const root=[actor.x,actor.y],fallback=aimAtTarget(root,target,actor.aim);
  const records=Array.from({length:8},(_,facing)=>{
    const muzzle=muzzleForDirection(facing),aim=aimAtTarget(muzzle,target,fallback);
    return {direction:facing,muzzle,aim,error:Math.abs(wrap(aim-facing*Math.PI/4))};
  });
  // Inside the illustrated weapon reach there may be no forward ray toward
  // the cursor. Keep a forward body/shot cone instead of shooting backwards.
  const reach=Math.max(...records.map(r=>Math.hypot(r.muzzle[0]-actor.x,r.muzzle[1]-actor.y)));
  if(Math.hypot(target[0]-actor.x,target[1]-actor.y)>reach+.05){
    const current=records[actor.direction];
    if(current.error<=Math.PI/8+.035)return {...current,converges:true};
    // Discrete authored muzzles can leave a gap between adjacent half-octant
    // cones. Pick the closest forward-facing view, at most one octant away,
    // rather than missing a reachable cursor or iterating between two views.
    const candidates=records.filter(r=>r.error<=Math.PI/4).sort((a,b)=>a.error-b.error);
    if(candidates.length)return {...candidates[0],converges:true};
  }
  return {aim:fallback,direction:direction(fallback),converges:false};
}

// Commit the latest sample synchronously, not through the locomotion clock or
// weapon cooldown. Reuse this before emission and presentation as the camera,
// authored frame and recoil can move the illustrated muzzle in between inputs.
export function applyPointerAim(actor,target,muzzleForDirection){
  const solution=resolvePointerAim(actor,target,muzzleForDirection);
  actor.aim=solution.aim;actor.direction=solution.direction;
  return solution;
}

export function createPlayerProjectile(actor,origin){
  const [x,y,z]=origin,aim=actor.aim;
  return {x,y,z,vx:Math.cos(aim)*17,vy:Math.sin(aim)*17,life:1.15,enemy:false};
}

```

## FILE: motion_lab_v1/public/atlas-renderer.js
SHA256: fef4991277a4f85fa30b2e8db8b98d1803e607593fb3c7e96d33e7705637a3e8

```text
import {DIRECTIONS,clamp} from './simulation.js';

// A source cycle may use a non-uniform amount of travelled distance per
// keyframe.  In particular, a natural walk lingers on each planted contact
// and crosses the two unweighted transition frames more quickly.  This stays
// distance-driven: frame timing never depends on wall-clock time or firing.
export function phaseIndex(phase,frames,phaseStarts=null){
  const count=Math.max(1,Math.trunc(Number(frames)||1));
  // Avoid adding 1 before a positive boundary: 0.2 + 1 can round below the
  // authored 0.20 transition on a binary float, holding the prior keyframe.
  const raw=Number(phase)||0;
  const p=raw-Math.floor(raw);
  const valid=Array.isArray(phaseStarts)&&phaseStarts.length===count&&phaseStarts[0]===0&&
    phaseStarts.every((value,index)=>Number.isFinite(value)&&value>=0&&value<1&&(index===0||value>phaseStarts[index-1]));
  if(valid){
    for(let index=count-1;index>=0;index--)if(p>=phaseStarts[index])return index;
  }
  return Math.floor(p*count)%count;
}

// Review tools address a keyframe by its ordinal. Pick the middle of its
// authored interval so a non-uniform contact dwell cannot make “frame 2”
// preview frame 1.
export function phaseForFrame(frame,frames,phaseStarts=null){
  const count=Math.max(1,Math.trunc(Number(frames)||1));
  const index=((Math.trunc(Number(frame)||0)%count)+count)%count;
  const valid=Array.isArray(phaseStarts)&&phaseStarts.length===count&&phaseStarts[0]===0&&
    phaseStarts.every((value,position)=>Number.isFinite(value)&&value>=0&&value<1&&(position===0||value>phaseStarts[position-1]));
  const start=valid?phaseStarts[index]:index/count;
  const end=valid?(phaseStarts[index+1]??1):(index+1)/count;
  return start+(end-start)*.5;
}

// Only authored RGBA frames enter the live texture. Recoil is a continuous
// upper-body transform, applied to a dense quad without detaching any limb.
export class AtlasRenderer {
  constructor(canvas){
    this.canvas=canvas;this.models={};
    const options={alpha:true,antialias:true,premultipliedAlpha:false,preserveDrawingBuffer:true};
    const gl=this.gl=canvas.getContext('webgl2',options)||canvas.getContext('webgl',options);
    if(!gl)throw new Error('WebGL을 사용할 수 없습니다.');
    this.webgl2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;
    const shader=(kind,source)=>{const s=gl.createShader(kind);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const p=this.program=gl.createProgram();
    let vs='attribute vec2 a_position;attribute vec2 a_uv;uniform vec2 u_resolution;varying vec2 v_uv;void main(){gl_Position=vec4(a_position/u_resolution*vec2(2.,-2.)+vec2(-1.,1.),0.,1.);v_uv=a_uv;}';
    let fs='precision highp float;uniform sampler2D u_image;uniform float u_alpha;varying vec2 v_uv;void main(){vec4 c=texture2D(u_image,v_uv);gl_FragColor=vec4(c.rgb,c.a*u_alpha);}';
    if(this.webgl2){vs='#version 300 es\n'+vs.replaceAll('attribute ','in ').replace('varying ','out ');fs='#version 300 es\n'+fs.replace('varying ','in ').replace('void main()','out vec4 fragColor;void main()').replace('texture2D(','texture(').replace('gl_FragColor','fragColor');}
    gl.attachShader(p,shader(gl.VERTEX_SHADER,vs));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fs));
    gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));
    this.aPosition=gl.getAttribLocation(p,'a_position');this.aUv=gl.getAttribLocation(p,'a_uv');
    this.uResolution=gl.getUniformLocation(p,'u_resolution');this.uAlpha=gl.getUniformLocation(p,'u_alpha');
    this.positionBuffer=gl.createBuffer();this.uvBuffer=gl.createBuffer();
  }
  async load(profile,fireBundle=null){
    this.profile=profile;this.fireModels={};this.fullBodyModels={};
    // A modern recipe owns ALL states. A leftover character-specific bundle
    // must not silently replace its approved full-body walk/idle artwork.
    if(profile.animation?.presentation==='authored_frames')fireBundle=null;
    const loadTexture=async(src)=>{
      const im=new Image();im.decoding='async';im.src=src;await im.decode();
      const gl=this.gl,texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      if(this.webgl2){gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);}
      return {texture,im};
    };
    await Promise.all(Object.entries(profile.views).map(async([name,view])=>{
      const clips={};
      for(const action of ['walk','run','idle']){if(!view[action])continue;
        const {texture,im}=await loadTexture(view[action].image);
        clips[action]={texture,im,clip:view[action]};
      }
      this.models[name]={...clips.walk,clips,view};
    }));
    // Current ASTER production uses one authored full-body raster for every
    // state.  This prevents the old upper/lower seam and keeps idle, walking,
    // and firing on the same identity/weapon silhouette.
    if(fireBundle?.runtime_eligible===true&&fireBundle.contracts?.single_full_body_texture_per_frame&&fireBundle.directions){
      const cell=Array.isArray(fireBundle.cell)?fireBundle.cell:[384,384];
      const artHeight=Number.isFinite(fireBundle.art_height)?fireBundle.art_height:340;
      const frameCounts=fireBundle.frames||{idle:4,move:24,fire:6};
      const frameRates=fireBundle.fps||{idle:4,move:24,fire:12};
      await Promise.all(Object.entries(fireBundle.directions).map(async([name,entry])=>{
        if(!entry?.idle||!entry.move||!entry.fire)return;
        const walkSource=entry.walk||entry.move,runSource=entry.run||walkSource;
        const [idle,move,fire,walk,run]=await Promise.all([
          loadTexture(entry.idle),loadTexture(entry.move),loadTexture(entry.fire),
          loadTexture(walkSource),loadTexture(runSource)
        ]);
        this.fullBodyModels[name]={idle,move,fire,walk,run,muzzle:entry.muzzle,root:entry.root||[192,350],cell,artHeight,
          frameCounts:{idle:frameCounts.idle||4,walk:frameCounts.walk||6,run:frameCounts.run||6,move:frameCounts.move||24,fire:frameCounts.fire||6},
          frameRates:{idle:frameRates.idle||4,walk:frameRates.walk||8,run:frameRates.run||12,move:frameRates.move||24,fire:frameRates.fire||12},muzzleFrame:fireBundle.muzzle_frame??2};
      }));
    }
    if(fireBundle?.candidate_status==='PASS'&&fireBundle.runtime_eligible===true&&fireBundle.directions){
      const cell=Array.isArray(fireBundle.cell)?fireBundle.cell:[384,384];
      const root=Array.isArray(fireBundle.root)?fireBundle.root:[192,350];
      const height=Number.isFinite(fireBundle.height)?fireBundle.height:340;
      await Promise.all(Object.entries(fireBundle.directions).map(async([name,entry])=>{
        if(!entry?.upper||!entry.idleLower||!entry.moveLower)return;
        const [upper,idleLower,moveLower]=await Promise.all([loadTexture(entry.upper),loadTexture(entry.idleLower),loadTexture(entry.moveLower)]);
        this.fireModels[name]={upper,idleLower,moveLower,muzzle:entry.muzzle,cell,root,height,frames:fireBundle.frames||6,frameRate:fireBundle.frameRate||12};
      }));
    }
  }
  hasFullBody(direction){return !!this.fullBodyModels?.[direction];}
  fullBodyFrame(direction,pose){
    const model=this.fullBodyModels?.[direction];if(!model)return null;
    const moving=(Number(pose.amount)||0)>.055;
    // Pure locomotion uses the authored six-frame walk cycle.  Held-fire
    // keeps the already-reviewed full-body moving-fire family, while run
    // uses the same coherent walk source at a distinct higher cadence and
    // the simulation's independently measured run speed/stride.
    let action=moving?(pose.firing?'move':(pose.run?'run':'walk')):(pose.firing?'fire':'idle');
    if(!model[action])action=moving?'move':(pose.firing?'fire':'idle');
    const frames=model.frameCounts[action]||1,rate=model.frameRates[action]||12;
    let index=0;
    if(['walk','run','move'].includes(action))index=Math.floor((((Number(pose.phase)||0)%1+1)%1)*frames)%frames;
    else if(action==='idle')index=Math.floor(Math.max(0,Number(pose.time)||0)*rate)%frames;
    else {
      const recoil=Number(pose.recoil)||0;
      if(recoil>.72)index=2;
      else if(recoil>.32)index=3;
      else if(recoil>.10)index=4;
      else if(pose.firing)index=Math.floor(Math.max(0,Number(pose.time)||0)*rate)%2;
      else index=5;
      index=Math.min(index,frames-1);
    }
    return {model,action,index,frameCount:frames,texture:model[action].texture,im:model[action].im,muzzle:model.muzzle,root:model.root,cell:model.cell,artHeight:model.artHeight};
  }
  projectFullBodyPoint(direction,pose,point,x,y,height=230){
    const record=this.fullBodyFrame(direction,pose);if(!record||!Array.isArray(point))return null;
    const scale=height/record.artHeight;
    return [x+(point[0]-record.root[0])*scale,y+(point[1]-record.root[1])*scale];
  }
  begin(width,height){
    this.width=width;this.height=height;const gl=this.gl;
    gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(this.program);gl.uniform2f(this.uResolution,width,height);
    gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  }
  frame(direction,pose){
    const model=this.models[direction];if(!model)return null;
    const action=pose.amount<.06&&model.clips.idle?'idle':pose.run&&model.clips.run?'run':'walk';
    const {clip,texture,im}=model.clips[action];
    const phase=pose.amount<.06?0:pose.phase;
    return {model,clip,texture,im,index:phaseIndex(phase,clip.frames,clip.phaseStarts)};
  }
  hasFire(direction){return !!this.fireModels?.[direction];}
  fireFrame(direction,pose){
    const model=this.fireModels?.[direction];if(!model)return null;
    const fireRecoil=Number(pose.recoil)||0;
    let upperIndex=0;
    if(fireRecoil>.72)upperIndex=2;
    else if(fireRecoil>.32)upperIndex=3;
    else if(fireRecoil>.10)upperIndex=4;
    else if(pose.firing)upperIndex=Math.floor(Math.max(0,pose.time||0)*model.frameRate)%2;
    else upperIndex=5;
    const moving=(Number(pose.amount)||0)>.055;
    const lower=model[moving?'moveLower':'idleLower'];
    const lowerFrames=moving?24:4;
    const lowerPhase=moving?pose.phase:(Math.max(0,pose.time||0)*.25);
    const lowerIndex=Math.floor(((lowerPhase%1+1)%1)*lowerFrames)%lowerFrames;
    return {model,upper:model.upper,lower,upperIndex,lowerIndex,muzzle:model.muzzle,root:model.root,height:model.height,cell:model.cell,frames:model.frames};
  }
  projectFirePoint(direction,pose,point,x,y,height=230){
    const model=this.fireModels?.[direction];if(!model||!Array.isArray(point))return null;
    const scale=height/model.height;
    return [x+(point[0]-model.root[0])*scale,y+(point[1]-model.root[1])*scale];
  }
  drawFireLayer(layer,frame,x,y,height,root,cell){
    const {texture,im}=layer,gl=this.gl,scale=height/340,[cw,ch]=cell;
    const x0=x-root[0]*scale,y0=y-root[1]*scale,x1=x+(cw-root[0])*scale,y1=y+(ch-root[1])*scale;
    const row=Math.max(0,Math.min(Math.floor(im.height/ch)-1,frame));
    const positions=[x0,y0,x1,y0,x0,y1,x0,y1,x1,y0,x1,y1];
    const v0=(row*ch)/im.height,v1=((row+1)*ch)/im.height;
    const uv=[0,v0,1,v0,0,v1,0,v1,1,v0,1,v1];
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,6);
  }
  drawFire(direction,pose,x,y,height=230){
    const record=this.fireFrame(direction,pose);if(!record)return null;
    // The V2 ImageGen upper is composited over the existing V6 lower in one
    // 384px source coordinate system. It keeps the authored shoulder, hand,
    // rifle and muzzle together; no raster rotation or procedural body bend.
    this.drawFireLayer(record.lower,record.lowerIndex,x,y,height,record.root,record.cell);
    this.drawFireLayer(record.upper,record.upperIndex,x,y,height,record.root,record.cell);
    const muzzle=this.projectFirePoint(direction,pose,record.muzzle,x,y,height);
    return {muzzle,frame:record.upperIndex,frameCount:record.frames,lowerFrame:record.lowerIndex,fire:true,root:[x,y],direction,record};
  }
  drawFullBodyLayer(record,x,y,height){
    const {texture,im}=record,gl=this.gl,scale=height/record.artHeight,[cw,ch]=record.cell;
    const x0=x-record.root[0]*scale,y0=y-record.root[1]*scale,x1=x+(cw-record.root[0])*scale,y1=y+(ch-record.root[1])*scale;
    const row=Math.max(0,Math.min(Math.floor(im.height/ch)-1,record.index));
    const positions=[x0,y0,x1,y0,x0,y1,x0,y1,x1,y0,x1,y1];
    const v0=(row*ch)/im.height,v1=((row+1)*ch)/im.height;
    const uv=[0,v0,1,v0,0,v1,0,v1,1,v0,1,v1];
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,6);
  }
  drawFullBody(direction,pose,x,y,height=230){
    const record=this.fullBodyFrame(direction,pose);if(!record)return null;
    this.drawFullBodyLayer(record,x,y,height);
    const muzzle=this.projectFullBodyPoint(direction,pose,record.muzzle,x,y,height);
    return {muzzle,frame:record.index,frameCount:record.frameCount,clip:{frames:record.frameCount,height:record.artHeight,root:record.root,cell:record.cell,sources:[]},root:[x,y],direction,fullBody:true,action:record.action,fire:!!pose.firing,record};
  }
  projectPoint(clip,pose,point,x,y,height){
    const scale=height/clip.height;
    const waist=clip.waistY||clip.root[1]-clip.height*.5;
    const w=clamp((waist+35-point[1])/65,0,1);
    const q=w*w*(3-2*w);
    const angle=(pose.recoil*.04+pose.reload*.05)*Math.cos(pose.facing);
    const px=point[0]-clip.root[0],py=point[1]-waist;
    const rx=Math.cos(angle)*px-Math.sin(angle)*py,ry=Math.sin(angle)*px+Math.cos(angle)*py;
    const breath=Math.sin(pose.time*2.5)*1.1*(1-pose.amount);
    return [x+(point[0]-clip.root[0]+(rx-px-pose.recoil*6*Math.cos(pose.facing))*q)*scale,
      y+(point[1]-clip.root[1]+(ry-py+pose.reload*6-breath)*q)*scale];
  }
  draw(direction,pose,x,y,height=230){
    if(this.hasFullBody(direction))return this.drawFullBody(direction,pose,x,y,height);
    if(pose.firing&&this.hasFire(direction))return this.drawFire(direction,pose,x,y,height);
    const record=this.frame(direction,pose);if(!record)return null;
    const {model,clip,index,texture,im}=record,gl=this.gl,[cw,ch]=clip.cell;
    const col=index%clip.columns,row=Math.floor(index/clip.columns),positions=[],uv=[];
    const cols=8,rows=40;
    const vertex=(i,j)=>{
      const point=[i/cols*cw,j/rows*ch];positions.push(...this.projectPoint(clip,pose,point,x,y,height));
      uv.push((col*cw+point[0])/im.width,(row*ch+point[1])/im.height);
    };
    for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){vertex(i,j);vertex(i+1,j);vertex(i,j+1);vertex(i+1,j);vertex(i+1,j+1);vertex(i,j+1);}
    gl.bindBuffer(gl.ARRAY_BUFFER,this.positionBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(positions),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aPosition);gl.vertexAttribPointer(this.aPosition,2,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,this.uvBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.aUv);gl.vertexAttribPointer(this.aUv,2,gl.FLOAT,false,0,0);
    gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1f(this.uAlpha,1);gl.drawArrays(gl.TRIANGLES,0,positions.length/2);
    const muzzle=model.view.muzzle||clip.muzzles[Math.floor(index/(clip.steps||1))];
    return {muzzle:this.projectPoint(clip,pose,muzzle,x,y,height),frame:index,frameCount:clip.frames,clip,root:[x,y],direction};
  }
}

```

## FILE: motion_lab_v1/tests/test_cycle_review.py
SHA256: c42791c15da9815213b123efdc74326ba7b8822cb352b6bca771e2804cb3149b

```text
"""Synthetic review fixtures only. They are never production art approvals."""
import copy
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import cycle_review as cycle
import gait_contract as contract
import intake_frame


class CycleGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cv2
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        cls.video_fixture=Path(tempfile.mkdtemp(prefix='cycle_video_',dir=base))/'synthetic_1080p.mp4'
        writer=cv2.VideoWriter(str(cls.video_fixture),cv2.VideoWriter_fourcc(*'mp4v'),30,(1920,1080))
        if not writer.isOpened():raise RuntimeError('Local cycle video encoder unavailable')
        try:
            for i in range(108):writer.write(np.full((1080,1920,3),i,dtype=np.uint8))
        finally:writer.release()

    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='cycle_',dir=base))
        for module in (w,intake_frame):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        reference=self.root/'art/fixture/identity.png';reference.parent.mkdir(parents=True);reference.write_bytes(b'identity fixture')
        c={'id':'fixture','name':'Fixture','source':'art/fixture','workflowVersion':1,
           'identityReference':'art/fixture/identity.png','referenceSHA256':w.sha(reference),
           'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
        w.write(self.root/'characters/fixture.json',c)
        reviews=[]
        proof=self.root/'qa/tool-fixture.json';w.write(proof,{'technicalFixture':True,'notActualToolResponse':True})
        for i,(slot,path) in enumerate(w.slots(c)):
            path.write_bytes(('non-art fixture '+str(i)).encode())
            w.write(path.with_suffix('.source.json'),{'generator':'Codex built-in ImageGen','sha256':w.sha(path),'toolResponse':w.binding(proof)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':w.sha(path),'referenceSHA256':c['referenceSHA256'],'evidence':w.binding(path)})
        w.write(self.root/'qa/fixture/source_reviews.json',reviews)
        self.expected=cycle.inputs('fixture','E')
        self.out=self.root/'qa/cycle';self.out.mkdir(parents=True)
        self.clip={'cell':[768,768],'height':656,'columns':3,'frames':6}
        atlas_path=self.out/'atlas.png';Image.new('RGBA',(2304,1536),(90,120,130,255)).save(atlas_path)
        contact=self.out/'contact.png';Image.new('RGB',(2304,1536)).save(contact)
        movie=self.out/'video.mp4';shutil.copy2(self.video_fixture,movie)
        self.preview=self.out/'preview.json'
        w.write(self.preview,{'cycleInputs':self.expected,'clip':self.clip,'atlas':w.binding(atlas_path),
                'contact':w.binding(contact),'video':w.binding(movie),'nativeVideo':[1920,1080],
                'cycles':3,'durationSeconds':3.6})
        soles=[([500,716],[220,690]),([390,716],[290,640]),([290,716],[450,650]),
               ([220,690],[500,716]),([290,640],[390,716]),([450,650],[290,716])]
        frames=[]
        for p,(left,right) in zip(contract.PHASES,soles):
            pts={}
            for side,sole,hx in [('left',left,375),('right',right,405)]:
                pts[side+'Hip']=[hx,360];pts[side+'Knee']=[(hx+sole[0])/2,(360+sole[1])/2];pts[side+'Sole']=sole
            frames.append({'index':p['index'],'phase':p['name'],'support':p['support'],'landmarks':pts})
        self.packet={'kind':'sable-cycle-observation','character':'fixture','direction':'E','action':'walk',
                     'inputs':self.expected,'preview':w.binding(self.preview),'decision':'approved','reviewer':'UNIT FIXTURE NOT ART REVIEW',
                     'legMarkers':{'left':'left technical marker','right':'right technical marker'},'frames':frames,
                     'observations':{name:{'decision':'pass','seconds':[.1,1.1], 'notes':'Synthetic geometry unit test only'} for name in cycle.OBSERVATIONS}}
        self.packet_path=self.out/'observations.json';w.write(self.packet_path,self.packet)

    def test_explicit_complete_technical_packet_is_accepted(self):
        self.assertTrue(cycle.validate_packet(self.packet,self.expected))

    def test_same_leading_leg_at_opposite_contact_is_rejected(self):
        p=copy.deepcopy(self.packet);p['frames'][3]['landmarks']=copy.deepcopy(p['frames'][0]['landmarks'])
        with self.assertRaisesRegex(ValueError,'Opposite contacts'):cycle.validate_packet(p,self.expected)

    def test_declared_video_dimensions_cannot_hide_undecodable_bytes(self):
        movie=self.out/'video.mp4';movie.write_bytes(b'not an actual video')
        preview=w.read(self.preview);preview['video']=w.binding(movie);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'actually decode'):cycle.validate_packet(self.packet,self.expected)

    def test_blank_approvals_wrong_phase_and_missing_video_binding_fail(self):
        for mutate in [lambda p:p.update(decision='unreviewed'),lambda p:p['frames'][1].update(phase='right_passing'),
                       lambda p:p['frames'][3].update(support='left'),lambda p:p['frames'][0]['landmarks'].update(leftSole=None),
                       lambda p:p['observations']['footSliding'].update(seconds=[]),lambda p:p['observations']['loopSeam'].update(notes=''),
                       lambda p:p.update(preview={'path':'missing.json','sha256':'0'*64})]:
            p=copy.deepcopy(self.packet);mutate(p)
            with self.assertRaises(ValueError):cycle.validate_packet(p,self.expected)

    def test_background_landmarks_are_rejected(self):
        atlas=np.zeros((1536,2304,4),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,'visible subject'):cycle.validate_landmarks(self.packet,self.clip,atlas)

    def test_changed_source_recipe_and_review_packet_invalidate_gate(self):
        cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(cycle.current('fixture','E')['state'],'approved')
        p=copy.deepcopy(self.packet);p['observations']['footSliding']['notes']='edited after approval'
        w.write(self.packet_path,p)
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')
        w.write(self.packet_path,self.packet)
        (self.root/'art/fixture/E_walk_3_master.png').write_bytes(b'replacement source')
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')

    def test_rejected_pixels_cannot_be_reapproved_by_notes(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Actual fixture rejection',reviewer='unit fixture')
        with self.assertRaisesRegex(ValueError,'source bytes are unchanged'):
            cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(w.read(self.root/'dist/fixture.delivery.json')['status'],'HOLD_VISUAL_REPAIR')

    def test_renaming_rejected_sources_does_not_clear_rejection(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic rejection fixture',reviewer='unit fixture')
        for i in range(6):
            path=self.root/f'art/fixture/E_walk_{i}_master.png'
            shutil.copy2(path,path.with_name(f'E_walk_{i}_override.png'))
        self.assertEqual(cycle.current('fixture','E')['state'],'repair')

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)


if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_character_workflow.py
SHA256: fb16dc988331ae45d4632b1f1648bda3987803ee9492bd3e705bd9070a8dac10

```text
"""Deterministic technical fixtures only; no generated game art or API calls."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import character_workflow as workflow
import package_standalone as packager
import new_character
import build_character
import cycle_review
from PIL import Image

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding='utf-8')

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='workflow_',dir=base))
        assert self.root.resolve().is_relative_to(base.resolve())
        # Preserve tiny test fixtures as evidence; never recursively clean user assets.
        self.patches=[patch.object(module,'ROOT',self.root) for module in [workflow,packager,new_character,build_character]]
        for p in self.patches:p.start();self.addCleanup(p.stop)
        self.art=self.root/'art/fixture';self.art.mkdir(parents=True)
        self.reference=self.art/'identity_reference.png';self.reference.write_bytes(b'technical-identity-fixture')
        self.config=json.loads((LAB/'characters/mica.json').read_text(encoding='utf-8-sig'))
        self.config.update(id='fixture',name='TECHNICAL FIXTURE',source='art/fixture',workflowVersion=1,identityReference='art/fixture/identity_reference.png',referenceSHA256=digest(self.reference),clips={'walk':{'frames':6},'idle':{'frames':1}},annotations={})
        save(self.root/'characters/fixture.json',self.config)
    def populate_sources(self):
        reviews=[]
        for index,(slot,path) in enumerate(workflow.slots(self.config)):
            path.write_bytes(('non-art fixture '+str(index)).encode())
            proof=self.art/f'proof_{index}.json';save(proof,{'testFixture':True})
            save(path.with_suffix('.source.json'),{'generator':'Codex built-in ImageGen','sha256':digest(path),'toolResponse':workflow.binding(proof)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':digest(path),'referenceSHA256':self.config['referenceSHA256'],'evidence':workflow.binding(path)})
        save(self.root/'qa/fixture/source_reviews.json',reviews)
        return list(workflow.slots(self.config))
    def browser_report(self):
        test_script=self.root/'public/qa/combat-checks.js';test_script.parent.mkdir(parents=True);test_script.write_text('fixture')
        rows=[{'name':f'{mode}_{d}','direction':d,'spriteDirection':d,'pass':True,'heldMouse':True,'shotCount':2,'observedShots':2,'travel':.2,'maxFacingErrorDegrees':0,'convergedShots':2,'maxCursorError':0} for mode in ['mouse','keyboard'] for d in workflow.DIRECTIONS]
        rows.append(dict(rows[0],name='repeat_preserves_mouse'))
        rapid=[dict(name=f'{mode}_{d}',pass_=True,heldMouse=True,locomotionUnchanged=True,oldProjectileVelocityUnchanged=True,immediateErrorDegrees=0,firstFrameErrorDegrees=0,shotErrorDegrees=0,immediateMs=.1,firstFrameMs=16,shotWaitSeconds=.1,eligibleBudgetSeconds=.1,shotCount=1) for mode in ['stationary','moving'] for d in workflow.DIRECTIONS]
        for r in rapid:
            r['pass']=r.pop('pass_');r['travel']=.2 if r['name'].startswith('moving_') else 0
        return {'kind':'motion-studio-combat-browser','character':'fixture','build':{'inputSHA256':'current'},'testScriptSHA256':digest(test_script),'pass':True,'results':rows,'rapidAim':rapid,'externalResources':[],'viewport':[1920,1080]}
    def test_missing_source_returns_concrete_pilot(self):
        report=workflow.source_status('fixture')
        self.assertFalse(report['ready']);self.assertEqual(report['next']['slot'],'E/idle/0')
    def test_static_walk_cannot_replace_the_required_motion(self):
        self.config['clips']['walk']['frames']=1;save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.source_status('fixture')
    def test_scaffold_requests_exact_character_slots_without_generation(self):
        save(self.root/'characters/mica.json',self.config)
        for name,run,count in [('newwalk',False,56),('newrun',True,104)]:
            new_character.scaffold(name,name.upper(),self.reference,run)
            recipe=json.loads((self.root/'characters'/f'{name}.json').read_text())
            requests=json.loads((self.root/'art'/name/'requests.json').read_text())
            self.assertEqual(recipe['id'],name);self.assertEqual(recipe['annotations'],{})
            self.assertEqual(recipe['referenceSHA256'],digest(self.reference));self.assertEqual(len(requests),count)
            self.assertTrue(all(r['state']=='NEEDS_IMAGEGEN' and r['destination'].startswith('art/'+name+'/') for r in requests))
            self.assertEqual(recipe['clips']['walk']['phaseStarts'],[0,.2,.33,.5,.7,.83])
    def test_exact_reviewed_inputs_are_ready(self):
        self.populate_sources();self.assertTrue(workflow.source_status('fixture')['ready'])
    def test_complete_sources_do_not_bypass_whole_cycle_gate(self):
        self.populate_sources();state=workflow.workflow_status('fixture')
        self.assertTrue(state['sourcesReady']);self.assertFalse(state['ready'])
        self.assertEqual(state['next']['kind'],'cycle-review')
        self.assertEqual(state['next']['direction'],'E')
        with self.assertRaisesRegex(ValueError,'Whole-cycle'):
            build_character.compile_character(self.root/'characters/fixture.json')
    def test_alternate_recipe_cannot_bypass_active_build_gate(self):
        self.populate_sources()
        alternative=copy.deepcopy(self.config);alternative.pop('workflowVersion')
        path=self.root/'qa/alternate.json';save(path,alternative)
        with self.assertRaisesRegex(ValueError,'canonical reviewed'):
            build_character.compile_character(path)
    def test_replacing_source_invalidates_previous_review(self):
        slots=self.populate_sources();slots[0][1].write_bytes(b'changed source')
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertEqual(report['slots'][0]['state'],'stale_provenance')
    def test_pilot_source_review_precedes_cycle_approval(self):
        self.populate_sources()
        path=self.root/'qa/fixture/source_reviews.json'
        save(path,[r for r in workflow.read(path) if r['slot']!='E/walk/5'])
        state=workflow.workflow_status('fixture')
        self.assertFalse(state['ready'])
        self.assertEqual(state['next']['slot'],'E/walk/5')
    def test_reference_change_invalidates_readiness(self):
        self.populate_sources();self.reference.write_bytes(b'changed identity')
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_duplicate_source_cannot_pass_as_a_distinct_phase(self):
        slots=self.populate_sources();slots[1][1].write_bytes(slots[0][1].read_bytes())
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertIn('same source',report['errors'][0])
    def test_rejected_source_is_retained_and_blocks_build(self):
        slots=self.populate_sources();slot,path=slots[0]
        workflow.review_source('fixture',slot,'repair',str(path),'Fixture rejection, not a real visual review','unit-test')
        self.assertFalse(workflow.source_status('fixture')['ready'])
        self.assertTrue((self.root/'qa/fixture/quarantine'/digest(path)/path.name).exists());self.assertTrue(path.exists())
    def test_changed_tool_response_invalidates_provenance(self):
        self.populate_sources();save(self.art/'proof_0.json',{'changed':True})
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_path_escape_and_identity_mismatch_fail(self):
        for value in ['../other','foo/bar','C:\\outside']:
            with self.assertRaises(ValueError):workflow.ident(value)
        self.config['source']='../outside';save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.recipe('fixture')
    def test_browser_receipt_checks_rows_not_only_pass_label(self):
        report=self.browser_report();path=self.root/'qa/browser.json';save(path,report)
        workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
        for mutate in [lambda r:r['results'].pop(),lambda r:r['results'][0].update(spriteDirection='W'),lambda r:r['results'][0].update(heldMouse=False),lambda r:r['results'][0].update(observedShots=0),lambda r:r['results'][0].update(convergedShots=0),lambda r:r['results'][0].update(maxCursorError=1),lambda r:r['results'][0].update(maxFacingErrorDegrees=150),lambda r:r['build'].update(inputSHA256='old'),lambda r:r.update(viewport=[1280,720]),lambda r:r.update(externalResources=['https://example.invalid/image.png'])]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_bundle_changes_cannot_reuse_a_previous_receipt(self):
        path=self.root/'dist/FIXTURE_Motion_Studio.html';path.parent.mkdir();path.write_text('<html>fixture</html>')
        inputs={'runtime':'abc'};report={'character':'fixture','path':path.relative_to(self.root).as_posix(),'inputs':inputs,'inputSHA256':hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest(),'sha256':digest(path),'bytes':path.stat().st_size}
        save(self.root/'dist/fixture.package.json',report)
        with patch.object(packager,'bundle_inputs',return_value=inputs):
            workflow.check_package('fixture');path.write_text('changed')
            with self.assertRaises(ValueError):workflow.check_package('fixture')
    def test_rapid_aim_gate_rejects_eventual_pass_stale_input_and_homing(self):
        report=self.browser_report();path=self.root/'qa/rapid.json'
        for mutate in [lambda r:r.pop('rapidAim'),lambda r:r['rapidAim'].pop(),lambda r:r['rapidAim'][0].update(immediateErrorDegrees=180),lambda r:r['rapidAim'][0].update(firstFrameErrorDegrees=12),lambda r:r['rapidAim'][0].update(shotWaitSeconds=.5),lambda r:r['rapidAim'][0].update(immediateMs=float('nan')),lambda r:r['rapidAim'][0].update(oldProjectileVelocityUnchanged=False),lambda r:r['rapidAim'][0].update(locomotionUnchanged=False)]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_new_recipe_never_overwrites_an_existing_art_folder(self):
        (self.root/'characters/fixture.json').unlink() # owned technical fixture only
        with self.assertRaises(FileExistsError):new_character.scaffold('fixture','Fixture',self.reference)
        self.assertTrue(self.reference.exists())
    def test_incomplete_direction_set_cannot_be_packaged(self):
        save(self.root/'public/assets/atlas/fixture/profile.json',{'id':'fixture','views':{'E':{}},'missingDirections':[]})
        with self.assertRaises(ValueError):packager.bundle_inputs('fixture')
    def fake_build(self,config,direction,action,paths,annotations,output_root=None):
        out=output_root/'public/assets/atlas/fixture';out.mkdir(parents=True,exist_ok=True)
        path=out/f'{direction}_{action}.webp';Image.new('RGBA',(80,120),(30,80,150,255)).save(path,lossless=True)
        return {'image':f'assets/atlas/fixture/{path.name}','cell':[80,120],'frames':1,'columns':1,'height':100,'root':[40,115],'muzzles':[[60,40]],'sources':[{'source':paths[0].relative_to(self.root).as_posix()}]}
    def test_single_frame_imports_produce_their_own_portrait(self):
        self.populate_sources()
        with patch.object(build_character,'build',side_effect=self.fake_build),patch.object(cycle_review,'require_build'):
            build_character.compile_character(self.root/'characters/fixture.json')
        portrait=self.root/'public/assets/atlas/fixture/portrait.png';self.assertTrue(portrait.exists())
        self.assertEqual(Image.open(portrait).getpixel((20,20)),(30,80,150,255))
    def test_failed_and_partial_builds_preserve_the_existing_character(self):
        self.populate_sources();marker=self.root/'public/assets/atlas/fixture/existing.txt';marker.parent.mkdir(parents=True);marker.write_text('keep')
        calls=0
        def fail_late(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==4:raise ValueError('injected late source failure')
            return self.fake_build(*args,**kwargs)
        with patch.object(build_character,'build',side_effect=fail_late),patch.object(cycle_review,'require_build'):
            with self.assertRaises(ValueError):build_character.compile_character(self.root/'characters/fixture.json')
        self.assertEqual(marker.read_text(),'keep')
        with patch.object(build_character,'build',side_effect=self.fake_build):
            build_character.compile_character(self.root/'characters/fixture.json',partial=True)
        self.assertEqual(marker.read_text(),'keep')

if __name__=='__main__':unittest.main()

```

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: dc1e0f95238045ce0752719450928a23d601ca25589d763511c26b79f717b257

```text
extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")

var actor: EnemyActor
var state := "REPOSITION"
var state_left := 0.7
var state_duration := 0.7
var locked_aim := Vector2.LEFT
var locked_ground := Vector2.LEFT
var burst_left := 0
var burst_clock := 0.0
var phase := 1
var attack_serial := 0
var shots_fired := 0
var lunges := 0
var _struck: Array[int] = []
var _age := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_index = 1

func _enter(next_state: String, duration: float) -> void:
    state = next_state
    state_left = duration
    state_duration = maxf(duration, 0.001)

func interrupt() -> void:
    burst_left = 0
    _struck.clear()
    _enter("RECOVER", 0.55)

func step(target: OperatorActor, delta: float) -> void:
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    var aim := (target.get_combat_aim_point() - actor.get_combat_aim_point()).normalized()
    var boss := "BOSS" in actor.enemy_id
    var rifle := "RIFLE" in actor.enemy_id
    var shield := "SHIELD" in actor.enemy_id
    var drone := "DRONE" in actor.enemy_id
    var melee := "ABERRANT" in actor.enemy_id
    phase = 1 if actor.health > actor.max_health * 0.66 else (2 if actor.health > actor.max_health * 0.33 else 3)
    actor.velocity = Vector2.ZERO
    actor._aim_dir = locked_aim if state in ["WINDUP", "BURST", "LUNGE"] else aim
    if state == "REPOSITION":
        if drone:
            var tangent := toward.orthogonal() * actor._orbit_sign
            actor.velocity = (tangent * 0.72 + toward * clampf((dist - 280.0) / 160.0, -0.7, 0.7)).limit_length(1.0) * 118.0
        elif melee:
            actor.velocity = toward * 112.0 if dist > 85.0 else Vector2.ZERO
        elif shield:
            actor.velocity = toward * 62.0 if dist > 190.0 else Vector2.ZERO
        elif rifle:
            var radial := 1.0 if dist > 360.0 else (-0.7 if dist < 220.0 else 0.0)
            actor.velocity = (toward * radial + toward.orthogonal() * actor._orbit_sign * 0.38).limit_length(1.0) * 86.0
        if state_left <= 0.0 and (not melee or dist < 250.0):
            locked_aim = aim
            locked_ground = toward
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.95 if boss else (0.7 if shield else (0.6 if melee else 0.48)))
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", 0.42)
            elif boss:
                _boss_attack(target)
                _enter("RECOVER", (1.8 - float(phase) * 0.20) * actor.run_attack_interval_multiplier)
            else:
                burst_left = 3 if rifle else 1
                burst_clock = 0.0
                _enter("BURST", 0.5)
    elif state == "BURST":
        burst_clock -= delta
        if burst_left > 0 and burst_clock <= 0.0:
            _fire(locked_aim)
            burst_left -= 1
            burst_clock += 0.14
        if burst_left <= 0:
            _enter("RECOVER", (1.4 if shield else 0.85) * actor.run_attack_interval_multiplier)
    elif state == "LUNGE":
        actor.velocity = locked_ground * 360.0
        for victim in get_tree().get_nodes_in_group("operators"):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if actor.global_position.distance_to(victim.global_position) < 58.0:
                victim.apply_damage(18.0 * actor.run_damage_multiplier)
                _struck.append(victim.get_instance_id())
        if state_left <= 0.0:
            actor.velocity = Vector2.ZERO
            _enter("RECOVER", 1.1 * actor.run_attack_interval_multiplier)
    elif state == "RECOVER":
        if drone:
            actor.velocity = toward.orthogonal() * actor._orbit_sign * 62.0
        if state_left <= 0.0:
            _enter("REPOSITION", 0.9 if not boss else 0.45)
    queue_redraw()

func _fire(direction: Vector2) -> void:
    shots_fired += 1
    CombatFeedback.play_fire(get_tree(), actor.art_profile)
    actor._spawn_projectile(direction)

func _boss_attack(target: OperatorActor) -> void:
    # Slow readable fan in phase one; frozen impact zones in two; cross lanes
    # in three. Large gaps are intentional. These are damaging, not fake decals.
    if phase >= 2 and attack_serial % 2 == 0:
        _warning("circle", target.global_position, Vector2.RIGHT)
        if phase == 3:
            var origin := actor.global_position
            for i in range(4):
                var ray := locked_ground.rotated(float(i) * PI * 0.5)
                _warning("lane", origin + ray * 100.0, ray)
    else:
        var count := 3 if phase == 1 else 5
        for i in range(count):
            _fire(locked_aim.rotated((float(i) - float(count - 1) * 0.5) * 0.22))

func _warning(kind: String, location: Vector2, direction: Vector2) -> void:
    var warning := Warning.new()
    warning.source = actor
    warning.kind = kind
    warning.position = location
    warning.ray = direction
    warning.windup = 1.15 if kind == "circle" else 1.35
    warning.damage = 20.0
    actor.get_parent().add_child(warning)

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if "ABERRANT" in actor.enemy_id:
        var side := locked_ground.orthogonal() * 13.0
        var tip := locked_ground * 165.0
        draw_colored_polygon(PackedVector2Array([-side, side, tip + side, tip - side]), Color(color, 0.12))
        draw_line(Vector2.ZERO, tip, color, 1.8)
    else:
        var origin := actor.get_combat_aim_point() - actor.global_position
        draw_line(origin + locked_aim * 40.0, origin + locked_aim * 340.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "telegraph_before_damage": true, "melee_projectiles": false}

```

## FILE: scripts/combat/site7_attack_warning.gd
SHA256: e7991fdc15bb9ca2365934119c6ebd63bec55f90c92f0f939ca5571341d6d737

```text
extends Node2D
## A floor warning and its damage share the same frozen geometry and clock.
## No invisible homing: moving out of the marked region always evades the hit.

var source: EnemyActor
var kind := "circle"
var radius := 58.0
var ray := Vector2.RIGHT
var reach := 430.0
var half_width := 16.0
var windup := 1.05
var damage := 16.0
var elapsed := 0.0
var fired := false

func _ready() -> void:
    z_index = -2
    add_to_group("site7_attack_warnings")

func _physics_process(delta: float) -> void:
    if not is_instance_valid(source) or source.health <= 0.0:
        queue_free()
        return
    elapsed += delta
    if elapsed >= windup and not fired:
        fired = true
        for actor in get_tree().get_nodes_in_group("operators"):
            if actor is OperatorActor and not actor.is_downed() and contains(actor.global_position):
                actor.apply_damage(damage * source.run_damage_multiplier)
    if elapsed > windup + 0.26:
        queue_free()
    queue_redraw()

func contains(point: Vector2) -> bool:
    var offset := point - global_position
    if kind == "circle":
        return offset.length() <= radius
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= reach and absf(offset.dot(ray.orthogonal())) <= half_width

func _draw() -> void:
    var progress := clampf(elapsed / windup, 0.0, 1.0)
    var color := Color("f48caa")
    if fired:
        color = Color("eee2ff")
    var fill := Color(color, 0.12 if not fired else 0.36)
    if kind == "circle":
        draw_circle(Vector2.ZERO, radius, fill)
        draw_arc(Vector2.ZERO, radius, 0.0, TAU, 64, Color(color, 0.75), 1.8)
        draw_arc(Vector2.ZERO, radius - 5.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 64, color, 2.4)
        draw_line(Vector2(-7,0), Vector2(7,0), color, 1.3)
        draw_line(Vector2(0,-7), Vector2(0,7), color, 1.3)
    else:
        var side := ray.orthogonal() * half_width
        draw_colored_polygon(PackedVector2Array([-side, side, ray * reach + side, ray * reach - side]), fill)
        draw_line(-side, ray * reach - side, Color(color, 0.8), 1.5)
        draw_line(side, ray * reach + side, Color(color, 0.8), 1.5)
        draw_line(Vector2.ZERO, ray * reach * progress, color, 2.2 if not fired else 6.0)

```

## FILE: qa/stage1_implementation_20260913/full_operation.json
SHA256: 04a9c1682d0d4b16decbb816361a88d24322701067995a939ed86d5cdcdbf67b

```text
{
  "drive": "test bot -> real actor physics / weapon cooldown / projectile collisions / mission interactions",
  "failures": [],
  "result": {
    "active_run_boosts": [],
    "cargo_before_resolution": {
      "common_research": 135,
      "fragments": 1,
      "intel": {
        "ABERRANT": 1,
        "ANCHOR": 1,
        "SECURITY": 3
      },
      "salvage": 2,
      "unsecured_research": 85
    },
    "carrier_fragment": true,
    "carrier_fragment_secured": true,
    "chapter_id": "CH01",
    "early_extraction": false,
    "elapsed_seconds": 32.0499999999995,
    "extraction_depth": 6,
    "extraction_room": "",
    "field_supplies": true,
    "full_route_cleared": true,
    "hostiles_defeated": 10,
    "ledger_recovered": true,
    "ledger_retained_on_wipe": false,
    "lost_intel_samples": 0,
    "lost_unsecured": 0,
    "mission_id": "MIS_CH01_01",
    "outcome": "EXTRACTED",
    "research_multiplier": 1.0,
    "run_contract": {},
    "run_fragment_reward_multiplier": 1.0,
    "run_id": "STAGE1-TECHNICAL-PLAYTHROUGH",
    "run_only_boosts_expire_on_return": true,
    "run_research_reward_multiplier": 1.0,
    "run_salvage_reward_multiplier": 1.0,
    "secured_fragments": 1,
    "secured_intel": {
      "ABERRANT": 1,
      "ANCHOR": 1,
      "SECURITY": 3
    },
    "secured_research": 220,
    "secured_rewards": 220,
    "secured_salvage": 2,
    "transaction_id": "STAGE1-TECHNICAL-PLAYTHROUGH",
    "wipe_policy": "50% COMMON RESEARCH/SALVAGE RETAINED; HIGH-VALUE RESEARCH + SIGNAL FRAGMENTS + INTEL SAMPLES LOST; RUN-ONLY BOOSTS EXPIRE; STORY LEDGER RETAINED"
  },
  "status": "PASS_TECHNICAL_PLAYTHROUGH",
  "trace": [
    {
      "ammo": 24,
      "health": [
        96.0,
        138.0,
        112.0
      ],
      "position": [
        410.0,
        390.0
      ],
      "remaining": 0,
      "step": 0,
      "tick": 0,
      "wave": 0
    },
    {
      "ammo": 24,
      "health": [
        96.0,
        138.0,
        112.0
      ],
      "position": [
        321.285400390625,
        444.593658447266
      ],
      "remaining": 0,
      "step": 1,
      "tick": 32,
      "wave": 0
    },
    {
      "ammo": 8,
      "health": [
        89.0,
        138.0,
        112.0
      ],
      "position": [
        687.109436035156,
        472.490966796875
      ],
      "remaining": 0,
      "step": 2,
      "tick": 493,
      "wave": 1
    },
    {
      "ammo": 8,
      "health": [
        73.0,
        138.0,
        112.0
      ],
      "position": [
        1057.43212890625,
        681.029174804688
      ],
      "remaining": 0,
      "step": 2,
      "tick": 600,
      "wave": 1
    },
    {
      "ammo": 24,
      "health": [
        96.0,
        138.0,
        112.0
      ],
      "position": [
        1084.61962890625,
        559.022338867188
      ],
      "remaining": 0,
      "step": 3,
      "tick": 634,
      "wave": 1
    },
    {
      "ammo": 19,
      "health": [
        72.0,
        138.0,
        112.0
      ],
      "position": [
        1538.64123535156,
        237.280288696289
      ],
      "remaining": 0,
      "step": 4,
      "tick": 1082,
      "wave": 1
    },
    {
      "ammo": 0,
      "health": [
        72.0,
        130.0,
        112.0
      ],
      "position": [
        1895.97973632813,
        331.018432617188
      ],
      "remaining": 1,
      "step": 4,
      "tick": 1200,
      "wave": 0
    },
    {
      "ammo": 1,
      "health": [
        0.0,
        0.0,
        64.0
      ],
      "position": [
        1922.08703613281,
        684.709228515625
      ],
      "remaining": 0,
      "step": 5,
      "tick": 1800,
      "wave": 0
    }
  ],
  "visual_approval": false
}
```
