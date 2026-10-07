#!/usr/bin/env python3
"""Per-frame torso registration for Motion Studio walk atlases (no pixel change).

The Studio builder places every walk frame by its hip column, so where a frame's
lean differs the upper body jumps back and forth between frames: ASTER's E walk
lurches 4-7 on-map px per frame, which read as an awkward gait. This tool measures
each native atlas cell's torso column (mean of the top-45 % body alpha centroid and
the top-12 % head centroid) and records the x shift that puts it on the cycle mean.
MotionLabCharacterRuntime moves the sprite by that shift while it shows the frame;
atlas bytes, source masters and muzzle anchors are untouched. Every row is bound to
the frame's source master SHA-256 from profile.json, and the runtime ignores a row
whose source no longer matches.

    python tools/character_pipeline/build_walk_torso_registration.py          # write
    python tools/character_pipeline/build_walk_torso_registration.py --check  # stale?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "motion_lab_v1/public"
OUTPUT = ROOT / "data/art_profiles/motion_lab_walk_registration.json"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
# Only ASTER is registered: MICA and ROOK keep their accepted hip placement.
CHARACTERS = ("aster",)
ALPHA_OPAQUE = 128


def torso_x(cell: np.ndarray) -> float:
    mask = cell[:, :, 3] > ALPHA_OPAQUE
    ys, xs = np.where(mask)
    top, height = int(ys.min()), int(ys.max()) - int(ys.min()) + 1
    head = np.where(mask[top:top + int(height * 0.12), :])[1]
    upper = np.where(mask[top:top + int(height * 0.45), :])[1]
    return (float(head.mean()) + float(upper.mean())) * 0.5


def build() -> dict:
    characters = {}
    for character in CHARACTERS:
        profile = json.loads((PUBLIC / "assets/atlas" / character / "profile.json").read_text(encoding="utf-8"))
        walk = {}
        for direction in DIRECTIONS:
            clip = profile["views"][direction]["walk"]
            atlas = np.asarray(Image.open(PUBLIC / clip["image"]).convert("RGBA"))
            cell_w, cell_h = clip["cell"]
            columns = clip["columns"]
            columns_x = []
            for frame in range(clip["frames"]):
                x0 = (frame % columns) * cell_w
                y0 = (frame // columns) * cell_h
                columns_x.append(torso_x(atlas[y0:y0 + cell_h, x0:x0 + cell_w]))
            mean = sum(columns_x) / len(columns_x)
            walk[direction] = [
                {"source_sha256": source["sha256"], "offset_x": round(mean - value, 2)}
                for source, value in zip(clip["sources"], columns_x)
            ]
        characters[character] = {"walk": walk}
    return {
        "schema": 1,
        "generator": "tools/character_pipeline/build_walk_torso_registration.py",
        "units": "atlas cell px (the profile's native cell), added to the sprite's x while that walk frame shows",
        "scope": "Runtime placement only; atlas pixels, source masters and muzzle anchors are unchanged. A row applies only while its frame's profile source SHA-256 matches.",
        "characters": characters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if the stored file differs from a fresh measurement")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2) + "\n"
    if args.check:
        stored = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if stored != text:
            print("WALK_TORSO_REGISTRATION STALE: rerun without --check")
            return 1
        print("WALK_TORSO_REGISTRATION PASS")
        return 0
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
