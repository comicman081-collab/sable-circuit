# Ponytail FULL — art authority repair and actual MICA proof review

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review date: 2026-09-07 UTC; final code snapshot inspected after 14:36 UTC.
- Scope: read-only execution-path/code/skill audit and actual source/proof pixels. No ImageGen, Blender, runtime matrix, Luna, Work, production build, or promotion was run by this reviewer. Only this review document is written here.
- Skill used: `sable-motion-production`, including its art/motion boundary, rig/motion and job-format instructions.

## Verdict

**Boundary repair: the specifically identified bypasses below are closed in the reviewed code. Production remains HOLD because `approved_motion_adapters` is empty; no working, reviewed art-preserving adapter is certified by this report.**

**Astra E contact R4: FAIL_NOT_PROMOTABLE.** The deterministic checker-background conversion removed 244 real forearm-light pixels. Preserving the remaining pixels byte-for-byte did not preserve the whole character. A subsequent code repair does not repair, approve, or supersede this failed image.

**The unchanged S neutral source is separately reviewable as source art only.** The seven source-image checks were inspected again. R5 and R6 code-bound subjects must not be carried forward after gate code changes; the final exact source-only subject/review is recorded in a separate new revision when frozen.

## Actual authority repair inspected

The execution path inspected was `next` / `audit_build_plan` → source authority → `art_authority.production_errors` → build receipt/reservation/runner and builder claims → `authorize_build` → first-pose re-audit → `authorize_animation` / final `motion_build_bindings`. This is not a review of labels alone.

| Finding / counterexample | Current result and limits |
| --- | --- |
| The four anatomical/skinned MICA builder/runner entrypoints reconstructed face, hair, costume and boots locally. | All four current modules contain an unconditional top-level `RuntimeError` tombstone. Their original files are preserved in `artifacts/quarantine/generation_diagnostics/art_authority_retired_scripts_r1`. AST and actual preserved hashes were checked. `art_authority.py:16` denies both retired paths and known content hashes; path/content rejection precedes stale dependency errors. |
| A new or one-line-edited builder could previously pass `authorize_build(..., diagnostic=True)` under quarantine. A truthy string could select that branch. | `generation_harness.py` now requires a real boolean. `True` always raises `CHARACTER_BUILD_HAS_NO_DIAGNOSTIC_BYPASS`; string `"false"` raises `DIAGNOSTIC_FLAG_MUST_BE_BOOLEAN`. These two failures were exercised read-only without creating an output directory. Retired code is denied before this branch. |
| Source-only approval could previously stand in for a newly reviewed actual builder. | The fallback now raises `MOTION_ONLY_BUILD_PLAN_REQUIRED`. A real retired `job_r12.json` routed to `REPAIR_MOTION_ADAPTER_WITHOUT_REAUTHORING_ART`, not another ImageGen request. A declaration of allowed operations does not satisfy an empty adapter registry. |
| A synthetic source/first-pose receipt could previously reach production export by setting or omitting `qa_fixture_only` later. | The old escape was reproduced without rendering or writing output. The shared `assert_production_source_receipt` now reopens the original source requests and rejects any flag that is not a boolean `False`. It is called before production animation render and by final motion packaging. The exporter consumes that common authorization path. Synthetic output-path/provenance checks remain separate. |
| Adapter reviews previously bound code but did not bind the actual source, requested operations and neutral evidence. | `art_authority.py:61` now computes a subject from actor/costume/direction, art authority, operation set, source receipt/images/bindings, executable closure and neutral evidence. The entry and both required review roles must use that subject. This fixes the identified content-substitution omission; it is not a visual-quality classifier. |
| That stronger adapter subject initially introduced a cycle: policy → adapter subject → source receipt/bindings → policy hash. First registration could never stabilize. | The source audit now binds `SOURCE_AUDIT_CODE=(generation_harness.py, generation_contract.json)` plus the actual request/provenance/images/masks/annotations. The mutable downstream policy is no longer part of this source closure. This specific cycle is removed for the reviewed MICA request. |
| Removing policy from the source initially left the scope guard/policy unbound at build stage when a plan omitted them from dependencies. | The final inspected `audit_build_plan` explicitly adds `art_authority.py` and `art_authority_policy.json` to `build_authority` before calculating build bindings/subject. These are no longer optional plan declarations. This closes the intermediate missing-binding issue while keeping source → adapter → build approvals acyclic. |

