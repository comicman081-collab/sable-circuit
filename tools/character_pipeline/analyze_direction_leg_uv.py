#!/usr/bin/env python3
"""Report horizontal subject runs at lower-body UV bands for cutout rig tuning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def runs(active: np.ndarray) -> list[list[float]]:
    result: list[list[float]] = []
    start = None
    for index, value in enumerate([*active.tolist(), False]):
        if value and start is None:
            start = index
        elif not value and start is not None:
            if index - start >= 3:
                result.append([start / len(active), (index - 1) / len(active), (start + index - 1) / (2 * len(active))])
            start = None
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_root = (ROOT / args.root).resolve()
    output = (ROOT / args.output).resolve()
    output.relative_to(ROOT)
    report: dict[str, object] = {}
    for direction in DIRECTIONS:
        path = source_root / f"{args.prefix}_{direction}_IMAGEGEN_MASK.png"
        mask = np.asarray(Image.open(path).convert("L")) >= 128
        height, width = mask.shape
        bands: dict[str, object] = {}
        for name, v, half in (("ankle", 0.10, 0.035), ("knee", 0.33, 0.04), ("hip", 0.52, 0.035)):
            y0 = max(0, int(height * (1.0 - v - half)))
            y1 = min(height, int(height * (1.0 - v + half)))
            occupancy = mask[y0:y1].mean(axis=0)
            bands[name] = {"v": v, "runs": runs(occupancy >= 0.22)}
        report[direction] = {"mask": path.relative_to(ROOT).as_posix(), "resolution": [width, height], "bands": bands}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
