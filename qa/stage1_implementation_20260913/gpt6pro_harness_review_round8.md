# Round 8: new changes only; do not reopen closed R6 cases without a new counterexample

The user asks whether GPT review and actual harness/skill repair continue in
parallel with asset production. We accurately reported that round7 closed the
three R6 counterexamples, and these newer changes had not yet had external review.

Please independently review these two bounded changes in Korean:

1. Source anatomy review: the user rejected SE/walk/3 because the two visible
boots had a third knee/shin branch. We had recorded `repair`, kept the raw,
derived art and evidence in quarantine, and generated a new source using the
exact guide first plus original identity only (removed a competing full-body
posture reference). The new source was visually inspected on native light/dark
panels and source-approved, NOT user-approved or whole-cycle/app-approved.
The two attached PNGs are the actual before/after native lower-body panels.
The extra skill text requires tracing two complete hip-knee-ankle-boot chains,
using the right-only holster as a side marker; two boots alone are not proof.
The source-review helper preserves protected pixels and creates matte panels;
it does NOT perform automatic limb recognition. Is the correction well scoped,
or does it still imply a false automatic art/temporal approval? Flag concrete
anatomy problems in the supplied replacement too. Do not claim to have watched
an unattached video. Source completeness is currently 13/56; only E cycle has
approval. SE cycle review and SE idle generation are underway, not delivered.

2. Normal app connection of the fixed boss (drone app binding also now active):
machine body stationary, central purple iris emission, original three-phase
Tactics attacks. No independently yawing/firing four arms. App normal-path
smokes actually passed locally: drone 170, anchor 271. Source smoke now has
436 checks (48 new full-art health-bar corner checks under transforms).
The machine overhead bar uses full transformed art corners instead of inset
damage bounds. Controlled native boss captures use the actual home position
because its anchor component undoes arbitrary relocation; offscreen first
capture remains VISUAL_HOLD. New 22 captures pass native1920x1080 decoding,
three representative phase captures were actually observed. The capture uses
HP/attack-serial fixtures and is not a whole-operation playthrough. A separate
actual-logic full operation test passed without infiniteHP/ammo/deleting living
enemies; human difficulty is not certified. Short headless smokes still report
ObjectDB shutdown warnings; no false claim that this is fixed.

Read the attached exact current source blocks. Report only concrete bugs,
meaningful missing negative tests, or contradictory instructions in these new
changes, with file/function and smallest correction. Distinguish your actual
execution/static review/image observation and local reported test results.
Do not expand this into a new framework, automatic artistic approval, full
Stage1/MVP completion, or a claimed Luna reproduction. Accepted player art,
gait, 1.8x map scale and weapon timings are untouched. The mobile humanoids
remain unconnected until complete approved cycles and runtime review exist.

