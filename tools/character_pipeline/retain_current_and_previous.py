#!/usr/bin/env python3
"""Retain one promoted motion candidate and exactly one prior candidate."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
import motion_harness


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = ("idle", "move", "fire")


def project_dir(value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} escaped project root: {resolved}") from exc
    if not resolved.is_dir():
        raise SystemExit(f"missing {label}: {resolved}")
    return resolved


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--previous-candidate", type=Path, required=True)
    parser.add_argument("--duplicate-current-candidate", type=Path, required=True)
    args = parser.parse_args()
    current = project_dir(args.current, "current")
    previous = project_dir(args.previous, "previous")
    previous_candidate = project_dir(args.previous_candidate, "previous candidate")
    duplicate = project_dir(args.duplicate_current_candidate, "duplicate current candidate")
    if any(previous.iterdir()):
        raise SystemExit(f"refusing to replace non-empty previous candidate: {previous}")
    for direction in DIRECTIONS:
        for state in STATES:
            promoted = current / direction / f"{state}_green.png"
            staged = duplicate / direction / f"{state}_green.png"
            if not promoted.is_file() or not staged.is_file() or digest(promoted) != digest(staged):
                raise SystemExit(f"duplicate verification failed: {direction}/{state}")
    targets = [current, previous, previous_candidate, duplicate]
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(targets) for b in targets[i + 1:]):
        raise SystemExit("retention targets must not overlap")
    motion_harness.quarantine(previous, "empty retention slot preserved")
    previous_candidate.replace(previous)
    motion_harness.quarantine(duplicate, "duplicate atlas but potentially distinct provenance/QA; no disposal")
    print("RETAIN_CURRENT_AND_PREVIOUS_QUARANTINED_NO_DISPOSAL")
    print(f"CURRENT={current.relative_to(ROOT).as_posix()}")
    print(f"PREVIOUS={previous.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
