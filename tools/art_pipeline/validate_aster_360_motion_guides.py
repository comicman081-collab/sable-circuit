#!/usr/bin/env python3
"""Validate non-final ASTER Blender 360 pose guides before 2D authoring.

The guide set is intentionally not a visual asset.  This QA only asserts that
the expected UAL-timing/ASTER-rifle construction guides exist, use the exact
green source matte, and preserve the no-UAL-mesh policy recorded by Blender.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
GUIDE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {
    "idle": ("ready", "inhale", "micro_weight_shift", "return"),
    "move": ("contact_a", "down_a", "passing_a", "high_a", "contact_b", "down_b", "passing_b", "high_b"),
    "fire": ("aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"),
}
GREEN = (0, 255, 0)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Path must stay inside project: {resolved}") from exc
    return resolved


def expected_files(root: Path) -> list[Path]:
    return [
        root / "poses" / state / f"ASTER_GUIDE_{state}_{direction}_{key}_GREEN.png"
        for state, keys in STATES.items()
        for key in keys
        for direction in DIRECTIONS
    ]


def inspect_png(path: Path) -> dict:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
        pixels = image.getdata()
        green_pixels = sum(pixel == GREEN for pixel in pixels)
        total_pixels = image.width * image.height
        corners = [image.getpixel(corner) for corner in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1))]
        return {
            "resolution": [image.width, image.height],
            "corner_green": all(pixel == GREEN for pixel in corners),
            "green_ratio": round(green_pixels / total_pixels, 6),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guides", type=Path, default=GUIDE_ROOT)
    args = parser.parse_args()
    guides = project_path(args.guides)
    manifest_path = guides / "ASTER_360_MOTION_GUIDE_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"FAIL: manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = expected_files(guides)
    missing = [path.relative_to(ROOT).as_posix() for path in files if not path.is_file()]
    checks = [inspect_png(path) for path in files if path.is_file()]
    failures: list[str] = []
    if manifest.get("key_count") != len(files):
        failures.append("manifest key_count does not match expected guides")
    if manifest.get("direction_count") != len(DIRECTIONS):
        failures.append("manifest direction_count is not 8")
    if manifest.get("ual_mesh_rendered") is not False or manifest.get("final_body_rendered") is not False:
        failures.append("manifest incorrectly claims UAL mesh or final body render")
    if manifest.get("saved_mesh_object_count") != 0:
        failures.append("saved non-final blend contains mesh objects")
    if missing:
        failures.append(f"missing guide images: {len(missing)}")
    for check in checks:
        if check["resolution"] != [512, 512]:
            failures.append("non-512 guide image")
        if not check["corner_green"] or check["green_ratio"] < 0.60:
            failures.append("guide image lacks exact #00FF00 exterior matte")
    result = {
        "schema": 1,
        "guide_root": guides.relative_to(ROOT).as_posix(),
        "expected_key_count": len(files),
        "found_key_count": len(checks),
        "states": {state: len(keys) * len(DIRECTIONS) for state, keys in STATES.items()},
        "green_ratio_min": min((check["green_ratio"] for check in checks), default=0.0),
        "green_ratio_max": max((check["green_ratio"] for check in checks), default=0.0),
        "ual_mesh_rendered": manifest.get("ual_mesh_rendered"),
        "saved_mesh_object_count": manifest.get("saved_mesh_object_count"),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "next": "manual SABLE sprite authoring only after a separate user-approved 2048 Static Master",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
