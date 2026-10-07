# Ponytail FULL — build-plan / anatomical builder code review R2

Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.  
Date: 2026-09-07.  
Verdict: **R1 authority-boundary fixes accepted by code review; HOLD first construction until the boot outer-surface issue below is fixed.**

This review used code, existing R4 anatomical-rig metadata, source-mask pixels, and regression-test source. It did not run Blender/Godot/tests or generate/render a character. The main agent's reported 47/49 unit-test results are not a new independent execution result. Source, mesh appearance, gait, HTML and Astra-before-Luna completion remain separate approvals. Only this report was written.

## Reviewed snapshot

- `generation_harness.py`: `4a10c7ca1464b21ee57fa0e55e74ffdf8ceaf89159c7b9ec72433bbfae60bc46`.
- `generation_contract.json`: `da9ce074cdc1abf34ae888b29b5a895a9e3fcf5b4767c40805fcc5ee8d517d81`.
- `build_mica_anatomical_candidate.py`: `1e217afca7a9438954e76da220fd2e6044fb764b94cf71eafc2351d794ffd565`.
- `run_mica_anatomical_candidate.py`: `e2f0fb7da2f47b7b5f260e74b32373ae73c510ba9a38e23df0b2701e0e6cfd31`.
- `MICA_ANATOMICAL_FIRST_CONSTRUCTION_SCOPE.md`: `422b2ea99ce55283bee51577f2f378a9f43df4a19761434f3a6664755b2d1688`.
- Existing collector is preserved at `6d540f387cc3e93780ecfdd8795e7e127317f26985e486a40ca1fe10864b6805`.

## R1 findings: closed in the shared gate

1. **Construction and resume cannot be omitted.** `audit_pose_bundle` lines 584–591 requires construction unless every source is explicitly synthetic and the actual bundle/mesh/blend/pose/render evidence stays in the unit-fixture area. `next_action` now checks the selected plan and receipt before the existing-mesh branch; lines 875–882 bind the actual construction receipt, attempt, both execution claims, direction and output root. The prior absent-construction/preexisting-mesh shortcut no longer proceeds through the production route.
2. **Actual input/output scope is rechecked.** Lines 607–615 resolve mesh/blend/construction/native/render paths under `plan.output_root` and compare both declared charts and actual collected material-image paths with `plan.source_images`. This closes the approved-but-not-selected texture case and the internally consistent outside-output pose case. Existing semantic mask/purpose/allowed-mesh-part validation remains intact.
3. **Execution is claimed once at both entrypoints.** Lines 491–518 create exact runner/builder claims with the existing atomic no-replace writer. The child requires the runner claim. `authorize_build` now requires an attempt and exact direction. The new runner claims before creating the output directory; the new direct builder verifies and claims before construction. A retained claim cannot be replayed simply by moving a failed output to quarantine. The claim references are included in the construction/pose closure.

I read the added test cases for missing construction, a preexisting mesh without a plan, missing/wrong attempt/image/direction/entrypoint, duplicate claims, actual material inputs, and output/claim scope. They target the originally reported boundaries rather than merely asserting generic PASS fields. No additional concrete P1 bypass was found in that repaired gate chain during this bounded review.

## Remaining P1: boot inner and outer surfaces become indistinguishable sole evidence

Location: `build_mica_anatomical_candidate.py:72`–79 and lines 215–219.

`fitted_region(..., close=True)` applies SOLIDIFY to the copied actual foot/calf surface, creating both an outer shell and a hidden inner shell. The later loop does not preserve or select shell provenance: **every** vertex with `z < 0.018` is set to `z = 0.006`, and all such vertices on either side become `sole_vertex_ids`.

Thus vertices on both bottom shells are forced into the same ground plane. The interior shell is not excluded from measured sole evidence, and the two bottom surfaces can overlap instead of retaining a real sole thickness. Nonzero weights and membership in a face do not establish that a sampled inner-surface vertex is externally visible. The existing collector's role/weights/face checks will not distinguish these surfaces merely because both belong to the visible `MICA_Boots` object.

This is a code/provenance finding, not a claim that a new render has already failed. The source R4 rig's actual underlying topology and weights are a valid improvement over the rejected cutout legs; the subsequent shell processing still must preserve genuine external sole measurement.

Minimum correction before the one first-pose attempt:

- Preserve explicit outer-surface vertex/face provenance when constructing/applying boot thickness, or construct a clearly identified outer sole and matching interior without collapsing both.
- Select sole IDs from the actual external, downward-facing boot bottom only; exclude inner/rim vertices even when they have the same height.
- Validate positive shell separation/non-overlap and selected vertices on the real exterior after applying thickness. Do not fix this by relabeling both layers as visible or weakening the collector.
- Keep the real anatomical foot/calf surface and weights. No cylinder, cutout, or hidden sole helper is needed.

A builder-only correction does not by itself change the current source audit subject because this new builder is authorized in the separate build plan, not inserted into the historical ImageGen request. Its new exact hash must, however, be used in the future build-plan review.

## Small remaining execution/phase notes

- At line 269, the builder hardcodes `scene.render.threads = 2`, whereas the plan validator accepts one or two threads and the runner uses the plan value. Use `plan['limits']['threads']` in the builder too. A one-thread approved plan must not silently become a two-thread render.
- The currently read skill still says the build-plan route is unimplemented and mandates the old `check_build_handoff.py`, which has no new build-receipt route. Update/remove that obsolete handoff requirement or route it to the new mandatory checks. Otherwise the documented path still blocks a valid new builder after source/build-plan approval. This can be changed without touching the old source request or permit.
- The scope correctly states **S neutral, empty hands, no weapon/motion approval**. The current general `pose_review_checks` still requires `visible_muzzle`. Do not pass that check for an absent weapon. Before neutral-pose approval can lead onward, distinguish a content-bound neutral-rig pose scope from combat/muzzle approval. This is a known subsequent gate limitation, not permission to render combat or batch motion now.

## Other inspected implementation facts

The imported input is restricted to the real body, two eyeballs and anatomical rig. The earlier rig builder applies the source transforms into mesh coordinates and sets object matrices to identity; it normalizes actual skin weights. Existing `rig_probe.json` maps the literal `Head`, pelvis, spine, thigh/calf/foot bone names used by this builder, so those names are not an evident lookup failure. The new builder clears diagnostic rig animation and restores pose bases before fitting.

The coat texture references the approved `coat` region; its four planned swatch UV corners, including their 3×3 mask neighborhoods, were independently checked against the current R3 mask and were inside it. This is not a full Blender UV/interior or visual result. Face projection, garment fit, coat outward normals, closed topology, real shoulder/waist attachment, boot shape, hair likeness and material detail still require actual preflight/native first-pose inspection. I did not infer those outcomes from code or from the earlier anatomical-rig diagnostic.

The documented license manifest identifies the selected Blender Studio realistic female base as CC0 geometry, not the separate Rain/stylized assets. This review does not broaden that selection or treat a licensed base as MICA appearance authority. All particular rig/tool/source/license inputs must still enter the exact build plan and its independent review.

## Scope of approval

The repaired shared generation gate passes this code review for the three R1 boundaries. **The anatomical builder remains HOLD at the observed hash because of the external-sole issue.** This is not a source review, a particular build-plan seal, a new Blender execution result, or a MICA visual/motion PASS.

Applied: Ponytail FULL semantics and `sable-motion-production`. Existing source masters, masks, request/permit and R3 receipt were not modified. No new framework, alternate collector, new ImageGen attempt, or old-source approval rewrite is required for the remaining fixes.
