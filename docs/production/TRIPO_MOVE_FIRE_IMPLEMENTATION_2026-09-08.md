# Tripo Run movement and shooting implementation

This is an active Astra implementation candidate, not the completed motion
procedure to freeze for Luna. No SABLE art profile or production pointer has
been replaced. Original Tripo inputs and all rejected candidates remain intact.

## Implemented and measured

The supplied native Run contains about two similar strides over 1.25 seconds.
The new reference action explicitly fits a periodic 0.625-second derived cycle;
it does not claim that either raw half was an exact source loop. Planar travel
is separated from the moving Hip, not the stationary Root. The licensed CC0
target's actual neutral REST soles fix the floor before animation evaluation.

The first direct retarget penetrated the floor and twisted an ankle. Analytic
two-bone leg IK corrected actual evaluated sole height. A subsequent stage
locks a fixed sole vertex in world XY while preserving the independently
derived planar transport. Left toe-off moves one sample earlier when the target
leg would otherwise overextend. The current support-anchor result has zero
reach clamps and at most 8.8 micrometres final horizontal anchor error. These
solver diagnostics do not replace independent whole-sole slip or visual review.

Current reference files:

- `artifacts/quarantine/generation_diagnostics/tripo_support_anchor_r02/retarget_result.json`
- `artifacts/quarantine/generation_diagnostics/tripo_support_anchor_calibration_r02/contact_calibration.json`
- `artifacts/quarantine/generation_diagnostics/tripo_support_capture_r02/CAPTURE.json`
- `artifacts/quarantine/generation_diagnostics/tripo_support_capture_r02/RUN_CONTACT_8_LOOPS_1080P.mp4`

The fresh Blender reopen/calibration identifies eight distinct phases and
passes its technical contact contract. Supporting soles are approximately 2 mm
above the fixed floor. The 49 native 1920×1080 captures reproduce the sampled
sole arrays exactly. The encoder requested eight 0.625-second loops, but a
fresh complete decode found 383 frames / 4.98 seconds; the video must not be
described as eight complete loops. `ACTUAL_VIDEO_DECODE_CORRECTION.json` retains
that correction beside the original encoding intent. The visual container
validator passes 49 PNGs and the video. It does not judge animation.

## Runtime behavior

`FastCharacterRuntime` now accepts optional strictly increasing `phase_starts`
on every authored move/aim/fire channel. `frames / fps` remains the whole-cycle
duration; `phase_starts` specifies when each distinct frame begins. All channels
of one locomotion mode must share the same boundaries. Legacy uniform timings
are equivalent to `[0, 1/N, …, (N-1)/N]`.

The existing actor commits actual displacement after collision and bounds
resolution. That displacement advances the gait phase. A shot or aim change
selects its reviewed channel at the same phase and uses that visible frame's
muzzle. Frame selection no longer assumes that contact, down, passing and
flight occupy equal durations. The Python motion auditor independently checks
the same declared timing against observed position, phase, sprite pixels and
projectile events.

The real Godot input/physics test consumed a Tripo-derived nonuniform timing
schedule using synthetic channel-marker atlases. All 240 cases passed at each
of 30, 60 and 120 Hz: eight-direction walk/run, 8×8 movement/aim shooting,
stop/resume, adjacent/opposite turns, speed switches, reload, collision, bounds
and firing during transitions. This proves runtime selection and synchronization,
not MICA art. The 30 Hz capture was completed before a user resume interrupted
the wrapper; its exact snapshot and complete raw capture were recovered and
independently scored. The 60/120 Hz wrappers exited normally.

Exact report:
`art_src/motion_reference/tripo_run_20260908/movement_fire_r01/IMPLEMENTATION_REPORT_R2.json`

The current tested schedule is `timing_r02/RUN_PHASE_TIMING.json`, freshly
derived from the final XY-anchor calibration. All 720 cases passed again with
that exact schedule and all owned Godot children exited normally. The earlier
`timing_r01` evidence remains historical: its right passing event differs by one
sample. There is no supplied Tripo walk clip and no claim of authored walk art.

## Visible-frame continuation

The current entrypoint has an explicit Tripo/CC0 guide branch in
`tripo_pose_guide_gate.py`. It does not manufacture UAL/VRM provenance. The inlet
binds the user's exact paid-output license, CC0 target, native source pack,
retarget chain, full capture, current gate code and independent phase reviews.
Its initial scope is E/run geometry only. All ordinary fixed-floor contact and
ImageGen art gates still apply.

The initial exact E/contact_l guide passed independent visual and Ponytail FULL
review. Two authorized whole-frame ImageGen attempts (R4 and R5) nevertheless
placed MICA's beige-plated anatomical right leg forward. Both are independently
FAIL_NOT_PROMOTABLE and remain in quarantine; neither is relabeled contact_r.
Removing the earlier flight reference in R5 did not correct the error.

The next mechanism uses actual licensed deform-group weights to color the left
leg blue and right leg orange, with labels pointing to evaluated joints. This
changes only the pose reference's leg labels, not its geometry or any SABLE
pixels. `capture_tripo_laterality_guide.py` binds its exact child inputs and
checks fresh sole arrays against the unchanged calibration. The current harness
adds an explicit optional `semantic_laterality_guide.py` gate and requires exact
independent annotation reviews before that image can be used as an input.

The refreshed draft is
`art_src/motion_reference/tripo_run_20260908/pose_guide_r02/E_CONTACT_L_GUIDE_DRAFT_R2.json`.
Its review subjects bind the updated gate code; the earlier code-bound guide
receipts are historical. MICA's approved front/profile and rifle art remain
the appearance authorities. The Tripo spear-arm gesture and bare CC0 reference
surface cannot furnish MICA firing pixels. A whole visible sequence, independent
visual gait review, game-scale no-slip evidence, final runtime matrix, HTML
parity and ChatGPT web review are still required before production promotion.
