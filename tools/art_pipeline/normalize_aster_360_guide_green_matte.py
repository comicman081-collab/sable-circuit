#!/usr/bin/env python3
"""Normalize only the exterior matte of ASTER Blender guide PNGs to #00FF00.

Blender's display transform leaves sub-value rounding variance at a few world
background pixels. This deterministic flood fill replaces only near-green
pixels connected to an image edge; it never touches detached guide geometry.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360"
GREEN = (0, 255, 0)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Path must stay inside project: {resolved}") from exc
    return resolved


def looks_like_matte(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return red <= 12 and green >= 235 and blue <= 12


def normalize(path: Path) -> int:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    data = image.load()
    seen = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    for x, y in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        if looks_like_matte(data[x, y]):
            queue.append((x, y))
    changed = 0
    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if seen[index] or not looks_like_matte(data[x, y]):
            continue
        seen[index] = 1
        if data[x, y] != GREEN:
            data[x, y] = GREEN
            changed += 1
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))
    image.save(path)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guides", type=Path, default=DEFAULT)
    parser.add_argument("--image", type=Path, default=None, help="Normalize one project-local guide PNG without touching a manifest")
    args = parser.parse_args()
    if args.image is not None:
        image = project_path(args.image)
        if not image.is_file() or image.suffix.lower() != ".png":
            raise SystemExit(f"Expected one PNG guide image: {image}")
        changed = normalize(image)
        print(json.dumps({"files": 1, "changed_pixels": changed, "matte": "#00FF00", "image": image.relative_to(ROOT).as_posix()}))
        return 0
    guides = project_path(args.guides)
    paths = sorted((guides / "poses").rglob("*_GREEN.png"))
    if len(paths) != 144:
        raise SystemExit(f"Expected exactly 144 generated guide PNGs, found {len(paths)}")
    total_changed = sum(normalize(path) for path in paths)
    manifest_path = guides / "ASTER_360_MOTION_GUIDE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["green_matte_normalization"] = {
        "method": "edge-connected near-green deterministic replacement",
        "source_matte": "#00FF00",
        "changed_pixels": total_changed,
        "guide_geometry_modified": False,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(paths), "changed_pixels": total_changed, "matte": "#00FF00"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