## FILE: .agents/skills/sable-character-studio/SKILL.md
SHA256: 1648d74418e895a0ab9615c65f53e0840372238d3a4999a75ecb4554ff4978c1
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
- **SITE-7 enemy front/weapon faces away from its target:** read
  [the enemy-facing repair](references/enemy-facing.md). Flying directional
  artwork, anchored emitters and telegraph-locked AI are separate from biped
  gait and the player's latest-pointer response.
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
SHA256: fa39874d9020cb5d4d5f10a7d601ecdb37a391195e7058a2533bb77b1a099774
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
   For a biped, trace each hip -> knee -> ankle -> boot on the native lower-body
   light/dark panels. Two visible boots are insufficient: the rejected SITE-7
   SE/walk/3 had two boots but a third knee/shin branch. Use asymmetric costume
   markers (this rifle trooper's right-only holster) to track anatomical sides,
   including occlusion, rather than treating screen left as anatomical left.
   If a chain is ambiguous, record `repair`; do not explain it away from the
   prompt. A conflicting full-body posture reference caused trouble in this
   attempt; guide-first plus the identity reference yielded a clean replacement.
   That is a tested prompt adjustment, not a guarantee of subsequent anatomy.
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

## FILE: .agents/skills/sable-character-studio/references/enemy-facing.md
SHA256: bcb67f0fcb33b194a88f63bb654793635b456f3bc877f07786d62cb1977544e4
```text
# SITE-7 enemy facing: visible front, emitter and warning

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

`tests/render/site7_machine_edge_case_smoke.gd` checks the R6 close-target,
metadata-only/hidden-RGB duplicate and interrupted-warning regressions. Run it
with actual rendering, not headless: the warning check reads native viewport
pixels as well as the Tactics draw signal. Synthetic PNGs are test-only.

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

```

## FILE: .agents/skills/sable-character-studio/references/cycle-review.md
SHA256: 153c2e877a05176bb9a20d1db1b6db8718513d3b8f68f497a8451197d537486b
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
Check the entire difference region, not a deterministic subset: the 4096/4160
pixel interlaced-ghost regression demonstrates why subsampling is unsafe here.
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

## FILE: motion_lab_v1/prepare_slot_review.py
SHA256: e19ddd992d0222e586e16d9eac491d55ba55c34f2c0baf9adb869ca8946fd961
```text
"""Native source-slot evidence on light/dark mattes. Never grants approval."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageDraw
from build_atlas import key_image
from character_workflow import ROOT, recipe, slots, sha, write
from source_provenance import validate_slot

def prepare(character, slot):
    source = dict(slots(recipe(character)))[slot]
    receipt = json.loads(source.with_suffix('.source.json').read_text(encoding='utf-8'))
    validate_slot(ROOT, source, receipt)
    rgba = Image.fromarray(key_image(source))
    dependencies = {p.name:sha(p) for p in [Path(__file__),ROOT/'build_atlas.py',ROOT/'source_provenance.py']}
    implementation = hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()[:8]
    signature = sha(source)[:12]+'_'+implementation
    out = ROOT/'qa'/character/'source_panels'/signature
    out.mkdir(parents=True, exist_ok=True)
    rgba.save(out/'candidate_rgba.png')
    rows = []
    for label in ['full','native_upper','native_lower']:
        board = Image.new('RGB',(1920,1080),'#15232b')
        for x, color in [(0,'#eeeeee'),(960,'#15232b')]:
            panel = Image.new('RGBA',(960,1080),color)
            im = rgba.copy()
            if label == 'full':
                im.thumbnail((930,1010),Image.Resampling.LANCZOS)
            else:
                left = max(0,(im.width-940)//2)
                top = 0 if label=='native_upper' else max(0,im.height-1010)
                im = im.crop((left,top,min(im.width,left+940),min(im.height,top+1010)))
            panel.alpha_composite(im,((960-im.width)//2,45+(1010-im.height)//2))
            board.paste(panel.convert('RGB'),(x,0))
        ImageDraw.Draw(board).text((20,14),character+' / '+slot+' / '+label+' / NOT APPROVED',fill='#bb874f')
        target = out/(label+'_1920x1080.png')
        board.save(target)
        rows.append({'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'native':[1920,1080],'source_pixel_scale':1 if label!='full' else 'fit-down-only'})
    report={'status':'PREPARED_NOT_APPROVED','source':source.relative_to(ROOT).as_posix(),'sourceSHA256':sha(source),'sourceNative':list(rgba.size),'provenanceSHA256':sha(source.with_suffix('.source.json')),'images':rows,'implementationDependencies':dependencies}
    write(out/'report.json',report)
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--slot',required=True)
    a=p.parse_args();prepare(a.character,a.slot)

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

## FILE: motion_lab_v1/qa/site7_rifle/source_reviews.json
SHA256: 2c2d7d5709bf4ff2729c2f0b249a2ae7c2673d09a183718cf79407162d0fc511
```text
[
  {
    "recordedAt": "2026-09-13T04:26:49.167484+00:00",
    "slot": "E/walk/0",
    "decision": "repair",
    "reviewer": "Codex",
    "notes": "Viewed actual source. Pose is opposite-leg contact as requested, but file is RGB with painted checkerboard, not actual alpha; source cannot be used. Preserve rejected bytes; green fallback is in progress.",
    "sourceSHA256": "3b172e832cdf32f804cb4d69a2b16f96fe0fea31e426b3a192f248dc18b16ea6",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "art/site7_rifle/E_walk_0_master.png",
      "sha256": "3b172e832cdf32f804cb4d69a2b16f96fe0fea31e426b3a192f248dc18b16ea6"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:01.866611+00:00",
    "slot": "E/idle/0",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Observed dark hood, full mask, silver segmented armor with muted red trim and shoulder-held bullpup. The native light/dark composite has clean opaque machinery/fabric and genuinely separated edges; no visible green backdrop. This is source approval only, not motion/runtime approval.",
    "sourceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "sourcePixelSHA256": "0162d00fa844d1b6e6ad9656b9fb8509dcfc7e063b3dbd7d0763f7ff8c974626",
    "sourceReceiptSHA256": "fa69b4db50020e51448228b4106e25ef6f87d5d7e13196c458662b997092856a",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_idle/7deb2c01ea66_3203b573/full_1920x1080.png",
      "sha256": "1406f7317e700827a4f4067b3a255b4a2a7047e9ac815217d763a0237cf5a50e"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:10.877123+00:00",
    "slot": "E/walk/0",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Far unholstered left leg leads into contact; near holstered right leg trails. Connected waist/knees/boots, shoulder-held horizontal bullpup and masked hood identity retained. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "e10e98d4d9e3018b8e82cf34fbf6d5c2af4b1e9106444126f936537680f5b10e",
    "sourcePixelSHA256": "2edd9f2cd8c744194f9551a37de1375663325331bccaa7fd99c41d8a07ef6bc8",
    "sourceReceiptSHA256": "6f75a96da930aeb54c299a2d46ce87d5777d95e4f3a7c363203af8ddab7a22fa",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_0.png",
      "sha256": "b68e5aed5c4c22270b100cdc8ab352dfd86019d64c26b0f605bce64295fa0545"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:19.202070+00:00",
    "slot": "E/walk/1",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Near holstered right knee bends and its boot lifts behind; far unholstered left boot supports beneath the body. Original-scale tracing confirms the two separate chains, clean silhouette and same rifle. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "29834d6a27022e3362b3172c2f5da448c57df90b4465d76e2d9e3852510632e0",
    "sourcePixelSHA256": "f91a6ba6d440d6b403617f68607450b4b0d567306c13cc11611653fcca95f29a",
    "sourceReceiptSHA256": "49af045c7c89d776a25c5b2ac9f47eee3af09b704800b154510e94b0adeeb3a4",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_1.png",
      "sha256": "f2af3743c8bb7236bf2f9518a663c8ab4b75449b09f48e4f996527e3b3aef128"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:27.829279+00:00",
    "slot": "E/walk/2",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Near holstered right knee/boot pass ahead while far unholstered left foot supports. Gun remains shouldered, silhouette is complete and alpha edges are clean on the native review panel. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "92a1e1d1742798b42f8ec796edd331f71f8f80387ac8b6bdcabdd6f8364360cd",
    "sourcePixelSHA256": "f660c413c35487f5f0631634b8d6d3a9c6920c75f161e75994e79dc40851212c",
    "sourceReceiptSHA256": "1c7e03180416a47fbea15851fe44fae59a9b820e1f35d33ad29c9e8f7d7c358e",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_2.png",
      "sha256": "b97b155033ef4290a988c6007b491bda55691d5a9e4ae19925f18bf559f99307"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:36.650957+00:00",
    "slot": "E/walk/3",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Near holstered right boot now leads into contact and far left leg trails; this is the opposite actual anatomical lead from frame0. Same armor/hood/weapon identity and connected body. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "3a0b16487aa4b7334f396598f230902529a38b880ddf43dca58272d5883299c8",
    "sourcePixelSHA256": "b0c9964f2c618f73cfe96ca73a4e4f40711fb88f99f9d9bbaa9d238e37ec9fac",
    "sourceReceiptSHA256": "91763eb6ef9adf8977ef67663d84319c57fc37b53e8bb4268832c75aaf0c00db",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_3.png",
      "sha256": "cefab934547ed3727874b74adfcc346283938e15eb625b69bb870560036b9409"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:45.514463+00:00",
    "slot": "E/walk/4",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Far unholstered left boot swings behind the planted near holstered right leg. Selected right figure from the retained pair, not the rejected left figure. Whole subject is unwarped and preserves the authored gun and armor. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "46276e65843a6fa80032139e785622ac67b6e10dbb3d9819a8690f95e1ed5755",
    "sourcePixelSHA256": "1be74fd3d28eb51148d6eba8c250eedb00c00caf5fe23060cc81208eb752a44b",
    "sourceReceiptSHA256": "50cb20deaeefc06f67b93e3dfcf75c0b226e1ebcadaf6338b8833eb6e2737931",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_4.png",
      "sha256": "16ae3b01c026dc9e7ea395f3230da244c6bc189cf141786fa78791ad52d4b6c1"
    }
  },
  {
    "recordedAt": "2026-09-13T07:28:53.284083+00:00",
    "slot": "E/walk/5",
    "decision": "approved",
    "reviewer": "Codex main - observed native source review 2026-09-13",
    "notes": "Far left knee/boot pass forward; near holstered right boot stays the support. The earlier repeated-right-support pair was not reused for the opposite phase. Clean body/weapon connection and alpha observed. Source only; six-frame temporal limits and the actual cycle are reviewed separately.",
    "sourceSHA256": "d9b98cb5d83f2b5929d8d5baf29d0e6f8db2c9f48fcb088317cca1ae4af29cca",
    "sourcePixelSHA256": "6f0ae29a29b60735613c8e83ed2592753ddb26e44affce6fbb7d3a03ea7e43bc",
    "sourceReceiptSHA256": "99a70eed6771a12a02e211a308c2577c248c8acb3e6e1165e975c291068735bd",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/stage1_enemies_20260913/rifle_e_annotation_review_v3/frame_5.png",
      "sha256": "1543fb74c34bfd3ec83bd3ee07e06e56a77dd013928472a15f5e1e770ff77dbb"
    }
  },
  {
    "recordedAt": "2026-09-13T08:07:55.214969+00:00",
    "slot": "SE/walk/0",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Viewed raw guide and identity, full source and native upper/lower light-dark panels. Front-right three-quarter view, rifle perspective points lower-right; black hood/visor, scratched silver dark-red armor and radio retained. Anatomical left unholstered leg leads; anatomical right holstered leg trails with raised heel; two complete connected legs. Stock shouldered, right grip and left support hand visible. Real keyed RGBA has no checkerboard/green at inspected hands, weapon, boots and cloth edges. Source-slot acceptance only; temporal gait and floor contacts require complete SE cycle observation.",
    "sourceSHA256": "81f9195d21d7ac3624a16b7d8c0ad248f6cf7b46b015441085f0f467905bcb23",
    "sourcePixelSHA256": "49094085708e5ddf72da613dc7af90fd8d4cd3a1ff27336f0d51c5bf69a437d5",
    "sourceReceiptSHA256": "6b970a7c68a55778cec1e35209c163b01039856d7a606180567af33bdf3d6695",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/81f9195d21d7_8ad17e3b/native_lower_1920x1080.png",
      "sha256": "24125414ab22eb7963e28d8bf6ae554752c802c8324cb1f74caf385b2213d81a"
    }
  },
  {
    "recordedAt": "2026-09-13T08:18:00.586100+00:00",
    "slot": "SE/walk/1",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Observed guide, generated whole frame and native upper/lower panels on both mattes. Anatomical left unholstered leg supports under body; holstered right thigh leads into a knee folded backward and lifted boot, distinct from SE0 stretched contact. Two connected anatomical limbs, consistent black hood/mask, silver-red armor, radio, bullpup optic and hands. Entire boots and weapon remain inside source. No checkerboard or remaining green on inspected subject edges. Individual pose only; phase timing, actual support drift and pelvis motion remain subject to complete SE cycle review.",
    "sourceSHA256": "e186478b036ecdcf630493d597472f44134bbc45786fbadac02f24dc6a3d1bd9",
    "sourcePixelSHA256": "855740ddb476f6e7121d6f0ecb0018cadf6601be73fc2ffd7080476729796a94",
    "sourceReceiptSHA256": "fc6768f96cfe63860d1962ff5a6e5e9d60fcf050c25a0c27cd4439de38349812",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/e186478b036e_3f539202/native_lower_1920x1080.png",
      "sha256": "ab563728f52113c1a641a1eef6252b6ac91459c7fb79873983e34078f741cd95"
    }
  },
  {
    "recordedAt": "2026-09-13T08:27:03.468427+00:00",
    "slot": "SE/walk/2",
    "decision": "repair",
    "reviewer": "current main implementation agent",
    "notes": "Observed right-only holster connects to foreground leg whose shin extends down-forward and whose boot reads planted ahead. The unholstered left boot is raised behind. This reverses the requested left-support/right-forward-swing passing pose in SE_Walk_Loop_2 and would introduce an early support swap. REJECT pose, preserve original and derivatives; do not reinterpret prompt anatomy as observed anatomy.",
    "sourceSHA256": "6a4a8e08bb8aedce33c84e2f9e5a813784fcbdf33473ccae76357f9dd5aa2fe4",
    "sourcePixelSHA256": "97e572e48b995fdefe9fc96c0598eed5cb46817fbc855b34f7376035addc1687",
    "sourceReceiptSHA256": "3188f3f228905a4d546db12c56a9adc33b84eea66120ff2ba8e2462a023547d3",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/6a4a8e08bb8a_3f539202/native_lower_1920x1080.png",
      "sha256": "fbd0d9e0448aa3d3c764aee94d764a65ae8c7cc5f403ccbf1291d3c9de46646b"
    }
  },
  {
    "recordedAt": "2026-09-13T08:33:48.761971+00:00",
    "slot": "SE/walk/2",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Observed original-scale upper/lower panels on light and dark. Foreground holstered RIGHT thigh leads to bent forward knee, shin returns down-left, boot lifted above the unholstered LEFT supporting boot. Left shin/boot visible behind; tight passing occlusion follows SE guide and differs from rejected v1 early right support. Hood, red/silver armor, radio, right-only holster, two-handed shouldered bullpup and clean alpha preserved. Source-pose approval only; compact boot overlap and temporal contact/slide must still be judged in the complete SE cycle, not from this static frame.",
    "sourceSHA256": "3a7dc59adc9c0fedc9920fdcd1ae2740251e82075a333e6a7c6ec8f2592f980e",
    "sourcePixelSHA256": "4352955a7c7ae04895dc39390c4ba19722035c6d88691a0536be3a7083f110f5",
    "sourceReceiptSHA256": "0814f0ecb20c93b41fac4541b6656b1930d5d75f5628cfd5b5bb033e024bda95",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/3a7dc59adc9c_3f539202/native_lower_1920x1080.png",
      "sha256": "d91a1df363b859b60c16441aa96131e1098f94ec1e2e4131da6925be9e598bb1"
    }
  },
  {
    "recordedAt": "2026-09-13T08:40:42.496987+00:00",
    "slot": "SE/walk/3",
    "decision": "repair",
    "reviewer": "current main implementation agent",
    "notes": "Observed native lower panel. Right holstered foreground leg reaches the front boot, but the left leg has an extra far-right knee/shin silhouette while a separate calf emerges toward the rear-left boot. I cannot trace one continuous left hip-knee-shin-boot chain compatible with the supplied guide. Reject ambiguous/branched leg geometry instead of approving two boots as proof of two connected legs. Next attempt removes the competing SE0 full-body posture reference and uses exact guide plus original identity only.",
    "sourceSHA256": "9df8e882aa9ff1b074ab4a517a6b32f210c80408a94c9ee84507f2ed7cfc94be",
    "sourcePixelSHA256": "845dd491dfd3ff57c294c11ff225c0f4b890fc5593c85308baebb5909ce05559",
    "sourceReceiptSHA256": "74a0cad068b1f98e3842c59b779201b38f424e37e0f27baba9a8f1cf41643726",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/9df8e882aa9f_3f539202/native_lower_1920x1080.png",
      "sha256": "59294ff80ac2a4fbf9950ab6aec077e6f7abe92eef37983dd1842913a6f85a21"
    }
  },
  {
    "recordedAt": "2026-09-13T08:49:16.946293+00:00",
    "slot": "SE/walk/3",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Viewed actual new raw and native upper/lower light-dark panels. Exactly two leg chains: foreground right-only holster/thigh to one forward knee, shin and contacting right boot; occluded left thigh leads to one rear-left knee/calf and raised-heel left boot. The extra far-right knee/shin silhouette from user-rejected v1 is absent. No fused/third limb observed in either matte. Identity, hood, scratched silver/red armor, radio and two-hand shouldered bullpup maintained; muzzle holes/background cleanly keyed. Source-level replacement approval only, not user approval or complete-cycle/runtime approval; existing rejected bytes stay quarantined.",
    "sourceSHA256": "a750392e7a26edb06f69cb5a4fd789302e96e2b7960e44f5bcc89d57dcb4cea5",
    "sourcePixelSHA256": "2f46088db38b726d07dea3fd43c6421fe008548041b534c312dc9d983116ede3",
    "sourceReceiptSHA256": "10056fd0f7e61de0c84bfd02ae5871ebb479080a915f43225d6aa491192479e3",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/a750392e7a26_3f539202/native_lower_1920x1080.png",
      "sha256": "efe50d70821474a840528b8355cd3d825361121833ee983eecbcd6f789a148c5"
    }
  },
  {
    "recordedAt": "2026-09-13T08:59:57.728919+00:00",
    "slot": "SE/walk/4",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Viewed native upper/lower on both light/dark and actual guide. Foreground holstered right thigh continues into one flexed knee, shin and supporting boot. Left thigh/knee are occluded behind this chain; one left calf folds back almost horizontally to the raised rear boot. No extra far-right knee/shin or third branch. Same hood, silver/red armor, shouldered two-hand rifle and right-only holster. Alpha clean including muzzle/trigger gaps. Source-pose approval only: stable upper-body scale, contact displacement and all temporal transitions still require complete SE cycle review.",
    "sourceSHA256": "a062e70908d8ac200ea55af5acec879639de9b2d28f3b75b03b9fdc4686db512",
    "sourcePixelSHA256": "fbbf1071a0995864fc03c221a9605c4d542f5177c98cd052450ae61d29ba635a",
    "sourceReceiptSHA256": "4de69a475299e64d58fac49f71abbcea8ae9a1e1720a6e771959fb87fd7368fd",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/a062e70908d8_3f539202/native_lower_1920x1080.png",
      "sha256": "f406ef670b7b8c986cfdc959cfd11b03caa1b177f156d607cb49fb473e7f8bd9"
    }
  },
  {
    "recordedAt": "2026-09-13T09:06:51.319522+00:00",
    "slot": "SE/walk/5",
    "decision": "approved",
    "reviewer": "current main implementation agent",
    "notes": "Viewed raw plus native upper/lower on both mattes against SE5 guide. Holstered anatomical right leg is supporting: vertical thigh, knee, down-left shin and planted boot. Unholstered left thigh leads diagonally screen right to flexed knee, shin returns down-left and boot is lifted clear ahead. Distinct two continuous chains, no extra knee/shin branch, both boots readable. Hood/visor, scratched silver-red armor, radio and shouldered two-hand bullpup preserved, no green edge remnant in inspected pixels. Source only; actual six-frame body/gun continuity and foot sliding remain complete-cycle review work.",
    "sourceSHA256": "e3cc18e5eab411e8dc1d7c62f8f94a62be7d7edcf6c55ea647d99dac0b1b67d5",
    "sourcePixelSHA256": "7135278d6fda846a05350024357ca1592998d45094e1cc9ed986fec2e80944e1",
    "sourceReceiptSHA256": "dc83031f3557d3724aa085dce4d3660ed19c65d70c7e87ed124857d7f18f0f8a",
    "referenceSHA256": "7deb2c01ea66450a39174a268b4bbf080b239122e8d908162d7f18f74ff5c096",
    "evidence": {
      "path": "qa/site7_rifle/source_panels/e3cc18e5eab4_3f539202/native_lower_1920x1080.png",
      "sha256": "d702a25058fd2dbf86076ffbdd95ce767ee04e4f66b1a713ce9aab69fb055be4"
    }
  }
]
```

## FILE: scripts/animation/site7_machine_sprite.gd
SHA256: 986d9b4f34c33ee9c07d4737c286bad32c0acd84b78361e4b7f7a7fbcdc338c8
```text
extends Node2D
## Source-preserving preview/runtime for non-walking machines only.
## A drone banks as one rigid object; an anchor stays anchored. Neither is a
## humanoid gait and neither may use a six-frame foot-cycle approval as proof.

