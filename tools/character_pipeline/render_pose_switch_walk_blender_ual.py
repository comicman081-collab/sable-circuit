#!/usr/bin/env python3
"""Render a project-local ImageGen pose-switch walk through Blender + UAL.

R17 deliberately separates source-art authoring from motion implementation:
the neutral/A/B frames are built-in ImageGen masters, while Blender renders
the aligned full-body planes and UAL supplies the 24-frame cadence/contact
schedule.  No image model, repaint, or local diffusion pipeline is used here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def base_module():
    """Import the existing deterministic Blender scene/plane helpers."""
    helper_path = str(Path(__file__).resolve().parent)
    if helper_path not in sys.path:
        sys.path.insert(0, helper_path)
    import render_fast_motion_blender_ual as helper

    return helper


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--neutral-root", type=Path, required=True)
    parser.add_argument("--pose-source-root", type=Path, required=True)
    parser.add_argument("--ual-locomotion", type=Path, required=True)
    parser.add_argument("--ual-fire", type=Path, required=True)
    return parser.parse_args(argv)


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{label} must be a JSON object: {path}")
    return value


def pin_pose_source(root: Path, direction: str, phase: str) -> dict[str, str]:
    source_dir = root / direction
    rgb = source_dir / f"{phase}_green.png"
    mask = source_dir / f"{phase}_mask.png"
    qa = source_dir / "WALK_POSE_SOURCE_ALIGNMENT_QA.json"
    if not rgb.is_file() or not mask.is_file() or not qa.is_file():
        raise SystemExit(f"missing aligned {direction} {phase} source: {source_dir}")
    return {
        "rgb": rgb.relative_to(ROOT).as_posix(),
        "rgb_sha256": sha256(rgb),
        "mask": mask.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(mask),
        "alignment_qa": qa.relative_to(ROOT).as_posix(),
        "alignment_qa_sha256": sha256(qa),
    }


def source_file(root: Path, direction: str, phase: str, kind: str) -> Path:
    return root / direction / f"{phase}_{kind}.png"


def cycle_phase(index: int) -> str:
    """Map UAL contact cadence to planted A / neutral transfer / planted B.

    The six-frame contact windows in UAL V5 are kept intact.  Neutral transfer
    frames are explicit and prevent the old R16 X-leg/tap-dance look caused by
    applying one continuous deformation to both legs.
    """
    bucket = index % 24
    if bucket < 6:
        return "pose_a"
    if bucket < 12:
        return "neutral"
    if bucket < 18:
        return "pose_b"
    return "neutral"


def hide_all(planes: dict[str, bpy.types.Object]) -> None:
    for plane in planes.values():
        plane.hide_render = True
        plane.location = (0.0, 0.0, 0.0)
        plane.rotation_euler = (0.0, 0.0, 0.0)
        plane.scale = (1.0, 1.0, 1.0)


def render_plane_frames(
    scene: bpy.types.Scene,
    planes: dict[str, bpy.types.Object],
    output_dir: Path,
    state: str,
    frame_count: int,
    *,
    helper,
    locomotion_samples: list[dict],
) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for index in range(frame_count):
        hide_all(planes)
        if state == "move":
            if index >= len(locomotion_samples):
                raise SystemExit(f"missing UAL sample {index}")
            phase_name = cycle_phase(index)
            sample = locomotion_samples[index]
        else:
            phase_name = "neutral"
            sample = locomotion_samples[(index * 6) % len(locomotion_samples)]
        plane = planes[phase_name]
        plane.hide_render = False
        # The runtime owns world translation.  The sprite source is rendered
        # at a fixed local origin so the runtime can apply UAL root motion
        # without baking a second translation into the atlas.
        plane.location = (0.0, 0.0, 0.0)
        plane.rotation_euler = (0.0, 0.0, 0.0)
        output = output_dir / f"{index:02d}.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        if not output.is_file() or output.stat().st_size <= 0:
            raise SystemExit(f"Blender failed to render {state} frame {index}: {output}")
        row: dict[str, object] = {
            "index": index,
            "path": output.relative_to(ROOT).as_posix(),
            "pose_source": phase_name,
            "root_transform": [0.0, 0.0, 0.0],
            "ual_sample_index": int(sample.get("index", index)),
            "ual_phase": float(sample.get("phase", index / max(1, frame_count))),
            "ual_contacts": sample.get("contacts", {}),
            "sha256": sha256(output),
        }
        if state == "move":
            root_motion = sample.get("root_motion", {}).get("translation_xy_norm", [0.0, 0.0])
            if not isinstance(root_motion, list) or len(root_motion) != 2:
                raise SystemExit(f"invalid UAL root motion sample {index}")
            row["ual_root_motion_translation_xy_norm"] = [float(root_motion[0]), float(root_motion[1])]
        rows.append(row)
    return rows


def main() -> int:
    args = parse_args()
    helper = base_module()
    spec_path = project_path(args.spec, "spec")
    candidate = project_path(args.candidate, "candidate")
    neutral_root = project_path(args.neutral_root, "neutral-root")
    pose_root = project_path(args.pose_source_root, "pose-source-root")
    locomotion_path = project_path(args.ual_locomotion, "ual-locomotion")
    fire_path = project_path(args.ual_fire, "ual-fire")
    if candidate.exists() and any(candidate.iterdir()):
        entries = {entry.name for entry in candidate.iterdir()}
        if entries != {"blender_frames"}:
            raise SystemExit(f"refusing to overwrite non-resumable candidate: {candidate}")

    spec = load_json(spec_path, "spec")
    prefix = str(spec.get("art_prefix", "MICA_C03"))
    runtime = spec["runtime"]
    cell_size = int(runtime["cell_size"])
    if cell_size != 384:
        raise SystemExit("pose-switch renderer requires 384px runtime cells")
    locomotion = load_json(locomotion_path, "UAL locomotion")
    samples = locomotion.get("locomotion", {}).get("samples", [])
    if not isinstance(samples, list) or len(samples) != 24:
        raise SystemExit("UAL locomotion must provide exactly 24 samples")
    fire = load_json(fire_path, "UAL fire")
    fire_samples = fire.get("samples", [])
    if not isinstance(fire_samples, list) or len(fire_samples) != 6:
        raise SystemExit("UAL fire must provide exactly six samples")
    if not neutral_root.is_dir() or not pose_root.is_dir():
        raise SystemExit("neutral and aligned pose roots must be project directories")
    review = load_json(neutral_root / f"{prefix}_COSTUME_CONTINUITY_REVIEW.json", "costume continuity review")
    if review.get("costume_continuity") != "PASS":
        raise SystemExit("neutral ImageGen source costume continuity must PASS")

    candidate.mkdir(parents=True, exist_ok=True)
    scene, _camera = helper.configure_scene(cell_size)
    records: dict[str, dict[str, list[dict[str, object]]]] = {}
    source_pins: dict[str, dict[str, object]] = {}
    blend_objects: list[bpy.types.Object] = []
    for direction in DIRECTIONS:
        neutral_rgb = neutral_root / f"{prefix}_{direction}_IMAGEGEN_EXACT_GREEN.png"
        neutral_mask = neutral_root / f"{prefix}_{direction}_IMAGEGEN_MASK.png"
        if not neutral_rgb.is_file() or not neutral_mask.is_file():
            raise SystemExit(f"missing neutral authority for {direction}")
        source_pins[direction] = {
            "neutral": {
                "rgb": neutral_rgb.relative_to(ROOT).as_posix(),
                "rgb_sha256": sha256(neutral_rgb),
                "mask": neutral_mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(neutral_mask),
                "authority_review": (neutral_root / f"{prefix}_COSTUME_CONTINUITY_REVIEW.json").relative_to(ROOT).as_posix(),
            },
            "pose_a": pin_pose_source(pose_root, direction, "pose_a"),
            "pose_b": pin_pose_source(pose_root, direction, "pose_b"),
        }
        planes = {
            "neutral": helper.build_subject_plane(neutral_rgb, neutral_mask, f"{prefix}_{direction}_NEUTRAL"),
            "pose_a": helper.build_subject_plane(
                source_file(pose_root, direction, "pose_a", "green"),
                source_file(pose_root, direction, "pose_a", "mask"),
                f"{prefix}_{direction}_POSE_A",
            ),
            "pose_b": helper.build_subject_plane(
                source_file(pose_root, direction, "pose_b", "green"),
                source_file(pose_root, direction, "pose_b", "mask"),
                f"{prefix}_{direction}_POSE_B",
            ),
        }
        for plane in planes.values():
            blend_objects.append(plane)
        direction_rows: dict[str, list[dict[str, object]]] = {}
        direction_rows["idle"] = render_plane_frames(
            scene, planes, candidate / "blender_frames" / direction / "idle", "idle", 4,
            helper=helper, locomotion_samples=samples,
        )
        direction_rows["move"] = render_plane_frames(
            scene, planes, candidate / "blender_frames" / direction / "move", "move", 24,
            helper=helper, locomotion_samples=samples,
        )
        direction_rows["fire"] = render_plane_frames(
            scene, planes, candidate / "blender_frames" / direction / "fire", "fire", 6,
            helper=helper, locomotion_samples=samples,
        )
        records[direction] = direction_rows
        for plane in planes.values():
            bpy.data.objects.remove(plane, do_unlink=True)

    blend_path = candidate / "blender_scene" / f"{prefix}_POSE_SWITCH_UAL_V1.blend"
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    manifest = {
        "schema": 1,
        "role": f"{prefix} ImageGen neutral/A/B pose-switch move frames driven by UAL V5 cadence",
        "motion_only": True,
        "source_art": "built-in ImageGen neutral masters plus built-in ImageGen walk-pose masters",
        "source_art_modified": False,
        "neutral_master_root": neutral_root.relative_to(ROOT).as_posix(),
        "pose_source_root": pose_root.relative_to(ROOT).as_posix(),
        "source_pins": source_pins,
        "blender": {"version": bpy.app.version_string, "scene": blend_path.relative_to(ROOT).as_posix(), "scene_sha256": sha256(blend_path)},
        "ual": {
            "locomotion_curve": locomotion_path.relative_to(ROOT).as_posix(),
            "locomotion_curve_sha256": sha256(locomotion_path),
            "fire_curve": fire_path.relative_to(ROOT).as_posix(),
            "fire_curve_sha256": sha256(fire_path),
            "license": "CC0-1.0 motion-only reference",
            "locomotion_action": locomotion.get("locomotion", {}).get("action"),
            "fire_action": fire.get("action", {}).get("name"),
        },
        "states": {"idle": 4, "move": 24, "fire": 6},
        "gait_contract": {
            "schedule": "UAL contact windows: pose_a[0..5], neutral[6..11], pose_b[12..17], neutral[18..23]",
            "pose_phases": ["pose_a", "neutral", "pose_b", "neutral"],
            "runtime_root_motion": "Atlas root held at [0,0,0]; runtime maps UAL root_motion.translation_xy_norm to actor world translation.",
            "support_sole_policy": "Source A/B frames are selected only at UAL contact windows; no Blender limb deformation or boot rotation is applied.",
            "source_art_raster_edit": False,
        },
        "directions": records,
    }
    manifest_path = candidate / f"{prefix}_POSE_SWITCH_BLENDER_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("POSE_SWITCH_BLENDER_UAL_RENDER_PASS=" + json.dumps({"candidate": candidate.relative_to(ROOT).as_posix(), "manifest": manifest_path.relative_to(ROOT).as_posix(), "directions": len(records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
