"""Refine actual sole contact timing in a Blender+UAL pose guide only.

This never authors or modifies visible SABLE character art.  It adjusts the
existing diagnostic IK empties at the independently sampled timeline so sole
vertices converge to a fixed floor.  The right contact window is deliberately
opened earlier than the down pose, preserving a visible natural pelvis drop.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g


def blender_pass(args):
    import bpy
    import calibrate_vrm_ual_ground_contact as contact

    result = g.read(args.result)
    calibration = g.read(args.calibration)
    if calibration.get("input_result") != g.ref(args.result):
        raise ValueError("CALIBRATION_RETARGET_RESULT_MISMATCH")
    if calibration.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY":
        raise ValueError("PASS_TECHNICAL_CALIBRATION_REQUIRED")
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(result["output_blend"])))
    scene = bpy.context.scene
    sole_mesh = bpy.data.objects[result["sole_mesh"]]
    sole_ids = result["sole_vertex_ids"]
    cleanup = result.get("motion_repair", {}).get("actual_leg_ik_contact_cleanup", {})
    targets = {side: bpy.data.objects.get(name) for side, name in cleanup.get("targets", {}).items()}
    if set(targets) != {"left", "right"} or any(target is None for target in targets.values()):
        raise ValueError("EXACT_EXISTING_FOOT_IK_TARGETS_REQUIRED")

    rig = next((
        mod.object for mod in sole_mesh.modifiers
        if mod.type == "ARMATURE" and mod.object is not None
    ), None)
    if rig is None:
        raise ValueError("SKINNED_TARGET_ARMATURE_REQUIRED")
    floor_z = float(calibration["fixed_floor"]["world_z_m"])
    sample_rows = {int(row["sample"]): row for row in calibration["samples"][:-1]}
    # Metres above the independently fixed floor.  The right entry begins at
    # sample 26 (pelvis ~29 mm above its sample-30 minimum), so contact/down are
    # no longer visually duplicate while passing and flight order stay intact.
    desired = {
        "left": {2: .002, 3: .001, 4: .001, 5: .001, 6: .001, 7: .001, 8: .001, 9: .004},
        "right": {26: .002, 27: .002, 28: .001, 29: .001, 30: .001, 31: .001,
                  32: .001, 33: .001, 34: .002, 35: .010},
    }
    convergence = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for iteration in range(96):
        maximum_error = 0.0
        for side in ("left", "right"):
            target = targets[side]
            for sample, wanted in desired[side].items():
                row = sample_rows[sample]
                frame = float(row["frame"])
                scene.frame_set(int(frame), subframe=frame - int(frame))
                bpy.context.view_layer.update()
                vertices = contact._sample_sole(sole_mesh, sole_ids, depsgraph)
                actual = min(point[2] for point in vertices[side]) - floor_z
                error = float(wanted) - float(actual)
                maximum_error = max(maximum_error, abs(error))
                target.location.z += error
                target.keyframe_insert("location", frame=frame)
        convergence.append({"iteration": iteration + 1, "maximum_clearance_error_m": maximum_error})
        print("contact-refine", convergence[-1], flush=True)
        if maximum_error <= .0005:
            break

    # Confirm directly from evaluated sole vertices after all keys settle.
    measured = {"left": {}, "right": {}}
    for side in ("left", "right"):
        for sample, wanted in desired[side].items():
            frame = float(sample_rows[sample]["frame"])
            scene.frame_set(int(frame), subframe=frame - int(frame))
            bpy.context.view_layer.update()
            vertices = contact._sample_sole(sole_mesh, sole_ids, depsgraph)
            actual = min(point[2] for point in vertices[side]) - floor_z
            measured[side][str(sample)] = {"desired_m": wanted, "actual_m": actual}
            print("contact-measure", side, sample, wanted, actual, flush=True)
            if abs(actual - wanted) > .0015:
                raise ValueError("SOLE_CONTACT_REFINEMENT_DID_NOT_CONVERGE:" + side + ":" + str(sample))

    out = g.local(args.out)
    output_blend = out / "SeedSan_UAL_Sprint_Loop_CONTACT_REFINED_DIAGNOSTIC.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    refined = dict(result)
    refined.update({
        "status": "HOLD_REFINED_POSE_GUIDE_REQUIRES_FRESH_CALIBRATION_AND_VISUAL_REVIEW",
        "production_ready": False,
        "output_blend": g.ref(output_blend),
        "generator": g.ref(__file__),
        "contact_refinement": {
            "input_calibration": g.ref(args.calibration),
            "fixed_floor_world_z_m": floor_z,
            "per_frame_root_translation_applied": False,
            "visible_art_modified": False,
            "desired_sole_clearance_m": desired,
            "measured_sole_clearance_m": measured,
            "convergence": convergence,
            "right_contact_opened_at_sample": 26,
            "right_down_expected_sample": 30,
            "expected_contact_to_down_pelvis_drop_m": (
                float(sample_rows[26]["pelvis_world_m"][2])
                - float(sample_rows[30]["pelvis_world_m"][2])
            ),
        },
        "limitations": list(result.get("limitations", [])) + [
            "This is Blender+UAL pose geometry only; its pixels are prohibited from runtime art.",
            "Fresh independent calibration and visual plus Ponytail FULL review remain mandatory.",
        ],
    })
    g.write(out / "retarget_result.json", refined)
    print(str(out / "retarget_result.json"))


def main(args):
    g.resolve(g.read(args.result)["output_blend"])
    g.resolve(g.read(args.calibration)["input_blend"])
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
        raise ValueError("POSE_GUIDE_CONTACT_REFINEMENT_FAILED:" + str(out / "blender.log"))
    refined = g.read(out / "retarget_result.json")
    g.resolve(refined["output_blend"])
    g.write(out / "completion.json", {
        "status": "COMPLETE_DIAGNOSTIC_REFINEMENT_REQUIRES_RECALIBRATION",
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
    blender_pass(parsed) if parsed.blender_pass else main(parsed)