var actor: EnemyActor
var sprite: Sprite2D
var kind := ""
var emitter_px := Vector2.ZERO
var image_size := Vector2.ZERO
var age := 0.0
var flash := 0.0
var render_scale := 1.0
var body_origin := Vector2.ZERO
var configured := false
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
var views: Dictionary = {}
var facing := ""
var emitter_visible := true
const MAX_TARGET_ERROR := PI / 8.0 + 0.02
static var _pixel_hash_cache: Dictionary = {}

func _visible_pixel_hash(image: Image, file_hash: String) -> String:
    if _pixel_hash_cache.has(file_hash): return _pixel_hash_cache[file_hash]
    var canonical := image.duplicate() as Image
    canonical.convert(Image.FORMAT_RGBA8)
    var bytes := canonical.get_data()
    # Invisible RGB is not another direction. Do not change the source or the
    # displayed texture; canonicalize only the comparison buffer.
    for alpha in range(3,bytes.size(),4):
        if bytes[alpha]==0:
            bytes[alpha-3]=0; bytes[alpha-2]=0; bytes[alpha-1]=0
    var hash := HashingContext.new()
    hash.start(HashingContext.HASH_SHA256)
    hash.update((str(image.get_width())+"x"+str(image.get_height())+":RGBA8:").to_utf8_buffer())
    hash.update(bytes)
    var result := hash.finish().hex_encode()
    _pixel_hash_cache[file_hash]=result
    return result

func _read_view(spec: Dictionary) -> Dictionary:
    var path := str(spec.get("texture", ""))
    if FileAccess.get_sha256(path) != str(spec.get("texture_sha256", "")): return {}
    var image := Image.load_from_file(path)
    if image == null or image.is_empty(): return {}
    var root_xy: Array = spec.get("root_px", [])
    var emitter_xy: Array = spec.get("emitter_px", [])
    if root_xy.size() != 2 or emitter_xy.size() != 2: return {}
    var size := Vector2(image.get_size())
    var origin := Vector2(float(root_xy[0]),float(root_xy[1]))
    var emitter := Vector2(float(emitter_xy[0]),float(emitter_xy[1]))
    var ratio := float(spec.get("display_height",110.0)) / size.y
    if not origin.is_finite() or not emitter.is_finite() or not is_finite(ratio): return {}
    if ratio <= 0.0 or ratio > 1.0 or not Rect2(Vector2.ZERO,size).has_point(emitter): return {}
    return {"texture":ImageTexture.create_from_image(image),"size":size,"root":origin,
        "emitter":emitter,"scale":ratio,"emitter_visible":bool(spec.get("emitter_visible",true)),
        "texture_sha256":str(spec.texture_sha256),
        "pixel_sha256":_visible_pixel_hash(image,str(spec.texture_sha256))}

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    if configured or not is_instance_valid(owner_actor): return false
    var staged_kind := str(spec.get("kind", ""))
    var expected_kind := {"ENM_SITE7_DRONE_01":"hover_machine", "BOSS_SITE7_ANCHOR_01":"anchored_machine"}
    if expected_kind.get(owner_actor.enemy_id,"") != staged_kind or staged_kind.is_empty(): return false
    # Load the complete set before publishing any node/state. A single front
    # illustration is NOT an omnidirectional drone, even with an omni emitter.
    var staged: Dictionary = {}
    if staged_kind == "hover_machine":
        if str(spec.get("facing_mode","")) != "authored_yaw8": return false
        var authored: Dictionary = spec.get("views",{})
        if authored.size() != 8: return false
        var hashes: Array[String] = []
        var pixel_hashes: Array[String] = []
        for direction in DIRECTIONS:
            if not authored.has(direction): return false
            var view := _read_view(authored[direction])
            if view.is_empty() or hashes.has(view.texture_sha256) or pixel_hashes.has(view.pixel_sha256): return false
            hashes.append(view.texture_sha256)
            pixel_hashes.append(view.pixel_sha256)
            staged[direction] = view
    else:
        var fixed := _read_view(spec)
        if fixed.is_empty(): return false
        staged["ANCHORED"] = fixed
    actor = owner_actor
    kind = staged_kind
    sprite = Sprite2D.new()
    sprite.name = "AuthoredMachinePixels"
    sprite.set_meta("preserve_authored_material", true)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = false
    add_child(sprite)
    views = staged
    _apply_view("E" if kind == "hover_machine" else "ANCHORED")
    configured = true
    face_direction(actor._aim_dir)
    return true

func _apply_view(direction: String) -> void:
    if facing == direction: return
    var view: Dictionary = views[direction]
    facing = direction
    image_size = view.size
    emitter_px = view.emitter
    emitter_visible = view.emitter_visible
    render_scale = float(view.scale)
    sprite.texture = view.texture
    sprite.scale = Vector2.ONE * render_scale
    body_origin = -view.root * render_scale
    sprite.position = body_origin

