# Diagnose the visible gait, not only actor position

The 2026-09-11 ASTER failure had three independent causes:

- `fullBodyFrame()` handled only `move` as locomotion. Newly added `walk` and
  `run` fell into recoil recovery and returned frame 5 for every phase.
- Firing switched from the new realistic walk art to an unrelated old 24-frame
  raster leg warp. More frame indices did not make that a real walk.
- The input QA ran only short moving-fire cases. Source hashes, distance and a
  static 1080p screenshot all passed while actual walking stayed frozen.

## Repair order

1. Record the selected action/texture and frame index over a complete stride,
   both firing and not firing. Use `atlas-renderer.test.js` and the live
   `motionDebug.current` state. A profile atlas is not evidence if another
   bundle overrides it in `AtlasRenderer.load()`.
2. Check source pixels using `gait_contract.py`: 0/3 opposite contacts,
   1/4 opposite swings behind and 2/5 opposite forward passing poses.
   Follow the anatomical leg by its costume
   marker: ASTER's LEFT white/cyan leg versus RIGHT thigh-pouch leg. Six new
   file hashes or six pictures of the same forward foot fail this check.
3. Preserve the approved whole-body look. For actual missing phases, ImageGen
   may use one native opposite-pose pair at a time: put the corresponding
   `reference/ual_guides/D_walk_pairN.png` first as CAMERA/POSE authority and
   the character's identity reference as APPEARANCE authority. Explicitly
   specify each leg's role in both figures. Inspect before the next attempt.
   A six-figure sheet copied EAST into SE and repeated S support legs; do not
   treat it as success. Use a direction-specific aimed reference if weapon
   foreshortening drifts. Do not fix missing leg poses with a raster warp.
4. A native 1536x1024 pair contains larger figures than a six-cell sheet.
   `intake_pair.py --character ID --direction D --pair N --generated PATH
   --tool-response PROOF` preserves the real master and separates complete
   connected figures without resizing. It imports phases N and N+3, preserves
   previous sources in quarantine and binds the exact tool response. Never
   pad/upscale a small six-cell output and call it a native high-res master.
5. Run `character_workflow.py prepare-cycle --character ID --direction D`.
   Follow [the enforced cycle gate](cycle-review.md). Inspect the generated
   native-scale light/dark pair panels AND the chronological cycle. Record
   `review-source` and the whole-cycle `review-cycle` only after actually viewing that evidence. Observe rifle
   axis/muzzle, identity, contacts, passing knees and alpha. The command does
   not approve or activate anything by itself.

## Source failure patterns actually observed

- **SITE-7 rifle pilot, 2026-09-13:** two opposite-pose pairs repeated the same
  planted right leg. For this repair line use ONE pose per image, the exact
  UAL phase guide FIRST and the appearance reference SECOND. Do not repeat the
  failed pair approach. The right-thigh holster belongs to the anatomical
  right leg; inspect hip-to-boot continuity, not just the pouch location.
  Retain the valid half via `--side` only after viewing it. Existing approved
  pair sources are unaffected. E1/E2 improvements are not an approved cycle.

- A moving seed can preserve the same support leg despite opposite-leg text.
  Use the direction's reviewed planted aimed master to separate camera/weapon
  authority from the phase guide. Mannequin colors are labels, never costume.
- Follow the cyan leg from its anatomical hip through knee to boot. A cyan
  calf or white stripe on the other leg does not repair swapped hips. A third
  leg, missing panel or brown guide material on trousers is a source failure.
- Single portrait replacements can become thinner/longer than adjacent pair
  sources. Compare their normalized chronological cycle, not isolated beauty.
  The square SW replacement improved this observed proportion mismatch.
- When one half of a pair is valid, `intake_pair.py --side 0` or `--side 1`
  can retain just that observed half. The other half remains unapproved; the
  complete native master and failed-half evidence are retained.
- Low toe clearance is distinct from a high marching knee. Inspect the
  actual game-size moving cycle before expanding a pilot to all directions.

## Runtime invariants and evidence

### ROOK source repair findings (2026-09-13)

