# Ponytail FULL — runtime / root-capture / native-alpha batch review

Reviewer: `/root/ponytail_motion_audit` (Ponytail FULL independent reviewer)  
Date: 2026-09-07; runtime binding check: 10:58:11 UTC.  
Scope: read-only inspection of the actual implementations and already-produced evidence. Only this report was written. No new render, engine run, generation, source edit, process control, or Luna task was performed.

## Decision

- **PASS_TECHNICAL_ONLY:** the scoped actual-displacement deadband, normalized movement direction, distance-based phase, same-tick fire-channel selection, and synthetic visible-marker/socket regression.
- **PASS_HARNESS_SMOKE_ONLY:** R2's two-frame root-translation camera and evaluated-vertex binding. This is a synthetic two-plane fixture, not a character or gait approval.
- **FAIL_NOT_PROMOTABLE:** the attempted native-alpha ImageGen output. The checkerboard is painted RGB content, not transparency. The current alpha gate correctly preserves this failure.
- **HOLD — real production handoff:** a newly implemented MICA builder is not in the existing source approval. The new handoff checker exposes this blocker; a reviewed build-plan authorization route is still unimplemented.
- **HOLD:** actual MICA eight-direction walk/run, anatomical/grounding quality, complete movement × aim firing, production HTML, and Astra completion before Luna reproduction. Nothing in this report approves those milestones.

## 1. Actual runtime evidence and independent recomputation

Evidence root: `artifacts/motion_harness_audit/technical_fixtures/combined_c4c7f8d4b3ff45b5bf531d8fc98ce3ea`.

I parsed each raw runtime JSON, not only its score or summary. An independent read-only Python calculation used successive `world_position` differences, `dt`, the fixed 152/224 px/s contract, case IDs, 24-frame walk/run timing, and decoded atlas RGBA bytes. It did not call the harness scorer or runtime functions to generate its expected results.

| Hz | Exact cases | Movement samples | Actual shots | Samples with nonzero speed ≤12 px/s | Stationary shots | Maximum phase error | Maximum shot/visible-marker error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30 | 240 | 15,120 | 1,856 | 158 | 248 | 1.55e-9 cycles | 0 px |
| 60 | 240 | 30,240 | 2,016 | 42 | 272 | 7.75e-10 cycles | 0 px |
| 120 | 240 | 60,480 | 2,024 | 528 | 272 | 2.82e-10 cycles | 0.000123 px |

All 240 expected case IDs occur at each rate. Across 105,840 samples and 5,896 shots, the independent calculation found no mismatch in the scoped deadband/channel/phase/frame checks, movement/aim/mode selection, decoded displayed RGBA frame, same-tick shot association, or shot origin against the actual Sprite2D marker. The per-rate raw hashes match their recorded score references. All 279 snapshot-bound files matched current bytes at the recorded check time, and the snapshot subject recomputed exactly.

The formerly failing `collision_fire/NW` now retains zero phase increment and an empty locomotion channel during collision recovery. Examples include 1.9033 px/s at 30 Hz, 3.6771 px/s at 60 Hz, and 7.6962 px/s at 120 Hz. These remain recorded world-position movements; the runtime suppresses only the visual gait below the existing presentation threshold. It does not erase measured displacement or lower the required walk/run speed.

Execution path reviewed:

- `scripts/actors/operator_actor.gd:234` performs movement/collision/bounds before `commit_actor_displacement` at line 237, then calls `_try_fire` at line 243. The synchronous `primary_fired` signal at line 294 allows the fire clip/socket to be selected before projectile construction.
- `scripts/animation/fast_character_runtime.gd:393` uses `displacement.length() / delta > MOVE_THRESHOLD` with the existing 12 px/s constant. Line 397 passes the normalized actual displacement to sector selection, eliminating the old small-vector direction fallback. Phase advances from actual distance only when that threshold is crossed.
- `tools/character_pipeline/motion_harness.py:871` independently defines the acceptance deadband in px/s. Lines 895–912 recompute phase and displayed frame from actual displacement; lines 913–932 require the correct fire channel and the same physics sample; lines 943–957 compare actual Sprite2D region RGBA and visible marker position.
- `tests/run_combined_runtime_smoke.py` distinguishes walk/run with separate marker pixels; the descriptor uses a nontrivial 1.7 display scale and `[13,-9]` offset. This makes the transform test more meaningful than unit-scale/socket-table equality alone.

