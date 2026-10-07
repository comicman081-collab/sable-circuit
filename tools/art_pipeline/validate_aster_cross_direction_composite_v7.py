#!/usr/bin/env python3
"""Audit the existing ASTER V6 split assets for independent move/aim use.

This is deliberately a pre-promotion validator.  The original Composite Fire
V6 gate covered only matching lower/upper directions; a top-down shooter needs
velocity-selected legs and aim-selected upper art.  The audit composites every
8x8 direction pair, measures whether the aim upper overwrites the locked lower
costume, detects waist-band alpha holes, and emits a human-readable contact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
SAMPLE_MOVE_FRAME = 0
SAMPLE_UPPER_FRAME = 0
CONTACT_CELL = 192
LABEL_H = 28
OUT_DIR = ROOT / "artifacts" / "aster_cross_direction_composite_v7"
ASSET_ROOT = ROOT / "assets" / "units" / "operators" / "aster" / "composite_fire_v6"
MANIFEST_PATH = ASSET_ROOT / "ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cell(path: Path, frame: int) -> np.ndarray:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if rgba.shape[1] != CELL or rgba.shape[0] % CELL != 0:
        raise RuntimeError(f"invalid atlas: {path} {rgba.shape}")
    count = rgba.shape[0] // CELL
    if not 0 <= frame < count:
        raise RuntimeError(f"frame {frame} outside {count}: {path}")
    return rgba[frame * CELL : (frame + 1) * CELL].copy()


def alpha_composite(lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.asarray(
        Image.alpha_composite(Image.fromarray(lower, "RGBA"), Image.fromarray(upper, "RGBA")),
        dtype=np.uint8,
    )


def corridor_mask(start: list[float], end: list[float], radius: float = 15.0) -> np.ndarray:
    y, x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    a = np.asarray(start, dtype=np.float32)
    b = np.asarray(end, dtype=np.float32)
    segment = b - a
    denominator = max(float(np.dot(segment, segment)), 1e-6)
    t = np.clip(((x - a[0]) * segment[0] + (y - a[1]) * segment[1]) / denominator, 0.0, 1.0)
    closest_x = a[0] + t * segment[0]
    closest_y = a[1] + t * segment[1]
    return np.hypot(x - closest_x, y - closest_y) <= radius


def enclosed_hole_pixels(alpha: np.ndarray, split_y: float) -> int:
    visible = (alpha > 12).astype(np.uint8)
    band_top = max(0, int(round(split_y)) - 16)
    band_bottom = min(CELL, int(round(split_y)) + 22)
    band = visible[band_top:band_bottom]
    if not np.any(band):
        return band.size
    closed = cv2.morphologyEx(band, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return int(np.count_nonzero((closed > 0) & (band == 0)))


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    contact = Image.new(
        "RGBA",
        (CONTACT_CELL * len(DIRECTIONS), (CONTACT_CELL + LABEL_H) * len(DIRECTIONS)),
        (8, 15, 20, 255),
    )
    draw = ImageDraw.Draw(contact)
    records: list[dict[str, object]] = []
    failures: list[str] = []

    for row, lower_direction in enumerate(DIRECTIONS):
        lower_record = manifest["directions_output"][lower_direction]
        lower_path = ROOT / lower_record["layers"]["move_lower"]["output"]
        lower = load_cell(lower_path, SAMPLE_MOVE_FRAME)
        partition = lower_record["layers"]["move_lower"]["partition_frames"][SAMPLE_MOVE_FRAME]
        lock_y = float(partition["lower_costume_lock_y"])
        split_y = float(partition["split_y"])
        hard_lower = (lower[:, :, 3] > 8) & (np.arange(CELL)[:, None] >= lock_y)

        for column, upper_direction in enumerate(DIRECTIONS):
            upper_record = manifest["directions_output"][upper_direction]
            upper_path = ROOT / upper_record["layers"]["fire_upper"]["output"]
            upper = load_cell(upper_path, SAMPLE_UPPER_FRAME)
            composite = alpha_composite(lower, upper)
            corridor = manifest["weapon_corridors_384_cell"][upper_direction]
            allowed_weapon = corridor_mask(corridor["barrel_inner_xy"], corridor["muzzle_xy"])
            protected = hard_lower & ~allowed_weapon
            rgba_delta = np.max(
                np.abs(composite.astype(np.int16) - lower.astype(np.int16)), axis=2
            )
            overwritten = int(np.count_nonzero(protected & (rgba_delta > 3)))
            holes = enclosed_hole_pixels(composite[:, :, 3], split_y)
            same_direction = lower_direction == upper_direction
            passed = overwritten == 0 and holes <= 24
            if not passed:
                failures.append(
                    f"lower={lower_direction} upper={upper_direction} overwritten={overwritten} holes={holes}"
                )
            records.append(
                {
                    "lower_velocity_direction": lower_direction,
                    "upper_aim_direction": upper_direction,
                    "same_direction": same_direction,
                    "locked_lower_overwrite_pixels": overwritten,
                    "waist_band_hole_pixels": holes,
                    "gate": "PASS" if passed else "FAIL",
                }
            )
            thumb = Image.fromarray(composite, "RGBA").resize(
                (CONTACT_CELL, CONTACT_CELL), Image.Resampling.LANCZOS
            )
            x = column * CONTACT_CELL
            y = row * (CONTACT_CELL + LABEL_H)
            contact.alpha_composite(thumb, (x, y + LABEL_H))
            label_color = (80, 235, 180, 255) if passed else (255, 105, 90, 255)
            draw.rectangle((x, y, x + CONTACT_CELL - 1, y + LABEL_H - 1), fill=(3, 9, 13, 245))
            draw.text(
                (x + 5, y + 7),
                f"MOVE {lower_direction} | AIM {upper_direction} | {'PASS' if passed else 'FAIL'}",
                fill=label_color,
            )

    contact_path = OUT_DIR / "ASTER_V6_8X8_MOVE_AIM_CROSS_COMPOSITE_CONTACT.png"
    contact.save(contact_path, optimize=True)
    result = {
        "schema": 1,
        "purpose": "pre-promotion audit for lower=velocity and upper=aim split",
        "source_manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": sha256(MANIFEST_PATH),
        "sample_move_frame": SAMPLE_MOVE_FRAME,
        "sample_upper_frame": SAMPLE_UPPER_FRAME,
        "pairs": len(records),
        "passed_pairs": sum(record["gate"] == "PASS" for record in records),
        "failed_pairs": sum(record["gate"] == "FAIL" for record in records),
        "records": records,
        "failures": failures,
        "contact_sheet": contact_path.relative_to(ROOT).as_posix(),
        "contact_sha256": sha256(contact_path),
        "gate": "PASS" if not failures else "FAIL_HOLD",
        "note": "A metric pass is not a human visual pass; all 64 cells require review.",
    }
    result_path = OUT_DIR / "ASTER_V6_8X8_MOVE_AIM_CROSS_COMPOSITE_QA.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"ASTER_V6_CROSS_DIRECTION_COMPOSITE: {result['gate']} "
        f"pairs={result['passed_pairs']}/{result['pairs']} contact={contact_path}"
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
