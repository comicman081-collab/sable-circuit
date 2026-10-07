#!/usr/bin/env python3
"""Validate ASTER's current V4 12-key, eight-direction move review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
KEY_LITERAL = "'contact_a','down_a','push_a','passing_a','high_a','reach_a','contact_b','down_b','push_b','passing_b','high_b','reach_b'"


def atlas_path(direction: str) -> Path:
    return ROOT / f"assets/units/operators/aster/move_360_interpolated_v4/{direction}/ASTER_MOVE_{direction}_360_INTERPOLATED_V4_ATLAS.webp"


def main() -> int:
    html_path = ROOT / "art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html"
    html = html_path.read_text(encoding="utf-8")
    records = []
    failures = []
    for direction in DIRECTIONS:
        path = atlas_path(direction)
        if not path.is_file():
            failures.append(f"missing atlas {direction}: {path}")
            continue
        rgba = np.asarray(Image.open(path).convert("RGBA"))
        if rgba.shape != (4608, 384, 4):
            failures.append(f"wrong atlas dimensions {direction}: {rgba.shape}")
            continue
        frames = [rgba[index * 384:(index + 1) * 384] for index in range(12)]
        hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames]
        adjacent = [float(np.mean(np.abs(frames[index].astype(np.int16) - frames[(index + 1) % 12].astype(np.int16)))) for index in range(12)]
        unique = len(set(hashes))
        if unique != 12:
            failures.append(f"{direction} has only {unique} unique decoded frames")
        records.append({
            "direction": direction,
            "atlas": path.relative_to(ROOT).as_posix(),
            "resolution": [rgba.shape[1], rgba.shape[0]],
            "unique_decoded_frames": unique,
            "mean_adjacent_delta": round(float(np.mean(adjacent)), 4),
            "loop_seam_delta": round(adjacent[-1], 4),
        })
    html_checks = {
        "eight_direction_v4_path": "move_360_interpolated_v4/${d}" in html,
        "twelve_key_cycle": KEY_LITERAL in html,
        "continuous_temporal_blend": "ctx.globalAlpha=blend" in html and "if(state==='move')" in html,
        "legacy_e_override_removed": "d === 'E' ?" not in html,
    }
    failures.extend(f"HTML check failed: {name}" for name, passed in html_checks.items() if not passed)
    report = {
        "result": "PASS" if not failures else "FAIL",
        "html": html_path.relative_to(ROOT).as_posix(),
        "html_checks": html_checks,
        "atlases": records,
        "failures": failures,
    }
    output = ROOT / "art_src/pilot_v2/aster_v2/animation_360/move_360_interpolated_v4/ASTER_MOVE_360_INTERPOLATED_V4_QA.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_MOVE_360_INTERPOLATED_V4_QA=" + json.dumps(report, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
