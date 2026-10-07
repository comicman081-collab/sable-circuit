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

- **User-authorized VRoid/VRM or Kimodo motion assistance:** read
  [the local motion-assistance route](references/local-motion-assistance.md).
  This supplements the existing Studio; it is not a replacement appearance
  pipeline, automatic source approval, or a reason to rebuild accepted players.
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

- **Enemy scope (2026-09-19 user update):** ZERO humanoid enemies, including
  `site7_rifle`. The user cancelled their production to save resources. Do not
  resume their source slots or gait; retain them as retired provenance only.
  Human biped work is for playable characters. Shield and old aberrant roles become
  legless robots; do not resume `site7_shield` gait or create robot bipeds or
  quadruped cycles. Only reviewed drone/boss are active; old humanoid slots use
  the existing drone until robot replacements are reviewed. Read `data/art_profiles/site7_enemy_body_plan.json` and
  the enemy-facing reference. Existing playable characters are unaffected.

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
  provide pose/contact only. New masters must be actual RGBA PNGs: background
  alpha 0, visible alpha 1..255 and opaque interiors (alpha 255 allowed since
  the user's 2026-09-28 instruction). Run
  `source_alpha_policy.py` on the returned master. Green/chroma generation or
  fallback and locally clamped/keyed substitutes are forbidden by the user's
  2026-09-13 correction. Retain exact historical approvals and failed candidates.
  Every appearance or pose reference passed to a generation request must resolve
  inside this SABLE repository and match the recipe's identity reference;
  `source_alpha_policy.require_project_reference` rejects another project,
  another SABLE character, Codex staging, clipboard and locked-tool paths. The
  managed ImageGen return path is allowed only as a newly generated output that
  is copied into the project and bound to its actual response. Retain exact
  historical approvals and failed candidates.
  If the user explicitly authorizes the fallback, `web_alpha_bridge.py` may
  register one failed Luna green/near-green result as
  `WEB_ALPHA_BRIDGE_ONLY` in quarantine for the existing GPT web conversation
  to remove the matte. The bridge never keys, crops or intakes that source;
  preserve the actual web response and admit its returned file only after the
  native RGBA alpha gate passes. This exception does not permit unrelated
  images, local conversion, or direct green-source promotion.
  Keep original sources; inspect identity, anatomical
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

When the user explicitly selects Luna Max, use one bounded `gpt-5.6-luna`
attempt for the named slot with the current reasoning setting. Validate the
project-owned reference list before the call and the native-alpha source after
the return. A wrong-project image, RGB/checkerboard return or alpha-gate
failure is a quarantined HOLD; it does not authorize another blind attempt.
Only an explicit user instruction can open the green bridge described above;
it remains a quarantined handoff until a GPT web return passes the same native
alpha gate and the source/response hashes are recorded.

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