The reviewed final scope-guard/build-binding snapshot is:

| File | SHA-256 |
| --- | --- |
| `tools/character_pipeline/generation_harness.py` | `0c5aaccff0d0805d447b8193dcae739818c61823eb9bf76d21ffc4788a10abb9` |
| `tools/character_pipeline/art_authority.py` | `8ca8dc2d791b27aa6b4af74105864cf20641479ab4b311a394473bbf44b4807f` |
| `tools/character_pipeline/art_authority_policy.json` | `0359c070e31a8a9a64430a277567e88eaa77e353b656f61ec2b83ec1e9a5ea82` |
| `tools/character_pipeline/normalize_painted_checker_to_green.py` | `2e771332f320484fdded1e28d5ae65cb773a7878af41f40cb556d80b03cc0ce9` |

The reviewed AGENTS/skill boundary correctly assigns visible original/repair pixels to ImageGen and approved-art-preserving rig/pose/motion work to Blender+UAL. A generic humanoid may supply a pose guide, not final character pixels. Conservative semantic swatches do not authorize remodeling a character or tiling them over newly fabricated costume geometry. The later quarantine-retention rule takes precedence over older immediate-deletion wording.

## Astra E contact R4 — actual visual evidence

Personally opened the immutable painted-checker ImageGen input, the exact-green derivative, the native 1920×1080 review board, the approved S source, and the actual E weapon reference. Compared actual pixel arrays as well as appearance. The board places the 1536×1024 source at 1:1; its 1080p container is not a claim that the source was rendered at 1920 pixels or that any animation was captured.

| Evidence | SHA-256 |
| --- | --- |
| `artifacts/quarantine/generation_diagnostics/mica_astra_e_contact_r1_alpha_fail/MICA_C03_E_RUN_CONTACT_A_IMAGEGEN_PAINTED_CHECKER_FAIL.png` | `50efd461eb2933b30bbef5baba4f05fc8501aad7c653860dbd2bc415e0912ccc` |
| `art_src/characters/mica/pose_proofs/candidate_mica_c03_astra_e_contact_r4/MICA_C03_E_RUN_CONTACT_A_EXACT_GREEN_R4.png` | `0a3bbfc47b568b615b4473f78f7ab8d451b693c366941cceab28c3bf7a508f98` |
| `artifacts/generation_harness_audit/MICA_C03_ASTRA_E_CONTACT_R4_NATIVE_1920X1080_REVIEW.png` | `7b4f2b8c2b913aaf52fdf5de347a2db3d80b1ab907c7893094d54cc7034c00b0` |

