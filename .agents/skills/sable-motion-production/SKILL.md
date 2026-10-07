---
name: sable-motion-production
description: Inspect historical SABLE production-gate receipts only when the user explicitly requests the legacy pipeline. Current character creation, repair and Motion Studio work use sable-character-studio instead.
---

# SABLE character production

## Historical route only — 2026-09-10

For current character or Motion Studio requests, stop reading this historical
procedure and use `../sable-character-studio/SKILL.md`. The user replaced this
route with the working `motion_lab_v1` implementation. Preserve the material
below for explicit legacy audits; do not invoke its old jobs for new production.

Work from the repository root containing `project.godot` and
`tools/character_pipeline/generation_harness.py`. All artifacts, caches, failed
attempts and evidence stay inside that project. This skill does not authorize
external services, new models, deployment, or deletion beyond the user's request.

## Resume without guessing

User-ordered validation sequence: **Astra actual production and all required
reviews first → freeze the proven harness/skill → Luna reproduction test**.
Do not delegate exploratory generation or further forward tests to Luna before
Astra's real candidate succeeds. A read-only routing test is not that milestone.

1. Read project `AGENTS.md`, then
   `docs/production/GENERATION_GATES_2026-09-07.md` in full.
2. Find the current job JSON in the active character's project work directory.
   If none exists, create the minimal job described in `references/job-format.md`.
   Do not infer current status from the newest filename or an old chat's PASS.
3. Run `python tools/character_pipeline/generation_harness.py next --input JOB`.
   Follow `allowed_next_action`. Nonempty `errors`, HOLD, missing files, or stale
   hashes are not permissions to skip forward. `next` is read-only.
4. Perform one permitted production step, save exact hashes to a **new revision**
   of the job, then run `next` again. Do not run an unreviewed full eight-view batch.
5. Record what was actually checked and the next artifact needed. Never claim
   “ready for Luna” or “character complete” from syntax/unit tests alone.

For all new ImageGen-authored motion-frame work, run
`tools/character_pipeline/visible_frame_harness_current.py`: reserve and review one
direction/phase before another output. A full candidate needs 64 distinct,
exactly reviewed frame receipts (8 directions × 8 named phases). The resulting
sequence is still HOLD until temporal gait, firing, runtime-rate and HTML-parity
gates pass.

`visible_frame_harness.py` is the frozen verifier used by already sealed
airborne receipts. Do not call it directly for new work. The current entrypoint
patches the fixed-floor contact audit into request, reserve, frame, seal,
receipt verification and sequence closure without invalidating those receipts.

Before approving or using any Blender+UAL contact/down/passing guide, run
`tools/character_pipeline/calibrate_vrm_ual_ground_contact.py` against the exact
retarget result and bind its fresh report. The fixed floor comes from actual
sole vertices in the licensed target's neutral REST pose before UAL evaluation;
the action's own global sole minimum, an IK target, a socket table, or a declared
contact flag may never define ground truth. Any floor penetration, foot-axis
yaw violation, duplicate phase sample, missing bilateral flight window, or
non-distinct contact/down/passing event is HOLD and blocks the ImageGen request.
Do not apply a per-frame root offset to manufacture contact. Airborne guides
still need their exact independent lower-body review; they do not waive this
calibration for the remaining phases.

Technical phase discovery is not contact promotion. For every support phase,
also bind `tools/character_pipeline/pose_guide_visual_promotion_contract.json`
through `visible_frame_harness_current.py`. The actual supporting sole must be
at most 4 mm above the independently fixed floor, and each down phase must put
the evaluated pelvis at least 15 mm below its same-side contact phase. The
current entrypoint, technical contract, visual-promotion contract, calibrator,
calibration rows, capture rows, actual sole arrays and fixed floor must all be
exactly hash-bound. A different valid JSON or script is not an equivalent
input. Independent visual plus Ponytail FULL contact-review bundles are still
required after the numeric thresholds pass.

Use the support-foot phase convention in
`tools/character_pipeline/visible_frame_contract.json` literally. In particular,
`flight_l` means flight **after left support/toe-off**, so the right leg leads;
`flight_r` means flight **after right support/toe-off**, so the left leg leads.
Never infer a phase name from the lowest sole or from the leading leg alone.
The exact phase definition must be present in the request, prompt, licensed
Blender/UAL pose guide, and its independent visual + Ponytail FULL reviews.
Review the complete captured action cycle before approving any individual guide.
For an asymmetrical costume, bind anatomical left/right to immutable visible
costume markers in both the request and prompt, then verify those same markers
in the output annotation and independent reviews. Screen-left/right, filename,
or an unverified annotation cannot establish anatomical laterality.

