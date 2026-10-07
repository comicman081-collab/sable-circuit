#!/usr/bin/env python3
"""Guard a full-body move atlas against held-raster gait regressions.

The R17 pose-switch candidate intentionally exposed a failure mode that the
schema/runtime checks could not see: a 24-frame atlas can be technically
complete while displaying the same raster for several consecutive samples.
This project-local check is a static pre-promotion guard.  It never edits the
source atlas and does not claim to replace Blender+UAL or native video review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
FRAMES = 24
MAX_EXACT_HOLD = 2


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {path}") from exc
    return path


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def frame_hashes(atlas_path: Path) -> tuple[list[str], np.ndarray]:
    with Image.open(atlas_path) as image:
        if image.mode != "RGBA" or image.size != (CELL, CELL * FRAMES):
            raise SystemExit(f"expected 384x9216 RGBA move atlas: {atlas_path} {image.mode} {image.size}")
        pixels = np.asarray(image, dtype=np.uint8).reshape(FRAMES, CELL, CELL, 4)
    hashes = [digest_bytes(frame.tobytes()) for frame in pixels]
    return hashes, pixels


def run_length(values: list[bool]) -> int:
    best = current = 1
    for same in values:
        current = current + 1 if same else 1
        best = max(best, current)
    return best


def inspect_direction(direction: str, atlas_path: Path) -> dict[str, object]:
    hashes, pixels = frame_hashes(atlas_path)
    exact_pairs = [index for index in range(1, FRAMES) if hashes[index] == hashes[index - 1]]
    duplicate_runs = run_length([hashes[index] == hashes[index - 1] for index in range(1, FRAMES)])
    changed_pixels = [
        int(np.count_nonzero(np.any(pixels[index] != pixels[index - 1], axis=2)))
        for index in range(1, FRAMES)
    ]
    changed_ratio = [value / float(CELL * CELL) for value in changed_pixels]
    return {
        "direction": direction,
        "atlas": atlas_path.relative_to(ROOT).as_posix(),
        "frame_count": FRAMES,
        "unique_frame_count": len(set(hashes)),
        "exact_duplicate_pairs": exact_pairs,
        "exact_duplicate_pair_count": len(exact_pairs),
        "max_exact_hold_run": duplicate_runs,
        "changed_pixel_ratio_min": min(changed_ratio),
        "changed_pixel_ratio_max": max(changed_ratio),
        "changed_pixel_ratio_mean": sum(changed_ratio) / len(changed_ratio),
        "gate": "FAIL_EXACT_HELD_RASTER" if duplicate_runs > MAX_EXACT_HOLD else "PASS_STATIC_NO_LONG_EXACT_HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True, help="project-local runtime root containing DIR/move.png")
    parser.add_argument("--output", type=Path, required=True, help="new project-local JSON report")
    args = parser.parse_args()
    runtime = project_path(args.runtime, "runtime")
    output = project_path(args.output, "output")
    if output.exists():
        raise SystemExit(f"refusing to overwrite report: {output}")
    rows = [inspect_direction(direction, runtime / direction / "move.png") for direction in DIRECTIONS]
    failed = [row["direction"] for row in rows if row["gate"] != "PASS_STATIC_NO_LONG_EXACT_HOLD"]
    report = {
        "schema": 1,
        "role": "static anti-held-raster gait guard",
        "runtime_root": runtime.relative_to(ROOT).as_posix(),
        "directions": rows,
        "max_exact_hold_run_allowed": MAX_EXACT_HOLD,
        "overall_gate": "FAIL_NOT_PROMOTABLE" if failed else "PASS_STATIC_NO_LONG_EXACT_HOLD",
        "failed_directions": failed,
        "visual_review_required": True,
        "note": "A static PASS never replaces Blender+UAL temporal review or native 1920x1080 playback.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall_gate": report["overall_gate"], "failed_directions": failed, "output": output.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
