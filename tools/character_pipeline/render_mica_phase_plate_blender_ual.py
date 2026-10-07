#!/usr/bin/env python3
"""Render discrete immutable ImageGen lower gait plates through Blender+UAL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_mica_isolated_lower_blender_ual import (  # noqa: E402
    ROOT,
    build_grid_plane,
    configure_scene,
    project_path,
    sha256,
)


def args_after_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--cell-size", type=int, default=384)
    return parser.parse_args(args_after_dash())


def main() -> None:
    args = parse_args()
    spec_path = project_path(args.spec, "spec")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    direction = str(spec["direction"]).upper()
    candidate_root = project_path(spec["candidate_root"], "candidate root")
    technical_root = project_path(spec["output_dir"], "technical output")
    ual_path = project_path(spec["ual_curve"], "UAL curve")
    upper_rgb = project_path(spec["upper_rgb"], "upper rgb")
    source_height = int(spec.get("source_height_px", 1536))
    seam_y_px = float(spec["composite"]["upper_seam_y_px"])
    upper_mask = technical_root / "UPPER_FIXED_MASK.png"
    if not upper_mask.is_file():
        raise SystemExit(f"missing fixed upper mask: {upper_mask}")

    ual = json.loads(ual_path.read_text(encoding="utf-8"))
    ual_samples = ual["locomotion"]["samples"]
    frame_count = int(ual["locomotion"]["sample_count"])
    phase_sequence = list(spec["phase_sequence"])
    phase_contacts = spec.get("phase_contacts", {})
    phase_events = spec.get("phase_events", {})
    if len(phase_sequence) != frame_count:
        raise SystemExit("phase sequence length must match UAL sample count")

    scene, _camera = configure_scene(args.cell_size)
    upper_plane = build_grid_plane(upper_rgb, upper_mask, f"MICA_{direction}_PHASE_UPPER")
    upper_plane.location.z = 0.3

    phase_planes: dict[str, bpy.types.Object] = {}
    source_records: dict[str, object] = {}
    for key, entry in spec["phase_plates"].items():
        rgb_path = project_path(entry["rgb"], f"{key} rgb")
        mask_path = technical_root / f"{key.upper()}_LOWER_MASK.png"
        if not mask_path.is_file():
            raise SystemExit(f"missing lower phase mask: {mask_path}")
        plane = build_grid_plane(rgb_path, mask_path, f"MICA_{direction}_{key.upper()}")
        translation = [float(v) for v in entry.get("translation_px", [0.0, 0.0])]
        compensation_px = float(entry.get("stance_compensation_source_px", 0.0))
        compensation_span_px = float(
            entry.get("compensation_anchor_to_sole_span_px", source_height - seam_y_px)
        )
        if compensation_span_px <= 0.0:
            raise SystemExit(f"{key}: compensation anchor-to-sole span must be positive")
        scale_y = 1.0 + compensation_px / compensation_span_px
        # The source plane is exactly three Blender units high.  Vertical
        # stance compensation is a seam-pinned Y-only stretch: the waist
        # remains registered while the planted sole moves opposite the
        # continuous world root.  This avoids both a hard seam gap and the
        # old whole-plate six-frame jump.
        seam_anchor_y = 1.5 - 3.0 * seam_y_px / source_height
        plane.scale.y = scale_y
        plane.location.x = translation[0] * 3.0 / source_height
        plane.location.y = (
            seam_anchor_y * (1.0 - scale_y)
            - translation[1] * 3.0 / source_height
        )
        plane.location.z = 0.2
        phase_planes[key] = plane
        source_records[key] = {
            "rgb": rgb_path.relative_to(ROOT).as_posix(),
            "rgb_sha256": sha256(rgb_path),
            "mask": mask_path.relative_to(ROOT).as_posix(),
            "mask_sha256": sha256(mask_path),
            "translation_px": translation,
            "uniform_scale": 1.0,
            "scale_y_about_seam": scale_y,
            "stance_compensation_source_px": compensation_px,
            "compensation_anchor_to_sole_span_px": compensation_span_px,
            "rotation_degrees": 0.0,
        }

    component_root = candidate_root / "blender_components" / direction / "phase_plate"
    component_root.mkdir(parents=True, exist_ok=True)
    scene_root = candidate_root / "blender_scene"
    scene_root.mkdir(parents=True, exist_ok=True)
    all_planes = [upper_plane, *phase_planes.values()]

    def render_component(visible: bpy.types.Object, output_path: Path) -> None:
        for item in all_planes:
            item.hide_render = item is not visible
        scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)

    upper_component = component_root / "upper_fixed.png"
    render_component(upper_plane, upper_component)
    frames: list[dict[str, object]] = []
    for index, key in enumerate(phase_sequence):
        if key not in phase_planes:
            raise SystemExit(f"frame {index}: unknown phase plate {key}")
        output_path = component_root / f"{index:02d}_{key}.png"
        render_component(phase_planes[key], output_path)
        sample = ual_samples[index]
        contacts = (
            phase_contacts.get(key, {})
            if phase_contacts
            else sample.get("contacts", {})
        )
        events = (
            phase_events.get(key, [])
            if phase_events
            else sample.get("events", [])
        )
        frames.append(
            {
                "index": index,
                "phase": float(sample["phase"]),
                "phase_key": key,
                "ual_contacts": contacts,
                "ual_events": events,
                "phase_component": {
                    "path": output_path.relative_to(ROOT).as_posix(),
                    "sha256": sha256(output_path),
                },
                "upper_root_translation_px": [0.0, 0.0],
                "lower_uniform_scale": 1.0,
                "boot_rotation_degrees": 0.0,
            }
        )

    blend_path = scene_root / f"MICA_C03_{direction}_PHASE_PLATE_UAL.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    manifest = {
        "schema": 1,
        "role": f"MICA C03 {direction} Blender+UAL immutable ImageGen phase-plate render",
        "direction": direction,
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "source_art_modified": False,
        "spec": spec_path.relative_to(ROOT).as_posix(),
        "spec_sha256": sha256(spec_path),
        "ual_curve": ual_path.relative_to(ROOT).as_posix(),
        "ual_curve_sha256": sha256(ual_path),
        "frame_count": frame_count,
        "cell_size": [args.cell_size, args.cell_size],
        "phase_sources": source_records,
        "upper_component": {
            "path": upper_component.relative_to(ROOT).as_posix(),
            "sha256": sha256(upper_component),
        },
        "frames": frames,
        "blend": blend_path.relative_to(ROOT).as_posix(),
        "blend_sha256": sha256(blend_path),
    }
    manifest_path = candidate_root / f"MICA_C03_{direction}_PHASE_PLATE_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
