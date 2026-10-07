# Ponytail FULL — MICA flight_l ImageGen repair review R2

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- Review UTC: 2026-09-07T16:28:09Z (2026-09-08 01:28:09 KST).
- Actor / costume: `CHR_PROTO_03` / `MICA_RECON_C03`.
- Exact raw SHA-256: `f35c120e4ff1c63b03100eb9a0581ba674c5617e59d70788baa40e242d3bee17`.
- Request subject: `e9e2719c93cecd0453cddd640150ac43404abc235b0fdf16631c6db90d0356a6` (single-attempt request subject, not a completed frame-audit subject).
- Overall verdict: **FAIL_NOT_PROMOTABLE. The anatomical laterality repair did not succeed.**
- Applied: Ponytail FULL and `sable-motion-production`. This is a read-only review plus this report; no generation, rendering, production-code edits, asset modifications, runtime, promotion or Luna execution was performed.

## Evidence actually inspected

I directly opened the new 1254×1254 RGB repair output and the proposed alternative edit target, the quarantined flight_r R2 raw. I read the exact request, prompt, permit, latest target failure manifest and relevant request-audit caller. I independently verified all eleven request path/hash references: every hash matched. The approved S source, older E reference, current failed flight_l target and exact F6 guide had already been directly inspected during the immediately preceding independent reviews; their immutable hashes matched those same references here.

The new directory contained the raw, request, prompt and one permit only at inspection time. No current raw-specific RGBA/mask/normalization evidence, annotated frame audit, completed receipt or native 1920×1080-or-larger review board was supplied. I do not transfer another image's matte approval to this raw. Original-scale inspection suffices to establish the rejection below; it is not a passed 1080p evidence-container or full-frame gate.

## Seven required verdicts

| Contract check | Verdict | Actual evidence and limitation |
| --- | --- | --- |
| `identity_and_costume` | PASS, static recognition only | MICA's face, brown side braid, navy/beige/teal coat, fitted trousers, pouches, guards, boots, cyan equipment and rifle remain recognizable. The beige right-thigh marker exists, but remains on the trailing side. Its identity establishes the phase failure rather than approving the requested pose. |
| `anatomy_and_limb_count` | PASS, one frame only | Two coherent arms and legs, two boots and one head. No obvious duplicate hand, disconnected knee, crossed feet or barrel-shaped calf is visible. No temporal deformation quality is established. |
| `whole_body_direction` | HOLD | Face, gun and leg travel face screen-right, without a gross 90-degree waist snap. The chest/zipper/lapels and pelvis remain three-quarter rather than strict E profile. The requested profile correction is not established. The older E source has the same limitation and cannot override this requirement. |
| `phase_and_stride` | **FAIL** | The stride is broad and airborne-looking, not a tiny in-place shuffle. The beige vertical-plate **anatomical right** thigh is still the trailing thigh. The unmarked left leg leads. `flight_l` explicitly requires the **right leg leading after left toe-off**. |
| `feet_ankles_and_contact` | PASS, static airborne silhouette only | The front boot follows its shin and the rear boot pitches down behind it. No obvious 90-degree sideways ankle yaw, swollen calf or foot merge is visible. Neither foot is claimed planted; independent ground clearance, prior toe-off and a continuous support cycle remain unverified. |
| `weapon_hands_and_visible_muzzle` | PASS, static image only | Two-hand support remains coherent and the main horizontal right-facing muzzle is distinct from the lower auxiliary cylinder. No projectile or runtime socket exists in this reviewed evidence, so actual moving-fire alignment is not approved. |
| `matte_edges_and_subject_preservation` | HOLD | This raw is RGB with green background, not transparent. No raw-specific keyed derivative or edge-preservation proof was provided. The background is not literally uniform `(0,255,0)`; it has visible generated texture and measured corner variation. A separately reviewed matte may normalize genuine background, but it cannot repair the failed leg relationship. |

Result: four tightly scoped static PASS checks, two HOLD checks and one FAIL. No full-frame PASS.

## Exact anatomical contradiction

