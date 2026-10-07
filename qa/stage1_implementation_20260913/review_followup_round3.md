# Round 3: verify the seven concrete R2 counterexamples, not final art approval

Same SABLE CIRCUIT local work. R1 and R2 actual visible replies are preserved at
motion_lab_v1/qa/stage1_enemies_20260913/cycle_capture/gpt6pro_review_round{1,2}.json.
This is a current-byte snapshot, not an assertion that all R1 work is finished.

Changes for your exact R2 cases:
- R2-01: BEFORE each pointer event retain actorPosition and requestedTarget;
  after dispatch compare actual target to that independent request. Validator
  recomputes requested world point from actor basis+sector+4m radius, not aim=sector.
- R2-02: ninth before/after Actor component is actual reload. Match ammo, cooldown,
  reload to initial timing, keep weapon cadence unchanged. Concurrent positive
  reload/cooldown use max; empty-magazine initiation still includes cooldown+reload.
- R2-03: source-atlas validator binds phaseStarts to actual recipe and re-runs
  source registration into memory; compares alpha, visible RGB, clip and muzzle
  metadata. RGB under zero alpha is normalized (WebP may discard hidden RGB).
- R2-04: distinguish each expected/alternative phase on their difference region,
  never on foreground/background average alone. Keep every native differing pixel
  for small regions, cap broad regions to 4096 evenly distributed native samples.
  An ambiguous pair is insufficient evidence, not automatic art-repair/approval.
  Added your frozen 32x32 patch counterexample, lossless FFV1; it is rejected.
  Positive fixture now really advances six different synthetic cells at recipe
  speed. Actual rifle candidate's 107 decoded frames also passed before its
  subsequent background-only source normalization; no artistic approval claimed.
- R2-05: shared source_provenance.response_master validates full path boundaries;
  result.png.other.png counterexample rejected. It is still local consistency,
  never cryptographic provider attestation.
- R2-06: candidate fingerprint includes prepare + matte + provenance code SHA.
  Actual prepare() test changes matte dependency and verifies first report retained.
- R2-07: machine hit rectangle transforms all four native corners into world AABB.
  Native interior points tested under rotation/nonuniform parent scale.

Other R1 work completed in the meantime: shared retained-master and explicit
derivation checks across all three importers and source_status; approved source
receipts bound by hash; decoded source-pixel rejection; failure-scoped cycle
records with actual failedSlots or requiredChange; independent source recompile;
pair halves prevalidated before slot writes; import invalidates delivery while
preserving history; handoff includes new code/matte evidence dependencies.
Historical accepted ASTER/MICA/ROOK raster bytes, gait and weapon settings are
not regenerated or changed; old evidence is not relabeled as a fresh run.

Executed locally on this implementation:
- Entire Python discovery: 90 tests, 94.876s, OK.
- Entire Node test suite: 30 tests, OK (actual existing Actor/renderer tests).
- Godot machine source/transform/projectile test: 370 checks, PASS.
- Real Stage 1 technical playthrough after geometry fix: 6 rooms, both optional
  recoveries, 10 defeats, EXTRACTED, all operators alive at boss exit (4/106/88 HP).
- Native 1920x1080 actual Godot candidate screenshots captured and decoded.
  Those are candidate previews only, not registry promotion or motion approval.

Still OPEN, not claimed fixed: atomic renderer loading / scoped legacy fallback;
browser 1x/no-seek observation and category-specific timing coverage; actual
anatomical-label observations and overlays; four-limb contract; final human enemy
cycles and Stage 1 raster promotion; full live browser recapture with the newly
strengthened QA rows. Pair prevalidation does not claim crash-proof filesystem
transactions. Independent generation by Luna has NOT been run.

Please review only whether R2-01 through R2-07 remain reproducibly defective in
this snapshot. Give the smallest new counterexample if one remains. Do not label
untested art/runtime or the whole MVP approved. Broader R1 remaining work above
is still tracked separately. Korean response requested.