Source PASS alone does not bind a newly written builder. `next` now requires an
exact `build_plan` and independent `build_receipt` before the mesh stage, even
when a previous mesh file exists. Preserve the approved image and original
permit; review the new builder handoff, not another ImageGen attempt. Never
insert an unreviewed script into an old receipt's hash table. Read the build-plan
section in `references/job-format.md`. The old `check_build_handoff.py` is a
historical diagnostic and is not the new execution entrypoint.

Read `references/job-format.md` before writing a request, source annotation,
semantic mask manifest, or review bundle. Read
`references/rig-and-motion.md` before changing a rig, importing VRM, retargeting
UAL, calibrating stride, or exporting animation.

For a user-supplied Tripo Run GLB, read `references/tripo-motion-reference.md`.
This provisional standing/body-reference inlet preserves native rig/mesh/action
data and exposes actual sampled joints to SABLE's motion harness. It does not
replace ImageGen appearance or establish a completed Astra/Luna production route.

## Authoritative division of work

- ImageGen: original/repair raster art, identity, costume, missing pixels.
  Reuse approved source when it is correct. No local diffusion or inpainting.
  Prefer direct `transparent_alpha` source after actual alpha and original-scale
  light/dark edge review pass; no mandatory green intermediate. Preserve the
  generated alpha, reject painted checkerboards, matte halos and body holes.
  Keep existing green masters; use green only if clean native alpha fails.
  A painted transparency checkerboard is a generation failure. Never infer
  that enclosed white/gray components are background by size or colour: they
  may be costume lights or metal. Only edge-connected matte normalization is
  automatic; ambiguous enclosed components require a new ImageGen output.
  When a green master is required for a costume that excludes chroma green, derive runtime
  RGBA with `derive_chroma_runtime_rgba.py`. Include dark low-luminance chroma
  fringe in the removal rule; a threshold that catches bright green but leaves
  dark green pixels at weapon/coat/boot edges is a visual FAIL. A visible-frame receipt must bind
  both the preserved green master and the reproducible runtime RGBA, prove a
  transparent border, zero unmistakable strong-green residuals on the alpha boundary, and byte-exact
  retained RGB. An edge-connected mask alone cannot approve closed background
  holes between limbs or weapon parts.
- Blender + UAL: rigging and deformation of approved ImageGen pixels/layers,
  skin weights, pose transfer, licensed retargeting, contact/cadence calibration
  and pose-guide export while preserving approved ImageGen appearance. Do not
  sculpt/rebuild a replacement
  face, eyes, hair, costume, boots or weapon, even with an approved ImageGen
  swatch attached. No primitive/constant-material appearance reconstruction.
  Missing visual content is ImageGen work, not a local modeling workaround.
  A locally rendered generic/VRoid character is pose-guide evidence only and
  must never become final visible character pixels, an atlas, or a runtime asset.
  A final visible frame is either a deformation of exact approved ImageGen art,
  or a separately approved ImageGen pose authored from a Blender/UAL guide.
  A Blender workbench/rendered VRM body is never the original illustration and
  never a deliverable appearance layer; it may be referenced only for pose,
  joint, cadence and contact geometry. The ImageGen request must explicitly
  forbid copying the guide model's face, hair, costume, body surface, weapon,
  colors, materials and accessories.
  Never
  animate a static leg cutout by shifting pixels, rotating calf planes, or
  stretching coat rectangles. A semantic label cannot make a plane anatomical.
- VRoid: user-authorized optional **motion/body-rig reference** inlet, not
  authority to replace a character's visible appearance. Installed
  Studio and VRM add-on do not mean a model's license, appearance, or UAL mapping
  is approved. Use the intake checker and references before adopting a model.
- Godot: actual actor/input/shot validation. HTML must share the reviewed runtime;
  do not invent a second movement speed or independent projectile origin.

## Gates that cannot be traded for one another

| Evidence | What it permits | What it does not permit |
| --- | --- | --- |
| Valid request + single-attempt permit | One ImageGen source attempt | Source/pose approval |
| Source technical checks | Independent source review | Rig batch or visual PASS |
| Source receipt | Review exact builder/runner/input/output plan | Running unbound new code |
| Art-preserving adapter + build-plan receipt + one reservation | Motion rig setup and one appearance-preservation pose | Reauthoring appearance, animation batches or retries |
| Actual mesh preflight + native first pose | First-pose visual/Ponytail review | Any other direction |
| Exact first-pose receipt | One bounded clip in the approved view | Gait/runtime PASS |
| All generation, gait, runtime, visual, Ponytail and web gates | Exact candidate promotion | Renamed rejected assets or unrelated files |