Boundary unit-test source was reviewed for 12 versus 12.01 px/s at 30/60/120 Hz and invalid `dt`. I did not rerun those tests in this review. A 32 px synthetic marker atlas cannot establish anatomy, stride quality, footwear orientation, coat continuity, or real barrel-tip alignment. The evidence correctly remains technical-only.

Runtime identity:

- Subject: `f13e10806fca468ad54d2d35c633f58f012f709fbffc2551401570632433f258`.
- Raw 30 Hz SHA-256: `67c5a97e5b0ab08b73d30c6cb51711b1d1c83ef12e9c45712c230658f74d603f`.
- Raw 60 Hz SHA-256: `e96311a2c67e062aec57369b26fc337174700353e103c86d51cd2376f3b65e59`.
- Raw 120 Hz SHA-256: `67128ea69c30c106a53242949c561cb8f425c7689d1735d124da5a70739d27a3`.

## 2. R2 actual world-space root capture

Evidence root: `artifacts/motion_harness_audit/technical_fixtures/blender_root_capture_r2`.

I read the fixture, runner, exporter, capture validator, geometry JSON, render receipt, and result. I also opened both existing native PNGs: they depict the expected two rectangular synthetic sole planes, not a humanoid. Their decoded native dimensions are 1920×1920; runtime derivatives are 384×384.

Independent matrix/vertex and hash checks confirmed:

- Actual ground translation, frame 1→2: `[1.25,-0.5,0]`.
- Actual camera translation: the same `[1.25,-0.5,0]`; its rotation, lens/projection/render fields and camera-relative-to-ground transform are unchanged.
- Each of the eight evaluated world vertices moves approximately `[1.45,-0.5,0.08]` (floating-point differences below 3e-8 m). Thus ground travel remains in world evidence, while the additional `[0.2,0,0.08]` skin movement is not normalized away.
- Each recorded `world_to_body_m` equals the inverse of the actual render ground matrix with scene-unit scaling.
- Both geometry-frame hashes match the exporter's exact JSON serialization. Both native hashes, both runtime hashes, each geometry/runtime image binding, config hash, receipt hash, and current exporter/capture-validator hashes match.

`tests/blender/motion_geometry_smoke.py:41` converts the intended world displacement into the rest bone's local axes before keyframing (line 44). This corrects the documented R1 fixture-axis mistake. R2's camera follows authored ground motion; the exporter does not silently recenter the subject or crop its pixels.

`root_locked_capture.py:21` permits ground translation only: unit/orthogonal ground frame, world-Z up, unchanged orientation, no root bob, exact camera translation, and unchanged camera fields. `export_evaluated_motion_geometry.py:100` validates these observed matrices before each render. `motion_harness.py:749` binds capture space to config and the reviewed pose's camera/body anchor; lines 968–980 revalidate actual per-frame camera/ground and its inverse geometry transform.

The two-pose result does not measure a human gait cycle, stance slip, alternate foot support, all camera directions, or movement × aim firing. These remain HOLD for a real MICA candidate. The synthetic fixture exception is explicit and must not become production authority.

R2 geometry SHA-256: `47310c856ca98a0cf259de4cbe7f4dd7bcc613de8966d239b87c5caad1f81f02`.  
R2 render receipt SHA-256: `41d287253260ff5adc372fc8d91f1b2e6477965048622503a958a1d7937bd0b8`.

## 3. Native-alpha failure is not a PASS

I opened and independently decoded:
`artifacts/quarantine/generation_diagnostics/mica_native_alpha_probe_r1/MICA_C03_S_NATIVE_ALPHA_REQUEST_R1.png`.

Actual result: RGB, 1024×1536, alpha after RGBA decoding 255 everywhere, **0 transparent pixels, 0 partial-alpha pixels, 1,572,864 opaque pixels**. The visible gray/white checkerboard is part of the picture. SHA-256 is `d62d2c9d035cbf2f19b02ef5f079c7e2122aa5730bded1a5bbbc8e28b63bdbed`, matching its retained failure audit. The audit's original pre-quarantine path is historical provenance, not evidence that the image became a current source.

