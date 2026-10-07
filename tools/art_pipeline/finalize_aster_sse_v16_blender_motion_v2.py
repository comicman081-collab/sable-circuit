#!/usr/bin/env python3
"""Finalize the seam-free ASTER SSE V16 full-pose Blender/UAL V2."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

import finalize_aster_sse_v16_blender_motion_v1 as base


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_blender_v2"
)
MANIFEST = PACKAGE / (
    "blender_scene/"
    "ASTER_FIRE_SSE_V16_FULL_POSE_67_5_UAL_MOTION_V2_MANIFEST.json"
)
EXPECTED_MANIFEST_SHA256 = "b4f897a6a86175b687380e0a02002d29eddd0fd3abe7674d6d86fda26c48a11c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def v2_matte_mask(rgb: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    background, report = base._v1_matte_mask(rgb)
    values = rgb.astype(np.int16)
    r, g, b = values[:, :, 0], values[:, :, 1], values[:, :, 2]
    exact = (r == 0) & (g == 255) & (b == 0)
    strong_chroma = (g >= 180) & ((g - r) >= 100) & ((g - b) >= 100)
    forced = (exact | strong_chroma) & ~background
    background |= exact | strong_chroma
    report = dict(report)
    report["forced_exact_or_strong_chroma_background_pixels"] = int(np.count_nonzero(forced))
    return background, report


def v2_estimate_rifle_angle(rgb: np.ndarray) -> dict[str, object]:
    report = base._v1_estimate_rifle_angle(rgb)
    eligible = [
        item for item in report["top_segments"]
        if float(item["length_px"]) >= 300.0 and 60.0 <= float(item["angle_degrees"]) <= 75.0
    ]
    if not eligible:
        raise RuntimeError("no sufficiently long V2 rifle centreline candidate")
    chosen = min(
        eligible,
        key=lambda item: (abs(float(item["angle_degrees"]) - base.TARGET_TANGENT), -float(item["length_px"])),
    )
    report = dict(report)
    report.update(
        {
            "method": "long HoughLinesP rifle segment nearest the locked 67.5-degree rigid-transform axis",
            "measured_tangent_degrees": float(chosen["angle_degrees"]),
            "absolute_residual_degrees": abs(float(chosen["angle_degrees"]) - base.TARGET_TANGENT),
            "longest_segment_length_px": float(chosen["length_px"]),
            "longest_segment_xyxy": list(chosen["xyxy"]),
        }
    )
    return report


def configure() -> None:
    base.PACKAGE = PACKAGE
    base.BLENDER_MANIFEST = MANIFEST
    base.RAW_DIR = PACKAGE / "blender_raw/current"
    base.FINAL_DIR = PACKAGE / "final/current"
    base.RUNTIME_DIR = PACKAGE / "runtime/current"
    base.QA_DIR = PACKAGE / "qa/current"
    base.EXPECTED_MANIFEST_SHA256 = EXPECTED_MANIFEST_SHA256
    if not hasattr(base, "_v1_matte_mask"):
        base._v1_matte_mask = base.matte_mask
    if not hasattr(base, "_v1_estimate_rifle_angle"):
        base._v1_estimate_rifle_angle = base.estimate_rifle_angle
    base.matte_mask = v2_matte_mask
    base.estimate_rifle_angle = v2_estimate_rifle_angle


def main() -> int:
    configure()
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