func face_direction(direction: Vector2) -> void:
    if not configured or kind != "hover_machine" or direction.length_squared() < 0.000001: return
    var local_dir := actor.global_transform.affine_inverse().basis_xform(direction)
    var sector := int(floor(fposmod(local_dir.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    _apply_view(DIRECTIONS[sector])

func visible_heading_world() -> Vector2:
    if kind != "hover_machine": return Vector2.ZERO
    var index := DIRECTIONS.find(facing)
    return global_transform.basis_xform(Vector2.from_angle(index*PI/4.0)).normalized()

func resolve_target(target: Vector2) -> Vector2:
    if not configured or not target.is_finite(): return Vector2.INF
    if kind != "hover_machine": return (target-muzzle_world()).normalized()
    # Each authored yaw has a different physical emitter offset. Evaluate its
    # own ray, then keep the pose whose front actually agrees with that ray.
    # No interpolation, horizontal mirroring, or whole-bitmap screen rotation.
    var best := facing
    var error := INF
    sync_pose()
    for i in range(DIRECTIONS.size()):
        var direction: String = DIRECTIONS[i]
        var view: Dictionary = views[direction]
        var local_emitter: Vector2 = (view.emitter-view.root)*float(view.scale)
        var ray := (target-to_global(local_emitter)).normalized()
        var heading := global_transform.basis_xform(Vector2.from_angle(i*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(ray))
        if candidate_error < error:
            best = direction
            error = candidate_error
    # "Least wrong" is not necessarily forward. Inside the illustrated gun's
    # reach there may be no legal view. Retain the pose and explicitly reject
    # this target; the tactics controller must reposition without winding up.
    if error > MAX_TARGET_ERROR: return Vector2.INF
    _apply_view(best)
    return (target-muzzle_world()).normalized()

func _process(delta: float) -> void:
    if not configured: return
    age += delta
    flash = move_toward(flash, 0.0, delta * 7.0)
    sync_pose()
    queue_redraw()

func sync_pose() -> void:
    if not configured: return
    # Use bounded rigid-body motion only. No image stretching or cut-up limbs.
    if kind == "hover_machine":
        rotation = clampf(actor.velocity.x / 118.0, -1.0, 1.0) * 0.045
        position.y = sin(age * 2.8) * 3.0
        if actor.health <= 0.0:
            rotation += (0.55 - actor._death_left) * 1.2
            position.y += (0.55 - actor._death_left) * 65.0
    else:
        rotation = 0.0
        position = Vector2.ZERO
    sprite.modulate = Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash * 0.4)

func muzzle_world() -> Vector2:
    sync_pose()
    return sprite.to_global(emitter_px)

func fired() -> void:
    flash = 1.0
    queue_redraw()

func hit_rect_world() -> Rect2:
    var shape := Rect2(image_size * Vector2(0.12,0.15), image_size * Vector2(0.76,0.70))
    var bounds := Rect2(sprite.to_global(shape.position),Vector2.ZERO)
    for corner in [shape.position + Vector2(shape.size.x,0), shape.end, shape.position + Vector2(0,shape.size.y)]:
        bounds = bounds.expand(sprite.to_global(corner))
    return bounds

func _draw() -> void:
    if not configured or actor.health <= 0.0: return
    var center := to_local(sprite.to_global(emitter_px))
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0 - actor.tactics.state_left / actor.tactics.state_duration, 0.0, 1.0)
    var radius := 8.0 if kind == "hover_machine" else 26.0
    var power := maxf(flash, charge * 0.5)
    if power > 0.0 and emitter_visible:
        draw_circle(center, radius * (1.0 + power), Color(0.94,0.25,0.75,power * 0.22))
        draw_arc(center, radius * 1.4, -age, TAU-age, 32, Color(0.8,0.45,1.0,power * 0.75),1.5)

func debug_contract() -> Dictionary:
    return {"kind":kind,"configured":configured,"art_warp":false,
        "gait_claim":false,"emitter_px":emitter_px,"emitter_world":muzzle_world(),
        "native_size":image_size,"display_height":image_size.y * render_scale,
        "facing":facing,"view_count":views.size(),"heading_world":visible_heading_world(),
        "emitter_visible":emitter_visible,"texture_sha256":views[facing].texture_sha256,
        "mirrored":false}

```

## FILE: scripts/actors/enemy_actor.gd
SHA256: 6960d7b99d0df3098399645cb389e4ed4fee4ae51397af8ebeb81560cf0e7b95
```text
extends CharacterBody2D
class_name EnemyActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const TILE := 512.0

signal defeated(enemy: EnemyActor)
signal projectile_emitted(event: Dictionary)

@export var enemy_id := "ENM_SITE7_RIFLE_01"
@export var max_health := 100.0

var health := 100.0
var art_profile: Dictionary = {}
var home_position := Vector2.ZERO
var _phase := 0.0
var _attack_cd := 0.8
var _hit_flash := 0.0
var _lunge_left := 0.0
var _orbit_sign := 1.0
var _aim_dir := Vector2.LEFT

var _exposed_left := 0.0
var _stagger_left := 0.0
var _status_source := ""
var _last_consumed_source := ""

# M11 deployment-only modifiers. They are applied after authored encounter HP is
# configured and never written to CampaignProgression.
var run_health_multiplier := 1.0
var run_damage_multiplier := 1.0
var run_speed_multiplier := 1.0
var run_attack_interval_multiplier := 1.0

var _visual_root: Node2D
var _hidden_master: Sprite2D
var _rig: Skeleton2D
var _rig_texture: Texture2D
var _bones: Dictionary = {}
var _parts: Dictionary = {}
var _base_positions: Dictionary = {}
var tactics: Node2D
var _death_left := -1.0
var machine_sprite: Node2D

func _ready() -> void:
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
    _load_reviewed_machine_source()
    tactics = preload("res://scripts/combat/site7_enemy_tactics.gd").new()
    tactics.name = "Tactics"
    add_child(tactics)
    queue_redraw()

func configure(id_value: String, hp: float = -1.0) -> void:
    enemy_id = id_value
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if hp > 0.0:
        max_health = hp
    health = max_health
    _exposed_left=0.0; _stagger_left=0.0; _status_source=""; _last_consumed_source=""
    if is_node_ready():
        _rebuild_visual()

func apply_run_modifiers(modifiers: Dictionary) -> void:
    run_health_multiplier = clampf(float(modifiers.get("enemy_health_multiplier",1.0)),0.5,3.0)
    run_damage_multiplier = clampf(float(modifiers.get("enemy_damage_multiplier",1.0)),0.5,3.0)
    run_speed_multiplier = clampf(float(modifiers.get("enemy_speed_multiplier",1.0)),0.5,2.0)
    run_attack_interval_multiplier = clampf(float(modifiers.get("enemy_attack_interval_multiplier",1.0)),0.5,2.0)
    max_health *= run_health_multiplier
    health = max_health

func apply_damage(amount: float) -> void:
    if amount<=0.0 or health<=0.0: return
    var guard := get_node_or_null("BossPhaseTransitionGuard")
    if guard and guard.has_method("debug_guard_active") and guard.debug_guard_active():
        return
    health = maxf(0.0, health - amount)
    _hit_flash = 1.0
    if health <= 0.0:
        remove_from_group("prototype_targets")
        remove_from_group("m3_enemies")
        velocity = Vector2.ZERO
        _death_left = 0.55
        if tactics: tactics.visible = false
        if get_node_or_null("OverheadUI"): get_node("OverheadUI").visible = false
        defeated.emit(self)
        return
    queue_redraw()

func apply_exposed(duration: float, source: String = "") -> void:
    if health<=0.0: return
    _exposed_left=maxf(_exposed_left,maxf(0.0,duration))
    _status_source=source
    queue_redraw()

func is_exposed() -> bool:
    return _exposed_left>0.0

func apply_stagger(duration: float, source: String = "") -> void:
    if health<=0.0: return
    var applied:=maxf(0.0,duration)
    if "BOSS" in enemy_id or "ANCHOR" in enemy_id: applied=minf(applied,1.2)
    _stagger_left=maxf(_stagger_left,applied)
    _status_source=source
    velocity=Vector2.ZERO
    if tactics: tactics.interrupt()
    queue_redraw()

func is_staggered() -> bool:
    return _stagger_left>0.0

func consume_exposed_for_stagger(duration: float, source: String = "") -> bool:
    if not is_exposed(): return false
    _last_consumed_source=_status_source
    _exposed_left=0.0
    apply_stagger(duration,source)
    return true

func _physics_process(delta: float) -> void:
    if health <= 0.0:
        _death_left -= delta
        modulate.a = clampf(_death_left / 0.55, 0.0, 1.0)
        if _death_left <= 0.0: queue_free()
        return
    _phase += delta
    _attack_cd = maxf(0.0, _attack_cd - delta)
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 4.5)
    _exposed_left=maxf(0.0,_exposed_left-delta)
    _stagger_left=maxf(0.0,_stagger_left-delta)
    if _stagger_left>0.0:
        velocity=Vector2.ZERO
    else:
        var target := _nearest_operator()
        if target:
            tactics.step(target, delta)
            velocity *= run_speed_multiplier
        else:
            velocity = velocity.move_toward(Vector2.ZERO, 260.0 * delta)
    move_and_slide()
    var stage := get_parent()
    if stage and stage.has_method("constrain_battle_position"):
        global_position = stage.call("constrain_battle_position", global_position)
    _animate_identity()
    if is_instance_valid(_rig):
        var tint:=Color.WHITE
        if _exposed_left>0.0: tint=tint.lerp(Color("8ff5e8"),0.26)
        if _stagger_left>0.0: tint=tint.lerp(Color("ffd17d"),0.32)
        _rig.modulate = tint.lerp(Color("ff8a8a"), _hit_flash * 0.68)
    queue_redraw()

func _nearest_operator() -> OperatorActor:
    var best: OperatorActor = null
    var best_d2: float = INF
    for node in get_tree().get_nodes_in_group("operators"):
        if node is OperatorActor and not node.is_downed():
            var d2: float = global_position.distance_squared_to(node.global_position)
            if d2 < best_d2:
                best_d2 = d2
                best = node
    return best

func get_combat_hit_rect() -> Rect2:
    if is_instance_valid(machine_sprite): return machine_sprite.hit_rect_world()
    var local := Rect2(-25,-108,50,112)
    if "SHIELD" in enemy_id: local = Rect2(-38,-128,76,132)
    elif "DRONE" in enemy_id: local = Rect2(-38,-105,76,62)
    elif "ABERRANT" in enemy_id: local = Rect2(-31,-104,62,108)
    elif "BOSS" in enemy_id or "ANCHOR" in enemy_id: local = Rect2(-98,-210,196,214)
    return Rect2(global_position + local.position, local.size)

func get_combat_aim_point() -> Vector2:
    return get_combat_hit_rect().get_center()

func _update_tactics(target: OperatorActor, delta: float) -> void:
    var to_target := target.global_position - global_position
    var dist: float = to_target.length()
    var dir := to_target.normalized() if dist > 0.001 else Vector2.RIGHT
    var aim_delta := target.get_combat_aim_point() - get_combat_aim_point()
    _aim_dir = aim_delta.normalized() if aim_delta.length_squared() > 1.0 else dir
    var motion := str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion:
        var radial: float = 0.0
        if dist > 350.0: radial = 1.0
        elif dist < 250.0: radial = -0.8
        var side := Vector2(-dir.y, dir.x) * sin(_phase * 2.2) * 0.72
        velocity = (dir * radial + side).limit_length(1.0) * 105.0
        _try_attack(_aim_dir, 1.05)
    elif "SHIELD" in motion:
        velocity = dir * (72.0 if dist > 190.0 else 18.0)
        _try_attack(_aim_dir, 1.65)
    elif "DRONE" in motion:
        var tangent := Vector2(-dir.y, dir.x) * _orbit_sign
        var radial: float = clampf((dist - 300.0) / 140.0, -0.7, 0.7)
        velocity = (tangent * 0.9 + dir * radial).normalized() * 138.0
        _try_attack(_aim_dir, 0.78)
    elif "ABERRANT" in motion:
        if _lunge_left > 0.0:
            _lunge_left = maxf(0.0, _lunge_left - delta)
            velocity = dir * 330.0
        elif dist > 130.0:
            velocity = dir * 126.0
            if dist < 270.0 and _attack_cd <= 0.0:
                _lunge_left = 0.22
                _attack_cd = 1.35 * run_attack_interval_multiplier
        else:
            velocity = Vector2.ZERO
            _try_attack(_aim_dir, 1.25)
    elif "BOSS" in motion or "ANCHOR" in motion:
        velocity = Vector2(sin(_phase * 0.7), cos(_phase * 0.53)) * 18.0
        _try_attack(_aim_dir.rotated(sin(_phase * 0.8) * 0.18), 1.18)
    else:
        velocity = dir * 80.0
        _try_attack(_aim_dir, 1.2)

func _try_attack(dir: Vector2, interval: float) -> void:
    if _attack_cd > 0.0 or _stagger_left>0.0:
        return
    _attack_cd = interval * run_attack_interval_multiplier
    CombatFeedback.play_fire(get_tree(), art_profile)
    _spawn_projectile(dir)
    if "BOSS" in str(art_profile.get("projectile_profile", "")):
        _spawn_projectile(dir.rotated(-0.16))
        _spawn_projectile(dir.rotated(0.16))

func _spawn_projectile(dir: Vector2, emission_owner: Node = null, attack_serial: int = -1, ordinal: int = -1) -> void:
    if not dir.is_finite() or dir.length_squared() < 0.000001: return
    var projectile := Projectile.new()
    get_tree().root.add_child(projectile)
    var origin := projectile_origin(dir)
    if is_instance_valid(machine_sprite):
        machine_sprite.fired()
    projectile.setup(origin, dir, self, _projectile_color(), art_profile, "operators")
    projectile.damage *= run_damage_multiplier
    # Observe the actual creation boundary, including any legacy caller. A
    # controller's intended shot count alone cannot prove duplicate-free fire.
    var owner_node: Node = emission_owner if is_instance_valid(emission_owner) else self
    projectile_emitted.emit({"actor_id":get_instance_id(),"enemy_id":enemy_id,
        "attack_serial":attack_serial,"ordinal":ordinal,"owner_id":owner_node.get_instance_id(),
        "owner_path":str(owner_node.get_path()),"projectile_id":projectile.get_instance_id(),
        "origin":[origin.x,origin.y],"direction":[dir.x,dir.y],"physics_tick":Engine.get_physics_frames()})

func projectile_origin(dir: Vector2) -> Vector2:
    if is_instance_valid(machine_sprite): return machine_sprite.muzzle_world()
    return get_combat_aim_point() + dir * _muzzle_distance()

func aim_from_emitter(target_point: Vector2) -> Vector2:
    if is_instance_valid(machine_sprite): return machine_sprite.resolve_target(target_point)
    # Legacy muzzle offsets are collinear with aim and need no iterative solve.
    var origin: Vector2 = get_combat_aim_point()
    return (target_point-origin).normalized()

func preview_machine_source(spec: Dictionary) -> bool:
    # Explicit candidate intake for the owned native QA scene. No registry or
    # production pointer is written. Promotion is a separate reviewed change.
    if is_instance_valid(machine_sprite): return false
    var candidate := preload("res://scripts/animation/site7_machine_sprite.gd").new()
    candidate.name = "AuthoredMachine"
    add_child(candidate)
    if not candidate.configure(self,spec):
        candidate.queue_free()
        return false
    machine_sprite = candidate
    _visual_root.visible = false
    return true

func _load_reviewed_machine_source() -> void:
    if not bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)): return
    var binding: Dictionary = art_profile.get("machine_asset",{})
    if binding.is_empty(): return
    var path := str(binding.get("spec",""))
    if not path.begins_with("res://assets/enemies/") or FileAccess.get_sha256(path) != str(binding.get("sha256","")):
        push_error("Reviewed machine spec is missing or changed: "+enemy_id);return
    var spec: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
    if not spec is Dictionary or str(spec.get("enemy_id","")) != enemy_id:
        push_error("Reviewed machine identity mismatch: "+enemy_id);return
    if not preview_machine_source(spec): push_error("Reviewed machine intake failed: "+enemy_id)

func _muzzle_distance() -> float:
    if "BOSS" in enemy_id: return 92.0
    if "SHIELD" in enemy_id: return 44.0
    if "DRONE" in enemy_id: return 38.0
    return 34.0

func _projectile_color() -> Color:
    var p := str(art_profile.get("projectile_profile", ""))
    if "RIFLE" in p: return Color("d95c65")
    if "SHIELD" in p: return Color("e2a94e")
    if "DRONE" in p: return Color("d9577d")
    if "ABERRANT" in p: return Color("a055c5")
    if "ANCHOR" in p: return Color("9b7cff")
    return Color.WHITE