`generation_harness.py:112` requires real zero and opaque alpha, a transparent border, and adequate transparent/opaque coverage. This image independently reproduces the three recorded failure conditions. Even numerically valid alpha returns `HOLD_ALPHA_VISUAL_REVIEW`, never PASS. `audit_source` propagates these errors and rejects transparency inside material masks. `seal_source` and `verify_receipt` still require exact-content independent reviews with all source checks.

The current `sable-motion-production` wording prefers direct alpha only after actual alpha and original-scale light/dark edge review pass; it explicitly rejects painted checkerboards and preserves existing green masters. Therefore this conditional policy does not promote the failed probe or revoke the valid green-source route. Clean alpha edges and body-hole absence were not approved for this failed image.

## 4. Remaining production blocker: source approval is not new-builder approval

This is a real stage-boundary limitation, not a defect in the existing good source art.

The approved `source_front_r1/request.json` binds only `collect_generation_mesh_preflight.py` in `implementation`. `generation_harness.authorize_build` at lines 409–414 requires the actual builder's current hash in source authority bindings. A new genuine MICA 3D adapter therefore fails `GENERATOR_NOT_BOUND_TO_SOURCE_REVIEW`; the collector is not a production character builder. A `source_set` only combines already-reviewed source receipts and cannot authorize arbitrary new code.

The base `next_action` at lines 692–693 still returns `BUILD_ONE_MESH_AND_FIRST_POSE` without a builder argument. I reviewed the new `check_build_handoff.py`: lines 17–25 revalidate source authority and identity and return `AUTHOR_AND_REVIEW_EXACT_BUILD_PLAN` for the unbound builder; line 26 reuses the real authorization check for an already-bound builder. It does not issue an approval or launch a process. The skill now mandates this extra check and honestly states that the separate approval route is not implemented. Runner and direct builder retain their existing hard checks.

Minimal safe next implementation, without reissuing an old ImageGen permit or reauthoring the good image:

1. Keep the original request, permit, source manifest, R3 source receipt and reviews immutable. Create a separate exact-content build plan referring to that receipt, actor/costume identity, actual builder/runner and used helper hashes, licensed body/rig input and license evidence, UAL source/action, approved material regions, permitted shape/costume modifications, output root, and one native first-pose budget.
2. Independently review that plan as a **construction authorization only**. Reuse the existing hash/receipt/review helpers; do not introduce an unrelated general workflow framework.
3. Require the approved plan in both the launching runner and direct builder, verify it before creating work output, and carry it into the mesh/first-pose receipt closure and eventual motion/promotion closure. Edits to builder, body, source, scope or license inputs require a fresh affected plan review.
4. A front-source construction plan permits only the reviewed first-pose scope. It does not approve unseen costume surfaces, eight directional poses, UAL gait quality, native alpha, runtime promotion, or Luna.

There is no honest current-schema shortcut that inserts the new builder hash into an old source receipt, hides code as unrelated review evidence, or regenerates a past permit. Those would change the meaning of source approval. The missing build-plan implementation remains HOLD; this review does not pretend the bridge checker completes it.

Source R3 receipt SHA-256 at review: `0c4288f1f27a70cace7d4eda4d692ee637e2eefaa88a21b4ca27945fba04840f`.  
Handoff checker SHA-256: `f999ae4593afa55691d57522ccbd517d60c8140f29ebc3098f7e55b79e924444`.  
Skill SHA-256: `c1e1863b2be361bd4747e06677091cac553d6d2b830b0a613aa77cb2b82e4d66`.

## Final scope statement

Within the inspected runtime/root/alpha changes, I found no additional concrete P0/P1 contradiction in the recorded evidence. The unimplemented exact-content source-to-new-builder handoff is the remaining confirmed production blocker in this review. Actual MICA construction, full gait/grounding and firing review, final HTML, Astra production completion and Luna reproduction are not approved by this report.

Applied: Ponytail FULL independent review semantics and `sable-motion-production`. Only the assigned report was added; existing failed assets, source approvals, implementation files and other agents' work were left unchanged.
