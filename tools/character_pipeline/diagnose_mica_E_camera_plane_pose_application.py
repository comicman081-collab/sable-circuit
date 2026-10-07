"""Read-only Blender diagnostic for camera-plane global pose application."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def _path(value):
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    if path == ROOT or not path.is_relative_to(ROOT):
        raise ValueError("PROJECT_LOCAL_PATH_REQUIRED")
    return path


def _sha(path):
    return hashlib.sha256(_path(path).read_bytes()).hexdigest()


def main():
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-pose-index", type=int, default=0)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    config_path = _path(args.config)
    out = _path(args.out)
    if out.exists():
        raise ValueError("REFUSE_TO_OVERWRITE_DIAGNOSTIC_EVIDENCE")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    matrices = np.load(_path(config["camera_plane_pose_matrices"]), allow_pickle=False)
    skin = json.loads(_path(config["camera_plane_source_skin"]).read_text(encoding="utf-8"))
    bones = skin["bone_order"]
    if not 0 <= args.source_pose_index < matrices.shape[0]:
        raise ValueError("SOURCE_POSE_INDEX_OUT_OF_RANGE")
    rig = bpy.data.objects.get(config["camera_plane_rig"])
    camera = bpy.data.objects.get("SourceLockedCamera")
    if rig is None or camera is None or camera.data.type != "ORTHO":
        raise ValueError("EXACT_R7_RIG_AND_CAMERA_REQUIRED")
    normal = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()

    def reset():
        for row in bones:
            rig.pose.bones[row["name"]].matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def in_plane(vector):
        return vector - normal * vector.dot(normal)

    def signed_angle(first, second):
        return math.atan2(normal.dot(first.cross(second)), first.dot(second))

    reset()
    rest_matrices = {row["name"]: Matrix(rig.data.bones[row["name"]].matrix_local) for row in bones}
    rest_joints = {row["name"]: {"head": Vector(rig.pose.bones[row["name"]].head),
                                 "tail": Vector(rig.pose.bones[row["name"]].tail)} for row in bones}
    for index, row in enumerate(bones):
        rig.pose.bones[row["name"]].matrix = Matrix(matrices[args.source_pose_index, index].tolist())
        bpy.context.view_layer.update()
    raw_joints = {row["name"]: {"head": Vector(rig.pose.bones[row["name"]].head),
                                "tail": Vector(rig.pose.bones[row["name"]].tail)} for row in bones}
    proposed = []
    for row in bones:
        name = row["name"]
        rest_vector = in_plane(rest_joints[name]["tail"] - rest_joints[name]["head"])
        target_vector = in_plane(raw_joints[name]["tail"] - raw_joints[name]["head"])
        angle = 0.0 if rest_vector.length < 1e-6 or target_vector.length < 1e-6 else signed_angle(rest_vector.normalized(), target_vector.normalized())
        proposed.append(Matrix.Translation(raw_joints[name]["head"])
                        @ Matrix.Rotation(angle, 4, normal)
                        @ Matrix.Translation(-rest_joints[name]["head"])
                        @ rest_matrices[name])
    reset()
    for index, row in enumerate(bones):
        rig.pose.bones[row["name"]].matrix = proposed[index]
        bpy.context.view_layer.update()
    rows = []
    for index, row in enumerate(bones):
        actual = rig.pose.bones[row["name"]].matrix
        difference = max(abs(float(actual[i][j]) - float(proposed[index][i][j])) for i in range(4) for j in range(4))
        rows.append({"bone": row["name"], "parent": row.get("parent"), "max_global_matrix_error": difference,
                     "target_translation": [float(v) for v in proposed[index].translation],
                     "actual_translation": [float(v) for v in actual.translation]})
    rows.sort(key=lambda row: row["max_global_matrix_error"], reverse=True)
    out.mkdir(parents=True)
    report = {"schema": 1, "stage": "camera_plane_pose_application_diagnostic", "production_ready": False,
              "scope": "read_only single-pose matrix-application diagnosis; no render or source-art output",
              "config": {"path": str(config_path.relative_to(ROOT)), "sha256": _sha(config_path)},
              "blend": {"path": str(_path(bpy.data.filepath).relative_to(ROOT)), "sha256": _sha(bpy.data.filepath)},
              "source_pose_index": args.source_pose_index,
              "camera": camera.name, "rig": rig.name,
              "maximum_global_matrix_error": rows[0]["max_global_matrix_error"],
              "largest_errors": rows[:12]}
    (out / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CAMERA_PLANE_POSE_APPLICATION_DIAGNOSED", report["maximum_global_matrix_error"])


if __name__ == "__main__":
    main()
