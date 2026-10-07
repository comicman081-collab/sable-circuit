# E sample 23 attachment failure

**FAIL_NOT_PROMOTABLE for the actual posed result.** The preserved neutral source approval is unaffected. I opened the actual native 1920-square image and independently observed a horizontal waist gap, a larger wedge at the screen-right waist, and a long narrow coat-edge arc. Face, hands and rifle remain recognizable source artwork. No source regeneration is indicated.

The waist is a deformation discontinuity at the semantic ownership boundary. `reviewed_rgba_surface_harness.py` creates vertices with `(x, y, region)` keys, so two regions may have separate vertices at the same original-art coordinate. Its upper rectangle ends at source y=553 and assigns spine_03 exclusively. The adjacent default region uses nearest-four weights over all bones, including pelvis. The retarget rotates the pelvis while preserving neutral upper rotations, so those coincident rest positions receive different transforms. Closed edge incidence does not prove continuity of these separate visible regions in motion.

Coat roots must participate in the same repair. The right and left coat polygons begin at y=545 and y=550 and are processed before the upper rectangle. Their pelvis-only weights conflict with the upper skin at their roots. Changing only default torso vertices would leave those discontinuities.

The proposed source-y field is a direct repair: all regions use the same spine_03-to-pelvis weights through the torso, with the gun and hands above y=560 staying rigidly spine_03. Original UV and RGB must stay unchanged. Verify actual coincident seam-pair displacement in the same sample-23 pose; matching neutral positions and closed topology alone cannot verify the repair. Shared boundary subdivisions also need to agree if interpolated edges remain visibly separated.

The outer coat arc is consistent with a strip of visible trim falling outside the left-coat polygon and receiving default leg weights. The exact offending UV/vertex list has not been measured here, so the polygon hypothesis is not asserted as a measured fact. A narrow source-coordinate/weight audit can establish it. Prioritize the detached waist; a minor residual trim issue does not justify another broad art or motion batch.

One implementation caveat remains in the first proposed helper: its dynamic top-four truncation can introduce a weight jump in the 740–840 blend band when pelvis is added to an original four-bone basis. The companion JSON records a concrete counterexample. The common torso band through y=740 itself is appropriate. For the later band, verify the actual basis or fail closed on five influences instead of silently dropping a changing bone. The four existing tests use small bases and do not exercise that switch. They were read but not executed by this reviewer.

This review changes no code, source art, masks, thresholds or runtime pointers. It authorizes no completed pose, clip, firing or runtime claim.
