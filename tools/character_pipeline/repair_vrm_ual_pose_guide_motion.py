"""Repair only Blender+UAL pose-guide motion; never author visible SABLE art.

The exact licensed VRM/UAL diagnostic is copied to a fresh project-local blend.
One constant armature-height calibration prevents floor penetration, and the
actual evaluated foot longitudinal axes are corrected around world-up at each
source frame.  No per-frame root translation, mesh/material editing, ImageGen
pixel editing, atlas packaging, or runtime promotion is performed.
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


def _mapped_target(result, source_name):
    matches = [target for target, source in result["mapping"].items() if source == source_name]
    if len(matches) != 1:
        raise ValueError("EXACT_TARGET_BONE_MAPPING_REQUIRED:" + source_name)
    return matches[0]


def _wrap_pi(angle):
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    while angle > math.pi:
        angle -= 2.0 * math.pi
    return angle


def _nearest_axis_delta(vector, travel_axis):
    foot = math.atan2(vector.y, vector.x)
    travel = math.atan2(travel_axis.y, travel_axis.x)
    direct = _wrap_pi(travel - foot)
    reverse = _wrap_pi(travel + math.pi - foot)
    return direct if abs(direct) <= abs(reverse) else reverse


def blender_pass(args):
    import bpy
    from mathutils import Matrix, Vector

    result = g.read(args.result)
    calibration = g.read(args.calibration)
    if calibration.get("input_result") != g.ref(args.result):
        raise ValueError("CALIBRATION_RETARGET_RESULT_MISMATCH")
    required = {"FIXED_FLOOR_PENETRATION_LEFT", "FIXED_FLOOR_PENETRATION_RIGHT"}
    if not required.issubset(set(calibration.get("errors", []))):
        raise ValueError("EXACT_PENETRATION_DIAGNOSTIC_REQUIRED")
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(result["output_blend"])))
    scene = bpy.context.scene
    sole_mesh = bpy.data.objects[result["sole_mesh"]]
    target_bones = set(result["mapping"])
    rigs = [
        ob for ob in scene.objects
        if ob.type == "ARMATURE" and target_bones.issubset({bone.name for bone in ob.data.bones})
        and (
            sole_mesh.parent == ob
            or any(mod.type == "ARMATURE" and mod.object == ob for mod in sole_mesh.modifiers)
        )
    ]
    if len(rigs) != 1:
        raise ValueError("ONE_SKINNED_TARGET_ARMATURE_REQUIRED")
    rig = rigs[0]
    original_location = list(rig.location)
    minimum = min(
        row["sole_clearance_m"][side]
        for row in calibration["samples"][:-1]
        for side in ("left", "right")
    )
    safety_margin = 0.002
    constant_lift = max(0.0, -float(minimum) + safety_margin)
    rig.location.z += constant_lift

    travel_axis = Vector(calibration["travel_axis_world"])
    travel_axis.z = 0.0
    if travel_axis.length <= 1e-9:
        raise ValueError("HORIZONTAL_TRAVEL_AXIS_REQUIRED")
    travel_axis.normalize()
    feet = {
        "left": (_mapped_target(result, "foot_l"), _mapped_target(result, "ball_l")),
        "right": (_mapped_target(result, "foot_r"), _mapped_target(result, "ball_r")),
    }
    start, end = [int(value) for value in result["baked_frame_range"]]
    frame_values = [float(row["frame"]) for row in calibration["samples"]]
    if len(frame_values) < 9 or len(frame_values) > 49 or frame_values[0] != start or frame_values[-1] != end:
        raise ValueError("EXACT_BOUNDED_CALIBRATION_SAMPLE_TIMELINE_REQUIRED")
    original_foot_world = {}
    for frame in frame_values:
        scene.frame_set(int(frame), subframe=frame - int(frame))
        original_foot_world[frame] = {
            side: (rig.matrix_world @ rig.pose.bones[foot_name].matrix).copy()
            for side, (foot_name, _) in feet.items()
        }
    calibration_contract = g.read(g.resolve(calibration["contract"]))
    contact_max = float(calibration_contract["contact_clearance_max_m"])
    support_clearance = 0.003
    support_samples = {}
    ik_targets = {}
    for side, label in (("left", "l"), ("right", "r")):
        contact_sample = int(calibration["phase_candidates"]["contact_" + label])
        passing_sample = int(calibration["phase_candidates"]["passing_" + label])
        selected = []
        cursor = contact_sample
        while cursor < len(calibration["samples"]) - 1:
            selected.append(cursor)
            if cursor > passing_sample and calibration["samples"][cursor]["sole_clearance_m"][side] > contact_max:
                selected.pop()
                break
            cursor += 1
        if passing_sample not in selected or len(selected) < 3:
            raise ValueError("BOUND_CONTACT_THROUGH_PASSING_WINDOW_REQUIRED:" + side)
        support_samples[side] = selected
        target = bpy.data.objects.new("UAL_Guide_" + side + "_Foot_IK", None)
        scene.collection.objects.link(target)
        target.hide_render = True
        target.empty_display_type = "PLAIN_AXES"
        for row in calibration["samples"]:
            frame = float(row["frame"])
            base = Vector(row["joint_heads_world_m"][side + "_ankle"])
            base.z += constant_lift
            if int(row["sample"]) in selected:
                base.z += float(calibration["fixed_floor"]["world_z_m"]) + support_clearance - (
                    float(row["sole_clearance_m"][side]) + float(calibration["fixed_floor"]["world_z_m"]) + constant_lift
                )
            target.location = base
            target.keyframe_insert("location", frame=frame)
        shin = rig.pose.bones[_mapped_target(result, "calf_" + ("l" if side == "left" else "r"))]
        constraint = shin.constraints.new("IK")
        constraint.name = "UAL_GUIDE_FIXED_FLOOR_" + side.upper()
        constraint.target = target
        constraint.chain_count = 2
        constraint.use_tail = True
        ik_targets[side] = target

    correction_rows = []
    for frame in frame_values:
        scene.frame_set(int(frame), subframe=frame - int(frame))
        frame_row = {"frame": frame, "foot_world_up_correction_degrees": {}}
        for side, (foot_name, toe_name) in feet.items():
            foot = rig.pose.bones[foot_name]
            toe = rig.pose.bones[toe_name]
            ankle_world = rig.matrix_world @ foot.head
            preserved = original_foot_world[frame][side].copy()
            preserved.translation = ankle_world
            foot.rotation_mode = "QUATERNION"
            foot.matrix = rig.matrix_world.inverted() @ preserved
            bpy.context.view_layer.update()
            ankle_world = rig.matrix_world @ foot.head
            toe_world = rig.matrix_world @ toe.head
            vector = toe_world - ankle_world
            vector.z = 0.0
            delta = _nearest_axis_delta(vector, travel_axis)
            pivot = ankle_world
            world = rig.matrix_world @ foot.matrix
            rotation = Matrix.Translation(pivot) @ Matrix.Rotation(delta, 4, "Z") @ Matrix.Translation(-pivot)
            foot.matrix = rig.matrix_world.inverted() @ rotation @ world
            bpy.context.view_layer.update()
            foot.keyframe_insert("rotation_quaternion", frame=frame)
            frame_row["foot_world_up_correction_degrees"][side] = math.degrees(delta)
        correction_rows.append(frame_row)

    action = rig.animation_data.action if rig.animation_data else None
    if action is None:
        raise ValueError("BOUND_TARGET_ACTION_REQUIRED")
    if hasattr(action, "fcurves"):
        curves = list(action.fcurves)
    else:
        curves = [
            curve
            for layer in action.layers
            for strip in layer.strips
            for channelbag in strip.channelbags
            for curve in channelbag.fcurves
        ]
    for curve in curves:
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"

    out = g.local(args.out)
    scene.frame_set(start)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    preview = out / "FIRST_CORRECTED_POSE_GUIDE_NATIVE_1920.png"
    scene.render.filepath = str(preview)
    bpy.ops.render.render(write_still=True)
    output_blend = out / "SeedSan_UAL_Sprint_Loop_CONTACT_REPAIRED_DIAGNOSTIC.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))

    repaired = dict(result)
    repaired.update({
        "status": "HOLD_CORRECTED_POSE_GUIDE_REQUIRES_FIXED_FLOOR_RECALIBRATION",
        "production_ready": False,
        "output_blend": g.ref(output_blend),
        "generator": g.ref(__file__),
        "first_native_pose": g.ref(preview),
        "motion_repair": {
            "input_calibration": g.ref(args.calibration),
            "constant_armature_world_z_lift_m": constant_lift,
            "original_armature_location": original_location,
            "corrected_armature_location": list(rig.location),
            "per_frame_root_translation_applied": False,
            "actual_leg_ik_contact_cleanup": {
                "support_clearance_m": support_clearance,
                "support_sample_indices": support_samples,
                "targets": {side: target.name for side, target in ik_targets.items()},
                "horizontal_support_lock": False,
                "constraints": "two_bone_shin_IK_on_actual_target_rig",
                "note": "This stage establishes vertical contact and phase geometry only; authored horizontal root travel and planted-foot slide are separate runtime gates.",
            },
            "foot_axis_corrections": correction_rows,
            "interpolation": "LINEAR",
        },
        "limitations": list(result.get("limitations", [])) + [
            "Corrected Blender/VRM appearance remains pose-guide-only and cannot enter visible SABLE art.",
            "Requires a fresh independent fixed-floor calibration and Ponytail visual review before guide use.",
        ],
    })
    g.write(out / "retarget_result.json", repaired)
    print(str(out / "retarget_result.json"))


def main(args):
    g.resolve(g.read(args.result)["output_blend"])
    calibration = g.read(args.calibration)
    if calibration.get("status") != "HOLD":
        raise ValueError("FAILED_CALIBRATION_INPUT_REQUIRED")
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
        "--calibration", str(g.local(args.calibration)), "--out", str(out), "--blender-pass",
    ]
    with (out / "blender.log").open("w", encoding="utf-8") as log:
        child = subprocess.run(
            command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    if child.returncode:
        raise ValueError("POSE_GUIDE_MOTION_REPAIR_FAILED:" + str(out / "blender.log"))
    repaired = g.read(out / "retarget_result.json")
    g.resolve(repaired["output_blend"])
    g.resolve(repaired["first_native_pose"])
    g.write(out / "completion.json", {
        "status": "COMPLETE_DIAGNOSTIC_REPAIR_REQUIRES_RECALIBRATION",
        "result": g.ref(out / "retarget_result.json"),
        "owned_child_exited": True,
        "production_ready": False,
    })
    print(str(out / "completion.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--blender-pass", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parsed = parser.parse_args(argv)
    if parsed.blender_pass:
        blender_pass(parsed)
    else:
        main(parsed)
