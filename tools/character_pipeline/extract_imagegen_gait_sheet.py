#!/usr/bin/env python3
"""Deterministically split one approved 2x3 ImageGen gait sheet into source cells.

The production cell contract is 512×512.  ImageGen may return a wider
portrait sheet (for example 1280×1536) while retaining its six equal-height
cells.  In that case this tool takes a centered *lossless crop* from each
cell; it never resizes, repaints, or overwrites the immutable sheet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
COLS, ROWS = 2, 3


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--direction", required=True, type=str.upper, choices=("E", "SE", "S", "SW", "W", "NW", "N", "NE"))
    parser.add_argument("--start-index", type=int, required=True, choices=(0, 6))
    parser.add_argument("--art-prefix", default="ROOK_C02")
    parser.add_argument("--target-cell-size", type=int, default=512)
    args = parser.parse_args()
    source = project_path(args.input, "input")
    output_dir = project_path(args.output_dir, "output-dir")
    if not source.is_file():
        raise SystemExit(f"missing gait sheet: {source}")
    image = Image.open(source).convert("RGB")
    target_size = int(args.target_cell_size)
    if target_size != 512:
        raise SystemExit("gait source target cell size is fixed at 512px")
    if image.width % COLS or image.height % ROWS:
        raise SystemExit(f"gait sheet must divide evenly into a 2x3 grid, got {image.size}: {source}")
    cell_width, cell_height = image.width // COLS, image.height // ROWS
    if cell_width < target_size or cell_height < target_size:
        raise SystemExit(
            f"gait sheet cells must contain a native {target_size}x{target_size} crop, got "
            f"{cell_width}x{cell_height}: {source}"
        )
    crop_offset_x = (cell_width - target_size) // 2
    crop_offset_y = (cell_height - target_size) // 2
    outputs = [output_dir / f"{args.art_prefix}_{args.direction}_GAIT_F{args.start_index + index:02d}_IMAGEGEN_GREEN.png" for index in range(COLS * ROWS)]
    manifest = output_dir / f"{args.art_prefix}_{args.direction}_GAIT_SHEET_{'A' if args.start_index == 0 else 'B'}_EXTRACTION.json"
    if any(path.exists() for path in [*outputs, manifest]):
        raise SystemExit("refusing to overwrite extracted gait source or manifest")
    output_dir.mkdir(parents=True, exist_ok=True)
    cells = []
    for index, output in enumerate(outputs):
        row, col = divmod(index, COLS)
        cell_box = (col * cell_width, row * cell_height, (col + 1) * cell_width, (row + 1) * cell_height)
        box = (
            cell_box[0] + crop_offset_x,
            cell_box[1] + crop_offset_y,
            cell_box[0] + crop_offset_x + target_size,
            cell_box[1] + crop_offset_y + target_size,
        )
        image.crop(box).save(output)
        cells.append({
            "gait_source_index": args.start_index + index,
            "source_cell_xyxy": list(cell_box),
            "crop_xyxy": list(box),
            "output": output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(output),
        })
    evidence = {
        "schema": 1,
        "role": "Lossless deterministic 2x3 ImageGen gait-sheet extraction; optional centered native cell crop without resampling",
        "input": source.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(source),
        "input_resolution": list(image.size),
        "grid": {
            "columns": COLS,
            "rows": ROWS,
            "source_cell_resolution": [cell_width, cell_height],
            "output_cell_resolution": [target_size, target_size],
            "center_crop_offset_xy": [crop_offset_x, crop_offset_y],
            "resampled": False,
        },
        "direction": args.direction,
        "art_prefix": args.art_prefix,
        "cells": cells,
        "pass": True,
    }
    manifest.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("IMAGEGEN_GAIT_SHEET_EXTRACT_PASS=" + json.dumps(evidence, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