The approved S neutral reference is frontal: the beige vertical-plate thigh pouch is on its screen-left/anatomical-right leg. The opposite thigh has dark equipment without that beige plate. This side relation is explicitly bound in the current request and prompt.

In the repair raw, that beige vertical plate occupies approximately **x575–590, y675–738**. The carrying thigh runs downward/back to the bent knee around x530/y830 and then to the screen-left rear boot. The unmarked opposite thigh extends toward the front knee around x838/y755 and the leading boot around x990/y1050. The visible right-side braid and near-side trigger arm are consistent with the marked near-side right leg, not with renaming the forward leg.

The resulting laterality is therefore still the opposite of the requested `flight_l`. If the leading leg is instead asserted to be anatomical right, the distinctive right-only equipment has migrated to the opposite side and costume continuity fails instead. An annotation cannot make either interpretation a complete PASS.

The targeted edit changed the drawing's coat sweep and leg configuration, but did not accomplish its central requested side correction. Neither `operation=repair_failed_frame` nor the presence of explicit marker prose is evidence that the output followed those instructions.

## Background observation

The raw is **1254×1254 RGB**, with no source alpha channel. Its four corner RGB values are `(35,210,29)`, `(32,211,23)`, `(33,213,24)` and `(33,217,26)`. No obvious floor or cast shadow is depicted, and the character is fully inside the frame. The nonuniform generated green still requires this new raw's own preserved-master/keyed-derivative review; the prior CONNECTED_R4 approval was explicitly tied to a different hash.

## Proposed next mechanism — design assessment only

Proposed primary target:

`artifacts/quarantine/generation_diagnostics/mica_astra_e_flight_r_r2_failed_review/MICA_C03_E_RUN_FLIGHT_R_IMAGEGEN_RAW.png`

SHA-256: `2c2cca4bcf5a806ba315810fc88367d2481d62418d464033903bdab40bff53f8`.

I opened it again: the beige right-thigh marker is visibly on the forward leg. Thus it contains the **actual right-leading relation needed by the new flight_l request**, despite having originally failed its different, left-leading flight_r request. Its existing FAIL status and original phase history must not change.

Using that raw as the primary ImageGen edit target is a **reasonable mechanism change to reduce contradictory pose guidance**: the principal image would already contain the required marked leading leg, instead of asking ImageGen to preserve a strong target silhouette while reversing that target's anatomical lead. This can avoid specifying the wrong lead relation in the primary target. It does **not** prove that internal ImageGen “target dominance” caused the current failure, nor guarantee that another edit will obey the reference. That causal interpretation is an inference, not an observed model-internals fact.

The allowed visual repair would still have to genuinely correct the chest/pelvis/whole-body E profile while preserving the marked leg relation, identity and weapon. A torso-only edit must not leave frontal hips or misaligned knees/boots outside its accepted scope. Any required missing pixels are ImageGen-authored, not locally repainted or rebuilt. The connected matte is a separate deterministic derivative and requires fresh evidence for the resulting raw.

**Design disposition: plausible diagnostic direction, not production authorization.** Reusing the failed bytes unchanged under a flight_l filename, merely changing annotations, or recompressing them is not the proposed repair and is not allowed. A fresh ImageGen output still needs all seven independent checks.

### Required fail-closed bindings

