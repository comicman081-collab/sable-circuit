# Provisional Tripo reference pack review

Reviewed pack: `art_src/motion_reference/tripo_run_20260908/pack_r01`.
Scope: independent implementation and native still-image review under Ponytail FULL;
no Blender child, generation service, retarget, source-art creation or promotion.
Status: **HOLD pending two implementation corrections** listed in `REVIEW.json`.
This review does not approve later code edits or a newly generated pack.

The reference implementation preserves the supplied GLB and uses its imported
mesh/skin. It creates a separate standing action with identity pose matrices,
compares its evaluated vertices against Blender's native REST result, preserves
the original Run action as a separate asset, and checks its exact key digest
after sampling. No code path reconstructs face, hair, costume, footwear or weapon
geometry. The single 1.70 m scale convention is explicit, uniform and applied to
the derivative rig, with no frame-dependent floor offset. The supplied source
still has the original `253912742fa69261bd34ac44cf18cdde38a6a4dcc4ce17ccd0560942509c352b`
SHA. All source, blend, image and geometry references examined match their hashes.
The reviewer did not independently reload Blender actions; action/standing
equivalence conclusions are from the exact inspected implementation and completed
builder evidence, not a second native execution.

All three viewed PNGs are actual 1920×1920 images and match their receipt hashes.
REST_FRONT and REST_SIDE show the source character upright with its spear grip.
This is a native standing bind pose, not a standardized T/A-pose or a corrected
two-foot level stance. RUN_START shows a plausible individual stride pose, but
it provides no full-cycle or contact approval. No floor plane is visible in these
images, so floor contact is not visually established.

The exact raw Run spans frames 1–31 at 24 Hz, or 1.25 seconds, and has 49 sampled
timestamps with the real terminal sample retained. Ten left and fourteen right
actual weighted surface vertices are used for sole measurement. The neutral
sole-bottom difference is 32.3887 mm. Minimum sampled sole clearance is 9.966 mm
on the left and 40.318 mm on the right relative to the fixed neutral floor.
These values do not meet the visible contact requirement. The pelvis moves
4.91955 m horizontally while the Root bone stays stationary; its world-space
sole endpoint difference is 5.06871 m. This traveling clip cannot be declared
one wrapped cycle by substituting its first pose for the terminal sample or by
using the stationary Root as evidence that the actor is stationary.

The current pack's `HOLD_CONTACT_AND_CYCLE_REVIEW` and explicit absence of visible
art authority are correct. The reused classifier is a diagnostic against its
single-cycle assumptions, not proof that this entire supplied clip represents
one cycle. A future cycle/trajectory decomposition must preserve raw timestamps
and remain a separate reviewed derivative.

Before the reusable reference verifier can receive implementation clearance,
cross-check the internal map/calibrator links against the exact source, Run
blend, raw geometry, sole mesh/IDs and timestamp range. A file hash alone does
not prevent a foreign-but-well-formed map or calibrator record from being linked
into an otherwise valid pack. Also require the builder to bind the runner's exact
execution input and consume an exclusive child claim before writing native
outputs. Its current final-inspection-only existence check does not protect
partial failed output from a direct retry.

The report JSON binds the inspected code revisions, all measured facts, original
contact errors and exact output hashes. Reviewed code copies are preserved beside
it because the parent is still completing the runner. No SABLE visible-frame,
gait, eight-direction, firing or runtime approval is issued.