| Check | Independent judgment |
| --- | --- |
| Identity | **PASS, this static image only.** The brown side braid, face and established MICA head design are recognizable. This is not a generic locally modeled replacement face. |
| Costume / whole-subject preservation | **FAIL.** Navy tactical fabric, beige binding, teal lining, equipment and light placement are broadly continuous, but the converter deleted actual forearm-light pixels. Exact preservation is false even though the retained subset is unchanged. |
| Anatomy | **PASS for major static form only.** Two coherent legs, knees and boots are visible, with no obvious crossed-leg knot, swollen calf or right-angle waist discontinuity seen in earlier rejected images. This cannot certify joint deformation over a cycle. |
| Strict E body–leg–foot alignment | **HOLD.** Rightward intention is clear, but torso/pelvis/front-of-body surfaces remain visibly three-quarter. The picture does not establish a strict common E-facing body/hip/knee/foot coordinate frame. A rightward gun is insufficient evidence. |
| Stride | **PASS for static readability only.** A substantial front/back leg separation is visible. There is no alternating-cycle, cadence, stride-distance or speed proof. |
| Contact / grounding | **HOLD.** No actual ground, actor displacement, evaluated visible sole correspondence or adjacent time samples are present. The forward boot is raised at the toe and the trailing foot is airborne-looking; naming the image `CONTACT` does not establish planted support. |
| Weapon and hands | **PASS for visible major arrangement only.** Main carbine design and two grip placements agree with the actual E weapon reference. Hidden finger/contact details are not certified. |
| Muzzle axis / firing | **PASS for readable static barrel axis; runtime HOLD.** The main upper barrel points right and is distinguishable from the lower attachment. No shot, socket-to-visible-tip comparison or movement×aim result was supplied in this one frame. |
| Edges / separation | **FAIL.** The forearm light contains deleted subject pixels; apparent preservation in a reduced view is misleading because its cyan outline remains. The source also failed native transparency (RGB painted checker), so neither true alpha nor final runtime edges are approved. |

### Reproducible pixel cause

The old normalizer selected bright neutral regions by colour and, for large enclosed bright components, flood-filled them into the background. In source-coordinate ROI `x=700..774, y=310..344`, **244 actual forearm-light pixels** were changed; their changed bounding box is `x=711..764, y=317..338`.

Examples, source → green derivative → dark review panel:

- `(762,317)`: `[234,251,251]` → `[0,255,0]` → `[30,42,54]`.
- `(741,328)`: `[255,255,255]` → `[0,255,0]` → `[30,42,54]`.
- `(716,338)`: `[242,252,253]` → `[0,255,0]` → `[30,42,54]`.

The review panel starts at `(192,40)`. Its retained subject pixels match the derivative: this is **not evidence-board image substitution**. The defect is in the mask itself. `unchanged_subject_pixels=279656` and `subject_pixels_byte_exact=true` compare only the converter's own surviving mask; they cannot independently prove that the mask excluded no character pixels.

The repaired normalizer was inspected and its pure `checker_background` function was applied read-only to the actual failed input. It reports three ambiguous components (229, 965 and 227 bright-core pixels) and selects **zero** forearm-ROI pixels as background. `normalize` now raises before saving if those ambiguous components exist. The 227-pixel bright core is not the old 244-pixel expanded deleted region. No new derivative was made in this review. Edge-connected matte processing still needs actual independent edge review; it is not automatic visual PASS.

## Source review and unresolved production status

The unchanged S source image (`6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895`) and R3 mask/landmark board were personally reopened. Identity/costume, whole-body S facing, source scale/baseline, visible selected material regions, exclusion of foreign pixels in those masks, native source resolution and source-stage key separation remain suitable for **source-only** approval. The four masks are small visible semantic patches, not complete face/body/garment UV charts. The annotated heels are explicitly projected through opaque boots and remain approximate construction landmarks, never contact evidence.

R5 was equal to a fresh audit at its earlier snapshot. Subsequent code changes correctly made that approval stale. The requested R6 subject `a10d056da8b9dcb081338860543021b85534c7c18fa6cb0c3eea9c5110860cfa` also differed from the fresh audit after build-policy binding was repaired. A fresh subject is required; neither old report is edited to pretend that it reviewed later code.

Independent verification in this review consisted of actual file/image/hash inspection, AST checks, read-only gate calls, source-audit recalculation and pixel comparisons. The implementation owner additionally reports generation 55 tests, motion 33 tests and the repaired normalizer 3 tests passing; these full suites were not rerun by this reviewer. Their technical result is not substituted for visual review.

No real MICA eight-direction walk/run, world grounding, 8×8 move/aim firing, 30/60/120Hz actual-character matrix or playable HTML is approved here. Astra production remains unfinished; Luna reproduction and final promotion remain HOLD. Retain the failed proof, old reconstruction outputs and provenance in project quarantine under the user's disposal rule.
