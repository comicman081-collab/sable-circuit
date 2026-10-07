# Astra-first production and verification status — 2026-09-07

**Overall: IN PROGRESS / not MICA-complete / Luna reproduction HOLD.**

## Current resume checkpoint — supplied Tripo motion reference (2026-09-08)

The historical anatomical reconstruction plans below remain retired; do not
resume their builders. `rigged_v2/job_r12.json` still correctly returns
`REPAIR_MOTION_ADAPTER_WITHOUT_REAUTHORING_ART`.

The new companion resume job is
`art_src/motion_reference/tripo_run_20260908/motion_reference_job_r01.json`.
Run `tripo_motion_reference.py next --input` on that exact job. It verifies the
new standing/body pack independently and calls the original generation router.

The user's paid Tripo Run GLB is preserved byte-for-byte. Current `pack_r03`
contains native Standing and unchanged Run actions, source/normalized scenes,
humanoid role mapping, actual sole IDs and 49 native-time samples. The joint
bridge binds all eight directional coordinate transforms plus ASTER/ROOK/MICA
speed requirements. It supplies geometry only, never SABLE character pixels.

Eleven regressions, saved Blender reopen/integrity checks and 53 native visual
container checks passed. Independent Ponytail FULL approved reference-pack
implementation and corrected capture framing only. Exact QA/reviews are bound
in the companion job and `DELIVERY_MANIFEST.json`. Prior failed/clipped attempts
are retained with rehashed quarantine inventories; no failed asset was deleted.

Contact remains HOLD: native REST sole-level delta approximately 32.39mm at the
explicit 1.70m reference convention; Run minima approximately 9.97/40.32mm above
that fixed floor. Hip travels approximately 4.92m while Root stays stationary.
The supplied translating action still needs proper cycle/trajectory/contact
adaptation. No actual SABLE motion/runtime/appearance promotion or Luna success
is claimed. Read `docs/production/TRIPO_STANDING_REFERENCE_2026-09-08.md` next.

The user requires Astra to generate and implement a real successful candidate,
then freeze that proven harness/skill, then test Luna reproduction. An earlier
Luna read-only routing exercise generated nothing and does not meet this milestone.
No further Luna generation or forward tests were started after that correction.

## Completed bounded engineering checks

- Generation gate: 36 regression tests passed.
- Motion gate: 27 regression tests passed.
- VRM intake: 7 regression tests passed.
- Actual Blender generation counterexamples: 6 checks passed in
  `artifacts/generation_harness_audit/technical_fixtures/409b1de049e74e61a0ee4b0414029beb/result.json`.
- Actual paired native render/evaluated skin export passed in
  `artifacts/motion_harness_audit/technical_fixtures/generation_bound_export_20260907/test_result.json`.
- Candidate packaging/promotion-guard smoke passed. Project skill format passed.
- Ponytail FULL reviewed the three final approval-chain fixes; see
  `PONYTAIL_CODE_REVIEW_20260907.md`. This is code approval, not character approval.

All synthetic test work remains diagnostic. No test receipt authorizes art.

## Actual licensed geometry work performed by Astra

- Downloaded official Seed-san VRM, exact SHA
  `624d0d554bc205bbdc33e22a68a2c3c20edebb3e573011ead8878a65e5329b23`.
  Exact embedded commercial/derivative conditions, upstream license and required
  VirtualCast credit are recorded in `third_party/vrm/seed_san/`.
- Loaded the read-only installed VRM add-on 4.6.0 under its MIT option, using
  Blender 5.2.1 in a bounded offline child with project-local caches.
- First import was rejected because a startup Cube remained. Corrected startup
  isolation; `seed_san_import_astra_r2/completion.json` verifies 5 actual skinned
  meshes, 51 humanoid roles, unchanged original model/add-on and child exit.
- Retargeted UAL Walk_Loop to the actual humanoid, not image-plane legs. The wear
  mesh has 18,781 vertices/23,374 polygons; tracked 54 real sole vertices per foot.
- Saved action replay exactly reproduced the sampled vertices in this probe.
  Forward centroid excursion is approximately 0.689m per side with alternating
  forward foot positions. These are actual geometry observations, not IK targets.
- Ponytail detected r2 timing compression (32 source frames → 24 target frames).
  r3 preserves source and baked duration at 1.333333s; r2 remains rejected evidence.
- First native 1920×1920 pose shows connected volume in the legs/ankles. It is a
  gray Workbench anatomy view of Seed-san, **not new MICA source art or costume**.
