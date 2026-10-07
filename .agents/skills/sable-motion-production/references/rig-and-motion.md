# Rig, retarget and motion construction

## Choose a supported starting point

Read `art-motion-boundary.md` first. A properly licensed weighted humanoid may
be used as a motion/body-rig reference, not a replacement rendered character.
Approved ImageGen appearance must be preserved by the actual motion adapter.
VRoid is not permission for MICA costume reconstruction. Do not use the rejected pilot's
procedural cylinders, image-plane legs or rectangular coat patches as a fallback.

Installed local tools and exact license evidence are recorded in
`tools/licenses/vroid_studio/INSTALLED_TOOL_REVIEW.json`.
Use `inspect_vrm_source.py --input MODEL --license MODEL_LICENSE --out REPORT`
on a project-local VRM before adopting it. A clean intake is still HOLD until
Blender import, materials, UAL retarget and visual tests succeed.

VRoid/VRM can introduce large anime heads, narrow hips, hidden body faces under
clothes, MToon node groups, spring bones and different humanoid/rest-pose axes.
Never treat an import success or matching bone names as retarget success.
The current collector deliberately rejects unsupported shader node groups;
do not bypass that rejection. Add a narrowly tested adapter or convert the
project-local candidate's material graph to the supported graph, then re-review.
Do not modify the installed editor/add-on or silently substitute VRoid textures
for ImageGen source art. The user authorized commercially usable body-model
downloads; inspect exact licenses and save approved downloads inside this project.

## Mesh contract before rendering

In Blender, author `scene["generation_mesh_contract"]` as JSON containing:

- `body_height_m`, `required_parts` mapping every mesh name to its anatomical or
  garment role; `sole_mesh` and distinct left/right `sole_vertex_ids` (≥3 each).
- `attachments`: explicit named pairs of actual vertex sets on joining meshes.
  Use full seam boundaries, not one hand-selected near point. A decorative
  single-quad upper image is never an anatomical lower-body mesh.
- `body_coordinate_frame`, `body_axes_world` (forward/left/up unit vectors),
  `ground_origin_world_m`. Confirm right-handed, Z-up, ground-level origin.

Every anatomical mesh has a render-enabled real Armature modifier, normalized
weights, closed nondegenerate geometry and genuine volume. Required sole IDs
must be on the visible weighted boot/foot surface, not a hidden helper mesh.
Preserve vertex identity during evaluation; unsupported topology-changing
anatomical modifiers must be removed or explicitly adapted and tested.

Set `scene["generation_source_charts"]` to named charts with the source image,
semantic mask, purpose and allowed mesh parts from source approval. Each
textured mesh has a FACE-domain integer `generation_chart_id` and JSON object
`generation_chart_table` mapping IDs to charts. UVs are per-loop, never mixed
across front/profile/back charts within one triangle. The harness samples
triangle interiors and the filter footprint, not just its three corners.

### Retired appearance reconstruction is not a motion starting point

The anatomical pilot's source-projected face, procedural scalp/coat and voxel
shoe recipe was rejected for reauthoring appearance. Earlier construction
scopes/receipts are historical only. Do not execute those builders or repair
their visible costume. Mathematical geometry tests may remain regressions but
cannot become a production recommendation. Recover motion implementation from
the unchanged ImageGen sources and an independently verified source-preserving
adapter. If that adapter is missing, implement it; do not restore a retired one.

For each probe, register `scene["generation_view"]`, orthographic camera,
scale/pivot, native render resolution and original frame. Collect geometry and
render in the same process. The current experimental `build_mica_skinned_pilot.py`
is gated and its old outputs are rejected; it is **not** a complete approved
character generator. Do not add invented semantics to make its checks green.

## Retarget/calibrate one clip

1. Map humanoid bones by anatomical role. Compare rest axes and bone lengths,
   not name coincidence. Check both thigh→calf→foot chains and bone roll.
2. Load the license-cleared UAL action. Keep weapon/hand sockets on the same
   actual upper rig. Verify bind pose before keyframes. Avoid 90° ankle fixes
   pasted across directions.
3. Use genuine forward/backward/strafe motion appropriate to movement relative
   to aim. Do not rotate only the lower body under a forward upper torso.
   Start with move=aim E, then N/S, then diagonals; these are limited probes,
   not permission to skip the eventual 8×8 matrix.
4. Calibrate world units and time **once**. Read actual body/foot vertices and
   the independently required actor speed from `motion_contract.json`.
   Do not tune runtime speed downward to disguise a tiny stride.
   Preserve source timestamps when resampling: UAL frames 0..32 at 24Hz are
   1.333 seconds, even if only 25 pose samples are stored. Never use sample
   index as a new frame number unless an explicit cadence transform is reviewed.
   Keep world ground-up independent from a leaning torso's inferred up axis.
5. Export ≤49 samples per invocation, enough for two complete cycles plus wrap.
   Ensure the UAL action actually repeats for the second cycle; duplicating
   receipt entries or holding the last animation frame is not a loop.
6. Check decoded runtime pixels alongside evaluated contact vertices: alternate
   support, forward excursion, foot height, stance slip, calf width, toe/ankle
   heading, body sway, cloth continuity and loop seam. Walk and run are separate
   clips and cadence/flight expectations, not one clip played faster.

Exporter config binds `generation_receipt`, `direction`, `skinned_mesh`,
`sole_vertex_ids`, `body_coordinate_frame`, `native_size`, `runtime_cell`,
output/render-receipt paths, and frames with time_s/native image/runtime image.
Use the reviewed `.blend` read-only. It is reloaded before export, and its camera
is locked at every frame. Put every output/cache/TEMP below the project.

## Fire and runtime

Read `docs/production/MOTION_PIPELINE_REBUILD_2026-09-05.md` and the exact motion
contract before packaging. Record the visible muzzle tip/axis for each actual
frame; do not use the socket table to validate itself. Muzzle and projectile
spawn share the reviewed world transform, including display scale and pivot.

Moving fire keeps the lower gait active and actual velocity constant. Verify
the real Godot actor with public movement/aim/fire input at 30/60/120Hz, including
stop/resume, turns, reload and collisions. Independent upper/lower or authored
8×8 coverage must exist as actual assets. Eight whole-body directions are not
automatically sixty-four movement/aim combinations.

If any visual check remains unresolved, quarantine the candidate and report the
specific HOLD. Continue diagnostics, not mass rendering. No model, including
Luna, is expected to guess an unimplemented retarget/material adapter into being.

## Actual Astra reference (not production approval)

See `artifacts/generation_harness_audit/ASTRA_FIRST_PRODUCTION_STATUS.md`.
The licensed Seed-san import and UAL diagnostic demonstrate control-mesh deformation,
not MICA identity, calibrated contact, eight-direction fire, or completed runtime.
Do not resume Luna tests from these intermediate results. Read the exact named
result and hashes; earlier r2 retarget data had a rejected cadence conversion.
