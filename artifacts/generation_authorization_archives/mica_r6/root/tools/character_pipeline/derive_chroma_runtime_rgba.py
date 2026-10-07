#!/usr/bin/env python3
"""Derive RGBA from a preserved green master without repainting character art.

Only exact green and connected unmistakable chroma-green pixels are made
transparent. This tool is for characters whose reviewed costume contract
excludes chroma green; cyan and teal details do not satisfy the green-vs-blue
test. Every retained visible RGB pixel stays byte-identical. Closed background
holes are deliberately included.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def local(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    if path == ROOT or not path.is_relative_to(ROOT):
        raise SystemExit("project-local non-root path required")
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def background_mask(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = rgb.astype(np.int16)
    exact = np.all(rgb == np.asarray([0, 255, 0], dtype=np.uint8), axis=2)
    # Seed unmistakable bright chroma anywhere so closed holes between limbs
    # are included. Expand only inside a stricter green-hue family. This catches
    # dark antialiased halo such as [7,28,7] without deleting cyan/teal pixels
    # such as [46,198,189], whose blue channel stays close to green.
    bright_seed = ((values[:, :, 1] >= 64) &
                   (values[:, :, 1] - values[:, :, 0] >= 45) &
                   (values[:, :, 1] - values[:, :, 2] >= 45) &
                   (values[:, :, 1] * 4 >= values[:, :, 0] * 5) &
                   (values[:, :, 1] * 4 >= values[:, :, 2] * 5))
    chroma_family = ((values[:, :, 1] >= 12) &
                     (values[:, :, 1] - values[:, :, 0] >= 16) &
                     (values[:, :, 1] - values[:, :, 2] >= 16) &
                     (values[:, :, 1] * 4 >= values[:, :, 0] * 5) &
                     (values[:, :, 1] * 4 >= values[:, :, 2] * 5))
    background = exact | bright_seed
    height, width = background.shape
    # Only seed-boundary pixels can expand the connected chroma family. Keeping
    # the full solid-green field out of the Python queue avoids millions of
    # redundant entries on production-size masters while preserving closed
    # holes and antialiased edge traversal.
    non_background = ~background
    touches_non_background = np.zeros_like(background)
    touches_non_background[1:, :] |= non_background[:-1, :]
    touches_non_background[:-1, :] |= non_background[1:, :]
    touches_non_background[:, 1:] |= non_background[:, :-1]
    touches_non_background[:, :-1] |= non_background[:, 1:]
    frontier = background & touches_non_background
    queue: deque[tuple[int, int]] = deque(map(tuple, np.argwhere(frontier)))
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if (0 <= ny < height and 0 <= nx < width and chroma_family[ny, nx]
                    and not background[ny, nx]):
                background[ny, nx] = True
                queue.append((ny, nx))
    return background, exact


def derive(input_path: Path, output_path: Path) -> dict:
    rgb = np.asarray(Image.open(input_path).convert("RGB"), dtype=np.uint8)
    background, exact = background_mask(rgb)
    if not all(bool(background[y, x]) for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
        raise ValueError("CHROMA_BACKGROUND_CORNERS_REQUIRED")
    coverage = float(background.mean())
    if not 0.10 <= coverage < 0.98:
        raise ValueError(f"CHROMA_BACKGROUND_COVERAGE_FAIL:{coverage:.6f}")
    rgba = np.zeros((*rgb.shape[:2], 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = np.where(background, 0, 255).astype(np.uint8)
    rgba[background, :3] = 0
    Image.fromarray(rgba, "RGBA").save(output_path)
    visible = ~background
    if not np.array_equal(rgba[visible, :3], rgb[visible]):
        raise ValueError("VISIBLE_RGB_PIXELS_CHANGED")
    values = rgb.astype(np.int16)
    green_family = ((values[:, :, 1] >= 12) &
                    (values[:, :, 1] - values[:, :, 0] >= 16) &
                    (values[:, :, 1] - values[:, :, 2] >= 16) &
                    (values[:, :, 1] * 4 >= values[:, :, 0] * 5) &
                    (values[:, :, 1] * 4 >= values[:, :, 2] * 5))
    transparent = ~visible
    alpha_boundary = np.zeros_like(visible)
    alpha_boundary[1:, :] |= transparent[:-1, :]
    alpha_boundary[:-1, :] |= transparent[1:, :]
    alpha_boundary[:, 1:] |= transparent[:, :-1]
    alpha_boundary[:, :-1] |= transparent[:, 1:]
    residual = visible & green_family
    boundary_residual = residual & alpha_boundary
    return {
        "schema": 1,
        "operation": "exact-green plus connected chroma-green transparency under chroma-green-excluded costume contract",
        "input": input_path.relative_to(ROOT).as_posix(),
        "input_sha256": digest(input_path),
        "output": output_path.relative_to(ROOT).as_posix(),
        "output_sha256": digest(output_path),
        "native_size": [int(rgb.shape[1]), int(rgb.shape[0])],
        "transparent_pixels": int(background.sum()),
        "removed_strong_green_non_exact_pixels": int((background & ~exact).sum()),
        "visible_pixels": int(visible.sum()),
        "visible_rgb_byte_exact": True,
        "visible_strong_green_residual_pixels": int(residual.sum()),
        "visible_strong_green_alpha_boundary_residual_pixels": int(boundary_residual.sum()),
        "quality_verdict": "HOLD_VISUAL_EDGE_REVIEW"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--costume-excludes-chroma-green", action="store_true", required=True)
    args = parser.parse_args()
    source, output, qa = local(args.input), local(args.output), local(args.qa)
    if not source.is_file() or output == source or output.exists() or qa.exists():
        raise SystemExit("missing input or refusing overwrite/in-place derivation")
    output.parent.mkdir(parents=True, exist_ok=True)
    report = derive(source, output)
    qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
