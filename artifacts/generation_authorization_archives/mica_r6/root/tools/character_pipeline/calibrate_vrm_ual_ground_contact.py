"""Calibrate one Blender+UAL pose-guide cycle against an independent fixed floor.

The floor is sampled once from actual sole vertices in the licensed target
model's neutral REST pose, before UAL action evaluation.  The action is then
sampled without per-frame root correction.  This tool is diagnostic only:
Blender/VRM pixels can guide pose geometry but can never become visible MICA
art, a runtime atlas, or an HTML asset.
"""
import argparse
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g

CONTRACT = ROOT / "tools/character_pipeline/pose_guide_contact_contract.json"


def _vec(value):
    return [float(value.x), float(value.y), float(value.z)]


def _sample_sole(mesh_object, sole_ids, depsgraph):
    evaluated = mesh_object.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return {
            side: [_vec(evaluated.matrix_world @ mesh.vertices[index].co) for index in ids]
            for side, ids in sole_ids.items()
        }
    finally:
        evaluated.to_mesh_clear()


def _centre(points):
    return [sum(p[axis] for p in points) / len(points) for axis in range(3)]


def _dot(point, axis):
    return sum(point[index] * axis[index] for index in range(3))


def _angle_degrees(vector, axis):
    vector = [float(vector[0]), float(vector[1]), 0.0]
    axis = [float(axis[0]), float(axis[1]), 0.0]
    vl = math.sqrt(_dot(vector, vector))
    al = math.sqrt(_dot(axis, axis))
    if vl <= 1e-9 or al <= 1e-9:
        return 180.0
    cosine = max(-1.0, min(1.0, _dot(vector, axis) / (vl * al)))
    angle = math.degrees(math.acos(cosine))
    # Bone head/tail conventions may reverse the longitudinal foot axis.  The
    # failure of interest is sideways yaw, so compare the undirected axis.
    return min(angle, 180.0 - angle)


def _bone_head_world(rig, bone_name):
    return _vec(rig.matrix_world @ rig.pose.bones[bone_name].head)


def _mapped_target(result, source_name):
    matches = [target for target, source in result["mapping"].items() if source == source_name]
    if len(matches) != 1:
        raise ValueError("EXACT_TARGET_BONE_MAPPING_REQUIRED:" + source_name)
    return matches[0]


