#!/usr/bin/env python3
"""Derive an ASTER idle atlas with saturated-green matte pixels removed.

The V5 atlases remain immutable evidence.  This creates a new V6 derivative
from their decoded RGBA pixels, removing only the palette-prohibited green
contamination and preserving every other pixel.  No source art is overwritten.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
FRAME_COUNT = 4
SOURCE = ROOT / "assets/units/operators/aster/idle_360_clean_v5"
OUTPUT = ROOT / "assets/units/operators/aster/idle_360_clean_v6"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def green_mask(frame: np.ndarray) -> np.ndarray:
    r = frame[:, :, 0].astype(np.int16)
    g = frame[:, :, 1].astype(np.int16)
    b = frame[:, :, 2].astype(np.int16)
    a = frame[:, :, 3]
    # ASTER's approved palette has cyan (high blue) but no saturated green.
    # Keep the predicate narrow so only chroma-key contamination is removed.
    return (
        (a > 16)
        & (g > 180)
        & (r < 45)
        & (b < 85)
        & (g > r * 2 + 16)
        & (g > b * 2 + 16)
    )


def main() -> int:
    if not SOURCE.is_dir():
        raise SystemExit(f"missing immutable source family: {SOURCE}")
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite existing derivative: {OUTPUT}")
    OUTPUT.mkdir(parents=True)
    records: dict[str, object] = {}
    preview = Image.new("RGBA", (256 * len(DIRECTIONS), 276 * FRAME_COUNT), (16, 22, 29, 255))
    draw = ImageDraw.Draw(preview)

    for column, direction in enumerate(DIRECTIONS):
        source_path = SOURCE / direction / f"ASTER_IDLE_{direction}_CLEAN_V5_ATLAS.webp"
        if not source_path.is_file():
            raise SystemExit(f"missing atlas: {source_path}")
        source = np.asarray(Image.open(source_path).convert("RGBA"), dtype=np.uint8)
        expected = (CELL * FRAME_COUNT, CELL, 4)
        if source.shape != expected:
            raise SystemExit(f"unexpected {direction} shape {source.shape}, expected {expected}")
        output = source.copy()
        frame_records = []
        total_removed = 0
        for index in range(FRAME_COUNT):
            frame = output[index * CELL : (index + 1) * CELL]
            mask = green_mask(frame)
            removed = int(np.count_nonzero(mask))
            if removed:
                frame[mask, :3] = 0
                frame[mask, 3] = 0
            total_removed += removed
            preview.alpha_composite(Image.fromarray(frame, "RGBA").resize((256, 256), Image.Resampling.LANCZOS), (column * 256, index * 276))
            draw.rectangle((column * 256, index * 276, column * 256 + 118, index * 276 + 20), fill=(4, 9, 13, 230))
            draw.text((column * 256 + 5, index * 276 + 4), f"{direction} FRAME {index + 1:02d}", fill=(132, 238, 244, 255))
            frame_records.append({"frame": index, "removed_saturated_green_pixels": removed})
        output_path = OUTPUT / direction / f"ASTER_IDLE_{direction}_CLEAN_V6_ATLAS.webp"
        output_path.parent.mkdir(parents=True)
        Image.fromarray(output, "RGBA").save(output_path, "WEBP", lossless=True, method=6, exact=True)
        decoded = np.asarray(Image.open(output_path).convert("RGBA"), dtype=np.uint8)
        if not np.array_equal(decoded, output):
            raise SystemExit(f"lossless round-trip changed {direction}")
        residual = int(np.count_nonzero(green_mask(decoded)))
        if residual:
            raise SystemExit(f"{direction} retains {residual} saturated-green pixels")
        records[direction] = {
            "source": source_path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(source_path),
            "atlas": output_path.relative_to(ROOT).as_posix(),
            "atlas_sha256": sha256(output_path),
            "resolution": [CELL, CELL * FRAME_COUNT],
            "frame_count": FRAME_COUNT,
            "removed_saturated_green_pixels": total_removed,
            "frames": frame_records,
        }

    preview_path = OUTPUT / "ASTER_IDLE_360_CLEAN_V6_CONTACT.png"
    preview.save(preview_path, optimize=True)
    manifest = {
        "schema": 1,
        "role": "ASTER 8-direction four-frame artifact-free idle V6 derivative",
        "parent_family": "assets/units/operators/aster/idle_360_clean_v5",
        "directions": list(DIRECTIONS),
        "frame_size": [CELL, CELL],
        "frame_count_per_direction": FRAME_COUNT,
        "fps": 4,
        "method": "lossless RGBA decode of V5 followed by narrow saturated-green chroma contamination removal",
        "source_modified": False,
        "removed_only_palette_prohibited_green": True,
        "directions_output": records,
        "preview": preview_path.relative_to(ROOT).as_posix(),
        "preview_sha256": sha256(preview_path),
        "qa": {
            "residual_visible_saturated_green_pixels": 0,
            "lossless_webp_roundtrip": True,
            "visual_gate": "USER_REVIEW_REQUIRED",
        },
    }
    manifest_path = OUTPUT / "ASTER_IDLE_360_CLEAN_V6_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "total_removed": sum(item["removed_saturated_green_pixels"] for item in records.values()), "preview": preview_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
