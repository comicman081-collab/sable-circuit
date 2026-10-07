"""Blender --background approved.blend --python this.py -- --config project.json.

Paired Blender animation render/evaluated mesh sampling, never controller/IK
targets or source-art painting. Requires semantic sole vertex IDs on an actual
skinned mesh and authored world root travel. The .blend input is never saved.
Fails for the old unskinned 2D cutout planes; they cannot supply 3D foot evidence.
All output is routed to the project. Config/body frame axes: forward, left, up.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def path(value):
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    if p == ROOT or not p.is_relative_to(ROOT):
        raise ValueError("Geometry inputs/outputs must be project-local")
    return p


def sha(p):
    return hashlib.sha256(path(p).read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    args = p.parse_args(sys.argv[sys.argv.index("--")+1:])
    config_path = path(args.config)
    c = json.loads(config_path.read_text(encoding="utf-8"))
    sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
    import generation_harness as generation_gate
    from collect_generation_mesh_preflight import collect_scene,validate_collected,camera_state
    import root_locked_capture

    camera_plane_mode = c.get("camera_plane_pose_matrices") is not None

    def authorize_camera_plane_motion(blend_path, scene_fingerprint=None, consume=False):
        """Consume an external permit without importing Pillow-backed intake.

        The project-Python runner verifies the first-pose receipt and source
        authority before Blender starts.  Blender only compares that immutable
        permit against this config and its read-only scene, preventing a
        dependency on Pillow in Blender's embedded Python.
        """
        permit_path = path(c["camera_plane_motion_permit"])
        permit = generation_gate.read(permit_path)
        expected = {
            "schema": 1,
            "stage": "camera_plane_motion_blender_permit",
            "config": generation_gate.ref(config_path),
            "inputs": generation_gate.ref(c["camera_plane_motion_inputs"]),
            "attempt": generation_gate.ref(c["camera_plane_motion_attempt"]),
            "generation_receipt": generation_gate.ref(c["generation_receipt"]),
            "sealed_blend": generation_gate.ref(blend_path),
            "direction": c["direction"],
            "tripo_matrices": generation_gate.ref(c["camera_plane_pose_matrices"]),
            "source_skin": generation_gate.ref(c["camera_plane_source_skin"]),
            "support_schedule": generation_gate.ref(c["camera_plane_support_schedule"]),
            "sole_binding_evidence": generation_gate.ref(c["camera_plane_sole_binding_evidence"]),
            "scene_sha256": c["approved_scene_sha256"],
            "output_root": str(path(c["output"]).parent.relative_to(ROOT)),
        }
        if permit != expected:
            raise ValueError("STALE_OR_FORGED_CAMERA_PLANE_MOTION_PERMIT")
        if scene_fingerprint is not None and permit.get("scene_sha256") != scene_fingerprint:
            raise ValueError("LIVE_CAMERA_OR_SCENE_CHANGED_AFTER_FIRST_POSE_REVIEW")
        if consume:
            consumption_path = path(c["camera_plane_motion_consumption"])
            if consumption_path.exists():
                raise ValueError("CAMERA_PLANE_MOTION_PERMIT_ALREADY_CONSUMED")
            generation_gate.write(consumption_path, {
                "schema": 1,
                "stage": "camera_plane_motion_blender_consumption",
                "permit": generation_gate.ref(permit_path),
                "inputs": generation_gate.ref(c["camera_plane_motion_inputs"]),
                "attempt": generation_gate.ref(c["camera_plane_motion_attempt"]),
                "config": generation_gate.ref(config_path),
            })
    # Shared source/mesh/native-pose gate. Calling this exporter directly is
    # not a bypass around the production runner's first-pose review.
    scene_fingerprint=None
    if type(c.get('qa_fixture_only',False)) is not bool:
        raise ValueError('QA_FIXTURE_FLAG_MUST_BE_BOOLEAN')
    if c.get('qa_fixture_only') is not True:
        if not c.get('generation_receipt'):
            raise ValueError('FIRST_POSE_RECEIPT_REQUIRED_BEFORE_ANIMATION_RENDER')
        # Restore the exact approved immutable file, discarding arbitrary live
        # material/UV/mesh/modifier edits made by an earlier script in this process.
        # After this point only this hash-bound exporter can set frame/output.
        if camera_plane_mode:
            authorize_camera_plane_motion(bpy.data.filepath)
        else:
            generation_gate.authorize_animation(c,bpy.data.filepath)
        approved_path=bpy.data.filepath
        bpy.ops.wm.open_mainfile(filepath=approved_path)
        collected=collect_scene()
        live_audit=validate_collected(collected)
        if live_audit['errors']:
            raise ValueError('LIVE_MESH_PREFLIGHT_FAILED:'+','.join(live_audit['errors']))
        scene_fingerprint=generation_gate.canonical(collected['scene'])
    if camera_plane_mode:
        authorize_camera_plane_motion(bpy.data.filepath,scene_fingerprint,consume=True)
    else:
        generation_gate.authorize_animation(c,bpy.data.filepath,scene_fingerprint)
    if not 1 <= len(c["frames"]) <= 49:
        raise ValueError("One bounded pilot only: 1..49 frames per invocation")
    scene = bpy.context.scene
    mesh = bpy.data.objects[c["skinned_mesh"]]
    body = bpy.data.objects[c["body_coordinate_frame"]]
    if mesh.type != "MESH" or not any(m.type == "ARMATURE" for m in mesh.modifiers):
        raise ValueError("Actual skinned mesh required; segmented planes cannot provide anatomy evidence")
    sole_ids = c["sole_vertex_ids"]
    if set(sole_ids) != {"left", "right"} or not sole_ids["left"] or not sole_ids["right"] or set(sole_ids["left"]) & set(sole_ids["right"]):
        raise ValueError("Distinct anatomical left/right sole vertex IDs required")
    scale = float(scene.unit_settings.scale_length)
    if not 0 < scale <= 100:
        raise ValueError("Explicit Blender scene unit scale required")
    if float(c.get('scene_unit_scale',1))!=scale:
        raise ValueError('CONFIG_UNITS_DIFFER_FROM_ACTUAL_SCENE')
    size = int(c.get("native_size", 1920))
    cell = int(c.get("runtime_cell", 384))
    if not 1920 <= size <= 4096 or not 64 <= cell <= size:
        raise ValueError("Native >=1920 square master and valid runtime cell required")
    out = path(c["output"])
    receipt_path = path(c["render_receipt"])
    if out.exists() or receipt_path.exists():
        raise ValueError("Refusing to overwrite retained geometry/render evidence")
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.use_file_extension = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    blend_hash = sha(bpy.data.filepath)
    camera_plane_contact_records = {}

    # A first-pose receipt freezes the source surface, not a throwaway Blender
    # action.  For a bounded production clip, a reviewed Tripo matrix sequence
    # may therefore be supplied as an immutable project input.  Materialize it
    # as a real in-memory Blender action before any render is made.  The opened
    # approved blend is never saved: the only new bytes are the configured frame
    # renders and evaluated-geometry ledger.
    matrix_sequence = c.get("camera_plane_pose_matrices")
    if matrix_sequence is not None:
        import numpy as np
        from mathutils import Matrix, Vector

        sequence_path = path(matrix_sequence)
        skin_path = path(c["camera_plane_source_skin"])
        rig_name = c["camera_plane_rig"]
        action_name = c["camera_plane_action_name"]
        if not isinstance(rig_name, str) or not rig_name or not isinstance(action_name, str) or not action_name:
            raise ValueError("CAMERA_PLANE_RIG_AND_ACTION_NAME_REQUIRED")
        rig = bpy.data.objects.get(rig_name)
        if rig is None or rig.type != "ARMATURE":
            raise ValueError("CAMERA_PLANE_ARMATURE_REQUIRED")
        skin = json.loads(skin_path.read_text(encoding="utf-8"))
        bones = skin.get("bone_order")
        matrices = np.load(sequence_path, allow_pickle=False)
        if (not isinstance(bones, list) or not bones or matrices.ndim != 4
                or matrices.shape[1:] != (len(bones), 4, 4) or not np.isfinite(matrices).all()):
            raise ValueError("FINITE_EXACT_CAMERA_PLANE_POSE_MATRICES_REQUIRED")
        if any(not isinstance(row, dict) or not isinstance(row.get("name"), str)
               or row["name"] not in rig.pose.bones for row in bones):
            raise ValueError("CAMERA_PLANE_SOURCE_BONE_ORDER_REQUIRED")
        if any(not isinstance(row.get("source_pose_index"), int)
               or not 0 <= row["source_pose_index"] < matrices.shape[0]
               for row in c["frames"]):
            raise ValueError("EXACT_CAMERA_PLANE_SOURCE_POSE_INDEX_REQUIRED")

        support_schedule_path = c.get("camera_plane_support_schedule")
        sole_binding_path = c.get("camera_plane_sole_binding_evidence")
        support_enabled = support_schedule_path is not None or sole_binding_path is not None
        if support_enabled and (support_schedule_path is None or sole_binding_path is None):
            raise ValueError("CAMERA_PLANE_SUPPORT_SCHEDULE_AND_SOLE_BINDING_REQUIRED")
        support_rows = {}
        support_bindings = {}
        lower_indices_by_side = {}
        target_clearance = None
        fixed_floor = None
        weights = None
        indices = None
        if support_enabled:
            schedule = json.loads(path(support_schedule_path).read_text(encoding="utf-8"))
            sole_evidence = json.loads(path(sole_binding_path).read_text(encoding="utf-8"))
            sides = schedule.get("sides")
            support_bindings = sole_evidence.get("visible_sole_bindings")
            fixed_floor = float(sole_evidence.get("fixed_neutral_floor_m"))
            target_clearance = float(c.get("camera_plane_support_target_clearance_m"))
            if (not isinstance(sides, dict) or set(sides) != {"l", "r"}
                    or not isinstance(support_bindings, dict) or set(support_bindings) != {"l", "r"}
                    or not np.isfinite(fixed_floor)
                    or not np.isfinite(target_clearance) or not 0.0 <= target_clearance <= 0.004):
                raise ValueError("REVIEWED_CAMERA_PLANE_SUPPORT_CONTRACT_REQUIRED")
            support_rows = {
                side: {int(item["sample"]): bool(item["support"])
                       for item in sides[side].get("rows", [])
                       if isinstance(item, dict) and isinstance(item.get("sample"), int)
                       and isinstance(item.get("support"), bool)}
                for side in ("l", "r")
            }
            if (not all(support_rows[side] for side in ("l", "r"))
                    or any("support_sample_index" not in row for row in c["frames"])):
                raise ValueError("EXACT_CAMERA_PLANE_SUPPORT_SAMPLE_INDEX_REQUIRED")
            weights = np.asarray(skin.get("weights"), dtype=float).reshape(-1, 4)
            indices = np.asarray(skin.get("bones"), dtype=int).reshape(-1, 4)
            if (weights.shape != indices.shape or weights.shape[0] == 0
                    or not np.isfinite(weights).all() or np.any(indices < 0)
                    or np.any(indices >= len(bones))):
                raise ValueError("FINITE_EXACT_SOURCE_SKIN_BINDING_REQUIRED")
            for side in ("l", "r"):
                binding = support_bindings[side]
                vertices_index = np.asarray(binding.get("vertices"), dtype=int)
                barycentric = np.asarray(binding.get("barycentric"), dtype=float)
                lower_names = {f"calf_{side}", f"foot_{side}", f"ball_{side}"}
                lower_indices = {index for index, bone in enumerate(bones) if bone["name"] in lower_names}
                if (vertices_index.ndim != 2 or vertices_index.shape[1] != 3
                        or barycentric.shape != vertices_index.shape
                        or np.any(vertices_index < 0) or np.any(vertices_index >= weights.shape[0])
                        or not np.isfinite(barycentric).all() or not lower_indices):
                    raise ValueError("EXACT_CAMERA_PLANE_SOLE_BINDING_REQUIRED")
                influences = (weights[vertices_index]
                              * np.isin(indices[vertices_index], list(lower_indices))).sum(axis=2)
                point_influence = (influences * barycentric).sum(axis=1)
                if np.any(point_influence < 0.95):
                    raise ValueError("SUPPORT_SOLE_NOT_OWNED_BY_LOWER_LEG_BONES")
                support_bindings[side] = {
                    "vertices": vertices_index,
                    "barycentric": barycentric,
                    "point_influence": point_influence,
                }
                lower_indices_by_side[side] = lower_indices
        camera = bpy.data.objects.get(collected["scene"]["camera"]["name"])
        if camera is None or camera.type != "CAMERA" or camera.data.type != "ORTHO":
            raise ValueError("REVIEWED_ORTHOGRAPHIC_CAMERA_REQUIRED")
        normal = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
        if abs(normal.z) < 1e-6:
            raise ValueError("CAMERA_NORMAL_MUST_AFFECT_FIXED_GROUND_AXIS")
        global_matrix_tolerance = float(c.get("camera_plane_global_matrix_tolerance"))
        if (not math.isfinite(global_matrix_tolerance)
                or not 0.0 < global_matrix_tolerance <= 1e-5):
            raise ValueError("MEASURED_CAMERA_PLANE_GLOBAL_MATRIX_TOLERANCE_REQUIRED")
        projection_materialization_tolerance = float(c.get("camera_plane_projection_materialization_tolerance"))
        if (not math.isfinite(projection_materialization_tolerance)
                or not global_matrix_tolerance <= projection_materialization_tolerance <= 1.1e-5):
            raise ValueError("MEASURED_CAMERA_PLANE_PROJECTION_MATERIALIZATION_TOLERANCE_REQUIRED")

        def reset_pose():
            for row in bones:
                rig.pose.bones[row["name"]].matrix_basis = Matrix.Identity(4)
            bpy.context.view_layer.update()

        reset_pose()
        rest_matrices = {row["name"]: Matrix(rig.data.bones[row["name"]].matrix_local) for row in bones}
        rest_joints = {
            row["name"]: {
                "head": Vector(rig.pose.bones[row["name"]].head),
                "tail": Vector(rig.pose.bones[row["name"]].tail),
            }
            for row in bones
        }

        def in_plane(vector):
            return vector - normal * vector.dot(normal)

        def signed_angle(first, second):
            return math.atan2(normal.dot(first.cross(second)), first.dot(second))

        def assert_current_global_pose(global_matrices, error_code):
            maximum_error = max(
                max(abs(float(rig.pose.bones[row["name"]].matrix[row_index][column_index])
                        - float(global_matrix[row_index][column_index]))
                    for row_index in range(4) for column_index in range(4))
                for row, global_matrix in zip(bones, global_matrices)
            )
            if maximum_error > global_matrix_tolerance:
                raise ValueError(error_code)

        def materialize_global_pose(requested_matrices, error_code):
            reset_pose()
            for index, row in enumerate(bones):
                rig.pose.bones[row["name"]].matrix = requested_matrices[index]
                bpy.context.view_layer.update()
            evaluated_matrices = [rig.pose.bones[row["name"]].matrix.copy() for row in bones]
            materialization_error = max(
                max(abs(float(evaluated[row_index][column_index])
                        - float(requested[row_index][column_index]))
                    for row_index in range(4) for column_index in range(4))
                for evaluated, requested in zip(evaluated_matrices, requested_matrices)
            )
            if materialization_error > projection_materialization_tolerance:
                raise ValueError(error_code)
            # Blender stores pose-channel transforms at its own precision.  The
            # evaluated matrices are the only honest action targets; preserving
            # the unrepresentable requested floats would make playback fail a
            # numerical comparison without changing the rendered motion.
            return evaluated_matrices, materialization_error

        def apply_camera_plane_pose(source_index):
            reset_pose()
            for index, row in enumerate(bones):
                parent = int(row.get("parent", -1))
                if parent >= index or parent < -1:
                    raise ValueError("PARENT_BEFORE_CHILD_SOURCE_BONE_ORDER_REQUIRED")
                rig.pose.bones[row["name"]].matrix = Matrix(matrices[source_index, index].tolist())
                bpy.context.view_layer.update()
            raw_joints = {
                row["name"]: {
                    "head": Vector(rig.pose.bones[row["name"]].head),
                    "tail": Vector(rig.pose.bones[row["name"]].tail),
                }
                for row in bones
            }
            requested = []
            for row in bones:
                name = row["name"]
                rest_vector = in_plane(rest_joints[name]["tail"] - rest_joints[name]["head"])
                target_vector = in_plane(raw_joints[name]["tail"] - raw_joints[name]["head"])
                angle = 0.0 if rest_vector.length < 1e-6 or target_vector.length < 1e-6 else signed_angle(
                    rest_vector.normalized(), target_vector.normalized())
                requested.append(Matrix.Translation(raw_joints[name]["head"])
                                 @ Matrix.Rotation(angle, 4, normal)
                                 @ Matrix.Translation(-rest_joints[name]["head"])
                                 @ rest_matrices[name])
            return materialize_global_pose(
                requested, "CAMERA_PLANE_PROJECTED_POSE_EXCEEDS_MEASURED_MATERIALIZATION_BOUND")

        def support_clearance(side):
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated = mesh.evaluated_get(depsgraph)
            vertices = evaluated.to_mesh()
            try:
                binding = support_bindings[side]
                ids = binding["vertices"]
                points = np.asarray([
                    [(evaluated.matrix_world @ vertices.vertices[int(vertex)].co)[axis] * scale
                     for axis in range(3)]
                    for triangle in ids for vertex in triangle
                ], dtype=float).reshape(ids.shape[0], 3, 3)
                sampled = (points * binding["barycentric"][..., None]).sum(axis=1)
                selected = int(np.argmin(sampled[:, 2]))
                return (float(sampled[selected, 2] - fixed_floor),
                        float(binding["point_influence"][selected]))
            finally:
                evaluated.to_mesh_clear()

        rig.animation_data_create()
        action = bpy.data.actions.new(action_name)
        rig.animation_data.action = action
        expected_playback = {}
        camera_plane_projection_records = {}
        for row in c["frames"]:
            frame_number = int(row["frame"])
            scene.frame_set(frame_number)
            proposed, projection_error = apply_camera_plane_pose(row["source_pose_index"])
            frame_projection_errors = [projection_error]
            if support_enabled:
                support_sample_index = row["support_sample_index"]
                if not isinstance(support_sample_index, int):
                    raise ValueError("INTEGER_CAMERA_PLANE_SUPPORT_SAMPLE_INDEX_REQUIRED")
                contact_record = {"support_sample_index": support_sample_index, "sides": {}}
                for side in ("l", "r"):
                    if not support_rows[side].get(support_sample_index, False):
                        continue
                    before_clearance, influence = support_clearance(side)
                    correction_distance = ((target_clearance - before_clearance)
                                           / (influence * normal.z))
                    correction = Matrix.Translation(normal * correction_distance)
                    proposed = [correction @ global_matrix if index in lower_indices_by_side[side]
                                else global_matrix
                                for index, global_matrix in enumerate(proposed)]
                    proposed, correction_error = materialize_global_pose(
                        proposed, "CAMERA_PLANE_SUPPORT_CORRECTION_EXCEEDS_MEASURED_MATERIALIZATION_BOUND")
                    frame_projection_errors.append(correction_error)
                    actual_clearance, _ = support_clearance(side)
                    if abs(actual_clearance - target_clearance) > 5e-5:
                        raise ValueError("ACTUAL_CAMERA_PLANE_SUPPORT_CLEARANCE_DOES_NOT_MATCH_FIXED_FLOOR")
                    contact_record["sides"][side] = {
                        "before_clearance_m": before_clearance,
                        "actual_clearance_m": actual_clearance,
                        "target_clearance_m": target_clearance,
                        "influence": influence,
                    }
                camera_plane_contact_records[str(frame_number)] = contact_record
            camera_plane_projection_records[str(frame_number)] = {
                "source_pose_index": row["source_pose_index"],
                "maximum_materialization_error": max(frame_projection_errors),
            }
            expected_playback[frame_number] = {
                bone["name"]: proposed[index].copy()
                for index, bone in enumerate(bones)
            }
            # Blender 5.2 actions record pose channels through its action-slot
            # path.  Key local TRS rather than the legacy matrix-basis fcurve
            # collection, then prove that playback returns the same globals.
            for bone in rig.pose.bones:
                location, rotation, local_scale = bone.matrix_basis.decompose()
                bone.rotation_mode = "QUATERNION"
                bone.location = location
                bone.rotation_quaternion = rotation
                bone.scale = local_scale
                bone.keyframe_insert(data_path="location", frame=frame_number)
                bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_number)
                bone.keyframe_insert(data_path="scale", frame=frame_number)
            bpy.context.view_layer.update()
            assert_current_global_pose(proposed, "CAMERA_PLANE_LOCAL_TRS_RECORDING_CHANGED_PROPOSED_TARGET")
        for row in c["frames"]:
            frame_number = int(row["frame"])
            scene.frame_set(frame_number)
            if rig.animation_data.action != action:
                raise ValueError("CAMERA_PLANE_ACTION_SLOT_NOT_ACTIVE")
            maximum_error = max(
                max(abs(float(rig.pose.bones[name].matrix[row_index][column_index])
                        - float(expected_matrix[row_index][column_index]))
                    for row_index in range(4) for column_index in range(4))
                for name, expected_matrix in expected_playback[frame_number].items()
            )
            if maximum_error > global_matrix_tolerance:
                raise ValueError("CAMERA_PLANE_RECORDED_ACTION_DOES_NOT_REPLAY_EVALUATED_POSE")
        scene.frame_set(int(c["frames"][0]["frame"]))

    actions = {o.name:o.animation_data.action.name for o in scene.objects if o.animation_data and o.animation_data.action}
    if not actions:
        raise ValueError("Authored/retargeted actions required; static mesh is not locomotion")
    frames = {}
    renders = {}
    locked_camera=collected['scene']['camera'] if c.get('qa_fixture_only') is not True else camera_state(scene)
    camera_space=c.get('camera_space','world_locked')
    if camera_space not in ('world_locked','root_translation_locked'):
        raise ValueError('UNKNOWN_CAPTURE_COORDINATE_SPACE')
    initial_ground=[list(r) for r in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world]
    for row in c["frames"]:
        scene.frame_set(int(row["frame"]))
        current_camera=camera_state(scene)
        current_ground=[list(r) for r in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world]
        if camera_space=='root_translation_locked':
            root_locked_capture.verify(locked_camera,current_camera,initial_ground,current_ground)
        else:
            generation_gate.assert_camera_lock(locked_camera,current_camera)
        contact_record = camera_plane_contact_records.get(str(row["frame"]))
        if contact_record and contact_record["sides"]:
            for side, measured in contact_record["sides"].items():
                rendered_clearance, rendered_influence = support_clearance(side)
                if (abs(rendered_clearance - measured["target_clearance_m"]) > 5e-5
                        or abs(rendered_clearance - measured["actual_clearance_m"]) > 5e-5
                        or abs(rendered_influence - measured["influence"]) > 1e-9):
                    raise ValueError("RENDERED_CAMERA_PLANE_SUPPORT_CONTACT_DIVERGED")
                measured["rendered_clearance_m"] = rendered_clearance
        native = path(row["master_image"])
        image_path = path(row["image"])
        if native.exists() or image_path.exists() or native == image_path:
            raise ValueError("New distinct native and runtime frame paths required")
        native.parent.mkdir(parents=True, exist_ok=True)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(native)
        bpy.ops.render.render(write_still=True)
        # Animation export only. Preserve the high-resolution master and derive
        # the engine cell; never upscale a sprite as review-quality evidence.
        image = bpy.data.images.load(str(native), check_existing=False)
        try:
            image.scale(cell, cell)
            image.filepath_raw = str(image_path)
            image.file_format = "PNG"
            image.save()
        finally:
            bpy.data.images.remove(image)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = mesh.evaluated_get(depsgraph)
        vertices = evaluated.to_mesh()
        try:
            positions = {}
            for i in set(sole_ids["left"] + sole_ids["right"]):
                v = evaluated.matrix_world @ vertices.vertices[int(i)].co
                positions[str(i)] = [float(x * scale) for x in v]
            matrix = body.evaluated_get(depsgraph).matrix_world.copy()
            # Body frame must have unit, orthogonal orientation; nonuniform
            # scaling would silently turn vertical height into a screen offset.
            if any(abs(v-1) > 0.001 for v in matrix.to_scale()):
                raise ValueError("Body coordinate frame must have identity scale")
            matrix.translation *= scale
            inverse = matrix.inverted()
            frames[str(row["frame"])] = {"time_s": float(row["time_s"]),
                "image_sha256": sha(row["image"]), "vertices_world_m": positions,
                "world_to_body_m": [[float(x) for x in line] for line in inverse]}
            if str(row["frame"]) in camera_plane_contact_records:
                frames[str(row["frame"])]["camera_plane_contacts"] = camera_plane_contact_records[str(row["frame"])]
            if str(row["frame"]) in camera_plane_projection_records:
                frames[str(row["frame"])]["camera_plane_projection"] = camera_plane_projection_records[str(row["frame"])]
            renders[str(row["frame"])] = {"frame":row["frame"], "actions":actions,
                "actual_camera":current_camera,"actual_ground_frame":current_ground,
                "native": {"path":str(native.relative_to(ROOT)), "sha256":sha(native)},
                "runtime": {"path":str(image_path.relative_to(ROOT)), "sha256":sha(image_path)},
                "native_resolution":[size,size], "runtime_resolution":[cell,cell],
                "geometry_frame_sha256":hashlib.sha256(json.dumps(frames[str(row["frame"])],sort_keys=True).encode()).hexdigest()}
        finally:
            evaluated.to_mesh_clear()
    out.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    generation_binding={
        'qa_fixture_only':c.get('qa_fixture_only',False),
        'generation_receipt':generation_gate.ref(c['generation_receipt']) if c.get('generation_receipt') else None,
        'direction':c.get('direction'),
        'motion_channel':c.get('motion_channel'),
        'config':generation_gate.ref(config_path),
        'skinned_mesh':c['skinned_mesh'],
        'body_coordinate_frame':c['body_coordinate_frame'],
        'scene_unit_scale':scale,
    }
    receipt = {"schema":1, "method":"same_process_render_and_evaluated_vertices", **generation_binding,
        "camera_space":camera_space,"approved_camera":locked_camera,"approved_ground_frame":initial_ground,
        "capture_validator":generation_gate.ref(root_locked_capture.__file__),
        "subject_sha256":c["subject_sha256"], "blend_sha256":blend_hash,
        "generator_sha256":sha(__file__), "frames":renders}
    generation_gate.write(receipt_path,receipt)
    result = {"schema": 1, "method": "Blender_evaluated_depsgraph_vertices", **generation_binding, "subject_sha256": c["subject_sha256"],
        "exporter_sha256": sha(__file__), "config_sha256": sha(config_path), "blend_sha256": blend_hash,
        "render_receipt":{"path":str(receipt_path.relative_to(ROOT)),"sha256":sha(receipt_path)},
        "sole_vertex_ids": sole_ids, "frames": frames}
    if matrix_sequence is not None:
        result["camera_plane_motion"] = {
            "source_pose_matrices": generation_gate.ref(matrix_sequence),
            "source_skin": generation_gate.ref(c["camera_plane_source_skin"]),
            "support_schedule": generation_gate.ref(c["camera_plane_support_schedule"])
                                 if c.get("camera_plane_support_schedule") else None,
            "sole_binding_evidence": generation_gate.ref(c["camera_plane_sole_binding_evidence"])
                                     if c.get("camera_plane_sole_binding_evidence") else None,
            "support_target_clearance_m": c.get("camera_plane_support_target_clearance_m"),
            "global_matrix_tolerance": c.get("camera_plane_global_matrix_tolerance"),
            "projection_materialization_tolerance": c.get("camera_plane_projection_materialization_tolerance"),
            "projection_materialization_records": camera_plane_projection_records,
        }
    generation_gate.write(out,result)
    print("EVALUATED_GEOMETRY_EXPORTED_NOT_VISUAL_PASS", out)


if __name__ == "__main__":
    main()