def _classify(rows, contract):
    errors = []
    contact_max = float(contract["contact_clearance_max_m"])
    flight_min = float(contract["flight_clearance_min_m"])
    minimum_support = int(contract["minimum_support_samples"])
    penetration_max = float(contract["ground_penetration_max_m"])
    yaw_max = float(contract["maximum_foot_yaw_from_travel_degrees"])
    unique = rows[:-1]
    if not unique or rows[0]["sole_vertices_world_m"] != rows[-1]["sole_vertices_world_m"]:
        errors.append("EXACT_WRAP_SAMPLE_REQUIRED")

    support_windows = {}
    contact_indices = {}
    phase_candidates = {}
    count = len(unique)
    for side in ("left", "right"):
        if min(row["sole_clearance_m"][side] for row in unique) < -penetration_max:
            errors.append("FIXED_FLOOR_PENETRATION_" + side.upper())
        if max(row["foot_yaw_from_travel_degrees"][side] for row in unique) > yaw_max:
            errors.append("FOOT_YAW_EXCEEDS_TRAVEL_CONTRACT_" + side.upper())
        expected_sign = 1.0 if side == "left" else -1.0
        entries = []
        for index, row in enumerate(unique):
            previous = unique[(index - 1) % count]
            if (
                previous["sole_clearance_m"][side] > contact_max
                and row["sole_clearance_m"][side] <= contact_max
                and row["sole_clearance_m"][side] < previous["sole_clearance_m"][side]
                and row["left_minus_right_travel_m"] * expected_sign > 0.0
            ):
                entries.append(index)
        if len(entries) != 1:
            errors.append("ONE_DESCENDING_FIXED_FLOOR_CONTACT_REQUIRED_" + side.upper())
            low_leading = [
                index for index, row in enumerate(unique)
                if row["sole_clearance_m"][side] <= contact_max
                and row["left_minus_right_travel_m"] * expected_sign > 0.0
            ]
            if not low_leading:
                errors.append("INSUFFICIENT_FIXED_FLOOR_SUPPORT_WINDOW_" + side.upper())
                continue
            contact_index = min(low_leading, key=lambda index: unique[index]["sole_clearance_m"][side])
        else:
            contact_index = entries[0]
        contact_indices[side] = contact_index
        window = []
        cursor = contact_index
        while len(window) < count and unique[cursor]["sole_clearance_m"][side] <= contact_max:
            window.append(cursor)
            cursor = (cursor + 1) % count
        support_windows[side] = window
        if len(window) < minimum_support:
            errors.append("INSUFFICIENT_FIXED_FLOOR_SUPPORT_WINDOW_" + side.upper())
        label = "l" if side == "left" else "r"
        phase_candidates["contact_" + label] = unique[contact_index]["sample"]
        passing_position = None
        for position in range(1, len(window)):
            previous_delta = unique[window[position - 1]]["left_minus_right_travel_m"] * expected_sign
            current_delta = unique[window[position]]["left_minus_right_travel_m"] * expected_sign
            if previous_delta > 0.0 and current_delta <= 0.0:
                passing_position = position
                break
        if passing_position is None:
            errors.append("SUPPORT_MUST_PERSIST_THROUGH_TRUE_PASSING_" + side.upper())
            continue
        passing_pair = [window[passing_position - 1], window[passing_position]]
        passing_index = min(
            passing_pair,
            key=lambda index: abs(unique[index]["left_minus_right_travel_m"]),
        )
        down_candidates = window[1:passing_position]
        if not down_candidates:
            errors.append("DISTINCT_CONTACT_DOWN_PASSING_REQUIRED_" + side.upper())
            continue
        down_index = min(down_candidates, key=lambda index: unique[index]["pelvis_world_m"][2])
        phase_candidates["down_" + label] = unique[down_index]["sample"]
        phase_candidates["passing_" + label] = unique[passing_index]["sample"]
        if len({contact_index, down_index, passing_index}) != 3:
            errors.append("DISTINCT_CONTACT_DOWN_PASSING_REQUIRED_" + side.upper())

    if set(contact_indices) == {"left", "right"}:
        for phase, start_side, end_side, leading_sign in (
            ("flight_l", "left", "right", -1.0),
            ("flight_r", "right", "left", 1.0),
        ):
            indices = []
            cursor = (contact_indices[start_side] + 1) % count
            while cursor != contact_indices[end_side]:
                indices.append(cursor)
                cursor = (cursor + 1) % count
            candidates = [
                index for index in indices
                if min(unique[index]["sole_clearance_m"].values()) >= flight_min
                and unique[index]["left_minus_right_travel_m"] * leading_sign > 0.0
            ]
            if not candidates:
                errors.append("DISTINCT_BILATERAL_FLIGHT_WINDOW_REQUIRED_" + phase.upper())
            else:
                selected = max(
                    candidates,
                    key=lambda index: min(unique[index]["sole_clearance_m"].values()),
                )
                phase_candidates[phase] = unique[selected]["sample"]

    if len(set(phase_candidates.values())) != len(phase_candidates):
        errors.append("ONE_CAPTURE_SAMPLE_MAY_NOT_FILL_MULTIPLE_PHASES")
    expected_order = [
        "contact_l", "down_l", "passing_l", "flight_l",
        "contact_r", "down_r", "passing_r", "flight_r",
    ]
    if set(phase_candidates) == set(expected_order):
        observed = [name for name, _ in sorted(phase_candidates.items(), key=lambda item: item[1])]
        rotations = [expected_order[index:] + expected_order[:index] for index in range(len(expected_order))]
        if observed not in rotations:
            errors.append("CYCLIC_GAIT_PHASE_ORDER_INVALID")
    else:
        errors.append("COMPLETE_EIGHT_PHASE_CANDIDATE_SET_REQUIRED")
    return phase_candidates, errors


