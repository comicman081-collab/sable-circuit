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
