# Generation job and evidence format

Run commands at the SABLE repository root. JSON paths in this reference are
project-relative, never model/runtime directories. `{path, sha256}` means the
actual current file SHA-256; use `generation_harness.ref()` to produce it, not
a remembered digest. JSON does not allow NaN, Infinity, or comments.

## Job

Minimal job fields: `schema: 1`, exact `actor_id`, exact `costume_id`.
Add only the stages actually present, in this order:

`request → permit → source_manifest → source_receipt → build_plan → build_receipt → mesh_preflight →
pose_bundle → pose_receipt → motion_descriptor → motion_receipt`.

Every stage value is a `{path, sha256}` reference. A job is a small resume record,
not an approval. Use `job_r01.json`, `job_r02.json`, etc.; preserve predecessors.
`next` checks actual files and stage relationships, not presence of a field alone.

## Request, before using ImageGen

Required request fields:

- `schema: 1`, `generator: built_in_ImageGen`, `actor_id`, `costume_id`.
- `output_root`: character work directory under `art_src/characters`.
- `max_unreviewed_outputs: 1`, explicit `background: transparent_alpha`
  (preferred after a clean-alpha probe) or `uniform_chroma_green` (fallback).
- `prompt`: reference to the complete prompt text file.
- `references`: file references with `role`; at least one `identity_authority`.
- `implementation`: references to every consuming generator/adapter script.
- `views`: each has `id` (E/SE/S/SW/W/NW/N/NE), `body_facing` equal to `id`,
  `projection: orthographic`, `pose: neutral_rig` or `neutral_combat`,
  `minimum_canvas` (actual width and height, each ≥1024), and `regions`.

Use one direction per attempt when a multi-view sheet would make each figure
too small. A portrait request such as 1024×1536 must still provide ≥1024 actual
subject pixels from head to ground. Requested resolution is not returned
resolution. Do not upscale a failed return to pass this test.

The prompt locks adult identity, exact costume, complete visible body, true
whole-body direction, neutral stance and the requested native alpha or flat
green background. Require no overlapping
hands over a region intended as cloth texture. Do not ask ImageGen to invent
the entire gait cycle, bones, UVs or collision geometry.

Commands:

```powershell
python tools/character_pipeline/generation_harness.py request --input REQUEST
python tools/character_pipeline/generation_harness.py reserve --input REQUEST
```

Use the returned `permit` in the job and source manifest. Call ImageGen once,
with the request's references and prompt. Verify the project copy/hash before
removing only its corresponding managed staging copy. This CLI cannot intercept
the built-in tool itself: respecting one attempt before review is also an agent
workflow obligation. Renaming the same request does not create a new permit.

## Source manifest and annotations

Source fields: `actor_id`, `costume_id`, `source_author: built_in_ImageGen`,
`request`, `attempt_permit`, `views`, `regions`.

Each view: `id`, `image` reference, `annotations` reference, exact `native_size`,
and `panel: [x, y, width, height]` in **top-left image pixel coordinates**.
One request/permit may cover multiple panels in the same returned image, not
several independently generated images.

Annotation fields: exact `image_sha256`, `body_facing`, positive
`metres_per_pixel`, and `points`, each a two-number pixel coordinate:

`head_top, ground, hip_left, hip_right, shoulder_left, shoulder_right,
heel_left, heel_right, toe_left, toe_right`.

Left/right are anatomical, not screen halves. For unwarped upper art, also
annotate `waist`. Measure from the source itself. Review the marked source at
original scale inside native 1080p evidence; landmarks are not independent
anatomical truth merely because they are numbers.

Each region: unique `id`, `view`, `mask` reference, `exclusions` references,
`purpose` (`volumetric_texture` or `unwarped_upper`), `allowed_mesh_parts` names.
Masks match source dimensions and use white inclusion/black exclusion. The
region must not contain chroma/transparent background, a foreign hand, another panel, or unrelated
clothing. Upper masks stop at the annotated waist. Keep useful excluded-hand
masks as separate evidence so “nearest foreground” cannot silently copy a hand.

```powershell
python tools/character_pipeline/generation_harness.py source --input SOURCE --out SOURCE_AUDIT
```

No errors still means `HOLD_SOURCE_VISUAL_REVIEW`.

Native alpha must contain real transparent background and opaque subject pixels,
with a clear canvas border. Review `clean_subject_separation` on both light and
dark compositions at original scale: fine hair, fingertips, coat/boot edges,
matte halos and body holes. Alpha statistics alone never approve those details.
Preserve the original RGBA bytes; no extra keying or forced-opaque conversion.
Semantic material masks select opaque pixels, not antialiased silhouette edges.

