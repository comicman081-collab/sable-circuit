#!/usr/bin/env python3
"""Replace only edge-connected bright neutral checker pixels with #00FF00.

This is a deterministic background conversion for a built-in ImageGen output
that painted a transparency checkerboard. It does not synthesize, repaint, or
inpaint character pixels. The immutable ImageGen input is preserved.
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


def inside_project(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _flood(candidate: np.ndarray, seeds: list[tuple[int, int]]) -> np.ndarray:
    height, width = candidate.shape
    selected = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for y, x in seeds:
        if candidate[y, x] and not selected[y, x]:
            selected[y, x] = True
            queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < height and 0 <= nx < width and candidate[ny, nx] and not selected[ny, nx]:
                selected[ny, nx] = True
                queue.append((ny, nx))
    return selected


def checker_background(rgb: np.ndarray) -> tuple[np.ndarray, list[dict]]:
    values = rgb.astype(np.int16)
    spread = values.max(axis=2) - values.min(axis=2)
    candidate = (values.min(axis=2) >= 185) & (spread <= 24)
    height, width = candidate.shape
    border_seeds = ([(0, x) for x in range(width)] + [(height - 1, x) for x in range(width)]
                    + [(y, 0) for y in range(height)] + [(y, width - 1) for y in range(height)])
    background = _flood(candidate, border_seeds)

    # Never guess that an enclosed bright-neutral component is background.
    # Costume lights and metallic highlights can be pixel-identical to a
    # painted checker.  The previous size-based heuristic deleted real MICA
    # forearm pixels.  Report every ambiguous component and fail closed.
    core = (values.min(axis=2) >= 235) & (spread <= 18) & ~background
    unseen = core.copy()
    ambiguous = []
    for y, x in zip(*np.where(core)):
        if not unseen[y, x]:
            continue
        component = _flood(core, [(int(y), int(x))])
        unseen[component] = False
        size = int(component.sum())
        if size >= 128:
            yy, xx = np.where(component)
            ambiguous.append({
                "pixels": size,
                "bbox_xyxy": [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())],
            })
    return background, ambiguous


def normalize(input_path: Path, output_path: Path, mask_path: Path) -> dict:
    rgb = np.asarray(Image.open(input_path).convert("RGB"), dtype=np.uint8)
    background, ambiguous = checker_background(rgb)
    coverage = float(background.mean())
    if not 0.50 <= coverage <= 0.94:
        raise ValueError(f"CHECKER_BACKGROUND_COVERAGE_FAIL:{coverage:.6f}")
    if not all(bool(background[y, x]) for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
        raise ValueError("CHECKER_BACKGROUND_CORNERS_NOT_CONNECTED")
    if ambiguous:
        raise ValueError("AMBIGUOUS_ENCLOSED_BRIGHT_COMPONENTS:" + json.dumps(ambiguous, separators=(",", ":")))
    normalized = rgb.copy()
    normalized[background] = GREEN
    mask = np.where(background, 0, 255).astype(np.uint8)
    if not np.array_equal(normalized[~background], rgb[~background]):
        raise ValueError("SUBJECT_PIXELS_CHANGED")
    Image.fromarray(normalized, "RGB").save(output_path)
    Image.fromarray(mask, "L").save(mask_path)
    return {
        "schema": 1,
        "operation": "edge-connected bright-neutral checker replacement only; no character pixel generation",
        "source_author": "built-in ImageGen",
        "input": input_path.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(input_path),
        "output": output_path.relative_to(ROOT).as_posix(),
        "output_sha256": sha256(output_path),
        "mask": mask_path.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(mask_path),
        "native_size": [int(rgb.shape[1]), int(rgb.shape[0])],
        "background_coverage": coverage,
        "changed_pixels": int(background.sum()),
        "accepted_enclosed_checker_pixels": 0,
        "ambiguous_enclosed_bright_components": [],
        "unchanged_subject_pixels": int((~background).sum()),
        "subject_pixels_byte_exact": True,
        "corners_exact_green": all(normalized[y, x].tolist() == [0, 255, 0] for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))),
        "visual_review_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()
    source = inside_project(args.input, "input")
    output = inside_project(args.output, "output")
    mask = inside_project(args.mask, "mask")
    qa = inside_project(args.qa, "qa")
    if not source.is_file():
        raise SystemExit(f"input missing: {source}")
    if output == source or any(path.exists() for path in (output, mask, qa)):
        raise SystemExit("refusing overwrite or in-place normalization")
    for path in (output, mask, qa):
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = normalize(source, output, mask)
    except Exception:
        for path in (output, mask):
            if path.exists():
                path.unlink()
        raise
    qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PAINTED_CHECKER_NORMALIZATION_HOLD_VISUAL_REVIEW=" + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
