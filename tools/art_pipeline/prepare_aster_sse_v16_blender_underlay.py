#!/usr/bin/env python3
"""Prepare the project-local ImageGen body underlay for Blender compositing.

This is deterministic chroma extraction only.  It does not generate, repaint,
or alter the immutable ImageGen raw input.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_blender_v1/input"
)
RAW = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_IMAGEGEN_V1_GREEN_RAW.png"
MASTER = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_IMAGEGEN_V1_GREEN.png"
MASK = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_IMAGEGEN_V1_MASK.png"
RGBA = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_IMAGEGEN_V1_RGBA.png"
REVIEW = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_REVIEW_1920X1440.png"
QA = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_QA.json"
EVIDENCE = INPUT_DIR / "ASTER_FIRE_SSE_V16_BODY_UNDERLAY_EVIDENCE_1080P_QA.json"
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

EXPECTED_RAW_SHA256 = "23a9e3673ab84ac1a48118736187f0c83414fd2a2df9cf69c5e4c01eec393f6a"
EXPECTED_SIZE = (1254, 1254)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def matte_mask(rgb: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    values = rgb.astype(np.int16)
    r, g, b = values[:, :, 0], values[:, :, 1], values[:, :, 2]
    loose = (g >= 70) & ((g - r) >= 15) & ((g - b) >= 15)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        loose.astype(np.uint8), 8
    )
    border_labels = set(
        np.unique(
            np.concatenate((labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]))
        ).tolist()
    )
    border_labels.discard(0)
    if not border_labels:
        raise RuntimeError("no border-connected chroma component")
    background = np.isin(labels, list(border_labels))

    preserved: list[int] = []
    for index in range(1, count):
        if index in border_labels:
            continue
        area = int(stats[index, cv2.CC_STAT_AREA])
        if area >= 5:
            preserved.append(index)
    return background, {
        "loose_green_component_count": int(count - 1),
        "border_background_labels": sorted(int(value) for value in border_labels),
        "preserved_subject_green_labels": preserved,
    }


def build_review(master: np.ndarray, rgba: np.ndarray) -> None:
    canvas = Image.new("RGB", (1920, 1440), (9, 14, 20))
    native = Image.fromarray(master, "RGB")
    canvas.paste(native, (24, 88))
    canvas.paste(native.resize((384, 384), Image.Resampling.LANCZOS), (1302, 88))
    alpha_image = Image.fromarray(rgba, "RGBA").resize((384, 384), Image.Resampling.LANCZOS)
    for index, color in enumerate(((230, 230, 230), (35, 40, 47))):
        panel = Image.new("RGB", (384, 384), color)
        panel.paste(alpha_image, (0, 0), alpha_image)
        canvas.paste(panel, (1302, 520 + index * 404))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 20), "ASTER SSE V16 IMAGEGEN BODY UNDERLAY", fill=(245, 247, 250), font=font)
    draw.text((24, 43), "PROJECT-LOCAL BLENDER INPUT / NOT RUNTIME", fill=(255, 188, 65), font=font)
    draw.text((24, 70), "NATIVE 1254x1254 1:1", fill=(70, 225, 245), font=font)
    draw.text((1302, 70), "384x384 / RGBA LIGHT+DARK", fill=(70, 225, 245), font=font)
    canvas.save(REVIEW, "PNG", optimize=True)


def main() -> int:
    outputs = (MASTER, MASK, RGBA, REVIEW, QA, EVIDENCE)
    if any(path.exists() for path in outputs):
        raise SystemExit("underlay derivative already exists; refusing overwrite")
    if not RAW.is_file() or sha256(RAW) != EXPECTED_RAW_SHA256:
        raise SystemExit("locked ImageGen underlay raw missing or SHA mismatch")
    with Image.open(RAW) as image:
        image.load()
        if image.mode != "RGB" or image.size != EXPECTED_SIZE:
            raise SystemExit(f"underlay input mismatch: {image.mode} {image.size}")
        rgb = np.asarray(image, dtype=np.uint8).copy()

    background, components = matte_mask(rgb)
    subject = ~background
    master = rgb.copy()
    master[background] = EXACT_GREEN
    alpha = np.where(subject, 255, 0).astype(np.uint8)
    rgba = np.dstack((master, alpha))
    exact = np.all(master == EXACT_GREEN[None, None, :], axis=2)
    metrics = {
        "resolution": list(EXPECTED_SIZE),
        "subject_pixels": int(np.count_nonzero(subject)),
        "background_pixels": int(np.count_nonzero(background)),
        "exact_green_background_pixels": int(np.count_nonzero(exact & background)),
        "non_green_exterior_pixels": int(np.count_nonzero((~exact) & background)),
        "interior_exact_green_pixels": int(np.count_nonzero(exact & subject)),
        "component_report": components,
    }
    if metrics["non_green_exterior_pixels"]:
        raise SystemExit("underlay exact-green contract failed")

    Image.fromarray(master, "RGB").save(MASTER, "PNG", optimize=True)
    Image.fromarray(alpha, "L").save(MASK, "PNG", optimize=True)
    Image.fromarray(rgba, "RGBA").save(RGBA, "PNG", optimize=True)
    build_review(master, rgba)
    QA.write_text(
        json.dumps(
            {
                "schema": 1,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "role": "ASTER SSE V16 project-local Blender body underlay technical QA",
                "result": "PASS_INPUT_MATTE_ONLY",
                "runtime_asset": False,
                "promotion_ready": False,
                "visual_pass_claimed": False,
                "metrics": metrics,
                "raw": {"path": rel(RAW), "sha256": EXPECTED_RAW_SHA256},
                "outputs": {
                    "master": {"path": rel(MASTER), "sha256": sha256(MASTER)},
                    "mask": {"path": rel(MASK), "sha256": sha256(MASK)},
                    "rgba": {"path": rel(RGBA), "sha256": sha256(RGBA)},
                    "review": {"path": rel(REVIEW), "sha256": sha256(REVIEW)},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    command = [
        sys.executable,
        os.fspath(VALIDATOR),
        os.fspath(REVIEW),
        "--require-dynamic-capture",
        "--output",
        os.fspath(EVIDENCE),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"1080p evidence validator failed: {result.stdout}{result.stderr}")
    print(
        json.dumps(
            {
                "master": os.fspath(MASTER),
                "rgba": os.fspath(RGBA),
                "metrics": metrics,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