func _rebuild_visual() -> void:
    if is_instance_valid(machine_sprite):
        machine_sprite.hide()
        machine_sprite.queue_free()
        machine_sprite=null
    if is_instance_valid(_visual_root):
        _visual_root.hide()
        _visual_root.queue_free()
    _bones.clear(); _parts.clear(); _base_positions.clear(); _rig_texture = null
    _build_high_res_visual()
    _load_reviewed_machine_source()

func _build_high_res_visual() -> void:
    _visual_root = Node2D.new()
    _visual_root.name = "HighResVisualRoot"
    add_child(_visual_root)
    _hidden_master = Sprite2D.new(); _hidden_master.name="UniqueMasterSprite"; _hidden_master.visible=false
    var master_path := str(art_profile.get("master_asset", ""))
    if not master_path.is_empty() and ResourceLoader.exists("res://" + master_path): _hidden_master.texture=load("res://"+master_path) as Texture2D
    _visual_root.add_child(_hidden_master)
    var rig_path := str(art_profile.get("rig_sheet", ""))
    if not rig_path.is_empty() and ResourceLoader.exists("res://" + rig_path): _rig_texture=load("res://"+rig_path) as Texture2D
    _rig=Skeleton2D.new(); _rig.name="UniqueLayerRig"; _visual_root.add_child(_rig)
    if "RIFLE" in enemy_id: _build_rifle_rig()
    elif "SHIELD" in enemy_id: _build_shield_rig()
    elif "DRONE" in enemy_id: _build_drone_rig()
    elif "ABERRANT" in enemy_id: _build_aberrant_rig()
    elif "BOSS" in enemy_id: _build_boss_rig()
    for key in _bones.keys():
        var bone: Bone2D=_bones[key]; bone.rest=bone.transform; _base_positions[key]=bone.position

func _build_rifle_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-42)); var head:=_bone(body,"head",Vector2(0,-28)); var arm_l:=_bone(body,"arm_L",Vector2(-10,-2)); var arm_r:=_bone(body,"arm_R",Vector2(10,-2)); var leg_l:=_bone(body,"leg_L",Vector2(-7,23)); var shin_l:=_bone(leg_l,"shin_L",Vector2(0,18)); var leg_r:=_bone(body,"leg_R",Vector2(7,23)); var shin_r:=_bone(leg_r,"shin_R",Vector2(0,18)); var weapon:=_bone(body,"weapon",Vector2(3,0))
    _part(head,"Head",0,0,.115,3); _part(body,"RadioPack",1,0,.105,0); _part(body,"Torso",2,0,.108,1); _part(body,"Pelvis",3,0,.105,1); _part(arm_l,"ArmL",0,1,.105,2); _part(arm_r,"ArmR",2,1,.105,2); _part(leg_l,"ThighL",0,2,.105,0); _part(shin_l,"ShinL",1,2,.105,0); _part(leg_r,"ThighR",2,2,.105,0); _part(shin_r,"ShinR",3,2,.105,0); _part(weapon,"Rifle",2,3,.11,5)

func _build_shield_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-45)); var head:=_bone(body,"head",Vector2(5,-31)); var shield:=_bone(body,"shield",Vector2(-19,5)); var arm:=_bone(body,"hydraulic_arm",Vector2(14,-2)); var weapon:=_bone(arm,"weapon",Vector2(18,3)); var leg_l:=_bone(body,"leg_L",Vector2(-4,24)); var leg_r:=_bone(body,"leg_R",Vector2(9,24))
    _part(head,"WedgeHelmet",0,0,.12,4); _part(body,"Torso",1,0,.12,1); _part(body,"Pelvis",2,0,.11,1); _part(shield,"SlabShield",3,0,.13,6); _part(arm,"HydraulicArm",0,1,.12,3); _part(leg_l,"LegL",2,1,.115,0); _part(leg_r,"LegR",3,1,.115,0); _part(weapon,"RamPistol",2,2,.115,5); _part(body,"Cable",0,3,.11,2)

func _build_drone_rig() -> void:
    var chassis:=_bone(_rig,"chassis",Vector2(0,-56)); var eyes:=_bone(chassis,"sensor_cluster",Vector2(0,2)); var fins:=_bone(chassis,"fins",Vector2(0,-2)); var mast:=_bone(chassis,"mast",Vector2(0,-16)); var thruster:=_bone(chassis,"thruster",Vector2(0,20)); var emitter:=_bone(chassis,"emitter",Vector2(0,10))
    _part(chassis,"Crescent",0,0,.14,2); _part(eyes,"Eyes",1,0,.13,4); _part(fins,"Fins",2,0,.14,1); _part(mast,"Mast",3,0,.11,0); _part(thruster,"Thruster",0,1,.11,0); _part(emitter,"ScanArc",1,1,.12,3); _part(emitter,"Gun",0,2,.11,5); _part(chassis,"Glow",3,3,.12,0)

func _build_aberrant_rig() -> void:
    var torso:=_bone(_rig,"torso",Vector2(0,-42)); var skull:=_bone(torso,"skull",Vector2(0,-30)); var arm_l:=_bone(torso,"forelimb_L",Vector2(-13,-1)); var arm_r:=_bone(torso,"forelimb_R",Vector2(13,-1)); var leg_l:=_bone(torso,"leg_L",Vector2(-8,22)); var leg_r:=_bone(torso,"leg_R",Vector2(8,22)); var tail:=_bone(torso,"tail",Vector2(8,20)); var gland:=_bone(torso,"gland",Vector2(0,7))
    _part(skull,"SplitSkull",0,0,.12,4); _part(torso,"Torso",1,0,.112,1); _part(torso,"Pelvis",2,0,.105,1); _part(arm_r,"ForelimbR",3,0,.12,3); _part(arm_l,"ForelimbL",0,1,.12,3); _part(leg_l,"LegL",1,1,.115,0); _part(leg_r,"LegR",2,1,.115,0); _part(tail,"BioTail",1,2,.12,0); _part(gland,"Gland",3,1,.10,2)

func _build_boss_rig() -> void:
    var ring:=_bone(_rig,"ring",Vector2(0,-110)); var iris:=_bone(ring,"iris",Vector2.ZERO); var p1:=_bone(ring,"pylon_1",Vector2(-54,-54)); var p2:=_bone(ring,"pylon_2",Vector2(54,-54)); var p3:=_bone(ring,"pylon_3",Vector2(-54,54)); var p4:=_bone(ring,"pylon_4",Vector2(54,54)); var a1:=_bone(ring,"arm_1",Vector2(-58,-20)); var a2:=_bone(ring,"arm_2",Vector2(58,-20)); var a3:=_bone(ring,"arm_3",Vector2(-58,38)); var a4:=_bone(ring,"arm_4",Vector2(58,38)); var anchor:=_bone(ring,"anchor",Vector2(0,92)); var distortion:=_bone(ring,"distortion",Vector2.ZERO)
    _part(ring,"OuterRing",0,0,.27,1); _part(iris,"SignalIris",1,0,.24,5); _part(p1,"Pylon1",2,0,.18,2); _part(p2,"Pylon2",3,0,.18,2); _part(a1,"Arm1",0,1,.18,3); _part(a2,"Arm2",1,1,.18,3); _part(a3,"Arm3",2,1,.18,3); _part(a4,"Arm4",3,1,.18,3); _part(p3,"Pylon3",0,2,.18,2); _part(p4,"Pylon4",1,2,.18,2); _part(anchor,"Anchor",0,3,.18,0); _part(distortion,"Distortion",1,3,.24,0)

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone:=Bone2D.new(); bone.name=bone_name; bone.position=pos; bone.set_autocalculate_length_and_angle(false); parent.add_child(bone); _bones[bone_name]=bone; return bone

func _part(parent:Node2D, part_name:String, col:int, row:int, scale_value:float, z:int) -> Sprite2D:
    var sprite:=Sprite2D.new(); sprite.name=part_name; sprite.texture=_rig_texture; sprite.region_enabled=true; sprite.region_rect=Rect2(col*TILE,row*TILE,TILE,TILE); sprite.centered=true; sprite.scale=Vector2.ONE*scale_value; sprite.z_index=z; sprite.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS; parent.add_child(sprite); _parts[part_name]=sprite; return sprite

func _animate_identity() -> void:
    if not is_instance_valid(_rig): return
    var motion:=str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion: _animate_rifle()
    elif "SHIELD" in motion: _animate_shield()
    elif "DRONE" in motion: _animate_drone()
    elif "ABERRANT" in motion: _animate_aberrant()
    elif "BOSS" in motion or "ANCHOR" in motion: _animate_boss()

func _animate_rifle() -> void:
    var gait:float=sin(_phase*7.2)*0.28*minf(1.0,velocity.length()/maxf(1.0,105.0*run_speed_multiplier)); (_bones["leg_L"] as Bone2D).rotation=gait; (_bones["leg_R"] as Bone2D).rotation=-gait; (_bones["shin_L"] as Bone2D).rotation=-gait*.55; (_bones["shin_R"] as Bone2D).rotation=gait*.55; (_bones["body"] as Bone2D).rotation=sin(_phase*3.6)*.018; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle(); (_bones["arm_L"] as Bone2D).rotation=_aim_dir.angle()+.10; (_bones["arm_R"] as Bone2D).rotation=_aim_dir.angle()-.08
func _animate_shield() -> void:
    var stomp:float=absf(sin(_phase*4.1)); (_bones["body"] as Bone2D).position=(_base_positions["body"] as Vector2)+Vector2(0,stomp*3.2); (_bones["shield"] as Bone2D).rotation=-.06+sin(_phase*2.0)*.025; (_bones["hydraulic_arm"] as Bone2D).rotation=_aim_dir.angle()*.45; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle()*.55
func _animate_drone() -> void:
    (_bones["chassis"] as Bone2D).position=(_base_positions["chassis"] as Vector2)+Vector2(0,sin(_phase*3.8)*7.0); (_bones["chassis"] as Bone2D).rotation=sin(_phase*2.6)*.10; (_bones["fins"] as Bone2D).rotation=-sin(_phase*3.3)*.13; (_bones["thruster"] as Bone2D).scale=Vector2(1.0,1.0+sin(_phase*8.0)*.18); (_bones["sensor_cluster"] as Bone2D).rotation=sin(_phase*1.7)*.09
func _animate_aberrant() -> void:
    var gait:float=sin(_phase*6.6); (_bones["torso"] as Bone2D).position=(_base_positions["torso"] as Vector2)+Vector2(0,absf(gait)*4.5); (_bones["forelimb_L"] as Bone2D).rotation=.42+gait*.34; (_bones["forelimb_R"] as Bone2D).rotation=-.38-gait*.31; (_bones["leg_L"] as Bone2D).rotation=-gait*.38; (_bones["leg_R"] as Bone2D).rotation=gait*.38; (_bones["tail"] as Bone2D).rotation=sin(_phase*3.1-.8)*.32; (_bones["skull"] as Bone2D).rotation=-sin(_phase*3.3)*.07
func _animate_boss() -> void:
    var ring:=_bones["ring"] as Bone2D; ring.position=(_base_positions["ring"] as Vector2)+Vector2(0,sin(_phase*1.2)*9.0); ring.rotation=sin(_phase*.72)*.035; (_bones["iris"] as Bone2D).rotation=-_phase*.22; (_bones["distortion"] as Bone2D).rotation=_phase*.15
    for i in range(1,5):
        var arm:=_bones["arm_%d"%i] as Bone2D; arm.rotation=sin(_phase*1.35+float(i)*.8)*.18
        var pylon:=_bones["pylon_%d"%i] as Bone2D; pylon.scale=Vector2.ONE*(1.0+sin(_phase*1.1+float(i))*.035)

