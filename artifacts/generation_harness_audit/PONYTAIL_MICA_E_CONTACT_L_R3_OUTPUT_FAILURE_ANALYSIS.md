# MICA E/contact_l R3 output — independent failure analysis

Reviewer: `/root/ponytail_motion_audit`, Ponytail FULL. UTC: 2026-09-07T20:16:20Z.

Output verdict: **FAIL_NOT_PROMOTABLE**.
Next-production verdict: **HOLD — neither output-adaptive ground redefinition nor another unchanged built-in edit is approved.**

The input repair scope was subject `5064be6bed0756a9cc101d5c1b24292971540ee1e1d3832aeae6f8831c55a0dd`. That scope-only approval did not guarantee ImageGen's compliance. The actual R3 failed more than the absolute baseline: the edit did not maintain immutable pixels outside its allowed regions, and it introduced a ground-shadow shape. This report preserves the prior reviews and failures.

## What I actually inspected

Opened the native 1024×1536 raw, normalized green master, saved mask and runtime RGBA; inspected native foot crops, including RGBA against a light background. Read the exact executed REQUEST/PROMPT, normalization/alpha QA, quarantine inventory and failure record. Compared the unchanged R1 target, approved neutral/true-E MICA sources and exact previously reviewed R12 contact guide. Independently recomputed pixel bounds, mask/alpha differences, fixed-region image correspondence and outside-edit RGB differences. Analysis was in memory/stdout only; no image/code/candidate was modified or generated.

## Findings separated from their limits

| Area | Independent finding |
|---|---|
| Identity / costume | MICA remains recognizable, and exactly two dark cyan-lit back devices returned. The face, braid, coat and weapon are broadly consistent visually. **This is not immutable-region preservation:** outside the two allowed areas, widespread RGB reauthoring occurred. Full identity/costume/texture continuity approval remains HOLD rather than inferred from recognizability. |
| Anatomical laterality | **PASS for this static relation:** plate-free anatomical LEFT leads toward screen-right; beige-plate anatomical RIGHT trails. No marker swap is visible. |
| E direction / anatomy | Head, torso, pelvis, knees and boots remain coherently E-facing; no obvious 90-degree waist/ankle yaw, extra leg or bulbous calf is visible. This is a limited static observation, not gait approval. |
| Contact / stride | The leading sole is substantially flatter and the trailing boot remains raised. The leading lower-leg/foot also moved inward, reducing forward excursion relative to R1; this cannot be described as only a vertical six-pixel error. The pose is a more credible support candidate, but initial-contact phase, stride and temporal loading remain HOLD. No world-contact measurement transfers automatically from the generic R12 model into this new raster. |
| Ground / shadow | Raw and normalized images contain a thin dark ground-shadow wedge extending beneath/beyond the toe, despite the explicit no-shadow requirement. The edge-connected mask includes part of it. The later ratio-aware alpha removes much of its green-tinted area, so the edge mask and final visible sole are **not interchangeable contact evidence**. |
| Weapon / matte | Main muzzle and coherent two-hand grip remain visible. No new independent muzzle annotation or firing test exists. Retained RGBA RGB is byte-identical to this R3 raw, but that proves derivative fidelity to R3, not preservation of R1. Alpha/weapon/sequence approval remains HOLD. |

### Baseline measurements: confirm the error without misdescribing the 50px test

The reviewed line was y=1250±2, with no subject pixel below y=1252.

| Actual representation | Maximum y | Excess over 1252 | Lowest row |
|---|---:|---:|---|
| Saved edge mask | 1258 | 6px | x619..648, 30 pixels |
| Actual final RGBA alpha | 1257 | 5px | x622..650, 29 pixels |

Both representations fail the fixed maximum. However, **30 pixels on one lowest row is not the same test as 50 horizontal sole pixels inside a five-row band**. I measured y=1248..1252 in the leading-foot ROI x570..849/y1150..1299:

- Saved edge mask: 190 unique foreground x columns in the band; 61 columns whose actual lower envelope lies in the band; longest continuous lower-envelope run 60px, x745..804.
- Runtime alpha: 143 unique foreground x columns in the band; 59 lower-envelope columns; longest continuous run **44px**, x734..777. Other runs are 1, 6 and 8px.

Thus a simple foreground-band count can pass while including sole interiors/shadow, and counting only the lowest row can incorrectly fail the band test. Contact must use independently identified **actual visible sole lower contour**, a fixed contact-tolerance definition and original-scale visual review. A continuous-50px requirement, if intended, must be explicitly specified prospectively; it must not be silently added to reinterpret this historical scope. The maximum-y failure is already decisive without that reinterpretation.