- ROOK's anatomical RIGHT thigh carries the paired black/gold cylinders; the
  LEFT forearm has the gold support gauntlet. Trace hip, knee and boot separately.
  In rear views right is screen-right; in front views it is screen-left. In
  three-quarter views a lifted boot crossing the silhouette does not change
  its anatomical side. A hidden cylinder alone cannot identify a passing leg.
- A whole moving-body reference repeatedly copied its old support pose into a
  requested opposite phase. Use the approved direction-specific upper-body
  crop as appearance/camera reference and the phase guide for the whole pose.
  This crop is a reference only: every accepted visible frame is newly authored
  whole-body art, never a runtime upper/lower cut-and-paste assembly.
- SW frame 4 and W frame 2 required a second repair after the chronological
  review exposed the wrong support leg. Inspect the actual recompiled frame,
  not the requested pose name or an earlier review packet. New source hashes
  require a fresh preview, annotations and whole-cycle review.
- Put observed hip/knee/sole points on the native compiled cell. If a landmark
  falls outside the silhouette, inspect the native grid before correcting it;
  do not move a point just to satisfy a threshold. State when a joint is partly
  occluded. On-subject points are a diagnostic, not an anatomy PASS.
- Straight front/rear muzzle heuristics can select hair or a hand. Annotate the
  visible muzzle in raw-source pixels per affected slot, then inspect its
  compiled location and live shot. Do not fix a bad socket by moving artwork.
- The cycle preview now uses VP8/WebM. OpenCV decoding of mp4v was insufficient:
  the Chromium review page could not play that codec. Check real browser
  playback at 1x as well as sequentially decoded samples. Preview videos remain
  source diagnostics, not delivered-runtime evidence.

- Preserve the working physical-code input and shared aim solution.
- The generic authored renderer selects walk/run by actual traveled-distance
  phase, independent of shot cadence. Fire applies the existing continuous
  upper-body recoil and uses the same transform for the muzzle. The lower body
  stays on the same gait; at rest it stays on the same planted idle source.
- Keep `runSpeed` and `walkSpeed` independent. Reusing the walk source with a
  faster distance cadence is the accepted MICA prototype capability, NOT a
  separately authored sprint clip. State this limit explicitly.
- Run the 17-case held-mouse input test AND the 40-case temporal locomotion
  test. The latter checks all eight directions for walk, run, moving fire and
  stationary fire, hashes the actual selected lower-body pixels, and rejects
  fixed/duplicate frames. It does not automatically judge anatomy or sliding.
- The report validator now checks chronological frame/phase agreement, increasing
  sample times, measured position deltas, shot counters and, with the current
  profile, phase-to-distance and speed bounds. A six-element set is insufficient.
- Watch native 1080p runtime video spanning complete strides, turns, stopping,
  speed change and fire transitions. Compare visible foot support to ground
  motion, not a speed HUD. A character at the world boundary is not running
  evidence. Still-image review alone cannot authorize `deliver`.
- Cycle validation also compares the decoded native character panel to the
  expected authored atlas phase with codec tolerance. A moving timer or grid
  over a frozen body is not gait evidence. Opposite 1/4 and 2/5 chain checks
  catch repeated annotated poses, but cannot prove that the reviewer labeled
  the actual anatomical legs correctly. Uncertain limbs remain unapproved.
- Do not report a Luna reproduction unless a real authorized Luna run occurred.
  Regression tests prevent the reproduced bugs, not every possible future
  artistic or implementation error.
- `capture-motion.js` saves a sibling JSON binding the actual video hash,
  current build, capture script and time-stamped full cycles/transitions.
  `motion_evidence.py` rejects stale footage and missing phases. Never create
  that metadata by hand to rehabilitate unrelated footage. Review the video
  and its native decoded sequential frames; index-seeking an unindexed WebM
  can silently display a different moment (`inspect_video.py` decodes forward).
- A source or runtime rejection invalidates the current delivery JSON to HOLD
  while preserving its prior receipt. Never leave an older REVIEWED_DELIVERY
  label as the apparent current result of a failed repair.
