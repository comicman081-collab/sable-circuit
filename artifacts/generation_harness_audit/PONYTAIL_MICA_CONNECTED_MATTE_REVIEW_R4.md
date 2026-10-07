# Ponytail FULL — connected chroma matte mechanism review R4

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review UTC: 2026-09-07T16:19:13Z (2026-09-08 01:19:13 KST).
- Scope: the exact `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_CONNECTED_R4.png`, its preserved master/raw, QA and current derivation implementation. Not a new character-frame or motion approval.
- Mechanism verdict: **PASS_LIMITED_MATTING_MECHANISM_CHECKS_FOR_THIS_DIAGNOSTIC**.
- Existing candidate verdict: **FAIL_NOT_PROMOTABLE remains unchanged**, because the requested `flight_l` anatomical lead leg is wrong. This report is not a PASS frame receipt.
- Applied: Ponytail FULL and `sable-motion-production`. No production code, source image, mask or candidate asset was modified. Only this report was created.

## What I actually checked

I directly opened the current RGBA and preserved exact-green master at their original 1254×1254 scale. I compared the visible body, face, hair, coat lining and edges, equipment lights, hands/weapon gaps and boots. I read the actual `derive_chroma_runtime_rgba.py` path from CLI argument/path validation through `background_mask`, output alpha construction and QA emission. I independently decoded the raw, master, previous THRESHOLD_R2 derivative and current CONNECTED_R4 derivative.

The pixel checks below were performed without calling the generator's `background_mask`. An independent synchronous four-neighbour reconstruction from the documented chroma seeds converged in eight expansion rounds and matched every saved alpha pixel. This verifies that the saved output corresponds to the inspected algorithm; it is not an independent semantic definition of which colors belong to the character.

No ImageGen, Blender, runtime, Luna, promotion or full matrix was run. No 1920×1080 review container was supplied for this narrow diagnostic; therefore no 1080p visual-evidence floor, light/dark presentation package or complete frame gate is approved here.

## Required checks and results

| Check | Verdict | Actual result |
| --- | --- | --- |
| Previously recorded dark chroma halo counterexamples | PASS, exact six samples | All six previously failed scope/muzzle/coat pixels listed below are now alpha 0. |
| Cyan/teal costume preservation | PASS, observed and sampled regions | Both known forearm-light counterexamples remain alpha 255 with exact original RGB. Five native subject regions also remain fully opaque and byte-identical. The visible coat lining and lights are not erased as they were by the earlier broad-threshold attempt. |
| No visible legitimate subject deletion | PASS, bounded native inspection | No obvious new missing face, hair, hand, coat panel, light, pouch, boot or silhouette chunk was visible in the opened RGBA/master comparison. This is an actual visual finding, not a proof that every removed pixel has independently labelled semantic ground truth. |
| Alpha-boundary strong-green residual | PASS, independently counted | **0** pixels under the inspected `G>=12`, `G-R>=16`, `G-B>=16` family on the four-neighbour visible/transparent boundary, agreeing with the QA. |
| Saved-output reproducibility and retained RGB | PASS | Independent reconstruction vs saved alpha: **0 mismatches**. Current visible RGB vs original raw: **0 differences**. Transparent pixels contain zero RGB; the entire outer border is transparent. |

The actual alpha counts are **1,204,946 at 0** and **367,570 at 255**, with no intermediate alpha values. Relative to THRESHOLD_R2, **1,324 formerly visible pixels became transparent and 1 was restored**, a net visible reduction of 1,323. This count alone is not used to approve the removed content.

## Exact counterexamples

Coordinates are from the native 1254×1254 image. All six values were opaque in the previous THRESHOLD_R2 result.

| Pixel `(x,y)` | Original RGB | Current CONNECTED_R4 RGBA |
| --- | --- | --- |
| `(831,317)` | `(7,28,7)` | `(0,0,0,0)` |
| `(832,320)` | `(5,32,5)` | `(0,0,0,0)` |
| `(905,328)` | `(1,35,7)` | `(0,0,0,0)` |
| `(1156,388)` | `(7,38,8)` | `(0,0,0,0)` |
| `(448,750)` | `(7,24,5)` | `(0,0,0,0)` |
| `(446,753)` | `(6,31,6)` | `(0,0,0,0)` |

The previously deleted cyan-light counterexamples are preserved:

- `(577,423)`: raw RGB `(46,198,189)` → current RGBA `(46,198,189,255)`.
- `(576,424)`: raw RGB `(79,222,209)` → current RGBA `(79,222,209,255)`.

