#!/usr/bin/env python3
"""Assemble the immutable ASTER Fire16 locked-SE 17-role source-mask contract.

This builder copies the twelve reviewed hard semantic masks, derives BODY_CORE
as the exact remainder of the locked subject, derives a narrow shoulder/elbow
seam exception band, and derives target occlude/reveal masks from the locked
SSE rigid-cluster similarity matrix.  It creates source-mask evidence only;
it does not generate pixels, composite an SSE body, start a server, or promote
anything to runtime.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1"
)
FULL_ROOT = SEMANTIC_ROOT / "manual_full_contract_v1"
UPPER_ROOT = FULL_ROOT / "upper_identity_staging"
LOWER_ROOT = FULL_ROOT / "lower_costume_staging"
FALLBACK_ROOT = SEMANTIC_ROOT / "manual_fallback_v1"
RIGID_ROOT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_rigid_cluster_preview_v1"
)
OUT = FULL_ROOT / "accepted_v1"

SOURCE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
SUBJECT = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/masks/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_MASK.png"
)
UPPER_MANIFEST = UPPER_ROOT / "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_MANIFEST.json"
LOWER_MANIFEST = LOWER_ROOT / "ASTER_FIRE_SE_LOWER_COSTUME_MASKS_V1_MANIFEST.json"
FALLBACK_MANIFEST = FALLBACK_ROOT / "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_MANIFEST.json"
RIGID_MANIFEST = RIGID_ROOT / "ASTER_FIRE_SSE_RIGID_CLUSTER_PREVIEW_V1_MANIFEST.json"
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

EXPECTED_SIZE = (1254, 1254)
REVIEW_SIZE = (1920, 1440)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
RESULT = "PASS_FULL_SE_SOURCE_MASK_CONTRACT_ONLY_HOLD"

EXPECTED_SOURCE_SHA256 = "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838"
EXPECTED_SUBJECT_SHA256 = "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5"
EXPECTED_MANIFEST_SHA256 = {
    UPPER_MANIFEST: "a8b116459b21d29ce0c4e00489323ebe9d0ea5c8090ae6b2875da07cb68ccc41",
    LOWER_MANIFEST: "dd4236eeb3e9e1b751f07b8edcdba284655e8fb50cd01ce206424a554f11261a",
    FALLBACK_MANIFEST: "6e463e3bd7bca1fbbfaa4c069d6fb082c29fc8f85fec2e37cc9f48a62ad26c50",
    RIGID_MANIFEST: "ca7d3b784ca355d226253d549dcf2447cd116349d3c770c50c4e18e6e137ea9f",
}

PRIMARY_INPUTS = {
    "HAIR_BACK": (
        UPPER_ROOT / "ASTER_FIRE_SE_HAIR_BACK_MANUAL_V1_MASK.png",
        "c07b9cdf5d1f1359421d055d8cdad1456a8b1af147d0ddf919850985a557baec",
        "upper_identity_staging",
    ),
    "HEAD_FACE": (
        UPPER_ROOT / "ASTER_FIRE_SE_HEAD_FACE_MANUAL_V1_MASK.png",
        "77d0616a0add94d81769e713c95befe3967cbb036bc64cd35e85f3ce43d2a240",
        "upper_identity_staging",
    ),
    "HAIR_FRONT": (
        UPPER_ROOT / "ASTER_FIRE_SE_HAIR_FRONT_MANUAL_V1_MASK.png",
        "768d788c8cc07ca91f960ea72be42579f0c1f00f679621ba3b8886bf7879802a",
        "upper_identity_staging",
    ),
    "ARM_TRIGGER_UPPER": (
        UPPER_ROOT / "ASTER_FIRE_SE_ARM_TRIGGER_UPPER_MANUAL_V1_MASK.png",
        "157b0ad58aff0e62f0f31fbd4e06ce5fa689d1160a715096ed76103d4cc5f345",
        "upper_identity_staging",
    ),
    "ARM_SUPPORT_UPPER": (
        UPPER_ROOT / "ASTER_FIRE_SE_ARM_SUPPORT_UPPER_MANUAL_V1_MASK.png",
        "d88d026ae328edc2ac72a99b42ce5deeaf7a5289c433a6946bc024431c5a67d5",
        "upper_identity_staging",
    ),
    "SHOULDER_PLATE": (
        UPPER_ROOT / "ASTER_FIRE_SE_SHOULDER_PLATE_MANUAL_V1_MASK.png",
        "7ae08d4ec3cece3309eb85932ba9d7754a8421d57094fd716e50c07ce51a5962",
        "upper_identity_staging",
    ),
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE": (
        LOWER_ROOT / "ASTER_FIRE_SE_ANATOMICAL_LEFT_WHITE_LEG_MODULE_V1_MASK.png",
        "9269873f74bfa7017435b8b56231c295e5ed31104b6ccc2672022254ea967a26",
        "lower_costume_staging",
    ),
    "OPPOSITE_STRAPS_POUCH_LEG": (
        LOWER_ROOT / "ASTER_FIRE_SE_OPPOSITE_STRAPS_POUCH_LEG_V1_MASK.png",
        "44d733b3f0f9480abcd8406c176420b8fac556ebd84141a5aee008d58a1c6ea2",
        "lower_costume_staging",
    ),
    "BOOTS_ACCESSORIES": (
        LOWER_ROOT / "ASTER_FIRE_SE_BOOTS_ACCESSORIES_V1_MASK.png",
        "16bc92cae8551152ef7c34523d09d95fdb00d5ca16cfdcf45baa7ea0bc200aeb",
        "lower_costume_staging",
    ),
    "RIFLE": (
        FALLBACK_ROOT / "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png",
        "51876f84ba9fe1f5c3d300bc4057950e500bb655d58162547f59d6e4c52b55c6",
        "manual_fallback_v1",
    ),
    "TRIGGER_FOREARM_HAND": (
        FALLBACK_ROOT / "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
        "5ececa81d3870a91d91a7f799e8e41f15cb7c54dc2f32999110b8bdaf6d078e9",
        "manual_fallback_v1",
    ),
    "SUPPORT_FOREARM_HAND": (
        FALLBACK_ROOT / "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
        "bc5feaf79f9264a84fa22e6f58493378687f5a20ba488637c25bf41abbea83b9",
        "manual_fallback_v1",
    ),
}

PRIMARY_ROLES = tuple(PRIMARY_INPUTS)
DERIVED_ROLES = (
    "BODY_CORE",
    "SHOULDER_ELBOW_SEAM_BRIDGE",
    "TARGET_OCCLUDE",
    "TARGET_REVEAL",
)
ALL_ROLES = ("SUBJECT",) + PRIMARY_ROLES + DERIVED_ROLES
RIGID_ROLES = ("RIFLE", "TRIGGER_FOREARM_HAND", "SUPPORT_FOREARM_HAND")

LOCKED_SIMILARITY_MATRIX = np.asarray(
    (
        (0.819538462095366, -0.6029075341936835, 349.78853886295576),
        (0.6029075341936835, 0.819538462095366, -310.6517236724445),
    ),
    dtype=np.float64,
)
RECEIVER_UNDER_FLAP_STRAP_ROI_XYXY = (430, 438, 518, 524)
SEAM_DILATION_RADIUS_PX = 6

QA_NAME = "ASTER_FIRE_SE_FULL_CONTRACT_V1_QA.json"
MANIFEST_NAME = "ASTER_FIRE_SE_FULL_CONTRACT_V1_MANIFEST.json"
REVIEW_NAME = "ASTER_FIRE_SE_FULL_CONTRACT_V1_REVIEW_1920X1440.png"
EVIDENCE_NAME = "ASTER_FIRE_SE_FULL_CONTRACT_V1_EVIDENCE_1080P_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def load_rgb(path: Path, expected_sha: str) -> np.ndarray:
    if not path.is_file() or sha256(path) != expected_sha:
        raise RuntimeError(f"locked RGB input missing or SHA mismatch: {path}")
    with Image.open(path) as image:
        image.load()
        if image.mode != "RGB" or image.size != EXPECTED_SIZE:
            raise RuntimeError(
                f"locked RGB input mismatch: {relative(path)} mode={image.mode} size={image.size}"
            )
        return np.asarray(image, dtype=np.uint8).copy()


def load_binary_l(path: Path, expected_sha: str) -> np.ndarray:
    if not path.is_file() or sha256(path) != expected_sha:
        raise RuntimeError(f"locked L input missing or SHA mismatch: {path}")
    with Image.open(path) as image:
        image.load()
        if image.mode != "L" or image.size != EXPECTED_SIZE:
            raise RuntimeError(
                f"locked mask mismatch: {relative(path)} mode={image.mode} size={image.size}"
            )
        raw = np.asarray(image, dtype=np.uint8).copy()
    values = set(np.unique(raw).tolist())
    if values - {0, 255}:
        raise RuntimeError(f"locked mask is not binary L {{0,255}}: {relative(path)} {sorted(values)}")
    return raw == 255


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        json.loads(temporary.read_text(encoding="utf-8"))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_mask(path: Path, mask: np.ndarray) -> None:
    temporary = path.with_name(path.name + ".tmp.png")
    try:
        Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), mode="L").save(
            temporary, "PNG", optimize=True
        )
        with Image.open(temporary) as check:
            check.load()
            if check.mode != "L" or check.size != EXPECTED_SIZE:
                raise RuntimeError(f"generated mask decode mismatch: {path.name}")
            if set(np.unique(np.asarray(check, dtype=np.uint8)).tolist()) - {0, 255}:
                raise RuntimeError(f"generated mask is not binary: {path.name}")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def output_name(role: str) -> str:
    return f"ASTER_FIRE_SE_{role}_MANUAL_FULL_CONTRACT_V1_MASK.png"


def component_metrics(mask: np.ndarray) -> dict[str, Any]:
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), 8
    )
    areas = sorted((int(row[cv2.CC_STAT_AREA]) for row in stats[1:]), reverse=True)
    ys, xs = np.nonzero(mask)
    bbox = [0, 0, 0, 0]
    if xs.size:
        bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    pixels = int(np.count_nonzero(mask))
    return {
        "pixels": pixels,
        "components": max(0, count - 1),
        "significant_components_40px": len([area for area in areas if area >= 40]),
        "largest_component_ratio": float(areas[0] / max(1, pixels)) if areas else 0.0,
        "bbox_xyxy_exclusive": bbox,
    }


def validate_lineage_manifests() -> dict[str, dict[str, Any]]:
    manifests: dict[str, dict[str, Any]] = {}
    for path, expected_sha in EXPECTED_MANIFEST_SHA256.items():
        if not path.is_file() or sha256(path) != expected_sha:
            raise RuntimeError(f"locked lineage manifest missing or SHA mismatch: {path}")
        manifests[path.name] = read_json(path)

    upper = manifests[UPPER_MANIFEST.name]
    lower = manifests[LOWER_MANIFEST.name]
    fallback = manifests[FALLBACK_MANIFEST.name]
    rigid = manifests[RIGID_MANIFEST.name]
    if upper.get("result") != "PASS_SIX_UPPER_IDENTITY_MASKS_STAGING_HOLD":
        raise RuntimeError("upper identity staging gate is not at the locked PASS/HOLD result")
    if lower.get("result") != "PASS_LOWER_COSTUME_SOURCE_MASK_CHECKS_ONLY_HOLD":
        raise RuntimeError("lower costume staging gate is not at the locked PASS/HOLD result")
    if fallback.get("technical_result") != "PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD":
        raise RuntimeError("manual fallback gate is not at the locked PASS/HOLD result")
    if rigid.get("qa", {}).get("result") != "PASS_STRUCTURAL_GEOMETRY_ONLY_HOLD":
        raise RuntimeError("rigid preview gate is not at the locked structural PASS/HOLD result")

    matrix = np.asarray(rigid.get("similarity", {}).get("matrix_2x3"), dtype=np.float64)
    if matrix.shape != (2, 3) or not np.array_equal(matrix, LOCKED_SIMILARITY_MATRIX):
        raise RuntimeError("rigid preview similarity matrix differs from the locked matrix")

    for role, (path, expected_sha, lineage) in PRIMARY_INPUTS.items():
        if lineage == "upper_identity_staging":
            record = upper.get("parts", {}).get(role, {})
        elif lineage == "lower_costume_staging":
            record = lower.get("outputs", {}).get(role, {})
        else:
            record = fallback.get("parts", {}).get(role.lower(), {})
        if record.get("path") != relative(path) or record.get("sha256") != expected_sha:
            raise RuntimeError(f"lineage manifest path/SHA mismatch for {role}")
    return manifests


def derive_seam(primary: dict[str, np.ndarray], subject: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (SEAM_DILATION_RADIUS_PX * 2 + 1, SEAM_DILATION_RADIUS_PX * 2 + 1),
    )
    pairs = (
        ("ARM_TRIGGER_UPPER", "TRIGGER_FOREARM_HAND"),
        ("ARM_SUPPORT_UPPER", "SUPPORT_FOREARM_HAND"),
    )
    seam = np.zeros(subject.shape, dtype=bool)
    pair_metrics: dict[str, Any] = {}
    for upper_role, forearm_role in pairs:
        upper = primary[upper_role]
        forearm = primary[forearm_role]
        upper_dilated = cv2.dilate(upper.astype(np.uint8), kernel) > 0
        forearm_dilated = cv2.dilate(forearm.astype(np.uint8), kernel) > 0
        pair = upper_dilated & forearm_dilated & subject
        distance_to_upper = cv2.distanceTransform((~upper).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        distance_to_forearm = cv2.distanceTransform((~forearm).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        pair_metrics[f"{upper_role}__{forearm_role}"] = {
            "pixels": int(np.count_nonzero(pair)),
            "max_distance_to_upper_px": float(distance_to_upper[pair].max()) if np.any(pair) else None,
            "max_distance_to_forearm_px": float(distance_to_forearm[pair].max()) if np.any(pair) else None,
        }
        seam |= pair
    return seam, {
        "derivation": (
            "union((dilate(UPPER, radius=6) intersection dilate(FOREARM_HAND, radius=6)) "
            "intersection SUBJECT) for trigger/support pairs"
        ),
        "native_dilation_radius_each_side_px": SEAM_DILATION_RADIUS_PX,
        "declared_full_boundary_band_max_px": SEAM_DILATION_RADIUS_PX * 2,
        "pairs": pair_metrics,
    }


def tint(image: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float) -> None:
    image[mask] = np.clip(
        image[mask].astype(np.float32) * (1.0 - alpha)
        + np.asarray(color, dtype=np.float32) * alpha,
        0,
        255,
    ).astype(np.uint8)


def build_review(
    source_rgb: np.ndarray,
    masks: dict[str, np.ndarray],
    receiver_report: dict[str, Any],
    partition_report: dict[str, Any],
    output: Path,
) -> None:
    native = source_rgb.copy()
    colors = {
        "HAIR_BACK": (145, 70, 255),
        "HEAD_FACE": (255, 105, 145),
        "HAIR_FRONT": (205, 120, 255),
        "ARM_TRIGGER_UPPER": (0, 215, 255),
        "ARM_SUPPORT_UPPER": (255, 170, 0),
        "SHOULDER_PLATE": (250, 250, 250),
        "ANATOMICAL_LEFT_WHITE_LEG_MODULE": (255, 40, 210),
        "OPPOSITE_STRAPS_POUCH_LEG": (255, 145, 30),
        "BOOTS_ACCESSORIES": (30, 225, 255),
        "RIFLE": (90, 255, 80),
        "TRIGGER_FOREARM_HAND": (0, 255, 215),
        "SUPPORT_FOREARM_HAND": (255, 230, 40),
    }
    for role in PRIMARY_ROLES:
        tint(native, masks[role], colors[role], 0.42)
        contours, _ = cv2.findContours(
            masks[role].astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(native, contours, -1, colors[role], 1)

    exception_colors = {
        "SHOULDER_ELBOW_SEAM_BRIDGE": (255, 255, 255),
        "TARGET_OCCLUDE": (255, 20, 20),
        "TARGET_REVEAL": (20, 150, 255),
    }
    for role, color in exception_colors.items():
        contours, _ = cv2.findContours(
            masks[role].astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(native, contours, -1, color, 2)

    x1, y1, x2, y2 = RECEIVER_UNDER_FLAP_STRAP_ROI_XYXY
    cv2.rectangle(native, (x1, y1), (x2 - 1, y2 - 1), (255, 0, 255), 2)

    canvas = Image.new("RGB", REVIEW_SIZE, (12, 17, 23))
    canvas.paste(Image.fromarray(native, mode="RGB"), (24, 88))
    receiver_crop = native[y1:y2, x1:x2]
    trigger_crop = native[260:440, 270:470]
    support_crop = native[380:540, 580:780]
    canvas.paste(Image.fromarray(receiver_crop, mode="RGB"), (1320, 104))
    canvas.paste(Image.fromarray(trigger_crop, mode="RGB"), (1320, 252))
    canvas.paste(Image.fromarray(support_crop, mode="RGB"), (1544, 252))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    white, muted, amber, cyan = (245, 247, 250), (185, 195, 205), (255, 188, 65), (70, 225, 245)
    draw.text((24, 20), "ASTER FIRE16 LOCKED-SE FULL 17-ROLE SOURCE MASK CONTRACT V1", fill=white, font=font)
    draw.text((24, 43), "SOURCE MASK CONTRACT ONLY / HOLD — no runtime promotion, composite, or visual PASS", fill=amber, font=font)
    draw.text((24, 68), "NATIVE 1254x1254 PANEL AT 1:1", fill=cyan, font=font)
    draw.text((1320, 82), "Receiver-under flap/strap ROI at native 1:1", fill=white, font=font)
    draw.text((1320, 228), "Trigger and support seam bands at native 1:1", fill=white, font=font)

    x, y = 1320, 445
    lines = [
        f"RESULT: {RESULT}",
        "COSTUME: ASTER_COMBAT_SUIT_C01 (identity/asymmetry locked)",
        f"17 roles present; 12 primary hard masks overlap={partition_report['primary_pairwise_overlap_pixels']}",
        f"Hard union + BODY_CORE miss={partition_report['partition_miss_pixels']}",
        f"Hard union + BODY_CORE overlap={partition_report['partition_overlap_pixels']}",
        f"Receiver ROI subject px={receiver_report['subject_pixels']}",
        f"Receiver ROI BODY_CORE px={receiver_report['body_core_pixels']}",
        f"Receiver BODY_CORE coverage={receiver_report['body_core_fraction_of_subject']:.6f}",
        "WHITE contours: SHOULDER_ELBOW_SEAM_BRIDGE (declared exception)",
        "RED contours: TARGET_OCCLUDE (declared exception)",
        "ORANGE/BLUE contours: TARGET_REVEAL (declared exception)",
        "Rigid transform is the locked SSE preview 2x3 similarity matrix.",
        "Exact-green inclusion: 0 pixels for every mask.",
        "No model, network, server, generation, upscale, or source mutation.",
        "Visual quality is not approved by this technical sheet.",
    ]
    for index, line in enumerate(lines):
        draw.text((x, y + index * 23), line, fill=amber if index in {0, 14} else muted, font=font)

    y = 820
    for index, role in enumerate(ALL_ROLES):
        record = component_metrics(masks[role])
        draw.text(
            (1320, y + index * 24),
            f"{index + 1:02d} {role}: {record['pixels']} px",
            fill=colors.get(role, exception_colors.get(role, muted)),
            font=font,
        )

    temporary = output.with_name(output.name + ".tmp.png")
    try:
        canvas.save(temporary, "PNG", optimize=True)
        with Image.open(temporary) as check:
            check.load()
            if check.mode != "RGB" or check.size != REVIEW_SIZE:
                raise RuntimeError("review decode/resolution mismatch")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    if OUT.exists():
        if not OUT.is_dir():
            raise SystemExit(f"refusing non-directory accepted-v1 collision: {OUT}")
        if any(OUT.iterdir()):
            raise SystemExit(
                f"accepted_v1 is immutable and non-empty; use a new version instead of overwriting: {OUT}"
            )
        OUT.rmdir()

    manifests = validate_lineage_manifests()
    source_rgb = load_rgb(SOURCE, EXPECTED_SOURCE_SHA256)
    subject = load_binary_l(SUBJECT, EXPECTED_SUBJECT_SHA256)
    exact_green = np.all(source_rgb == EXACT_GREEN[None, None, :], axis=2)
    if np.count_nonzero(subject & exact_green):
        raise RuntimeError("locked subject contains exact-green authority pixels")

    primary = {
        role: load_binary_l(path, expected_sha)
        for role, (path, expected_sha, _lineage) in PRIMARY_INPUTS.items()
    }
    failures: list[str] = []
    for role, mask in primary.items():
        outside = int(np.count_nonzero(mask & ~subject))
        green = int(np.count_nonzero(mask & exact_green))
        if not np.any(mask):
            failures.append(f"{role}: empty primary mask")
        if outside:
            failures.append(f"{role}: {outside} pixels outside SUBJECT")
        if green:
            failures.append(f"{role}: {green} exact-green pixels")

    pairwise: dict[str, int] = {}
    for index, first in enumerate(PRIMARY_ROLES):
        for second in PRIMARY_ROLES[index + 1 :]:
            overlap = int(np.count_nonzero(primary[first] & primary[second]))
            pairwise[f"{first}__{second}"] = overlap
            if overlap:
                failures.append(f"primary hard-mask overlap {first}/{second}: {overlap}")

    primary_union = np.logical_or.reduce(tuple(primary.values()))
    body_core = subject & ~primary_union
    partition_union = primary_union | body_core
    partition_miss = int(np.count_nonzero(subject & ~partition_union))
    partition_outside = int(np.count_nonzero(partition_union & ~subject))
    partition_overlap = int(np.count_nonzero(primary_union & body_core))
    if partition_miss or partition_outside or partition_overlap:
        failures.append(
            f"hard/BODY_CORE partition failure miss={partition_miss} outside={partition_outside} overlap={partition_overlap}"
        )

    x1, y1, x2, y2 = RECEIVER_UNDER_FLAP_STRAP_ROI_XYXY
    roi_subject = subject[y1:y2, x1:x2]
    roi_body = body_core[y1:y2, x1:x2]
    receiver_report = {
        "roi_xyxy_exclusive": list(RECEIVER_UNDER_FLAP_STRAP_ROI_XYXY),
        "semantic_decision": "receiver-under non-weapon flap/strap remains owned by BODY_CORE",
        "subject_pixels": int(np.count_nonzero(roi_subject)),
        "body_core_pixels": int(np.count_nonzero(roi_body)),
        "body_core_fraction_of_subject": float(
            np.count_nonzero(roi_body) / max(1, np.count_nonzero(roi_subject))
        ),
        "minimum_required_body_core_pixels": 4000,
        "minimum_required_fraction": 0.75,
    }
    if receiver_report["body_core_pixels"] < receiver_report["minimum_required_body_core_pixels"]:
        failures.append("receiver-under flap/strap BODY_CORE pixel support is insufficient")
    if receiver_report["body_core_fraction_of_subject"] < receiver_report["minimum_required_fraction"]:
        failures.append("receiver-under flap/strap BODY_CORE coverage fraction is insufficient")

    seam, seam_report = derive_seam(primary, subject)
    if not np.any(seam):
        failures.append("SHOULDER_ELBOW_SEAM_BRIDGE is empty")
    for pair_name, record in seam_report["pairs"].items():
        if record["pixels"] <= 0:
            failures.append(f"seam pair is empty: {pair_name}")
        if record["max_distance_to_upper_px"] is None or record["max_distance_to_upper_px"] > 6.5:
            failures.append(f"seam band escaped upper boundary radius: {pair_name}")
        if record["max_distance_to_forearm_px"] is None or record["max_distance_to_forearm_px"] > 6.5:
            failures.append(f"seam band escaped forearm boundary radius: {pair_name}")

    source_rigid_cluster = np.logical_or.reduce(tuple(primary[role] for role in RIGID_ROLES))
    warped_cluster = cv2.warpAffine(
        np.where(source_rigid_cluster, 255, 0).astype(np.uint8),
        LOCKED_SIMILARITY_MATRIX,
        EXPECTED_SIZE,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    ) == 255
    target_occlude = warped_cluster & (subject & ~source_rigid_cluster)
    target_reveal = source_rigid_cluster & ~warped_cluster

    masks = {
        "SUBJECT": subject,
        **primary,
        "BODY_CORE": body_core,
        "SHOULDER_ELBOW_SEAM_BRIDGE": seam,
        "TARGET_OCCLUDE": target_occlude,
        "TARGET_REVEAL": target_reveal,
    }
    if tuple(masks) != ALL_ROLES:
        raise RuntimeError(f"internal role order/set mismatch: {tuple(masks)}")

    exception_metrics: dict[str, Any] = {}
    for role in ("SHOULDER_ELBOW_SEAM_BRIDGE", "TARGET_OCCLUDE", "TARGET_REVEAL"):
        mask = masks[role]
        outside = int(np.count_nonzero(mask & ~subject))
        green = int(np.count_nonzero(mask & exact_green))
        exception_metrics[role] = {
            "outside_subject_pixels": outside,
            "exact_green_pixels": green,
            "overlap_with_primary_hard_union_pixels": int(np.count_nonzero(mask & primary_union)),
            "overlap_with_BODY_CORE_pixels": int(np.count_nonzero(mask & body_core)),
            **component_metrics(mask),
        }
        if not np.any(mask):
            failures.append(f"{role}: declared exception mask is empty")
        if outside:
            failures.append(f"{role}: {outside} pixels outside SUBJECT")
        if green:
            failures.append(f"{role}: {green} exact-green pixels")

    output_metrics: dict[str, Any] = {}
    for role, mask in masks.items():
        output_metrics[role] = {
            **component_metrics(mask),
            "outside_subject_pixels": int(np.count_nonzero(mask & ~subject)),
            "exact_green_pixels": int(np.count_nonzero(mask & exact_green)),
        }
        if not np.any(mask):
            failures.append(f"{role}: output mask is empty")
        if output_metrics[role]["outside_subject_pixels"]:
            failures.append(f"{role}: output escaped SUBJECT")
        if output_metrics[role]["exact_green_pixels"]:
            failures.append(f"{role}: output includes exact-green pixels")

    partition_report = {
        "primary_hard_mask_count": len(PRIMARY_ROLES),
        "primary_pairwise_overlap_pixels": int(sum(pairwise.values())),
        "primary_hard_union_pixels": int(np.count_nonzero(primary_union)),
        "BODY_CORE_pixels": int(np.count_nonzero(body_core)),
        "SUBJECT_pixels": int(np.count_nonzero(subject)),
        "partition_miss_pixels": partition_miss,
        "partition_outside_subject_pixels": partition_outside,
        "partition_overlap_pixels": partition_overlap,
        "declared_exception_roles": [
            "SHOULDER_ELBOW_SEAM_BRIDGE",
            "TARGET_OCCLUDE",
            "TARGET_REVEAL",
        ],
    }

    if failures:
        raise RuntimeError("full source-mask contract checks failed: " + "; ".join(failures))

    FULL_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".accepted_v1_stage_", dir=FULL_ROOT))
    try:
        output_paths = {role: stage / output_name(role) for role in ALL_ROLES}
        # Preserve reviewed source mask encodings byte-for-byte wherever a role
        # is copied.  Derived roles are encoded as deterministic binary L PNGs.
        shutil.copyfile(SUBJECT, output_paths["SUBJECT"])
        for role, (path, _expected_sha, _lineage) in PRIMARY_INPUTS.items():
            shutil.copyfile(path, output_paths[role])
        for role in DERIVED_ROLES:
            save_mask(output_paths[role], masks[role])

        for role, path in output_paths.items():
            decoded = load_binary_l(path, sha256(path))
            if not np.array_equal(decoded, masks[role]):
                raise RuntimeError(f"staged output pixels differ from assembled mask: {role}")

        review_path = stage / REVIEW_NAME
        qa_path = stage / QA_NAME
        manifest_path = stage / MANIFEST_NAME
        evidence_path = stage / EVIDENCE_NAME
        build_review(source_rgb, masks, receiver_report, partition_report, review_path)

        generated_at = datetime.now(timezone.utc).isoformat()
        target_report = {
            "matrix_2x3": LOCKED_SIMILARITY_MATRIX.tolist(),
            "warp_interpolation": "INTER_NEAREST",
            "source_rigid_cluster_roles": list(RIGID_ROLES),
            "source_rigid_cluster_pixels": int(np.count_nonzero(source_rigid_cluster)),
            "warped_cluster_pixels": int(np.count_nonzero(warped_cluster)),
            "warped_cluster_outside_SUBJECT_pixels": int(np.count_nonzero(warped_cluster & ~subject)),
            "TARGET_OCCLUDE_definition": "warped_cluster intersection (SUBJECT - source_rigid_cluster)",
            "TARGET_REVEAL_definition": "source_rigid_cluster - warped_cluster",
            "TARGET_OCCLUDE_pixels": int(np.count_nonzero(target_occlude)),
            "TARGET_REVEAL_pixels": int(np.count_nonzero(target_reveal)),
        }
        qa = {
            "schema": 1,
            "generated_at_utc": generated_at,
            "role": "ASTER Fire16 locked-SE complete 17-role source semantic-mask contract technical QA",
            "result": RESULT,
            "candidate_status": "HOLD",
            "contract_complete": True,
            "contract_scope": "locked-SE source-mask set only",
            "promotion_ready": False,
            "runtime_asset": False,
            "runtime_promotion": False,
            "visual_pass": False,
            "costume_id": "ASTER_COMBAT_SUIT_C01",
            "identity_lock": {
                "mature_character_identity_preserved": True,
                "silver_split_comet_hair_roles_preserved": True,
                "canonical_anatomical_right_shoulder_plate_preserved": True,
                "anatomical_left_white_leg_module_preserved": True,
                "opposite_leg_straps_pouch_preserved": True,
                "weapon_class_and_grip_roles_preserved": True,
                "mirroring_used": False,
            },
            "role_count": len(ALL_ROLES),
            "roles": list(ALL_ROLES),
            "primary_pairwise_overlaps": pairwise,
            "partition": partition_report,
            "receiver_under_flap_strap_BODY_CORE": receiver_report,
            "seam_bridge": seam_report,
            "target_transition": target_report,
            "metrics": output_metrics,
            "declared_exception_metrics": exception_metrics,
            "exact_green_invasion_total_pixels": int(
                sum(record["exact_green_pixels"] for record in output_metrics.values())
            ),
            "failures": [],
            "prohibitions": [
                "no runtime promotion",
                "no SSE body composite",
                "no visual PASS from technical checks",
                "no source mutation",
                "no model, network, or server use",
            ],
            "review": relative(OUT / REVIEW_NAME),
            "review_resolution": list(REVIEW_SIZE),
            "native_panel": {"xy": [24, 88], "resolution": list(EXPECTED_SIZE), "scale": "1:1"},
        }
        atomic_write_json(qa_path, qa)

        validator = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                str(review_path),
                "--require-dynamic-capture",
                "--output",
                str(evidence_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if validator.returncode != 0:
            raise RuntimeError(f"1080p evidence validator failed: {validator.stdout}{validator.stderr}")
        evidence = read_json(evidence_path)
        if evidence.get("gate") != "PASS":
            raise RuntimeError(f"1080p evidence gate did not pass: {evidence.get('gate')}")
        for record in evidence.get("evidence", []):
            if Path(str(record.get("path", ""))).name == REVIEW_NAME:
                record["path"] = str(OUT / REVIEW_NAME)
        atomic_write_json(evidence_path, evidence)

        input_records: dict[str, Any] = {
            "SOURCE_RGB": {
                "path": relative(SOURCE),
                "sha256": sha256(SOURCE),
                "mode": "RGB",
                "resolution": list(EXPECTED_SIZE),
            },
            "SUBJECT": {
                "path": relative(SUBJECT),
                "sha256": sha256(SUBJECT),
                "mode": "L",
                "resolution": list(EXPECTED_SIZE),
                "binary_values": [0, 255],
            },
        }
        for role, (path, expected_sha, lineage) in PRIMARY_INPUTS.items():
            input_records[role] = {
                "path": relative(path),
                "sha256": expected_sha,
                "mode": "L",
                "resolution": list(EXPECTED_SIZE),
                "binary_values": [0, 255],
                "lineage": lineage,
            }

        manifest = {
            "schema": 1,
            "generated_at_utc": generated_at,
            "role": "ASTER Fire16 locked-SE accepted full source-mask contract v1",
            "result": RESULT,
            "candidate_status": "HOLD",
            "contract_complete": True,
            "contract_scope": "locked-SE source-mask set only",
            "promotion_ready": False,
            "runtime_asset": False,
            "runtime_promotion": False,
            "visual_pass": False,
            "costume_id": "ASTER_COMBAT_SUIT_C01",
            "builder": relative(Path(__file__).resolve()),
            "builder_sha256": sha256(Path(__file__).resolve()),
            "construction": {
                "twelve_primary_hard_masks_copied_byte_identically": True,
                "BODY_CORE_definition": "SUBJECT - union(12 primary hard semantic masks)",
                "seam_bridge_definition": seam_report["derivation"],
                "TARGET_OCCLUDE_definition": target_report["TARGET_OCCLUDE_definition"],
                "TARGET_REVEAL_definition": target_report["TARGET_REVEAL_definition"],
                "target_similarity_matrix_locked_from_rigid_preview_manifest": True,
                "model_used": False,
                "network_used": False,
                "server_used": False,
                "generation_used": False,
                "upscale_used": False,
            },
            "locked_lineage_manifests": {
                path.name: {
                    "path": relative(path),
                    "sha256": EXPECTED_MANIFEST_SHA256[path],
                    "result": manifests[path.name].get("result")
                    or manifests[path.name].get("technical_result")
                    or manifests[path.name].get("status"),
                }
                for path in EXPECTED_MANIFEST_SHA256
            },
            "locked_inputs": input_records,
            "locked_similarity": {
                "manifest": relative(RIGID_MANIFEST),
                "manifest_sha256": EXPECTED_MANIFEST_SHA256[RIGID_MANIFEST],
                "matrix_2x3": LOCKED_SIMILARITY_MATRIX.tolist(),
                "warp_interpolation": "INTER_NEAREST",
            },
            "outputs": {
                role: {
                    "path": relative(OUT / output_name(role)),
                    "sha256": sha256(path),
                    "mode": "L",
                    "resolution": list(EXPECTED_SIZE),
                    "binary_values": [0, 255],
                    "provenance": (
                        "locked byte-identical copy"
                        if role == "SUBJECT" or role in PRIMARY_ROLES
                        else "deterministically derived"
                    ),
                }
                for role, path in output_paths.items()
            },
            "partition": partition_report,
            "receiver_under_flap_strap_BODY_CORE": receiver_report,
            "seam_bridge": seam_report,
            "target_transition": target_report,
            "qa": {
                "path": relative(OUT / QA_NAME),
                "sha256": sha256(qa_path),
                "result": RESULT,
            },
            "review": {
                "path": relative(OUT / REVIEW_NAME),
                "sha256": sha256(review_path),
                "resolution": list(REVIEW_SIZE),
                "native_panel": {"xy": [24, 88], "resolution": list(EXPECTED_SIZE), "scale": "1:1"},
                "visual_pass_claimed": False,
            },
            "evidence_1080p": {
                "path": relative(OUT / EVIDENCE_NAME),
                "sha256": sha256(evidence_path),
                "gate": evidence.get("gate"),
                "quality_claim": False,
            },
            "staging_retained": {
                "upper_identity_staging": True,
                "lower_costume_staging": True,
                "manual_fallback_v1": True,
            },
            "prohibitions": [
                "no runtime promotion",
                "no SSE body composite",
                "no visual PASS from technical checks",
                "no source mutation",
            ],
        }
        atomic_write_json(manifest_path, manifest)

        os.replace(stage, OUT)
        print(
            json.dumps(
                {
                    "result": RESULT,
                    "output": str(OUT),
                    "role_count": len(ALL_ROLES),
                    "contract_complete": True,
                    "runtime_promotion": False,
                    "visual_pass": False,
                    "receiver_under_flap_strap_body_core_pixels": receiver_report["body_core_pixels"],
                    "receiver_under_flap_strap_body_core_fraction": receiver_report[
                        "body_core_fraction_of_subject"
                    ],
                },
                ensure_ascii=False,
            )
        )
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
