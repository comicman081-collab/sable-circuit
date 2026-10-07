"""Read-only diagnostic for a camera-plane-constrained MICA E contact pose.

The failed R3 first pose applied the full three-dimensional Tripo bone bases to
an ImageGen-authored, source-preserving surface.  Its right calf was therefore
turned almost edge-on to the fixed review camera.  This diagnostic keeps the
same source image, REST matrices, UVs, weights, camera, and sampled Tripo
screen-space joint locations, but constrains each bone's rotation around the
camera normal.  It produces diagnostic-only evidence; it is not a visible frame
candidate, does not save a Blend, and never modifies an input.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "character_pipeline"))
import generation_harness as g

OUT_NAME = "mica_E_camera_plane_pose_r01"
NEUTRAL = ROOT / "artifacts" / "quarantine" / "generation_diagnostics" / "mica_E_projected_neutral_r02" / "PROJECTED_SOURCE_NEUTRAL.blend"
SKIN = ROOT / "artifacts" / "quarantine" / "generation_diagnostics" / "mica_E_forward_clip_r02" / "SOURCE_SKIN.json"
POSES = ROOT / "artifacts" / "quarantine" / "generation_diagnostics" / "mica_E_native_dense_world_anchor_math_r03" / "PROPOSED_GLOBAL_MATRICES.npy"
ANCHOR = ROOT / "artifacts" / "quarantine" / "generation_diagnostics" / "mica_E_native_dense_world_anchor_math_r03" / "PROBE.json"
FAILED_MAPPING = ROOT / "artifacts" / "tripo_reference_review" / "motion_r13" / "FIRST_POSE_R3_CALF_PIXEL_MAPPING.json"
SAMPLE = 46


def ref(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def run_child(out):
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    import source_surface_sampling as sampling

    bpy.ops.wm.open_mainfile(filepath=str(NEUTRAL), load_ui=False)
    skin = json.loads(SKIN.read_text(encoding="utf-8"))
    raw_poses = np.load(POSES, allow_pickle=False)
    anchor = json.loads(ANCHOR.read_text(encoding="utf-8"))
    prior = g.read(g.resolve(anchor["inputs"]["prior"]))
    mapping = json.loads(FAILED_MAPPING.read_text(encoding="utf-8"))
    rows = skin["bone_order"]
    rig = bpy.data.objects.get("CHR_PROTO_03_SourceRig")
    mesh = bpy.data.objects.get("CHR_PROTO_03_SourceSurface_E")
    cameras = [item for item in bpy.data.objects if item.type == "CAMERA"]
    if rig is None or mesh is None or len(cameras) != 1:
        raise ValueError("EXPECTED_SOURCE_RIG_SURFACE_AND_ONE_CAMERA_REQUIRED")
    if raw_poses.shape != (97, len(rows), 4, 4):
        raise ValueError("EXACT_R03_DENSE_POSE_SHAPE_REQUIRED")
    camera = cameras[0]
    if camera.data.type != "ORTHO":
        raise ValueError("FIXED_ORTHOGRAPHIC_REVIEW_CAMERA_REQUIRED")
    if mesh.matrix_world != Matrix.Identity(4) or rig.matrix_world != Matrix.Identity(4):
        raise ValueError("UNTRANSFORMED_SOURCE_BINDING_REQUIRED")

    def reset():
        for row in rows:
            rig.pose.bones[row["name"]].matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def digest_chunks(chunks):
        digest = hashlib.sha256()
        for chunk in chunks:
            digest.update(chunk)
        return digest.hexdigest()

    def surface_integrity():
        active_uv = mesh.data.uv_layers.active
        if active_uv is None:
            raise ValueError("ACTUAL_SOURCE_SURFACE_UV_REQUIRED")
        rest_values = np.asarray([np.asarray(rig.data.bones[row["name"]].matrix_local, dtype="<f8")
                                  for row in rows], dtype="<f8")
        uv_values = np.asarray([tuple(loop.uv) for loop in active_uv.data], dtype="<f8")
        topology = []
        for polygon in mesh.data.polygons:
            topology.extend([polygon.index, len(polygon.vertices), *polygon.vertices])
        weights = []
        for vertex in mesh.data.vertices:
            for item in sorted(vertex.groups, key=lambda group: group.group):
                weights.extend([vertex.index, item.group, item.weight])
        textures = []
        for material in mesh.data.materials:
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        textures.append(str(Path(bpy.path.abspath(node.image.filepath)).resolve()))
        if len(textures) != 1:
            raise ValueError("EXACT_ONE_SOURCE_TEXTURE_REQUIRED")
        return {
            "rest_matrices_sha256": hashlib.sha256(rest_values.tobytes()).hexdigest(),
            "uv_loop_values_sha256": hashlib.sha256(uv_values.tobytes()).hexdigest(),
            "topology_sha256": digest_chunks([json.dumps(topology, separators=(",", ":")).encode("utf-8")]),
            "vertex_group_weights_sha256": digest_chunks([json.dumps(weights, separators=(",", ":")).encode("utf-8")]),
            "source_texture": ref(Path(textures[0])),
        }

    # Capture the exact original R3 projection targets before the constrained
    # solve.  These are motion-guide coordinates, never a source-art render.
    reset()
    for index, row in enumerate(rows):
        rig.pose.bones[row["name"]].matrix = Matrix(raw_poses[SAMPLE, index].tolist())
        bpy.context.view_layer.update()
    raw_joints = {
        row["name"]: {
            "head": Vector(rig.pose.bones[row["name"]].head),
            "tail": Vector(rig.pose.bones[row["name"]].tail),
        }
        for row in rows
    }
    reset()
    rest_matrices = {row["name"]: Matrix(rig.data.bones[row["name"]].matrix_local)
                     for row in rows}
    rest_joints = {
        row["name"]: {
            "head": Vector(rig.pose.bones[row["name"]].head),
            "tail": Vector(rig.pose.bones[row["name"]].tail),
        }
        for row in rows
    }
    integrity_before = surface_integrity()

    def evaluated_positions():
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        evaluated_mesh = evaluated.to_mesh()
        try:
            return np.asarray([tuple(vertex.co) for vertex in evaluated_mesh.vertices], dtype=float)
        finally:
            evaluated.to_mesh_clear()

    neutral_actual = evaluated_positions()
    sole_bindings = prior["visible_sole_bindings"]
    floor = min(float(sampling.sample_positions(neutral_actual, binding)[:, 2].min())
                for binding in sole_bindings.values())

    # An orthographic camera has parallel rays.  The action's original
    # three-dimensional *translations* retain measured sole height and contact;
    # only bone rotation is constrained about this camera normal so the planar
    # source surface cannot turn edge-on.
    normal = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()

    def in_plane(vector):
        return vector - normal * vector.dot(normal)

    def signed_angle(first, second):
        return math.atan2(normal.dot(first.cross(second)), first.dot(second))

    proposed = []
    fallback_by_name = {}
    for index, row in enumerate(rows):
        name = row["name"]
        rest_head = rest_joints[name]["head"]
        rest_vector = in_plane(rest_joints[name]["tail"] - rest_head)
        target_head = raw_joints[name]["head"]
        target_vector = in_plane(raw_joints[name]["tail"] - raw_joints[name]["head"])
        if rest_vector.length < 1e-6 or target_vector.length < 1e-6:
            angle = 0.0
            fallback = True
        else:
            angle = signed_angle(rest_vector.normalized(), target_vector.normalized())
            fallback = False
        transform = (Matrix.Translation(target_head)
                     @ Matrix.Rotation(angle, 4, normal)
                     @ Matrix.Translation(-rest_head)
                     @ rest_matrices[name])
        proposed.append(transform)
        fallback_by_name[name] = fallback

    # Parent-to-child writes are required by Blender's PoseBone.matrix
    # semantics.  Each matrix is world-space and preserves the fixed camera
    # normal; no source image, UV, REST matrix, or vertex group is changed.
    def apply(matrices):
        reset()
        for index, row in enumerate(rows):
            parent = int(row["parent"])
            if parent >= index or parent < -1:
                raise ValueError("PARENT_BEFORE_CHILD_SOURCE_BONE_ORDER_REQUIRED")
            rig.pose.bones[row["name"]].matrix = matrices[index]
            bpy.context.view_layer.update()

    from bpy_extras.object_utils import world_to_camera_view

    scene = bpy.context.scene
    if (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) != (1920, 1920, 100):
        raise ValueError("EXACT_NATIVE_1920_REVIEW_CAPTURE_REQUIRED")

    def pixels(world):
        point = world_to_camera_view(scene, camera, world)
        return np.array([point.x * 1920.0, (1.0 - point.y) * 1920.0], dtype=float)

    apply(proposed)
    initial_actual = evaluated_positions()
    initial_clearances = {
        side: float(sampling.sample_positions(initial_actual, binding)[:, 2].min() - floor)
        for side, binding in sole_bindings.items()
    }
    contact_row = next(row for row in prior["samples"] if row.get("sample") == 23)
    contact_target = float(contact_row["feet"]["l"]["desired_clearance_m"])
    if not 0.0 <= contact_target <= 0.004:
        raise ValueError("REVIEWED_R03_CONTACT_TARGET_REQUIRED")
    lower_names = {"calf_l", "foot_l", "ball_l"}
    lower_indices = {index for index, row in enumerate(rows) if row["name"] in lower_names}
    skin_weights = np.asarray(skin["weights"], dtype=float).reshape(-1, 4)
    skin_indices = np.asarray(skin["bones"], dtype=int).reshape(-1, 4)
    contact_binding = sole_bindings["l"]
    contact_vertices = np.asarray(contact_binding["vertices"], dtype=int)
    contact_barycentric = np.asarray(contact_binding["barycentric"], dtype=float)
    per_vertex_lower_influence = (skin_weights[contact_vertices]
                                  * np.isin(skin_indices[contact_vertices], list(lower_indices))).sum(axis=2)
    point_lower_influence = (per_vertex_lower_influence * contact_barycentric).sum(axis=1)
    initial_contact_positions = sampling.sample_positions(initial_actual, contact_binding)
    lowest_contact_index = int(np.argmin(initial_contact_positions[:, 2]))
    influence = float(point_lower_influence[lowest_contact_index])
    if influence < 0.95:
        raise ValueError("SUPPORT_SOLE_NOT_OWNED_BY_LOWER_LEFT_LEG_BONES")
    support_delta_z = (contact_target - initial_clearances["l"]) / influence
    if abs(normal.z) < 1e-6:
        raise ValueError("CAMERA_NORMAL_MUST_AFFECT_FIXED_GROUND_AXIS")
    support_delta_along_camera_normal = support_delta_z / normal.z
    # Correct the support chain along the orthographic camera ray.  That brings
    # the evaluated sole to the independently fixed world floor without moving
    # a rendered joint even one pixel or correcting the actor root.
    correction = Matrix.Translation(normal * support_delta_along_camera_normal)
    corrected = [correction @ matrix
                 if index in lower_indices else matrix
                 for index, matrix in enumerate(proposed)]
    apply(corrected)
    actual = evaluated_positions()
    integrity_after = surface_integrity()
    if integrity_before != integrity_after:
        raise ValueError("SOURCE_SURFACE_INTEGRITY_CHANGED_DURING_DIAGNOSTIC")
    sole_clearances = {
        side: float(sampling.sample_positions(actual, binding)[:, 2].min() - floor)
        for side, binding in sole_bindings.items()
    }
    if abs(sole_clearances["l"] - contact_target) > 5e-5:
        raise ValueError("CAMERA_PLANE_CONTACT_CORRECTION_DID_NOT_REACH_FIXED_TARGET")

    # Rebind the exact source pixel witnesses from the independent failure
    # evidence to actual source-surface triangles.  Alpha was established by
    # the original receipt; the opaque array prevents image decoder choices in
    # this diagnostic from changing which previously reviewed source points are
    # measured.
    source_path = ROOT / mapping["source_rgba"]["path"]
    source_image = bpy.data.images.load(str(source_path), check_existing=False)
    source_w, source_h = source_image.size[:]
    bpy.data.images.remove(source_image)
    if (source_w, source_h) != (1024, 1536):
        raise ValueError("EXACT_CURRENT_E_RGBA_NATIVE_DIMENSIONS_REQUIRED")
    alpha = np.full((source_h, source_w, 4), 255, dtype=np.uint8)
    witness_rows = []
    for cross in mapping["calf_r_cross_sections"]:
        binding = sampling.bind_pixels(skin, alpha, cross["source_pixels"])
        world = sampling.sample_positions(actual, binding)
        projected = [pixels(Vector(value)).tolist() for value in world]
        width = float(np.linalg.norm(np.asarray(projected[1]) - np.asarray(projected[0])))
        witness_rows.append({
            "source_y_px": cross["source_y_px"],
            "source_pixels": cross["source_pixels"],
            "source_triangle_vertices": binding["vertices"],
            "source_barycentric": binding["barycentric"],
            "source_cross_section_width_px": cross["source_cross_section_width_px"],
            "camera_plane_render_points_px": projected,
            "camera_plane_cross_section_distance_px": width,
            "retained_width_ratio": width / float(cross["source_cross_section_width_px"]),
        })

    bone_rows = []
    for index, row in enumerate(rows):
        name = row["name"]
        output = rig.pose.bones[name]
        expected_head = pixels(raw_joints[name]["head"])
        actual_head = pixels(output.head)
        raw_vector = in_plane(raw_joints[name]["tail"] - raw_joints[name]["head"])
        rendered_vector = in_plane(output.tail - output.head)
        bone_rows.append({
            "name": name,
            "fallback_rotation": fallback_by_name[name],
            "screen_head_error_px": float(np.linalg.norm(actual_head - expected_head)),
            "rotation_has_camera_normal_component": float((output.matrix.to_3x3() @ normal).dot(normal)),
            "projected_raw_tail_direction": (pixels(raw_joints[name]["tail"]) - pixels(raw_joints[name]["head"])).tolist(),
            "projected_output_tail_direction": (pixels(output.tail) - pixels(output.head)).tolist(),
        })

    image = out / "CAMERA_PLANE_CONTACT_L_DIAGNOSTIC_1920.png"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    scene.render.filepath = str(image)
    bpy.ops.render.render(write_still=True)
    if not image.is_file():
        raise ValueError("DIAGNOSTIC_RENDER_NOT_WRITTEN")
    report = {
        "schema": 1,
        "scope": "read-only R3 E contact mechanism diagnostic only; never a visible frame or runtime asset",
        "production_ready": False,
        "sample": SAMPLE,
        "inputs": {
            "neutral": ref(NEUTRAL),
            "source_skin": ref(SKIN),
            "r03_native_pose_matrices": ref(POSES),
            "r03_anchor": ref(ANCHOR),
            "independent_r3_failure_mapping": ref(FAILED_MAPPING),
        },
        "operation": "camera-plane-constrained pose transfer; source image, REST matrices, UVs, vertex weights, mesh topology and original action screen-space heads remain unchanged",
        "source_surface_integrity_before": integrity_before,
        "source_surface_integrity_after": integrity_after,
        "source_surface_integrity_unchanged": True,
        "camera": {"name": camera.name, "type": camera.data.type, "normal": list(normal)},
        "screen_head_max_error_px": max(row["screen_head_error_px"] for row in bone_rows),
        "fixed_neutral_floor_m": floor,
        "r03_left_contact_clearance_target_m": contact_target,
        "camera_plane_before_local_support_correction_m": initial_clearances,
        "camera_plane_local_support_bones": sorted(lower_names),
        "camera_plane_local_support_influence": influence,
        "camera_plane_local_support_delta_z_m": support_delta_z,
        "camera_plane_local_support_delta_along_camera_normal_m": support_delta_along_camera_normal,
        "actual_visible_sole_clearance_m": sole_clearances,
        "calf_r_cross_sections": witness_rows,
        "calf_r_min_retained_width_ratio": min(row["retained_width_ratio"] for row in witness_rows),
        "bones": bone_rows,
        "diagnostic_render": ref(image),
        "requires": ["independent visual review", "new adapter/build-plan review", "fresh one-output build permit before any candidate"],
    }
    g.write(out / "CAMERA_PLANE_POSE_REPORT.json", report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--inside", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    out = Path(args.out).resolve()
    quarantine = (ROOT / "artifacts" / "quarantine" / "generation_diagnostics").resolve()
    if not out.is_relative_to(quarantine):
        raise ValueError("DIAGNOSTIC_QUARANTINE_ONLY")
    if args.inside:
        run_child(out)
        return
    if out.exists():
        raise ValueError("FRESH_DIAGNOSTIC_OUTPUT_REQUIRED")
    out.mkdir(parents=True)
    cache = out / "cache"
    cache.mkdir()
    env = os.environ.copy()
    for key in ("TEMP", "TMP", "TMPDIR", "APPDATA", "LOCALAPPDATA", "XDG_CACHE_HOME", "XDG_DATA_HOME", "BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "PYTHONPYCACHEPREFIX"):
        env[key] = str(cache)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "2"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [str(ROOT / "tools" / "blender" / "5.2.1" / "blender.exe"), "--background", "--factory-startup", "--disable-autoexec", "--offline-mode", "--threads", "2", "--python-exit-code", "2", "--python", __file__, "--", "--inside", "--out", str(out)]
    with (out / "blender.log").open("w", encoding="utf-8") as log:
        child = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=120,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if child.returncode:
        raise ValueError("CAMERA_PLANE_DIAGNOSTIC_FAILED:" + str(out / "blender.log"))
    g.write(out / "COMPLETION.json", {
        "schema": 1,
        "owned_child_exited": True,
        "production_ready": False,
        "report": ref(out / "CAMERA_PLANE_POSE_REPORT.json"),
        "diagnostic_render": ref(out / "CAMERA_PLANE_CONTACT_L_DIAGNOSTIC_1920.png"),
        "note": "No Blend was saved and no production pointer was changed.",
    })


if __name__ == "__main__":
    main()