The one-pixel difference between saved edge mask and current ratio-aware alpha is expected from different separation rules; it does not erase the failure. In particular, raw `(640,1258)=[9,83,19]` is retained by the coarse edge mask but transparent in runtime alpha. A reported 1080p container or zero strong-green alpha boundary cannot prove that these mask pixels are anatomical sole pixels.

### Whole-frame preservation is not a common root translation

For a conservative independent check, I excluded two rectangles covering both old/new editable content: back-device region `[330,140,480,590]` and leading lower-leg region `[540,800,950,1320]`, in half-open xyxy coordinates. Among **244,599** common subject pixels outside those regions:

- Exact RGB equality: **0.0050777** (0.5078%).
- Any channel difference greater than 8: **0.501110** (50.1110%).
- Mean absolute RGB difference: **12.87984**.

These independently reproduce the parent's differently masked comparison in scale, without claiming identical ROIs. They prove literal outside-region pixel immutability failed. They alone do not prove every colour difference changes character identity; colour/texture regeneration and geometric drift must be distinguished.

Native grayscale patch correlation, allowing translation only within ±10px, found:

| Preserved patch (R1 xyxy) | Best R1→R3 dx,dy | Correlation |
|---|---|---:|
| Face `[540,280,640,380]` | -1, -3 | 0.9677 |
| Rifle cyan ring `[742,431,795,481]` | -1, -2 | 0.9775 |
| Waist buckle `[503,641,541,668]` | -1, -1 | 0.7388 |
| Right thigh plate `[400,801,429,865]` | 0, -1 | 0.9662 |
| Trailing boot `[85,986,158,1127]` | 0, 0 | 0.9669 |

This is limited image correspondence, not an anatomical rig registration. Nevertheless, it rules out treating the entire discrepancy as a uniform downward shift: upper-body patches moved slightly upward, the trailing boot stayed essentially fixed, and the leading sole reached farther downward. The changed upper bbox y220→187 is mainly the newly restored devices, not a 33px head/root rise. Centroid changes likewise mix new devices and changed leg geometry; they are not actor-root measurements.

## Root cause in the present generation mechanism

The request correctly described fixed limits, but the actual built-in image operation is a probabilistic full-frame edit. The exposed call accepts prompt/reference images; it has no independently demonstrated hard edit-mask or protected-pixel interface in this workflow. “Immutable”, “50 pixels” and “y=1250” were prompt instructions, not enforced spatial constraints. The generator approximately repaired the foot and devices while resynthesizing other pixels and inventing a visual contact shadow. Exact scope review verifies intent and provenance; it cannot convert those prompt words into control the generation tool does not provide.

The separation step did not cause the widespread R1→R3 RGB change: all final retained R3 pixels match the R3 raw exactly. It did, however, change which green-tinted shadow/edge pixels counted as foreground, so the saved broad mask is unsuitable as the sole authority for final contact.

## Decision on A / B and the exact next mechanism

**A — do not apply it to rescue R3.** An output's bounding box, centroid or lowest sole must not redefine its own floor. An actor-ground plane and a genuinely independent body anchor can be a sound *prospective* packaging contract, but the anchor transform must be fixed from source/rig calibration and measured at several non-edited landmarks, with scale and allowed registration already reviewed. Here the foot's discrepancy is not the common body shift, so output-specific rebaselining would conceal error rather than remove canvas placement noise. It would also leave outside-scope reauthoring and shadow defects unresolved.

**B — not another prompt-only edit, even with a mask merely supplied as an extra reference.** No repeated built-in edit is recommended. A reference mask is still advisory unless a real protected-region mechanism exists and has been verified.

**Selected next step: HOLD production and establish an actually enforced spatial-preservation boundary using the existing R1/R3 evidence before requesting more art.** The bounded mechanism to implement/review is:

