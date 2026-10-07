#!/usr/bin/env python3
"""Derive non-destructive Blender root translations for full-body gait art.

The pose sheets are immutable ImageGen source art.  This tool never crops or
rewrites them: it records a per-pose translation that Blender applies to the
whole cutout plane.  The correlation deliberately sees only the head, torso,
and pelvis band, so a stepping boot cannot pull the character root sideways.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.signal import correlate2d


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
GAIT_POSES = 12
PLANTED_POSE_INDEX = 10
# The lower legs must not influence root placement.  This band still contains
# enough silhouette detail (head, weapon, torso, hips) for stable alignment.
ROOT_BAND = (40, 48, 464, 318)  # x0, y0, x1, y1 in native 512px source cells
MAX_X_SHIFT = 96
MAX_Y_SHIFT = 48


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle-sources", type=Path, required=True)
    parser.add_argument("--art-prefix", required=True)
    parser.add_argument("--gait-version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_mask(cycle_root: Path, art_prefix: str, gait_version: str, direction: str, index: int) -> Path:
    candidate = cycle_root / f"candidate_{art_prefix.lower()}_walk_{direction.lower()}_{gait_version}_real_gait" / "normalized"
    path = candidate / f"{art_prefix}_{direction}_GAIT_F{index:02d}_IMAGEGEN_GREEN_MASK.png"
    if not path.is_file():
        raise SystemExit(f"missing native gait matte: {path}")
    qa = candidate / f"{art_prefix}_{direction}_GAIT_F{index:02d}_IMAGEGEN_GREEN_NORMALIZATION_QA.json"
    if not qa.is_file():
        raise SystemExit(f"missing source normalization evidence: {qa}")
    evidence = json.loads(qa.read_text(encoding="utf-8"))
    if evidence.get("pass") is not True or evidence.get("generated_pixels_modified") is not False:
        raise SystemExit(f"source normalization is not immutable-safe: {qa}")
    return path


def mask_band(path: Path) -> np.ndarray:
    mask = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
    if mask.shape != (512, 512):
        raise SystemExit(f"root registration requires a native 512x512 matte: {path}")
    x0, y0, x1, y1 = ROOT_BAND
    # Binary alpha keeps the correlation deterministic and resilient to
    # antialiasing along source edges.
    return (mask[y0:y1, x0:x1] >= 128).astype(np.float32)


def translation_to_reference(reference: np.ndarray, source: np.ndarray) -> tuple[int, int, float]:
    """Return the native-pixel translation to place source on reference.

    ``correlate2d(reference, source)`` has the desired sign convention: a
    source positioned left/up of the reference yields a positive x/y
    translation.  The positive y is an image-coordinate value (downscreen),
    converted to Blender's y-up space by the renderer.
    """
    # 4px coarse phase is fast and prevents fine matching from wandering to a
    # weapon/arm feature.  Search the immediate native neighbourhood to keep
    # exact pixel placement without changing the art itself.
    coarse_ref = reference[::4, ::4]
    coarse_src = source[::4, ::4]
    correlation = correlate2d(coarse_ref, coarse_src, mode="full")
    max_index = np.unravel_index(int(np.argmax(correlation)), correlation.shape)
    coarse_y = int(max_index[0] - (coarse_src.shape[0] - 1)) * 4
    coarse_x = int(max_index[1] - (coarse_src.shape[1] - 1)) * 4
    best: tuple[int, int, float] | None = None
    for y_shift in range(coarse_y - 5, coarse_y + 6):
        if abs(y_shift) > MAX_Y_SHIFT:
            continue
        for x_shift in range(coarse_x - 5, coarse_x + 6):
            if abs(x_shift) > MAX_X_SHIFT:
                continue
            # Compare only the overlapping root band after an integer shift.
            y0 = max(0, y_shift)
            y1 = min(reference.shape[0], reference.shape[0] + y_shift)
            x0 = max(0, x_shift)
            x1 = min(reference.shape[1], reference.shape[1] + x_shift)
            if y1 <= y0 or x1 <= x0:
                continue
            ref_crop = reference[y0:y1, x0:x1]
            src_crop = source[y0 - y_shift:y1 - y_shift, x0 - x_shift:x1 - x_shift]
            union = float(np.logical_or(ref_crop, src_crop).sum())
            score = 0.0 if union == 0.0 else float(np.logical_and(ref_crop, src_crop).sum()) / union
            candidate = (x_shift, y_shift, round(score, 6))
            if best is None or candidate[2] > best[2] or (candidate[2] == best[2] and abs(candidate[0]) + abs(candidate[1]) < abs(best[0]) + abs(best[1])):
                best = candidate
    if best is None:
        raise SystemExit("unable to derive a bounded root translation")
    return best


def main() -> int:
    args = parse_args()
    cycle_root = project_path(args.cycle_sources, "cycle sources")
    output = project_path(args.output, "root registration output")
    if output.exists():
        raise SystemExit(f"refusing to overwrite root registration: {output}")
    rows: dict[str, dict] = {}
    for direction in DIRECTIONS:
        masks = [source_mask(cycle_root, args.art_prefix, args.gait_version, direction, index) for index in range(GAIT_POSES)]
        reference = mask_band(masks[PLANTED_POSE_INDEX])
        frames: list[dict] = []
        for index, path in enumerate(masks):
            if index == PLANTED_POSE_INDEX:
                x_shift, y_shift, score = 0, 0, 1.0
            else:
                x_shift, y_shift, score = translation_to_reference(reference, mask_band(path))
            frames.append({
                "index": index,
                "translation_pixels": [x_shift, y_shift],
                "root_band_iou": score,
                "mask": path.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(path),
            })
        rows[direction] = {"reference_pose_index": PLANTED_POSE_INDEX, "frames": frames}
    payload = {
        "schema": 1,
        "role": "Immutable ImageGen full-body gait source root-registration for Blender plane transforms",
        "art_prefix": args.art_prefix,
        "gait_version": args.gait_version,
        "source_art_modified": False,
        "coordinate_system": "translation_pixels is [x right, y down] in native source-image pixels; Blender converts y to its y-up plane coordinate",
        "root_band": {"xyxy": list(ROOT_BAND), "purpose": "head torso pelvis correlation only; excludes stepping feet"},
        "limits": {"max_abs_x_pixels": MAX_X_SHIFT, "max_abs_y_pixels": MAX_Y_SHIFT},
        "directions": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("GAIT_ROOT_REGISTRATION_PASS=" + json.dumps({"output": output.relative_to(ROOT).as_posix(), "directions": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
