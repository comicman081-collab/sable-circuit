#!/usr/bin/env python3
"""Compose a native-1920x1080 technical review video from 384px runtime cells.

The video is an evidence container, not a visual-quality pass: cells remain at
their native 384px size and are never upscaled.  It shows every canonical
direction and the UAL pose-switch schedule so reviewers can inspect the actual
frame order without relying on an interactive browser tab.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
WIDTH, HEIGHT = 1920, 1080
GREEN = (0, 255, 0)


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atlas_cell(path: Path, index: int) -> Image.Image:
    with Image.open(path) as atlas:
        if atlas.mode != "RGBA" or atlas.size != (CELL, CELL * 24):
            raise SystemExit(f"expected 384x9216 RGBA move atlas: {path} {atlas.mode} {atlas.size}")
        return atlas.crop((0, index * CELL, CELL, (index + 1) * CELL)).copy()


def frame(direction: str, index: int, cell: Image.Image) -> np.ndarray:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (7, 16, 25, 255))
    draw = ImageDraw.Draw(canvas)
    # Native 384px cell, centered.  This is intentionally not enlarged.
    x, y = (WIDTH - CELL) // 2, 320
    canvas.alpha_composite(cell, (x, y))
    draw.rectangle((48, 44, WIDTH - 48, HEIGHT - 48), outline=(70, 127, 156, 190), width=2)
    draw.line((160, 756, WIDTH - 160, 756), fill=(115, 206, 226, 95), width=2)
    for gx in range(160, WIDTH - 159, 160):
        draw.line((gx, 756, gx, HEIGHT - 48), fill=(90, 170, 195, 45), width=1)
    draw.text((72, 76), "MICA C03 R17 POSE-SWITCH | BLENDER+UAL | TECHNICAL DYNAMIC REVIEW", fill=(222, 239, 249, 255))
    draw.text((72, 112), f"direction {direction} | UAL move frame {index:02d}/23 | pose schedule A[00-05] · neutral[06-11] · B[12-17] · neutral[18-23]", fill=(141, 201, 220, 255))
    draw.text((72, 1032), "Native 1920x1080 container; character cell preserved at native 384x384 (no upscale). Visual/Ponytail/runtime promotion remains HOLD until review.", fill=(144, 167, 182, 255))
    return np.asarray(canvas.convert("RGB"), dtype=np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = project_path(args.runtime, "runtime")
    output = project_path(args.output, "output")
    if output.exists():
        raise SystemExit(f"refusing to overwrite video: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    source_paths = {direction: runtime / direction / "move.png" for direction in DIRECTIONS}
    if not all(path.is_file() for path in source_paths.values()):
        raise SystemExit(f"missing one or more move atlases under {runtime}")
    writer = imageio.get_writer(str(output), fps=24, codec="libx264", quality=8, macro_block_size=1)
    try:
        for direction in DIRECTIONS:
            for index in range(24):
                writer.append_data(frame(direction, index, atlas_cell(source_paths[direction], index)))
    finally:
        writer.close()
    if not output.is_file() or output.stat().st_size <= 0:
        raise SystemExit(f"video writer produced no output: {output}")
    manifest = {
        "schema": 1,
        "role": "MICA C03 R17 native dynamic technical review video",
        "video": output.relative_to(ROOT).as_posix(),
        "video_sha256": sha256(output),
        "resolution": [WIDTH, HEIGHT],
        "fps": 24,
        "frame_count": len(DIRECTIONS) * 24,
        "directions": list(DIRECTIONS),
        "native_cell_resolution": [CELL, CELL],
        "upscale": False,
        "runtime_root": runtime.relative_to(ROOT).as_posix(),
        "dynamic_capture": True,
        "visual_gate": "HOLD_PENDING_PONYTAIL_AND_CHATGPT_WEB_REVIEW",
        "promotion": "UNREVIEWED_DO_NOT_PROMOTE",
    }
    manifest_path = output.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"video": manifest["video"], "sha256": manifest["video_sha256"], "resolution": manifest["resolution"], "frames": manifest["frame_count"], "manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
