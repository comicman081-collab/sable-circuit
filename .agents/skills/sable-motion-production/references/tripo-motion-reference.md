# Supplied Tripo Run GLB: provisional body/motion inlet

Use when the user supplies an already-generated paid-plan GLB for SABLE motion.
This path makes a reusable Blender reference pack; it is not a proven complete
character production procedure and does not enable Luna reproduction.

Current exact input: `art_src/motion_reference/tripo_run_20260908/source/ORIGINAL_Run.glb`.
It was retrieved from the user's `세이블 서킷 코덱스 전달` ChatGPT attachment and
copied byte-for-byte. Read its `MODEL_LICENSE_MANIFEST.json` and evidence.
No new Tripo generation/API request is required or authorized by this inlet.

Resume with the companion job in that directory:

```powershell
python tools/character_pipeline/tripo_motion_reference.py next --input art_src/motion_reference/tripo_run_20260908/motion_reference_job_r01.json
```

The companion router calls existing generation `next` and verifies the reference
pack independently. Reference intake cannot override retired builders, source/
first-pose approvals, contact/HOLD, or production-pointer rules.

For another explicitly supplied GLB, inspect and license-bind actual skin,
weights, roles and timestamps before `tripo_motion_reference.py build`. The
current adapter supports the provided Tripo 41-bone schema; other rigs need an
adapter. The launcher requires a fresh project reference directory; Blender
requires exact execution inputs plus an exclusive consumed child claim.
Failed partial attempts are preserved. `disable_bone_shape=True` avoids counting
the importer's hidden Icosphere custom-bone display object as source geometry.

The pack contains `SABLE_REFERENCE_Standing_NativeBind` and the unchanged
`preset:biped:run.001` action assets. Native bind matrices, vertices, weights,
UVs and packed textures remain intact. Its single 1.70m global scale is a stated
working convention, not a claim that actual character height is known. The
original imported-unit scene is separate. Native standing does not promise a
symmetric grounded neutral pose, T-pose, undressed body or anatomical rebuild.

Source frames 1..31 at 24Hz are 1.25 seconds. Root is stationary while Hip
translates. Do not infer zero world motion from Root or call the whole action one
cycle. Preserve actual final samples and inspect cycle boundaries before trimming.
The original neutral soles differ by about 32.39mm at the 1.70m convention;
Run sole minima are about 9.97mm/40.32mm above the original REST floor. These are
diagnostics, not contact-approved pose guides.

`bridge` exports eight rotations of actual joint coordinates and binds the
independent ASTER/ROOK/MICA speed contract. It does not supply walking, backward/
strafe running, 8×8 firing, ImageGen pixels or a runtime atlas. Its linear planar
reference origin is only a retarget coordinate transform; raw world samples stay
preserved. Do not use it to manufacture contact or lower required game speed.

Use `CALIBRATOR_INPUT.json` with the existing contact calibrator for diagnostics;
keep Tripo-versus-UAL provenance explicit. Camera-derived travel and one-cycle
exact-wrap assumptions are not generalized to this translating multi-stride clip.
Raw HOLD cannot authorize a visible-frame request.

`tests/test_tripo_motion_reference.py` checks intake/receipt failures.
`tests/blender/verify_tripo_reference_pack.py` reopens saved files, reproduces
49 sole samples, compares original Run curves, mesh/UV/skin and packed texture
bytes, and checks consumed-child rejection. All future visible SABLE frames
still use `visible_frame_harness_current.py` with independent review.
