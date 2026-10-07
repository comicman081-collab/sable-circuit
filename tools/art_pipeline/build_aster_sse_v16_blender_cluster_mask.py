#!/usr/bin/env python3
"""Build the V16 rifle-and-both-arms cluster mask for Blender motion."""

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
SOURCE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "sse_aim_master_v1/current/"
    "ASTER_FIRE_SSE_DIRECTION_AIM_MASTER_IMAGEGEN_V16_NO_SHOULDER_GREEN.png"
)
SUBJECT = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "sse_aim_master_v1/qa_v16_no_shoulder/ASTER_FIRE_SSE_V16_NO_SHOULDER_MASK.png"
)
OUT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_blender_v1/cluster"
)
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

EXPECTED_SIZE = (1254, 1254)
EXPECTED = {
    SOURCE: "1a4b873d3e18d043e037cc75295e8b5156e447b9b6d53b8e5ab8df1b8671e8c0",
    SUBJECT: "9739d9c87d4e22472b1eb3175c7192be8bb090569e58dc79bce4f238a4c51cef",
}

MASK_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_MASK.png"
RGBA_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_RGBA.png"
REVIEW_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_REVIEW_1920X1440.png"
QA_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_QA.json"
MANIFEST_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_MANIFEST.json"
EVIDENCE_NAME = "ASTER_FIRE_SSE_V16_RIFLE_ARMS_CLUSTER_EVIDENCE_1080P_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def polygon(shape: tuple[int, int], points: tuple[tuple[int, int], ...]) -> np.ndarray:
    output = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(output, [np.asarray(points, dtype=np.int32)], 1)
    return output > 0


