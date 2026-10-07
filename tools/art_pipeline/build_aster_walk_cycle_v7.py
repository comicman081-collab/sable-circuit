#!/usr/bin/env python3
"""Build a source-preserving 384px ASTER walk-cycle runtime derivative.

The existing ImageGen-authored six-frame walk atlases are already approved
source art.  This script only repacks their 768px cells into the current
full-body runtime cell size, clears RGB under transparent pixels, and removes
the one-pixel saturated-green fringe that can survive chroma cleanup.  It
does not redraw, segment, rotate, or reconstruct the character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
SOURCE_ROOT = ROOT / "motion_lab_v1/public/assets/atlas/aster"
DEFAULT_OUTPUT = ROOT / "assets/units/operators/aster/walk_cycle_imagegen_v7"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clear_transparent_rgb(im: Image.Image) -> tuple[Image.Image, int]:
    rgba = im.convert("RGBA")
    px = rgba.load()
    removed = 0
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a == 0:
                if (r, g, b) != (0, 0, 0):
                    px[x, y] = (0, 0, 0, 0)
            elif g > 100 and g > r * 1.30 and g > b * 1.30:
                # Only the saturated green matte fringe is removed.  The
                # authored subject pixels remain byte-for-byte represented.
                px[x, y] = (0, 0, 0, 0)
                removed += 1
    return rgba, removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": 1,
        "role": "ASTER ImageGen-authored six-frame walk-cycle derivative",
        "generator": "Codex built-in ImageGen source, repacked only",
        "cell": [384, 384],
        "frames": 6,
        "fps": {"walk": 8, "run": 12},
        "source_root": "motion_lab_v1/public/assets/atlas/aster/*_walk.webp",
        "directions": {},
        "green_fringe_pixels_removed": {},
    }
    for direction in DIRECTIONS:
        source = SOURCE_ROOT / f"{direction}_walk.webp"
        if not source.is_file():
            raise SystemExit(f"missing source: {source}")
        with Image.open(source) as original:
            original = original.convert("RGBA")
            if original.size != (2304, 1536):
                raise SystemExit(f"unexpected source size {source}: {original.size}")
            strip = Image.new("RGBA", (384, 384 * 6), (0, 0, 0, 0))
            removed = 0
            for index in range(6):
                cell = original.crop(((index % 3) * 768, (index // 3) * 768,
                                      (index % 3 + 1) * 768, (index // 3 + 1) * 768))
                cell = cell.resize((384, 384), Image.Resampling.LANCZOS)
                cell, count = clear_transparent_rgb(cell)
                removed += count
                strip.alpha_composite(cell, (0, index * 384))
        # PNG is intentional here: the bundled browser must decode the
        # derivative reliably on all supported Chromium builds.  The
        # source-facing WebP assets remain untouched beside this runtime copy.
        path = output / f"ASTER_WALK_{direction}_IMAGEGEN_V7_ATLAS.png"
        strip.save(path, format="PNG", optimize=True)
        with Image.open(path) as check:
            if check.size != (384, 2304) or check.mode != "RGBA":
                raise SystemExit(f"invalid derivative: {path}")
        manifest["directions"][direction] = {
            "source": str(source.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha256(source),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path),
            "frames": 6,
        }
        manifest["green_fringe_pixels_removed"][direction] = removed
    (output / "WALK_CYCLE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