Use the existing Ponytail FULL reviewer for independent implementation and
visual checks when available and authorized. Feed the actual bound evidence,
not only the generator's summary. If the reviewer is unavailable, record HOLD;
continue independent tests/repairs, but do not fabricate its approval.
Use the user's authorized existing ChatGPT web conversation for the final
motion review; never create a ChatGPT Work task as a substitute.

## Failure handling

The anatomical/skinned MICA reconstruction builders are retired after the
2026-09-07 user correction. `art_authority.py` blocks their paths/content and
requires a separately implemented/reviewed source-preserving motion adapter.
Do not edit an allowlist simply to make `next` advance. A scope failure routes
to `REPAIR_MOTION_ADAPTER_WITHOUT_REAUTHORING_ART`, not another source generation.
Read `references/art-motion-boundary.md` before repairing that boundary.

Keep the failed output plus source, masks, scene, config, logs and evidence in
project quarantine. Preserve path/hash inventory when moving it. Do not delete
until the user's final-replacement disposal gate is actually satisfied.

- Wrong entire-body direction: repair the source direction, not only the gun or
  pelvis. E/W require matching hip, knee and boot direction.
- Ghost hand, green band, swollen calf: inspect the source region and actual
  UV triangle interiors. Never “fix” it by nearest non-green-pixel sampling.
- Detached waist/coat: repair rig attachment or obtain missing ImageGen art;
  do not remodel its visible appearance. Do not hide it with
  a rectangular overlay or tighten the camera crop.
- Bad foot arc/stride: fix UAL retarget/unit/contact timing using evaluated
  soles. Never lower a threshold or call intended IK targets measured feet.
- Misnamed gait phase: quarantine the affected request/output, correct the
  phase convention in the shared contract, prompt and runtime mapping together,
  then recapture the entire licensed action cycle. Renaming a file or receipt
  does not repair the motion semantics.
- Stale approval: re-collect affected evidence and obtain a new review. Do not
  edit only the receipt hash, review verdict, or date.
- Two attempts failing the same category: stop generating further variants.
  Reproduce that failure with a small diagnostic, obtain an independent cause
  review, and change the failed mechanism before the next production attempt.
  For a localized ImageGen-authored costume/laterality defect, the changed
  mechanism may be an explicit `repair_failed_frame` request that binds the
  quarantined raw target, its failure manifest, anatomical marker contract and
  a fresh one-output permit. Never relabel or directly promote the failed image.
  The repair target also needs an independent scope review, a disjoint exact-
  preserve list and minimal-change list, and a hash match against its own
  quarantine inventory. Prefer a target that already visibly satisfies the
  requested anatomical phase rather than asking ImageGen to swap legs. The
  review subject must bind the exact prompt, source receipt, previous failure,
  target inventory and ordered ImageGen inputs so text or input-order changes
  invalidate it. The edit must produce a new project-local raster; the target
  stays quarantined.

  A prompt, reference image, or reference mask is not an enforced edit mask.
  Before `finalize_reviewed_visible_frame_repair_request.py` may reserve a new
  `repair_failed_frame` attempt, require the exact
  `imagegen_repair_execution_contract.json`, a nonempty binary mask at the
  target's native size, proof that the selected generator consumes that mask,
  byte-immutability outside it, and independent implementation plus Ponytail
  FULL review. The current built-in ImageGen edit call has no demonstrated
  hard-mask parameter, so another prompt-only repair stays HOLD. Do not relax
  pixel/ground thresholds or reinterpret a reference mask as that capability.

  Blender+UAL may supply joint/contact geometry for a source-preserving motion
  adapter, but never visible guide-model pixels. Extract those joints with
  `extract_vrm_ual_projected_joints.py` and bind the exact blend, calibration,
  capture and extractor hashes. A geometry-only projection is not adapter,
  gait or visual approval.

## Before handing off

Run the tests appropriate to changed code, then the required **real** candidate
checks. Technical fixtures are marked synthetic and cannot become source art.
Do not mark completion while native gait, muzzle, 8×8 aim/move, 30/60/120Hz,
HTML live-input parity, or independent reviews remain HOLD/FAIL.
Stop only owned task children when they finish; never terminate unrelated
VRoid, Blender, Codex or browser processes by name.
