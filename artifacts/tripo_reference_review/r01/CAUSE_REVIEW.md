# Tripo intake independent cause review — 2026-09-08

Status: CAUSE_CONFIRMED; corrected implementation and real output remain unreviewed.
This is a read-only cause review under Ponytail FULL semantics. No Blender process,
generation service, model inference, asset export or runtime promotion was run by
this reviewer. Reviewed failing code is the preserved r02 builder, not later edits.

The failure is an importer-created custom bone shape counted as source geometry.
It is not evidence that the scene changed. Both failed logs stop at
`ONE_BOUND_RIG_AND_MESH_REQUIRED`. The parent's single import inventory contains
one Armature, one 26,588-vertex mesh bound to that Armature, and an unskinned
42-vertex Icosphere in the same Scene. Independently decoded source GLB contains
exactly one mesh node, one skin with 41 joints, and one Run animation; the Icosphere
is absent from its source mesh inventory.

The installed Blender 5.2.1 glTF importer explains the extra object directly:
`blender/imp/node.py` lines 145–170 creates an icosphere in a hidden special
collection unless `disable_bone_shape` is true; lines 257–265 assign it to
`pose_bone.custom_shape`. Collection visibility does not remove the object from
`scene.objects`. Consequently, counting all scene meshes conflates imported skin
geometry with importer display helpers. `blender/imp/scene.py` begins from the
current scene, consistent with the actual inventory. The r01 quarantine's
`GLTF_IMPORT_CONTEXT_SCENE_CHANGED` reason was a hypothesis and must be corrected
by a new record while preserving the original evidence.

The smallest repair is to use the existing native importer option
`disable_bone_shape=True`, preserve the one-rig/one-source-mesh constraint, and
verify the mesh has an enabled Armature modifier targeting the selected rig.
This avoids either deleting an arbitrary named object or accepting arbitrary
extra meshes. If custom shapes are intentionally retained, excluding them must
use exact `pose_bone.custom_shape` object identity and reject unknown extras;
the native importer option needs less code.

The real execution path is CLI `tripo_motion_reference.py` → `build()` →
`inspect()` → shared `decode_glb()` / `accessor()` / project-local hash and path
helpers → bounded Blender subprocess → `build_tripo_standing_reference.py` →
installed glTF importer → scene validation → reference-only renders and blend →
inspection/completion evidence. Repository search found no additional caller or
existing Tripo regression test at review time. Fix this one shared inlet; do not
patch downstream assets or weaken motion/promotion gates.

Source immutability is respected by the reviewed code: the supplied GLB is only
read/imported, images are packed into the project derivative, output uses a fresh
project directory, and the source SHA is compared after the derivative is saved.
The source still hashes to
`253912742fa69261bd34ac44cf18cdde38a6a4dcc4ce17ccd0560942509c352b`.
Shared GLB decoding rejects external buffers/textures, malformed container bounds
and nonfinite values. The launcher routes process cache/temp/config paths into
the output directory and owns one bounded subprocess. No external original tool
or model artifact is mutated by this path.

Native animation timing is presently correct for this exact file. Its 123
samplers all span 0.0416666679084301–1.2916666269302368 seconds, approximately
1.25 seconds; some tracks contain 2 keys and others 31. The installed importer
maps time to frames using `fps * fps_base`. Setting 24 and 1 before import yields
the observed 1–31 frame action, with 30 frame intervals / 24 = 1.25 seconds.
Do not reinterpret 31 samples as 31 intervals, shift time using sample indices,
or resample a standing derivative into the original Run action. A corrected
builder should compare imported timing with the exact intake and record the
comparison. A future standing pose must be a separate action/scene derivative,
with the original Run keys and bind/rest data preserved and checked.

The reviewed implementation exports REST_FRONT, REST_SIDE and RUN_START reference
views plus SOURCE_RUN.blend. It does not yet create the separately authored
standing action promised by its docstring, and that inspection alone is not the
user's completed standing body pack. Its `production_ready=False` and
`visible_art_authority=none` boundary is appropriate. Tripo reference geometry,
surface appearance, textures and renders cannot become SABLE visible artwork,
an atlas or runtime character layer. Any SABLE use still requires the exact
source-preserving art mechanism and independent motion/contact/runtime gates.

License review here verifies the exact GLB binding and the local evidence record,
including the user's paid-at-generation attestation. No account/invoice was
independently inspected. The artifact is a supplied output, not a local inference
weight. This does not create broader rights or replace input-artwork rights.

Required next verification: one corrected bounded import must contain the exact
source mesh/skin binding and preserve source hash plus native timing. Run the
smallest regression that fails if helper meshes are again counted as source
geometry or unknown/unbound geometry is admitted. Review the produced standing
pack and native-resolution geometry evidence independently. No visual, contact,
gait, eight-direction, firing or runtime PASS is issued by this report.
