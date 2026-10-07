# Round 4 — only the two residual R3 counterexamples

This is the same user-authorized SABLE harness/skill review, not a request to
approve unseen art or all Stage 1 delivery. Please test only these two residuals
against the attached exact current code; report concrete remaining failures or
that these two examples are blocked. Korean answer requested.

1. R3 ghost-superposition: phase-difference ROIs now require absolute expected
pixel agreement (mean <=12, no more than 10% pixels above channel error48), in
addition to relative phase separation and full-panel checks. New FFV1 regression
uses the average of all six frames plus a 4-level current-phase patch. Correct
six-phase output passes; the ghost fails. The actual rifle VP8 candidate passes
all 107 decoded frames with these thresholds. This proves byte/chronology
consistency only, not human gait quality.

2. R3 quoted longer path: tokenize complete single/double/backtick quoted spans,
match a whole quoted path, and never scan inside unmatched quoted spans as an
unquoted path. Unquoted paths must terminate the line (or actual tool boilerplate
'by default.'). Tests reject result.png other.png and result.png. other.png in
all three quoting styles; accept real space-containing paths and the actual
tool-result format. This is retained-source consistency, not provider attestation.

Executed after both changes: all 94 Python tests passed in 90.085s; dedicated
provenance9 and cycle17 passed. Earlier valid browser ROOK reports exposed a
validator-only XY/XYZ assumption: actual muzzle is XYZ while target is XY. The
validator and fixtures now require finite XYZ and the actual weapon height; the
actual 33 combat and 40 locomotion report rows passed. No character art, accepted
gait, weapon cadence or packaged runtime JS was changed by this validator fix.

Other work has continued locally, not submitted as approval: a source-preserving
1x canvas avoids an actual embedded-video decoder crash and records frame times,
visibility and viewport. This trace is NOT yet enforced as an approval input.
Enemy actual projectile creation is separately traced, including caller/attack/
ordinal; a dedicated Godot test passed339 and a real operation reached extraction
with10 defeats,6 rooms,both optionals,2 operators alive (4/46/0 boss-exit HP).
Those were prior to the separately pending authored-emitter aim correction in
the tactics snapshot; new Godot checks for that are still to be run.

Still open: art observation and anatomical annotation improvements; atomic
renderer load/scoped MICA compatibility; four-limb motion contract; remaining
enemy gait sources and Stage1 raster promotion. No Luna generation run claimed.
Please do not expand this bounded review into another whole-framework redesign.

## FILE: .agents/skills/sable-character-studio/SKILL.md
SHA256: 5e4887812b7e9c62110e766c049790b55e15ee779ada157de335ccda598c1929

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

- This six-phase authoring contract is **bipedal**, not a universal monster
  contract. Drones and anchored machines need their actual hover/root/emitter
  evidence; quadrupeds need four named limb chains and their own contact cycle.
  Do not invent foot observations or drop workflowVersion to make them pass.

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
- A saved response plus a source hash is provenance consistency, not provider
  attestation. Bind the actual returned master immediately, retain it, and
  compare allowed derivatives to its pixels. A report's preservation boolean
  cannot replace that comparison. Unverified provenance blocks source approval.
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

## External review applied, not universal approval

The user-requested GPT 6 Pro review on 2026-09-13 found concrete provenance,
derivative, cycle-video, aim-report and NPC-warning gaps. Track its actual reply
and remaining work in `qa/stage1_implementation_20260913/`. It did not run the
project, view the art, or approve delivery. READY_TO_RESUME is permission to
resume the named pending step; technical PASS and reviewed delivery are separate.

```

## FILE: .agents/skills/sable-character-studio/references/authoring.md
SHA256: b7f56884153bc604a23bbd7e605a5aceed9a6926ffe58fbbf12136cd7d55824f

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
   {"tool":"image_gen.imagegen","returnedPath":"actual returned absolute file path","result":{"output_hint":"actual untouched returned metadata"},"projectCopy":"art/ID/retained-original.png","projectCopySHA256":"actual verified copied bytes SHA256"}
   ```

   Replace the example contents with the real response. Import with:

   ```powershell
   & 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' intake_frame.py --character ID --direction E --action idle --frame 0 --generated 'actual output.png' --tool-response 'qa/ID/actual-tool-response.json'
   ```

   The selected PNG must be native high resolution. Existing active overrides
   are replaced in their actual slot, not shadowed by an unused master. Prior
   files and provenance are retained. Verify the project copy/hash before any
   separately authorized managed-staging cleanup.

   Preserve the actual response and the returned master hash at intake, not a
   later invented tool receipt. For a retained project master, record and verify
   `projectCopy` and `projectCopySHA256` against the returned file before using
   it. This is local byte binding, not a cryptographic signature from ImageGen.
   Keep actual request slot, guide/reference paths, hashes and reference order
   with the attempt. Requested anatomy is not observed anatomy.

   If ImageGen returns a near-green RGB backdrop, do not edit the character or
   pretend the result has alpha. Copy the raw result into the lab, run the
   project-local `tools/character_pipeline/normalize_imagegen_chroma.py`, and
   import the exact-green derivative with `intake_derived_frame.py`. That
   importer binds the raw ImageGen copy, its untouched tool response, the
   normalization report and binary mask; it never labels the derivative as a
   new generation. Inspect the resulting RGBA candidate on light and dark
   backgrounds before source review.

   The derivative verifier now decodes both originals and derivatives, checks
   equal RGB size, recomputes the edge-connected background mask, and directly
   compares every protected subject pixel. A rehashed redraw, empty subject or
   a mask reclassifying the subject as background must fail. Do not alter the
   source to satisfy these checks. A rejected unchanged source cannot be
   reapproved merely by writing different notes.
   `source_provenance.py` now revalidates the saved response, retained master,
   explicit pair-crop or matte derivation, and current slot pixels. Source
   approval binds the exact `.source.json` too. Removing derivation fields
   does not turn a derivative into a new original. A stale historical receipt
   requires genuine reinspection/intake, never invented old tool output.
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
SHA256: f8b1826fceb2d4c09019db2f3a539c553d7a492ead2bae1aa63710b3e45e69c8

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

