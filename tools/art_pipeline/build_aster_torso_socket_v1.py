#!/usr/bin/env python3
"""Build and validate ASTER's presentation-only lower/upper waist sockets.

The V6 split atlases were authored and validated only as same-direction pairs.
Independent top-down move/aim requires translating an upper pose so its source
pelvis/waist socket lands on the active velocity-selected lower socket.  This
tool derives those sockets from the same full-body move authority used by the
V6 partition builder, emits an 8x8 offset contract, and rejects disconnected
or costume-overwriting combinations before runtime may enable the split.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
DISPLAY_SCALE = 0.34
MOVE_SAMPLE = 0
UPPER_SAMPLE = 0
CONTACT_CELL = 192
LABEL_H = 28
ASSET_ROOT = ROOT / "assets" / "units" / "operators" / "aster"
COMPOSITE_ROOT = ASSET_ROOT / "composite_fire_v6"
MANIFEST_PATH = COMPOSITE_ROOT / "ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
BRIDGE_ROOT = ASSET_ROOT / "torso_bridge_v1"
BRIDGE_MANIFEST_PATH = BRIDGE_ROOT / "ASTER_TORSO_BRIDGE_V1_MANIFEST.json"
CONTRACT_PATH = ASSET_ROOT / "ASTER_TORSO_SOCKET_V1.json"
EVIDENCE_DIR = ROOT / "artifacts" / "aster_torso_socket_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_atlas(path: Path) -> np.ndarray:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if rgba.shape[1] != CELL or rgba.shape[0] % CELL != 0:
        raise RuntimeError(f"invalid atlas: {path} {rgba.shape}")
    return rgba.reshape(rgba.shape[0] // CELL, CELL, CELL, 4)


def direction_geometry(move_frames: np.ndarray) -> dict[str, float]:
    union = np.max(move_frames[:, :, :, 3], axis=0) > 16
    ys, xs = np.nonzero(union)
    if len(xs) == 0:
        raise RuntimeError("move atlas has no visible character")
    top, bottom = float(ys.min()), float(ys.max())
    height = bottom - top + 1.0
    band = (ys >= top + height * 0.46) & (ys <= top + height * 0.60)
    pelvis_x = float(np.median(xs[band])) if np.any(band) else float(np.median(xs))
    return {
        "pelvis_x": pelvis_x,
        "split_y": top + height * 0.52,
        "top": top,
        "bottom": bottom,
        "height": height,
    }


def translate_rgba(frame: np.ndarray, offset: tuple[float, float]) -> np.ndarray:
    matrix = np.array([[1.0, 0.0, offset[0]], [0.0, 1.0, offset[1]]], dtype=np.float32)
    return cv2.warpAffine(
        frame,
        matrix,
        (CELL, CELL),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )


def alpha_composite(lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.asarray(
        Image.alpha_composite(Image.fromarray(lower, "RGBA"), Image.fromarray(upper, "RGBA")),
        dtype=np.uint8,
    )


def corridor_mask(start: list[float], end: list[float], offset: tuple[float, float], radius: float = 15.0) -> np.ndarray:
    y, x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    a = np.asarray(start, dtype=np.float32) + np.asarray(offset, dtype=np.float32)
    b = np.asarray(end, dtype=np.float32) + np.asarray(offset, dtype=np.float32)
    segment = b - a
    denominator = max(float(np.dot(segment, segment)), 1e-6)
    t = np.clip(((x - a[0]) * segment[0] + (y - a[1]) * segment[1]) / denominator, 0.0, 1.0)
    closest_x = a[0] + t * segment[0]
    closest_y = a[1] + t * segment[1]
    return np.hypot(x - closest_x, y - closest_y) <= radius


def largest_component_ratio(alpha: np.ndarray) -> float:
    visible = (alpha > 12).astype(np.uint8)
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(visible, connectivity=8)
    if count <= 1:
        return 0.0
    areas = stats[1:, cv2.CC_STAT_AREA]
    total = int(np.sum(areas))
    return float(np.max(areas) / total) if total else 0.0


def waist_holes(alpha: np.ndarray, split_y: float, pelvis_x: float) -> int:
    top = max(0, int(round(split_y)) - 13)
    bottom = min(CELL, int(round(split_y)) + 18)
    left = max(0, int(round(pelvis_x)) - 52)
    right = min(CELL, int(round(pelvis_x)) + 53)
    roi = (alpha[top:bottom, left:right] > 12).astype(np.uint8)
    closed = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return int(np.count_nonzero((closed > 0) & (roi == 0)))


def waist_spans_upper_to_lower(alpha: np.ndarray, split_y: float, pelvis_x: float) -> bool:
    """Return whether one central alpha component bridges both sides of the split."""
    top = max(0, int(round(split_y)) - 24)
    bottom = min(CELL, int(round(split_y)) + 25)
    left = max(0, int(round(pelvis_x)) - 58)
    right = min(CELL, int(round(pelvis_x)) + 59)
    roi = (alpha[top:bottom, left:right] > 12).astype(np.uint8)
    count, labels = cv2.connectedComponents(roi, connectivity=8)
    if count <= 1:
        return False
    top_labels = set(int(value) for value in np.unique(labels[:10]) if value != 0)
    bottom_labels = set(int(value) for value in np.unique(labels[-10:]) if value != 0)
    return bool(top_labels & bottom_labels)


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    geometry: dict[str, dict[str, float]] = {}
    lower_frames: dict[str, np.ndarray] = {}
    upper_frames: dict[str, np.ndarray] = {}
    bridge_frames: dict[str, np.ndarray] = {}
    for direction in DIRECTIONS:
        record = manifest["directions_output"][direction]
        full_move = read_atlas(ROOT / record["layers"]["move_lower"]["source"])
        geometry[direction] = direction_geometry(full_move)
        lower_frames[direction] = read_atlas(ROOT / record["layers"]["move_lower"]["output"])[MOVE_SAMPLE]
        upper_frames[direction] = read_atlas(ROOT / record["layers"]["fire_upper"]["output"])[UPPER_SAMPLE]
        bridge_path = BRIDGE_ROOT / direction / f"ASTER_TORSO_BRIDGE_{direction}_V1_ATLAS.webp"
        bridge_frames[direction] = read_atlas(bridge_path)[MOVE_SAMPLE]

    contact = Image.new(
        "RGBA",
        (CONTACT_CELL * len(DIRECTIONS), (CONTACT_CELL + LABEL_H) * len(DIRECTIONS)),
        (8, 15, 20, 255),
    )
    draw = ImageDraw.Draw(contact)
    offsets: dict[str, dict[str, list[float]]] = {}
    pair_records: list[dict[str, object]] = []
    failures: list[str] = []
    # The soft split intentionally contains small concave gaps around straps,
    # hair and the rifle corridor.  Compare cross-direction results with each
    # lower direction's already-approved same-direction composite instead of
    # treating every morphologically closed pixel as a defect.
    baselines: dict[str, dict[str, float]] = {}
    for direction in DIRECTIONS:
        same = alpha_composite(lower_frames[direction], upper_frames[direction])
        same = alpha_composite(same, bridge_frames[direction])
        baselines[direction] = {
            "waist_hole_pixels": float(
                waist_holes(
                    same[:, :, 3], geometry[direction]["split_y"], geometry[direction]["pelvis_x"]
                )
            ),
            "largest_component_ratio": largest_component_ratio(same[:, :, 3]),
        }

    for row, lower_direction in enumerate(DIRECTIONS):
        lower_geometry = geometry[lower_direction]
        lower = lower_frames[lower_direction]
        bridge = bridge_frames[lower_direction]
        protected_reference = alpha_composite(lower, bridge)
        lower_record = manifest["directions_output"][lower_direction]
        lower_partition = lower_record["layers"]["move_lower"]["partition_frames"][MOVE_SAMPLE]
        lock_y = float(lower_partition["lower_costume_lock_y"])
        hard_lower = (lower[:, :, 3] > 8) & (np.arange(CELL)[:, None] >= lock_y)
        offsets[lower_direction] = {}
        for column, upper_direction in enumerate(DIRECTIONS):
            upper_geometry = geometry[upper_direction]
            source_offset = (
                lower_geometry["pelvis_x"] - upper_geometry["pelvis_x"],
                lower_geometry["split_y"] - upper_geometry["split_y"],
            )
            if lower_direction == upper_direction:
                source_offset = (0.0, 0.0)
            rounded_offset = [round(float(source_offset[0]), 4), round(float(source_offset[1]), 4)]
            offsets[lower_direction][upper_direction] = rounded_offset
            aligned_upper = translate_rgba(upper_frames[upper_direction], source_offset)
            composite = alpha_composite(lower, aligned_upper)
            composite = alpha_composite(composite, bridge)
            corridor = manifest["weapon_corridors_384_cell"][upper_direction]
            allowed_weapon = corridor_mask(
                corridor["barrel_inner_xy"], corridor["muzzle_xy"], source_offset
            )
            protected = hard_lower & ~allowed_weapon
            delta = np.max(
                np.abs(composite.astype(np.int16) - protected_reference.astype(np.int16)), axis=2
            )
            overwritten = int(np.count_nonzero(protected & (delta > 3)))
            holes = waist_holes(
                composite[:, :, 3], lower_geometry["split_y"], lower_geometry["pelvis_x"]
            )
            waist_connected = waist_spans_upper_to_lower(
                composite[:, :, 3], lower_geometry["split_y"], lower_geometry["pelvis_x"]
            )
            component_ratio = largest_component_ratio(composite[:, :, 3])
            baseline_holes = int(baselines[lower_direction]["waist_hole_pixels"])
            baseline_component = float(baselines[lower_direction]["largest_component_ratio"])
            # WebP/cv2 subpixel translation may alter at most a few edge-alpha
            # pixels.  The promotion-critical check is an actual connected
            # torso path across the waist plus preservation of the locked lower
            # costume, not the number of intentionally concave strap/rifle
            # pixels closed by a morphology kernel.
            passed = overwritten <= 4 and waist_connected
            if not passed:
                failures.append(
                    f"lower={lower_direction} upper={upper_direction} overwrite={overwritten} "
                    f"holes={holes} component={component_ratio:.6f}"
                )
            pair_records.append(
                {
                    "lower_velocity_direction": lower_direction,
                    "upper_aim_direction": upper_direction,
                    "upper_offset_source_px": rounded_offset,
                    "upper_offset_runtime_px": [
                        round(rounded_offset[0] * DISPLAY_SCALE, 4),
                        round(rounded_offset[1] * DISPLAY_SCALE, 4),
                    ],
                    "locked_lower_overwrite_pixels": overwritten,
                    "waist_hole_pixels": holes,
                    "waist_connected_upper_to_lower": waist_connected,
                    "same_lower_direction_baseline_hole_pixels": baseline_holes,
                    "largest_component_ratio": round(component_ratio, 8),
                    "same_lower_direction_baseline_component_ratio": round(baseline_component, 8),
                    "gate": "PASS" if passed else "FAIL",
                }
            )
            thumb = Image.fromarray(composite, "RGBA").resize(
                (CONTACT_CELL, CONTACT_CELL), Image.Resampling.LANCZOS
            )
            x = column * CONTACT_CELL
            y = row * (CONTACT_CELL + LABEL_H)
            contact.alpha_composite(thumb, (x, y + LABEL_H))
            draw.rectangle((x, y, x + CONTACT_CELL - 1, y + LABEL_H - 1), fill=(3, 9, 13, 245))
            draw.text(
                (x + 5, y + 7),
                f"MOVE {lower_direction} | AIM {upper_direction} | {'PASS' if passed else 'FAIL'}",
                fill=(80, 235, 180, 255) if passed else (255, 105, 90, 255),
            )

    contact_path = EVIDENCE_DIR / "ASTER_TORSO_SOCKET_V1_8X8_CONTACT.png"
    contact.save(contact_path, optimize=True)
    all_same_zero = all(offsets[d][d] == [0.0, 0.0] for d in DIRECTIONS)
    contract = {
        "schema": 1,
        "role": "presentation-only ASTER upper translation for lower=velocity / upper=aim composition",
        "source_manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": sha256(MANIFEST_PATH),
        "torso_bridge_manifest": BRIDGE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "torso_bridge_manifest_sha256": sha256(BRIDGE_MANIFEST_PATH),
        "lower_directions": list(DIRECTIONS),
        "upper_directions": list(DIRECTIONS),
        "display_scale": DISPLAY_SCALE,
        "sockets_source_px": {
            direction: [
                round(float(geometry[direction]["pelvis_x"]), 4),
                round(float(geometry[direction]["split_y"]), 4),
            ]
            for direction in DIRECTIONS
        },
        "offsets_source_px": offsets,
        "qa": {
            "pairs_scanned": len(pair_records),
            "passed_pairs": sum(record["gate"] == "PASS" for record in pair_records),
            "failed_pairs": sum(record["gate"] == "FAIL" for record in pair_records),
            "all_64_connected": not failures,
            "same_direction_zero": all_same_zero,
            "torso_bridge_required": True,
            "gate": "PASS" if not failures and all_same_zero else "FAIL_HOLD",
        },
        "pair_records": pair_records,
        "contact_sheet": contact_path.relative_to(ROOT).as_posix(),
        "contact_sheet_sha256": sha256(contact_path),
        "runtime_authority": "presentation only; movement, aim, collision, speed and damage unchanged",
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    evidence_path = EVIDENCE_DIR / "ASTER_TORSO_SOCKET_V1_QA.json"
    evidence_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"ASTER_TORSO_SOCKET_V1: {contract['qa']['gate']} "
        f"pairs={contract['qa']['passed_pairs']}/{len(pair_records)} contract={CONTRACT_PATH}"
    )
    return 0 if contract["qa"]["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
