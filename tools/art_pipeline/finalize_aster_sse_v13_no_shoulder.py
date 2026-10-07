#!/usr/bin/env python3
"""Finalize ASTER SSE V13 no-shoulder source art and QA derivatives.

This helper performs deterministic green-matte normalization and alpha export
only.  It does not generate or repaint source art and does not promote the
57-degree source pose as the final 67.5-degree motion result.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "sse_aim_master_v1"
)
RAW = PACKAGE / (
    "current/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V13_"
    "NO_SHOULDER_GREEN_RAW.png"
)
MASTER = PACKAGE / (
    "current/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V13_"
    "NO_SHOULDER_GREEN.png"
)
PREVIOUS = PACKAGE / (
    "previous/ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V9_GREEN_RAW.png"
)
AUTHORITY = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
AGENTS = ROOT / "AGENTS.md"
OUT = PACKAGE / "qa_v13_no_shoulder"
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

EXPECTED_SIZE = (1254, 1254)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
EXPECTED = {
    RAW: "bd8d7783cf4a7a757a3c95d4bd2fba21ed72a3b4bbc267ef905961b82e62d0ce",
    PREVIOUS: "dd97036f7443c41e5e199f4ba4c261343d89d574963a798112580d0b3f930d4f",
    AUTHORITY: "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838",
}

MASK_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_MASK.png"
RGBA_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_RGBA.png"
REVIEW_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_REVIEW_1920X1440.png"
QA_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_QA.json"
MANIFEST_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_MANIFEST.json"
EVIDENCE_NAME = "ASTER_FIRE_SSE_V13_NO_SHOULDER_EVIDENCE_1080P_QA.json"
CANDIDATE_LABEL = "V13"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_rgb(path: Path, expected_sha: str) -> np.ndarray:
    if not path.is_file() or sha256(path) != expected_sha:
        raise RuntimeError(f"locked input missing or SHA mismatch: {path}")
    with Image.open(path) as image:
        image.load()
        if image.mode != "RGB" or image.size != EXPECTED_SIZE:
            raise RuntimeError(f"RGB input mismatch: {path} {image.mode} {image.size}")
        return np.asarray(image, dtype=np.uint8).copy()


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

    cage_labels: list[int] = []
    preserved_green_labels: list[int] = []
    for index in range(1, count):
        if index in border_labels:
            continue
        cx, cy = (float(value) for value in centroids[index])
        area = int(stats[index, cv2.CC_STAT_AREA])
        if cx >= 800.0 and cy >= 800.0 and area >= 5:
            background |= labels == index
            cage_labels.append(index)
        elif area >= 5:
            preserved_green_labels.append(index)

    return background, {
        "loose_green_component_count": int(count - 1),
        "border_background_labels": sorted(int(value) for value in border_labels),
        "muzzle_cage_hole_labels": cage_labels,
        "preserved_subject_green_labels": preserved_green_labels,
    }


def estimate_rifle_angle(rgb: np.ndarray) -> dict[str, object]:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 150)
    roi = np.zeros_like(edges)
    roi[300:1020, 470:970] = 1
    lines = cv2.HoughLinesP(
        edges * roi,
        1,
        np.pi / 720.0,
        threshold=45,
        minLineLength=70,
        maxLineGap=18,
    )
    candidates: list[tuple[float, float, list[int]]] = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            dx, dy = float(x2 - x1), float(y2 - y1)
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0.0:
                angle += 180.0
            length = math.hypot(dx, dy)
            if 45.0 <= angle <= 85.0:
                candidates.append(
                    (float(length), float(angle), [int(x1), int(y1), int(x2), int(y2)])
                )
    candidates.sort(reverse=True)
    if not candidates:
        raise RuntimeError("could not estimate V13 rifle tangent")
    longest = candidates[0]
    return {
        "method": "longest HoughLinesP segment inside locked rifle ROI",
        "measured_tangent_degrees": longest[1],
        "target_tangent_degrees": 67.5,
        "absolute_residual_degrees": abs(longest[1] - 67.5),
        "longest_segment_length_px": longest[0],
        "longest_segment_xyxy": longest[2],
        "top_segments": [
            {"length_px": item[0], "angle_degrees": item[1], "xyxy": item[2]}
            for item in candidates[:8]
        ],
    }


def save_rgb(path: Path, rgb: np.ndarray) -> None:
    Image.fromarray(rgb, "RGB").save(path, "PNG", optimize=True)


def save_mask(path: Path, subject: np.ndarray) -> None:
    Image.fromarray(np.where(subject, 255, 0).astype(np.uint8), "L").save(
        path, "PNG", optimize=True
    )


def save_rgba(path: Path, rgb: np.ndarray, subject: np.ndarray) -> None:
    rgba = np.dstack((rgb, np.where(subject, 255, 0).astype(np.uint8)))
    Image.fromarray(rgba, "RGBA").save(path, "PNG", optimize=True)


def checker(size: tuple[int, int], light: bool) -> Image.Image:
    colors = ((235, 235, 235), (200, 200, 200)) if light else ((38, 42, 48), (70, 76, 84))
    array = np.empty((size[1], size[0], 3), dtype=np.uint8)
    block = 24
    yy, xx = np.indices((size[1], size[0]))
    choice = ((xx // block) + (yy // block)) % 2
    array[choice == 0] = colors[0]
    array[choice == 1] = colors[1]
    return Image.fromarray(array, "RGB")


def build_review(
    master: np.ndarray,
    subject: np.ndarray,
    rgba_path: Path,
    review_path: Path,
    angle: dict[str, object],
    metrics: dict[str, object],
) -> None:
    canvas = Image.new("RGB", (1920, 1440), (9, 14, 20))
    native = Image.fromarray(master, "RGB")
    canvas.paste(native, (24, 88))
    canvas.paste(native.resize((384, 384), Image.Resampling.LANCZOS), (1302, 88))
    canvas.paste(native.resize((131, 131), Image.Resampling.LANCZOS), (1710, 88))

    rgba = Image.open(rgba_path).convert("RGBA")
    scaled = rgba.resize((288, 288), Image.Resampling.LANCZOS)
    for index, light in enumerate((True, False)):
        panel = checker((288, 288), light)
        panel.paste(scaled, (0, 0), scaled)
        canvas.paste(panel, (1302 + index * 300, 520))

    crop = native.crop((400, 210, 860, 760))
    canvas.paste(crop, (1302, 830))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    white, cyan, amber, muted = (245, 247, 250), (70, 225, 245), (255, 188, 65), (185, 195, 205)
    draw.text(
        (24, 20),
        f"ASTER FIRE SSE {CANDIDATE_LABEL} NO-SHOULDER SOURCE MASTER",
        fill=white,
        font=font,
    )
    draw.text((24, 43), "SOURCE ART COMPLETE / HOLD_MOTION_REQUIRED — not runtime promotion", fill=amber, font=font)
    draw.text((24, 70), "NATIVE 1254x1254 1:1", fill=cyan, font=font)
    draw.text((1302, 70), "384x384 / 131x131 1:1", fill=cyan, font=font)
    draw.text((1302, 498), "RGBA LIGHT / DARK CHECKER", fill=cyan, font=font)
    draw.text((1302, 808), "NATIVE 1:1 FACE / SHOULDER / GRIP CROP", fill=cyan, font=font)
    details = (
        f"Shoulder armor: ABSENT",
        f"Exact-green background px: {metrics['exact_green_background_pixels']}",
        f"Non-green exterior px: {metrics['non_green_exterior_pixels']}",
        f"Rifle tangent: {angle['measured_tangent_degrees']:.3f} deg",
        f"Target: 67.500 deg; residual: {angle['absolute_residual_degrees']:.3f} deg",
        "Status: HOLD_MOTION_REQUIRED (Blender/UAL correction pending)",
        "Visual PASS is not claimed by this technical sheet.",
    )
    y = 1390 - len(details) * 20
    for line in details:
        draw.text((1302, y), line, fill=amber if "HOLD" in line else muted, font=font)
        y += 20
    canvas.save(review_path, "PNG", optimize=True)


def main() -> int:
    if MASTER.exists() or OUT.exists():
        raise SystemExit("final V13 output already exists; refusing overwrite")
    for path, expected_sha in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected_sha:
            raise SystemExit(f"locked input unavailable or SHA mismatch: {path}")
    raw = load_rgb(RAW, EXPECTED[RAW])
    background, component_report = matte_mask(raw)
    subject = ~background
    master = raw.copy()
    master[background] = EXACT_GREEN
    exact_green = np.all(master == EXACT_GREEN[None, None, :], axis=2)
    metrics = {
        "resolution": list(EXPECTED_SIZE),
        "mode": "RGB",
        "subject_pixels": int(np.count_nonzero(subject)),
        "background_pixels": int(np.count_nonzero(background)),
        "exact_green_background_pixels": int(np.count_nonzero(exact_green & background)),
        "non_green_exterior_pixels": int(np.count_nonzero((~exact_green) & background)),
        "interior_exact_green_pixels": int(np.count_nonzero(exact_green & subject)),
        "border_non_green_pixels": int(
            np.count_nonzero(~exact_green[0, :])
            + np.count_nonzero(~exact_green[-1, :])
            + np.count_nonzero(~exact_green[:, 0])
            + np.count_nonzero(~exact_green[:, -1])
        ),
        "component_report": component_report,
    }
    if metrics["non_green_exterior_pixels"] or metrics["border_non_green_pixels"]:
        raise SystemExit("exact-green matte contract failed")
    angle = estimate_rifle_angle(master)

    OUT.mkdir(parents=True, exist_ok=False)
    staging_master = OUT / (MASTER.name + ".verified-stage.png")
    mask_path = OUT / MASK_NAME
    rgba_path = OUT / RGBA_NAME
    review_path = OUT / REVIEW_NAME
    qa_path = OUT / QA_NAME
    manifest_path = OUT / MANIFEST_NAME
    evidence_path = OUT / EVIDENCE_NAME
    save_rgb(staging_master, master)
    save_mask(mask_path, subject)
    save_rgba(rgba_path, master, subject)
    build_review(master, subject, rgba_path, review_path, angle, metrics)

    with Image.open(staging_master) as check:
        check.load()
        if check.mode != "RGB" or check.size != EXPECTED_SIZE:
            raise RuntimeError("staged source master decode mismatch")
    with Image.open(rgba_path) as check:
        check.load()
        if check.mode != "RGBA" or check.size != EXPECTED_SIZE:
            raise RuntimeError("RGBA derivative decode mismatch")

    qa = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": f"ASTER SSE {CANDIDATE_LABEL} no-shoulder source-master technical QA",
        "result": "PASS_SOURCE_MATTE_AND_COMPONENT_REMOVAL_HOLD_MOTION_REQUIRED",
        "candidate_status": "HOLD_MOTION_REQUIRED",
        "source_art_complete": True,
        "motion_complete": False,
        "promotion_ready": False,
        "runtime_asset": False,
        "visual_pass_claimed": False,
        "shoulder_component_removal": "PASS",
        "shoulder_anatomy": "HOLD_MINOR_TO_MODERATE",
        "weapon_angle": angle,
        "metrics": metrics,
        "remaining_visual_holds": [
            "source rifle tangent is not the 67.5-degree runtime target",
            "cheek weld and support-hand clamp require motion-stage review",
            "unarmored shoulder taper requires final visual review",
        ],
    }
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    command = [
        sys.executable,
        os.fspath(VALIDATOR),
        os.fspath(review_path),
        "--require-dynamic-capture",
        "--output",
        os.fspath(evidence_path),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"1080p validator failed: {result.stdout}{result.stderr}")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("gate") != "PASS":
        raise RuntimeError(f"1080p evidence gate failed: {evidence.get('gate')}")

    manifest = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": f"ASTER SSE {CANDIDATE_LABEL} no-shoulder ImageGen source master",
        "status": "HOLD_MOTION_REQUIRED",
        "candidate_status": "HOLD_MOTION_REQUIRED",
        "promotion_ready": False,
        "runtime_asset": False,
        "visual_pass_claimed": False,
        "costume_correction": {
            "white_shoulder_armor": "ABSENT",
            "cyan_shoulder_stripe": "ABSENT",
            "gold_shoulder_hardware": "ABSENT",
            "authority": "AGENTS.md ASTER shoulder-costume correction",
            "agents_sha256": sha256(AGENTS),
        },
        "construction": {
            "source_author": "built-in ImageGen",
            "deterministic_postprocess": "border-connected chroma matte plus enclosed muzzle-cage holes",
            "local_model_generation_used": False,
            "source_raw_sha256": EXPECTED[RAW],
            "source_raw_deleted_after_verified_master": True,
        },
        "previous": {"path": rel(PREVIOUS), "sha256": sha256(PREVIOUS)},
        "identity_reference": {"path": rel(AUTHORITY), "sha256": sha256(AUTHORITY)},
        "weapon_angle": angle,
        "metrics": metrics,
        "outputs": {
            "source_master_green": {"path": rel(MASTER), "sha256": sha256(staging_master), "resolution": list(EXPECTED_SIZE)},
            "subject_mask": {"path": rel(mask_path), "sha256": sha256(mask_path)},
            "rgba_derivative": {"path": rel(rgba_path), "sha256": sha256(rgba_path)},
            "review": {"path": rel(review_path), "sha256": sha256(review_path), "resolution": [1920, 1440]},
            "qa": {"path": rel(qa_path), "sha256": sha256(qa_path), "result": qa["result"]},
            "evidence": {"path": rel(evidence_path), "sha256": sha256(evidence_path), "gate": evidence.get("gate")},
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    os.replace(staging_master, MASTER)
    RAW.unlink()
    if not MASTER.is_file() or sha256(MASTER) != manifest["outputs"]["source_master_green"]["sha256"]:
        raise RuntimeError("final source master hash mismatch after promotion")
    print(
        json.dumps(
            {
                "master": os.fspath(MASTER),
                "sha256": sha256(MASTER),
                "review": os.fspath(review_path),
                "qa_result": qa["result"],
                "evidence_gate": evidence.get("gate"),
                "rifle_tangent_degrees": angle["measured_tangent_degrees"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
