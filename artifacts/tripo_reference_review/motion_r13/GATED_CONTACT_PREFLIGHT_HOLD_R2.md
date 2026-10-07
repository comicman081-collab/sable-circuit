Independent Ponytail FULL: **HOLD_NOT_EXECUTABLE_AS_STAGED**. Exact inputs and reproduced read-only failures are in the adjacent JSON. No reservation, execution claim, Blender job or pose was run.

The actual existing-source receipt fails `g.source_authority` with `APPROVED_SOURCE_OR_SOURCE_SET_REQUIRED`; that entry accepts only legacy source/source_set stages. The builder additionally requires the existing receipt recorded in the neutral config, so swapping in a different receipt does not connect the path. Current `generation_harness.py` also invalidates the historical exact source and neutral bindings: the actual intake verifier reports `EXISTING_SOURCE_RECEIPT_STALE`, and the neutral input's old harness hash fails resolution. This needs an explicit current admission retaining the original evidence.

The BOX report must be read through `qa_capture_inputs`, not its inherited neutral `inputs`. The latter has no `neutral` field and makes the current equality check fail. Actual successful BOX settings are `scene.cycles.pixel_filter_type` and `scene.cycles.filter_width`; the current builder addresses `scene.render` instead.

The support target is misread. Dense46 `sole_height_residual_m` is6.1213e-9 m, whereas the actual original23 desired clearance is0.002081620534 m. Residual is an error bound, not a desired height. The current comparison would reject the correctly solved pose.

The collector/CONSTRUCTION path is also incomplete. The source-surface neutral carries no legacy anatomical role/chart/body-frame/attachment/sole contract; appending only `construction` does not supply one. Its transparent unobserved closure and barycentric visible sole sampling require a source-preserving schema that validates those actual structures. The current builder neither rejects `raw.errors` nor calls `validate_collected` before writing CONSTRUCTION/render receipts. Fake anatomical roles or empty attachment declarations would not be a correction.

The distinct runner/builder exclusive claims are connected correctly, and the added native REST/positions shape/finiteness checks address earlier concerns. These do not override the six execution and schema blockers above.
