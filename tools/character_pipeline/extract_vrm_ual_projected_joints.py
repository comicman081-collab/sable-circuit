#!/usr/bin/env python3
"""Extract reviewed Blender+UAL joint projections without rendering appearance.

Run inside Blender against an already calibrated diagnostic blend.  The output
contains camera-space joint coordinates only.  It cannot contain, rebuild or
promote any visible character pixels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[2]
CAPTURE_GENERATOR = ROOT / "tools/character_pipeline/capture_calibrated_pose_guides.py"
PHASES = ["contact_l", "down_l", "passing_l", "flight_l",
          "contact_r", "down_r", "passing_r", "flight_r"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def project_path(value: str, label: str) -> Path:
    path = Path(value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside project: {path}") from exc
    return path


def ref(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


def point(camera, scene, world) -> list[float]:
    ndc = world_to_camera_view(scene, camera, world)
    width = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
    height = scene.render.resolution_y * scene.render.resolution_percentage / 100.0
    return [round(float(ndc.x * width), 6), round(float((1.0 - ndc.y) * height), 6)]


def matrix_close(left, right, tolerance=1e-6) -> bool:
    return max(abs(float(a) - float(b)) for row_a, row_b in zip(left, right)
               for a, b in zip(row_a, row_b)) <= tolerance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--armature", default="SeedSan_Licensed_Target_Rig")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])

    calibration_path = project_path(args.calibration, "calibration")
    capture_path = project_path(args.capture, "capture")
    out = project_path(args.out, "out")
    if out.exists():
        raise SystemExit(f"refusing to overwrite: {out}")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    if calibration.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY":
        raise SystemExit("exact calibrated phase guide report required")
    blend_path = Path(bpy.data.filepath).resolve()
    if calibration.get("errors") != [] or calibration.get("input_blend", {}).get("sha256") != digest(blend_path):
        raise SystemExit("opened blend does not match calibration")
    if (capture.get("calibration") != ref(calibration_path) or
            capture.get("blend") != calibration.get("input_blend") or
            capture.get("capture_generator") != ref(CAPTURE_GENERATOR) or
            capture.get("native_resolution") != [1920, 1920]):
        raise SystemExit("exact calibrated capture provenance required")
    capture_rows = capture.get("frames", [])
    samples = {int(row["sample"]): row for row in calibration.get("samples", [])}
    if [row.get("phase") for row in capture_rows] != PHASES:
        raise SystemExit("canonical eight-phase capture order required")
    for row in capture_rows:
        phase = row["phase"]
        sample_index = calibration.get("phase_candidates", {}).get(phase)
        sample = samples.get(sample_index)
        if (row.get("sample") != sample_index or sample is None or
                float(row.get("frame")) != float(sample.get("frame"))):
            raise SystemExit("capture phase/sample/frame mismatch")
        guide_path = project_path(row["image"]["path"], "guide image")
        if ref(guide_path) != row["image"]:
            raise SystemExit("stale or substituted guide image")

    # Reload the exact disk blend so altered in-memory scene state cannot be
    # attributed to an unchanged file hash, then restore the exact camera used
    # by the reviewed capture (including its 1.28x wider orthographic scale).
    bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False)
    armature = bpy.data.objects.get(args.armature)
    camera = bpy.context.scene.camera
    if armature is None or armature.type != "ARMATURE" or camera is None:
        raise SystemExit("reviewed target armature and camera required")

    required = ["hips", "thigh.L", "shin.L", "foot.L", "toe.L", "thigh.R", "shin.R", "foot.R", "toe.R"]
    if any(name not in armature.pose.bones for name in required):
        raise SystemExit("required humanoid leg bones missing")
    scene = bpy.context.scene
    camera.matrix_world = Matrix(capture["locked_capture_camera_world_matrix"])
    camera.data.ortho_scale = float(capture["locked_capture_ortho_scale"])
    scene.render.resolution_x, scene.render.resolution_y = capture["native_resolution"]
    scene.render.resolution_percentage = 100
    locked_matrix = [[float(value) for value in row] for row in camera.matrix_world]
    if not matrix_close(locked_matrix, capture["locked_capture_camera_world_matrix"]):
        raise SystemExit("capture camera matrix restoration failed")
    rows = []
    for capture_row in capture_rows:
        frame = float(capture_row["frame"])
        whole = int(frame)
        scene.frame_set(whole, subframe=frame - whole)
        bpy.context.view_layer.update()
        if (not matrix_close([[float(value) for value in row] for row in camera.matrix_world], locked_matrix) or
                abs(float(camera.data.ortho_scale) - float(capture["locked_capture_ortho_scale"])) > 1e-6):
            raise SystemExit("capture camera drift")
        bones = armature.pose.bones
        world = lambda vector: armature.matrix_world @ vector
        joints = {
            "pelvis": point(camera, scene, world(bones["hips"].head)),
            "hip_left": point(camera, scene, world(bones["thigh.L"].head)),
            "knee_left": point(camera, scene, world(bones["thigh.L"].tail)),
            "ankle_left": point(camera, scene, world(bones["shin.L"].tail)),
            "toe_left": point(camera, scene, world(bones["toe.L"].tail)),
            "hip_right": point(camera, scene, world(bones["thigh.R"].head)),
            "knee_right": point(camera, scene, world(bones["thigh.R"].tail)),
            "ankle_right": point(camera, scene, world(bones["shin.R"].tail)),
            "toe_right": point(camera, scene, world(bones["toe.R"].tail)),
        }
        pelvis_world = Vector(samples[int(capture_row["sample"])]["pelvis_world_m"])
        calibration_pelvis_px = point(camera, scene, pelvis_world)
        if max(abs(a - b) for a, b in zip(joints["pelvis"], calibration_pelvis_px)) > 1.0:
            raise SystemExit("projected pelvis does not match calibration geometry")
        rows.append({
            "phase": capture_row["phase"],
            "sample": capture_row["sample"],
            "frame": frame,
            "guide_image": capture_row["image"],
            "projected_joints_px": joints,
            "calibration_pelvis_projection_px": calibration_pelvis_px,
        })
    if [row["phase"] for row in rows] != PHASES:
        raise SystemExit("canonical eight-phase capture order required")
    payload = {
        "schema": 1,
        "stage": "vrm_ual_projected_joint_guides",
        "status": "PASS_GEOMETRY_DATA_ONLY",
        "production_ready": False,
        "visible_art_authority": "none",
        "blender_ual_role": "joint_and_contact_geometry_only",
        "input_blend": ref(Path(bpy.data.filepath)),
        "calibration": ref(calibration_path),
        "capture": ref(capture_path),
        "extractor": ref(Path(__file__).resolve()),
        "camera": {
            "name": camera.name,
            "world_matrix": locked_matrix,
            "orthographic_scale": float(camera.data.ortho_scale)
        },
        "native_projection_size": [
            int(scene.render.resolution_x * scene.render.resolution_percentage / 100),
            int(scene.render.resolution_y * scene.render.resolution_percentage / 100)
        ],
        "coordinate_system": "image pixels, origin top-left, +x right, +y down",
        "phases": rows,
        "limitations": [
            "Contains no MICA or Seed-san visible pixels.",
            "Does not authorize a renderer, visible frame, gait, runtime, firing or promotion PASS."
        ]
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out), "sha256": digest(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
