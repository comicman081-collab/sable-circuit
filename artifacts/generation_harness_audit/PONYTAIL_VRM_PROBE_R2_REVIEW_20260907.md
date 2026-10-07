# Ponytail FULL — actual licensed VRM / UAL probe review

Scope: `seed_san_ual_astra_r2`, one native pose and actual skin data, read-only.
Verdict: real skin deformation confirmed; full-cycle gait and MICA production HOLD.

The reviewer checked seven input/output/model/generator/UAL/license/image hashes,
the imported wear mesh (18,781 vertices, 23,374 polygons), and 54 sole vertices per
foot. Forward excursion was 0.688878 / 0.688587m; left/right positions exchanged
at half-cycle. Initial collection versus baked replay differed by at most 0.0m.
The first native pose showed connected leg/ankle volume and no visible 90-degree
sideways ankle twist in that pose. This is not validation of all poses.

The reviewer found the 0..32 source-frame to 0..24 target-frame timing error:
1.333 seconds became 1 second. The current code correction preserves source frame
numbers and timestamps, but the reviewer explicitly did not reuse r2 evidence as
a test of r3. A new r3 data/capture review is recorded separately when returned.

Still required: ground-referenced continuous cycles and actual world travel,
heel/toe contact, knee/ankle motion, lift and cycle seam. Some r2 sole vertices
reached about -6.3mm in world Z and the swing foot bottom reached about 143mm.
Assigned-matrix error 0 only confirms a matrix application, not natural gait.
Torso-inferred orientation must not replace world-ground calibration.

No runtime, shooting, MICA identity/costume or Luna readiness approval was issued.
