#!/usr/bin/env python3
"""Build project-local binary limb mattes from an approved source matte.

The source artwork is never repainted.  Each output is the intersection of the
approved subject matte and a project-authored polygon used only by Blender's
2D cutout rig.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[2]


def interpolate_chain_x(points: list[tuple[float, float]], y: float) -> float:
    ordered = sorted(points, key=lambda point: point[1])
    if y <= ordered[0][1]:
        return ordered[0][0]
    if y >= ordered[-1][1]:
        return ordered[-1][0]
    for first, second in zip(ordered, ordered[1:]):
        if first[1] <= y <= second[1]:
            span = max(1.0, second[1] - first[1])
            amount = (y - first[1]) / span
            return first[0] + (second[0] - first[0]) * amount
    return ordered[-1][0]


def midline_polygons(spec: dict, width: int, height: int) -> dict[str, list[tuple[int, int]]]:
    chains: dict[str, list[tuple[float, float]]] = {}
    for name in ("screen_left", "screen_right"):
        entry = spec["limbs"][name]
        chains[name] = [tuple(float(v) for v in entry[f"{joint}_px"]) for joint in ("hip", "knee", "ankle", "toe")]
    # The default lead-in keeps enough of the thigh plate above the seam for
    # directions whose lower-body source is already cleanly separated.  A
    # source with a weapon or arms crossing the midline can opt into a hard
    # seam start so those upper-body pixels never enter a moving leg plate.
    requested_top = spec.get("midline_top_px")
    if requested_top is None:
        requested_top = min(point[1] for chain in chains.values() for point in chain) - 120
    top = max(0, min(height - 1, int(requested_top)))
    bottom = height - 1
    boundary: list[tuple[int, int]] = []
    for index in range(65):
        y = top + (bottom - top) * index / 64.0
        left_x = interpolate_chain_x(chains["screen_left"], y)
        right_x = interpolate_chain_x(chains["screen_right"], y)
        boundary.append((int(round((left_x + right_x) * 0.5)), int(round(y))))
    return {
        "screen_left": [(0, top), *boundary, (0, bottom)],
        "screen_right": [*boundary, (width - 1, bottom), (width - 1, top)],
    }


def project_path(value: str, label: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain below the project root: {path}") from exc
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()

    spec_path = project_path(args.spec, "spec")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    source_mask_path = project_path(spec["source_mask"], "source mask")
    upper_mask_path = project_path(spec["upper_mask"], "upper mask")
    output_dir = project_path(spec["output_dir"], "output directory")
    output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(source_mask_path) as opened:
        source_mask = opened.convert("L")
    width, height = source_mask.size
    with Image.open(upper_mask_path) as opened:
        upper_mask = opened.convert("L")
    upper_width, upper_height = upper_mask.size

    manifest: dict[str, object] = {
        "schema": 1,
        "role": "project-local Blender-only isolated limb mattes",
        "source_mask": source_mask_path.relative_to(ROOT).as_posix(),
        "source_size": [width, height],
        "source_art_modified": False,
        "limbs": {},
    }

    seam_y = int(spec["composite"]["upper_seam_y_px"])
    if seam_y <= 0 or seam_y >= upper_height:
        raise SystemExit(f"upper seam must be within 1..{upper_height - 1}")
    upper_segment = Image.new("L", (upper_width, upper_height), 0)
    ImageDraw.Draw(upper_segment).rectangle((0, 0, upper_width - 1, seam_y), fill=255)
    upper_fixed = ImageChops.multiply(upper_mask, upper_segment)
    upper_output = output_dir / "UPPER_FIXED_MASK.png"
    upper_fixed.save(upper_output, optimize=True)
    manifest["upper_fixed"] = {
        "source_mask": upper_mask_path.relative_to(ROOT).as_posix(),
        "path": upper_output.relative_to(ROOT).as_posix(),
        "seam_y_px": seam_y,
        "nonzero_bbox_px": list(upper_fixed.getbbox() or ()),
    }

    mask_mode = str(spec.get("mask_mode", "polygons"))
    if mask_mode == "midline_split":
        generated_polygons = midline_polygons(spec, width, height)
    elif mask_mode == "polygons":
        generated_polygons = {}
    else:
        raise SystemExit("mask_mode must be polygons or midline_split")

    for name, entry in spec["limbs"].items():
        polygon = (
            generated_polygons[name]
            if mask_mode == "midline_split"
            else [tuple(int(v) for v in point) for point in entry["polygon_px"]]
        )
        if len(polygon) < 3:
            raise SystemExit(f"{name}: polygon requires at least three points")
        if any(x < 0 or x >= width or y < 0 or y >= height for x, y in polygon):
            raise SystemExit(f"{name}: polygon point lies outside {width}x{height}")
        polygon_mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(polygon_mask).polygon(polygon, fill=255)
        isolated = ImageChops.multiply(source_mask, polygon_mask)
        output_path = output_dir / f"{name.upper()}_ISOLATED_MASK.png"
        isolated.save(output_path, optimize=True)
        bbox = isolated.getbbox()
        if bbox is None:
            raise SystemExit(f"{name}: isolated mask is empty")
        manifest["limbs"][name] = {
            "path": output_path.relative_to(ROOT).as_posix(),
            "polygon_px": [list(point) for point in polygon],
            "nonzero_bbox_px": list(bbox),
        }

    manifest_path = output_dir / "ISOLATED_LIMB_MASK_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
