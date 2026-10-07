#!/usr/bin/env python3
"""Author a project-local, model-free semantic-mask fallback for ASTER SE fire.

This is a staging-only mask authoring helper.  It uses hand-authored OpenCV
GrabCut foreground/background seeds against the immutable, approved 1254px SE
aim master.  It never edits the source, starts a server, generates character
pixels, builds an SSE composite, or promotes anything to runtime.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

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
LEGACY_STAGING = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_manual_fallback_v1_staging"
)
OUT = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_semantic_masks_v1/manual_fallback_v1"
)
EXPECTED_SOURCE_SHA256 = "1a674d5d1f68cebc20a61fae1187f725500189700897785550b5642d8a174838"
EXPECTED_MASK_SHA256 = "4dedc673b1d8029b7455e1259994e354285838ff7d7618d77828cef89ac8e9b5"
EXPECTED_SIZE = (1254, 1254)
EXACT_GREEN_BGR = np.asarray((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cv_read(path: Path, flags: int) -> np.ndarray | None:
    """Decode a Windows Unicode path without relying on cv2.imread."""
    return cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), flags)


def polygon_mask(shape: tuple[int, int], polygons: tuple[tuple[tuple[int, int], ...], ...]) -> np.ndarray:
    result = np.zeros(shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(result, [np.asarray(polygon, dtype=np.int32)], 1)
    return result.astype(bool)


def draw_seed_lines(mask: np.ndarray, lines: tuple[tuple[tuple[int, int], ...], ...], value: int, width: int) -> None:
    for line in lines:
        cv2.polylines(mask, [np.asarray(line, dtype=np.int32)], False, value, width, cv2.LINE_8)


def grabcut_part(
    source_bgr: np.ndarray,
    subject: np.ndarray,
    possible_polygons: tuple[tuple[tuple[int, int], ...], ...],
    foreground_polygons: tuple[tuple[tuple[int, int], ...], ...],
    foreground_lines: tuple[tuple[tuple[int, int], ...], ...],
    background_polygons: tuple[tuple[tuple[int, int], ...], ...],
    background_lines: tuple[tuple[tuple[int, int], ...], ...],
) -> tuple[np.ndarray, np.ndarray]:
    possible = polygon_mask(subject.shape, possible_polygons) & subject
    labels = np.full(subject.shape, cv2.GC_BGD, dtype=np.uint8)
    labels[possible] = cv2.GC_PR_BGD
    likely_fg = polygon_mask(subject.shape, foreground_polygons) & possible
    labels[likely_fg] = cv2.GC_PR_FGD
    draw_seed_lines(labels, foreground_lines, cv2.GC_FGD, 5)
    hard_bg = polygon_mask(subject.shape, background_polygons)
    labels[hard_bg] = cv2.GC_BGD
    draw_seed_lines(labels, background_lines, cv2.GC_BGD, 9)
    labels[~subject] = cv2.GC_BGD

    # Ensure every hard foreground stroke remains inside the approved subject.
    labels[(labels == cv2.GC_FGD) & ~subject] = cv2.GC_BGD
    seed_labels = labels.copy()
    bg_model = np.zeros((1, 65), dtype=np.float64)
    fg_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(source_bgr, labels, None, bg_model, fg_model, 7, cv2.GC_INIT_WITH_MASK)
    output = ((labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD)) & possible & subject
    exact_green = np.all(source_bgr == EXACT_GREEN_BGR, axis=2)
    output[exact_green] = False
    return output, seed_labels


RIFLE_POSSIBLE = (
    (
        (352, 257), (425, 257), (507, 326), (545, 307), (619, 329),
        (658, 366), (812, 442), (884, 504), (925, 520), (1001, 557),
        (1020, 614), (972, 659), (855, 588), (818, 548), (735, 517),
        (636, 475), (594, 487), (548, 478), (506, 466), (469, 454),
        (427, 423), (390, 381), (363, 337),
    ),
    # Receiver, trigger housing, magazine and lower rail enclosure.
    (
        (427, 337), (578, 330), (687, 389), (699, 472), (638, 502),
        (578, 489), (549, 526), (513, 521), (503, 472), (445, 452),
        (412, 398),
    ),
)

RIFLE_FOREGROUND = (
    ((363, 278), (402, 274), (470, 338), (445, 370), (394, 329)),
    ((510, 326), (607, 333), (681, 386), (653, 441), (548, 416), (456, 391)),
    ((608, 394), (792, 455), (870, 510), (844, 552), (720, 503), (633, 469)),
    ((862, 514), (914, 526), (1005, 571), (1009, 613), (969, 647), (858, 579)),
    ((508, 431), (556, 442), (555, 515), (514, 512)),
    ((548, 305), (615, 312), (649, 363), (605, 391), (547, 364)),
)

RIFLE_FG_LINES = (
    ((371, 287), (408, 302), (455, 352)),
    ((456, 374), (533, 367), (616, 394), (699, 434), (792, 473), (867, 528)),
    ((864, 539), (925, 561), (993, 596)),
    ((527, 453), (535, 496)),
    ((568, 327), (606, 346)),
)

RIFLE_BACKGROUND = (
    # Face and hair regions above/around the receiver; avoid the actual rifle corridor.
    ((143, 25), (498, 25), (502, 132), (405, 252), (341, 286), (149, 394), (120, 220)),
    ((439, 137), (575, 166), (577, 291), (533, 322), (495, 299), (413, 286)),
    # Canonical right shoulder plate, excluding the optic/rail foreground strip.
    ((596, 261), (677, 267), (705, 348), (683, 383), (659, 357), (632, 322)),
    # Trigger skin and sleeve mass.
    ((279, 335), (355, 320), (454, 369), (473, 390), (459, 449), (359, 465), (294, 435)),
    ((463, 384), (523, 387), (558, 420), (549, 460), (503, 473), (466, 449)),
    # Support skin and sleeve mass.
    ((611, 419), (659, 422), (674, 450), (714, 454), (744, 481), (736, 528), (695, 541), (647, 507)),
    # Torso below the rifle.
    ((388, 448), (493, 458), (517, 526), (611, 494), (646, 525), (604, 646), (401, 616)),
)

RIFLE_BG_LINES = (
    ((479, 254), (513, 279), (527, 306)),
    ((602, 282), (654, 300), (684, 344)),
    ((305, 368), (376, 413), (445, 426)),
    ((480, 408), (510, 428), (535, 447)),
    ((638, 448), (678, 487), (714, 512)),
    ((430, 469), (483, 500), (498, 550)),
)


TRIGGER_POSSIBLE = (
    (
        (276, 328), (338, 304), (402, 334), (455, 369), (500, 380),
        (546, 397), (563, 430), (549, 463), (514, 478), (468, 461),
        (434, 464), (369, 463), (313, 443), (281, 414),
    ),
)
TRIGGER_FOREGROUND = (
    ((284, 350), (321, 329), (394, 356), (461, 398), (449, 445), (365, 450), (303, 428)),
    ((466, 389), (516, 388), (552, 411), (552, 446), (518, 466), (475, 447)),
)
TRIGGER_FG_LINES = (
    ((297, 369), (337, 397), (389, 418), (445, 421)),
    ((478, 405), (505, 419), (538, 434)),
)
TRIGGER_BACKGROUND = (
    ((347, 289), (434, 317), (483, 353), (459, 382), (405, 358)),
    ((422, 354), (516, 347), (576, 381), (557, 411), (493, 390)),
    ((512, 437), (569, 427), (585, 471), (552, 495), (511, 475)),
    ((294, 432), (408, 454), (478, 454), (493, 499), (357, 500)),
)
TRIGGER_BG_LINES = (
    ((365, 325), (424, 359), (468, 381)),
    ((449, 374), (506, 368), (550, 394)),
    ((524, 451), (554, 467)),
    ((328, 449), (405, 470)),
)


SUPPORT_POSSIBLE = (
    (
        (602, 414), (650, 406), (678, 438), (716, 446), (742, 463),
        (750, 500), (736, 532), (705, 543), (671, 529), (643, 510),
        (620, 486),
    ),
)
SUPPORT_FOREGROUND = (
    ((608, 430), (643, 416), (668, 450), (658, 489), (638, 500), (618, 478)),
    ((669, 453), (713, 455), (739, 474), (738, 511), (716, 531), (680, 519), (663, 490)),
)
SUPPORT_FG_LINES = (
    ((619, 442), (640, 464), (651, 489)),
    ((680, 467), (704, 482), (726, 505)),
)
SUPPORT_BACKGROUND = (
    ((584, 395), (641, 398), (672, 425), (658, 447), (615, 427)),
    ((635, 424), (716, 432), (755, 460), (739, 480), (685, 454)),
    ((620, 482), (667, 506), (704, 536), (673, 561), (624, 527)),
    ((704, 512), (752, 502), (763, 539), (725, 558), (690, 536)),
)
SUPPORT_BG_LINES = (
    ((615, 414), (649, 427)),
    ((660, 439), (709, 450), (741, 469)),
    ((631, 504), (668, 529)),
    ((718, 522), (743, 537)),
)

# Conservative landmark guards deliberately cover only visible identity pixels
# that the rifle does not occlude.  Zero intersection proves that the manual
# masks did not bleed into ASTER's face, hair mass, or canonical shoulder plate.
PROTECTED_IDENTITY_REGIONS = {
    "face": (
        ((465, 235), (550, 231), (570, 264), (558, 297), (529, 306), (508, 283), (477, 292), (454, 270)),
    ),
    "hair": (
        ((145, 29), (486, 25), (505, 125), (434, 204), (345, 260), (199, 318), (135, 291)),
        ((409, 130), (548, 134), (576, 196), (557, 247), (500, 258), (429, 232)),
    ),
    "canonical_right_shoulder_plate": (
        ((600, 265), (662, 265), (690, 304), (682, 333), (646, 321), (612, 305)),
    ),
}


def clean_component(mask: np.ndarray, close_radius: int = 1) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * close_radius + 1, 2 * close_radius + 1))
    closed = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(closed, 8)
    if count <= 1:
        return mask
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep_labels = np.where(areas >= 40)[0] + 1
    return np.isin(labels, keep_labels) & mask


def save_mask(path: Path, mask: np.ndarray) -> None:
    Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), mode="L").save(path)


def tint(image: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float = 0.58) -> None:
    image[mask] = np.clip(
        image[mask].astype(np.float32) * (1.0 - alpha) + np.asarray(color, dtype=np.float32) * alpha,
        0,
        255,
    ).astype(np.uint8)


def build_review(
    source_rgb: np.ndarray,
    subject: np.ndarray,
    parts: dict[str, np.ndarray],
    seeds: dict[str, np.ndarray],
    output: Path,
    metrics: dict[str, object],
) -> None:
    overlay = source_rgb.copy()
    tint(overlay, parts["rifle"], (255, 44, 44))
    tint(overlay, parts["trigger_forearm_hand"], (0, 220, 255))
    tint(overlay, parts["support_forearm_hand"], (255, 220, 0))
    contours, _ = cv2.findContours(subject.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (255, 255, 255), 2)

    seed_panel = source_rgb.copy()
    seed_colors = {
        cv2.GC_FGD: (255, 255, 255),
        cv2.GC_PR_FGD: (255, 0, 255),
        cv2.GC_BGD: (0, 0, 0),
        cv2.GC_PR_BGD: (0, 120, 255),
    }
    combined = seeds["rifle"]
    for label, color in seed_colors.items():
        selected = combined == label
        if label == cv2.GC_BGD:
            selected &= polygon_mask(subject.shape, RIFLE_POSSIBLE)
        tint(seed_panel, selected, color, 0.45)

    canvas = Image.new("RGB", (1920, 1440), (18, 21, 27))
    canvas.paste(Image.fromarray(overlay), (20, 110))
    # A 560px crop panel retains original pixels (1:1) for the weapon/hands.
    crop = source_rgb[245:665, 265:1045].copy()
    crop_masks = {name: mask[245:665, 265:1045] for name, mask in parts.items()}
    tint(crop, crop_masks["rifle"], (255, 44, 44))
    tint(crop, crop_masks["trigger_forearm_hand"], (0, 220, 255))
    tint(crop, crop_masks["support_forearm_hand"], (255, 220, 0))
    canvas.paste(Image.fromarray(crop), (1125, 110))
    canvas.paste(Image.fromarray(seed_panel[245:665, 265:1045]), (1125, 560))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((20, 22), "ASTER SE MANUAL FALLBACK V1 — AUTHORING / HOLD", fill=(255, 255, 255), font=font)
    draw.text((20, 48), "Native source and crop panels are shown 1:1; no model or generation.", fill=(210, 215, 225), font=font)
    draw.text((1125, 86), "1:1 weapon/hand overlay crop", fill=(255, 255, 255), font=font)
    draw.text((1125, 536), "1:1 rifle GrabCut seed diagnostic", fill=(255, 255, 255), font=font)
    draw.text((1125, 1006), "RED rifle | CYAN trigger | YELLOW support", fill=(255, 255, 255), font=font)
    y = 1036
    for name, record in metrics.items():
        draw.text((1125, y), f"{name}: {record}", fill=(205, 210, 220), font=font)
        y += 22
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def component_metrics(mask: np.ndarray) -> dict[str, object]:
    count, _labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    areas = sorted((int(area) for area in stats[1:, cv2.CC_STAT_AREA]), reverse=True)
    return {
        "pixels": int(np.count_nonzero(mask)),
        "components": max(0, count - 1),
        "significant_components": len([area for area in areas if area >= 200]),
        "largest_component_ratio": (float(areas[0]) / float(max(1, np.count_nonzero(mask)))) if areas else 0.0,
    }


def main() -> int:
    if not SOURCE.is_file() or not SUBJECT_MASK.is_file():
        raise SystemExit("approved SE source or subject mask unavailable")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256 or sha256(SUBJECT_MASK) != EXPECTED_MASK_SHA256:
        raise SystemExit("approved SE source authority SHA mismatch")
    # Cleanup is restricted to the retired legacy staging directory.  The
    # accepted v1 authoring package is immutable: a later attempt must use a
    # new versioned output instead of deleting or overwriting current evidence.
    staging_allowlist = {
        "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png",
        "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
        "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
        "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_REVIEW_1920X1440.png",
        "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_MANIFEST.json",
        "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_TECHNICAL_QA.json",
        "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_VALIDATOR_REVIEW_1920X1440.png",
        "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_EVIDENCE_1080P_QA.json",
        "ASTER_FIRE_SE_THREE_PART_SOURCE_MASK_QA_V1.json",
        "ASTER_FIRE_SE_THREE_PART_SOURCE_MASK_REVIEW_V1_1920X1440.png",
        "ASTER_FIRE_SE_THREE_PART_SOURCE_MASK_EVIDENCE_1080P_QA_V1.json",
    }
    if LEGACY_STAGING.exists():
        unexpected = [
            path for path in LEGACY_STAGING.iterdir() if path.name not in staging_allowlist or not path.is_file()
        ]
        if unexpected:
            raise SystemExit(f"refusing unexpected legacy staging content: {unexpected}")
        for path in LEGACY_STAGING.iterdir():
            path.unlink()
        LEGACY_STAGING.rmdir()
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(
            f"immutable manual_fallback_v1 already exists; author a new version instead of overwriting {OUT}"
        )

    source_bgr = cv_read(SOURCE, cv2.IMREAD_COLOR)
    subject_raw = cv_read(SUBJECT_MASK, cv2.IMREAD_GRAYSCALE)
    if source_bgr is None or subject_raw is None or source_bgr.shape[:2][::-1] != EXPECTED_SIZE:
        raise SystemExit("approved SE inputs must decode at 1254x1254")
    subject = subject_raw == 255

    rifle, rifle_seeds = grabcut_part(
        source_bgr,
        subject,
        RIFLE_POSSIBLE,
        RIFLE_FOREGROUND,
        RIFLE_FG_LINES,
        RIFLE_BACKGROUND,
        RIFLE_BG_LINES,
    )
    trigger, trigger_seeds = grabcut_part(
        source_bgr,
        subject,
        TRIGGER_POSSIBLE,
        TRIGGER_FOREGROUND,
        TRIGGER_FG_LINES,
        TRIGGER_BACKGROUND,
        TRIGGER_BG_LINES,
    )
    support, support_seeds = grabcut_part(
        source_bgr,
        subject,
        SUPPORT_POSSIBLE,
        SUPPORT_FOREGROUND,
        SUPPORT_FG_LINES,
        SUPPORT_BACKGROUND,
        SUPPORT_BG_LINES,
    )
    rifle = clean_component(rifle)
    trigger = clean_component(trigger)
    support = clean_component(support)

    # GrabCut correctly separates the skin/sleeve appearance, but the rifle
    # visually occludes the trigger wrist.  Preserve one narrow, hand-authored
    # cuff bridge so the semantic forearm/hand topology remains contiguous.
    trigger_bridge = polygon_mask(
        subject.shape,
        (
            ((438, 389), (473, 381), (493, 398), (493, 426), (477, 452), (446, 449), (432, 421)),
        ),
    )
    trigger |= trigger_bridge & subject

    # Reinforce only the locked visible barrel/cage centerline.  Subject-mask
    # clipping preserves the cage holes and exact-green background.
    rifle_corridor = np.zeros(subject.shape, dtype=np.uint8)
    cv2.line(rifle_corridor, (858, 514), (1019, 611), 1, 9, cv2.LINE_8)
    rifle |= (rifle_corridor > 0) & subject

    # Semantic parts must be disjoint.  Hands/forearms have visual ownership
    # over skin/sleeve pixels; rifle retains only pixels not assigned to them.
    rifle &= ~(trigger | support)
    support &= ~trigger
    parts = {
        "rifle": rifle,
        "trigger_forearm_hand": trigger,
        "support_forearm_hand": support,
    }

    exact_green = np.all(source_bgr == EXACT_GREEN_BGR, axis=2)
    metrics: dict[str, object] = {}
    failures: list[str] = []
    for name, mask in parts.items():
        record = component_metrics(mask)
        record["outside_subject_pixels"] = int(np.count_nonzero(mask & ~subject))
        record["exact_green_pixels"] = int(np.count_nonzero(mask & exact_green))
        metrics[name] = record
        if not record["pixels"]:
            failures.append(f"{name} is empty")
        if record["outside_subject_pixels"] or record["exact_green_pixels"]:
            failures.append(f"{name} violates subject/exact-green containment")

    protected_metrics: dict[str, dict[str, int]] = {}
    for region_name, polygons in PROTECTED_IDENTITY_REGIONS.items():
        region = polygon_mask(subject.shape, polygons)
        intersections = {name: int(np.count_nonzero(mask & region)) for name, mask in parts.items()}
        protected_metrics[region_name] = intersections
        for part_name, pixels in intersections.items():
            if pixels:
                failures.append(f"{part_name} intrudes into protected {region_name}: {pixels} pixels")
    metrics["protected_identity_regions"] = protected_metrics

    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "rifle": OUT / "ASTER_FIRE_SE_RIFLE_MANUAL_FALLBACK_V1_MASK.png",
        "trigger_forearm_hand": OUT / "ASTER_FIRE_SE_TRIGGER_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
        "support_forearm_hand": OUT / "ASTER_FIRE_SE_SUPPORT_FOREARM_HAND_MANUAL_FALLBACK_V1_MASK.png",
    }
    for name, path in paths.items():
        save_mask(path, parts[name])

    source_rgb = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)
    review = OUT / "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_REVIEW_1920X1440.png"
    build_review(
        source_rgb,
        subject,
        parts,
        {"rifle": rifle_seeds, "trigger": trigger_seeds, "support": support_seeds},
        review,
        metrics,
    )
    manifest = {
        "schema": 1,
        "role": "ASTER Fire16 SE model-free manual GrabCut semantic-mask fallback staging",
        "status": "HOLD_VISUAL_REVIEW_REQUIRED",
        "promotion_ready": False,
        "runtime_asset": False,
        "costume_id": "ASTER_COMBAT_SUIT_C01",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(SOURCE),
        "subject_mask": SUBJECT_MASK.relative_to(ROOT).as_posix(),
        "subject_mask_sha256": sha256(SUBJECT_MASK),
        "method": "OpenCV GrabCut with hand-authored foreground/background seed polygons and strokes",
        "model_used": False,
        "network_used": False,
        "server_used": False,
        "parts": {
            name: {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "metrics": metrics[name],
            }
            for name, path in paths.items()
        },
        "review": review.relative_to(ROOT).as_posix(),
        "review_sha256": sha256(review),
        "identity_protection": protected_metrics,
        "failures": failures,
        "prohibitions": [
            "no source mutation",
            "no runtime promotion",
            "no SSE composite build",
            "no model inference",
        ],
    }
    manifest_path = OUT / "ASTER_FIRE_SE_MANUAL_FALLBACK_V1_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "review": str(review), "failures": failures}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
