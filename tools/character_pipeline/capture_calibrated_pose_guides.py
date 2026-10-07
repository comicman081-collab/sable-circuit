"""Capture eight independently calibrated Blender+UAL pose-guide frames.

The generic licensed model remains diagnostic geometry only.  Images produced
here are prohibited from visible SABLE art, atlases, HTML and runtime assets.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g

PHASES = (
    "contact_l", "down_l", "passing_l", "flight_l",
    "contact_r", "down_r", "passing_r", "flight_r",
)


def _sample_sole(mesh_object, sole_ids, depsgraph):
    evaluated = mesh_object.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return {
            side: [list(evaluated.matrix_world @ mesh.vertices[index].co) for index in ids]
            for side, ids in sole_ids.items()
        }
    finally:
        evaluated.to_mesh_clear()


def blender_pass(args):
    import bpy

    result = g.read(args.result)
    calibration = g.read(args.calibration)
    if (
        calibration.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY"
        or calibration.get("errors") != []
        or calibration.get("input_result") != g.ref(args.result)
        or set(calibration.get("phase_candidates", {})) != set(PHASES)
    ):
        raise ValueError("EXACT_PASS_CALIBRATION_REQUIRED")
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(result["output_blend"])))
    scene = bpy.context.scene
    camera = scene.camera
    if camera is None or camera.data.type != "ORTHO":
        raise ValueError("LOCKED_ORTHOGRAPHIC_GUIDE_CAMERA_REQUIRED")
    original_camera = [list(row) for row in camera.matrix_world]
    camera.data.ortho_scale *= 1.28
    locked_camera = [list(row) for row in camera.matrix_world]

    floor_z = float(calibration["fixed_floor"]["world_z_m"])
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, floor_z - 0.001))
    floor = bpy.context.object
    floor.name = "INDEPENDENT_FIXED_FLOOR_GUIDE_ONLY"
    material = bpy.data.materials.new("FixedFloorGuideMaterial")
    material.diffuse_color = (0.12, 0.15, 0.19, 1.0)
    floor.data.materials.append(material)

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = "WORLD"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("GuideWorld")
    scene.world.color = (0.035, 0.045, 0.065)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2

    out = g.local(args.out)
    sole_mesh = bpy.data.objects[result["sole_mesh"]]
    samples = {int(row["sample"]): row for row in calibration["samples"]}
    rows = []
    for phase in PHASES:
        sample_index = int(calibration["phase_candidates"][phase])
        sample = samples[sample_index]
        frame = float(sample["frame"])
        scene.frame_set(int(frame), subframe=frame - int(frame))
        if [list(row) for row in camera.matrix_world] != locked_camera:
            raise ValueError("CAMERA_TRANSFORM_DRIFT")
        image = out / "frames" / (phase + ".png")
        image.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        actual_soles = _sample_sole(sole_mesh, result["sole_vertex_ids"], bpy.context.evaluated_depsgraph_get())
        rows.append({
            "phase": phase,
            "sample": sample_index,
            "frame": frame,
            "time_s": sample["time_s"],
            "image": g.ref(image),
            "actual_sole_vertices_world_m": actual_soles,
            "sole_clearance_m": sample["sole_clearance_m"],
            "foot_yaw_from_travel_degrees": sample["foot_yaw_from_travel_degrees"],
            "left_minus_right_travel_m": sample["left_minus_right_travel_m"],
        })
    g.write(out / "capture.json", {
        "schema": 1,
        "scope": "EIGHT_CALIBRATED_LICENSED_POSE_GUIDES_NOT_VISIBLE_ART",
        "production_ready": False,
        "visible_art_authority": "built_in_ImageGen_only",
        "blender_ual_role": "pose_geometry_guide_only",
        "retarget_result": g.ref(args.result),
        "calibration": g.ref(args.calibration),
        "blend": result["output_blend"],
        "capture_generator": g.ref(__file__),
        "action": result["action"],
        "screen_direction": result["screen_direction"],
        "native_resolution": [1920, 1920],
        "original_camera_world_matrix": original_camera,
        "locked_capture_camera_world_matrix": locked_camera,
        "locked_capture_ortho_scale": camera.data.ortho_scale,
        "fixed_floor_world_z_m": floor_z,
        "frames": rows,
        "limitations": [
            "Eight static generic-model pose guides only; not MICA appearance or temporal runtime approval.",
            "Every ImageGen use requires exact per-frame visual and Ponytail review before reservation.",
        ],
    })
    print(str(out / "capture.json"))


def main(args):
    result = g.read(args.result)
    g.resolve(result["output_blend"])
    calibration = g.read(args.calibration)
    if calibration.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY":
        raise ValueError("PASS_CONTACT_CALIBRATION_REQUIRED")
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
        raise ValueError("CALIBRATED_POSE_GUIDE_CAPTURE_FAILED:" + str(out / "blender.log"))
    capture = g.read(out / "capture.json")
    for row in capture["frames"]:
        g.resolve(row["image"])
    g.write(out / "completion.json", {
        "status": "COMPLETE_EIGHT_STATIC_GUIDES_PENDING_VISUAL_REVIEW",
        "capture": g.ref(out / "capture.json"),
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
