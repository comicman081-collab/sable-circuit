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
