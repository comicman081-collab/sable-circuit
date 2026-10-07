# Independent coat/leg ownership review

Reviewer: `/root/tripo_intake_review`, Ponytail FULL. Scope: the exact S-source knee probe and Tripo sample-23 source-surface probe only. No Blender child was launched by this reviewer. This is one independent reviewer, not two review roles.

**The contact candidate fails visible garment deformation. The small knee probe proves real skin deformation but remains HOLD for garment isolation. Neither is admitted to HTML, a visible motion sequence, or runtime.**

I directly inspected `LEFT_KNEE_10_DEGREES_1920.png` and `TRIPO_CONTACT_L_SOURCE_SKIN_1920.png`, both native 1920 x 1920, together with the original S source and the previously reviewed exact R4 neutral result. In the knee-only image, the anatomical left leg (image right) bends and the adjacent lower coat tip also lifts. In the contact image, the image-left beige coat hem curls upward into a conspicuous U around the knees, with folded green lining. The resulting long-coat silhouette is not acceptable. Face, hair, devices and artwork remain recognizable source pixels; preserving those pixels does not establish acceptable garment deformation.

The direct cause is `build_source_surface_adapter.py:243`: all vertices choose the four closest segments from all 22 bones, without separating visible garment and limb ownership. The inverse-distance weights at lines 247-249 therefore assign coat tails to nearby legs. `COAT_OWNERSHIP_QA.json` independently recomputes those unchanged builder weights at actual recorded neutral vertices, and compares the actual evaluated vertex arrays from both probes. This is a numerical reconstruction of the original weights, not a native reopening of Blender vertex groups.

| Observed coat source pixel | Vertex | Recomputed leg-chain weight | Knee-only displacement | Contact displacement |
| --- | ---: | ---: | ---: | ---: |
| (304, 1040) | 5800 | 100% | 0.73 mm | 276.41 mm |
| (720, 1040) | 5846 | 100% | 16.97 mm | 160.45 mm |
| (312, 1120) | 6392 | 100% | 0.00 mm | 420.41 mm |
| (704, 1120) | 6429 | 100% | 38.91 mm | 192.47 mm |

The lower samples are predominantly calf weighted (85.84% right and 84.65% left). The upper samples also receive weights from the opposite anatomical leg. These four visually identified points demonstrate the cause; they are not a complete coat mask. The whole knee array contains 14,842 evaluated vertices, with 3,089 moving over 1 mm and a maximum of 0.1064562146 m, independently recomputed from the recorded arrays.

A separate source-UV semantic ownership profile is an appropriate bounded correction. Define the entire visible coat-tail region from the exact approved source, bind its source/mask/profile hashes, and allow only pelvis/torso influence there. Zero every thigh/calf/foot/toe weight in that region, then normalize within its allowed set. Restrict visible legs to the appropriate limb chain. A single pelvis influence is a useful controlled baseline for coat isolation; it is not a final natural-cloth solution. Do not silently give unclassified visible pixels the old global nearest-four fallback.

The source grid also needs a boundary check: if a triangle or shared vertex crosses the visible coat/leg ownership boundary, a hard vertex mask can still stretch the intervening triangle. Refine or separate the source-bearing geometry at the observed boundary while keeping the original neutral projection, UV coordinates, original RGB and alpha authority. Do not hide the failure by trimming alpha, shrinking the coat, painting new material, or adding invented rear artwork. Transparent unknown closure cannot establish unseen appearance.

`coat_MASK_R3.png` contains 24,532 nonzero pixels and is partial material-region evidence, not full coat ownership. It must not be repurposed as the complete semantic mask. A new full-region annotation is implementation work, not source illustration authorship.

The next useful diagnostic is the exact same calf-left 10-degree input and the same Tripo sample 23 after the isolated weight change. Compare regional leaked leg-weight totals, unintended coat displacement, boundary stretching and native full-frame silhouettes. Keep the R4 neutral source and both current probes unchanged. This review allows the cause to be corrected and compared; it does not approve the corrected output in advance.

The recorded contact joints and source phase do not certify actual target soles, target REST floor or target anatomical foot axes. Those remain separate checks before contact or gait admission. Likewise, this one S source and one contact pose provide no eight-direction surface authority, full-cycle motion, upper-body aiming, rifle/muzzle, firing, or interactive-runtime approval.

`CONTAINERS.json` passes decoding and native container size for both images only. The code, render, report and source bindings are recorded in the companion JSON. No production code, source art, mask, asset or promotion pointer was changed by this review.