Additional independently selected native rectangular subject interiors, using half-open `(x0,y0,x1,y1)` bounds:

| Region | Bounds | Pixels | Transparent pixels / visible RGB changes |
| --- | --- | --- | --- |
| Forearm light | `(575,425,646,431)` | 426 | `0 / 0` |
| Back light | `(466,80,475,110)` | 270 | `0 / 0` |
| Teal coat lining | `(340,778,376,810)` | 1,152 | `0 / 0` |
| Face interior | `(700,168,715,202)` | 510 | `0 / 0` |
| Beige thigh plate | `(534,708,543,743)` | 315 | `0 / 0` |

These checks test preservation as well as the RGB equality of surviving pixels; they are not a complete manual semantic mask.

## Why the connected mechanism improves on a global threshold

The actual code seeds exact green and unmistakable bright chroma, then expands through adjacent pixels in a weaker chroma family. Dark fringe connected to the background can therefore be removed without globally deleting every dark teal/cyan pixel that satisfies a looser channel test. Bright chroma seeds can occur in closed weapon/limb gaps, so those gaps are not automatically ignored simply because they are disconnected from the canvas edge. The local path and no-overwrite checks remain in place, and the source master is unchanged.

The independently measured **165 interior family-matching pixels** are not a reason to perform global erasure. They occur primarily around existing teal/cyan equipment and weapon shading, including the waist light around x590–596/y567–571 and rear-shin light around x420–424/y923–925. For example `(594,570)` is `(12,212,186,255)`: it satisfies the broad family but is part of a visible colored light. None of the 165 is on the four-neighbour alpha boundary. I did not certify every one of those interior pixels individually, and they are not reclassified as background merely to force a whole-image zero count.

The boundary result is precisely scoped. It does **not** mean all possible green tint is numerically zero: `(831,316)` still retains `(8,20,10,255)`, below the tested channel separation. Nor is a zero boundary count alone visual proof: with connected growth through the same family, that condition is also an algorithmic consequence. The additional actual native inspection and explicit preservation/removal counterexamples are therefore required. No further unmistakable strong-green boundary defect or obvious subject deletion was established in this limited review.

Future source images or changed thresholds still require fresh pixel/edge review. This particular result does not prove that a color-only rule can always distinguish a differently shaded legitimate costume detail from a chroma reflection.

## Exact hashes

Candidate root: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r1_e_flight_l/`.

| Artifact | SHA-256 |
| --- | --- |
| Immutable `MICA_C03_E_RUN_FLIGHT_L_IMAGEGEN_RAW.png` | `548872ee7d748d738ca6deb0bebe0bb5f3b42e948d91c9bf78cb8535fed9d692` |
| `MICA_C03_E_RUN_FLIGHT_L_EXACT_GREEN.png` | `94c150e0b05d1005f4e8704490028c29cd6b2dcc1a54869a84d8ad6862064edd` |
| Previous `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_THRESHOLD_R2.png` | `9cbeb1a42da2f3489b8e2d4fd4484acd79c5e91f9fe998ca6f65903993cb97c7` |
| Current `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_CONNECTED_R4.png` | `d28fd039c91963509bb2752eb45d3fd300297d72b1473f41527c73deab3b7f3a` |
| Current `MICA_C03_E_RUN_FLIGHT_L_RUNTIME_RGBA_CONNECTED_R4_QA.json` | `38364e74dedf016dfe4b4e84d861dfab12ed19d474973ebd3521c7c44e20fe11` |
| Inspected `tools/character_pipeline/derive_chroma_runtime_rgba.py` | `5ce0b7793f03a765847263a6deb60c996df38d2d158ef5cb498e6e0ab8997dcd` |
| Existing `PONYTAIL_MICA_E_FLIGHT_L_REVIEW_R1.md` | `48406b6ac1cd256aa0ceaa26bede99e1a9d9cde2c35a4b79b81f8f4e28e86979` |

## Unchanged production disposition

The frame's anatomical right-thigh beige plate remains on the trailing leg, contradicting `flight_l` right-leg-leading semantics. **The frame remains FAIL_NOT_PROMOTABLE.** Strict whole-body E direction also has not received PASS. Do not relabel the frame, rewrite the earlier review, seal a PASS frame receipt, use it in a runtime atlas or dispose of failed evidence because this isolated matte diagnostic improved.

This report authorizes no new image attempt, no character promotion and no HTML/Luna completion claim. Only the observed connected-matting mechanism and listed exact diagnostic checks pass.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent mechanism review.