def load_inputs() -> tuple[np.ndarray, np.ndarray]:
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"locked input unavailable or SHA mismatch: {path}")
    source = cv2.imdecode(np.frombuffer(SOURCE.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
    subject_raw = cv2.imdecode(np.frombuffer(SUBJECT.read_bytes(), np.uint8), cv2.IMREAD_GRAYSCALE)
    if source is None or subject_raw is None:
        raise RuntimeError("could not decode locked V16 inputs")
    if source.shape[:2][::-1] != EXPECTED_SIZE or subject_raw.shape[:2][::-1] != EXPECTED_SIZE:
        raise RuntimeError("locked V16 inputs are not 1254x1254")
    return source, subject_raw == 255


def build_mask(source: np.ndarray, subject: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    shape = subject.shape
    labels = np.full(shape, cv2.GC_BGD, dtype=np.uint8)

    possible_polygons = (
        # Trigger-side arm, stock, hand, receiver.
        ((330, 260), (470, 250), (585, 350), (630, 500), (565, 575), (430, 530), (330, 450)),
        # Support-side upper/lower arm and hand.
        ((570, 270), (700, 270), (755, 390), (735, 590), (700, 730), (625, 710), (585, 590)),
        # Complete rifle corridor through muzzle cage.
        ((430, 280), (560, 285), (700, 500), (790, 700), (850, 800), (935, 900), (920, 990),
         (825, 985), (770, 850), (690, 780), (590, 650), (500, 545), (420, 410)),
    )
    possible = np.zeros(shape, dtype=bool)
    for points in possible_polygons:
        possible |= polygon(shape, points)
    possible &= subject
    labels[possible] = cv2.GC_PR_BGD

    foreground_polygons = (
        # Trigger sleeve/forearm/hand.
        ((344, 319), (409, 286), (491, 341), (557, 423), (548, 506), (477, 507), (388, 459), (342, 414)),
        # Support sleeve/forearm/hand.
        ((611, 296), (673, 291), (713, 373), (712, 527), (680, 675), (630, 670), (607, 549)),
        # Stock/optic/receiver/magazine.
        ((445, 299), (520, 300), (599, 389), (689, 545), (677, 658), (605, 651), (548, 553), (485, 467)),
        # Rail/barrel/muzzle cage.
        ((628, 535), (708, 586), (775, 712), (826, 817), (901, 846), (914, 942), (867, 969),
         (813, 935), (800, 849), (744, 775), (683, 689)),
    )
    for points in foreground_polygons:
        selected = polygon(shape, points) & possible
        labels[selected] = cv2.GC_PR_FGD

    foreground_lines = (
        ((363, 352), (421, 391), (486, 434), (538, 477)),
        ((630, 330), (673, 412), (680, 524), (654, 635)),
        ((460, 313), (528, 370), (592, 467), (655, 584), (733, 716), (809, 842), (868, 932)),
        ((512, 362), (580, 430), (642, 536)),
    )
    for points in foreground_lines:
        cv2.polylines(labels, [np.asarray(points, dtype=np.int32)], False, cv2.GC_FGD, 7, cv2.LINE_8)

    background_polygons = (
        # Hair/face exclusion.
        ((120, 20), (520, 20), (620, 190), (590, 330), (470, 360), (250, 350), (120, 220)),
        ((440, 190), (610, 190), (626, 330), (565, 360), (484, 350), (430, 280)),
        # Torso and waist away from visible arms/rifle.
        ((365, 460), (455, 480), (540, 540), (598, 650), (565, 720), (410, 700), (355, 590)),
        ((360, 630), (625, 625), (690, 790), (570, 870), (350, 790)),
        # Legs and exterior costume modules.
        ((190, 600), (410, 570), (485, 760), (380, 1070), (180, 1070)),
        ((575, 650), (735, 620), (850, 1160), (650, 1180), (535, 850)),
    )
    for points in background_polygons:
        labels[polygon(shape, points) & possible] = cv2.GC_BGD

    labels[~subject] = cv2.GC_BGD
    seeds = labels.copy()
    bg_model = np.zeros((1, 65), dtype=np.float64)
    fg_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(source, labels, None, bg_model, fg_model, 8, cv2.GC_INIT_WITH_MASK)
    result = ((labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD)) & possible & subject

    # Reinforce the long rigid weapon centre corridor without filling the cage holes.
    weapon_corridor = np.zeros(shape, dtype=np.uint8)
    cv2.polylines(
        weapon_corridor,
        [np.asarray(((454, 312), (548, 410), (650, 590), (748, 756), (831, 872)), dtype=np.int32)],
        False,
        1,
        11,
        cv2.LINE_8,
    )
    result |= (weapon_corridor > 0) & subject

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(result.astype(np.uint8), cv2.MORPH_CLOSE, kernel) > 0
    result = closed & subject & possible

    count, component_labels, stats, _ = cv2.connectedComponentsWithStats(result.astype(np.uint8), 8)
    keep = [index for index in range(1, count) if int(stats[index, cv2.CC_STAT_AREA]) >= 30]
    result = np.isin(component_labels, keep) & result
    return result, seeds


def build_review(source_rgb: np.ndarray, mask: np.ndarray, seeds: np.ndarray, output: Path) -> None:
    overlay = source_rgb.copy()
    overlay[mask] = np.rint(
        overlay[mask].astype(np.float32) * 0.35
        + np.asarray((255, 0, 255), dtype=np.float32) * 0.65
    ).astype(np.uint8)
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (255, 255, 0), 2)

    seed_overlay = source_rgb.copy()
    hard_fg = seeds == cv2.GC_FGD
    probable_fg = seeds == cv2.GC_PR_FGD
    seed_overlay[hard_fg] = (255, 255, 255)
    seed_overlay[probable_fg] = np.rint(
        seed_overlay[probable_fg].astype(np.float32) * 0.35
        + np.asarray((0, 220, 255), dtype=np.float32) * 0.65
    ).astype(np.uint8)

    canvas = Image.new("RGB", (1920, 1440), (9, 14, 20))
    canvas.paste(Image.fromarray(overlay, "RGB"), (24, 88))
    canvas.paste(Image.fromarray(overlay[250:850, 300:950], "RGB"), (1302, 88))
    canvas.paste(Image.fromarray(seed_overlay[250:850, 300:950], "RGB"), (1302, 700))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 20), "ASTER SSE V16 BLENDER RIFLE+ARMS CLUSTER MASK", fill=(245, 247, 250), font=font)
    draw.text((24, 43), "AUTHORING / HOLD — MAGENTA cluster, YELLOW boundary", fill=(255, 188, 65), font=font)
    draw.text((24, 70), "NATIVE 1254x1254 1:1", fill=(70, 225, 245), font=font)
    draw.text((1302, 70), "NATIVE 1:1 MASK CROP", fill=(70, 225, 245), font=font)
    draw.text((1302, 682), "NATIVE 1:1 GRABCUT SEEDS", fill=(70, 225, 245), font=font)
    canvas.save(output, "PNG", optimize=True)


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"cluster output already exists; refusing overwrite: {OUT}")
    source_bgr, subject = load_inputs()
    mask, seeds = build_mask(source_bgr, subject)
    source_rgb = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)
    pixels = int(np.count_nonzero(mask))
    outside_subject = int(np.count_nonzero(mask & ~subject))
    exact_green = np.all(source_rgb == np.asarray((0, 255, 0), dtype=np.uint8), axis=2)
    green_in_mask = int(np.count_nonzero(mask & exact_green))
    count, _labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    areas = sorted((int(row[cv2.CC_STAT_AREA]) for row in stats[1:]), reverse=True)
    metrics = {
        "pixels": pixels,
        "components": int(max(0, count - 1)),
        "significant_components_30px": len([area for area in areas if area >= 30]),
        "largest_component_ratio": float(areas[0] / max(1, pixels)) if areas else 0.0,
        "outside_subject_pixels": outside_subject,
        "exact_green_pixels": green_in_mask,
    }
    if not pixels or outside_subject or green_in_mask:
        raise SystemExit(f"cluster mask containment failed: {metrics}")

    OUT.mkdir(parents=True, exist_ok=False)
    mask_path = OUT / MASK_NAME
    rgba_path = OUT / RGBA_NAME
    review_path = OUT / REVIEW_NAME
    qa_path = OUT / QA_NAME
    manifest_path = OUT / MANIFEST_NAME
    evidence_path = OUT / EVIDENCE_NAME
    Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), "L").save(mask_path, "PNG", optimize=True)
    rgba = np.dstack((source_rgb, np.where(mask, 255, 0).astype(np.uint8)))
    Image.fromarray(rgba, "RGBA").save(rgba_path, "PNG", optimize=True)
    build_review(source_rgb, mask, seeds, review_path)

    qa = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": "ASTER SSE V16 Blender rigid rifle-and-both-arms cluster mask QA",
        "result": "PASS_CONTAINMENT_ONLY_HOLD_VISUAL_MASK_REVIEW_REQUIRED",
        "candidate_status": "HOLD",
        "promotion_ready": False,
        "runtime_asset": False,
        "visual_pass_claimed": False,
        "metrics": metrics,
        "manual_rejection_triggers": [
            "face or hair included",
            "torso or leg module included",
            "rifle/hand/forearm pixels missing",
            "muzzle cage holes filled",
        ],
    }
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    command = [sys.executable, os.fspath(VALIDATOR), os.fspath(review_path), "--require-dynamic-capture", "--output", os.fspath(evidence_path)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"1080p validator failed: {result.stdout}{result.stderr}")
    manifest = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": "ASTER SSE V16 Blender rigid rifle-and-both-arms cluster input",
        "status": "HOLD_VISUAL_MASK_REVIEW_REQUIRED",
        "promotion_ready": False,
        "runtime_asset": False,
        "source": {"path": rel(SOURCE), "sha256": sha256(SOURCE)},
        "subject_mask": {"path": rel(SUBJECT), "sha256": sha256(SUBJECT)},
        "method": "project-local OpenCV GrabCut with hand-authored regions and strokes",
        "model_used": False,
        "network_used": False,
        "outputs": {
            "cluster_mask": {"path": rel(mask_path), "sha256": sha256(mask_path)},
            "cluster_rgba": {"path": rel(rgba_path), "sha256": sha256(rgba_path)},
            "review": {"path": rel(review_path), "sha256": sha256(review_path), "resolution": [1920, 1440]},
            "qa": {"path": rel(qa_path), "sha256": sha256(qa_path), "result": qa["result"]},
            "evidence": {"path": rel(evidence_path), "sha256": sha256(evidence_path)},
        },
        "metrics": metrics,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mask": os.fspath(mask_path), "rgba": os.fspath(rgba_path), "metrics": metrics}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