## Independent review and source composition

A source review bundle has `source_manifest` reference and `reviews` array.
Each review has `role` (exactly `visual` and `Ponytail FULL`, one each), reviewer,
reviewed_utc, subject_sha256 from the audit, verdict, checks and reply_evidence.
`checks` must contain all keys from `generation_contract.json`'s
`source_review_checks`, individually assessed. `reply_evidence` is a reference
to the actual review reply. Never write a reviewer PASS on their behalf.

```powershell
python tools/character_pipeline/generation_harness.py seal-source --input REVIEW_BUNDLE --out SOURCE_RECEIPT
```

To reuse several **already approved** images, create a source-set JSON:
`stage: source_set`, `receipts: [source-receipt references]`. All must have the
same actor and costume. Different images may cover the same direction for
different purposes. Composition does not waive any source review.

## First-pose review

Read `art-motion-boundary.md`. This stage sets up motion while preserving
ImageGen appearance; it no longer permits reconstructing a visible character.

Before constructing the mesh, write a `schema: 1, stage: build_plan` JSON with:

- actor_id, costume_id and exact approved source_receipt;
- `art_authority: imagegen_visuals_blender_motion_only`, explicit
  `local_operations` from `art_authority_policy.json`; these labels alone do
  not pass the policy's exact reviewed executable-closure check;
- builder, runner, scope text and dependencies as actual file references;
- source_images as a nonempty exact subset of those approved sources;
- readonly_inputs entries `{asset: ref, license: ref, readonly: true}`;
- one approved source direction and a fresh character output_root;
- limits `{max_native_poses: 1, max_motion_frames: 0, threads: 2,
  timeout_seconds: 240}` (shorter time/lower threads permitted).

Dependencies include the actual collector, helper scripts and runtimes used.
License file presence alone does not establish commercial permission. Review
meaning and exact selected model scope, then implementation behavior.
`build-plan` audits this file. A review bundle contains `build_plan` and two real
reviews, roles `implementation` and `Ponytail FULL`, covering the exact
`build_review_checks` and audit subject. `seal-build-plan` issues the receipt.
Do not fabricate review replies or treat a synthetic fixture as a production
license, source or builder approval.

Run `reserve-build --input BUILD_RECEIPT`. Execute the exact reviewed runner
with that receipt and returned attempt. Both runner and Blender child call
`authorize_build` with receipt/attempt/direction, then claim their own entrypoint
once. A failed/crashed attempt is spent; preserve it and review a new plan.
Never rerun an old command against a used output directory.

The builder records receipt/attempt refs inside the actual scene's
`generation_mesh_contract.construction`. The collector carries them into its
raw output. `CONSTRUCTION.json` records the same refs, saved blend, both actual
execution claims, and rehashed unchanged readonly inputs. A production pose
bundle must reference it via `construction`. The gate binds those inputs and
requires actual textures and all constructed outputs to stay in approved scope.

The old anatomical and skinned MICA pilot scopes/receipts are retired historical
evidence. `imagegen_art_preservation` is mandatory in each build review. Never
renew their scope merely with a new hash or add a renamed builder to the adapter
registry. A new permitted adapter must prove actual source appearance preservation
and motion-only behavior before its executable closure is registered.

The Blender collector writes actual `MESH_PREFLIGHT_RAW.json`. It must not be
hand-authored from expected coordinates. A pose bundle contains:

- `source_receipt`: approved source or source-set reference.
- `mesh_preflight`: actual collector output reference.
- `construction`: actual build/attempt/entrypoint/input record reference.
- `views`: **exactly one** item, with `id`, `image` and `render_receipt` references.

The renderer's same-process receipt binds image, `.blend`, view, scene/camera
fingerprint, and mesh preflight. Run `pose-bundle`. After technical checks are
clean, request both independent reviews against the audit's subject hash and
`pose_review_checks`. The review wrapper has `pose_bundle` and `reviews`.
Run `seal-pose` to obtain the scoped receipt. A front receipt never approves a
side or diagonal view, and a first pose never approves locomotion.

## End of pipeline

Keep one first-pose receipt per direction. Packaging specifies those eight paths
as `motion_build_roles.generation_receipt`; it carries the full hash closure.
The existing motion harness still requires measured gait, actual runtime input,
visible muzzle observations, native visual evidence, web/Ponytail review and
an exact promotion receipt. A generation receipt alone cannot change runtime.
