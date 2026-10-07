"""Read-only Blender diagnostic matching the E camera-plane exporter context.

It opens a sealed scene, assigns an empty Blender 5 action exactly as the
exporter does, applies one projected pose, and records the matrix deviation.
It never saves, renders, writes source pixels, or creates an animation export.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


def project_path(value):
    candidate = Path(value)
    candidate = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    if candidate == ROOT or not candidate.is_relative_to(ROOT):
        raise ValueError("PROJECT_LOCAL_PATH_REQUIRED")
    return candidate


def sha256(path):
    return hashlib.sha256(project_path(path).read_bytes()).hexdigest()


def main():
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-pose-index", type=int, default=0)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    config_path = project_path(args.config)
    out = project_path(args.out)
    if out.exists():
        raise ValueError("REFUSE_TO_OVERWRITE_DIAGNOSTIC_EVIDENCE")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    matrices = np.load(project_path(config["camera_plane_pose_matrices"]), allow_pickle=False)
    skin = json.loads(project_path(config["camera_plane_source_skin"]).read_text(encoding="utf-8"))
    bones = skin["bone_order"]
    if not 0 <= args.source_pose_index < matrices.shape[0]:
        raise ValueError("SOURCE_POSE_INDEX_OUT_OF_RANGE")
    rig = bpy.data.objects.get(config["camera_plane_rig"])
    camera = bpy.data.objects.get("SourceLockedCamera")
    if rig is None or camera is None or camera.data.type != "ORTHO":
        raise ValueError("EXACT_R7_RIG_AND_CAMERA_REQUIRED")
    normal = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    tolerance = float(config.get("camera_plane_global_matrix_tolerance", 1.0e-6))

    def reset_pose():
        for bone in bones:
            rig.pose.bones[bone["name"]].matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def in_plane(vector):
        return vector - normal * vector.dot(normal)

    def signed_angle(first, second):
        return math.atan2(normal.dot(first.cross(second)), first.dot(second))

    reset_pose()
    rest_matrices = {bone["name"]: Matrix(rig.data.bones[bone["name"]].matrix_local) for bone in bones}
    rest_joints = {
        bone["name"]: {
            "head": Vector(rig.pose.bones[bone["name"]].head),
            "tail": Vector(rig.pose.bones[bone["name"]].tail),
        }
        for bone in bones
    }
    # Match exporter ordering: attach an empty action and set the frame before
    # building the projected target.
    rig.animation_data_create()
    action = bpy.data.actions.new("MICA_E_CAMERA_PLANE_EXPORT_CONTEXT_DIAGNOSTIC")
    rig.animation_data.action = action
    bpy.context.scene.frame_set(1)
    reset_pose()
    for index, bone in enumerate(bones):
        rig.pose.bones[bone["name"]].matrix = Matrix(matrices[args.source_pose_index, index].tolist())
        bpy.context.view_layer.update()
    raw_joints = {
        bone["name"]: {
            "head": Vector(rig.pose.bones[bone["name"]].head),
            "tail": Vector(rig.pose.bones[bone["name"]].tail),
        }
        for bone in bones
    }
    proposed = []
    for bone in bones:
        name = bone["name"]
        rest_vector = in_plane(rest_joints[name]["tail"] - rest_joints[name]["head"])
        target_vector = in_plane(raw_joints[name]["tail"] - raw_joints[name]["head"])
        angle = 0.0 if rest_vector.length < 1e-6 or target_vector.length < 1e-6 else signed_angle(
            rest_vector.normalized(), target_vector.normalized())
        proposed.append(
            Matrix.Translation(raw_joints[name]["head"])
            @ Matrix.Rotation(angle, 4, normal)
            @ Matrix.Translation(-rest_joints[name]["head"])
            @ rest_matrices[name]
        )
    reset_pose()
    for index, bone in enumerate(bones):
        rig.pose.bones[bone["name"]].matrix = proposed[index]
        bpy.context.view_layer.update()
    rows = []
    for index, bone in enumerate(bones):
        actual = rig.pose.bones[bone["name"]].matrix
        error = max(
            abs(float(actual[row][column]) - float(proposed[index][row][column]))
            for row in range(4) for column in range(4)
        )
        rows.append({
            "bone": bone["name"],
            "parent": bone.get("parent"),
            "max_global_matrix_error": error,
            "target_translation": [float(value) for value in proposed[index].translation],
            "actual_translation": [float(value) for value in actual.translation],
        })
    rows.sort(key=lambda item: item["max_global_matrix_error"], reverse=True)
    out.mkdir(parents=True)
    report = {
        "schema": 1,
        "stage": "camera_plane_export_context_diagnostic",
        "production_ready": False,
        "scope": "read_only one-pose exporter-context diagnosis; no save, render, source-art output, or animation export",
        "config": {"path": str(config_path.relative_to(ROOT)), "sha256": sha256(config_path)},
        "blend": {"path": str(project_path(bpy.data.filepath).relative_to(ROOT)), "sha256": sha256(bpy.data.filepath)},
        "source_pose_index": args.source_pose_index,
        "camera": camera.name,
        "rig": rig.name,
        "empty_action_assigned": True,
        "configured_tolerance": tolerance,
        "maximum_global_matrix_error": rows[0]["max_global_matrix_error"],
        "within_configured_tolerance": rows[0]["max_global_matrix_error"] <= tolerance,
        "largest_errors": rows[:12],
    }
    (out / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CAMERA_PLANE_EXPORT_CONTEXT_DIAGNOSED", report["maximum_global_matrix_error"])


if __name__ == "__main__":
    main()
