#!/usr/bin/env python3
"""Reject ROOK sprite atlases that only bob, reuse gait frames, or hide a leg jump.

This is a structural guard, not a visual-art PASS.  It checks decoded lower-body
pixels because the prior failure preserved the upper body while only swapping two
whole-body images.  A Ponytail Full visual review and native 1080p dynamic
capture remain mandatory after this validator passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384


def project_path(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"atlas root must remain inside project: {path}") from exc
    return path


def lower_hashes(atlas: Path, frames: int) -> list[str]:
    image = Image.open(atlas).convert("RGBA")
    if image.size != (CELL, CELL * frames):
        raise SystemExit(f"unexpected atlas size {image.size} for {atlas}; expected {(CELL, CELL * frames)}")
    # Hip-and-leg region only: upper-body recoil may overlap the waist seam,
    # but it must never masquerade as a gait or change a planted foot.
    lower_top = int(CELL * 0.60)
    return [
        hashlib.sha256(image.crop((0, frame * CELL + lower_top, CELL, (frame + 1) * CELL)).tobytes()).hexdigest()
        for frame in range(frames)
    ]


def longest_repeat(values: list[str]) -> int:
    largest = run = 0
    previous = None
    for value in values:
        run = run + 1 if value == previous else 1
        previous = value
        largest = max(largest, run)
    return largest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="directory containing E..NE state atlas directories")
    parser.add_argument("--suffix", default=".png", help="state file suffix, e.g. _green.png before runtime promotion")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    atlas_root = project_path(args.root)
    report_path = project_path(args.report)
    if report_path.exists():
        raise SystemExit(f"refusing to overwrite report: {report_path}")

    evidence: dict[str, dict[str, object]] = {}
    failures: list[str] = []
    for direction in DIRECTIONS:
        move = lower_hashes(atlas_root / direction / f"move{args.suffix}", 24)
        idle = lower_hashes(atlas_root / direction / f"idle{args.suffix}", 4)
        fire = lower_hashes(atlas_root / direction / f"fire{args.suffix}", 6)
        unique_move = len(set(move))
        max_run = longest_repeat(move)
        idle_unique = len(set(idle))
        fire_unique = len(set(fire))
        direction_pass = unique_move >= 8 and max_run <= 2 and idle_unique == 1 and fire_unique == 1
        evidence[direction] = {
            "move_lower_body_unique_frames": unique_move,
            "move_max_consecutive_identical_lower_frames": max_run,
            "idle_lower_body_unique_frames": idle_unique,
            "fire_lower_body_unique_frames": fire_unique,
            "pass": direction_pass,
        }
        if not direction_pass:
            failures.append(direction)
    report = {
        "schema": 1,
        "role": "ROOK C02 gait structural gate; not a visual-art approval",
        "atlas_root": atlas_root.relative_to(ROOT).as_posix(),
        "atlas_suffix": args.suffix,
        "requirements": {
            "move_lower_body_unique_frames_min": 8,
            "move_max_consecutive_identical_lower_frames_max": 2,
            "idle_lower_body_unique_frames_exact": 1,
            "fire_lower_body_unique_frames_exact": 1,
        },
        "directions": evidence,
        "pass": not failures,
        "failures": failures,
        "next_gate": "Ponytail Full temporal review plus 1920x1080 dynamic capture",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ROOK_GAIT_CONTRACT_" + ("PASS=" if report["pass"] else "FAIL=") + json.dumps(report, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
