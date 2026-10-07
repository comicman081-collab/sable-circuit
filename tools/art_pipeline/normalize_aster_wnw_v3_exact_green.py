#!/usr/bin/env python3
"""Normalize the WNW V3 ImageGen chroma master without altering the subject.

The ImageGen composition is authoritative.  This deterministic post-process
only converts border-connected green and sufficiently large enclosed green
negative-space components to the project chroma key (#00FF00).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v2/"
    "fire16_no_shoulder/current/WNW/"
    "ASTER_FIRE_WNW_DIRECTION_AIM_MASTER_IMAGEGEN_V4_NO_SHOULDER_GREEN.png"
)
WORK = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v2/"
    "fire16_no_shoulder/_work/wnw_v5_exact_green"
)
OUTPUT = WORK / "ASTER_FIRE_WNW_DIRECTION_AIM_MASTER_IMAGEGEN_V5_NO_SHOULDER_EXACT_GREEN.png"
REPORT = WORK / "ASTER_FIRE_WNW_IMAGEGEN_V5_EXACT_GREEN_REPORT.json"
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> int:
    if not SOURCE.is_file() or OUTPUT.exists() or REPORT.exists():
        raise SystemExit("source missing or normalized output already exists")
    rgb = np.asarray(Image.open(SOURCE).convert("RGB"), dtype=np.uint8).copy()
    values = rgb.astype(np.int16)
    r, g, b = values[:, :, 0], values[:, :, 1], values[:, :, 2]

    # Loose pixels include green antialias/spill around the flat-field region.
    loose = (
        (g >= 70)
        & ((g - r) >= 25)
        & ((g - b) >= 25)
        & (r <= 155)
        & (b <= 155)
    )
    # Core pixels match the generated green field, not cyan cloth or gold trim.
    core = (
        (g >= 135)
        & (g <= 242)
        & (r <= 100)
        & (b <= 110)
        & ((g - r) >= 70)
        & ((g - b) >= 70)
    )
    count, labels, stats, _ = cv2.connectedComponentsWithStats(loose.astype(np.uint8), 8)
    border_labels = set(
        np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))).tolist()
    )
    border_labels.discard(0)
    background = np.isin(labels, list(border_labels))
    enclosed = []
    preserved = []
    for index in range(1, count):
        if index in border_labels:
            continue
        component = labels == index
        area = int(stats[index, cv2.CC_STAT_AREA])
        core_count = int(np.count_nonzero(core & component))
        core_fraction = core_count / max(area, 1)
        cx = float(stats[index, cv2.CC_STAT_LEFT] + stats[index, cv2.CC_STAT_WIDTH] / 2)
        cy = float(stats[index, cv2.CC_STAT_TOP] + stats[index, cv2.CC_STAT_HEIGHT] / 2)
        p0 = np.asarray((130.0, 60.0)); p1 = np.asarray((736.0, 328.0)); point = np.asarray((cx, cy))
        axis_distance = float(abs(np.cross(p1 - p0, point - p0)) / np.linalg.norm(p1 - p0))
        eye_roi = 740 <= cx <= 795 and 245 <= cy <= 275
        weapon_negative_space = cx <= 760 and cy <= 350 and axis_distance <= 75 and not eye_roi
        # Large enclosed field islands plus every green component inside the
        # rifle corridor are background. The explicit eye ROI preserves the
        # character's green irises.
        if weapon_negative_space or (40 <= area <= 20000 and core_count >= 16 and core_fraction >= 0.35):
            background |= component
            enclosed.append({"label": index, "area": area, "core_count": core_count, "weapon_corridor": weapon_negative_space})
        else:
            preserved.append({"label": index, "area": area, "core_count": core_count})

    normalized = rgb.copy()
    normalized[background] = EXACT_GREEN
    WORK.mkdir(parents=True)
    Image.fromarray(normalized, "RGB").save(OUTPUT, "PNG", optimize=True)
    exact_count = int(np.count_nonzero(np.all(normalized == EXACT_GREEN, axis=2)))
    report = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "operation": "deterministic chroma normalization only; ImageGen subject pixels preserved",
        "source": {"path": rel(SOURCE), "sha256": sha256(SOURCE)},
        "output": {"path": rel(OUTPUT), "sha256": sha256(OUTPUT), "resolution": list(Image.open(OUTPUT).size)},
        "background_pixels_normalized": int(np.count_nonzero(background)),
        "exact_green_pixels": exact_count,
        "border_background_components": len(border_labels),
        "enclosed_background_components": enclosed,
        "preserved_green_components": preserved,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": rel(OUTPUT), "report": rel(REPORT), "exact_green_pixels": exact_count, "enclosed": enclosed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