- **SITE-7 rifle pilot, 2026-09-13:** two opposite-pose pairs repeated the same
  planted right leg. For this repair line use ONE pose per image, the exact
  UAL phase guide FIRST and the appearance reference SECOND. Do not repeat the
  failed pair approach. The right-thigh holster belongs to the anatomical
  right leg; inspect hip-to-boot continuity, not just the pouch location.
  Retain the valid half via `--side` only after viewing it. Existing approved
  pair sources are unaffected. E1/E2 improvements are not an approved cycle.

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
- Cycle validation also compares the decoded native character panel to the
  expected authored atlas phase with codec tolerance. A moving timer or grid
  over a frozen body is not gait evidence. Opposite 1/4 and 2/5 chain checks
  catch repeated annotated poses, but cannot prove that the reviewer labeled
  the actual anatomical legs correctly. Uncertain limbs remain unapproved.
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
SHA256: 6902b718cf5e6690e8a8c7d96f06e64b20860aa62bb246624e9c4e511f2caa19

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
chronological source sheet, native source pair panels, local canvas-review HTML,
and **unreviewed** `cycle-observations.json`. The left video panel displays the
compiled cell at 1:1 pixels. The right displays a 270px character over ground
moving at the recipe velocity. This is source-cycle evidence, not the real
game controller. The canvas uses actual unwarped cells and a real-time 1x clock;
its three-cycle button records presentation times, visibility and viewport to the
owned QA server. Preserve the encoded video for independent decoded-pixel checks.
If embedded video crashes, use this canvas, not a claimed unseen video review.
The trace records presentation only; it does not prove the reviewer watched or
understood it, and it is not yet an enforced cycle-approval input. Capture a native
1080p live surface for dynamic evidence. Nothing activates an atlas or approves art.

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
ACTUAL_REVIEWER --notes ACTUAL_FAILURE` and an explicit `--rejection-scope`.
For `source-art`, repeat `--failed-slot E/walk/4` for the actual failed slots.
Both file and decoded-pixel hashes are retained; changing a good slot or PNG
metadata cannot fix a different rejected slot. For `timing`, `preview`,
`annotation`, or `runtime`, repeat `--required-change ACTUAL_LOCAL_FILE` for
the actual configuration/code/evidence requiring repair. Each named input must
change and a fresh whole-cycle review is still required. Do not regenerate good
art to resolve a video codec, timing, or annotation error. Prior records stay
intact and delivery becomes HOLD; evidence existence is not a visual PASS.

The current gate also recompiles each source into its cell without writing an
active atlas, compares all alpha and visible RGB pixels plus muzzle/clip data,
then checks decoded video panels against the phase schedule with codec tolerance.
Each phase-difference region must also match the expected phase absolutely:
merely being closer than the alternatives allows superposed ghost frames. The
frozen-patch and ghost-superposition negative tests must fail while a real encoded
candidate passes; these are video-integrity checks, not motion-quality scores.
RGB stored under alpha=0 is canonicalized because lossless WebP need not retain
invisible color bytes. Neither comparison judges naturalness or anatomical labels.

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
SHA256: 06525e6ec60181067b24422dc85b6bed5c64f310f019128b7353cc4800fb33ed

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
SHA256: c80e556d0e2119eb8d42ee6c5d0678229dfa5cc1fb96f3115455d475d9cb10af

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
                try:
                    from source_provenance import validate_slot
                    validate_slot(ROOT,path,r)
                except (ValueError,KeyError,TypeError,OSError) as error:
                    row['state']='stale_provenance';row['provenanceError']=str(error)
            if digest in seen:row['state']='duplicate_source';errors.append(f'{name}: same source as {seen[digest]}')
            seen[digest]=name
            current=[r for r in reviews if r['slot']==name]
            if row['state']=='needs_review' and current:
                review=current[-1]
                if review.get('sourceSHA256')==digest and review.get('sourceReceiptSHA256')==sha(receipt) and review.get('referenceSHA256')==c['referenceSHA256'] and binding_valid(review.get('evidence')):
                    row['state']='approved' if review['decision']=='approved' else 'repair'
        rows.append(row)
    pending=[r for r in rows if r['state']!='approved']
    pilots=[r for slot in PILOT for r in pending if r['slot']==slot]
    repairs=[r for r in pending if r['state']=='repair']
    next_row=(repairs or pilots or pending or [None])[0]
    return {'character':character,'mode':'source-authoring','ready':not errors and not pending,'requiredFrames':len(rows),'approvedFrames':len(rows)-len(pending),'next':next_row or 'build','errors':errors,'slots':rows}

def review_source(character,slot,decision,evidence,notes,reviewer):
    if decision not in ('approved','repair'):raise ValueError('Use approved or repair')
    c=recipe(character);path=dict(slots(c)).get(slot)
    if path is None or not path.exists():raise ValueError('Cannot review a missing source slot')
    if decision=='approved':
        from cycle_review import require_pilot
        direction,action,_=slot.split('/')
        require_pilot(character,direction,action)
    if not notes.strip() or not reviewer.strip():raise ValueError('Record the actual observation and reviewer')
    proof=local(evidence)
    if not proof.is_file():raise ValueError('Review evidence is missing')
    ledger=ROOT/'qa'/character/'source_reviews.json';reviews=read(ledger) if ledger.exists() else []
    if decision=='approved':
        from source_provenance import pixels
        pixel_hash=pixels(path)
        if any(r.get('decision')=='repair' and (r.get('sourceSHA256')==sha(path) or r.get('sourcePixelSHA256')==pixel_hash) for r in reviews):
            raise ValueError('Rejected source bytes are unchanged; notes cannot repair source art')
        state=next(r['state'] for r in source_status(character)['slots'] if r['slot']==slot)
        if state not in ('needs_review','approved'):
            raise ValueError('Source provenance/readiness must pass before approval: '+state)
    from source_provenance import pixels
    row={'recordedAt':stamp(),'slot':slot,'decision':decision,'reviewer':reviewer,'notes':notes,'sourceSHA256':sha(path),'sourcePixelSHA256':pixels(path),'sourceReceiptSHA256':sha(path.with_suffix('.source.json')) if path.with_suffix('.source.json').exists() else None,'referenceSHA256':c['referenceSHA256'],'evidence':binding(proof)}
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
    weapon=recipe(character)['weapon']
    for key in ('fireInterval','reloadSeconds'):
        if type(weapon.get(key)) not in (int,float) or not math.isfinite(weapon[key]) or weapon[key]<=0:raise ValueError('Invalid authoritative weapon timing')
    for row in rapid:
        def finite(key):
            value=row.get(key)
            return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
        if any(row.get(k) is not True for k in ['pass','heldMouse','locomotionUnchanged','oldProjectileVelocityUnchanged']):raise ValueError('Rapid aim state failed: '+row['name'])
        if any(not finite(k) or row[k]>=1e-5 for k in ['immediateErrorDegrees','firstFrameErrorDegrees','shotErrorDegrees']):raise ValueError('Rapid aim used a stale input: '+row['name'])
        if any(not finite(k) for k in ['immediateMs','firstFrameMs','shotWaitSeconds','eligibleBudgetSeconds']):raise ValueError('Invalid aim timing')
        if row['immediateMs']>1000/120 or row['firstFrameMs']>50:raise ValueError('Aim response exceeds latency budget')
        if any(not finite(k) for k in ['initialCooldownSeconds','initialReloadSeconds']):raise ValueError('Missing initial weapon timing')
        cooldown,reload=row['initialCooldownSeconds'],row['initialReloadSeconds']
        ammo=row.get('initialAmmo')
        if (cooldown>weapon['fireInterval']+1e-8 or reload>weapon['reloadSeconds']+1e-8 or
                type(ammo) is not int or not 0<=ammo<=weapon['magazine']):raise ValueError('Initial weapon state exceeds current recipe')
        expected_budget=(max(reload,cooldown) if reload>0 else cooldown+weapon['reloadSeconds'] if ammo==0 else cooldown)+1/120
        if abs(row['eligibleBudgetSeconds']-expected_budget)>1e-8:raise ValueError('Self-declared eligibility budget differs from weapon state')
        samples=row.get('inputSamples',[]);sector=DIRECTIONS.index(row['name'].split('_',1)[1])
        if len(samples)!=3 or [s.get('sector') for s in samples]!=[(sector+4)%8,(sector+2)%8,sector]:raise ValueError('Missing actual reversal sample sequence')
        previous_ms=-1.0
        def vector2(value):return isinstance(value,list) and len(value)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in value)
        for sample in samples:
            ms=sample.get('offsetMs');angle=sample.get('aim')
            if type(ms) not in (int,float) or not math.isfinite(ms) or not previous_ms<=ms<=row['immediateMs']:raise ValueError('Invalid reversal sample time')
            previous_ms=ms
            muzzle=sample.get('muzzle')
            if (not isinstance(muzzle,list) or len(muzzle)!=3 or not vector2(muzzle[:2]) or
                type(muzzle[2]) not in (int,float) or not math.isfinite(muzzle[2]) or
                abs(muzzle[2]-weapon['height'])>1e-8 or not vector2(sample.get('target')) or
                type(angle) not in (int,float) or not math.isfinite(angle)):
                raise ValueError('Missing sampled muzzle ray at actual weapon height')
            if not vector2(sample.get('requestedTarget')) or not vector2(sample.get('actorPosition')):raise ValueError('Missing independently requested target')
            origin,requested=sample['actorPosition'],sample['requestedTarget']
            requested_angle=sample['sector']*math.pi/4
            if (math.hypot(*(requested[i]-origin[i]-4*f(requested_angle) for i,f in enumerate((math.cos,math.sin))))>1e-6 or
                math.hypot(*(sample['target'][i]-requested[i] for i in (0,1)))>1e-6):raise ValueError('Reversal labels do not match actual requested target')
            if origin!=row.get('locomotionBefore',[])[3:5] or sample.get('actorTime')!=row.get('locomotionBefore',[None])[0]:raise ValueError('Reversal actor basis differs from observed state')
            x,y=(sample['target'][i]-sample['muzzle'][i] for i in (0,1))
            difference=math.atan2(y,x)-angle
            if math.hypot(x,y)<1e-8 or abs(math.atan2(math.sin(difference),math.cos(difference)))>math.radians(1e-5):raise ValueError('A reversal sample used stale aim')
        before,after=row.get('locomotionBefore'),row.get('locomotionAfterInput')
        if (not isinstance(before,list) or len(before)!=9 or before!=after or
                any(type(v) not in (int,float) or not math.isfinite(v) for v in before)):
            raise ValueError('Immediate input changed locomotion or weapon state')
        if before[5]!=ammo or max(0,before[6])!=cooldown or before[8]!=reload:raise ValueError('Initial weapon state differs from sampled actor')
        old=row.get('oldProjectileSamples')
        if not isinstance(old,list):raise ValueError('Missing old projectile velocity samples')
        for i,bullet in enumerate(old):
            if bullet.get('index')!=i or not vector2(bullet.get('before')) or not vector2(bullet.get('after')) or bullet['before']!=bullet['after']:raise ValueError('Old projectile changed velocity')
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
            s.add_argument('--rejection-scope',choices=['source-art','timing','preview','annotation','runtime'])
            s.add_argument('--failed-slot',action='append');s.add_argument('--required-change',action='append')
    a=p.parse_args()
    try:
        if a.command=='status':result=workflow_status(a.character)
        elif a.command=='prepare-cycle':
            from cycle_preview import prepare
            result=prepare(a.character,a.direction,a.action)
        elif a.command=='review-cycle':
            from cycle_review import record
            result=record(a.character,a.direction,a.action,a.decision,a.packet,a.evidence,a.notes,a.reviewer,a.rejection_scope,a.failed_slot,a.required_change)
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
SHA256: 9e95d2c51983f09d1374afa1ab0655b4ee50330d6e236618d47e7977f44c319c

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
    from source_provenance import pixels
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
            'previewCodeSHA256': w.sha(Path(__file__).with_name('cycle_preview.py')),
            'liveReviewCodeSHA256': w.sha(Path(__file__).with_name('cycle_live_review.js')),
            'recipeValues': {'speed':c['locomotion'][action+'Speed'], 'stride':c['locomotion'][action+'Stride'], 'heightMetres':c['heightMetres']},
            'provenanceCodeSHA256': w.sha(Path(__file__).with_name('source_provenance.py')),
            'reviewCodeSHA256': w.sha(Path(__file__)),
            'sources': [dict(slot=name, pixelSHA256=pixels(path), **w.binding(path)) for name, path in zip(names, files)]}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_content(value):
    return {row['slot']:row.get('pixelSHA256',row['sha256']) for row in value['sources']}


def rejection_unresolved(row, expected):
    scope=row.get('rejectionScope','source-art')
    if scope=='source-art':
        old={r['slot']:r for r in row['inputs']['sources']}
        new={r['slot']:r for r in expected['sources']}
        # Historical unspecified failures remain conservative; changing one
        # unrelated frame is never an explicit resolution of a rejected frame.
        for slot in row.get('failedSlots',list(old)):
            if slot not in old or slot not in new:return True
            if old[slot]['sha256']==new[slot]['sha256']:return True
            if old[slot].get('pixelSHA256') and old[slot]['pixelSHA256']==new[slot].get('pixelSHA256'):return True
        return False
    changes=row.get('requiredChange',[])
    return not changes or any(not w.local(item['path']).is_file() or w.binding_valid(item) for item in changes)


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
        state = 'repair' if rejection_unresolved(latest,expected) else 'needs_cycle_review'
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
    # Contact-only checks missed repeated swing/passing poses. Compare both
    # anatomical chains relative to their own hips, so a translated copy of the
    # same stance is not an opposite step. This cannot authenticate limb labels.
    for first,opposite in ((1,4),(2,5)):
        changes=[]
        for side in ('left','right'):
            a=frames[first]['landmarks'];b=frames[opposite]['landmarks']
            for part in ('Knee','Sole'):
                av=[a[side+part][i]-a[side+'Hip'][i] for i in (0,1)]
                bv=[b[side+part][i]-b[side+'Hip'][i] for i in (0,1)]
                changes.append(math.dist(av,bv))
        if sum(changes)/len(changes)<height*.025:
            raise ValueError('Opposite swing/passing poses repeat the same anatomical chains')
    return True


@lru_cache(maxsize=16)
def validate_video_pixels(video_path,video_sha,atlas_path,atlas_sha,clip_json,speed,stride):
    """Check actual decoded left-panel pixels against the chronological atlas.

    VP8 is lossy, so compare the composited source region with a small codec
    tolerance. Headers and ground-grid text are not accepted as image evidence.
    The inputs include hashes so changed bytes cannot reuse an earlier result.
    """
    import cv2
    import numpy as np
    from PIL import Image
    clip=json.loads(clip_json)
    cw,ch=clip['cell'];columns=clip['columns']
    if (cw,ch)!=(768,768) or columns!=3 or clip['frames']!=6:
        raise ValueError('Unexpected source-cycle preview layout')
    with Image.open(atlas_path) as image:
        atlas=np.array(image.convert('RGBA'))
    # Lossless WebP may canonicalize RGB under alpha=0. Compare every alpha
    # byte and every visible RGB byte, not undefined invisible color storage.
    atlas[atlas[:,:,3]==0,:3]=0
    expected=[]
    for i in range(6):
        rgba=atlas[i//columns*ch:(i//columns+1)*ch,i%columns*cw:(i%columns+1)*cw]
        if rgba.shape!=(ch,cw,4):raise ValueError('Incomplete chronological atlas')
        a=rgba[:,:,3:4].astype(float)/255
        expected.append((rgba[:,:,:3]*a+np.array([16,30,39])*(1-a)).astype(np.float32))
    discriminating={}
    root_y=int(clip.get('root',[384,716])[1])
    for i in range(6):
        for j in range(i):
            mask=np.max(np.abs(expected[i]-expected[j]),axis=2)>16
            mask[max(0,root_y-1):min(ch,root_y+3)]=False
            if int(mask.sum())<16:
                raise ValueError('Cycle video has insufficient distinguishable phase pixels; review capture, not automatic art approval')
            # Keep every pixel of small differences (the frozen-foot counter-
            # example is 2048 pixels). Bound broad-body comparisons to evenly
            # distributed native pixel samples; never dilute into background.
            offsets=np.flatnonzero(mask)
            offsets=offsets[::max(1,math.ceil(len(offsets)/4096))]
            discriminating[(i,j)]=np.unravel_index(offsets,(ch,cw))
    cap=cv2.VideoCapture(video_path)
    count=0
    try:
        fps=cap.get(cv2.CAP_PROP_FPS)
        if not finite(fps) or abs(fps-30)>0.01:raise ValueError('Cycle preview requires recorded 30 Hz chronology')
        starts=contract.starts(clip)
        while True:
            ok,frame=cap.read()
            if not ok:break
            index=contract.frame_at(count/fps*speed/stride,starts)
            pixels=cv2.cvtColor(frame[170:170+ch,30:30+cw],cv2.COLOR_BGR2RGB).astype(np.float32)
            if pixels.shape!=expected[index].shape:raise ValueError('Missing native source panel in cycle video')
            difference=np.abs(pixels-expected[index])
            # The compiler draws a ground baseline across these two rows.
            root_y=int(clip.get('root',[384,716])[1])
            difference[max(0,root_y-1):min(ch,root_y+3)]=0
            if float(difference.mean())>4.0 or float(np.quantile(difference,.99))>32.0:
                raise ValueError('Cycle video pixels do not show the expected authored phase at frame '+str(count))
            for alternative in range(6):
                if alternative==index:continue
                mask=discriminating[(max(index,alternative),min(index,alternative))]
                roi_error=np.abs(pixels[mask]-expected[index][mask])
                correct_error=float(roi_error.mean())
                other_error=float(np.abs(pixels[mask]-expected[alternative][mask]).mean())
                # Relative similarity is insufficient: a faint superposition
                # of all phases can be slightly closer to the intended one.
                # Fixed codec tolerances, never adjustable in review receipts.
                if correct_error>12.0 or float((roi_error.max(axis=1)>48.0).mean())>0.10:
                    raise ValueError('Cycle video pixels have excessive phase-region error at frame '+str(count))
                if other_error-correct_error<=1.0:
                    raise ValueError('Cycle video pixels do not distinguish the expected phase from another cell at frame '+str(count))
            count+=1
    finally:cap.release()
    if count==0:raise ValueError('Cycle video must actually decode')
    return count


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
    validate_video_pixels(str(w.local(preview['video']['path'])),preview['video']['sha256'],
                          str(w.local(preview['atlas']['path'])),preview['atlas']['sha256'],
                          json.dumps(preview['clip'],sort_keys=True),speed,stride)
    validate_source_atlas(json.dumps(expected,sort_keys=True),json.dumps(preview['clip'],sort_keys=True),
                          str(w.local(preview['atlas']['path'])),preview['atlas']['sha256'])
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


@lru_cache(maxsize=16)
def validate_source_atlas(expected_json, clip_json, atlas_path, atlas_sha):
    """Independently re-run source registration; never write an active atlas."""
    import numpy as np
    from PIL import Image
    from build_atlas import register
    expected=json.loads(expected_json); clip=json.loads(clip_json)
    c=w.read(w.local(expected['recipe']['path']))
    direction=expected['direction']; action=expected['action']
    annotations=c.get('annotations',{}).get(direction,{}).get(action,{})
    cell=c.get('cell',[768,768]); root=c.get('root',[384,716]); height=c.get('spriteHeight',656)
    if any(clip.get(key)!=value for key,value in [('cell',cell),('columns',3),('frames',6),('root',root),('height',height)]):
        raise ValueError('Cycle clip differs from source compiler contract')
    if clip.get('phaseStarts')!=contract.starts(c['clips'][action]):
        raise ValueError('Cycle phase schedule differs from recipe')
    with Image.open(atlas_path) as image:
        atlas=np.array(image.convert('RGBA'))
    atlas[atlas[:,:,3]==0,:3]=0
    for i,row in enumerate(expected['sources']):
        source=w.local(row['path'])
        if w.sha(source)!=row['sha256']: raise ValueError('Source changed during cycle check')
        fresh,note=register(source,c,direction,annotations.get(str(i),{}))
        fresh[fresh[:,:,3]==0,:3]=0
        x=i%3*cell[0]; y=i//3*cell[1]
        if not np.array_equal(atlas[y:y+cell[1],x:x+cell[0]],fresh):
            raise ValueError('Cycle atlas pixels do not compile from current source: '+row['slot'])
        if clip.get('muzzles',[None]*6)[i]!=note['muzzle'] or clip.get('sources',[None]*6)[i]!=note:
            raise ValueError('Cycle metadata does not compile from current source: '+row['slot'])
    return True


def record(character, direction, action, decision, packet_path=None, evidence=None, notes=None, reviewer=None,
           rejection_scope=None,failed_slots=None,required_change=None):
    if decision not in ('approved','repair'):raise ValueError('Use approved or repair')
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
        unresolved=[r for r in previous if r['direction']==direction and r['action']==action and
                    r['decision']=='repair' and rejection_unresolved(r,expected)]
        if unresolved:
            raise ValueError('Rejected cycle source bytes are unchanged or required non-art repair is unresolved')
        packet = w.read(w.local(packet_path))
        validate_packet(packet, expected)
        row.update(packet=w.binding(w.local(packet_path)), reviewer=packet['reviewer'])
    else:
        if not notes or not reviewer or not evidence or not w.local(evidence).is_file():
            raise ValueError('Record real rejection observations and evidence')
        if rejection_scope not in ('source-art','timing','preview','annotation','runtime'):
            raise ValueError('Record an explicit rejection scope')
        row['rejectionScope']=rejection_scope
        if rejection_scope=='source-art':
            valid={r['slot'] for r in expected['sources']}
            if not failed_slots or not set(failed_slots)<=valid:raise ValueError('Name actual failed source slots')
            row['failedSlots']=list(dict.fromkeys(failed_slots))
        else:
            if not required_change:raise ValueError('Bind actual inputs/code/evidence requiring non-art repair')
            row['requiredChange']=[w.binding(w.local(path)) for path in required_change]
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
SHA256: 8679c863efb01e107540fed9449cb06be86bc7b63cc369627ade40c23e95c403

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
    if config.get('workflowVersion')!=1:raise ValueError('Explicit source migration is required before replacing historical sources')
    if tool_response is None:raise ValueError('Supply --tool-response with the actual saved ImageGen tool response')
    proof=None
    if tool_response is not None:
        tool_response=tool_response.resolve()
        if not tool_response.is_relative_to(ROOT):raise ValueError('Copy the tool response into this lab first')
        from source_provenance import response_master,digest
        master=response_master(ROOT,tool_response)
        if digest(source)!=digest(master):raise ValueError('Input differs from the preserved returned master')
        proof={'path':tool_response.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(tool_response.read_bytes()).hexdigest()}
    target=folder/f'{direction}_{action}_{frame}_master.png'
    override=folder/f'{direction}_{action}_{frame}_override.png'
    if override.exists():target=override
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()==digest and target.with_suffix('.source.json').exists():
            current=json.loads(target.with_suffix('.source.json').read_text(encoding='utf-8-sig'))
            from source_provenance import validate_slot
            try:
                validate_slot(ROOT,target,current)
                if current.get('toolResponse')==proof:return target
            except (ValueError,KeyError,TypeError,OSError):pass
        history=folder/'previous';history.mkdir(exist_ok=True);old=hashlib.sha256(target.read_bytes()).hexdigest()[:12];shutil.copy2(target,history/(target.stem+'_'+old+target.suffix))
        previous_receipt=target.with_suffix('.source.json')
        if previous_receipt.exists():shutil.copy2(previous_receipt,history/(target.stem+'_'+old+'.source.json'))
    if source.resolve()!=target:shutil.copy2(source,target)
    receipt={'generator':'Codex built-in ImageGen','importedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source.resolve()),'native':native,'sha256':digest,'destination':target.relative_to(ROOT).as_posix(),'sourceMaster':{'path':master.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(master.read_bytes()).hexdigest()}}
    if proof:receipt['toolResponse']=proof
    target.with_suffix('.source.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
    from character_workflow import invalidate_delivery
    invalidate_delivery(ident,'Source or provenance changed: '+direction+'/'+action+'/'+str(frame))
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--generated',type=Path,required=True);p.add_argument('--tool-response',type=Path);a=p.parse_args();intake(a.character,a.direction,a.action,a.frame,a.generated,a.tool_response)

```