func _draw() -> void:
    var ratio:=clampf(health/maxf(1.0,max_health),0.0,1.0); var width:=58.0 if "BOSS" not in enemy_id else 130.0; var bar_y:=-82.0 if "BOSS" not in enemy_id else -242.0
    var radius:=30.0 if "BOSS" not in enemy_id else 82.0
    # The scene already owns a foot ellipse and one overhead health UI.
    # Duplicating them here produced floating circles and double health bars.
    if get_node_or_null("OverheadUI") == null:
        draw_rect(Rect2(-width*.5,bar_y,width,5),Color("172028"),true)
        draw_rect(Rect2(-width*.5+1,bar_y+1,(width-2)*ratio,3),_projectile_color(),true)
    if _exposed_left>0.0:
        var sr:=radius+8.0; draw_arc(Vector2(0,5),sr,-2.7,-0.45,28,Color("70eadb",0.82),2.3); draw_arc(Vector2(0,5),sr,0.45,2.7,28,Color("70eadb",0.48),1.4)
    if _stagger_left>0.0:
        draw_arc(Vector2(0,5),radius+13.0,0.0,TAU,40,Color("ffc567",0.78),3.2)
        draw_line(Vector2(-12,bar_y-8),Vector2(12,bar_y-8),Color("ffdca0",0.85),2.0)

func debug_status_contract() -> Dictionary:
    return {"exposed":is_exposed(),"exposed_left":_exposed_left,"staggered":is_staggered(),"stagger_left":_stagger_left,"status_source":_status_source,"last_consumed_source":_last_consumed_source}

func debug_run_modifier_contract() -> Dictionary:
    return {
        "enemy_health_multiplier":run_health_multiplier,
        "enemy_damage_multiplier":run_damage_multiplier,
        "enemy_speed_multiplier":run_speed_multiplier,
        "enemy_attack_interval_multiplier":run_attack_interval_multiplier,
        "max_health":max_health,
        "health":health
    }

```

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02
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
    # Stagger skips step(). Invalidate THIS CanvasItem's cached warning now.
    queue_redraw()

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
    # Do not even resolve a new visual yaw while an announced attack is locked.
    # Its body, muzzle and shot must retain the same warning direction.
    var aim := locked_aim
    if state not in ["WINDUP", "BURST", "LUNGE"]:
        aim = actor.aim_from_emitter(target.get_combat_aim_point())
        if not _valid_aim(aim): aim = actor._aim_dir
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
            var reposition_velocity := actor.velocity
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            var candidate_aim := actor.aim_from_emitter(target.get_combat_aim_point())
            if not _valid_aim(candidate_aim):
                # The target may be inside every authored emitter offset.
                # Keep moving normally; do not advertise or emit a reverse ray.
                actor.velocity = reposition_velocity
                queue_redraw()
                return
            locked_aim = candidate_aim
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

func _valid_aim(direction: Vector2) -> bool:
    return direction.is_finite() and direction.length_squared() > 0.000001

func _fire(direction: Vector2) -> void:
    if not _valid_aim(direction): return
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

## FILE: scripts/ui/enemy_overhead_ui.gd
SHA256: ba2c0d4062fa454663f009f51ed53d5bd3d34239eec83c673d600d94f18d310a
```text
extends Node2D
class_name EnemyOverheadUI

var actor: EnemyActor
var _phase := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_as_relative = false
    z_index = 3200
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func bar_y_local() -> float:
    if actor == null: return -12.0
    if is_instance_valid(actor.machine_sprite):
        # Damage bounds deliberately omit antennas/pylons. A health bar must
        # clear the whole visible machine, not sit inside that inset hit box.
        var machine: Node2D=actor.machine_sprite
        var size: Vector2=machine.image_size
        var top:=INF
        for corner in [Vector2.ZERO,Vector2(size.x,0),size,Vector2(0,size.y)]:
            top=minf(top,to_local(machine.sprite.to_global(corner)).y)
        return top-12.0
    return actor.get_combat_hit_rect().position.y-actor.global_position.y-12.0

func _draw() -> void:
    if actor == null:
        return
    var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
    var boss := "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id
    var width := 118.0 if boss else 48.0
    var y := bar_y_local()
    var accent := _accent()

    # Backplate + thin luminous outline.
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(0.015,0.022,0.028,0.88),true)
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(accent.r,accent.g,accent.b,0.24),false,1.0)
    draw_rect(Rect2(-width*0.5,y,width,4.0),Color("182329"),true)

    # Segmented health fill.
    var segments := 12 if boss else 6
    var segment_w := (width-float(segments-1)*2.0)/float(segments)
    for i in range(segments):
        var threshold := float(i)/float(segments)
        var filled := ratio > threshold
        var x := -width*0.5 + float(i)*(segment_w+2.0)
        draw_rect(Rect2(x,y,segment_w,4.0),Color(accent,0.95 if filled else 0.12),true)

    # Small threat chevron. Boss gets a phase-reactive double marker.
    var pulse := 0.72 + sin(_phase*4.0)*0.16
    var marker_y := y-10.0
    var pts := PackedVector2Array([Vector2(-6,marker_y),Vector2(6,marker_y),Vector2(0,marker_y+6)])
    draw_colored_polygon(pts,Color(accent.r,accent.g,accent.b,pulse))
    if boss:
        var phase := 1 if ratio>0.66 else (2 if ratio>0.33 else 3)
        if phase>=2:
            draw_arc(Vector2.ZERO,94.0+phase*5.0,-PI*0.82,-PI*0.18,28,Color(accent.r,accent.g,accent.b,0.18+phase*0.06),2.0+phase)

func _accent() -> Color:
    if actor == null: return Color("f05b68")
    if "RIFLE" in actor.enemy_id: return Color("ef6470")
    if "SHIELD" in actor.enemy_id: return Color("e5a94d")
    if "DRONE" in actor.enemy_id: return Color("e45a91")
    if "ABERRANT" in actor.enemy_id: return Color("bd61da")
    if "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        var ratio := actor.health/maxf(1.0,actor.max_health)
        return Color("f0529d") if ratio<=0.33 else Color("9179ff")
    return Color("f05b68")

```

## FILE: data/art_profiles/enemy_profiles.json
SHA256: 549ca45d47ec39ea740776c9eccfd52323a00775da0a29b38e969baf4ec951a3
```text
{
  "schema_version": 1,
  "profiles": [
    {
      "enemy_id":"ENM_SITE7_RIFLE_01","name":"SITE-7 RIFLE TROOPER","tier":"NORMAL","visual_profile":"VIS_ENM_RIFLE_01",
      "master_asset":"assets/enemies/rifle_trooper/rifle_trooper_master.svg","rig_sheet":"assets/enemies/rifle_trooper/rifle_trooper_rig_sheet.svg",
      "silhouette":"narrow hazard hood, offset radio mast, split knee armor, long bullpup rifle","palette":["#D9E1E7","#43525C","#B83B45","#78A9B7"],
      "motion_profile":"MOT_ENM_RIFLE_01","motion_signature":"cautious shoulder-led patrol, quick alert snap, short lateral burst steps, disciplined three-round recoil",
      "projectile_profile":"PRJ_ENM_RIFLE_TRACER_01","projectile_signature":"red-white narrow tracer with intermittent dash gaps","hit_vfx_profile":"HIT_ENM_RIFLE_METAL_01","hit_vfx_signature":"small pale spark fork with red paint flecks","fire_sfx_profile":"SFX_FIRE_ENM_RIFLE_01","fire_sfx_signature":"dry suppressed mechanical crack with radio-like tail","impact_sfx_profile":"SFX_HIT_ENM_RIFLE_01","impact_sfx_signature":"thin plate ping and fabric thud"
    },
    {
      "enemy_id":"ENM_SITE7_SHIELD_01","name":"SITE-7 SHIELD BREACHER","tier":"ELITE","visual_profile":"VIS_ENM_SHIELD_01",
      "master_asset":"assets/enemies/shield_breacher/shield_breacher_master.svg","rig_sheet":"assets/enemies/shield_breacher/shield_breacher_rig_sheet.svg",
      "silhouette":"tall slab shield, forward helmet wedge, one exposed hydraulic arm, compact ram pistol","palette":["#C7D0D5","#2D3942","#E2A94E","#7D342E"],
      "motion_profile":"MOT_ENM_SHIELD_01","motion_signature":"slow shield-first advance, heavy stomp cadence, brace before fire, violent shoulder ram with long recover","projectile_profile":"PRJ_ENM_SHIELD_RAMSHOT_01","projectile_signature":"short fat brass plasma slug with rectangular shock wake","hit_vfx_profile":"HIT_ENM_SHIELD_PLATE_01","hit_vfx_signature":"broad angled spark sheet with shield-edge scrape streak","fire_sfx_profile":"SFX_FIRE_ENM_SHIELD_01","fire_sfx_signature":"compressed piston bark with shield resonance","impact_sfx_profile":"SFX_HIT_ENM_SHIELD_01","impact_sfx_signature":"thick steel gong with hydraulic rattle"
    },
    {
      "enemy_id":"ENM_SITE7_DRONE_01","name":"SITE-7 RECON DRONE","tier":"NORMAL","visual_profile":"VIS_ENM_DRONE_01",
      "machine_asset":{"spec":"res://assets/enemies/recon_drone/authored_yaw8_v1/spec.json","sha256":"0c716b309edfa5ecaa29cffef01642e23c855a3527a979a922002a9e8ad6b5ba"},
      "master_asset":"assets/enemies/recon_drone/recon_drone_master.svg","rig_sheet":"assets/enemies/recon_drone/recon_drone_rig_sheet.svg",
      "silhouette":"flat crescent chassis, three uneven sensor eyes, dangling micro-thruster, no humanoid limbs","palette":["#9DBAC7","#1D2A31","#D9577D","#65E1E8"],
      "motion_profile":"MOT_ENM_DRONE_01","motion_signature":"constant hover micro-orbit, asymmetric banking, scan pause, sudden lateral dart, rotational death tumble","projectile_profile":"PRJ_ENM_DRONE_BEAMLET_01","projectile_signature":"magenta dotted beamlet packets with cyan sensor ghost","hit_vfx_profile":"HIT_ENM_DRONE_ARC_01","hit_vfx_signature":"thin electric crescent arcs and falling pixel sparks","fire_sfx_profile":"SFX_FIRE_ENM_DRONE_01","fire_sfx_signature":"high servo chirp followed by clipped laser zip","impact_sfx_profile":"SFX_HIT_ENM_DRONE_01","impact_sfx_signature":"glass-electronic tick with unstable electrical sputter"
    },
    {
      "enemy_id":"ENM_SITE7_ABERRANT_01","name":"SITE-7 ABERRANT RUNNER","tier":"NORMAL","visual_profile":"VIS_ENM_ABERRANT_01",
      "master_asset":"assets/enemies/aberrant_melee/aberrant_melee_master.svg","rig_sheet":"assets/enemies/aberrant_melee/aberrant_melee_rig_sheet.svg",
      "silhouette":"long forelimbs, collapsed shoulder line, split mask-like skull plate, trailing biofilament tail","palette":["#C9C5BA","#302D32","#7F3FA4","#DA6B83"],
      "motion_profile":"MOT_ENM_ABERRANT_01","motion_signature":"uneven four-beat crouch gait, head lag, explosive lunge, elastic recoil and twitching recovery","projectile_profile":"PRJ_ENM_ABERRANT_SPIT_01","projectile_signature":"slow violet organic glob with whipping filament tail","hit_vfx_profile":"HIT_ENM_ABERRANT_BIO_01","hit_vfx_signature":"wet magenta membrane tear with dark filament snapback","fire_sfx_profile":"SFX_FIRE_ENM_ABERRANT_01","fire_sfx_signature":"throat click into viscous whip release","impact_sfx_profile":"SFX_HIT_ENM_ABERRANT_01","impact_sfx_signature":"damped flesh strike with fibrous tear"
    },
    {
      "enemy_id":"BOSS_SITE7_ANCHOR_01","name":"SIGNAL ANCHOR GUARDIAN","tier":"BOSS","visual_profile":"VIS_BOSS_ANCHOR_01",
      "machine_asset":{"spec":"res://assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json","sha256":"c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763"},
      "master_asset":"assets/enemies/signal_anchor_guardian/signal_anchor_guardian_master.svg","rig_sheet":"assets/enemies/signal_anchor_guardian/signal_anchor_guardian_rig_sheet.svg",
      "silhouette":"massive suspended ring body, offset armored pylons, four articulated emitter arms, exposed inner signal iris","palette":["#2A313B","#8572FF","#F0529D","#E7E0FF"],
      "motion_profile":"MOT_BOSS_ANCHOR_01","motion_signature":"slow orbital idle, pylon breathing, arm-by-arm charge choreography, phase-transition ring inversion, heavy camera-readable attacks","projectile_profile":"PRJ_BOSS_ANCHOR_LANCE_01","projectile_signature":"wide violet-magenta lance segment with rotating black notches and lingering distortion ribs","hit_vfx_profile":"HIT_BOSS_ANCHOR_RIFT_01","hit_vfx_signature":"large iris-shaped rupture, violet radial shards and inward-pulling black streaks","fire_sfx_profile":"SFX_FIRE_BOSS_ANCHOR_01","fire_sfx_signature":"layered resonant charge chord collapsing into a hard spatial crack","impact_sfx_profile":"SFX_HIT_BOSS_ANCHOR_01","impact_sfx_signature":"low structural boom plus reversed crystalline suction"
    }
  ]
}

