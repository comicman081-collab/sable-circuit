"""Blender-side QA for the mesh-free ASTER 360 motion driver.

Run only through Blender 5.2.1 background mode.  The report validates motion
coverage and provenance structure; it never asserts visual-art approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
RANGES = {"IDLE": (0.0, 24.0), "MOVE": (0.0, 21.0), "FIRE": (0.0, 15.0)}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide-root", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Path must remain inside project: {resolved}") from exc
    return resolved


def main() -> int:
    args = parse_args()
    root = project_path(args.guide_root)
    output = project_path(args.output or root / "ASTER_360_POSE_DRIVER_QA.json")
    rig = bpy.data.objects.get("ASTER_360_POSE_DRIVER__MESH_FREE")
    meshes = [obj.name for obj in bpy.context.scene.objects if obj.type == "MESH"]
    expected = {f"ASTER_{state}_{direction}__SABLE_POSE_DRIVER" for state in RANGES for direction in DIRECTIONS}
    actions = {action.name: action for action in bpy.data.actions if action.name.startswith("ASTER_")}
    failures: list[str] = []
    if rig is None or rig.type != "ARMATURE":
        failures.append("missing mesh-free ASTER pose rig")
    elif len(rig.pose.bones) != 22:
        failures.append(f"unexpected ASTER pose-bone count: {len(rig.pose.bones)}")
    if meshes:
        failures.append(f"saved mesh objects are forbidden: {meshes}")
    if set(actions) != expected:
        failures.append(f"motion actions mismatch: expected={len(expected)} actual={len(actions)}")
    fire_markers = ("aim_set", "muzzle_contact", "recoil_peak", "ready_return")
    action_records = []
    for name in sorted(expected):
        action = actions.get(name)
        if action is None:
            continue
        state = name.split("_")[1]
        actual_range = tuple(round(float(value), 3) for value in action.frame_range)
        if actual_range != RANGES[state]:
            failures.append(f"{name} range={actual_range}, expected={RANGES[state]}")
        markers = [marker.name for marker in action.pose_markers]
        if state == "FIRE" and tuple(markers) != fire_markers:
            failures.append(f"{name} fire markers={markers}")
        action_records.append({"name": name, "range": list(actual_range), "markers": markers})
    report = {
        "schema": 1,
        "role": "ASTER mesh-free Blender 360 motion-driver QA only",
        "blend": bpy.data.filepath,
        "status": "PASS" if not failures else "FAIL",
        "visual_gate": "NOT_EVALUATED",
        "runtime_promotion": False,
        "saved_mesh_object_count": len(meshes),
        "pose_bone_count": len(rig.pose.bones) if rig else 0,
        "expected_action_count": len(expected),
        "action_count": len(actions),
        "actions": action_records,
        "failures": failures,
        "next": "high-fidelity fire-pose authoring guide; no Qwen batch or runtime integration",
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_360_POSE_DRIVER_QA=" + json.dumps({
        "status": report["status"], "actions": report["action_count"], "meshes": report["saved_mesh_object_count"],
    }))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
