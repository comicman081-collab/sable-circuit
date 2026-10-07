#!/usr/bin/env python3
"""Normalize a green-matted SABLE source/mask pair onto a fixed square canvas.

This intentionally does not invent or redraw artwork.  It only letterboxes a
validated source pair with exact #00FF00 so Blender receives identical canvas
geometry for every animation key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


GREEN = np.array((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--mask", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--output-mask", required=True, type=Path)
    parser.add_argument("--qa", required=True, type=Path)
    parser.add_argument("--canvas", type=int, default=1254)
    args = parser.parse_args()
    if not args.source.is_file() or not args.mask.is_file():
        raise SystemExit("source/mask pair is unavailable")
    if args.output.exists() or args.output_mask.exists() or args.qa.exists():
        raise SystemExit("refusing to overwrite a normalized sprite artifact")

    rgb = Image.open(args.source).convert("RGB")
    mask = Image.open(args.mask).convert("L")
    if rgb.size != mask.size:
        raise SystemExit(f"source/mask size mismatch: {rgb.size} vs {mask.size}")
    width, height = rgb.size
    scale = min(args.canvas / width, args.canvas / height)
    target = (round(width * scale), round(height * scale))

    rgb_array = np.asarray(rgb, dtype=np.float32)
    alpha = np.asarray(mask, dtype=np.float32) / 255.0
    foreground = rgb_array * alpha[:, :, None]
    resized_foreground = np.asarray(
        Image.fromarray(np.clip(foreground, 0, 255).astype(np.uint8), "RGB").resize(target, Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    resized_alpha = np.asarray(mask.resize(target, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    binary_alpha = resized_alpha >= 0.5
    unpremultiplied = np.zeros_like(resized_foreground, dtype=np.uint8)
    np.divide(
        resized_foreground,
        np.maximum(resized_alpha[:, :, None], 1.0 / 255.0),
        out=unpremultiplied,
        where=resized_alpha[:, :, None] > 0,
        casting="unsafe",
    )
    canvas_rgb = np.empty((args.canvas, args.canvas, 3), dtype=np.uint8)
    canvas_rgb[:, :] = GREEN
    canvas_mask = np.zeros((args.canvas, args.canvas), dtype=np.uint8)
    left = (args.canvas - target[0]) // 2
    top = (args.canvas - target[1]) // 2
    window = canvas_rgb[top : top + target[1], left : left + target[0]]
    window[binary_alpha] = unpremultiplied[binary_alpha]
    canvas_mask[top : top + target[1], left : left + target[0]][binary_alpha] = 255
    if not np.all(canvas_rgb[canvas_mask == 0] == GREEN):
        raise SystemExit("exact green matte check failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output_mask.parent.mkdir(parents=True, exist_ok=True)
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(canvas_rgb, "RGB").save(args.output)
    Image.fromarray(canvas_mask, "L").save(args.output_mask)
    qa = {
        "pass": True,
        "operation": "non-generative letterbox normalization",
        "source": args.source.as_posix(),
        "input_resolution": [width, height],
        "output": args.output.as_posix(),
        "mask": args.output_mask.as_posix(),
        "canvas": [args.canvas, args.canvas],
        "scale": scale,
        "placement_xy": [left, top],
        "exact_green_outside_ratio": 1.0,
        "output_sha256": sha256(args.output),
        "mask_sha256": sha256(args.output_mask),
    }
    args.qa.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NORMALIZE_GREEN_SPRITE_CANVAS_PASS=" + json.dumps(qa, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