def blender_pass(args):
    import bpy
    from mathutils import Vector

    result = g.read(args.result)
    blend = g.resolve(result["output_blend"])
    contract = g.read(CONTRACT)
    out = g.local(args.out)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene = bpy.context.scene
    sole_mesh = bpy.data.objects[result["sole_mesh"]]
    sole_ids = result["sole_vertex_ids"]
    if set(sole_ids) != {"left", "right"} or not all(sole_ids.values()):
        raise ValueError("DISTINCT_ACTUAL_SOLE_VERTEX_IDS_REQUIRED")

    target_bones = set(result["mapping"])
    def has_target_bones(armature):
        return target_bones.issubset({bone.name for bone in armature.data.bones})
    modifier_rigs = [
        mod.object for mod in sole_mesh.modifiers
        if mod.type == "ARMATURE" and mod.object is not None
        and has_target_bones(mod.object)
    ]
    named_rig = bpy.data.objects.get("SeedSan_Licensed_Target_Rig")
    named = [named_rig] if (
        named_rig is not None and named_rig.type == "ARMATURE"
        and has_target_bones(named_rig)
    ) else []
    parent = [sole_mesh.parent] if (
        sole_mesh.parent is not None and sole_mesh.parent.type == "ARMATURE"
        and has_target_bones(sole_mesh.parent)
    ) else []
    rigs = list(dict.fromkeys(modifier_rigs + named + parent))
    if len(rigs) != 1:
        names = [ob.name for ob in rigs]
        raise ValueError("ONE_SKIN_MODIFIER_BOUND_TARGET_ARMATURE_REQUIRED:" + repr(names))
    rig = rigs[0]
    required_groups = {_mapped_target(result, "foot_l"), _mapped_target(result, "foot_r")}
    if not required_groups.issubset({group.name for group in sole_mesh.vertex_groups}):
        raise ValueError("SOLE_MESH_FOOT_VERTEX_GROUP_BINDING_REQUIRED")

    start, end = [float(value) for value in result["baked_frame_range"]]
    sample_count = int(contract["sample_count_including_wrap"])
    if sample_count < 9 or sample_count > 49:
        raise ValueError("BOUNDED_SAMPLE_COUNT_REQUIRED")
    frame_values = [start + (end - start) * index / (sample_count - 1) for index in range(sample_count)]

    # Fixed floor authority: actual neutral REST-pose sole geometry.  UAL action
    # data is not evaluated until after this immutable reference is recorded.
    prior_pose_position = rig.data.pose_position
    rig.data.pose_position = "REST"
    scene.frame_set(int(start), subframe=start - int(start))
    bpy.context.view_layer.update()
    neutral_vertices = _sample_sole(sole_mesh, sole_ids, bpy.context.evaluated_depsgraph_get())
    neutral_min = {side: min(point[2] for point in points) for side, points in neutral_vertices.items()}
    prior_floor = None
    motion_repair = result.get("motion_repair")
    if isinstance(motion_repair, dict) and isinstance(motion_repair.get("input_calibration"), dict):
        prior_floor = g.read(g.resolve(motion_repair["input_calibration"]))
        if prior_floor.get("fixed_floor", {}).get("method") != "actual_neutral_REST_pose_sole_vertex_minimum_before_UAL_evaluation":
            raise ValueError("IMMUTABLE_PRE_REPAIR_FIXED_FLOOR_REQUIRED")
        floor_z = float(prior_floor["fixed_floor"]["world_z_m"])
    else:
        floor_z = min(neutral_min.values())
    neutral_side_delta = abs(neutral_min["left"] - neutral_min["right"])

    rig.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    camera_right = scene.camera.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    travel_axis = _vec(camera_right.normalized())
    bone_names = {
        "pelvis": _mapped_target(result, "pelvis"),
        "left_hip": _mapped_target(result, "thigh_l"),
        "left_knee": _mapped_target(result, "calf_l"),
        "left_ankle": _mapped_target(result, "foot_l"),
        "left_toe": _mapped_target(result, "ball_l"),
        "right_hip": _mapped_target(result, "thigh_r"),
        "right_knee": _mapped_target(result, "calf_r"),
        "right_ankle": _mapped_target(result, "foot_r"),
        "right_toe": _mapped_target(result, "ball_r"),
    }

    rows = []
    for index, frame in enumerate(frame_values):
        scene.frame_set(int(frame), subframe=frame - int(frame))
        bpy.context.view_layer.update()
        vertices = _sample_sole(sole_mesh, sole_ids, bpy.context.evaluated_depsgraph_get())
        centres = {side: _centre(points) for side, points in vertices.items()}
        clearance = {side: min(point[2] for point in vertices[side]) - floor_z for side in ("left", "right")}
        joint_heads = {name: _bone_head_world(rig, bone) for name, bone in bone_names.items()}
        foot_yaw = {}
        for side in ("left", "right"):
            ankle = joint_heads[side + "_ankle"]
            toe = joint_heads[side + "_toe"]
            foot_yaw[side] = _angle_degrees(
                [toe[axis] - ankle[axis] for axis in range(3)], travel_axis
            )
        rows.append({
            "sample": index,
            "frame": frame,
            "time_s": (frame - start) / float(scene.render.fps),
            "sole_vertices_world_m": vertices,
            "sole_centres_world_m": centres,
            "sole_clearance_m": clearance,
            "left_minus_right_travel_m": _dot(centres["left"], travel_axis) - _dot(centres["right"], travel_axis),
            "pelvis_world_m": joint_heads["pelvis"],
            "joint_heads_world_m": joint_heads,
            "foot_yaw_from_travel_degrees": foot_yaw,
        })

    phase_candidates, errors = _classify(rows, contract)
    if neutral_side_delta > float(contract["neutral_sole_side_delta_max_m"]):
        errors.append("NEUTRAL_REST_SOLES_DO_NOT_DEFINE_ONE_LEVEL_FLOOR")
    report = {
        "schema": 1,
        "scope": "ONE_LICENSED_VRM_UAL_POSE_GUIDE_CONTACT_CALIBRATION",
        "production_ready": False,
        "visible_art_authority": "built_in_ImageGen_only",
        "blender_ual_role": "pose_geometry_guide_only",
        "status": "HOLD" if errors else "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY",
        "errors": errors,
        "input_result": g.ref(args.result),
        "input_blend": result["output_blend"],
        "contract": g.ref(CONTRACT),
        "generator": g.ref(__file__),
        "sole_mesh": sole_mesh.name,
        "sole_vertex_ids": sole_ids,
        "fixed_floor": {
            "method": "actual_neutral_REST_pose_sole_vertex_minimum_before_UAL_evaluation",
            "world_z_m": floor_z,
            "authority_chain": (
                motion_repair.get("input_calibration") if prior_floor is not None else None
            ),
            "neutral_side_min_z_m": neutral_min,
            "neutral_side_delta_m": neutral_side_delta,
            "neutral_sole_vertices_world_m": neutral_vertices,
        },
        "travel_axis_world": travel_axis,
        "sample_count_including_wrap": sample_count,
        "phase_candidates": phase_candidates,
        "samples": rows,
        "limitations": [
            "Technical candidate selection is not visual phase approval.",
            "No per-frame root correction, MICA art generation, atlas packaging, runtime promotion, or Luna test occurs here.",
            "Any HOLD blocks using contact/down/passing candidates in ImageGen requests.",
        ],
    }
    g.write(out / "contact_calibration.json", report)
    rig.data.pose_position = prior_pose_position
    print(str(out / "contact_calibration.json"))