1. Bind the exact new request/prompt, `operation=repair_failed_frame`, fresh single-output permit, project-local unused output path and actual ImageGen target/reference invocation provenance. One permit allows one output, not an unreviewed batch or silent retries.
2. Bind the **selected target's own** raw SHA and quarantine failure manifest. Preserve its old `flight_r` phase and rejection reasons. If the most recent failed attempt is a different image, bind that recent failure separately rather than pretending it is the selected target's provenance.
3. Resolve the target to an exact raw entry in that target failure manifest's file inventory, under its recorded quarantine path. Check actor/costume, path, hash and rejected status. An unrelated hashed PNG plus an unrelated failure JSON is not a valid repair relationship.
4. Bind unchanged `SOURCE_RECEIPT_R7`, source identity/costume and asymmetric marker authority. Keep the anatomical-right beige plate and anatomical-left plate-free equipment invariant; neither screen position nor the old filename establishes laterality.
5. Bind the actual F6 Sprint_Loop E guide, capture, licensed blend/model, exact `flight_l` support definition and both independent guide reviews. The old target's phase label is not motion authority for the new request.
6. Record that the target is **failed visual edit material**, not an approved production frame or source replacement. Bind any secondary references by exact role/hash; do not use the older three-quarter E reference as an override for strict E body direction.
7. Require a genuinely new ImageGen result and independently visible completion of the intended profile repair. A new file hash by itself is not proof of a new successful visual edit. Do not reuse the old target's frame/phase review or receipt.
8. Bind the new raw, preserved normalized master, mask, connected-matte implementation/QA, runtime RGBA and fresh native review evidence to the same final subject. Recheck dark boundaries, closed gaps and cyan/teal preservation on this new content; do not carry the previous raw's CONNECTED_R4 PASS forward.
9. Maintain separate disposition gates: this next output could pass one static frame only. Full-cycle grounding, temporal stride, eight directions, movement×aim firing, runtime rates and HTML remain HOLD until their actual evidence passes. All failed batches remain in quarantine until the user's completed-replacement disposal conditions are met.

### Concrete current request-audit gap

In the inspected `visible_frame_harness.py` (`audit_request`, lines 138–151), `previous_failure` and `repair_target` are individually resolved and hashed, but the code does **not** verify that the target belongs to that failure manifest's raw inventory or has the same actor/costume. The exact-reference binding around lines 198–201 preserves both independent values without establishing their semantic relationship.

By inspection, a valid existing but unrelated project PNG could therefore replace `repair_target` alongside a valid unrelated failure JSON without this particular relationship check producing an error. I did not execute that altered request or create another permit. The proposed different-phase target makes the missing relationship particularly important: the selected target's own historical failure must be explicit, not confused with the latest retry failure. This gap needs a fail-closed linkage before treating the request gate itself as verification of the proposed repair provenance.

Inspected code SHA-256: `5ea1e80764d5727c0e6373e5aaea63983b274f16f77d36234cd89c8776111db1`. This finding applies to that revision; no code was modified by this reviewer.

## Exact reviewed artifact hashes

Candidate root: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r2_e_flight_l_repair/`.

| Artifact | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_L_REPAIR_R2_IMAGEGEN_RAW.png` | `f35c120e4ff1c63b03100eb9a0581ba674c5617e59d70788baa40e242d3bee17` |
| `REQUEST.json` | `aadc5d8aa50dd5818d7968b2302584a621794fda2d113e4aa6e18253c21f68b8` |
| `PROMPT.txt` | `3d3321aa0af26a022dc25df4d20b146f4fdb7d48bc67a71e175cdefeef4fe415` |
| Single-attempt permit | `5c0877cf42f3cbf2d6da8f476262fcf6591703f8c7a81f742d0254134c433288` |
| Failed flight_l R1 target raw | `548872ee7d748d738ca6deb0bebe0bb5f3b42e948d91c9bf78cb8535fed9d692` |
| Failed flight_l R1 quarantine manifest | `73fbd8d2bf47faf97fd7492b4a3e3f4e35dc4cffebd1e14089d578058ca11526` |
| Proposed alternative flight_r R2 target raw | `2c2cca4bcf5a806ba315810fc88367d2481d62418d464033903bdab40bff53f8` |
| Approved source receipt R7 | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |
| F6 guide image | `b5b2769d207106dd00cce4a171c133eb4088dcc031303e8945530a803ba19988` |
| F6 guide review bundle | `4e391f2742d34ffd46c4621854475b64400b9ea0a29089e71f3af35573ea7e0b` |
| Older E appearance/weapon reference | `57f13ac47daa5b4b786ad8ae69e57eb79baeb4d75593e5146899cdb0b4468584` |

## Final disposition

Preserve the current failed repair output, request, permit and review with exact quarantine provenance. Do not seal or promote it. The mechanism assessment above is not approval to generate, not a new source-art approval, and not proof of temporal motion, runtime firing, HTML or Luna readiness.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent review.