```

## FILE: assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json
SHA256: c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763
```text
{
  "schema_version": 1,
  "enemy_id": "BOSS_SITE7_ANCHOR_01",
  "kind": "anchored_machine",
  "texture": "res://assets/enemies/signal_anchor_guardian/authored_core_v1/anchor.png",
  "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
  "display_height": 270,
  "root_px": [
    613,
    1235
  ],
  "emitter_px": [
    638,
    616
  ],
  "emission_contract": "stationary central signal iris; four rigid arm housings are not independently aimed barrels",
  "status": "REVIEWED_LOCAL_MVP_FIXED_CORE"
}

```

## FILE: tests/smoke/site7_anchor_app_smoke.gd
SHA256: a33ae14c8780d70dcaab2713ab9ce933c93ed81d2df7e959464a209ff2447fd5
```text
extends SceneTree
## Normal app registry intake, not an injected QA candidate or visual approval.
const ENEMY:=preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR:=preload("res://scenes/actors/player/OperatorActor.tscn")
var failures: Array[String]=[]
var checks:=0
var emissions: Array[Dictionary]=[]
func _init() -> void:call_deferred("run")
func check(ok: bool,label: String) -> void:
    checks+=1
    if not ok:failures.append(label);push_error(label)
func run() -> void:
    var actor:=ENEMY.instantiate() as EnemyActor
    actor.configure("BOSS_SITE7_ANCHOR_01",620.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Normal registry activates anchored art")
    if not is_instance_valid(actor.machine_sprite):quit(1);return
    actor.machine_sprite.set_process(false)
    var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(actor.art_profile.machine_asset.spec))
    check(FileAccess.get_sha256(actor.art_profile.machine_asset.spec)==actor.art_profile.machine_asset.sha256,"Exact spec hash")
    check(str(spec.texture).begins_with("res://assets/enemies/signal_anchor_guardian/") and not "/qa/" in str(spec.texture),"Runtime-owned texture")
    check(FileAccess.get_sha256(spec.texture)==spec.texture_sha256,"Exact authored image bytes")
    check(actor.health==620.0 and actor.max_health==620.0,"No gameplay HP substitution")
    check(actor.machine_sprite.kind=="anchored_machine" and actor.machine_sprite.views.size()==1,"Fixed structure, not manufactured yaw8")
    check(not actor._visual_root.visible,"Old mock hidden after valid intake")
    var victim:=OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(row: Dictionary) -> void:emissions.append(row))
    var iris: Vector2=actor.machine_sprite.muzzle_world()
    for hz in [30,60,120]:
        for sector in range(8):
            emissions.clear()
            victim.global_position=actor.global_position+Vector2.from_angle(sector*PI/4.0)*500.0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0;actor.tactics.attack_serial=0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP","Actual warning entered")
            check(locked.dot(victim.get_combat_aim_point()-iris)>0.0,"Warning aims from actual iris to initial target")
            victim.global_position=-victim.global_position
            for tick in range(hz+2):
                actor.tactics.step(victim,1.0/hz)
                if actor.tactics.state=="RECOVER":break
            check(emissions.size()==3,"Actual phase-1 transition emits three and only three")
            check(actor.machine_sprite.rotation==0.0 and actor.machine_sprite.position==Vector2.ZERO,"Chassis remains fixed")
            check(actor.machine_sprite.muzzle_world().distance_to(iris)<0.001,"Iris does not chase new target")
            for i in range(emissions.size()):
                var shot:=instance_from_id(emissions[i].projectile_id) as PrototypeProjectile
                check(shot.global_position.distance_to(iris)<0.001,"Created projectile originates at iris")
                var direction:=Vector2(emissions[i].direction[0],emissions[i].direction[1])
                check(direction.distance_to(locked.rotated((i-1)*0.22))<0.0001,"Fan keeps locked warning orientation")
                shot.free()
    actor.free();victim.free()
    await process_frame
    var hashes: Dictionary={}
    for path in ["scripts/actors/enemy_actor.gd","scripts/animation/site7_machine_sprite.gd","scripts/combat/site7_enemy_tactics.gd","scripts/ui/enemy_overhead_ui.gd","data/art_profiles/enemy_profiles.json","assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json","tests/smoke/site7_anchor_app_smoke.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var out:="res://qa/stage1_implementation_20260913/anchor_app_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json"
    var file:=FileAccess.open(out,FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"hashes":hashes,"candidate_injection":false,"visual_approval":false},"  "));file.close()
    print("SITE7_ANCHOR_APP_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks) ",out)
    quit(0 if failures.is_empty() else 1)

```

## FILE: tests/smoke/site7_drone_app_smoke.gd
SHA256: 902c800645e468ba34d17805e81b17fd0f1cf90c54ac8826ba0a9fc1221d2b1e
```text
extends SceneTree
## Normal registry intake and state-machine emissions, no QA texture injection.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const NAMES := ["E","SE","S","SW","W","NW","N","NE"]
var checks := 0
var failures: Array[String] = []
var emissions: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label);push_error(label)

func run() -> void:
    check(bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)),"Default app intake enabled")
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_DRONE_01",62.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Normal spawn binds registry without preview injection")
    if not is_instance_valid(actor.machine_sprite):quit(1);return
    actor.machine_sprite.set_process(false)
    check(actor.machine_sprite.views.size()==8 and actor.machine_sprite.facing=="W","All views and initial left facing")
    check(not actor._visual_root.visible and actor.machine_sprite.visible,"Mock hidden, authored machine visible")
    check(actor.max_health==62.0 and actor.enemy_id=="ENM_SITE7_DRONE_01","No gameplay health/identity override")
    var binding: Dictionary=actor.art_profile.machine_asset
    var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(binding.spec))
    check(FileAccess.get_sha256(binding.spec)==binding.sha256,"Registry binds exact versioned spec")
    for name in NAMES:
        var view: Dictionary=spec.views[name]
        check(str(view.texture).begins_with("res://assets/enemies/recon_drone/") and not "/qa/" in str(view.texture),"Runtime texture is not a QA path "+name)
        check(FileAccess.get_sha256(view.texture)==view.texture_sha256,"Exact reviewed texture "+name)
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(event: Dictionary) -> void:emissions.append(event))
    for hz in [30,60,120]:
        for i in range(8):
            emissions.clear()
            var direction := Vector2.from_angle(i*PI/4.0)
            victim.global_position=Vector2(0,-60)+direction*500.0
            actor.velocity=-direction*118.0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP","Normal warning entered")
            check(actor.machine_sprite.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"Front agrees with announced shot")
            # Adversarial target reversal after the warning has been advertised.
            victim.global_position=Vector2(0,-60)-direction*500.0
            for tick in range(hz):
                actor.tactics.step(victim,1.0/hz)
                if not emissions.is_empty():break
            check(emissions.size()==1,"Actual timed state transition emits exactly one shot")
            if emissions.size()==1:
                var shot:=instance_from_id(emissions[0].projectile_id) as PrototypeProjectile
                check(shot.global_position.distance_to(actor.machine_sprite.muzzle_world())<0.001,"Actual shot starts at illustrated emitter")
                check(actor.machine_sprite.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"No reversed body at emission")
                shot.free()
            actor.tactics.state="RECOVER";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(actor.machine_sprite.visible_heading_world().dot(locked)<-0.8,"Recovery follows the new opposite target")
    var prior:=actor.machine_sprite
    check(not prior.configure(actor,spec),"Repeated configure rejected atomically")
    check(prior.configured and prior.views.size()==8,"Rejected reconfigure preserves visible source")
    actor.configure("ENM_SITE7_RIFLE_01",100.0)
    check(not is_instance_valid(actor.machine_sprite) and not prior.visible and actor._visual_root.visible,"Role change retires old visible machine")
    check(not actor.preview_machine_source(spec),"Drone spec cannot attach to humanoid")
    actor.free();victim.free()
    await process_frame
    var hashes: Dictionary={}
    for path in ["scripts/animation/site7_machine_sprite.gd","scripts/actors/enemy_actor.gd","scripts/combat/site7_enemy_tactics.gd","data/art_profiles/enemy_profiles.json","assets/enemies/recon_drone/authored_yaw8_v1/spec.json","tests/smoke/site7_drone_app_smoke.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var out := "res://qa/stage1_implementation_20260913/drone_app_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json"
    var file:=FileAccess.open(out,FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"sha256":hashes,"candidate_injection":false,"visual_approval":false},"  "));file.close()
    print("SITE7_DRONE_APP_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks) ",out)
    quit(0 if failures.is_empty() else 1)

```

## FILE: tests/smoke/site7_machine_source_smoke.gd
SHA256: 9626a0c7a63e5f6e86cc9ed76b52362e18ca3d85c475707eaa8bf2d54f0666d5
```text
extends SceneTree
## Source pixel/candidate binding and real projectile-origin tests, not visual PASS.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("run")

func check(value: bool, label: String) -> void:
    checks += 1
    if not value:
        failures.append(label)
        push_error(label)

