#!/usr/bin/env python3
"""Normalize an ImageGen green backdrop without redrawing the source art.

Only green-dominant pixels connected to the canvas edge are replaced by exact
``#00FF00``. The subject pixels remain untouched; this is deterministic matte
normalization, not local image generation or visual repair.
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
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def project_path(value: Path, label: str) -> Path:
    resolved = value.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edge_connected_background(rgb: np.ndarray) -> tuple[np.ndarray, list[int]]:
    height, width, _ = rgb.shape
    edge = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]), axis=0)
    median = np.median(edge, axis=0).astype(np.int16)
    values = rgb.astype(np.int16)
    green_dominant = (values[:, :, 1] >= values[:, :, 0] + 80) & (values[:, :, 1] >= values[:, :, 2] + 80)
    near_edge_green = np.max(np.abs(values - median), axis=2) <= 48
    candidate = green_dominant & near_edge_green
    background = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        if candidate[0, x]:
            background[0, x] = True; queue.append((0, x))
        if candidate[height - 1, x] and not background[height - 1, x]:
            background[height - 1, x] = True; queue.append((height - 1, x))
    for y in range(height):
        if candidate[y, 0] and not background[y, 0]:
            background[y, 0] = True; queue.append((y, 0))
        if candidate[y, width - 1] and not background[y, width - 1]:
            background[y, width - 1] = True; queue.append((y, width - 1))
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < height and 0 <= nx < width and candidate[ny, nx] and not background[ny, nx]:
                background[ny, nx] = True
                queue.append((ny, nx))
    return background, [int(value) for value in median]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()
    for label in ["input", "output", "mask", "qa"]:
        setattr(args, label, project_path(getattr(args, label), label))
    if not args.input.is_file():
        raise SystemExit(f"input missing: {args.input}")
    if any(path.exists() for path in [args.output, args.mask, args.qa]):
        raise SystemExit("refusing to overwrite normalized source artifacts")
    rgb = np.asarray(Image.open(args.input).convert("RGB"))
    background, edge_median = edge_connected_background(rgb)
    coverage = float(background.mean())
    if not 0.10 <= coverage < 0.98:
        raise SystemExit(f"CHROMA_BACKGROUND_FAIL coverage={coverage:.6f}")
    normalized = rgb.copy()
    normalized[background] = GREEN
    mask = np.where(background, 0, 255).astype(np.uint8)
    if not np.all(normalized[background] == GREEN):
        raise SystemExit("EXACT_GREEN_NORMALIZATION_FAIL")
    for path in [args.output, args.mask, args.qa]:
        path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(normalized, mode="RGB").save(args.output)
    Image.fromarray(mask, mode="L").save(args.mask)
    report = {
        "schema": 1,
        "operation": "edge-connected green matte normalization only; no source-art redraw",
        "source_author": "built-in ImageGen",
        "input": args.input.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(args.input),
        "output": args.output.relative_to(ROOT).as_posix(),
        "output_sha256": sha256(args.output),
        "mask": args.mask.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(args.mask),
        "input_resolution": [int(rgb.shape[1]), int(rgb.shape[0])],
        "edge_median_rgb": edge_median,
        "exact_green_rgb": GREEN.tolist(),
        "edge_connected_background_coverage": coverage,
        "alpha_ready": True
    }
    args.qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("IMAGEGEN_CHROMA_NORMALIZATION_PASS=" + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
