#!/usr/bin/env python3
"""Author ASTER SE lower-costume semantic masks without generation.

This helper is deliberately limited to the locked 1254px SE fire authority.
It authors three staging-only masks for the asymmetric lower costume, records
their anatomical roles, and emits native 1:1 review evidence.  It does not
mirror a source, generate pixels, build a midpoint composite, or promote any
asset to runtime.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/source/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_GREEN.png"
)
SUBJECT_MASK = ROOT / (
    "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire/"
    "aim_master_v2/masks/ASTER_FIRE_SE_DIRECTION_AIM_MASTER_V2_MASK.png"
)
OUT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1/manual_full_contract_v1/"
    "lower_costume_staging"
)

EXPECTED_SOURCE_SHA256 = "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838"
EXPECTED_SUBJECT_SHA256 = "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5"
EXPECTED_SIZE = (1254, 1254)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)

MASK_PATHS = {
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE": OUT
    / "ASTER_FIRE_SE_ANATOMICAL_LEFT_WHITE_LEG_MODULE_V1_MASK.png",
    "OPPOSITE_STRAPS_POUCH_LEG": OUT
    / "ASTER_FIRE_SE_OPPOSITE_STRAPS_POUCH_LEG_V1_MASK.png",
    "BOOTS_ACCESSORIES": OUT / "ASTER_FIRE_SE_BOOTS_ACCESSORIES_V1_MASK.png",
}
REVIEW = OUT / "ASTER_FIRE_SE_LOWER_COSTUME_MASKS_V1_REVIEW_1920X1440.png"
MANIFEST = OUT / "ASTER_FIRE_SE_LOWER_COSTUME_MASKS_V1_MANIFEST.json"
QA = OUT / "ASTER_FIRE_SE_LOWER_COSTUME_MASKS_V1_QA.json"

REQUIRED_CONTRACT_MASKS = (
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
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cv_read(path: Path, flags: int) -> np.ndarray | None:
    return cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), flags)


def polygon_mask(
    shape: tuple[int, int], polygons: tuple[tuple[tuple[int, int], ...], ...]
) -> np.ndarray:
    output = np.zeros(shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(output, [np.asarray(polygon, dtype=np.int32)], 1)
    return output.astype(bool)


# The canonical white module belongs to ASTER's anatomical-left leg in
# ASTER_COMBAT_SUIT_C01.  In this immutable SE source it happens to project on
# the screen-right oblique leg.  The screen position is diagnostic only and is
# never used to infer or mirror the anatomical identity.
ANATOMICAL_LEFT_WHITE_MODULE = (
    (
        (598, 550),
        (612, 551),
        (627, 576),
        (641, 611),
        (655, 651),
        (666, 692),
        (677, 740),
        (691, 786),
        (710, 820),
        (728, 860),
        (741, 902),
        (752, 942),
        (764, 963),
        (750, 969),
        (738, 947),
        (725, 910),
        (711, 872),
        (698, 836),
        (681, 807),
        (667, 777),
        (656, 736),
        (643, 698),
        (626, 665),
        (608, 632),
        (598, 594),
    ),
)

# The pouch and two thigh straps are the opposite-leg module.  They remain on
# their native source leg and are not reflected from the white module.
OPPOSITE_STRAPS_POUCH = (
    (
        (310, 578),
        (343, 572),
        (360, 591),
        (360, 636),
        (349, 675),
        (329, 704),
        (302, 699),
        (289, 676),
        (296, 633),
    ),
    (
        (346, 573),
        (371, 579),
        (370, 642),
        (346, 641),
    ),
    (
        (337, 617),
        (449, 653),
        (444, 681),
        (329, 647),
    ),
    (
        (326, 650),
        (431, 690),
        (423, 718),
        (316, 678),
    ),
)

# Both boots are authored from their own visible contours.  Their disjoint
# components are intentional; no copy or mirrored boot silhouette is used.
BOOTS = (
    (
        (221, 870),
        (275, 870),
        (296, 899),
        (303, 945),
        (293, 984),
        (269, 1025),
        (232, 1044),
        (196, 1028),
        (187, 1003),
        (198, 968),
        (211, 936),
    ),
    (
        (703, 963),
        (760, 958),
        (781, 982),
        (789, 1028),
        (813, 1087),
        (835, 1138),
        (829, 1171),
        (807, 1193),
        (771, 1198),
        (737, 1179),
        (716, 1144),
        (709, 1093),
        (713, 1031),
        (700, 991),
    ),
)


def component_metrics(mask: np.ndarray) -> dict[str, Any]:
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), 8
    )
    areas = sorted((int(row[cv2.CC_STAT_AREA]) for row in stats[1:]), reverse=True)
    ys, xs = np.nonzero(mask)
    bbox = [0, 0, 0, 0]
    if len(xs):
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    pixels = int(np.count_nonzero(mask))
    return {
        "pixels": pixels,
        "bbox_xyxy_exclusive": bbox,
        "components": max(0, count - 1),
        "significant_components_40px": len([area for area in areas if area >= 40]),
        "component_areas": areas,
        "largest_component_ratio": float(areas[0]) / float(max(1, pixels)) if areas else 0.0,
    }


def remove_small_components(mask: np.ndarray, minimum_area: int = 40) -> np.ndarray:
    """Remove isolated polygon/subject-mask edge specks from a semantic part."""
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), 8
    )
    keep = np.zeros(mask.shape, dtype=bool)
    for index in range(1, count):
        if int(stats[index, cv2.CC_STAT_AREA]) >= minimum_area:
            keep |= labels == index
    return keep


def atomic_save_image(image: Image.Image, path: Path, expected_mode: str, expected_size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp.png")
    try:
        image.save(temporary, format="PNG")
        with Image.open(temporary) as decoded:
            decoded.verify()
        with Image.open(temporary) as decoded:
            if decoded.mode != expected_mode or decoded.size != expected_size:
                raise RuntimeError(
                    f"output decode mismatch for {path.name}: mode={decoded.mode} size={decoded.size}"
                )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        json.loads(temporary.read_text(encoding="utf-8"))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_mask(path: Path, mask: np.ndarray) -> None:
    image = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), mode="L")
    atomic_save_image(image, path, "L", EXPECTED_SIZE)


def tint(image: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float) -> None:
    image[mask] = np.clip(
        image[mask].astype(np.float32) * (1.0 - alpha)
        + np.asarray(color, dtype=np.float32) * alpha,
        0,
        255,
    ).astype(np.uint8)


def build_review(
    source_rgb: np.ndarray,
    subject: np.ndarray,
    masks: dict[str, np.ndarray],
    metrics: dict[str, Any],
) -> None:
    native = source_rgb.copy()
    colors = {
        "ANATOMICAL_LEFT_WHITE_LEG_MODULE": (255, 40, 210),
        "OPPOSITE_STRAPS_POUCH_LEG": (255, 165, 30),
        "BOOTS_ACCESSORIES": (20, 225, 255),
    }
    for name, mask in masks.items():
        tint(native, mask, colors[name], 0.56)
        contours, _ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(native, contours, -1, colors[name], 2)
    subject_contours, _ = cv2.findContours(
        subject.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(native, subject_contours, -1, (255, 255, 255), 2)

    canvas = Image.new("RGB", (1920, 1440), (18, 21, 27))
    canvas.paste(Image.fromarray(native), (24, 88))

    # Original-resolution lower-body crops.  No crop is enlarged.
    opposite_crop = native[535:755, 270:490]
    module_crop = native[525:995, 560:790]
    boots_crop = native[855:1215, 165:855]
    canvas.paste(Image.fromarray(opposite_crop), (1302, 88))
    canvas.paste(Image.fromarray(module_crop), (1546, 88))
    canvas.paste(Image.fromarray(boots_crop[:, :330]), (1302, 582))
    canvas.paste(Image.fromarray(boots_crop[:, 360:690]), (1550, 582))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text(
        (24, 24),
        "ASTER FIRE16 SE LOWER COSTUME MASKS V1 — HOLD / CONTRACT INCOMPLETE",
        fill=(255, 255, 255),
        font=font,
    )
    draw.text(
        (24, 48),
        "Locked native source at 1:1. No mirroring, generation, runtime promotion, or visual PASS.",
        fill=(205, 210, 220),
        font=font,
    )
    draw.text((1302, 64), "1:1 opposite-leg pouch/straps", fill=(255, 255, 255), font=font)
    draw.text((1546, 64), "1:1 anatomical-left white module", fill=(255, 255, 255), font=font)
    draw.text((1302, 558), "1:1 native boot crops", fill=(255, 255, 255), font=font)
    draw.text((1302, 972), "MAGENTA: anatomical-left white leg module", fill=(255, 90, 225), font=font)
    draw.text((1302, 996), "ORANGE: opposite-leg straps and pouch", fill=(255, 180, 60), font=font)
    draw.text((1302, 1020), "CYAN: two independently traced boots", fill=(40, 235, 255), font=font)
    draw.text((1302, 1058), "COSTUME ID: ASTER_COMBAT_SUIT_C01", fill=(210, 215, 225), font=font)
    draw.text((1302, 1082), "Anatomical role is authoritative; screen side is diagnostic only.", fill=(210, 215, 225), font=font)
    draw.text((1302, 1106), "Candidate status: HOLD / full 17-mask contract incomplete", fill=(255, 185, 80), font=font)
    y = 1144
    for name in masks:
        record = metrics[name]
        draw.text(
            (1302, y),
            f"{name}: px={record['pixels']} bbox={record['bbox_xyxy_exclusive']}",
            fill=(205, 210, 220),
            font=font,
        )
        y += 22
        draw.text(
            (1302, y),
            f"components>=40px={record['significant_components_40px']} outside=0 overlap=0",
            fill=(205, 210, 220),
            font=font,
        )
        y += 28
    atomic_save_image(canvas, REVIEW, "RGB", (1920, 1440))


def main() -> int:
    if not SOURCE.is_file() or not SUBJECT_MASK.is_file():
        raise SystemExit("locked SE source or subject mask is unavailable")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("locked SE source SHA mismatch")
    if sha256(SUBJECT_MASK) != EXPECTED_SUBJECT_SHA256:
        raise SystemExit("locked SE subject-mask SHA mismatch")
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(
            f"lower_costume_staging already contains a candidate; refuse overwrite: {OUT}"
        )

    source_bgr = cv_read(SOURCE, cv2.IMREAD_COLOR)
    subject_raw = cv_read(SUBJECT_MASK, cv2.IMREAD_GRAYSCALE)
    if source_bgr is None or subject_raw is None:
        raise SystemExit("failed to decode locked authority inputs")
    if (source_bgr.shape[1], source_bgr.shape[0]) != EXPECTED_SIZE:
        raise SystemExit(f"source size mismatch: {source_bgr.shape}")
    if (subject_raw.shape[1], subject_raw.shape[0]) != EXPECTED_SIZE:
        raise SystemExit(f"subject-mask size mismatch: {subject_raw.shape}")
    if set(np.unique(subject_raw).tolist()) - {0, 255}:
        raise SystemExit("locked subject mask is not binary L data")

    subject = subject_raw == 255
    exact_green = np.all(source_bgr == EXACT_GREEN, axis=2)
    masks = {
        "ANATOMICAL_LEFT_WHITE_LEG_MODULE": polygon_mask(
            subject.shape, ANATOMICAL_LEFT_WHITE_MODULE
        ),
        "OPPOSITE_STRAPS_POUCH_LEG": polygon_mask(
            subject.shape, OPPOSITE_STRAPS_POUCH
        ),
        "BOOTS_ACCESSORIES": polygon_mask(subject.shape, BOOTS),
    }
    masks = {
        name: remove_small_components(mask & subject & ~exact_green)
        for name, mask in masks.items()
    }

    # Semantic masks are mutually exclusive.  The boot cuff begins below the
    # anatomical-left stripe, so boots take only pixels not already assigned to
    # the leg module.  The opposite-leg module is spatially disjoint.
    masks["BOOTS_ACCESSORIES"] &= ~masks["ANATOMICAL_LEFT_WHITE_LEG_MODULE"]
    masks["OPPOSITE_STRAPS_POUCH_LEG"] &= ~masks["BOOTS_ACCESSORIES"]

    failures: list[str] = []
    metrics: dict[str, Any] = {}
    role_rules = {
        "ANATOMICAL_LEFT_WHITE_LEG_MODULE": {
            "bbox": ((590, 620), (540, 565), (750, 775), (950, 980)),
            "significant": 1,
            "minimum_pixels": 7000,
        },
        "OPPOSITE_STRAPS_POUCH_LEG": {
            "bbox": ((285, 320), (565, 590), (420, 460), (700, 725)),
            "significant": (1, 3),
            "minimum_pixels": 9000,
        },
        "BOOTS_ACCESSORIES": {
            "bbox": ((180, 205), (860, 885), (820, 845), (1180, 1210)),
            "significant": 2,
            "minimum_pixels": 28000,
        },
    }

    for name, mask in masks.items():
        record = component_metrics(mask)
        outside = int(np.count_nonzero(mask & ~subject))
        green_inside = int(np.count_nonzero(mask & exact_green))
        record["outside_subject_pixels"] = outside
        record["exact_green_inside_pixels"] = green_inside
        metrics[name] = record
        if outside:
            failures.append(f"{name}: {outside} pixels outside approved subject")
        if green_inside:
            failures.append(f"{name}: {green_inside} exact-green pixels included")
        rules = role_rules[name]
        if record["pixels"] < rules["minimum_pixels"]:
            failures.append(
                f"{name}: {record['pixels']} pixels below {rules['minimum_pixels']}"
            )
        bbox = record["bbox_xyxy_exclusive"]
        bbox_ok = all(low <= value <= high for value, (low, high) in zip(bbox, rules["bbox"]))
        record["bbox_role_check"] = bbox_ok
        if not bbox_ok:
            failures.append(f"{name}: role bbox outside locked envelope {bbox}")
        significant = record["significant_components_40px"]
        expected_significant = rules["significant"]
        if isinstance(expected_significant, tuple):
            significant_ok = expected_significant[0] <= significant <= expected_significant[1]
        else:
            significant_ok = significant == expected_significant
        record["significant_component_role_check"] = significant_ok
        if not significant_ok:
            failures.append(
                f"{name}: significant components {significant} != {expected_significant}"
            )

    overlaps: dict[str, int] = {}
    names = list(masks)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            overlap = int(np.count_nonzero(masks[first] & masks[second]))
            overlaps[f"{first}__{second}"] = overlap
            if overlap:
                failures.append(f"semantic overlap {first}/{second}: {overlap} pixels")
    metrics["pairwise_overlaps"] = overlaps

    if failures:
        raise RuntimeError("lower-costume authoring checks failed: " + "; ".join(failures))

    OUT.mkdir(parents=True, exist_ok=True)
    for name, path in MASK_PATHS.items():
        save_mask(path, masks[name])
    build_review(cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB), subject, masks, metrics)

    checked = list(masks)
    missing = [name for name in REQUIRED_CONTRACT_MASKS if name not in checked]
    common = {
        "schema": 1,
        "role": "ASTER Fire16 locked-SE lower-costume semantic mask authoring",
        "result": "PASS_LOWER_COSTUME_SOURCE_MASK_CHECKS_ONLY_HOLD",
        "candidate_status": "HOLD",
        "promotion_ready": False,
        "visual_gate": "HOLD_USER_VISUAL_REVIEW_REQUIRED",
        "contract_complete": False,
        "runtime_promotion": False,
        "visual_pass": False,
        "costume_id": "ASTER_COMBAT_SUIT_C01",
        "source_size": list(EXPECTED_SIZE),
        "checked_contract_masks": checked,
        "missing_contract_masks": missing,
        "anatomical_lock": {
            "mirroring_used": False,
            "anatomical_left_white_leg_module": (
                "Canonical anatomical-left module; projects on source screen-right in locked SE view."
            ),
            "opposite_straps_pouch_leg": (
                "Native opposite leg in locked SE source; not derived by reflecting the white module."
            ),
            "boots_accessories": (
                "Both visible boots independently traced from the locked source."
            ),
        },
        "network_used": False,
        "model_used": False,
        "server_used": False,
    }
    qa = {
        **common,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "subject_mask": SUBJECT_MASK.relative_to(ROOT).as_posix(),
        "sha256": {
            "source": sha256(SOURCE),
            "subject_mask": sha256(SUBJECT_MASK),
            **{name: sha256(path) for name, path in MASK_PATHS.items()},
            "review": sha256(REVIEW),
        },
        "metrics": metrics,
        "failures": [],
        "review": REVIEW.relative_to(ROOT).as_posix(),
        "review_resolution": [1920, 1440],
        "native_panel": {"xy": [24, 88], "resolution": [1254, 1254], "scale": "1:1"},
    }
    atomic_write_json(qa, QA)
    manifest = {
        **common,
        "builder": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "builder_sha256": sha256(Path(__file__).resolve()),
        "inputs": {
            "source": {
                "path": SOURCE.relative_to(ROOT).as_posix(),
                "sha256": sha256(SOURCE),
                "resolution": list(EXPECTED_SIZE),
            },
            "subject_mask": {
                "path": SUBJECT_MASK.relative_to(ROOT).as_posix(),
                "sha256": sha256(SUBJECT_MASK),
                "resolution": list(EXPECTED_SIZE),
            },
        },
        "outputs": {
            name: {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "mode": "L",
                "resolution": list(EXPECTED_SIZE),
            }
            for name, path in MASK_PATHS.items()
        },
        "review": {
            "path": REVIEW.relative_to(ROOT).as_posix(),
            "sha256": sha256(REVIEW),
            "resolution": [1920, 1440],
            "native_source_scale": "1:1",
        },
        "qa": QA.relative_to(ROOT).as_posix(),
    }
    atomic_write_json(manifest, MANIFEST)
    print(
        json.dumps(
            {
                "result": common["result"],
                "output": str(OUT),
                "review": str(REVIEW),
                "contract_complete": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