func run() -> void:
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",false)
    var specs: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json"))
    for id in ["ENM_SITE7_DRONE_01","BOSS_SITE7_ANCHOR_01"]:
        var actor := ENEMY.instantiate() as EnemyActor
        actor.configure(id,620.0)
        root.add_child(actor)
        actor.set_physics_process(false)
        check(actor.preview_machine_source(specs[id]),id+" exact candidate binds")
        await process_frame
        await process_frame
        var sprite: Node2D = actor.machine_sprite
        check(is_instance_valid(sprite),id+" raster selected")
        if not is_instance_valid(sprite):continue
        check(not actor._visual_root.visible,id+" previous body hidden")
        check(sprite.sprite.material == null,id+" ImageGen authored materials unchanged")
        var victim := OPERATOR.instantiate() as OperatorActor
        victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
        root.add_child(victim);victim.set_physics_process(false)
        victim.global_position = Vector2(450,120)
        for hz in [30,60,120]:
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2 = actor.tactics.locked_aim
            var target_point := victim.get_combat_aim_point()
            var actual_origin: Vector2 = sprite.sprite.to_global(sprite.emitter_px)
            check(absf(locked.cross((target_point-actual_origin).normalized()))<0.00001,"Telegraph ray originates at visible emitter")
            check(locked.dot(target_point-actual_origin)>0,"Telegraph points toward initial target")
            victim.global_position += Vector2(70,-45)
            actor.tactics.step(victim,1.0/hz)
            check(actor.tactics.locked_aim.is_equal_approx(locked),"Later target motion cannot home a telegraphed ray")
        victim.free()
        actor.rotation=0.13
        actor.scale=Vector2(0.8,1.2)
        for hz in [30,60,120]:
            for i in range(8):
                var dir := Vector2.from_angle(i * PI / 4.0)
                actor.velocity = dir * 118.0
                sprite._process(1.0 / hz)
                var expected: Vector2 = sprite.sprite.to_global(sprite.emitter_px)
                var bounds: Rect2 = sprite.hit_rect_world()
                var overhead: EnemyOverheadUI=actor.get_node("OverheadUI")
                var clears_all:=true
                for corner in [Vector2.ZERO,Vector2(sprite.image_size.x,0),sprite.image_size,Vector2(0,sprite.image_size.y)]:
                    clears_all=clears_all and overhead.bar_y_local()<=overhead.to_local(sprite.sprite.to_global(corner)).y-11.99
                check(clears_all,"Health bar clears full authored machine, including pylons and bank")
                for point in [Vector2(0.13,0.16),Vector2(0.87,0.16),Vector2(0.87,0.84),Vector2(0.13,0.84)]:
                    check(bounds.has_point(sprite.sprite.to_global(sprite.image_size*point)),"Machine AABB covers transformed native region")
                check(sprite.muzzle_world().distance_to(expected)<0.001,id+" emitter follows visible source transform")
                if id.begins_with("BOSS"):
                    check(sprite.position == Vector2.ZERO and sprite.rotation == 0.0,"Anchor stays anchored")
                var previous := root.get_child_count()
                actor._spawn_projectile(dir)
                check(root.get_child_count() == previous + 1,"One emitter, one projectile")
                var projectile := root.get_child(root.get_child_count()-1) as PrototypeProjectile
                check(projectile.global_position.distance_to(expected)<0.001,"Projectile starts at actual authored iris/orb")
                projectile.free()
        actor.apply_damage(10000.0)
        check(get_nodes_in_group("enemy_death_sequences").is_empty(),"No old SVG death fragments")
        actor.free()
    print("SITE7_MACHINE_SOURCE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)

```

## FILE: tests/render/site7_anchor_candidate_capture.gd
SHA256: 9f76f697da11efcec50e11dd0bbab1c9839c49e6ad7cc049d65c1a23f0d8d29f
```text
extends SceneTree
## Controlled boss phase/telegraph cases in the real scene, not a playthrough.
## Health and attack serial select the tested phase; no game values are changed.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const SPEC := "res://motion_lab_v1/qa/stage1_enemies_20260913/anchor/candidate_spec_v1.json"
var out := "res://qa/stage1_implementation_20260913/anchor_native_"+str(Time.get_unix_time_from_system()).replace(".","_")
var failures: Array[String] = []
var rows: Array[Dictionary] = []
var emissions: Array[Dictionary] = []
var use_app := "--app-registry" in OS.get_cmdline_user_args()

func _init() -> void: call_deferred("run")

func settle(count: int = 1) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func capture(actor: EnemyActor, label: String) -> void:
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    var path := out+"/"+label+".webp"
    var iris_screen: Vector2=actor.machine_sprite.sprite.get_global_transform_with_canvas()*actor.machine_sprite.emitter_px
    if not actor.machine_sprite.sprite.get_viewport_rect().has_point(iris_screen):
        failures.append("Boss iris is outside the captured viewport: "+label)
    if im.get_size()!=Vector2i(1920,1080) or im.save_webp(path,true,0.94)!=OK:
        failures.append("Capture failed: "+label)
    rows.append({"path":path,"sha256":FileAccess.get_sha256(path),"label":label,
        "native":[1920,1080],"iris_canvas":iris_screen,"wall_ms":Time.get_ticks_msec(),"physics_tick":Engine.get_physics_frames(),
        "health_fixture":actor.health,"tactics":actor.tactics.contract(),
        "machine":actor.machine_sprite.debug_contract(),"emissions":emissions.duplicate(true)})

func run() -> void:
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",use_app)
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SPEC))
    for phase in [1,2,3]:
        for serial in [0,1]:
            var label: String="phase%d_attack%d" % [phase,serial+1]
            var stage:=STAGE.instantiate() as StoryStage01
            stage.battle_preview=true;root.add_child(stage)
            await settle(4)
            stage.start_battle_preview(4)
            await settle(2)
            stage.set_process(false);stage.set_physics_process(false)
            stage.squad.set_process(false);stage.squad.set_physics_process(false)
            var actor: EnemyActor
            for enemy in get_nodes_in_group("m3_enemies"):
                enemy.set_physics_process(false)
                if enemy.enemy_id=="BOSS_SITE7_ANCHOR_01":actor=enemy
                else:enemy.hide()
            if actor==null or (not is_instance_valid(actor.machine_sprite) if use_app else not actor.preview_machine_source(spec)):
                failures.append("Boss source unavailable");stage.queue_free();await settle(2);continue
            # Keep the encounter's actual anchored position. The existing
            # BossAnchorLockPresentation restores it each frame; arbitrary
            # relocation makes a numeric test pass while the art is offscreen.
            actor.health=actor.max_health*([0.95,0.5,0.25][phase-1])
            actor.velocity=Vector2.ZERO
            var victim: OperatorActor
            for operator in get_nodes_in_group("operators"):
                operator.debug_drive(Vector2.ZERO,Vector2.RIGHT)
                operator.set_physics_process(false)
                if operator.operator_id=="CHR_PROTO_01":victim=operator
                else:operator.hide()
            victim.global_position=actor.global_position+Vector2(-310,-30)
            stage.camera.global_position=actor.global_position+Vector2(-110,-150)
            stage.camera.position_smoothing_enabled=false
            emissions.clear()
            actor.projectile_emitted.connect(func(row: Dictionary) -> void:emissions.append(row))
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.attack_serial=serial
            actor.tactics.step(victim,1.0/60.0)
            await settle(2)
            await capture(actor,label+"_windup_start")
            var fixed_position:=actor.global_position
            var fixed_muzzle: Vector2=actor.machine_sprite.muzzle_world()
            for tick in range(65):
                actor.tactics.step(victim,1.0/60.0)
                await settle()
                if tick==28:await capture(actor,label+"_windup_mid")
                if actor.tactics.state=="RECOVER":break
            await capture(actor,label+"_attack")
            if actor.tactics.state!="RECOVER":failures.append(label+" never attacked")
            if actor.global_position!=fixed_position or actor.machine_sprite.muzzle_world().distance_to(fixed_muzzle)>0.001:
                failures.append(label+" anchored geometry drifted")
            var expected_shots:=0 if phase>=2 and serial==1 else (3 if phase==1 else 5)
            if emissions.size()!=expected_shots:failures.append(label+" projectile count mismatch")
            for shot in emissions:
                if Vector2(shot.origin[0],shot.origin[1]).distance_to(fixed_muzzle)>0.001:
                    failures.append(label+" projectile did not originate at iris")
            if phase>=2 and serial==1:
                # Let the frozen ground warning advance normally to damage.
                await settle(45)
                await capture(actor,label+"_ground_warning")
                await settle(45)
                await capture(actor,label+"_ground_impact")
            stage.queue_free()
            for node in root.get_children():
                if node is PrototypeProjectile:node.queue_free()
            await settle(3)
    var hashes: Dictionary={}
    for path in [SPEC,"res://scripts/animation/site7_machine_sprite.gd","res://scripts/actors/enemy_actor.gd","res://scripts/combat/site7_enemy_tactics.gd","res://scripts/combat/site7_attack_warning.gd","res://scripts/ui/enemy_overhead_ui.gd","res://tests/render/site7_anchor_candidate_capture.gd","res://data/art_profiles/enemy_profiles.json"]:
        hashes[path]=FileAccess.get_sha256(path)
    var file:=FileAccess.open(out+"/capture_report.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"CAPTURED_CONTROLLED_PHASES_NOT_VISUAL_APPROVAL","app_registry":use_app,
        "failures":failures,"rows":rows,"hashes":hashes,"phase_health_and_serial_fixtures":true},"  "));file.close()
    print("SITE7_ANCHOR_CAPTURE: ","PASS_CAPTURE_ONLY" if failures.is_empty() else "FAIL"," ",out)
    quit(0 if failures.is_empty() else 1)

```

## FILE: qa/stage1_implementation_20260913/ANCHOR_APP_CHECK_KO.md
SHA256: 254ce8e9abe432f2c758e821286ae9db56ffeb438f20b9c098ef0636f6cc6ad5
```text
# 고정 코어 보스 — 앱 연결 후 확인

2026-09-13, 현재 주 작업 에이전트의 실제 관찰. 사용자/GPT/Luna 승인 아님.

- 기본 레지스트리의 `authored_core_v1/spec.json` SHA256:
  `c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763`.
  원화 SHA256 `c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4`.
- 앱 로딩·고정 몸체·실제 예고 후 발사: 271개 검사 통과.
  `anchor_app_1789289257_709.json`, SHA256
  `7f7ed4122dce4049bd79e2bdea856862cb2d39767d6c4e762fbc5ed09fe10845`.
- 앱 기본 경로의 네이티브 1920×1080 캡처:
  `anchor_native_1789289325_473/capture_report.json`, SHA256
  `010862d5a58bc71aed6b52619aa0f60c136620a83e4bdc248b0aa221759116fd`.
  실제 관찰한 장면은 phase1_attack1_attack, phase2_attack2_ground_impact,
  phase3_attack2_ground_warning이다. 중앙 홍채에서 분대를 향한 부채꼴 탄환,
  지면 공격 후 ASTER 체력 76/96, 원형/교차선 예고와 기둥 위 체력바를 확인했다.
  22장 전체의 해상도/디코딩은 `anchor_app_1080p.json`으로 검사했다.
- 이 캡처는 단계별 HP와 공격 순번을 지정한 촬영용 사례다. 적·분대를 모두
  자유롭게 둔 무수정 플레이 영상이라고 주장하지 않는다.
- 별도로 실제 전투/이동/상호작용을 구동한 `full_operation.json`이 다시 통과했다.
  현재 SHA256 `6eeb71e78af59e4887252f311c8ac853cbef92dad581402f0df49171a51e0f40`.
  HP/탄약 무한화나 살아 있는 적 삭제 없이 탈출했으며 인간 난이도 검증은 아니다.
- 보스 연결 후 드론 앱 회귀도 170개 통과했다:
  `drone_app_1789289734_917.json` SHA256
  `20b4fb501a528ba765e8d35527e204aca50b1cd09d458e0f4be6b8366467ad83`.

이 보스의 범위는 고정 중앙 코어 발사와 기존 3단계 공격이다. 네 팔 개별
회전/발사나 링 뒤집기 동작은 제작하지 않았다. 짧은 headless 시험 종료의
ObjectDB 경고는 미해결로 남긴다. 네이티브 캡처와 전체 경로 시험의 stderr에는
오류가 없었다. 소총병·방패병·변이체 제작 및 전체 MVP 완료와는 구분한다.

```