## FILE: motion_lab_v1/intake_pair.py
SHA256: 0249341fef80b65424b8ae2dc709c5ea6134428e714ca1e08e2854db498aada0

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
    if c.get('workflowVersion')!=1:raise ValueError('Explicit source migration required before historical source replacement')
    if direction not in DIRECTIONS or count!=6 or not 0<=pair<3:raise ValueError('Use an existing six-frame recipe and pair 0/1/2')
    from cycle_review import require_pilot
    require_pilot(character,direction,action)
    proof=local(tool_response);generated=Path(generated).resolve()
    from source_provenance import response_master
    original=response_master(ROOT,proof)
    if sha(original)!=sha(generated):raise ValueError('Pair input differs from preserved returned master')
    with Image.open(generated) as im:
        native=list(im.size)
        if min(native)<1024 or max(native)<1536:raise ValueError('Pair must be native 1536x1024 or larger')
    digest=sha(generated);masters=ROOT/'art'/character/'gait_v8'/'native_pairs';masters.mkdir(parents=True,exist_ok=True)
    master=masters/f'{direction}_{action}_pair{pair}_{digest[:12]}.png'
    if not master.exists():shutil.copy2(generated,master)
    if sha(master)!=digest:raise ValueError('Master copy hash mismatch')
    extracted=[(side,im,box) for side,(im,box) in enumerate(subjects(master,2)) if side_filter is None or side==side_filter]
    if not extracted or any(im.height<800 for _,im,_ in extracted):raise ValueError('Subject is too small for the current 656px atlas; request a native pair')
    # Validate every selected half before the first active-slot write.
    rows=[]
    for side,im,box in extracted:
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
    from character_workflow import invalidate_delivery
    invalidate_delivery(character,'Source or provenance changed: '+direction+'/'+action+'/pair'+str(pair))
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',default='walk');p.add_argument('--pair',type=int,required=True);p.add_argument('--generated',required=True);p.add_argument('--tool-response',required=True)
    p.add_argument('--side',type=int,choices=[0,1],help='Import only an actually reviewed half; a failed partner is not promoted')
    a=p.parse_args();print(json.dumps(intake(a.character,a.direction,a.action,a.pair,a.generated,a.tool_response,a.side),ensure_ascii=False))

```

## FILE: motion_lab_v1/intake_derived_frame.py
SHA256: de92a9355f690b2768b1e1d4c18b4c85e327d3c1d8d28a3bf1c9ccb9e6e5bf7f

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
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

from character_workflow import DIRECTIONS, ROOT, binding, local, recipe, sha, slots, write


GREEN = (0, 255, 0)


def _actual_background(rgb):
    path=Path(__file__).resolve().parents[1]/'tools/character_pipeline/normalize_imagegen_chroma.py'
    spec=importlib.util.spec_from_file_location('sable_chroma_verification',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.edge_connected_background(rgb)[0]


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
    from source_provenance import response_master
    if response_master(ROOT,tool_response)!=source_master:
        raise ValueError('Normalization source differs from actual preserved master')
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
    with Image.open(source_master) as original:
        original.load()
        if original.mode != 'RGB' or original.size != (rgb.shape[1],rgb.shape[0]):
            raise ValueError('normalization must preserve original RGB mode and dimensions')
        original_rgb=np.asarray(original)
    subject=mask_array==255
    if not subject.any() or not np.array_equal(rgb[subject],original_rgb[subject]):
        raise ValueError('normalization changed protected subject pixels')
    background = mask_array == 0
    if not np.array_equal(background,_actual_background(original_rgb)):
        raise ValueError('normalization mask differs from original edge-connected background')
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
    if config.get('workflowVersion') != 1:
        raise ValueError('Explicit source migration required before historical source replacement')
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
    from character_workflow import invalidate_delivery
    invalidate_delivery(character,'Source or provenance changed: '+direction+'/'+action+'/'+str(frame))
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
SHA256: d63a443ba1e9704e158a6bd4830f4471ca8b61ab1ddbf4f58d51e1ae2ee4237a

```text
"""Deterministic enemy matte/crop and native QA. Never activates an app asset.

Uses the established model-free compiler. Source artwork stays byte-immutable.
No leg segmentation, anatomical warp, local model or synthetic missing pixels.
"""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image, ImageDraw
import numpy as np
from build_atlas import key_image

ROOT=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_source(source, response):
    """Bind the exact retained master, not just the name of its generator.

    This is local provenance consistency, not cryptographic provider attestation
    or an artistic approval. The original tool response must be recorded honestly.
    """
    from source_provenance import response_master
    if response_master(ROOT,response)!=source:
        raise ValueError('Tool response must bind this exact project copy')
    return json.loads(response.read_text(encoding='utf-8-sig'))

def prepare(ident, source, response):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):
        raise ValueError('Use an asset id, not a path')
    source=source.resolve(); response=response.resolve()
    if not source.is_relative_to(ROOT) or not response.is_relative_to(ROOT):
        raise ValueError('Project-local source and actual tool response required')
    verify_source(source,response)
    with Image.open(source) as opened:raw=opened.copy()
    if max(raw.size)<1024:
        raise ValueError('Native high-resolution generated master required')
    rgba=key_image(source)
    yy,xx=np.where(rgba[:,:,3]>30)
    if not len(xx):
        raise ValueError('Empty separated subject; retain as failed source')
    # Keep previous QA bytes when the preparation implementation changes.
    dependencies={'preparation':sha(Path(__file__)),'matte':sha(ROOT/'build_atlas.py'),'provenance':sha(ROOT/'source_provenance.py')}
    implementation=hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()[:8]
    out=ROOT/'qa/stage1_enemies_20260913'/ident/(sha(source)[:12]+'_'+implementation)
    out.mkdir(parents=True,exist_ok=True)
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
            'preparationCodeSHA256':sha(Path(__file__)),
            'matteCodeSHA256':sha(ROOT/'build_atlas.py'),
            'implementationDependencies':dependencies,
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
SHA256: 38250b5dcafbf777d48456c452b7dfb1539aa5008bf40bf01c831dd0185a52b1

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
from PIL.PngImagePlugin import PngInfo

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import cycle_review as cycle
import gait_contract as contract
import intake_frame
import build_atlas
PALETTE=[(90,120,130),(170,90,110),(100,160,190),(170,140,70),(80,100,190),(180,80,180)]


class CycleGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cv2
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        cls.video_fixture=Path(tempfile.mkdtemp(prefix='cycle_video_',dir=base))/'synthetic_1080p.mp4'
        encoded=[]
        for i,color in enumerate(PALETTE):
            source=cls.video_fixture.with_name(f'phase_{i}.png');Image.new('RGB',(64,96),color).save(source)
            frame,_=build_atlas.register(source,{},'E',{})
            panel=Image.new('RGB',(1920,1080),(16,30,39))
            panel.paste(Image.fromarray(frame),(30,170),Image.fromarray(frame[:,:,3]))
            encoded.append(cv2.cvtColor(np.array(panel),cv2.COLOR_RGB2BGR))
        writer=cv2.VideoWriter(str(cls.video_fixture),cv2.VideoWriter_fourcc(*'mp4v'),30,(1920,1080))
        if not writer.isOpened():raise RuntimeError('Local cycle video encoder unavailable')
        try:
            for i in range(108):
                writer.write(encoded[contract.frame_at(i/30*1.35/1.6,contract.starts({}))])
        finally:writer.release()

    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='cycle_',dir=base))
        for module in (w,intake_frame,build_atlas):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        reference=self.root/'art/fixture/identity.png';reference.parent.mkdir(parents=True);reference.write_bytes(b'identity fixture')
        c={'id':'fixture','name':'Fixture','source':'art/fixture','workflowVersion':1,
           'identityReference':'art/fixture/identity.png','referenceSHA256':w.sha(reference),
           'heightMetres':1.72,'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
        w.write(self.root/'characters/fixture.json',c)
        reviews=[]
        for i,(slot,path) in enumerate(w.slots(c)):
            info=PngInfo();info.add_text('technical_slot',slot)
            Image.new('RGB',(64,96),PALETTE[int(slot.split('/')[-1])]).save(path,pnginfo=info)
            master=path.with_name(f'original_fixture_{i}.png');master.write_bytes(path.read_bytes())
            returned=str(self.root/f'fake_returned_{i}.png')
            proof=self.root/f'qa/tool-fixture-{i}.json';w.write(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test; not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':w.sha(master)})
            receipt=path.with_suffix('.source.json')
            w.write(receipt,{'generator':'Codex built-in ImageGen','sha256':w.sha(path),'destination':str(path.relative_to(self.root)),'toolResponse':w.binding(proof),'sourceMaster':w.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':w.sha(path),'sourceReceiptSHA256':w.sha(receipt),'referenceSHA256':c['referenceSHA256'],'evidence':w.binding(path)})
        w.write(self.root/'qa/fixture/source_reviews.json',reviews)
        self.expected=cycle.inputs('fixture','E')
        self.out=self.root/'qa/cycle';self.out.mkdir(parents=True)
        self.clip={'cell':[768,768],'height':656,'columns':3,'frames':6,'root':[384,716],'phaseStarts':contract.starts(c['clips']['walk']),'muzzles':[],'sources':[]}
        atlas=Image.new('RGBA',(2304,1536))
        for i,row in enumerate(self.expected['sources']):
            pixels,note=build_atlas.register(w.local(row['path']),c,'E',{})
            atlas.paste(Image.fromarray(pixels),(i%3*768,i//3*768))
            self.clip['muzzles'].append(note['muzzle']);self.clip['sources'].append(note)
        atlas_path=self.out/'atlas.png';atlas.save(atlas_path)
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

    def test_repeated_swing_and_passing_chain_is_rejected(self):
        for a,b in ((1,4),(2,5)):
            p=copy.deepcopy(self.packet)
            p['frames'][b]['landmarks']=copy.deepcopy(p['frames'][a]['landmarks'])
            with self.assertRaisesRegex(ValueError,'swing/passing'):
                cycle.validate_packet(p,self.expected)

    def test_rebound_video_hash_does_not_prove_the_correct_atlas_pixels(self):
        path=self.out/'atlas.png'
        Image.new('RGBA',(2304,1536),(220,30,80,255)).save(path)
        preview=w.read(self.preview);preview['atlas']=w.binding(path);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'video.*pixels'):
            cycle.validate_packet(self.packet,self.expected)

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
        Image.new('RGB',(64,96),(30,50,90)).save(self.root/'art/fixture/E_walk_3_master.png')
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')

    def test_rejected_pixels_cannot_be_reapproved_by_notes(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Actual fixture rejection',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        with self.assertRaisesRegex(ValueError,'source bytes are unchanged'):
            cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(w.read(self.root/'dist/fixture.delivery.json')['status'],'HOLD_VISUAL_REPAIR')

    def test_renaming_rejected_sources_does_not_clear_rejection(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic rejection fixture',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        for i in range(6):
            path=self.root/f'art/fixture/E_walk_{i}_master.png'
            shutil.copy2(path,path.with_name(f'E_walk_{i}_override.png'))
        self.assertEqual(cycle.current('fixture','E')['state'],'repair')

    def test_other_slot_or_metadata_cannot_resolve_failed_slot(self):
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic E4 failed',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/4'])
        Image.new('RGB',(64,96),(70,80,90)).save(self.root/'art/fixture/E_walk_0_master.png')
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        path=self.root/'art/fixture/E_walk_4_master.png'
        info=PngInfo();info.add_text('new_note','same rejected pixels')
        Image.new('RGB',(64,96),PALETTE[4]).save(path,pnginfo=info)
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))

    def test_preview_repair_does_not_force_source_replacement(self):
        path=self.out/'preview-settings.json';w.write(path,{'testFixture':'old'})
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic preview fault',reviewer='unit fixture',rejection_scope='preview',required_change=[str(path)])
        before=cycle.source_content(cycle.inputs('fixture','E'))
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        w.write(path,{'testFixture':'fixed'})
        self.assertFalse(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        self.assertEqual(before,cycle.source_content(cycle.inputs('fixture','E')))

    def test_rebound_source_metadata_cannot_use_old_atlas(self):
        path=self.root/'art/fixture/E_walk_0_master.png'
        Image.new('RGB',(64,96),(200,80,90)).save(path)
        expected=cycle.inputs('fixture','E')
        with self.assertRaisesRegex(ValueError,'atlas pixels'):
            cycle.validate_source_atlas(json.dumps(expected,sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_preview_timing_cannot_override_recipe(self):
        config=w.recipe('fixture');config['clips']['walk']['phaseStarts']=[0,.2,.33,.5,.7,.83]
        w.write(self.root/'characters/fixture.json',config)
        with self.assertRaisesRegex(ValueError,'phase schedule'):
            cycle.validate_source_atlas(json.dumps(cycle.inputs('fixture','E'),sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_frozen_panel_with_small_distinct_cells_is_rejected(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'small_changes.png';atlas.save(path)
        movie=self.out/'frozen.mkv'
        writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
        self.assertTrue(writer.isOpened())
        page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=frames[0][:,:,:3]
        encoded=cv2.cvtColor(page,cv2.COLOR_RGB2BGR)
        try:
            for _ in range(108):writer.write(encoded)
        finally:writer.release()
        with self.assertRaisesRegex(ValueError,'distinguish|phase-region'):
            cycle.validate_video_pixels(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)

    def test_superposed_phase_ghosts_cannot_pass_as_authored_frames(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell[:,:,:3]);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'phase_ghost_atlas.png';atlas.save(path)
        base=np.rint(np.mean(frames,axis=0)).astype(np.uint8)
        for ghost in (False,True):
            movie=self.out/('ghosts.mkv' if ghost else 'correct_small_motion.mkv')
            writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
            self.assertTrue(writer.isOpened())
            try:
                for tick in range(108):
                    index=contract.frame_at(tick/30*1.35/1.6,contract.starts(self.clip))
                    cell=base.copy() if ghost else frames[index]
                    if ghost:cell[300:332,100+index*70:132+index*70]+=4
                    page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=cell
                    writer.write(cv2.cvtColor(page,cv2.COLOR_RGB2BGR))
            finally:writer.release()
            args=(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)
            if ghost:
                with self.assertRaisesRegex(ValueError,'phase-region'):cycle.validate_video_pixels(*args)
            else:self.assertEqual(cycle.validate_video_pixels(*args),108)

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)


if __name__=='__main__':unittest.main()

```

## FILE: motion_lab_v1/tests/test_character_workflow.py
SHA256: a389462d56af4a7d14b553cce99c3713c9ce6963f7d6d8e2df6bf54363fb1448

```text
"""Deterministic technical fixtures only; no generated game art or API calls."""
import copy,hashlib,json,math,sys,tempfile,unittest
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
            Image.new('RGBA',(16,24),(30+index,80,150,255)).save(path)
            master=self.art/f'technical_master_{index}.png';master.write_bytes(path.read_bytes())
            returned=str((self.root/f'fake_returned_{index}.png').resolve())
            proof=self.art/f'proof_{index}.json';save(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Technical fixture, not a real tool invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':digest(master)})
            receipt=path.with_suffix('.source.json')
            save(receipt,{'generator':'Codex built-in ImageGen','sha256':digest(path),'destination':str(path.relative_to(self.root)),'toolResponse':workflow.binding(proof),'sourceMaster':workflow.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':digest(path),'sourceReceiptSHA256':digest(receipt),'referenceSHA256':self.config['referenceSHA256'],'evidence':workflow.binding(path)})
        save(self.root/'qa/fixture/source_reviews.json',reviews)
        return list(workflow.slots(self.config))
    def browser_report(self):
        test_script=self.root/'public/qa/combat-checks.js';test_script.parent.mkdir(parents=True,exist_ok=True);test_script.write_text('fixture')
        rows=[{'name':f'{mode}_{d}','direction':d,'spriteDirection':d,'pass':True,'heldMouse':True,'shotCount':2,'observedShots':2,'travel':.2,'maxFacingErrorDegrees':0,'convergedShots':2,'maxCursorError':0} for mode in ['mouse','keyboard'] for d in workflow.DIRECTIONS]
        rows.append(dict(rows[0],name='repeat_preserves_mouse'))
        rapid=[dict(name=f'{mode}_{d}',pass_=True,heldMouse=True,locomotionUnchanged=True,oldProjectileVelocityUnchanged=True,immediateErrorDegrees=0,firstFrameErrorDegrees=0,shotErrorDegrees=0,immediateMs=.1,firstFrameMs=16,shotWaitSeconds=.1,eligibleBudgetSeconds=.1,shotCount=1) for mode in ['stationary','moving'] for d in workflow.DIRECTIONS]
        for r in rapid:
            r['pass']=r.pop('pass_');r['travel']=.2 if r['name'].startswith('moving_') else 0
            r.update(initialCooldownSeconds=.1-1/120,initialReloadSeconds=0,initialAmmo=1)
            sector=workflow.DIRECTIONS.index(r['name'].split('_',1)[1])
            r['inputSamples']=[dict(sector=s,offsetMs=.01*i,actorTime=0,actorPosition=[0,0],requestedTarget=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],muzzle=[0,0,self.config['weapon']['height']],target=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],aim=s*math.pi/4) for i,s in enumerate([(sector+4)%8,(sector+2)%8,sector])]
            r['locomotionBefore']=[0,0,0,0,0,1,.1-1/120,-10,0]
            r['locomotionAfterInput']=r['locomotionBefore'].copy()
            r['oldProjectileSamples']=[dict(index=0,before=[10,0],after=[10,0])]
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
    def test_delayed_shot_cannot_enlarge_its_own_budget(self):
        report=self.browser_report()
        report['rapidAim'][0].update(shotWaitSeconds=99,eligibleBudgetSeconds=100)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'Self-declared eligibility'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_summary_booleans_cannot_replace_actual_aim_samples(self):
        for key,value in [('inputSamples',[]),('locomotionAfterInput',[0]*9),
                          ('oldProjectileSamples',[dict(index=0,before=[10,0],after=[0,10])])]:
            report=self.browser_report();report['rapidAim'][0][key]=value
            path=self.root/'qa/browser.json';save(path,report)
            with self.assertRaises(ValueError):
                workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reversal_labels_cannot_replace_changed_targets(self):
        report=self.browser_report()
        for sample in report['rapidAim'][0]['inputSamples']:
            sample.update(target=[4,0],aim=0)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'requested target'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reload_budget_must_match_sampled_actor(self):
        report=self.browser_report();reload=self.config['weapon']['reloadSeconds']
        report['rapidAim'][0].update(initialReloadSeconds=reload,eligibleBudgetSeconds=reload+1/120,shotWaitSeconds=reload)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'sampled actor'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_live_muzzle_includes_validated_weapon_height(self):
        report=self.browser_report();path=self.root/'qa/browser.json';save(path,report)
        workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
        for muzzle in [[0,0],[0,0,float('nan')],[0,0,self.config['weapon']['height']+1]]:
            bad=copy.deepcopy(report);bad['rapidAim'][0]['inputSamples'][0]['muzzle']=muzzle;save(path,bad)
            with self.assertRaisesRegex(ValueError,'weapon height'):
                workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_source_rejection_cannot_be_cleared_with_new_notes(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        evidence=path.relative_to(self.root).as_posix()
        workflow.review_source('fixture','E/walk/0','repair',evidence,'Observed incorrect support leg','technical fixture reviewer')
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',evidence,'Changed notes, not the art','technical fixture reviewer')
    def test_missing_provenance_cannot_receive_approval(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        # Corrupt the tiny owned fixture receipt, leaving its pixel bytes alone.
        save(path.with_suffix('.source.json'),{})
        with self.assertRaisesRegex(ValueError,'provenance/readiness'):
            workflow.review_source('fixture','E/walk/0','approved',path.relative_to(self.root).as_posix(),'Actual fixture test','technical fixture reviewer')
    def test_receipt_only_change_invalidates_source_approval(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row['provenanceNote']='Changed evidence context';save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'needs_review')
    def test_missing_master_cannot_downgrade_to_original(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row.pop('sourceMaster');save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'stale_provenance')
    def test_reencoded_rejected_pixels_remain_rejected(self):
        from PIL.PngImagePlugin import PngInfo
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        workflow.review_source('fixture','E/walk/0','repair',str(target),'Observed a wrong support foot in synthetic fixture','unit-test')
        before=digest(target)
        image=Image.open(target).copy();info=PngInfo();info.add_text('different-metadata','same actual pixels')
        image.save(target,pnginfo=info)
        self.assertNotEqual(before,digest(target))
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',str(target),'No pixels changed; this approval must fail','unit-test')
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
SHA256: 50ad9533a33675dcda3266983d66e0f4d8233bdb502c44fc2166fc8aa7a520c7

```text
extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")
const ROLES := {"ENM_SITE7_RIFLE_01":"rifle", "ENM_SITE7_SHIELD_01":"shield",
    "ENM_SITE7_DRONE_01":"drone", "ENM_SITE7_ABERRANT_01":"melee", "BOSS_SITE7_ANCHOR_01":"boss"}
const LUNGE_SPEED := 360.0
const LUNGE_DURATION := 0.42
const LUNGE_RADIUS := 58.0
signal attack_started(event: Dictionary)

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
var _lunge_origin := Vector2.ZERO
var _lunge_reach := 0.0
var _shot_ordinal := 0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    top_level = true
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
    global_transform = Transform2D(0.0, actor.global_position)
    var role := str(ROLES.get(actor.enemy_id,""))
    if role.is_empty():
        actor.velocity = Vector2.ZERO
        _enter("UNSUPPORTED_ROLE",1.0)
        return
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    var aim := actor.aim_from_emitter(target.get_combat_aim_point())
    var boss := role == "boss"
    var rifle := role == "rifle"
    var shield := role == "shield"
    var drone := role == "drone"
    var melee := role == "melee"
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
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            locked_aim = actor.aim_from_emitter(target.get_combat_aim_point())
            locked_ground = toward
            _lunge_origin = actor.global_position
            _lunge_reach = LUNGE_SPEED * LUNGE_DURATION * actor.run_speed_multiplier
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.95 if boss else (0.7 if shield else (0.6 if melee else 0.48)))
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            _shot_ordinal = 0
            attack_started.emit({"actor_id":actor.get_instance_id(),"enemy_id":actor.enemy_id,
                "attack_serial":attack_serial,"phase":phase,"owner_id":get_instance_id()})
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", LUNGE_DURATION)
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
        actor.velocity = locked_ground * LUNGE_SPEED
        for victim in get_tree().get_nodes_in_group("operators"):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if lunge_contains(victim.global_position) and actor.global_position.distance_to(victim.global_position) < LUNGE_RADIUS:
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
    actor._spawn_projectile(direction, self, attack_serial, _shot_ordinal)
    _shot_ordinal += 1

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
    warning.top_level = true
    warning.ray = direction
    warning.windup = 1.15 if kind == "circle" else 1.35
    warning.damage = 20.0
    actor.get_parent().add_child(warning)
    warning.global_transform = Transform2D(0.0,location)

func lunge_contains(point: Vector2) -> bool:
    var offset := point - _lunge_origin
    var nearest := _lunge_origin + locked_ground * clampf(offset.dot(locked_ground),0.0,_lunge_reach)
    return point.distance_to(nearest) <= LUNGE_RADIUS

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if "ABERRANT" in actor.enemy_id:
        var base := to_local(_lunge_origin)
        var side := locked_ground.orthogonal() * LUNGE_RADIUS
        var tip := base + locked_ground * _lunge_reach
        draw_colored_polygon(PackedVector2Array([base-side,base+side,tip+side,tip-side]),Color(color,0.12))
        draw_circle(base,LUNGE_RADIUS,Color(color,0.12))
        draw_circle(tip,LUNGE_RADIUS,Color(color,0.12))
        draw_line(base-side,tip-side,color,1.8)
        draw_line(base+side,tip+side,color,1.8)
        var angle := locked_ground.angle()
        draw_arc(base,LUNGE_RADIUS,angle+PI/2,angle+3*PI/2,32,color,1.8)
        draw_arc(tip,LUNGE_RADIUS,angle-PI/2,angle+PI/2,32,color,1.8)
    else:
        var origin := to_local(actor.projectile_origin(locked_aim))
        draw_line(origin, origin + locked_aim * 300.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "contract_is_intent_not_validation":true,
        "role":ROLES.get(actor.enemy_id,"unsupported"),"lunge_radius":LUNGE_RADIUS,"lunge_reach":_lunge_reach}

```

## FILE: scripts/combat/site7_attack_warning.gd
SHA256: a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39

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
    var offset := to_local(point)
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
SHA256: 33811ab2aa52fc6835e6b43a3f794e6101440471125d9e1fd8e35590353f1071

```text
{
  "attacks": [
    {
      "actor_id": 83365988041,
      "attack_serial": 1,
      "enemy_id": "ENM_SITE7_DRONE_01",
      "owner_id": 84355843669,
      "phase": 1
    },
    {
      "actor_id": 119437002577,
      "attack_serial": 1,
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "owner_id": 120527522516,
      "phase": 2
    },
    {
      "actor_id": 153008212681,
      "attack_serial": 1,
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "owner_id": 154098731514,
      "phase": 1
    },
    {
      "actor_id": 187753827015,
      "attack_serial": 1,
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "owner_id": 188844344928,
      "phase": 1
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "owner_id": 212550552051,
      "phase": 3
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 2,
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "owner_id": 212550552051,
      "phase": 3
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "owner_id": 212550552051,
      "phase": 3
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 4,
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "owner_id": 212550552051,
      "phase": 3
    }
  ],
  "drive": "test bot -> real actor physics / weapon cooldown / projectile collisions / mission interactions",
  "emissions": [
    {
      "actor_id": 83365988041,
      "attack_serial": 1,
      "direction": [
        -0.953801989555359,
        -0.300435960292816
      ],
      "enemy_id": "ENM_SITE7_DRONE_01",
      "ordinal": 0,
      "origin": [
        932.223876953125,
        368.359558105469
      ],
      "owner_id": 84355843669,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@83/Tactics",
      "physics_tick": 127,
      "projectile_id": 100545858195
    },
    {
      "actor_id": 119437002577,
      "attack_serial": 1,
      "direction": [
        -0.987838327884674,
        -0.155484884977341
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 0,
      "origin": [
        975.766784667969,
        367.251373291016
      ],
      "owner_id": 120527522516,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@275/Tactics",
      "physics_tick": 370,
      "projectile_id": 130258306883
    },
    {
      "actor_id": 119437002577,
      "attack_serial": 1,
      "direction": [
        -0.987838327884674,
        -0.155484884977341
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 1,
      "origin": [
        975.766784667969,
        367.251373291016
      ],
      "owner_id": 120527522516,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@275/Tactics",
      "physics_tick": 378,
      "projectile_id": 133143988851
    },
    {
      "actor_id": 153008212681,
      "attack_serial": 1,
      "direction": [
        -0.982928335666656,
        0.183988928794861
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 0,
      "origin": [
        1759.85327148438,
        292.541717529297
      ],
      "owner_id": 154098731514,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@388/Tactics",
      "physics_tick": 707,
      "projectile_id": 168292255330
    },
    {
      "actor_id": 153008212681,
      "attack_serial": 1,
      "direction": [
        -0.982928335666656,
        0.183988928794861
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 1,
      "origin": [
        1759.85327148438,
        292.541717529297
      ],
      "owner_id": 154098731514,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@388/Tactics",
      "physics_tick": 715,
      "projectile_id": 168929790435
    },
    {
      "actor_id": 153008212681,
      "attack_serial": 1,
      "direction": [
        -0.982928335666656,
        0.183988928794861
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 2,
      "origin": [
        1759.85327148438,
        292.541717529297
      ],
      "owner_id": 154098731514,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@388/Tactics",
      "physics_tick": 723,
      "projectile_id": 169667987989
    },
    {
      "actor_id": 187753827015,
      "attack_serial": 1,
      "direction": [
        -0.998774230480194,
        0.0494988672435284
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 0,
      "origin": [
        1765.58728027344,
        283.181396484375
      ],
      "owner_id": 188844344928,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@575/Tactics",
      "physics_tick": 948,
      "projectile_id": 198692571822
    },
    {
      "actor_id": 187753827015,
      "attack_serial": 1,
      "direction": [
        -0.998774230480194,
        0.0494988672435284
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 1,
      "origin": [
        1765.58728027344,
        283.181396484375
      ],
      "owner_id": 188844344928,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@575/Tactics",
      "physics_tick": 956,
      "projectile_id": 201477589490
    },
    {
      "actor_id": 187753827015,
      "attack_serial": 1,
      "direction": [
        -0.998774230480194,
        0.0494988672435284
      ],
      "enemy_id": "ENM_SITE7_RIFLE_01",
      "ordinal": 2,
      "origin": [
        1765.58728027344,
        283.181396484375
      ],
      "owner_id": 188844344928,
      "owner_path": "/root/StoryStage01/@CharacterBody2D@575/Tactics",
      "physics_tick": 964,
      "projectile_id": 205000804065
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "direction": [
        -0.945312976837158,
        0.326164871454239
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 0,
      "origin": [
        2035.75122070313,
        395.287170410156
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1150,
      "projectile_id": 232599325403
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "direction": [
        -0.993707299232483,
        0.112008154392242
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 1,
      "origin": [
        2031.29895019531,
        375.584747314453
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1150,
      "projectile_id": 232699987782
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "direction": [
        -0.994199931621552,
        -0.107547901570797
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 2,
      "origin": [
        2031.25354003906,
        355.385589599609
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1150,
      "projectile_id": 232800651904
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "direction": [
        -0.946766972541809,
        -0.321919590234756
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 3,
      "origin": [
        2035.61743164063,
        335.663391113281
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1150,
      "projectile_id": 232901314366
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 1,
      "direction": [
        -0.853695154190063,
        -0.52077317237854
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 4,
      "origin": [
        2044.18005371094,
        317.368865966797
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1150,
      "projectile_id": 233001978484
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "direction": [
        -0.596689403057098,
        -0.802472293376923
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 0,
      "origin": [
        2067.82446289063,
        291.452545166016
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1464,
      "projectile_id": 271572798195
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "direction": [
        -0.407184422016144,
        -0.91334593296051
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 1,
      "origin": [
        2085.25903320313,
        281.252166748047
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1464,
      "projectile_id": 271673460574
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "direction": [
        -0.198051109910011,
        -0.980191707611084
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 2,
      "origin": [
        2104.49926757813,
        275.102355957031
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1464,
      "projectile_id": 271774123732
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "direction": [
        0.0206293016672134,
        -0.999787211418152
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 3,
      "origin": [
        2124.61791992188,
        273.299560546875
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1464,
      "projectile_id": 271874787901
    },
    {
      "actor_id": 211392923335,
      "attack_serial": 3,
      "direction": [
        0.238315269351006,
        -0.971187889575958
      ],
      "enemy_id": "BOSS_SITE7_ANCHOR_01",
      "ordinal": 4,
      "origin": [
        2144.64501953125,
        275.930725097656
      ],
      "owner_id": 212550552051,
      "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
      "physics_tick": 1464,
      "projectile_id": 271975451187
    }
  ],
  "failures": [],
  "recorded_utc": "2026-09-13T06:07:31",
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
    "elapsed_seconds": 28.0759433333341,
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
  "tested_code_sha256": {
    "res://data/missions/MIS_CH01_01.json": "55e438587ab75e8184251bf3fed509ff487fd7b9e931638ba3d68b8356829d5f",
    "res://scripts/actors/enemy_actor.gd": "64068d2f33d795c5ede3541482818f8c69b3a7165bc89e4ea5712bfdd995b059",
    "res://scripts/animation/premium_enemy_presentation.gd": "de5c93ec94522564388209d4f7bdee73b30e6ef2369c39fd38c780af1aba02c2",
    "res://scripts/combat/site7_attack_warning.gd": "a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39",
    "res://scripts/combat/site7_enemy_tactics.gd": "4884f999d1052ad4a691d60e774c9bed946509b27b7748c5d798bf1c91a04162",
    "res://scripts/missions/story_stage_01.gd": "18d2ddad6b6d9bc6e7af322767b61848f60bebdd8f3a6c5683734f3edc879907",
    "res://tests/smoke/site7_full_operation_smoke.gd": "783f3f5fa70fe434d65c1cdc3cb8d3e1b8b5c089fdace75077d890d3560990c2"
  },
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
        374.51416015625,
        411.837463378906
      ],
      "remaining": 0,
      "step": 1,
      "tick": 3,
      "wave": 0
    },
    {
      "ammo": 13,
      "health": [
        96.0,
        131.0,
        112.0
      ],
      "position": [
        698.919799804688,
        463.7900390625
      ],
      "remaining": 0,
      "step": 2,
      "tick": 356,
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
        1079.2138671875,
        549.736145019531
      ],
      "remaining": 0,
      "step": 3,
      "tick": 482,
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
        1457.57165527344,
        558.294799804688
      ],
      "remaining": 0,
      "step": 3,
      "tick": 600,
      "wave": 1
    },
    {
      "ammo": 6,
      "health": [
        96.0,
        114.0,
        88.0
      ],
      "position": [
        1507.75439453125,
        442.684814453125
      ],
      "remaining": 0,
      "step": 4,
      "tick": 961,
      "wave": 1
    },
    {
      "ammo": 0,
      "health": [
        72.0,
        90.0,
        40.0
      ],
      "position": [
        2157.22021484375,
        217.791519165039
      ],
      "remaining": 1,
      "step": 4,
      "tick": 1200,
      "wave": 0
    },
    {
      "ammo": 3,
      "health": [
        4.0,
        46.0,
        0.0
      ],
      "position": [
        2410.14526367188,
        490.269866943359
      ],
      "remaining": 0,
      "step": 5,
      "tick": 1625,
      "wave": 0
    }
  ],
  "visual_approval": false
}
```

## FILE: motion_lab_v1/source_provenance.py
SHA256: 37d78bc48061a439dbc1264e118dd987bb9ea0f4e497a446e17c8101da492bb7

```text
"""Recheck saved ImageGen/master/derivative relationships; not provider attestation.

All reads are project-local. A saved JSON can establish consistency, never prove
that a dishonest caller actually invoked a provider. Keep the real tool event.
"""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(root, value):
    path = (root / value).resolve()
    if path == root or not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Missing project-local provenance input')
    return path


def bound(root, value):
    if not isinstance(value, dict): raise ValueError('Missing provenance binding')
    path = local(root, value['path'])
    if digest(path) != value['sha256']: raise ValueError('Stale provenance binding')
    return path


def pixels(path):
    with Image.open(path) as im:
        rgba = im.convert('RGBA')
        header = f'RGBA:{rgba.width}x{rgba.height}:'.encode()
        return hashlib.sha256(header + rgba.tobytes()).hexdigest()


def response_master(root, response_path):
    response_path = local(root, response_path)
    proof = json.loads(response_path.read_text(encoding='utf-8-sig'))
    result = proof.get('result')
    if proof.get('tool') != 'image_gen.imagegen' or not isinstance(result, dict) or not result:
        raise ValueError('Actual ImageGen metadata required')
    returned = proof.get('returnedPath')
    hint = result.get('output_hint')
    if not isinstance(returned,str) or not Path(returned).is_absolute() or not isinstance(hint,str):
        raise ValueError('Actual returned path missing')
    normalized = hint.replace('\\','/')
    candidate = returned.replace('\\','/')
    # Quoted paths are indivisible: whitespace inside quotes is a filename
    # character, not permission to accept a shorter prefix. Remove their spans
    # before considering the explicitly supported unquoted tool sentences.
    quoted=list(re.finditer(r'''(["'`])([^\r\n]*?)\1''',normalized))
    exact_quoted=any(m.group(2)==candidate for m in quoted)
    unquoted=re.sub(r'''(["'`])([^\r\n]*?)\1''',' ',normalized)
    def exact_unquoted(line):
        for match in re.finditer(re.escape(candidate),line):
            before=line[:match.start()];after=line[match.end():].strip()
            if (not before or before[-1].isspace()) and after in ('','.', 'by default.'):
                return True
        return False
    if not exact_quoted and not any(exact_unquoted(line) for line in unquoted.splitlines()):
        raise ValueError('Returned path differs from actual output metadata')
    if not isinstance(proof.get('projectCopy'),str):
        raise ValueError('Missing exact project copy')
    master = local(root, proof['projectCopy'])
    if digest(master) != proof.get('projectCopySHA256'):
        raise ValueError('Returned master bytes changed (hash mismatch)')
    with Image.open(master) as image:
        image.verify()
    return master


def validate_slot(root, target, receipt):
    """No missing derivation fields may downgrade an edited image to an original."""
    if receipt.get('generator') != 'Codex built-in ImageGen' or digest(target) != receipt.get('sha256'):
        raise ValueError('Slot content or generator mismatch')
    if local(root,receipt['destination']) != target:
        raise ValueError('Receipt names a different slot')
    proof_path = bound(root,receipt.get('toolResponse'))
    original = response_master(root,proof_path)
    master = bound(root,receipt.get('sourceMaster'))
    if digest(master) != digest(original):
        raise ValueError('Preserved source master differs from returned project copy')
    derivation = receipt.get('derivation')
    if derivation is None:
        if digest(target) != digest(master):
            raise ValueError('Changed source needs its explicit derivation')
        return True
    if not isinstance(derivation,dict) or derivation.get('resampling') is not False or derivation.get('anatomicalWarp') is not False:
        raise ValueError('Unsupported source-art derivation')
    kind = derivation.get('kind')
    if kind == 'edge-connected green matte normalization only; no source-art redraw':
        from intake_derived_frame import _verify_derivative
        _verify_derivative(target,master,proof_path,bound(root,derivation.get('normalization')),bound(root,derivation.get('mask')))
    elif kind == 'chroma-key and connected-subject crop only':
        from build_atlas import subjects
        with Image.open(target) as image:
            actual = np.asarray(image.convert('RGBA'))
        matching = [im for im,box in subjects(master,2) if list(box) == derivation.get('box')]
        if len(matching) != 1 or not np.array_equal(actual,np.asarray(matching[0].convert('RGBA'))):
            raise ValueError('Pair crop pixels do not derive from the preserved master')
    else:
        raise ValueError('Unknown source-art derivation')
    return True

```

## FILE: motion_lab_v1/cycle_preview.py
SHA256: 7ed3f1745edc1035bea4757dc38603a1129c93e531ea235d4f10fe060cdf9740

```text
"""Make a source-cycle review kit; no active atlas writes or art generation."""
import json
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import character_workflow as w
import cycle_review
import gait_contract as contract


def prepare(character, direction, action='walk'):
    cycle_review.require_pilot(character, direction, action)
    expected = cycle_review.inputs(character, direction, action)
    from preview_gait import preview
    result = preview(character, direction, action)
    c = w.recipe(character)
    clip = result['clip']
    clip['phaseStarts'] = contract.starts(c['clips'][action])
    out = w.local(result['contact']).parents[3]
    atlas_path = out / 'public' / clip['image']
    contact_path = w.local(result['contact'])
    with Image.open(atlas_path) as im:
        atlas = im.convert('RGBA')
    cw, ch = clip['cell']
    frames = [atlas.crop((i % clip['columns'] * cw, i // clip['columns'] * ch,
                         (i % clip['columns'] + 1) * cw, (i // clip['columns'] + 1) * ch)) for i in range(6)]
    speed = c['locomotion']['runSpeed' if action == 'run' else 'walkSpeed']
    stride = c['locomotion']['runStride' if action == 'run' else 'walkStride']
    if not all(cycle_review.finite(v) and v > 0 for v in (speed, stride)):
        raise ValueError('Finite positive speed/stride required')
    duration = max(3 * stride / speed, 2.1)
    # MPEG-4 Part 2 (mp4v) decodes in OpenCV but not the Chromium review page.
    # VP8/WebM is playable by the same browser used for actual runtime QA.
    movie = out / f'{direction}_{action}_cycle_1080p.webm'
    writer = cv2.VideoWriter(str(movie), cv2.VideoWriter_fourcc(*'VP80'), 30, (1920, 1080))
    if not writer.isOpened():
        raise ValueError('Native preview video encoder unavailable')
    theta = w.DIRECTIONS.index(direction) * math.pi / 4
    try:
        for tick in range(math.ceil(duration * 30)):
            t = tick / 30
            phase = (t * speed / stride) % 1
            index = contract.frame_at(phase, clip['phaseStarts'])
            page = Image.new('RGB', (1920, 1080), '#101e27')
            draw = ImageDraw.Draw(page)
            draw.text((28, 20), f'{character.upper()} {direction} {action} | t={t:.3f}s | phase={phase:.3f} | frame={index}', fill='#e4ece9')
            draw.text((28, 48), 'DIAGNOSTIC SOURCE CYCLE / not game-runtime approval / native compiled cell at left; 270px game-scale at right', fill='#b8d4ce')
            draw.text((28, 76), f'contract {contract.digest()[:12]} / source {cycle_review.signature(expected)[:12]} / speed {speed} / stride {stride}', fill='#b8d4ce')
            page.paste(frames[index], (30, 170), frames[index])
            draw.line((30, 170 + clip['root'][1], 30 + cw, 170 + clip['root'][1]), fill='#72897e', width=2)
            ratio = 270 / clip['height']
            small = frames[index].resize((round(cw * ratio), round(ch * ratio)), Image.Resampling.LANCZOS)
            x0, y0 = 1240, 550
            # Root-locked preview, with ground moving at recipe velocity.
            # Source-frame changes are unwarped; slides remain visible.
            dx = t * speed * 270 / c['heightMetres'] * math.cos(theta)
            dy = t * speed * 270 / c['heightMetres'] * .5 * math.sin(theta)
            for x in range(880, 1920, 80):
                xx = 880 + (x - 880 - dx) % 1040
                draw.line((xx, 190, xx, 1000), fill='#2b4349')
            for y in range(190, 1000, 60):
                yy = 190 + (y - 190 - dy) % 810
                draw.line((880, yy, 1910, yy), fill='#2b4349')
            page.paste(small, (x0, y0), small)
            draw.text((900, 1020), 'Observe actual support-foot exchange, sliding and the 5 -> 0 seam. Different pixels are not different steps.', fill='#e4ece9')
            writer.write(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR))
    finally:
        writer.release()
    cap = cv2.VideoCapture(str(movie))
    native = [int(cap.get(3)), int(cap.get(4))]
    frame_count = 0
    while cap.read()[0]:
        frame_count += 1
    cap.release()
    if native != [1920, 1080] or frame_count != math.ceil(duration * 30):
        raise ValueError('Cycle preview failed native sequential decoding')
    preview = {'kind': 'sable-cycle-preview', 'cycleInputs': expected, 'clip': clip,
               'atlas': w.binding(atlas_path), 'contact': w.binding(contact_path),
               'video': w.binding(movie), 'nativeVideo': native, 'cycles': frame_count / 30 * speed / stride,
               'durationSeconds': frame_count / 30, 'framesDecoded': frame_count,
               'visualApproval': False, 'gameRuntimeApproval': False}
    preview_path = out / 'cycle-preview.json'
    w.write(preview_path, preview)
    packet = {'kind': 'sable-cycle-observation', 'character': character, 'direction': direction,
              'action': action, 'inputs': expected, 'preview': w.binding(preview_path),
              'decision': 'unreviewed', 'reviewer': '', 'legMarkers': {'left': '', 'right': ''},
              'frames': [dict(index=p['index'], phase=p['name'], support=None,
                              landmarks={side + part: None for side in ('left', 'right') for part in ('Hip', 'Knee', 'Sole')}) for p in contract.PHASES],
              'observations': {name: {'decision': 'unreviewed', 'seconds': [], 'notes': ''} for name in cycle_review.OBSERVATIONS}}
    packet_path = out / 'cycle-observations.json'
    w.write(packet_path, packet)
    # Canvas avoids browser-specific native video decoder crashes. It presents
    # the same actual atlas at recipe speed; the encoded evidence stays intact.
    (out/'cycle-live-review.js').write_bytes(Path(__file__).with_name('cycle_live_review.js').read_bytes())
    html = out / 'cycle-review.html'
    html.write_text('<!doctype html><meta charset="utf-8"><title>Cycle review '+character+' '+direction+'</title>'
                   '<style>body{margin:0;background:#101e27;color:#dce9e4;font:20px sans-serif}canvas{display:block;width:1920px;height:1080px}img{display:block}button{font:20px sans-serif;padding:10px}</style>'
                   '<h1>'+character.upper()+' '+direction+' '+action+' — UNREVIEWED</h1>'
                   '<button disabled>1배속으로 세 주기 관찰·기록</button> <span id="status">원화 로딩 중</span>'
                   '<canvas width="1920" height="1080"></canvas>'
                   '<p><a href="'+movie.name+'">Native encoded evidence video</a> · Playback trace is not art approval.</p>'
                   '<script type="module" src="./cycle-live-review.js"></script>'
                   '<img alt="Chronological six-phase source sheet" src="'+contact_path.relative_to(out).as_posix()+'">', encoding='utf-8')
    return {'status': 'UNREVIEWED_CYCLE_KIT', 'packet': str(packet_path), 'preview': str(preview_path),
            'html': str(html), 'video': str(movie), 'inputSHA256': cycle_review.signature(expected)}

```

## FILE: motion_lab_v1/cycle_live_review.js
SHA256: a03d201fc18f406607f638592d6f0fd79ae41f6d5104e7cbc8589ae6f98c5c18

```text
// Owned source-cycle review surface. Native unwarped atlas cells, 1x only.
// A playback trace documents presentation, never an anatomical approval.
const preview=await fetch('./cycle-preview.json',{cache:'no-store'}).then(r=>r.json());
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d',{alpha:false});
const label=document.querySelector('#status'),button=document.querySelector('button');
const image=new Image();image.src='./public/'+preview.clip.image;await image.decode();
const recipe=preview.cycleInputs.recipeValues,clip=preview.clip;
const speed=recipe.speed,stride=recipe.stride,height=recipe.heightMetres;
const direction=['E','SE','S','SW','W','NW','N','NE'].indexOf(preview.cycleInputs.direction)*Math.PI/4;
const frameAt=phase=>{for(let i=5;i>=0;i--)if(phase>=clip.phaseStarts[i])return i;return 0;};
function draw(t){
  const phase=(t*speed/stride)%1,index=frameAt(phase),[cw,ch]=clip.cell;
  ctx.fillStyle='#101e27';ctx.fillRect(0,0,1920,1080);
  ctx.fillStyle='#e4ece9';ctx.font='20px sans-serif';
  ctx.fillText(`${preview.cycleInputs.character} · ${preview.cycleInputs.direction} · 1x · ${t.toFixed(3)}s · frame ${index}`,28,34);
  ctx.fillText('SOURCE-CYCLE OBSERVATION — not game-runtime / art approval',28,68);
  ctx.drawImage(image,index%3*cw,Math.floor(index/3)*ch,cw,ch,30,170,cw,ch);
  ctx.strokeStyle='#72897e';ctx.beginPath();ctx.moveTo(30,170+clip.root[1]);ctx.lineTo(798,170+clip.root[1]);ctx.stroke();
  const ratio=270/clip.height,dx=t*speed*270/height*Math.cos(direction),dy=t*speed*270/height*.5*Math.sin(direction);
  ctx.strokeStyle='#2b4349';ctx.beginPath();
  for(let x=880;x<1920;x+=80){const xx=880+((x-880-dx)%1040+1040)%1040;ctx.moveTo(xx,190);ctx.lineTo(xx,1000);}
  for(let y=190;y<1000;y+=60){const yy=190+((y-190-dy)%810+810)%810;ctx.moveTo(880,yy);ctx.lineTo(1910,yy);}
  ctx.stroke();ctx.drawImage(image,index%3*cw,Math.floor(index/3)*ch,cw,ch,1240,550,cw*ratio,ch*ratio);
  return {phase,index};
}
draw(0);button.disabled=false;label.textContent='원화 준비됨 · 1배속 세 주기 관찰';
button.onclick=()=>{
  button.disabled=true;const start=performance.now(),rows=[],visibility=[];
  const onVisibility=()=>visibility.push({wallSeconds:(performance.now()-start)/1000,state:document.visibilityState});
  document.addEventListener('visibilitychange',onVisibility);onVisibility();
  function tick(now){
    const t=(now-start)/1000,shown=draw(t);
    rows.push({seconds:t,phase:shown.phase,frame:shown.index,rate:1,visibility:document.visibilityState});
    label.textContent=`1x 관찰 중 · ${t.toFixed(2)} / ${preview.durationSeconds.toFixed(2)}초`;
    if(t<preview.durationSeconds){requestAnimationFrame(tick);return;}
    document.removeEventListener('visibilitychange',onVisibility);
    const trace={kind:'sable-cycle-live-observation',recordedAt:new Date().toISOString(),
      cycleInputs:preview.cycleInputs,atlas:preview.atlas,video:preview.video,nativeCanvas:[canvas.width,canvas.height],
      viewport:[innerWidth,innerHeight],devicePixelRatio,
      durationSeconds:t,rate:1,seeking:false,rows,visibility,artApproval:false};
    window.cyclePlaybackTrace=trace;
    fetch('/__qa/rifle_e_live_'+Date.now()+'.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(trace)})
      .then(r=>{if(!r.ok)throw Error('trace save failed');label.textContent='1x 재생 기록 저장 — 원화·보행 승인 아님';})
      .catch(e=>{label.textContent=String(e);});
    button.disabled=false;
  }
  requestAnimationFrame(tick);
};

```

## FILE: motion_lab_v1/tests/test_enemy_asset_provenance.py
SHA256: 2d65e1a4016845a142f6ed5bebcfcb0f6ae589e5448e8fb39f244dd2d55e9ae6

```text
"""Tiny local diagnostic inputs, not generated art or visual approvals."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import prepare_enemy_asset as prep

class EnemyProvenanceTests(unittest.TestCase):
    def setUp(self):
        folder=LAB/'qa/technical_tests';folder.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='enemy_proof_',dir=folder))
        p=patch.object(prep,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        self.source=self.root/'master.png';Image.new('RGBA',(16,24),(60,80,100,255)).save(self.source)
        self.response=self.root/'response.json'
        self.returned=str(self.root/'managed-original.png')
        self.proof={'tool':'image_gen.imagegen','returnedPath':self.returned,
                    'result':{'output_hint':'Generated image saved to '+self.returned},
                    'projectCopy':'master.png','projectCopySHA256':prep.sha(self.source)}
    def check(self):
        self.response.write_text(json.dumps(self.proof),encoding='utf-8')
        return prep.verify_source(self.source,self.response)
    def test_exact_retained_copy_survives_absent_managed_staging(self):
        self.check()
    def test_metadata_name_alone_does_not_prove_art(self):
        del self.proof['projectCopy']
        with self.assertRaisesRegex(ValueError,'exact project copy'):self.check()
    def test_source_tamper_rejected(self):
        self.source.write_bytes(b'changed fixture')
        with self.assertRaisesRegex(ValueError,'hash'):self.check()
    def test_other_tool_file_cannot_substitute(self):
        self.proof['result']['output_hint']='Saved another file.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_returned_path_requires_exact_output_path(self):
        self.proof['result']['output_hint']=self.returned+'.other.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_identifier_cannot_escape_qa(self):
        with self.assertRaisesRegex(ValueError,'asset id'):
            prep.prepare('../../runtime',self.source,self.response)

    def test_quoted_longer_path_is_not_the_returned_file(self):
        for quote in ['\"',"'",'`']:
            for suffix in [' other.png','. other.png']:
                self.proof['result']['output_hint']=f'Saved to {quote}{self.returned}{suffix}{quote}'
                with self.assertRaisesRegex(ValueError,'metadata'):self.check()

    def test_exact_path_with_spaces_remains_supported(self):
        self.proof['returnedPath']=str(self.root/'actual image with spaces.png')
        for hint in [f'Saved to "{self.proof["returnedPath"]}"',
                     f'Generated images are saved to {self.root} as {self.proof["returnedPath"]} by default.\nNext instruction.']:
            self.proof['result']['output_hint']=hint;self.check()

    def test_matte_code_change_preserves_previous_preparation(self):
        # Real prepare() and real deterministic key_image, synthetic art only.
        Image.new('RGBA',(1024,1024),(60,80,100,254)).save(self.source)
        self.proof['projectCopySHA256']=prep.sha(self.source);self.check()
        matte=self.root/'build_atlas.py';matte.write_text('technical dependency version 1')
        (self.root/'source_provenance.py').write_text('technical dependency fingerprint')
        prep.prepare('fixture',self.source,self.response)
        first=next((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        first_hash=prep.sha(first)
        matte.write_text('technical dependency version 2')
        prep.prepare('fixture',self.source,self.response)
        reports=list((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        self.assertEqual(len(reports),2);self.assertEqual(prep.sha(first),first_hash)

```

## FILE: motion_lab_v1/tests/test_reuse_improvements.py
SHA256: 577d54e758d1ae230269d04e41def39aec122d256effe69ee5eb5f8d57339a43

```text
"""Local technical fixtures only. No game art, providers, or model runs."""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import compact_atlas as atlas
import improvement_harness as harness
import character_handoff as handoff
import character_workflow as workflow

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')

def fixture_root(prefix):
    parent = LAB / 'qa/technical_tests'
    parent.mkdir(parents=True, exist_ok=True)
    # Keep owned fixtures and failed evidence; never recursively clean user data.
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.root = fixture_root('lossless_')
        self.desc_path = self.root / 'descriptor.json'
        self.output = self.root / 'motion_lab_v1/qa/candidate'
        desc = {'cell_size': 4, 'display_scale': .5, 'display_offset': [0, -4],
                'states': {'idle': {'frames': 1, 'fps': 1}, 'move': {'frames': 4, 'fps': 24},
                           'fire': {'frames': 2, 'fps': 12}}, 'directions': {}}
        for direction in atlas.DIRECTIONS:
            row = {'muzzle_xy': [3, 1]}
            for state, spec in desc['states'].items():
                path = self.root / direction / (state + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new('RGBA', (4, 4 * spec['frames']))
                for index in range(spec['frames']):
                    # Two visually transparent but byte-distinct cells catch
                    # accidental hidden-RGB normalization and false deduplication.
                    cell = Image.new('RGBA', (4, 4), (20 + 20 * (index % 2), 80, 120, 0))
                    image.paste(cell, (0, index * 4))
                image.save(path)
                row[state + '_atlas'] = path.relative_to(self.root).as_posix()
            desc['directions'][direction] = row
        save(self.desc_path, desc)

    def build(self):
        result = atlas.pack(self.root, self.desc_path, self.output)
        return Path(result['manifest'])

    def test_preserves_all_slots_and_hidden_rgba(self):
        path = self.build()
        result = atlas.verify(self.root, path)
        self.assertEqual(result['rgba_exact_timing_cells'], 56)
        self.assertTrue(result['timing_unchanged'])
        self.assertFalse(result['production_approved'])
        manifest = atlas.read(path)
        self.assertEqual(manifest['directions']['E']['unique_cells'], 2)
        frames = manifest['directions']['E']['states']['move']
        self.assertEqual(len(frames), 4)
        self.assertAlmostEqual(sum(f['duration_seconds'] for f in frames), 4 / 24)
        self.assertEqual(frames[0]['x'], frames[2]['x'])

    def test_changed_duration_or_order_or_offset_fails(self):
        path = self.build()
        original = atlas.read(path)
        for mutate in (
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=.5),
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=math.nan),
            lambda m: m['directions']['E']['states']['move'][0].update(source_frame=1),
            lambda m: m['directions']['E']['states']['move'][0].update(x=999),
            lambda m: m['directions']['E']['states']['move'].pop(),
            lambda m: m.update(display_offset=[0, 0]),
        ):
            broken = copy.deepcopy(original)
            mutate(broken)
            save(path, broken)
            with self.assertRaises(ValueError):
                atlas.verify(self.root, path)

    def test_resealed_pixel_corruption_still_fails_against_original(self):
        path = self.build()
        manifest = atlas.read(path)
        page = self.root / manifest['directions']['E']['texture']
        image = atlas.rgba(page)
        image.putpixel((0, 0), (1, 2, 3, 0))
        image.save(page)
        manifest['directions']['E']['sha256'] = atlas.sha(page)
        save(path, manifest)
        with self.assertRaisesRegex(ValueError, 'RGBA differs'):
            atlas.verify(self.root, path)

    def test_source_change_is_not_accepted_from_old_checks(self):
        path = self.build()
        source = self.root / 'E/move.png'
        Image.new('RGBA', (4, 16), (200, 0, 0, 255)).save(source)
        with self.assertRaisesRegex(ValueError, 'Original texture changed'):
            atlas.verify(self.root, path)

    def test_rgb_without_real_alpha_is_not_silently_converted(self):
        source = self.root / 'E/idle.png'
        Image.new('RGB', (4, 4), (0, 255, 0)).save(source)
        with self.assertRaisesRegex(ValueError, 'actual RGBA'):
            self.build()

    def test_no_overwrite_or_output_escape(self):
        path = self.build()
        before = atlas.sha(path)
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(atlas.sha(path), before)
        with self.assertRaises(ValueError):
            atlas.pack(self.root, self.desc_path, self.root / 'production')
        self.assertFalse((self.root / 'production').exists())

class PerformanceTests(unittest.TestCase):
    def rows(self):
        row = {'p95_ms': 6.424, 'p99_ms': 19.714, 'squad_count': 3, 'end_hostiles': 3}
        return [dict(row) for _ in range(3)]

    def test_r3_relative_failure_cannot_be_rounded_to_pass(self):
        baseline, candidate = self.rows(), self.rows()
        for row in candidate:
            row['p95_ms'] = 7.106
        result = harness.evaluate_performance(baseline, candidate)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(result['absolute_budget_met'])
        self.assertFalse(result['relative_budget_met'])

    def test_valid_within_budget_data_can_pass(self):
        self.assertEqual(harness.evaluate_performance(self.rows(), self.rows())['status'], 'PASS')

    def test_missing_repeat_invalid_number_and_population_fail(self):
        for mutate in (lambda r: r.pop(), lambda r: r[0].update(p95_ms=float('nan')),
                       lambda r: r[0].update(p99_ms=float('inf')), lambda r: r[0].update(p95_ms=True),
                       lambda r: r[0].update(end_hostiles=2), lambda r: r[0].update(p99_ms=1)):
            candidate = self.rows()
            mutate(candidate)
            with self.assertRaises(ValueError):
                harness.evaluate_performance(self.rows(), candidate)

    def test_empty_and_stale_input_binding_fails(self):
        root = fixture_root('binding_')
        path = root / 'file.txt'
        path.write_text('fixture', encoding='utf-8')
        values = {'file.txt': atlas.sha(path)}
        harness.check_bindings(root, values)
        path.write_text('changed', encoding='utf-8')
        for value in ({}, values, {'../outside': 'invalid'}):
            with self.assertRaises(ValueError):
                harness.check_bindings(root, value)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.project = fixture_root('handoff_')
        self.lab = self.project / 'motion_lab_v1'
        self.lab.mkdir()
        self.patch = patch.object(workflow, 'ROOT', self.lab)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name in handoff.CORE + ('AGENTS.md',):
            path = self.lab / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical file fixture only', encoding='utf-8')
        for name in handoff.REFERENCES:
            path = self.project / '.agents/skills/sable-character-studio' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical instruction fixture only', encoding='utf-8')
        reference = self.lab / 'art/fixture/identity_reference.png'
        reference.parent.mkdir(parents=True)
        reference.write_bytes(b'not image generation: identity hash fixture')
        self.config = {'id': 'fixture', 'name': 'Technical fixture', 'source': 'art/fixture',
                       'heightMetres': 1.72, 'locomotion': {'walkSpeed': 1.35, 'walkStride': 1.6},
                       'workflowVersion': 1, 'identityReference': 'art/fixture/identity_reference.png',
                       'referenceSHA256': atlas.sha(reference), 'clips': {'walk': {'frames': 6}, 'idle': {'frames': 1}}}
        save(self.lab / 'characters/fixture.json', self.config)
        self.packet_path = self.lab / 'qa/handoff.json'

    def packet(self):
        packet = handoff.make('fixture')
        save(self.packet_path, packet)
        return packet

    def test_packet_has_real_next_slot_not_generation_success(self):
        packet = self.packet()
        self.assertEqual(packet['status'], 'READY_TO_RESUME')
        self.assertEqual(packet['nextSource']['slot'], 'E/idle/0')
        self.assertFalse(packet['lunaGenerationTested'])
        self.assertFalse(packet['reviewedDelivery'])
        self.assertEqual(handoff.verify(str(self.packet_path))['status'], 'CURRENT_HANDOFF')

    def test_code_change_invalidates_packet(self):
        self.packet()
        (self.lab / 'public/atlas-renderer.js').write_text('changed fixture', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_new_missing_source_invalidates_packet(self):
        self.packet()
        (self.lab / 'art/fixture/E_walk_0_master.png').write_bytes(b'new test bytes')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_aim_latency_instruction_change_invalidates_packet(self):
        self.packet()
        path=self.project / '.agents/skills/sable-character-studio/references/aim-response.md'
        path.write_text('Changed aim latency constraint fixture',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_runtime_texture_change_invalidates_packet(self):
        texture = self.lab / 'public/assets/atlas/fixture/E_walk.webp'
        texture.parent.mkdir(parents=True)
        texture.write_bytes(b'non-art texture fixture')
        save(texture.parent / 'profile.json', {'id': 'fixture', 'animation': {'presentation': 'authored_frames'},
             'views': {'E': {'walk': {'image': 'assets/atlas/fixture/E_walk.webp', 'sources': []}}}})
        self.packet()
        texture.write_bytes(b'changed texture fixture')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_changed_claim_or_instruction_is_rejected(self):
        original = self.packet()
        for update in ({'reviewedDelivery': True}, {'lunaGenerationTested': True}, {'nextAction': 'DEPLOY_NOW'}):
            packet = copy.deepcopy(original)
            packet.update(update)
            save(self.packet_path, packet)
            with self.assertRaisesRegex(ValueError, 'instructions or conclusions'):
                handoff.verify(str(self.packet_path))

    def test_known_repair_precedes_missing_pilot_slot(self):
        source = self.lab / 'art/fixture/E_walk_0_master.png'
        Image.new('RGBA',(16,24),(90,110,130,255)).save(source)
        master=source.with_name('technical_original.png');master.write_bytes(source.read_bytes())
        proof = self.lab / 'qa/proof.json'
        returned=str(self.lab/'technical_returned.png')
        save(proof, {'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test, not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.lab)),'projectCopySHA256':atlas.sha(master)})
        save(source.with_suffix('.source.json'), {'testFixture': True, 'generator': 'Codex built-in ImageGen',
             'sha256': atlas.sha(source), 'toolResponse': workflow.binding(proof),'sourceMaster':workflow.binding(master),'destination':str(source.relative_to(self.lab))})
        workflow.review_source('fixture', 'E/walk/0', 'repair', str(source),
                               'Technical negative fixture, not actual art review', 'unit-test')
        packet = self.packet()
        self.assertEqual(packet['nextAction'], 'REPAIR_REPORTED_SOURCE')
        self.assertEqual(packet['nextSource']['slot'], 'E/walk/0')

    def test_runtime_rejection_is_the_next_action_not_a_rebuild(self):
        save(self.lab/'qa/fixture/runtime_reviews.json',[{'decision':'repair','notes':'Synthetic rejected gait fixture'}])
        packet=self.packet()
        self.assertEqual(packet['nextAction'],'REPAIR_RUNTIME_VISUAL')
        self.assertTrue(packet['sourceStatus']['runtimeRepairRequired'])
        self.assertFalse(packet['sourceStatus']['ready'])

    def test_pose_guide_and_request_change_invalidate_handoff(self):
        guide=self.lab/'reference/guide.png';guide.parent.mkdir(parents=True);guide.write_bytes(b'technical pose guide fixture')
        save(self.lab/'art/fixture/requests.json',[{'poseGuide':'reference/guide.png'}])
        self.packet();guide.write_bytes(b'changed guide fixture')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

if __name__ == '__main__':
    unittest.main()

```

## FILE: motion_lab_v1/build_atlas.py
SHA256: 1395b21aa409e4605ce769479e9984968f0a88912adda648879b6869d2dd527f

```text
"""Deterministic, model-free RGBA/atlas compiler for authored ImageGen frames."""
from pathlib import Path
import json,hashlib
import numpy as np
import cv2
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def key_image(path):
    im=Image.open(path)
    if im.mode=='RGBA' and im.getextrema()[3][0]<255:
        rgba=np.array(im);rgba[rgba[:,:,3]==0,:3]=0
        return rgba
    rgb=np.array(im.convert('RGB'));f=rgb.astype(np.float32)
    excess=f[:,:,1]-np.maximum(f[:,:,0],f[:,:,2])
    alpha=np.clip(1-(excess-8)/38,0,1)
    alpha[(excess>65)&(f[:,:,1]>85)]=0
    f[:,:,1]=np.where(alpha<.98,np.minimum(f[:,:,1],np.maximum(f[:,:,0],f[:,:,2])+4),f[:,:,1])
    f[alpha==0]=0
    return np.dstack((f,alpha*255)).astype(np.uint8)

def subjects(path,count):
    """Separate complete figures even when a rifle crosses a sheet-cell border."""
    rgba=key_image(path)
    n,labels,stats,_=cv2.connectedComponentsWithStats((rgba[:,:,3]>30).astype(np.uint8))
    components=sorted(range(1,n),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]),reverse=True)[:count]
    if len(components)!=count or min(stats[i,cv2.CC_STAT_AREA] for i in components)<10000:
        raise ValueError(f'{path}: expected {count} separate complete figures')
    components.sort(key=lambda i:int(stats[i,cv2.CC_STAT_LEFT]))
    result=[]
    for i in components:
        x,y,w,h,area=map(int,stats[i]);mask=(labels==i).astype(np.uint8)
        mask=cv2.dilate(mask,np.ones((3,3),np.uint8))
        separated=rgba.copy();separated[mask==0]=0
        box=[max(0,x-12),max(0,y-12),min(rgba.shape[1],x+w+12),min(rgba.shape[0],y+h+12)]
        result.append((Image.fromarray(separated[box[1]:box[3],box[0]:box[2]]),box))
    return result

def register(path,config,direction,annotation):
    raw=key_image(path);ys,xs=np.where(raw[:,:,3]>200)
    if not len(xs):raise ValueError(f'{path}: no opaque subject')
    x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    scale=height/(y1-y0)
    anchor=annotation.get('hipX')
    if anchor is None:
        region=raw[int(y0+(y1-y0)*.39):int(y0+(y1-y0)*.47),:,3]
        valid=np.where((region>200).sum(axis=0)>region.shape[0]*.7)[0]
        anchor=float(np.median(valid))
    matrix=np.float32([[scale,0,root[0]-anchor*scale],[0,scale,root[1]-y1*scale]])
    corners=np.array([[x0,y0,1],[x1,y1,1]])@matrix.T
    if np.any(corners[0]<4) or corners[1,0]>cell[0]-4 or corners[1,1]>cell[1]-4:
        raise ValueError(f'{path}: cell too small / hip anchor invalid; bounds={corners.tolist()}')
    out=cv2.warpAffine(raw,matrix,tuple(cell),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
    if 'muzzle' in annotation:
        muzzle=(matrix@np.array([*annotation['muzzle'],1])).tolist()
    else:
        band=raw[y0:int(y0+(y1-y0)*.45),:,3];yy,xx=np.where(band>210);yy+=y0
        if direction in ['W','SW','NW']:
            edge=xx.min();choose=xx<=edge+3
        elif direction=='N':
            edge=yy.min();choose=yy<=edge+3
        elif direction=='S':
            choose=np.zeros_like(xx,dtype=bool)
            choose[np.argmin(abs(xx-anchor)+abs(yy-(y0+(y1-y0)*.32)))]=True
        else:
            edge=xx.max();choose=xx>=edge-3
        muzzle=(matrix@np.array([float(np.median(xx[choose])),float(np.median(yy[choose])),1])).tolist()
    green=(out[:,:,1].astype(int)-np.maximum(out[:,:,0],out[:,:,2]).astype(int)>45)&(out[:,:,3]>128)
    with Image.open(path) as native_image:native_size=list(native_image.size)
    note={'source':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'native':native_size,
          'bounds':[x0,y0,x1,y1],'hipX':anchor,'scale':scale,'matrix':matrix.tolist(),'muzzle':muzzle,
          'opaqueGreenPixels':int(green.sum()),'alphaBounds':corners.tolist()}
    return out,note

def build(config,direction,action,paths,annotations,output_root=None):
    output_root=output_root or ROOT
    ident=config['id'];out=output_root/'public/assets/atlas'/ident;out.mkdir(parents=True,exist_ok=True)
    pairs=[register(path,config,direction,annotations.get(str(i),{})) for i,path in enumerate(paths)]
    frames=[p[0] for p in pairs];notes=[p[1] for p in pairs]
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    cols=min(3,len(frames));rows=(len(frames)+cols-1)//cols;atlas=Image.new('RGBA',(cell[0]*cols,cell[1]*rows))
    for i,im in enumerate(frames):atlas.paste(Image.fromarray(im),(i%cols*cell[0],i//cols*cell[1]))
    atlas.save(out/f'{direction}_{action}.webp',lossless=True,method=5)
    preview=output_root/'reference/atlas'/ident;preview.mkdir(parents=True,exist_ok=True)
    contact=Image.new('RGB',atlas.size,(18,28,36));contact.paste(atlas,(0,0),atlas);draw=ImageDraw.Draw(contact)
    for i in range(len(frames)):
        ox=i%cols*cell[0];oy=i//cols*cell[1]
        draw.text((ox+20,oy+20),f'{direction} / {action} / {i}',fill='#b0dacc')
        draw.line((ox+20,oy+root[1],ox+cell[0]-20,oy+root[1]),fill='#35534f')
        m=notes[i]['muzzle'];draw.ellipse((ox+m[0]-4,oy+m[1]-4,ox+m[0]+4,oy+m[1]+4),outline='#ffcc70',width=2)
    contact.save(preview/f'{direction}_{action}_keyframes.png')
    anim=[]
    for im in frames:
        bg=Image.new('RGB',tuple(cell),(18,28,36));bg.paste(Image.fromarray(im),(0,0),Image.fromarray(im[:,:,3]));anim.append(bg)
    anim[0].save(preview/f'{direction}_{action}.gif',save_all=True,append_images=anim[1:],duration=round(1200/len(frames)),loop=0)
    record={'image':f'assets/atlas/{ident}/{direction}_{action}.webp','cell':cell,'columns':cols,'frames':len(frames),
            'root':root,'height':height,'authoredFrames':len(frames),'muzzles':[n['muzzle'] for n in notes],'sources':notes}
    (out/f'{direction}_{action}.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'direction':direction,'action':action,'frames':len(frames)}),flush=True)
    return record

```
