# Authoring and repairing a character

All commands below run from `motion_lab_v1`; replace `ID` with the actual
requested character, never infer permission to start a different one. Use the
installed Python at `C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe`; it has
Pillow, NumPy and OpenCV. Do not modify that environment. Set `TEMP`, `TMP` and
any helper cache/output directories to a created directory below this lab;
set `PYTHONDONTWRITEBYTECODE=1` before executing installed Python tools.

## Create and advance

1. Inspect the supplied identity/master, including its original-scale costume
   markers and weapon. The identity and every pose guide must already be inside
   this SABLE repository and must match the recipe identity reference;
   `source_alpha_policy.require_project_reference` rejects another project,
   another SABLE character, Codex staging, clipboard and locked-tool paths. Use
   `new_character.py --id ID --name NAME --reference PATH` to copy that input and
   create the recipe plus exact request list. Add
   `--run-art` only when dedicated running art is requested. The scaffold never
   calls a generation service or copies MICA character pixels.
2. Read [the enforced cycle gate](cycle-review.md). Run `character_workflow.py handoff --character ID` and validate its printed
   packet with `verify-handoff --packet PATH`. `status` prioritizes known repair
   verdicts, then the complete E pilot before other directions. For a repair, existing
   exact-content approvals remain valid; only replaced/failed inputs need new
   review. Do not change frame counts or speed to make missing artwork pass.
3. Use the exact request's appearance reference and existing UAL pose guide in
   one built-in ImageGen attempt. Prefer one character per output. As of the
   user's 2026-09-13 correction, require actual RGBA PNG output with background
   alpha 0 and visible alpha 1..255; subject interiors stay opaque (alpha 255 is
   allowed since the user's 2026-09-28 instruction).
   Run `source_alpha_policy.py --source ACTUAL_RETAINED_MASTER` before intake.
   Inspect light/dark backgrounds and interior opacity. A green/chroma backdrop,
   painted checkerboard or failed separation requires another native
   alpha candidate. Never fall back to green or locally clamp/key the returned
   pixels and call that native-alpha generation.
   If (and only if) the user explicitly authorizes the fallback, retain the
   failed green/near-green result in quarantine and run `web_alpha_bridge.py`.
   Send that single project-owned file to the existing GPT web conversation for
   matte removal. The bridge is evidence only: do not key, crop, redraw or
   intake its source, and admit the returned web PNG only after the same native
   RGBA alpha gate passes.
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

   Keep a noncompliant result and its actual response as a failed candidate.
   `intake_frame.py` and `intake_pair.py` now inspect the native master before
   changing a slot. `intake_derived_frame.py` rejects new green-derived intake.
   Its historical verifier remains available only to validate existing exact
   green-master/provenance relationships; it is not a source-generation option.
   Exact existing approved slots keep their reviews. New or changed unapproved
   masters must meet the current native-alpha gate before source approval.

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