- Captured r3 from the saved scene: 32 distinct rendered frames plus a wrap
  sample at native 1920×1920. Encoded at the original 24fps, repeating that single
  observed 1.333-second cycle three times into a 4-second diagnostic video.
  `seed_san_ual_astra_r3_cycle_r2/video_manifest.json` records exact hashes and
  repetitions. Its `native_video_validation.json` passed decoding/resolution,
  not gait or runtime quality. This is still in-place, not speed/contact approval.
- Ponytail rechecked r3 timing, exact files, native poses and replay geometry;
  limited retarget/reproducibility PASS only. Nine common times in reloaded
  capture match the prior baked sole vertices exactly. Full character/gait
  remains HOLD; see `PONYTAIL_VRM_PROBE_R3_REVIEW_20260907.md`.

Diagnostic paths share prefix:
`artifacts/quarantine/generation_diagnostics/`.

```powershell
python tools/character_pipeline/run_vrm_import_probe.py --model third_party/vrm/seed_san/Seed-san.vrm --license third_party/vrm/seed_san/MODEL_LICENSE.json --out artifacts/quarantine/generation_diagnostics/NEW_IMPORT_REVISION
python tools/character_pipeline/run_vrm_motion_probe.py --import-result artifacts/quarantine/generation_diagnostics/seed_san_import_astra_r2/import_result.json --out artifacts/quarantine/generation_diagnostics/NEW_RETARGET_REVISION
```

Outputs must always use fresh revision names. Do not overwrite old evidence.

## Still required before the Astra → Luna milestone

1. Ground-referenced and speed-calibrated walk/run contact, heel/toe and knee/ankle
   review across real continuous cycles, not just one pose or intended matrices.
2. MICA-approved shape, costume, source charts/materials and first-pose receipts.
   Seed-san's robot gear and anime proportions are not MICA appearance approval.
3. Eight-direction walk/run and 8×8 moving aim/fire with true visible muzzle
   observations; then 720 actual engine-input cases and matching interactive HTML.
4. Native visual, Ponytail FULL, authorized ChatGPT web and exact promotion gates.
5. Freeze that successful production recipe and only then run Luna reproduction.

The same old 2D segmented MICA route is not a fallback. No production descriptor
or profile was promoted by this work.

## Failed assets retained

All three old `pilot_01/02/03` scenes were actually reopened and rejected by the
new mesh gate. Their image/scene folders and corresponding logs (6 directories)
were moved recoverably into quarantine after confirming no runtime pointers.
Every file was checked against the pre-move SHA inventory; nothing was deleted.
Mapping: `rejected_mica_pilots_20260907/quarantine_result.json`.

## Current checkpoint — 2026-09-07 native-alpha request and real source review

This checkpoint supersedes older routing/count summaries, not their evidence.
**Actual complete MICA / Luna / final interactive HTML are still NOT complete.**

- Current job: `art_src/characters/mica/rigged_v2/job_r05.json`.
  The new native 1024×1536 front ImageGen source passed source-only visual and
  Ponytail FULL review after R3 excluded thigh straps from cloth swatches.
  Receipt: `source_front_r1/SOURCE_RECEIPT_R3.json`, SHA
  `0c4288f1f27a70cace7d4eda4d692ee637e2eefaa88a21b4ca27945fba04840f`.
  `next` returns BUILD_ONE_MESH_AND_FIRST_POSE, not motion/batch permission.
- Outstanding route issue: the original source request binds only the collector,
  not a newly authored production MICA builder. `authorize_build` currently
  rejects a new builder not in those source bindings. Do not evade this check,
  fabricate an old generation permit, or regenerate good art just to update code.
  A separately exact-bound reviewed build-plan handoff is under independent
  review. A real MICA anatomical/costume adapter still needs implementation.
  `tools/character_pipeline/check_build_handoff.py` now exposes that blocker
  before Blender launches; it does not manufacture a build-plan approval.
- Official Blender Studio CC0 `GEO-body_female_realistic` provides genuine human
  anatomy. Intake/license are in `third_party/blender_studio/human_base_meshes_v1_4_1/`.
  `realistic_base_rig_astra_r4` saved a 22-bone skinned UAL walk probe using the
  original 1.333s duration, with evaluated soles (211 left / 213 right vertices).
  It is untextured anatomy, not MICA. Sole lift/contact need calibration and
  two genuine world-travel cycles; in-place excursions are not ground-lock PASS.
- Combined runtime consumer now uses actual post-collision displacement for
  gait phase and chooses the displayed authored move/aim/fire channel before
  projectile creation. Stop presentation uses existing 12px/s, not tiny per-frame
  jitter. The actual root ledger remains unaltered for independent speed/contact.