def main(args):
    result = g.read(args.result)
    g.resolve(result["output_blend"])
    out = g.local(args.out)
    if not out.is_relative_to(ROOT / "artifacts/quarantine/generation_diagnostics"):
        raise ValueError("POSE_GUIDE_DIAGNOSTIC_OUTPUT_REQUIRED")
    out.mkdir(parents=True, exist_ok=False)
    cache = out / "cache"
    cache.mkdir()
    env = os.environ.copy()
    for key in (
        "TEMP", "TMP", "TMPDIR", "APPDATA", "LOCALAPPDATA", "XDG_CACHE_HOME",
        "XDG_DATA_HOME", "BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "PYTHONPYCACHEPREFIX",
    ):
        env[key] = str(cache)
    env["OMP_NUM_THREADS"] = "2"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [
        str(ROOT / "tools/blender/5.2.1/blender.exe"), "--background", "--factory-startup",
        "--disable-autoexec", "--offline-mode", "--threads", "2", "--python-exit-code", "2",
        "--python", str(Path(__file__).resolve()), "--", "--result", str(g.local(args.result)),
        "--out", str(out), "--blender-pass",
    ]
    with (out / "blender.log").open("w", encoding="utf-8") as log:
        child = subprocess.run(
            command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    if child.returncode:
        raise ValueError("CONTACT_CALIBRATION_CHILD_FAILED:" + str(out / "blender.log"))
    report = g.read(out / "contact_calibration.json")
    g.resolve(report["input_blend"])
    g.write(out / "completion.json", {
        "status": report["status"],
        "calibration": g.ref(out / "contact_calibration.json"),
        "owned_child_exited": True,
        "production_ready": False,
    })
    print(str(out / "completion.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--blender-pass", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parsed = parser.parse_args(argv)
    if parsed.blender_pass:
        blender_pass(parsed)
    else:
        main(parsed)
