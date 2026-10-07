#!/usr/bin/env python3
"""Author six locked-SE upper/identity masks for ASTER Fire16.

This project-local helper is deliberately model-free.  It reads the immutable
1254px approved SE green master, its approved subject mask, and the accepted
three-part manual fallback masks.  It writes only a new versioned staging
package containing HAIR_BACK, HEAD_FACE, HAIR_FRONT, both upper-arm masks, and
the canonical right SHOULDER_PLATE mask.  It never edits authority pixels,
starts a server, builds an SSE composite, or promotes a runtime asset.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
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
FALLBACK = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1/manual_fallback_v1"
)
RIFLE_MASK = FALLBACK / "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png"
TRIGGER_MASK = FALLBACK / "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png"
SUPPORT_MASK = FALLBACK / "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png"
OUT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1/manual_full_contract_v1/"
    "upper_identity_staging"
)

EXPECTED_SIZE = (1254, 1254)
EXPECTED_SHA256 = {
    "source": "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838",
    "subject": "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5",
    "rifle": "51876f84ba9fe1f5c3d300bc4057950e500bb655d58162547f59d6e4c52b55c6",
    "trigger_forearm_hand": "5ececa81d3870a91d91a7f799e8e41f15cb7c54dc2f32999110b8bdaf6d078e9",
    "support_forearm_hand": "bc5feaf79f9264a84fa22e6f58493378687f5a20ba488637c25bf41abbea83b9",
}
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
CHECKED_MASKS = [
    "SUBJECT",
    "HAIR_BACK",
    "HEAD_FACE",
    "HAIR_FRONT",
    "ARM_TRIGGER_UPPER",
    "ARM_SUPPORT_UPPER",
    "RIFLE",
    "TRIGGER_FOREARM_HAND",
    "SUPPORT_FOREARM_HAND",
    "SHOULDER_PLATE",
]
MISSING_CONTRACT_MASKS = [
    "BODY_CORE",
    "ANATOMICAL_LEFT_WHITE_LEG_MODULE",
    "OPPOSITE_STRAPS_POUCH_LEG",
    "BOOTS_ACCESSORIES",
    "SHOULDER_ELBOW_SEAM_BRIDGE",
    "TARGET_OCCLUDE",
    "TARGET_REVEAL",
]
OUTPUT_FILENAMES = {
    "ASTER_FIRE_SE_HAIR_BACK_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_HEAD_FACE_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_HAIR_FRONT_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_ARM_TRIGGER_UPPER_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_ARM_SUPPORT_UPPER_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_SHOULDER_PLATE_MANUAL_V1_MASK.png",
    "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_REVIEW_1920X1440.png",
    "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_QA.json",
    "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_MANIFEST.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_image(path: Path, mode: str) -> np.ndarray:
    with Image.open(path) as opened:
        opened.load()
        if opened.mode != mode or opened.size != EXPECTED_SIZE:
            raise RuntimeError(
                f"{path} must be {mode} {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, "
                f"got {opened.mode} {opened.size}"
            )
        return np.asarray(opened, dtype=np.uint8).copy()


def polygon_mask(shape: tuple[int, int], *polygons: tuple[tuple[int, int], ...]) -> np.ndarray:
    mask = np.zeros(shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(mask, [np.asarray(polygon, dtype=np.int32)], 1)
    return mask > 0


def draw_lines(
    labels: np.ndarray,
    lines: tuple[tuple[tuple[int, int], ...], ...],
    value: int,
    width: int,
) -> None:
    for line in lines:
        cv2.polylines(labels, [np.asarray(line, dtype=np.int32)], False, value, width, cv2.LINE_8)


def grabcut_part(
    source_rgb: np.ndarray,
    subject: np.ndarray,
    possible: np.ndarray,
    foreground_polygons: tuple[tuple[tuple[int, int], ...], ...],
    foreground_lines: tuple[tuple[tuple[int, int], ...], ...],
    background_polygons: tuple[tuple[tuple[int, int], ...], ...] = (),
    background_lines: tuple[tuple[tuple[int, int], ...], ...] = (),
) -> np.ndarray:
    possible = possible & subject
    labels = np.full(subject.shape, cv2.GC_BGD, dtype=np.uint8)
    labels[possible] = cv2.GC_PR_BGD
    foreground = polygon_mask(subject.shape, *foreground_polygons) & possible
    labels[foreground] = cv2.GC_PR_FGD
    draw_lines(labels, foreground_lines, cv2.GC_FGD, 5)
    if background_polygons:
        labels[polygon_mask(subject.shape, *background_polygons)] = cv2.GC_BGD
    draw_lines(labels, background_lines, cv2.GC_BGD, 9)
    labels[~possible] = cv2.GC_BGD
    labels[~subject] = cv2.GC_BGD
    bg_model = np.zeros((1, 65), dtype=np.float64)
    fg_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(
        cv2.cvtColor(source_rgb, cv2.COLOR_RGB2BGR),
        labels,
        None,
        bg_model,
        fg_model,
        8,
        cv2.GC_INIT_WITH_MASK,
    )
    return ((labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD)) & possible & subject


def remove_small(mask: np.ndarray, minimum_area: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    keep = [index for index in range(1, count) if int(stats[index, cv2.CC_STAT_AREA]) >= minimum_area]
    return np.isin(labels, keep)


def close_mask(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    return cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel) > 0


def component_metrics(mask: np.ndarray) -> dict[str, Any]:
    count, _labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    areas = sorted((int(stats[index, cv2.CC_STAT_AREA]) for index in range(1, count)), reverse=True)
    ys, xs = np.nonzero(mask)
    return {
        "pixels": int(np.count_nonzero(mask)),
        "components": max(0, count - 1),
        "significant_components": len([area for area in areas if area >= 200]),
        "significant_component_areas": [area for area in areas if area >= 200],
        "largest_component_ratio": float(areas[0]) / float(max(1, np.count_nonzero(mask))) if areas else 0.0,
        "bbox_xyxy_exclusive": [
            int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        ] if len(xs) else [0, 0, 0, 0],
    }


def save_mask(path: Path, mask: np.ndarray) -> None:
    temporary = path.with_name(path.name + ".tmp.png")
    try:
        Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), mode="L").save(temporary)
        with Image.open(temporary) as opened:
            opened.verify()
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def tint(image: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float) -> None:
    image[mask] = np.clip(
        image[mask].astype(np.float32) * (1.0 - alpha)
        + np.asarray(color, dtype=np.float32) * alpha,
        0,
        255,
    ).astype(np.uint8)


def build_review(source: np.ndarray, parts: dict[str, np.ndarray], output: Path, result: str) -> None:
    colors = {
        "HAIR_BACK": (180, 70, 255),
        "HEAD_FACE": (255, 150, 80),
        "HAIR_FRONT": (80, 220, 255),
        "ARM_TRIGGER_UPPER": (30, 240, 100),
        "ARM_SUPPORT_UPPER": (255, 70, 190),
        "SHOULDER_PLATE": (255, 235, 40),
    }
    native = source.copy()
    for name, mask in parts.items():
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(native, contours, -1, colors[name], 3)

    head_crop = source[20:580, 120:760].copy()
    seam_crop = source[260:650, 260:790].copy()
    for name, mask in parts.items():
        tint(head_crop, mask[20:580, 120:760], colors[name], 0.52)
        tint(seam_crop, mask[260:650, 260:790], colors[name], 0.52)

    canvas = Image.new("RGB", (1920, 1440), (18, 21, 27))
    canvas.paste(Image.fromarray(native), (24, 92))
    canvas.paste(Image.fromarray(head_crop), (1300, 92))
    canvas.paste(Image.fromarray(seam_crop), (1300, 694))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 22), f"ASTER FIRE16 SE UPPER/IDENTITY MASKS V1 — {result}", fill=(255, 255, 255), font=font)
    draw.text((24, 48), "Native panel 1254x1254 at 1:1; project-local model-free authoring; HOLD only.", fill=(205, 210, 220), font=font)
    draw.text((1300, 68), "1:1 identity/shoulder crop", fill=(255, 255, 255), font=font)
    draw.text((1300, 670), "1:1 proximal seams / receiver-underbody crop", fill=(255, 255, 255), font=font)
    legend_y = 1110
    for name, color in colors.items():
        draw.rectangle((1300, legend_y, 1320, legend_y + 14), fill=color)
        draw.text((1330, legend_y), name, fill=(225, 228, 235), font=font)
        legend_y += 25
    draw.text((1300, 1270), "Trigger proximal seam: new upper-arm owns only the proximal shoulder cap.", fill=(255, 190, 90), font=font)
    draw.text((1300, 1294), "Receiver-under flap/strap: reserved for BODY_CORE; never absorbed here.", fill=(255, 190, 90), font=font)
    draw.text((1300, 1328), "CONTRACT INCOMPLETE / NO RUNTIME PROMOTION / NO VISUAL PASS", fill=(255, 120, 120), font=font)
    temporary = output.with_name(output.name + ".tmp.png")
    try:
        canvas.save(temporary)
        with Image.open(temporary) as opened:
            if opened.mode != "RGB" or opened.size != (1920, 1440):
                raise RuntimeError("review verification failed")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        json.loads(temporary.read_text(encoding="utf-8"))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    inputs = {
        "source": SOURCE,
        "subject": SUBJECT_MASK,
        "rifle": RIFLE_MASK,
        "trigger_forearm_hand": TRIGGER_MASK,
        "support_forearm_hand": SUPPORT_MASK,
    }
    for name, path in inputs.items():
        if not path.is_file():
            raise RuntimeError(f"required locked input unavailable: {path}")
        digest = sha256(path)
        if digest != EXPECTED_SHA256[name]:
            raise RuntimeError(f"{name} SHA mismatch: {digest}")
    if OUT.exists() and any(OUT.iterdir()):
        if sys.argv[1:] != ["--replace-failed"]:
            raise RuntimeError(f"immutable v1 staging already exists; refuse overwrite: {OUT}")
        qa_path = OUT / "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_QA.json"
        if not qa_path.is_file():
            raise RuntimeError("refusing failed-staging replacement without owned QA")
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        contents = list(OUT.iterdir())
        unexpected = [path for path in contents if not path.is_file() or path.name not in OUTPUT_FILENAMES]
        if qa.get("result") != "FAIL" or unexpected:
            raise RuntimeError(
                f"refusing non-FAIL or unexpected staging replacement: result={qa.get('result')} "
                f"unexpected={unexpected}"
            )
        for path in contents:
            path.unlink()
        OUT.rmdir()
    OUT.mkdir(parents=True, exist_ok=True)

    source = read_image(SOURCE, "RGB")
    subject = read_image(SUBJECT_MASK, "L") == 255
    existing = {
        "RIFLE": read_image(RIFLE_MASK, "L") == 255,
        "TRIGGER_FOREARM_HAND": read_image(TRIGGER_MASK, "L") == 255,
        "SUPPORT_FOREARM_HAND": read_image(SUPPORT_MASK, "L") == 255,
    }
    reserved_existing = np.logical_or.reduce(list(existing.values()))

    hair_back_possible = polygon_mask(
        subject.shape,
        (
            (137, 21), (422, 20), (492, 64), (508, 126), (490, 173),
            (445, 207), (402, 251), (365, 304), (324, 355), (264, 400),
            (182, 410), (132, 365), (124, 292), (145, 190), (194, 87),
        ),
    )
    hair_back = grabcut_part(
        source,
        subject,
        hair_back_possible,
        foreground_polygons=(
            ((284, 43), (411, 36), (472, 76), (475, 122), (422, 143), (329, 129)),
            ((166, 221), (264, 135), (402, 137), (426, 184), (355, 254), (245, 327), (151, 359)),
            ((167, 300), (274, 230), (367, 221), (358, 289), (266, 381), (169, 389)),
        ),
        foreground_lines=(
            ((320, 58), (402, 86), (438, 119)),
            ((196, 238), (282, 184), (374, 171), (412, 184)),
            ((171, 330), (248, 292), (324, 247), (372, 219)),
            ((199, 374), (261, 331), (318, 290)),
        ),
        background_polygons=(
            ((394, 124), (557, 124), (583, 333), (440, 359), (395, 278)),
            ((280, 285), (418, 270), (448, 430), (278, 453)),
        ),
        background_lines=(
            ((409, 147), (434, 191), (433, 242)),
            ((313, 305), (340, 344), (365, 378)),
        ),
    )
    # Preserve the dark elastic tie as part of the back-hair assembly.
    hair_tie = polygon_mask(subject.shape, ((404, 119), (465, 117), (485, 139), (472, 158), (419, 157), (397, 140)))
    hair_back |= hair_tie & subject
    hair_back = remove_small(close_mask(hair_back, 1), 35)

    hair_front_possible = polygon_mask(
        subject.shape,
        (
            (391, 119), (482, 112), (548, 143), (576, 196), (585, 259),
            (570, 319), (536, 354), (484, 356), (439, 330), (407, 291),
            (395, 231),
        ),
    )
    hair_front = grabcut_part(
        source,
        subject,
        hair_front_possible,
        foreground_polygons=(
            ((414, 144), (484, 128), (538, 160), (560, 207), (543, 230), (477, 227), (425, 210)),
            ((446, 194), (504, 178), (552, 206), (559, 248), (535, 278), (489, 267), (453, 247)),
            ((421, 227), (469, 207), (499, 239), (477, 292), (445, 322), (419, 291)),
        ),
        foreground_lines=(
            ((433, 153), (482, 144), (527, 166), (552, 201)),
            ((461, 210), (493, 227), (474, 269), (446, 304)),
            ((532, 202), (548, 235), (548, 270)),
        ),
        background_polygons=(
            ((467, 238), (533, 224), (568, 249), (570, 307), (531, 347), (476, 332), (451, 287)),
            ((573, 259), (706, 254), (711, 412), (568, 405)),
        ),
        background_lines=(
            ((480, 252), (512, 243), (548, 253)),
            ((466, 281), (492, 313), (524, 331)),
        ),
    )
    hair_front = remove_small(close_mask(hair_front, 1), 35)

    # A hand-traced visible face/ear envelope includes eyes as face pixels and
    # avoids color-threshold holes.  Hair has explicit ownership priority.
    head_face = polygon_mask(
        subject.shape,
        (
            (471, 238), (500, 226), (531, 227), (557, 243), (568, 270),
            (563, 300), (547, 326), (521, 345), (492, 339), (470, 321),
            (458, 297), (459, 269),
        ),
        ((408, 243), (430, 239), (448, 258), (451, 280), (438, 296), (416, 286), (407, 266)),
    )
    head_face &= subject & ~(hair_back | hair_front)
    head_face = remove_small(close_mask(head_face, 1), 25)

    shoulder_possible = polygon_mask(
        subject.shape,
        (
            (583, 260), (647, 254), (681, 273), (701, 306), (707, 352),
            (697, 387), (677, 409), (637, 407), (607, 386), (579, 358), (570, 307),
        ),
    )
    shoulder_plate = grabcut_part(
        source,
        subject,
        shoulder_possible,
        foreground_polygons=(
            ((603, 270), (649, 263), (679, 286), (691, 323), (679, 353), (631, 349), (596, 322)),
            ((608, 325), (672, 323), (695, 350), (687, 383), (654, 397), (620, 377)),
        ),
        foreground_lines=(
            ((609, 281), (646, 276), (675, 299)),
            ((595, 315), (635, 331), (678, 343)),
            ((626, 362), (655, 379), (678, 383)),
        ),
        background_polygons=(
            ((559, 343), (628, 344), (669, 390), (624, 421), (566, 395)),
            ((630, 389), (713, 373), (727, 480), (650, 492)),
        ),
        background_lines=(
            ((580, 358), (612, 374), (645, 395)),
            ((666, 400), (693, 424), (704, 458)),
        ),
    )
    shoulder_plate = remove_small(close_mask(shoulder_plate, 1), 30)

    trigger_upper = polygon_mask(
        subject.shape,
        (
            (299, 276), (350, 268), (391, 287), (414, 317), (423, 350),
            (400, 376), (366, 382), (337, 366), (308, 343), (292, 312),
        ),
    ) & subject
    support_upper = polygon_mask(
        subject.shape,
        (
            (623, 346), (671, 342), (701, 371), (715, 411), (724, 458),
            (713, 497), (688, 520), (660, 503), (641, 470), (628, 430), (615, 387),
        ),
    ) & subject

    # Enforce explicit semantic ownership and full disjointness.  The accepted
    # three-part masks are immutable and therefore always win any collision.
    parts = {
        "HAIR_BACK": hair_back,
        "HEAD_FACE": head_face,
        "HAIR_FRONT": hair_front,
        "ARM_TRIGGER_UPPER": trigger_upper,
        "ARM_SUPPORT_UPPER": support_upper,
        "SHOULDER_PLATE": shoulder_plate,
    }
    precedence = ["HEAD_FACE", "HAIR_FRONT", "HAIR_BACK", "SHOULDER_PLATE", "ARM_TRIGGER_UPPER", "ARM_SUPPORT_UPPER"]
    claimed = reserved_existing.copy()
    disjoint: dict[str, np.ndarray] = {}
    for name in precedence:
        mask = parts[name] & subject & ~claimed
        # The support upper arm is mostly hidden behind the rifle and accepted
        # support-hand mask.  Only its one continuous navy sleeve crescent is
        # valid; tiny residual islands are rifle apertures, not arm ownership.
        mask = remove_small(mask, 200 if name == "ARM_SUPPORT_UPPER" else 20)
        disjoint[name] = mask
        claimed |= mask
    parts = {name: disjoint[name] for name in parts}

    exact_green = np.all(source == EXACT_GREEN, axis=2)
    failures: list[str] = []
    metrics: dict[str, Any] = {}
    minimum_pixels = {
        "HAIR_BACK": 25000,
        "HEAD_FACE": 3500,
        "HAIR_FRONT": 10000,
        "ARM_TRIGGER_UPPER": 600,
        "ARM_SUPPORT_UPPER": 1000,
        "SHOULDER_PLATE": 5000,
    }
    for name, mask in parts.items():
        record = component_metrics(mask)
        record["outside_subject_pixels"] = int(np.count_nonzero(mask & ~subject))
        record["exact_green_pixels"] = int(np.count_nonzero(mask & exact_green))
        record["overlap_with_existing_three_part_pixels"] = int(np.count_nonzero(mask & reserved_existing))
        metrics[name] = record
        if record["pixels"] < minimum_pixels[name]:
            failures.append(f"{name}: {record['pixels']} pixels below {minimum_pixels[name]}")
        if record["outside_subject_pixels"] or record["exact_green_pixels"]:
            failures.append(f"{name}: subject/exact-green containment violation")
        if record["overlap_with_existing_three_part_pixels"]:
            failures.append(f"{name}: overlaps accepted three-part masks")
        if name in {"HAIR_BACK", "HAIR_FRONT", "ARM_TRIGGER_UPPER", "ARM_SUPPORT_UPPER", "SHOULDER_PLATE"}:
            if record["significant_components"] != 1 or record["largest_component_ratio"] < 0.98:
                failures.append(
                    f"{name}: expected one continuous significant part, got "
                    f"{record['significant_components']} / {record['largest_component_ratio']:.6f}"
                )

    overlaps: dict[str, int] = {}
    names = list(parts)
    for index, first in enumerate(names):
        for second in names[index + 1:]:
            count = int(np.count_nonzero(parts[first] & parts[second]))
            overlaps[f"{first}__{second}"] = count
            if count:
                failures.append(f"undeclared overlap {first}/{second}: {count}")
    metrics["new_part_overlaps"] = overlaps

    landmarks = {
        "HAIR_BACK": [(330, 80), (220, 300), (260, 340)],
        "HEAD_FACE": [(520, 280), (530, 315)],
        "HAIR_FRONT": [(465, 175), (445, 260)],
        "ARM_TRIGGER_UPPER": [(330, 310)],
        "ARM_SUPPORT_UPPER": [(680, 430)],
        "SHOULDER_PLATE": [(625, 290), (670, 335)],
    }
    landmark_metrics: dict[str, dict[str, bool]] = {}
    yy, xx = np.mgrid[0:subject.shape[0], 0:subject.shape[1]]
    for name, points in landmarks.items():
        checks: dict[str, bool] = {}
        for x, y in points:
            within = ((xx - x) ** 2 + (yy - y) ** 2) <= 14**2
            checks[f"{x},{y}"] = bool(np.any(parts[name] & within))
        landmark_metrics[name] = checks
        if not all(checks.values()):
            failures.append(f"{name}: misses locked semantic landmark {checks}")
    metrics["semantic_landmarks"] = landmark_metrics

    output_paths = {
        "HAIR_BACK": OUT / "ASTER_FIRE_SE_HAIR_BACK_MANUAL_V1_MASK.png",
        "HEAD_FACE": OUT / "ASTER_FIRE_SE_HEAD_FACE_MANUAL_V1_MASK.png",
        "HAIR_FRONT": OUT / "ASTER_FIRE_SE_HAIR_FRONT_MANUAL_V1_MASK.png",
        "ARM_TRIGGER_UPPER": OUT / "ASTER_FIRE_SE_ARM_TRIGGER_UPPER_MANUAL_V1_MASK.png",
        "ARM_SUPPORT_UPPER": OUT / "ASTER_FIRE_SE_ARM_SUPPORT_UPPER_MANUAL_V1_MASK.png",
        "SHOULDER_PLATE": OUT / "ASTER_FIRE_SE_SHOULDER_PLATE_MANUAL_V1_MASK.png",
    }
    for name, path in output_paths.items():
        save_mask(path, parts[name])

    result = "PASS_SIX_UPPER_IDENTITY_MASKS_STAGING_HOLD" if not failures else "FAIL"
    review_path = OUT / "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_REVIEW_1920X1440.png"
    build_review(source, parts, review_path, result)

    part_records = {
        name: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "metrics": metrics[name],
        }
        for name, path in output_paths.items()
    }
    common = {
        "schema": 1,
        "role": "ASTER Fire16 locked-SE upper/identity semantic-mask staging",
        "result": result,
        "candidate_status": "HOLD",
        "promotion_ready": False,
        "runtime_asset": False,
        "visual_pass": False,
        "contract_complete": False,
        "costume_id": "ASTER_COMBAT_SUIT_C01",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": EXPECTED_SHA256["source"],
        "subject_mask": SUBJECT_MASK.relative_to(ROOT).as_posix(),
        "subject_mask_sha256": EXPECTED_SHA256["subject"],
        "checked_contract_masks": CHECKED_MASKS,
        "missing_contract_masks": MISSING_CONTRACT_MASKS,
        "method": "hand-authored polygons plus local OpenCV GrabCut; no model inference",
        "semantic_ownership": {
            "trigger_forearm_proximal_seam": {
                "decision": "accepted TRIGGER_FOREARM_HAND remains immutable and wins collisions; ARM_TRIGGER_UPPER owns only the proximal navy shoulder cap above the existing diagonal seam",
                "approximate_seam_polyline_xy": [[323, 329], [344, 338], [365, 347], [390, 365]],
                "overlap_allowed_pixels": 0,
            },
            "receiver_under_flap_strap": {
                "decision": "non-weapon flap/strap below the receiver is excluded from both upper-arm masks and reserved for later BODY_CORE ownership",
                "reserved_roi_xyxy": [430, 438, 518, 524],
                "rifle_authority": "accepted RIFLE mask remains immutable; visible receiver and magazine pixels already assigned to it are not reclassified",
            },
            "identity": "mature ASTER face, silver split-comet hair, and canonical white anatomical-right shoulder plate remain separate locked parts",
        },
        "parts": part_records,
        "metrics": metrics,
        "failures": failures,
        "review": review_path.relative_to(ROOT).as_posix(),
        "review_sha256": sha256(review_path),
        "review_resolution": [1920, 1440],
        "native_panel": {"xy": [24, 92], "resolution": [1254, 1254], "scale": "1:1"},
        "network_used": False,
        "model_used": False,
        "server_used": False,
        "runtime_promotion": False,
        "prohibitions": [
            "no source mutation",
            "no runtime promotion",
            "no SSE composite build",
            "no visual PASS from technical checks",
        ],
    }
    qa_path = OUT / "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_QA.json"
    write_json(qa_path, common)
    manifest = {
        **common,
        "role": "ASTER Fire16 SE upper/identity manual authoring manifest",
        "qa": qa_path.relative_to(ROOT).as_posix(),
        "qa_sha256": sha256(qa_path),
    }
    manifest_path = OUT / "ASTER_FIRE_SE_UPPER_IDENTITY_MASKS_V1_MANIFEST.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"result": result, "failures": failures, "output": str(OUT)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