- Latest actual synthetic engine matrix: `combined_c4c7f8d4b3ff45b5bf531d8fc98ce3ea`,
  240 cases each at 30/60/120Hz, zero technical failures, all owned children exited.
  Subject `f13e10806fca468ad54d2d35c633f58f012f709fbffc2551401570632433f258`.
  This is marker-based consumer testing, NOT MICA appearance/gait/muzzle approval.
- `blender_root_capture_r2` actually rendered two native 1920-square frames and
  evaluated the skinned fixture. Ground moved (1.25,-0.5,0); camera followed only
  that translation, while actual skin motion and world sole values stayed bound.
  R1 failed a fixture bone-local/world-space assertion and is retained with cause.
- Tests: generation 40, motion 33, root capture 2; staging/promotion guard smoke
  PASS. Skill validator PASS with Python UTF-8 mode. These are technical scope.
- User allowed native-alpha source when clean separation is proven. One built-in
  ImageGen probe returned RGB painted checkerboard, alpha 255 everywhere (zero
  transparent pixels): FAIL. No API fallback or repeated regeneration was used.
  Conditional native-alpha request, actual alpha/mask checks and independent
  separation review are added to the harness and project skill. Current source
  remains the good green master, not the failed fake-transparent picture.
- Failed alpha probe (6 files) and R1/R2 annotations/evidence (20 files) were
  moved into project quarantine with exact path/hash inventories; nothing was
  deleted. Good shared source and approved R3 stayed active. Only each exact
  corresponding managed ImageGen staging copy was deleted after verified copy.

Evidence roots: `artifacts/motion_harness_audit/technical_fixtures/` and
`artifacts/quarantine/generation_diagnostics/`. No new production pointer,
playable profile or legacy HTML was promoted as complete. Keep Luna idle until
the real Astra all-gate candidate and matching Godot HTML genuinely pass.

## Resumed checkpoint — exact builder handoff (2026-09-07)

This supersedes the prior checkpoint's unimplemented handoff statement. The
actual character/motion/HTML/Luna milestones remain unfinished.

- New source-only receipt R4 reuses the unchanged R1 ImageGen source, R3 masks,
  original request and original permit. Both reviewers actually re-opened it.
  Subject `6101f73913dd0c12c3d7b24929c1e6bb1577a717530170600130dc0d5a483a7f`;
  receipt SHA `c51d6ad5e5bcf4c5369f5420ad5751f2a218c08de867c9cbda56671224c9070e`.
  R3 approval remains historical/stale under the changed code, not overwritten.
- `generation_harness.py` now implements audit/seal/verify of a separately
  reviewed build plan, reserved attempt, distinct one-time runner/child claims,
  mandatory actual construction, output and consumed-image scope checks.
  Ponytail R1 found three P1 boundaries; R2 confirmed those code paths closed.
- New actual entrypoints: `run_mica_anatomical_candidate.py` and
  `build_mica_anatomical_candidate.py`. They construct a limited S neutral model
  using real CC0 body/leg geometry and skin, fitted costume and external boot
  sole surfaces. R3 Ponytail review confirmed the earlier inner-shell/flattening
  measurement defect was removed. No synthetic marker becomes character art.
- Exact latest plan: `art_src/characters/mica/rigged_v2/BUILD_PLAN_R1.json`,
  subject `b2bcbff29deda912dc7d0cd4bfae966f969858bd25e41652c63792ca2f36de34`.
  One new `model_r01` directory, S neutral first pose only, 2 CPU threads/240s,
  no animation or runtime writes. Await actual plan reply and sealed receipt
  before running. Current job `rigged_v2/job_r07.json` correctly routes to
  `REQUEST_INDEPENDENT_BUILD_PLAN_REVIEW`, no errors.
- Generation unit tests: 50 PASS (including actual runner boundary with a
  mocked child, duplicate execution, actual pose inputs/outputs and fixture
  escape counterexamples). Motion unit tests: 33 PASS. Skill format PASS in
  UTF-8 mode; skill/job-format now use the real new handoff, not the old wrapper.
- A neutral empty-handed render cannot PASS a combat visible-muzzle check.
  Do not seal it as an animation-ready combat pose or run Luna from it.

## Actual construction attempt checkpoint — R2 (2026-09-07)

- R1 actually ran once and failed before mesh/render with StopIteration in the
  Blender library loader adapter. The loader mutated an aliased expected-name
  list into objects. The exact old builder and all logs/failure records moved
  intact to quarantine `mica_anatomical_model_r01`; the inventory records hashes.
  No source art was regenerated, no original input changed, no asset deleted.
