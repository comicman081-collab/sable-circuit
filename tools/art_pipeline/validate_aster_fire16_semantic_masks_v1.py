#!/usr/bin/env python3
"""Fail-closed QA for ASTER Fire16 native semantic assembly masks.

This validator never authors or repairs pixels.  It checks three human-review
inputs (rifle, trigger hand/forearm, support hand/forearm) against the approved
native subject mask and writes a project-local JSON report plus a 1920x1440
overlay.  A technical PASS remains ``HOLD_USER_VISUAL_REVIEW_REQUIRED``.
"""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from project_paths import PROJECT_ROOT, require_project_output_path


EXPECTED_SIZE = (1254, 1254)
GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
INNER = np.asarray((878.4531, 525.7656), dtype=np.float32)
MUZZLE = np.asarray((1018.8750, 610.6719), dtype=np.float32)
EXPECTED_TANGENT = 31.1593
SIGNIFICANT_AREA = 200
AUTHORITY_SOURCE = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
AUTHORITY_SUBJECT = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/aim_master_v2/masks/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_MASK.png"
)
AUTHORITY_SOURCE_SHA256 = "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838"
AUTHORITY_SUBJECT_SHA256 = "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5"
AUTHORING_ROOT = (
    PROJECT_ROOT
    / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_semantic_masks_v1"
)
REQUIRED_CONTRACT_MASKS = [
    "SUBJECT",
    "HAIR_BACK",
    "BODY_CORE",
    "HEAD_FACE",
    "HAIR_FRONT",
    "ARM_TRIGGER_UPPER",
    "ARM_SUPPORT_UPPER",
    "RIFLE",
    "TRIGGER_FOREARM_HAND",
    "SUPPORT_FOREARM_HAND",
    "SHOULDER_PLATE",
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE",
    "OPPOSITE_STRAPS_POUCH_LEG",
    "BOOTS_ACCESSORIES",
    "SHOULDER_ELBOW_SEAM_BRIDGE",
    "TARGET_OCCLUDE",
    "TARGET_REVEAL",
]
CHECKED_MASKS = ["SUBJECT", "RIFLE", "TRIGGER_FOREARM_HAND", "SUPPORT_FOREARM_HAND"]
ROLE_RULES: dict[str, dict[str, Any]] = {
    "rifle": {
        "fraction": (0.055, 0.145),
        "bbox_edges": {"x0": (340, 600), "y0": (260, 420), "x1": (930, 1040), "y1": (550, 680)},
        "positive": [(570, 370), (620, 400), (750, 475), (820, 515), (900, 555), (955, 585)],
        "negative": [(520, 285), (430, 220), (635, 300), (400, 410), (690, 495), (475, 555)],
    },
    "trigger_forearm_hand": {
        "fraction": (0.025, 0.095),
        "bbox_edges": {"x0": (260, 390), "y0": (300, 430), "x1": (500, 590), "y1": (430, 510)},
        "positive": [(340, 405), (410, 420), (480, 430), (525, 430)],
        "negative": [(575, 395), (520, 285), (650, 315), (690, 495), (455, 540)],
    },
    "support_forearm_hand": {
        "fraction": (0.008, 0.060),
        "bbox_edges": {"x0": (590, 690), "y0": (390, 480), "x1": (700, 790), "y1": (490, 570)},
        "positive": [(660, 445), (690, 490), (720, 510)],
        "negative": [(650, 315), (575, 395), (520, 285), (700, 580), (480, 430)],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_input(path: Path, label: str, *, authoring_only: bool = False) -> Path:
    resolved = (path if path.is_absolute() else PROJECT_ROOT / path).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as error:
        raise RuntimeError(f"{label} must be project-local: {resolved}") from error
    if not resolved.is_file():
        raise RuntimeError(f"{label} is unavailable: {resolved}")
    if authoring_only:
        try:
            resolved.relative_to(AUTHORING_ROOT)
        except ValueError as error:
            raise RuntimeError(f"{label} must be below {AUTHORING_ROOT}: {resolved}") from error
    return resolved


def read_pil(path: Path, label: str, expected_mode: str) -> tuple[Image.Image, bytes, str]:
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    with Image.open(BytesIO(payload)) as opened:
        opened.load()
        if opened.mode != expected_mode:
            raise RuntimeError(f"{label} must use mode {expected_mode}, got {opened.mode}")
        image = opened.copy()
    return image, payload, digest


def load_rgb(path: Path, label: str) -> tuple[np.ndarray, str]:
    opened, _payload, digest = read_pil(path, label, "RGB")
    image = np.asarray(opened, dtype=np.uint8)
    if image.shape[:2] != EXPECTED_SIZE[::-1]:
        raise RuntimeError(f"{label} must be 1254x1254, got {image.shape[1]}x{image.shape[0]}")
    return image, digest


def load_binary(path: Path, label: str) -> tuple[np.ndarray, str]:
    opened, _payload, digest = read_pil(path, label, "L")
    raw = np.asarray(opened, dtype=np.uint8)
    if raw.shape != EXPECTED_SIZE[::-1]:
        raise RuntimeError(f"{label} must be 1254x1254, got {raw.shape[1]}x{raw.shape[0]}")
    values = np.unique(raw)
    if not set(values.tolist()).issubset({0, 255}):
        raise RuntimeError(f"{label} must contain only 0/255, got {values[:16].tolist()}")
    mask = raw == 255
    if not np.any(mask):
        raise RuntimeError(f"{label} is empty")
    return mask, digest


def component_metrics(mask: np.ndarray, minimum_area: int = SIGNIFICANT_AREA) -> dict[str, Any]:
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    areas = sorted((int(area) for area in stats[1:, cv2.CC_STAT_AREA]), reverse=True)
    significant = [area for area in areas if area >= minimum_area]
    total = int(np.count_nonzero(mask))
    largest = areas[0] if areas else 0
    ys, xs = np.nonzero(mask)
    bbox = [
        int(xs.min()),
        int(ys.min()),
        int(xs.max()) + 1,
        int(ys.max()) + 1,
    ]
    return {
        "pixels": total,
        "components": max(0, count - 1),
        "significant_components": len(significant),
        "significant_component_areas": significant,
        "largest_component_ratio": float(largest) / float(max(1, total)),
        "bbox_xyxy_exclusive": bbox,
    }


def near_point(mask: np.ndarray, point: np.ndarray, radius: float) -> bool:
    yy, xx = np.mgrid[0 : mask.shape[0], 0 : mask.shape[1]]
    return bool(np.any(mask & (((xx - point[0]) ** 2 + (yy - point[1]) ** 2) <= radius**2)))


def mask_contains_point(mask: np.ndarray, point: tuple[int, int], radius: float = 12.0) -> bool:
    return near_point(mask, np.asarray(point, dtype=np.float32), radius)


def max_false_run(values: list[bool]) -> int:
    longest = 0
    current = 0
    for value in values:
        if value:
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return longest


def corridor_metrics(
    mask: np.ndarray,
    subject: np.ndarray,
    topology_mask: np.ndarray,
    inner: np.ndarray,
    muzzle: np.ndarray,
) -> dict[str, Any]:
    yy, xx = np.mgrid[0 : mask.shape[0], 0 : mask.shape[1]].astype(np.float32)
    vector = muzzle - inner
    length2 = max(float(np.dot(vector, vector)), 1e-6)
    projection = ((xx - inner[0]) * vector[0] + (yy - inner[1]) * vector[1]) / length2
    closest_x = inner[0] + np.clip(projection, 0.0, 1.0) * vector[0]
    closest_y = inner[1] + np.clip(projection, 0.0, 1.0) * vector[1]
    distance = np.sqrt((xx - closest_x) ** 2 + (yy - closest_y) ** 2)
    corridor = (projection >= 0.02) & (projection <= 0.98) & (distance <= 9.0)
    supported_corridor = corridor & subject
    visible = supported_corridor & mask
    support = float(np.count_nonzero(visible)) / float(max(1, np.count_nonzero(supported_corridor)))
    # Tangent is fitted independently from all distal-rifle pixels in a locked
    # broad ROI, not from the expected corridor used by the support check.
    distal = mask & (xx >= 700.0) & (xx <= 1045.0) & (yy >= 420.0) & (yy <= 690.0)
    ys, xs = np.nonzero(distal)
    tangent = EXPECTED_TANGENT
    residual = 180.0
    if len(xs) >= 10:
        coordinates = np.column_stack((xs.astype(np.float32), ys.astype(np.float32)))
        coordinates -= coordinates.mean(axis=0, keepdims=True)
        _values, vectors = np.linalg.eigh(coordinates.T @ coordinates)
        axis = vectors[:, -1]
        tangent = math.degrees(math.atan2(float(axis[1]), float(axis[0]))) % 180.0
        residual = abs((tangent - EXPECTED_TANGENT + 90.0) % 180.0 - 90.0)

    occupied_bins: list[bool] = []
    for index in range(64):
        low = index / 64.0
        high = (index + 1) / 64.0
        band = (projection >= low) & (projection < high) & (distance <= 12.0) & subject
        if np.any(band):
            occupied_bins.append(bool(np.any(mask & band)))

    count, labels = cv2.connectedComponents(topology_mask.astype(np.uint8), connectivity=8)

    def nearby_labels(point: np.ndarray, radius: float) -> set[int]:
        region = ((xx - point[0]) ** 2 + (yy - point[1]) ** 2) <= radius**2
        return {int(value) for value in np.unique(labels[region & topology_mask]) if int(value) > 0}

    inner_labels = nearby_labels(inner, 20.0)
    muzzle_labels = nearby_labels(muzzle, 40.0)
    endpoint_connected = bool(inner_labels & muzzle_labels)
    muzzle_roi = ((xx - muzzle[0]) ** 2 + (yy - muzzle[1]) ** 2) <= 75.0**2
    muzzle_local = (mask & muzzle_roi).astype(np.uint8)
    muzzle_local = cv2.morphologyEx(muzzle_local, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    local_count, _local_labels, local_stats, _local_centroids = cv2.connectedComponentsWithStats(
        muzzle_local, 8
    )
    muzzle_clusters = sum(
        int(local_stats[index, cv2.CC_STAT_AREA]) >= SIGNIFICANT_AREA
        for index in range(1, local_count)
    )
    return {
        "support_ratio": support,
        "subject_clipped_corridor_pixels": int(np.count_nonzero(supported_corridor)),
        "raster_tangent_degrees": tangent,
        "raster_tangent_residual_degrees": residual,
        "distal_pixels_used_for_independent_tangent": int(np.count_nonzero(distal)),
        "occupied_projection_bins": int(sum(occupied_bins)),
        "projection_bins": len(occupied_bins),
        "maximum_consecutive_empty_projection_bins": max_false_run(occupied_bins),
        "inner_muzzle_same_rifle_component": endpoint_connected,
        "muzzle_hardware_significant_clusters": int(muzzle_clusters),
        "closed_rigid_topology_component_count": max(0, count - 1),
    }


def rgba_overlay(source: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float) -> np.ndarray:
    result = source.astype(np.float32).copy()
    tint = np.asarray(color, dtype=np.float32)
    result[mask] = result[mask] * (1.0 - alpha) + tint * alpha
    return np.clip(result, 0, 255).astype(np.uint8)


def build_review(
    source: np.ndarray,
    subject: np.ndarray,
    rifle: np.ndarray,
    trigger: np.ndarray,
    support: np.ndarray,
    output: Path,
    result: str,
    failures: list[str],
) -> None:
    native = source.copy()
    contours, _ = cv2.findContours(subject.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(native, contours, -1, (255, 255, 255), 2)
    for mask, color in (
        (rifle, (255, 50, 50)),
        (trigger, (0, 220, 255)),
        (support, (255, 220, 0)),
    ):
        part_contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(native, part_contours, -1, color, 3)
    cv2.circle(native, tuple(np.round(INNER).astype(int)), 12, (255, 0, 255), 3)
    cv2.circle(native, tuple(np.round(MUZZLE).astype(int)), 12, (255, 0, 255), 3)
    cv2.line(
        native,
        tuple(np.round(INNER).astype(int)),
        tuple(np.round(MUZZLE).astype(int)),
        (255, 0, 255),
        3,
    )

    diagnostic = source.copy()
    diagnostic = rgba_overlay(diagnostic, rifle, (255, 50, 50), 0.58)
    diagnostic = rgba_overlay(diagnostic, trigger, (0, 220, 255), 0.58)
    diagnostic = rgba_overlay(diagnostic, support, (255, 220, 0), 0.58)

    canvas = Image.new("RGB", (1920, 1440), (20, 22, 28))
    canvas.paste(Image.fromarray(native), (24, 88))
    runtime = Image.fromarray(diagnostic).resize((384, 384), Image.Resampling.LANCZOS)
    gameplay = Image.fromarray(diagnostic).resize((131, 131), Image.Resampling.LANCZOS)
    canvas.paste(runtime, (1302, 88))
    canvas.paste(gameplay, (1710, 88))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 24), f"ASTER FIRE16 SE SOURCE-MASK QA — {result}", fill=(255, 255, 255), font=font)
    draw.text((1302, 482), "PRELIMINARY THREE-PART SOURCE MASK CHECK", fill=(255, 185, 80), font=font)
    draw.text((1302, 512), "RED: rifle", fill=(255, 90, 90), font=font)
    draw.text((1302, 536), "CYAN: trigger hand + forearm", fill=(40, 230, 255), font=font)
    draw.text((1302, 560), "YELLOW: support hand + forearm", fill=(255, 225, 50), font=font)
    draw.text((1302, 584), "WHITE: approved subject contour", fill=(255, 255, 255), font=font)
    draw.text((1302, 608), "MAGENTA: locked SE rifle anchors", fill=(255, 80, 255), font=font)
    draw.text((1302, 650), "Native source: 1254x1254 at 1:1", fill=(205, 210, 220), font=font)
    draw.text((1302, 674), "Runtime inspection: 384x384 at 1:1", fill=(205, 210, 220), font=font)
    draw.text((1302, 698), "Gameplay inspection: 131x131 at 1:1", fill=(205, 210, 220), font=font)
    draw.text((1302, 734), "Not a complete 17-mask contract gate.", fill=(255, 185, 80), font=font)
    draw.text((1302, 758), "Technical result never grants visual PASS.", fill=(255, 185, 80), font=font)
    y = 806
    for failure in failures[:24]:
        wrapped = [failure[index : index + 68] for index in range(0, len(failure), 68)] or [failure]
        for line in wrapped:
            draw.text((1302, y), line, fill=(255, 120, 120), font=font)
            y += 18
        y += 6
    atomic_save_image(canvas, output)


def atomic_save_image(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp.png")
    try:
        image.save(temporary, format="PNG")
        with Image.open(temporary) as decoded:
            decoded.verify()
        with Image.open(temporary) as decoded:
            if decoded.mode != "RGB" or decoded.size != (1920, 1440):
                raise RuntimeError(
                    f"review decode mismatch: mode={decoded.mode} size={decoded.size}"
                )
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        json.loads(temporary.read_text(encoding="utf-8"))
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def authoring_output(path: Path, label: str, suffix: str) -> Path:
    resolved = require_project_output_path(path, label)
    try:
        resolved.relative_to(AUTHORING_ROOT)
    except ValueError as error:
        raise RuntimeError(f"{label} must be below {AUTHORING_ROOT}: {resolved}") from error
    if resolved.suffix.lower() != suffix:
        raise RuntimeError(f"{label} must use {suffix}, got {resolved.suffix}")
    if resolved.exists() and resolved.is_dir():
        raise RuntimeError(f"{label} points to a directory: {resolved}")
    return resolved


def reject_path_collisions(inputs: list[Path], outputs: list[Path]) -> None:
    all_paths = inputs + outputs
    normalized = [os.path.normcase(str(path.resolve())) for path in all_paths]
    if len(set(normalized)) != len(normalized):
        raise RuntimeError("input/output path collision")
    for output in outputs:
        if not output.exists():
            continue
        for input_path in inputs:
            if os.path.samefile(output, input_path):
                raise RuntimeError(f"output is a hardlink to input: {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--subject-mask", type=Path, required=True)
    parser.add_argument("--rifle-mask", type=Path, required=True)
    parser.add_argument("--trigger-mask", type=Path, required=True)
    parser.add_argument("--support-mask", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()

    paths = {
        "source": project_input(args.source, "source"),
        "subject_mask": project_input(args.subject_mask, "subject mask"),
        "rifle_mask": project_input(args.rifle_mask, "rifle mask", authoring_only=True),
        "trigger_mask": project_input(args.trigger_mask, "trigger mask", authoring_only=True),
        "support_mask": project_input(args.support_mask, "support mask", authoring_only=True),
    }
    if paths["source"] != AUTHORITY_SOURCE.resolve():
        raise RuntimeError(f"source is not the locked SE authority: {paths['source']}")
    if paths["subject_mask"] != AUTHORITY_SUBJECT.resolve():
        raise RuntimeError(f"subject mask is not the locked SE authority: {paths['subject_mask']}")
    qa_path = authoring_output(args.qa, "semantic mask QA", ".json")
    review_path = authoring_output(args.review, "semantic mask review", ".png")
    reject_path_collisions(list(paths.values()), [qa_path, review_path])

    # Remove stale current outputs before reading authority bytes. A failed run
    # must never leave an older PASS-looking report at the requested path.
    qa_path.unlink(missing_ok=True)
    review_path.unlink(missing_ok=True)

    source, source_digest = load_rgb(paths["source"], "source")
    subject, subject_digest = load_binary(paths["subject_mask"], "subject mask")
    loaded_parts = {
        "rifle": load_binary(paths["rifle_mask"], "rifle mask"),
        "trigger_forearm_hand": load_binary(paths["trigger_mask"], "trigger mask"),
        "support_forearm_hand": load_binary(paths["support_mask"], "support mask"),
    }
    parts = {name: loaded[0] for name, loaded in loaded_parts.items()}
    part_digests = {name: loaded[1] for name, loaded in loaded_parts.items()}
    if source_digest != AUTHORITY_SOURCE_SHA256:
        raise RuntimeError(f"locked SE source SHA mismatch: {source_digest}")
    if subject_digest != AUTHORITY_SUBJECT_SHA256:
        raise RuntimeError(f"locked SE subject SHA mismatch: {subject_digest}")

    subject_pixels = int(np.count_nonzero(subject))
    failures: list[str] = []
    metrics: dict[str, Any] = {}
    source_exact_green = np.all(source == GREEN, axis=2)
    outside_green_violations = int(np.count_nonzero((~subject) & (~source_exact_green)))
    inside_green_violations = int(np.count_nonzero(subject & source_exact_green))
    metrics["locked_authority_green"] = {
        "outside_subject_non_exact_green_pixels": outside_green_violations,
        "inside_subject_exact_green_pixels": inside_green_violations,
    }
    if outside_green_violations:
        failures.append(f"locked source exterior has {outside_green_violations} non-#00FF00 pixels")
    if inside_green_violations:
        failures.append(f"locked source subject contains {inside_green_violations} #00FF00 pixels")

    for name, mask in parts.items():
        outside = int(np.count_nonzero(mask & ~subject))
        green_inside = int(np.count_nonzero(mask & source_exact_green))
        component = component_metrics(mask)
        ratio = float(component["pixels"]) / float(max(1, subject_pixels))
        rules = ROLE_RULES[name]
        low, high = rules["fraction"]
        bbox = component["bbox_xyxy_exclusive"]
        bbox_names = ("x0", "y0", "x1", "y1")
        bbox_checks = {
            key: bool(rules["bbox_edges"][key][0] <= bbox[index] <= rules["bbox_edges"][key][1])
            for index, key in enumerate(bbox_names)
        }
        positive_checks = {
            f"{point[0]},{point[1]}": mask_contains_point(mask, point, 16.0)
            for point in rules["positive"]
        }
        negative_checks = {
            f"{point[0]},{point[1]}": not mask_contains_point(mask, point, 10.0)
            for point in rules["negative"]
        }
        metrics[name] = {
            **component,
            "subject_fraction": ratio,
            "outside_subject_pixels": outside,
            "exact_green_inside_pixels": green_inside,
            "bbox_role_checks": bbox_checks,
            "positive_landmark_checks": positive_checks,
            "negative_landmark_checks": negative_checks,
        }
        if outside:
            failures.append(f"{name}: {outside} pixels outside approved subject")
        if green_inside:
            failures.append(f"{name}: {green_inside} exact-green pixels included")
        if not low <= ratio <= high:
            failures.append(f"{name}: subject fraction {ratio:.6f} outside {low:.3f}-{high:.3f}")
        if not all(bbox_checks.values()):
            failures.append(f"{name}: role bbox outside locked envelope {bbox_checks}")
        if not all(positive_checks.values()):
            failures.append(f"{name}: misses positive role landmarks")
        if not all(negative_checks.values()):
            failures.append(f"{name}: enters forbidden role landmarks")
        if name == "rifle":
            # Visible rifle pixels may split where the two hands occlude the
            # weapon. The rigid union below, not rifle-only alpha, must become
            # one connected assembly.
            if not 1 <= component["significant_components"] <= 3:
                failures.append(
                    f"{name}: significant components {component['significant_components']} outside 1-3"
                )
            component_floor = 0.55
        else:
            if component["significant_components"] != 1:
                failures.append(f"{name}: significant components {component['significant_components']} != 1")
            component_floor = 0.98
        if component["largest_component_ratio"] < component_floor:
            failures.append(
                f"{name}: largest component ratio {component['largest_component_ratio']:.6f} < {component_floor:.2f}"
            )

    rifle = parts["rifle"]
    union = rifle | parts["trigger_forearm_hand"] | parts["support_forearm_hand"]
    union_closed = cv2.morphologyEx(union.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    union_metrics = component_metrics(union_closed)
    union_fraction = float(np.count_nonzero(union)) / float(max(1, subject_pixels))
    union_metrics["subject_fraction"] = union_fraction
    metrics["rigid_union_after_2px_close"] = union_metrics
    if not 0.10 <= union_fraction <= 0.45:
        failures.append(f"rigid union subject fraction {union_fraction:.6f} outside 0.10-0.45")
    if union_metrics["significant_components"] != 1:
        failures.append(f"rigid union significant components {union_metrics['significant_components']} != 1")
    if union_metrics["largest_component_ratio"] < 0.995:
        failures.append(f"rigid union largest component ratio {union_metrics['largest_component_ratio']:.6f} < 0.995")

    overlap_records: dict[str, int] = {}
    names = list(parts)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            overlap = int(np.count_nonzero(parts[first] & parts[second]))
            overlap_records[f"{first}__{second}"] = overlap
            if overlap:
                failures.append(f"undeclared semantic overlap {first}/{second}: {overlap} pixels")
    metrics["part_overlaps"] = overlap_records

    corridor = corridor_metrics(rifle, subject, union_closed, INNER, MUZZLE)
    corridor["inner_anchor_within_20px"] = near_point(rifle, INNER, 20.0)
    corridor["muzzle_anchor_within_40px"] = near_point(rifle, MUZZLE, 40.0)
    metrics["se_rifle_anchor_corridor"] = corridor
    if not corridor["inner_anchor_within_20px"]:
        failures.append("rifle mask misses locked inner anchor")
    if not corridor["muzzle_anchor_within_40px"]:
        failures.append("rifle mask misses locked muzzle anchor envelope")
    if corridor["support_ratio"] < 0.85:
        failures.append(f"rifle native corridor support {corridor['support_ratio']:.6f} < 0.85")
    if corridor["raster_tangent_residual_degrees"] > 6.0:
        failures.append(
            f"rifle raster tangent residual {corridor['raster_tangent_residual_degrees']:.4f} > 6 degrees"
        )
    if corridor["maximum_consecutive_empty_projection_bins"] > 3:
        failures.append(
            "rifle centreline maximum consecutive empty projection bins "
            f"{corridor['maximum_consecutive_empty_projection_bins']} > 3"
        )
    if not corridor["inner_muzzle_same_rifle_component"]:
        failures.append("locked inner and muzzle envelopes are not in one closed rigid-union component")
    if corridor["muzzle_hardware_significant_clusters"] != 1:
        failures.append(
            "muzzle hardware significant clusters "
            f"{corridor['muzzle_hardware_significant_clusters']} != 1"
        )

    result = "PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD" if not failures else "FAIL"
    build_review(source, subject, rifle, parts["trigger_forearm_hand"], parts["support_forearm_hand"], review_path, result, failures)
    missing_masks = [name for name in REQUIRED_CONTRACT_MASKS if name not in CHECKED_MASKS]
    qa = {
        "schema": 1,
        "role": "ASTER Fire16 locked-SE preliminary three-part source-mask QA",
        "result": result,
        "candidate_status": "HOLD",
        "promotion_ready": False,
        "visual_gate": "HOLD_USER_VISUAL_REVIEW_REQUIRED",
        "contract_complete": False,
        "checked_contract_masks": CHECKED_MASKS,
        "missing_contract_masks": missing_masks,
        "source_size": list(EXPECTED_SIZE),
        "costume_id": "ASTER_COMBAT_SUIT_C01",
        "source_subject_pixels": subject_pixels,
        "locked_se_rifle": {
            "inner_xy": INNER.tolist(),
            "muzzle_xy": MUZZLE.tolist(),
            "tangent_degrees": EXPECTED_TANGENT,
        },
        "paths": {name: path.relative_to(PROJECT_ROOT).as_posix() for name, path in paths.items()},
        "sha256": {
            "source": source_digest,
            "subject_mask": subject_digest,
            "rifle_mask": part_digests["rifle"],
            "trigger_mask": part_digests["trigger_forearm_hand"],
            "support_mask": part_digests["support_forearm_hand"],
        },
        "metrics": metrics,
        "failures": failures,
        "review": review_path.relative_to(PROJECT_ROOT).as_posix(),
        "review_sha256": sha256(review_path),
        "review_resolution": [1920, 1440],
        "native_panel": {"xy": [24, 88], "resolution": [1254, 1254], "scale": "1:1"},
        "runtime_panel": {"xy": [1302, 88], "resolution": [384, 384], "scale": "1:1 inspection"},
        "gameplay_panel": {"xy": [1710, 88], "resolution": [131, 131], "scale": "1:1 inspection"},
        "network_used": False,
        "server_used": False,
        "runtime_promotion": False,
    }
    atomic_write_json(qa, qa_path)
    print(json.dumps({"result": result, "failures": len(failures), "qa": str(qa_path)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