1. Declare editable regions from anatomy and the approved repair scope, not from wherever the generated image happened to change. Keep the source file, native canvas, body landmarks and actor-ground mapping immutable. Separate semantic costume continuity from byte-preservation claims.
2. Demonstrate that the actual production route retains every protected visible source pixel and admits only the intended ImageGen-authored patch pixels, with exact provenance. This requires either a genuine hard-masked edit capability, or a **separately authorized and independently reviewed** source-preserving assembly of new ImageGen-authored layers. Neither exists merely because a binary mask is attached to a prompt. Do not introduce an unreviewed compositor, local painting/inpainting, whole-leg warp, generic Blender pixels, or hidden post-hoc y offset.
3. Test the boundary offline with existing R1/R3 as negative evidence: outside-edit reauthoring must fail; the new shadow must not become contact; final alpha's actual sole contour must be used; registration cannot be fitted to the foot. Verify joint/garment continuity at edit boundaries before any production attempt. Do not silently overwrite R3 with reconstructed pixels.
4. Only after that mechanism has exact reviewed evidence should a new one-output request be considered. Its body/ground rule and contact morphology must be fixed in advance, and its full frame/matte/phase reviews remain mandatory.

This is implementation/diagnostic work, not a request for an additional generation service, an assumption of new authority, or an authorization to generate now. If an enforced boundary cannot be provided within the authorized tools, report that specific limitation instead of running the same probabilistic edit again or relaxing the current failed threshold.

### Is R3 a suitable repair target?

R3 is a useful **quarantined diagnostic and potential future source of a reviewed ImageGen patch**: its laterality is correct, the two devices are present and the foot is flatter. It is **not currently eligible for a baseline-only repair-target PASS with “all other pixels already approved/preserved”**, because that premise is false. Do not promote it, relabel it, delete it, or select its own sole as new ground. Any future target scope needs fresh independent review of the changed appearance and actual preservation mechanism. A local source-preserving assembly, if separately authorized, must not be mistaken for the previously rejected cutout/warped-leg animation recipe.

## Exact evidence hashes

Quarantine directory: `artifacts/quarantine/generation_diagnostics/mica_c03_astra_e_contact_l_r12_r3_repair_baseline_fail/`. All following unqualified filenames are within it.

| File | SHA-256 |
|---|---|
| `QUARANTINE_MANIFEST.json` | `c5bb0ac277ab0020afad4c4211ca31c29d33adc66982efda4d95f19634d94ff5` |
| `FAIL_REVIEW.md` | `78ad4a8b462dd66acd5184c1d1636c17e2a4a5a26401ff463e2ffefc8fa1db36` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_IMAGEGEN_RAW.png` | `4137f95c8a3be70971932198a8e7504b13a889de69fce8e9f783e8e1eb9dc338` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_EXACT_GREEN.png` | `55ff193dd0650f158dc9ea65a972a4d11ebbfdbeef2ecee1ea591ded5e0ee30d` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_EDGE_MASK.png` | `b0a13d6b53809b37988edd91a7c4a12e541067514fbee9759ae5c28c2cf1926b` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_RUNTIME_RGBA.png` | `fc3c9ad44161a0551fb7314627f48b47383845684d19305f7a2821d6f0d907e7` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_NORMALIZATION_QA.json` | `0d90ea8e2f4fa981936f688e2f698fb3cee8a1f2303cc5ef3b92f08520a0362f` |
| `MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_RUNTIME_RGBA_QA.json` | `1c80d7cfe3880ae6505ed2affa3b16bac05ce49b3bbfc82027ed76433c5859f9` |
| `REQUEST.json` | `fdbb77ed4e07e92b758686bc192f6e1e04c83691019dbc17313409ba06b641c6` |
| `PROMPT.txt` | `798a19767ab685c875d902070e9781c31ec24ec721db681e62042887f0ec44fc` |
| `REPAIR_TARGET_REVIEW_BUNDLE.json` | `1d1a3251ab5117a5935b1ecaf38d8f19ca4cfed55e9a1b813a1d6f5b5c13abf2` |
| R1 raw, exact request target | `351443d83408de0418df2722c7cf29b80c2bc123d62ac633c2eedc7fba31d4ba` |
| R1 `QUARANTINE_MANIFEST_R2.json` | `948da7ca2e63ac32a63af73283e20c531192eec1db4b1a8cb76d18703bac6e92` |
| Exact R12 `frames/contact_l.png` | `a67d1f6aed89a12846318e10c83df09b285d2a876fb6ae6fed148a33d509a815` |
| Exact R12 `contact_calibration.json` | `9cab39b65b10762cdb024c81a172c7d0a99b4a4d0a52a631a362bed48a0c3207` |
| `tools/character_pipeline/derive_chroma_runtime_rgba.py` | `a72d94d664ccc536d2f84fa1c713c3cd91bc8cbc26e4283fc0450bd2fd74e603` |

Signed: `/root/ponytail_motion_audit` — Ponytail FULL; `sable-motion-production` applied. No MICA/source/frame/contact/gait/firing/runtime/HTML completion, promotion or Luna approval.