- Fixed by supplying a separate list to Blender. A regression executes the
  actual loader code block with the observed mutation behavior: historical R1
  fails and corrected R2 passes. This is technical API evidence only.
- R2 independently reviewed exact plan subject
  `a7b09a6bedb637b230be010b9bcf839b0ab688511d9c360a4660d80bd7ed06ea`.
  New receipt SHA `674d6bd31e0e933157e11793155f443e3ed9156b7aed29b0b1bcbaa99d3a3e9e`;
  one new reserved attempt, fresh `model_r02`, same 2-thread/240s limit. Job
  `rigged_v2/job_r09.json` routes correctly to one mesh and native first pose.
- R2 owned child has been dispatched. This checkpoint makes no successful
  render or first-pose visual claim. Read its actual output/failure next.
- Actual MICA motion, muzzle, full runtime, web review and Luna remain unfinished.

## Actual construction checkpoint — R3 boot envelope (2026-09-07)

- R2 failed before rendering at actual boot sole selection. Preserved intact in
  `artifacts/quarantine/generation_diagnostics/mica_anatomical_model_r02/` with
  old builder and exact moved-file inventory. Cuff closing inverted the right
  boot. A constant bare-toe normal offset also introduced actual intersections.
- The corrected Blender shoe envelope is not the old folded shell renamed.
  A 3mm unreprojected voxel surface, two retained anatomical shoe components,
  tightly bounded/recorded detached microcell removal, actual triangle-based
  skin transfer and entirely new final sole IDs replace that failed mechanism.
- Exact real diagnostic `mica_boot_envelope_adapter_r6/VOLUME_DIAGNOSTIC.json`
  SHA `c80eece8fe32cfad788199be1e73d522d0856097e3d03c334f8297a152833d82`:
  60842 final vertices; 2 outward closed shells; 761555 shared/BVH candidate
  checks, zero intersections beyond shared boundaries, zero folded triangles;
  2860 actual body vertices strictly inside by all 3 ray parities, none on the
  tolerance boundary. Normalized transfer skin-row error 2.22e-16 (not raw
  float32 barycentric precision), zero unweighted/invalid bones. Static geometry
  only; this does not prove gait/contact or costume likeness.
- R5 parity ambiguity was not ignored: a real cube reproduction exposed a BVH
  float32 duplicate exit hit. Explicit geometric-tolerance ray restart fixed
  it; six actual Blender cube/corner cases pass. Nine pure geometry/API tests
  pass, including shared-vertex crossing and opposite component orientations.
- Ponytail independent cause, geometry and exact R3 plan reviews are recorded.
  Source R4 stayed unchanged. New build receipt
  `c62188713f3cf1b500e9697c8e2b713d729f1d0607d12fbde29a3341d5ec0729`
  authorizes only one fresh `model_r03` S-neutral 1920x1920 construction,
  CPU 2 threads / 240s / zero motion. Current job is `rigged_v2/job_r11.json`.
- R3 owned child has actually been dispatched. Inspect its current output/log
  and mesh/first-pose results next; no rendered or visual-success claim here.
  Original source, models and failed asset evidence are retained. Skill rig
  instructions now describe the observed failures and exact tested route.

## Actual construction checkpoint — R4 facial projection (2026-09-07)

- R3 completed actual anatomical/boot mesh construction and saved the scene,
  then stopped before render on 45 unresolved source UV triangles. All old
  output and builder bytes are preserved in quarantine
  `mica_anatomical_model_r03/QUARANTINE_MANIFEST.json`; attempt remains spent.
- The new helper changes only the separate front facial overlay. Actual
  diagnostic `mica_face_projection_r2` retained 1358 resolved triangles,
  omitted 46 after explicit retriangulation, preserved underlying body/weights
  and retained position/UV/skin corners exactly. The unchanged full collector
  returned errors=[] / HOLD_NATIVE_FIRST_POSE. This is not visual approval.
- The diagnostic also exposed broken relative image links after quarantine
  move. Exact approved SHA-bound image links were restored in the derived
  diagnostic only. Fresh production saves absolute project-local image links;
  no original or archived blend was modified and no art was substituted.
- Ten builder/API/geometry unit tests pass. Ponytail independently reviewed
  the measured cause and limited repair. New exact R4 plan subject
  `6a6a2bd3ad0250dcf917c79e9b3d8e6c4445de219f0e1d84cdcb430ad7944714`
  binds current helper and actual diagnostic. Same source R4 remains approved.
- Next: obtain exact R4 plan receipt and reserve fresh model_r04 execution,
  one native S-neutral still / CPU2 / 240s. No first-pose render or actual
  character gait has passed at this checkpoint. Do not begin Luna testing.
