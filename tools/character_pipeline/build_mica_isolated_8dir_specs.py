#!/usr/bin/env python3
"""Create project-local per-direction specs for MICA's isolated Blender rig."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
AXES = {
    "E": (1.0, 0.0),
    "SE": (math.sqrt(0.5), -math.sqrt(0.5)),
    "S": (0.0, -1.0),
    "SW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "N": (0.0, 1.0),
    "NE": (math.sqrt(0.5), math.sqrt(0.5)),
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        default="art_src/characters/mica/fast_pipeline/imagegen/direction_masters/candidate_mica_c03_direction_masters_v8_r3",
    )
    parser.add_argument(
        "--landmarks",
        default="art_src/characters/mica/fast_pipeline/imagegen/direction_masters/candidate_mica_c03_direction_masters_v8_r3/MICA_C03_DIRECTION_LEG_LANDMARKS_V8_R3.json",
    )
    parser.add_argument(
        "--e-prototype-spec",
        default="art_src/characters/mica/fast_pipeline/motion_profiles/MICA_C03_E_LOWER_F00_ISOLATED_RIG_V1.json",
    )
    parser.add_argument(
        "--output-root",
        default="art_src/characters/mica/fast_pipeline/motion_profiles/candidate_mica_c03_v8_r7_isolated_8dir",
    )
    parser.add_argument(
        "--candidate-root",
        default="art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v8_r7_isolated_lower_ual_8dir",
    )
    parser.add_argument("--revision", default="V8_R7")
    args = parser.parse_args()

    source_root = (ROOT / args.source_root).resolve()
    landmarks_path = (ROOT / args.landmarks).resolve()
    prototype_path = (ROOT / args.e_prototype_spec).resolve()
    output_root = (ROOT / args.output_root).resolve()
    candidate_root = (ROOT / args.candidate_root).resolve()
    for path in (source_root, landmarks_path, prototype_path, output_root, candidate_root):
        path.relative_to(ROOT.resolve())
    output_root.mkdir(parents=True, exist_ok=True)
    landmarks = json.loads(landmarks_path.read_text(encoding="utf-8"))["directions"]
    prototype = json.loads(prototype_path.read_text(encoding="utf-8"))
    revision = str(args.revision).upper()
    revision_label = revision.replace("_", " ")
    w_lower_root = (
        ROOT
        / "art_src/characters/mica/fast_pipeline/imagegen/lower_gait_layers/"
        "candidate_mica_c03_lower_gait_w_v8_r7/normalized"
    ).resolve()
    w_lower_rgb = w_lower_root / "MICA_C03_W_LOWER_NEUTRAL_RIG_IMAGEGEN_GREEN_EXACT_GREEN.png"
    w_lower_mask = w_lower_root / "MICA_C03_W_LOWER_NEUTRAL_RIG_IMAGEGEN_GREEN_MASK.png"
    for path in (w_lower_rgb, w_lower_mask):
        path.relative_to(ROOT.resolve())
        if not path.is_file():
            raise SystemExit(f"missing W mirrored E lower source: {path}")

    generated: list[str] = []
    for direction in DIRECTIONS:
        if direction == "E":
            spec = json.loads(json.dumps(prototype))
            spec["role"] = f"MICA C03 {revision_label} E isolated lower Blender+UAL approved-prototype replication"
            spec["output_dir"] = rel(candidate_root / "technical_masks" / direction)
        elif direction == "W":
            exact = source_root / "MICA_C03_W_IMAGEGEN_EXACT_GREEN.png"
            mask = source_root / "MICA_C03_W_IMAGEGEN_MASK.png"
            # A profile master has overlapping legs, so a screen-midline split
            # cannot isolate them.  Mirror the already approved E lower source
            # and its hand-authored polygons, swapping screen-left/right.
            def mirror_points(points: list[list[int]]) -> list[list[int]]:
                return [[1023 - int(x), int(y)] for x, y in points]

            def mirror_point(point: list[int]) -> list[int]:
                return [1023 - int(point[0]), int(point[1])]

            e_left = prototype["limbs"]["screen_left"]
            e_right = prototype["limbs"]["screen_right"]
            legs = {
                "screen_left": {
                    "joint": "foot_l",
                    "knee_bend_sign": -1.0,
                    "polygon_px": mirror_points(e_right["polygon_px"]),
                    "hip_px": mirror_point(e_right["hip_px"]),
                    "knee_px": mirror_point(e_right["knee_px"]),
                    "ankle_px": mirror_point(e_right["ankle_px"]),
                    "toe_px": mirror_point(e_right["toe_px"]),
                },
                "screen_right": {
                    "joint": "foot_r",
                    "knee_bend_sign": -1.0,
                    "polygon_px": mirror_points(e_left["polygon_px"]),
                    "hip_px": mirror_point(e_left["hip_px"]),
                    "knee_px": mirror_point(e_left["knee_px"]),
                    "ankle_px": mirror_point(e_left["ankle_px"]),
                    "toe_px": mirror_point(e_left["toe_px"]),
                },
            }
            spec = {
                "schema": 1,
                "direction": direction,
                "role": f"MICA C03 {revision_label} W isolated lower Blender+UAL mirrored approved-E candidate",
                "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
                "mask_mode": "polygons",
                "source_rgb": rel(w_lower_rgb),
                "source_mask": rel(w_lower_mask),
                "upper_rgb": rel(exact),
                "upper_mask": rel(mask),
                "ual_curve": prototype["ual_curve"],
                "output_dir": rel(candidate_root / "technical_masks" / direction),
                "composite": {
                    "lower_uniform_scale": 0.731,
                    "lower_translation_xy": [0.066, -0.457],
                    "upper_crop_uv": [0.0, 0.0, 1.0, 1.0],
                    "upper_seam_y_px": 900,
                },
                "gait": {
                    "frame_count": 24,
                    "stride_units": 0.34,
                    "swing_lift_units": 0.18,
                    "stance_fraction": 0.62,
                    "foot_center_mode": "source_relative",
                    "foot_center_x": 0.055,
                    "depth_offset_units": 0.0,
                    "deformation_mode": "two_bone",
                    "forward_axis_xy": [-1.0, 0.0],
                    "source_ground_y_px": 1340,
                },
                "limbs": legs,
            }
        else:
            exact = source_root / f"MICA_C03_{direction}_IMAGEGEN_EXACT_GREEN.png"
            mask = source_root / f"MICA_C03_{direction}_IMAGEGEN_MASK.png"
            entry = landmarks[direction]
            is_diagonal = len(direction) == 2
            stride = 0.20 if is_diagonal else 0.16
            lift = 0.08
            legs: dict[str, object] = {}
            for name in ("screen_left", "screen_right"):
                points: dict[str, list[int]] = {}
                for joint, uv in entry["legs"][name].items():
                    points[f"{joint}_px"] = [int(round(float(uv[0]) * 1024)), int(round((1.0 - float(uv[1])) * 1536))]
                bend = -1.0 if name == "screen_left" else 1.0
                legs[name] = {
                    "joint": "foot_l" if name == "screen_left" else "foot_r",
                    "knee_bend_sign": bend,
                    **points,
                }
            spec = {
                "schema": 1,
                "direction": direction,
                "role": f"MICA C03 {revision_label} {direction} isolated lower Blender+UAL candidate",
                "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
                "mask_mode": "midline_split",
                "source_rgb": rel(exact),
                "source_mask": rel(mask),
                "upper_rgb": rel(exact),
                "upper_mask": rel(mask),
                "ual_curve": prototype["ual_curve"],
                "output_dir": rel(candidate_root / "technical_masks" / direction),
                "composite": {
                    "lower_uniform_scale": 1.0,
                    "lower_translation_xy": [0.0, 0.0],
                    "upper_crop_uv": [0.0, 0.0, 1.0, 1.0],
                    "upper_seam_y_px": 900,
                },
                "gait": {
                    "frame_count": 24,
                    "stride_units": stride,
                    "swing_lift_units": lift,
                    "stance_fraction": 0.62,
                    "foot_center_mode": "source_relative",
                    "foot_center_x": 0.0,
                    "depth_offset_units": 0.0,
                    "deformation_mode": "front_back_limited" if direction in {"N", "S"} or is_diagonal else "two_bone",
                    "knee_inward_units": 0.132 if direction in {"N", "S"} else (0.06 if is_diagonal else 0.0),
                    "ankle_inward_units": 0.045 if direction in {"N", "S"} else (0.02 if is_diagonal else 0.0),
                    "knee_raise_units": 0.03 if direction in {"N", "S"} else (0.015 if is_diagonal else 0.0),
                    "knee_ankle_follow": 0.45,
                    "forward_axis_xy": [round(v, 9) for v in AXES[direction]],
                    "source_ground_y_px": 1420,
                },
                "limbs": legs,
            }
        spec["direction"] = direction
        spec["candidate_root"] = rel(candidate_root)
        output_path = output_root / f"MICA_C03_{direction}_ISOLATED_RIG_{revision}.json"
        output_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        generated.append(rel(output_path))

    manifest = {
        "schema": 1,
        "role": f"MICA C03 {revision_label} isolated Blender+UAL per-direction spec set",
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "directions": generated,
    }
    manifest_path = output_root / f"MICA_C03_{revision}_ISOLATED_8DIR_SPEC_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
