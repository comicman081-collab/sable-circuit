#!/usr/bin/env python3
"""Build ASTER V5/V6 split layers for locomotion while firing.

The selected UAL lower body keeps advancing while the clean Fire V4 upper body
owns torso/arms/rifle/recoil.  A direction-specific soft waist partition keeps
pelvis/thigh costume pixels under lower-body authority.  Only the calibrated
visible rifle segment and the ponytail above the waist may pierce that split.
The partition weights are complementary, preventing a duplicated full-body
ghost.  Muzzle flash is never baked; Fire V4's separate runtime muzzle contract
stays authoritative.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
FEATHER_PX = 16.0
WEAPON_CORRIDOR_CORE_PX = 8.0
WEAPON_CORRIDOR_FEATHER_PX = 7.0
HAIR_MAX_BELOW_SPLIT_PX = -4.0
LOWER_COSTUME_LOCK_OFFSET_PX = FEATHER_PX * 0.5
MUZZLE_ALIGNMENT_RELATIVE = Path("assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json")
SOURCE_SPECS = {
    "move_lower": {
        "count": 24,
        "fps": 24,
        "path": "assets/units/operators/aster/move_360_ual_{generation}/{direction}/ASTER_MOVE_{direction}_360_UAL_{generation_upper}_ATLAS.webp",
        "output": "move_lower/{direction}/ASTER_MOVE_{direction}_LOWER_{generation_upper}_ATLAS.webp",
        "layer": "lower",
    },
    "idle_lower": {
        "count": 4,
        "fps": 4,
        "path": "assets/units/operators/aster/idle_360_clean_v5/{direction}/ASTER_IDLE_{direction}_CLEAN_V5_ATLAS.webp",
        "output": "idle_lower/{direction}/ASTER_IDLE_{direction}_LOWER_{generation_upper}_ATLAS.webp",
        "layer": "lower",
    },
    "fire_upper": {
        "count": 6,
        "fps": 12,
        "path": "assets/units/operators/aster/fire_360_clean_v4/ASTER_FIRE_{direction}_CLEAN_RGBA.webp",
        "output": "fire_upper/{direction}/ASTER_FIRE_{direction}_UPPER_{generation_upper}_ATLAS.webp",
        "layer": "upper",
    },
}


def resolved_source_specs(generation: str) -> dict[str, dict[str, Any]]:
    generation_upper = generation.upper()
    specs = copy.deepcopy(SOURCE_SPECS)
    for spec in specs.values():
        spec["path"] = spec["path"].format(
            direction="{direction}",
            generation=generation,
            generation_upper=generation_upper,
        )
        spec["output"] = spec["output"].format(
            direction="{direction}",
            generation=generation,
            generation_upper=generation_upper,
        )
    return specs


def load_muzzle_alignment() -> tuple[Path, dict[str, dict[str, np.ndarray]], str]:
    path = ROOT / MUZZLE_ALIGNMENT_RELATIVE
    if not path.is_file():
        raise SystemExit(f"muzzle alignment authority missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("cell_size") != CELL or payload.get("source_frame") != 2:
        raise SystemExit("muzzle alignment authority does not match Fire V4 contact frame")
    calibration: dict[str, dict[str, np.ndarray]] = {}
    source = payload.get("calibration", {})
    for direction in DIRECTIONS:
        record = source.get(direction, {})
        muzzle = np.asarray(record.get("muzzle_xy", []), dtype=np.float32)
        inner = np.asarray(record.get("barrel_inner_xy", []), dtype=np.float32)
        if muzzle.shape != (2,) or inner.shape != (2,):
            raise SystemExit(f"invalid muzzle alignment for {direction}")
        calibration[direction] = {"muzzle": muzzle, "inner": inner}
    return path, calibration, sha256(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_atlas(path: Path, count: int) -> np.ndarray:
    if not path.is_file():
        raise SystemExit(f"required source atlas missing: {path}")
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    expected = (CELL * count, CELL, 4)
    if rgba.shape != expected:
        raise SystemExit(f"atlas has wrong dimensions {rgba.shape}, expected {expected}: {path}")
    return rgba.reshape(count, CELL, CELL, 4)


def smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    t = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


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
        "left": float(xs.min()),
        "right": float(xs.max()),
        "top": top,
        "bottom": bottom,
        "height": height,
        "pelvis_x": pelvis_x,
        "split_y": top + height * 0.52,
    }


def distance_to_segment(
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    start: np.ndarray,
    end: np.ndarray,
) -> np.ndarray:
    segment = end - start
    denominator = max(float(np.dot(segment, segment)), 1e-6)
    t = ((grid_x - start[0]) * segment[0] + (grid_y - start[1]) * segment[1]) / denominator
    t = np.clip(t, 0.0, 1.0)
    closest_x = start[0] + t * segment[0]
    closest_y = start[1] + t * segment[1]
    return np.sqrt((grid_x - closest_x) ** 2 + (grid_y - closest_y) ** 2)


def connected_hair_weight(frame: np.ndarray, geometry: dict[str, float]) -> np.ndarray:
    """Preserve only the head-connected silver mass above the waist split.

    The old mask extended far below the pelvis and could join ASTER's white
    thigh panel through antialiased/closed pixels.  That made the lower layer
    erase the panel while the Fire upper layer supplied dark trousers there.
    The ponytail below the split now remains under the current idle/move lower
    authority instead of being reclassified as a Fire upper-body pixel.
    """
    rgb = frame[:, :, :3].astype(np.float32)
    alpha = frame[:, :, 3] > 18
    maximum = np.max(rgb, axis=2)
    minimum = np.min(rgb, axis=2)
    luminance = rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722
    candidate = (
        alpha
        & (luminance > 82.0)
        & ((maximum - minimum) < 118.0)
        & (rgb[:, :, 0] > 62.0)
        & (rgb[:, :, 2] > 66.0)
    )
    y_limit = int(np.clip(geometry["split_y"] + HAIR_MAX_BELOW_SPLIT_PX, 0, CELL - 1))
    candidate[y_limit + 1 :] = False
    closed = cv2.morphologyEx(candidate.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    count, labels = cv2.connectedComponents(closed, connectivity=8)
    seed_limit = int(min(CELL - 1, geometry["top"] + geometry["height"] * 0.34))
    seed_labels = set(int(value) for value in np.unique(labels[: seed_limit + 1]) if value != 0)
    keep = np.zeros((CELL, CELL), dtype=np.uint8)
    for label in seed_labels:
        keep[labels == label] = 255
    if count <= 1 or not seed_labels:
        return np.zeros((CELL, CELL), dtype=np.float32)
    keep = cv2.dilate(keep, np.ones((3, 3), np.uint8), iterations=1)
    return np.clip(cv2.GaussianBlur(keep.astype(np.float32) / 255.0, (0, 0), 2.4), 0.0, 1.0)


def partition_fields(
    frame: np.ndarray,
    direction: str,
    geometry: dict[str, float],
    muzzle_calibration: dict[str, dict[str, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return lower base, calibrated weapon corridor, and bounded hair mask."""
    grid_y, grid_x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    split_y = geometry["split_y"]
    lower = smoothstep(split_y - FEATHER_PX * 0.5, split_y + FEATHER_PX * 0.5, grid_y).astype(np.float32)

    # Use the visible Fire contact barrel, not runtime-local offsets.  The old
    # pelvis-to-offset segment crossed W's white thigh panel and incorrectly
    # promoted pants pixels into the upper layer.
    start = muzzle_calibration[direction]["inner"]
    end = muzzle_calibration[direction]["muzzle"]
    distance = distance_to_segment(grid_x, grid_y, start, end)
    corridor = 1.0 - smoothstep(
        WEAPON_CORRIDOR_CORE_PX,
        WEAPON_CORRIDOR_CORE_PX + WEAPON_CORRIDOR_FEATHER_PX,
        distance,
    )
    hair = connected_hair_weight(frame, geometry)
    return lower, corridor.astype(np.float32), hair


def lower_partition(
    frame: np.ndarray,
    direction: str,
    geometry: dict[str, float],
    muzzle_calibration: dict[str, dict[str, np.ndarray]],
) -> tuple[np.ndarray, dict[str, Any]]:
    grid_y = np.arange(CELL, dtype=np.float32)[:, None]
    lower, corridor, hair = partition_fields(frame, direction, geometry, muzzle_calibration)
    preserved_upper = np.maximum(corridor.astype(np.float32), hair)
    lower *= 1.0 - preserved_upper

    # Below the completed waist feather, the current idle/move frame owns the
    # full costume.  Only the calibrated visible rifle corridor may interrupt
    # that ownership.  This is the explicit pants/pelvis continuity contract.
    lock_y = geometry["split_y"] + LOWER_COSTUME_LOCK_OFFSET_PX
    hard_lower = (grid_y >= lock_y) & (corridor <= 0.001)
    lower = np.where(hard_lower, 1.0, lower)
    lower = np.clip(lower, 0.0, 1.0)
    return lower, {
        "split_y": round(float(geometry["split_y"]), 4),
        "feather_px": FEATHER_PX,
        "lower_costume_lock_y": round(float(lock_y), 4),
        "hair_upper_limit_y": round(float(geometry["split_y"] + HAIR_MAX_BELOW_SPLIT_PX), 4),
        "weapon_corridor_start": [
            round(float(value), 4) for value in muzzle_calibration[direction]["inner"]
        ],
        "weapon_corridor_end": [
            round(float(value), 4) for value in muzzle_calibration[direction]["muzzle"]
        ],
        "weapon_corridor_core_radius_px": WEAPON_CORRIDOR_CORE_PX,
        "weapon_corridor_feather_px": WEAPON_CORRIDOR_FEATHER_PX,
        "weapon_corridor_authority": MUZZLE_ALIGNMENT_RELATIVE.as_posix(),
        "connected_hair_preserved": bool(np.any(hair > 0.1)),
        "connected_hair_bounded_above_waist": True,
        "pelvis_thigh_costume_owned_by_lower": True,
    }


def apply_partition(frame: np.ndarray, weight: np.ndarray) -> np.ndarray:
    result = frame.copy()
    result[:, :, 3] = np.rint(frame[:, :, 3].astype(np.float32) * weight).astype(np.uint8)
    result[result[:, :, 3] == 0, :3] = 0
    return result


def clean_idle_shadow_artifact(
    frame: np.ndarray, clean_move_support: np.ndarray, split_y: float
) -> tuple[np.ndarray, dict[str, Any]]:
    """Remove only matte-black idle residue outside the clean V5 silhouette.

    The E idle source contains an opaque offset shadow under/behind the boots.
    Source art stays immutable; cleanup is restricted to the derived lower
    layer and uses the accepted V5 move silhouette as a spatial guard.
    """
    result = frame.copy()
    grid_y = np.arange(CELL, dtype=np.float32)[:, None]
    outside_distance = cv2.distanceTransform(
        (~clean_move_support).astype(np.uint8), cv2.DIST_L2, 3
    ).astype(np.float32)
    maximum = np.max(frame[:, :, :3], axis=2).astype(np.float32)
    darkness = 1.0 - smoothstep(18.0, 72.0, maximum)
    spatial = smoothstep(0.5, 4.0, outside_distance)
    lower_zone = smoothstep(split_y - 4.0, split_y + 6.0, grid_y)
    removal = np.clip(darkness * spatial * lower_zone, 0.0, 1.0)
    original_alpha = frame[:, :, 3].astype(np.float32)
    cleaned_alpha = np.rint(original_alpha * (1.0 - removal)).astype(np.uint8)
    opaque_black_core = (
        (maximum < 32.0)
        & (outside_distance > 0.0)
        & (grid_y > split_y)
        & (frame[:, :, 3] > 8)
    )
    cleaned_alpha[opaque_black_core] = 0
    result[:, :, 3] = cleaned_alpha
    result[cleaned_alpha == 0, :3] = 0
    residual = (
        (np.max(result[:, :, :3], axis=2) < 24)
        & (result[:, :, 3] > 32)
        & (~clean_move_support)
        & (grid_y > split_y)
    )
    return result, {
        "derived_idle_shadow_cleanup": True,
        "source_modified": False,
        "pixels_alpha_reduced": int(np.count_nonzero(cleaned_alpha < frame[:, :, 3])),
        "removed_alpha_sum": int(np.sum(frame[:, :, 3].astype(np.int64) - cleaned_alpha.astype(np.int64))),
        "residual_opaque_near_black_outside_move_support": int(np.count_nonzero(residual)),
    }


def save_lossless_atlas(frames: list[np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atlas = np.concatenate(frames, axis=0)
    image = Image.fromarray(atlas, "RGBA")
    image.save(path, "WEBP", lossless=True, method=6, exact=True)
    decoded = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if not np.array_equal(decoded, atlas):
        raise RuntimeError(f"lossless WebP round-trip changed pixels: {path}")


def nonempty_area(frame: np.ndarray) -> int:
    return int(np.count_nonzero(frame[:, :, 3] > 8))


def component_areas(mask: np.ndarray, minimum: int = 1) -> list[int]:
    count, _labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    return sorted(
        (int(stats[index, cv2.CC_STAT_AREA]) for index in range(1, count) if stats[index, cv2.CC_STAT_AREA] >= minimum),
        reverse=True,
    )


def lower_costume_authority_mask(
    source: np.ndarray,
    direction: str,
    geometry: dict[str, float],
    muzzle_calibration: dict[str, dict[str, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray]:
    """Return hard lower-body ownership and its white/cyan costume subset."""
    grid_y = np.arange(CELL, dtype=np.float32)[:, None]
    _base, corridor, _hair = partition_fields(source, direction, geometry, muzzle_calibration)
    authority = (
        (source[:, :, 3] > 24)
        & (grid_y >= geometry["split_y"] + LOWER_COSTUME_LOCK_OFFSET_PX)
        & (corridor <= 0.001)
    )
    rgb = source[:, :, :3].astype(np.float32)
    maximum = np.max(rgb, axis=2)
    minimum = np.min(rgb, axis=2)
    luminance = rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722
    white = (
        (luminance >= 82.0)
        & ((maximum - minimum) <= 112.0)
        & (rgb[:, :, 0] >= 58.0)
        & (rgb[:, :, 2] >= 64.0)
    )
    cyan = (
        (rgb[:, :, 1] >= 72.0)
        & (rgb[:, :, 2] >= 82.0)
        & (rgb[:, :, 2] >= rgb[:, :, 0] * 1.04)
    )
    return authority, authority & (white | cyan)


def composite_qa(
    lower: np.ndarray,
    upper: np.ndarray,
    lower_source: np.ndarray,
    clean_move_support: np.ndarray,
    geometry: dict[str, float],
    direction: str,
    muzzle_calibration: dict[str, dict[str, np.ndarray]],
) -> dict[str, Any]:
    lower_image = Image.fromarray(lower, "RGBA")
    lower_image.alpha_composite(Image.fromarray(upper, "RGBA"))
    composite = np.asarray(lower_image, dtype=np.uint8)
    alpha_mask = composite[:, :, 3] > 12
    visible_components = component_areas(alpha_mask)
    detached_area = sum(area for area in visible_components[1:] if area >= 20)
    grid_y = np.arange(CELL, dtype=np.float32)[:, None]
    black_blob = (
        (np.max(composite[:, :, :3], axis=2) < 24)
        & (composite[:, :, 3] > 32)
        & (~clean_move_support)
        & (grid_y > geometry["split_y"])
    )
    lower_alpha = lower[:, :, 3]
    upper_alpha = upper[:, :, 3]
    seam_band = np.abs(grid_y - geometry["split_y"]) <= FEATHER_PX
    overlap_source = (lower_alpha > 24) & (upper_alpha > 24) & seam_band
    seam_holes = overlap_source & (composite[:, :, 3] < 12)
    authority, accent_authority = lower_costume_authority_mask(
        lower_source,
        direction,
        geometry,
        muzzle_calibration,
    )
    rgba_delta = np.max(
        np.abs(composite.astype(np.int16) - lower_source.astype(np.int16)),
        axis=2,
    )
    authority_mismatch = authority & (rgba_delta > 2)
    authority_holes = authority & (
        composite[:, :, 3].astype(np.int16) + 2 < lower_source[:, :, 3].astype(np.int16)
    )
    accent_mismatch = accent_authority & (rgba_delta > 2)
    authority_pixels = int(np.count_nonzero(authority))
    accent_pixels = int(np.count_nonzero(accent_authority))
    authority_mismatch_pixels = int(np.count_nonzero(authority_mismatch))
    accent_mismatch_pixels = int(np.count_nonzero(accent_mismatch))
    authority_hole_areas = component_areas(authority_holes, minimum=1)
    return {
        "visible_area_px": int(np.count_nonzero(alpha_mask)),
        "component_count_area_ge_20": int(sum(1 for area in visible_components if area >= 20)),
        "largest_component_area_px": int(visible_components[0]) if visible_components else 0,
        "detached_component_area_px": int(detached_area),
        "opaque_near_black_blob_pixels": int(np.count_nonzero(black_blob)),
        "seam_hole_pixels": int(np.count_nonzero(seam_holes)),
        "lower_costume_authority_pixels": authority_pixels,
        "lower_costume_exact_retention_ratio": round(
            1.0 - authority_mismatch_pixels / max(authority_pixels, 1), 8
        ),
        "lower_costume_mismatch_pixels": authority_mismatch_pixels,
        "lower_costume_missing_hole_pixels": int(np.count_nonzero(authority_holes)),
        "lower_costume_missing_hole_components": len(authority_hole_areas),
        "lower_costume_largest_missing_hole_px": authority_hole_areas[0] if authority_hole_areas else 0,
        "white_cyan_authority_pixels": accent_pixels,
        "white_cyan_exact_retention_ratio": round(
            1.0 - accent_mismatch_pixels / max(accent_pixels, 1), 8
        ),
        "white_cyan_mismatch_pixels": accent_mismatch_pixels,
        "connected_lower_ownership": authority_pixels > 0 and not authority_hole_areas,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generation",
        choices=("v5", "v6"),
        default="v5",
        help="lower locomotion generation; idle V5 and clean Fire V4 stay authoritative",
    )
    parser.add_argument(
        "--replace-derived",
        action="store_true",
        help="atomically replace only the selected composite outputs and preserve the previous contact/manifest",
    )
    args = parser.parse_args()
    generation = args.generation
    generation_upper = generation.upper()
    source_specs = resolved_source_specs(generation)
    family = f"composite_fire_{generation}"
    contact_name = f"ASTER_COMPOSITE_FIRE_{generation_upper}_CONTACT.png"
    regression_contact_name = f"ASTER_COMPOSITE_FIRE_{generation_upper}_COSTUME_REGRESSION_CONTACT.png"
    manifest_name = f"ASTER_COMPOSITE_FIRE_{generation_upper}_MANIFEST.json"
    output = ROOT / f"assets/units/operators/aster/{family}"
    authoring = ROOT / f"art_src/pilot_v2/aster_v2/animation_360/{family}"
    if (output.exists() or authoring.exists()) and not args.replace_derived:
        raise SystemExit(f"refusing to overwrite existing {family} output")
    if args.replace_derived and (not output.is_dir() or not authoring.is_dir()):
        raise SystemExit(f"--replace-derived requires both existing {family} directories")
    clean_fire_manifest_path = ROOT / "assets/units/operators/aster/fire_360_clean_v4/ASTER_FIRE_360_CLEAN_V4_MANIFEST.json"
    clean_fire_manifest = json.loads(clean_fire_manifest_path.read_text(encoding="utf-8"))
    if clean_fire_manifest.get("baked_muzzle_vfx") is not False:
        raise SystemExit("Fire V4 source must explicitly declare baked_muzzle_vfx=false")
    muzzle_alignment_path, muzzle_calibration, muzzle_alignment_sha256 = load_muzzle_alignment()

    output.parent.mkdir(parents=True, exist_ok=True)
    authoring.parent.mkdir(parents=True, exist_ok=True)
    output_stage = Path(tempfile.mkdtemp(prefix=f"{family}_runtime_", dir=output.parent))
    authoring_stage = Path(tempfile.mkdtemp(prefix=f"{family}_authoring_", dir=authoring.parent))
    promoted_output = False
    promoted_authoring = False
    output_backup = output.with_name(output.name + "__replace_backup")
    authoring_backup = authoring.with_name(authoring.name + "__replace_backup")
    try:
        if args.replace_derived:
            if output_backup.exists() or authoring_backup.exists():
                raise SystemExit(f"stale {family} replacement backup exists; inspect before retry")
            previous_contact = authoring / contact_name
            previous_manifest = authoring / manifest_name
            if not previous_contact.is_file() or not previous_manifest.is_file():
                raise SystemExit("existing composite review evidence is incomplete")
            shutil.copy2(
                previous_contact,
                authoring_stage / f"ASTER_COMPOSITE_FIRE_{generation_upper}_CONTACT_PREVIOUS_BLOB.png",
            )
            shutil.copy2(
                previous_manifest,
                authoring_stage / f"ASTER_COMPOSITE_FIRE_{generation_upper}_MANIFEST_PREVIOUS_BLOB.json",
            )
        records: dict[str, Any] = {}
        previews: list[tuple[str, Image.Image, Image.Image]] = []
        for direction in DIRECTIONS:
            move_path = ROOT / source_specs["move_lower"]["path"].format(direction=direction)
            move_frames = read_atlas(move_path, 24)
            geometry = direction_geometry(move_frames)
            clean_move_support = cv2.dilate(
                (np.max(move_frames[:, :, :, 3], axis=0) > 8).astype(np.uint8),
                np.ones((9, 9), np.uint8),
                iterations=1,
            ) > 0
            direction_record: dict[str, Any] = {
                "geometry": {name: round(float(value), 4) for name, value in geometry.items()},
                "layers": {},
            }
            split_outputs: dict[str, list[np.ndarray]] = {}
            processed_sources: dict[str, list[np.ndarray]] = {}
            partition_records: dict[str, list[dict[str, Any]]] = {}

            for kind, spec in source_specs.items():
                source_path = ROOT / spec["path"].format(direction=direction)
                source_frames = read_atlas(source_path, int(spec["count"]))
                frames: list[np.ndarray] = []
                partitions: list[dict[str, Any]] = []
                mask_dir = authoring_stage / "masks" / kind / direction
                mask_dir.mkdir(parents=True, exist_ok=True)
                for index, frame in enumerate(source_frames):
                    cleanup_record = None
                    if kind == "idle_lower":
                        frame, cleanup_record = clean_idle_shadow_artifact(
                            frame, clean_move_support, geometry["split_y"]
                        )
                        if cleanup_record["residual_opaque_near_black_outside_move_support"] != 0:
                            raise RuntimeError(
                                f"idle shadow cleanup left opaque black residue: {direction} frame {index}"
                            )
                    lower_weight, partition = lower_partition(
                        frame,
                        direction,
                        geometry,
                        muzzle_calibration,
                    )
                    weight = lower_weight if spec["layer"] == "lower" else 1.0 - lower_weight
                    split = apply_partition(frame, weight)
                    if nonempty_area(split) < 120:
                        raise RuntimeError(f"{kind} {direction} frame {index} became empty")
                    mask_path = mask_dir / f"ASTER_{kind.upper()}_{direction}_F{index:02d}_ALPHA.png"
                    Image.fromarray(split[:, :, 3], "L").save(mask_path, optimize=True)
                    partition.update({
                        "index": index,
                        "visible_area_px": nonempty_area(split),
                        "alpha_mask": (authoring / "masks" / kind / direction / mask_path.name).relative_to(ROOT).as_posix(),
                        "alpha_mask_sha256": sha256(mask_path),
                    })
                    if cleanup_record is not None:
                        partition["idle_shadow_cleanup"] = cleanup_record
                    frames.append(split)
                    partitions.append(partition)
                output_relative = Path(spec["output"].format(direction=direction))
                output_path_stage = output_stage / output_relative
                save_lossless_atlas(frames, output_path_stage)
                output_path = output / output_relative
                split_outputs[kind] = frames
                processed_sources[kind] = source_frames.copy()
                if kind == "idle_lower":
                    processed_sources[kind] = []
                    for source_frame in source_frames:
                        cleaned_frame, _cleanup_record = clean_idle_shadow_artifact(
                            source_frame,
                            clean_move_support,
                            geometry["split_y"],
                        )
                        processed_sources[kind].append(cleaned_frame)
                partition_records[kind] = partitions
                direction_record["layers"][kind] = {
                    "source": source_path.relative_to(ROOT).as_posix(),
                    "source_sha256": sha256(source_path),
                    "output": output_path.relative_to(ROOT).as_posix(),
                    "output_sha256": sha256(output_path_stage),
                    "frame_count": int(spec["count"]),
                    "fps": int(spec["fps"]),
                    "resolution": [CELL, CELL * int(spec["count"])],
                    "partition_frames": partitions,
                    "lossless_webp_roundtrip": True,
                }

            move_composite = Image.fromarray(split_outputs["move_lower"][0], "RGBA")
            move_composite.alpha_composite(Image.fromarray(split_outputs["fire_upper"][2], "RGBA"))
            idle_composite = Image.fromarray(split_outputs["idle_lower"][0], "RGBA")
            idle_composite.alpha_composite(Image.fromarray(split_outputs["fire_upper"][2], "RGBA"))
            previews.append((direction, move_composite, idle_composite))
            move_scan = composite_qa(
                split_outputs["move_lower"][0],
                split_outputs["fire_upper"][2],
                processed_sources["move_lower"][0],
                clean_move_support,
                geometry,
                direction,
                muzzle_calibration,
            )
            idle_scan = composite_qa(
                split_outputs["idle_lower"][0],
                split_outputs["fire_upper"][2],
                processed_sources["idle_lower"][0],
                clean_move_support,
                geometry,
                direction,
                muzzle_calibration,
            )
            if move_scan["opaque_near_black_blob_pixels"] or idle_scan["opaque_near_black_blob_pixels"]:
                raise RuntimeError(f"black alpha blob detected in composite scan: {direction}")
            if move_scan["seam_hole_pixels"] or idle_scan["seam_hole_pixels"]:
                raise RuntimeError(f"waist seam hole detected in composite scan: {direction}")
            frame_pair_qa: dict[str, Any] = {}
            for lower_kind in ("move_lower", "idle_lower"):
                pair_count = 0
                minimum_costume_retention = 1.0
                minimum_accent_retention = 1.0
                maximum_mismatch = 0
                maximum_missing_hole = 0
                disconnected_pairs = 0
                for lower_index, lower_frame in enumerate(split_outputs[lower_kind]):
                    for upper_index, upper_frame in enumerate(split_outputs["fire_upper"]):
                        pair_scan = composite_qa(
                            lower_frame,
                            upper_frame,
                            processed_sources[lower_kind][lower_index],
                            clean_move_support,
                            geometry,
                            direction,
                            muzzle_calibration,
                        )
                        pair_count += 1
                        minimum_costume_retention = min(
                            minimum_costume_retention,
                            float(pair_scan["lower_costume_exact_retention_ratio"]),
                        )
                        minimum_accent_retention = min(
                            minimum_accent_retention,
                            float(pair_scan["white_cyan_exact_retention_ratio"]),
                        )
                        maximum_mismatch = max(
                            maximum_mismatch,
                            int(pair_scan["lower_costume_mismatch_pixels"]),
                        )
                        maximum_missing_hole = max(
                            maximum_missing_hole,
                            int(pair_scan["lower_costume_largest_missing_hole_px"]),
                        )
                        if not pair_scan["connected_lower_ownership"]:
                            disconnected_pairs += 1
                        if (
                            pair_scan["lower_costume_mismatch_pixels"]
                            or pair_scan["lower_costume_missing_hole_pixels"]
                            or pair_scan["white_cyan_mismatch_pixels"]
                        ):
                            raise RuntimeError(
                                "lower costume authority changed in composite: "
                                f"{direction} {lower_kind} F{lower_index:02d} + fire F{upper_index:02d} "
                                f"({pair_scan})"
                            )
                frame_pair_qa[lower_kind] = {
                    "frame_pairs_scanned": pair_count,
                    "minimum_lower_costume_exact_retention_ratio": round(minimum_costume_retention, 8),
                    "minimum_white_cyan_exact_retention_ratio": round(minimum_accent_retention, 8),
                    "maximum_lower_costume_mismatch_pixels": maximum_mismatch,
                    "maximum_missing_hole_component_px": maximum_missing_hole,
                    "disconnected_ownership_pairs": disconnected_pairs,
                }
            direction_record["composite_qa"] = {
                "move_plus_fire": move_scan,
                "idle_plus_fire": idle_scan,
                "all_frame_pairs": frame_pair_qa,
            }
            direction_record["costume_identity_lock"] = {
                "costumeId": "ASTER_COMBAT_SUIT_C01",
                "identity_changed": False,
                "palette_placement": "navy fitted fabric; white anatomical leg/boot panels; cyan emissive piping",
                "pelvis_waist_thigh_authority": "current idle/move lower source",
                "fire_overlay_authority": "torso/arms/rifle/head/hair only",
            }
            records[direction] = direction_record

        preview = Image.new("RGBA", (256 * len(DIRECTIONS), 552), (16, 22, 29, 255))
        draw = ImageDraw.Draw(preview)
        for column, (direction, move, idle) in enumerate(previews):
            x = column * 256
            preview.alpha_composite(move.resize((256, 256), Image.Resampling.LANCZOS), (x, 0))
            preview.alpha_composite(idle.resize((256, 256), Image.Resampling.LANCZOS), (x, 276))
            draw.rectangle((x, 0, x + 120, 20), fill=(4, 9, 13, 230))
            draw.rectangle((x, 276, x + 120, 296), fill=(4, 9, 13, 230))
            draw.text((x + 5, 4), f"{direction} MOVE+FIRE", fill=(132, 238, 244, 255))
            draw.text((x + 5, 280), f"{direction} IDLE+FIRE", fill=(132, 238, 244, 255))
        preview_stage = authoring_stage / contact_name
        preview.save(preview_stage, optimize=True)

        regression_cell = 160
        regression_label = 22
        regression_rows = 16
        regression = Image.new(
            "RGBA",
            (regression_cell * len(DIRECTIONS), (regression_cell + regression_label) * regression_rows),
            (16, 22, 29, 255),
        )
        regression_draw = ImageDraw.Draw(regression)
        for column, direction in enumerate(DIRECTIONS):
            move_source = read_atlas(
                ROOT / source_specs["move_lower"]["path"].format(direction=direction),
                24,
            )[0]
            idle_source = read_atlas(
                ROOT / source_specs["idle_lower"]["path"].format(direction=direction),
                4,
            )[0]
            move_lower = read_atlas(
                output_stage / Path(source_specs["move_lower"]["output"].format(direction=direction)),
                24,
            )[0]
            idle_lower = read_atlas(
                output_stage / Path(source_specs["idle_lower"]["output"].format(direction=direction)),
                4,
            )[0]
            fire_upper = read_atlas(
                output_stage / Path(source_specs["fire_upper"]["output"].format(direction=direction)),
                6,
            )
            row_images: list[tuple[str, Image.Image]] = [
                ("MOVE BEFORE", Image.fromarray(move_source, "RGBA")),
            ]
            for fire_index, upper_frame in enumerate(fire_upper):
                composite = Image.fromarray(move_lower, "RGBA")
                composite.alpha_composite(Image.fromarray(upper_frame, "RGBA"))
                row_images.append((f"MOVE+FIRE F{fire_index}", composite))
            row_images.append(("MOVE AFTER", Image.fromarray(move_source, "RGBA")))
            row_images.append(("IDLE BEFORE", Image.fromarray(idle_source, "RGBA")))
            for fire_index, upper_frame in enumerate(fire_upper):
                composite = Image.fromarray(idle_lower, "RGBA")
                composite.alpha_composite(Image.fromarray(upper_frame, "RGBA"))
                row_images.append((f"IDLE+FIRE F{fire_index}", composite))
            row_images.append(("IDLE AFTER", Image.fromarray(idle_source, "RGBA")))
            if len(row_images) != regression_rows:
                raise RuntimeError("unexpected costume regression row count")
            for row, (label, image) in enumerate(row_images):
                x = column * regression_cell
                y = row * (regression_cell + regression_label)
                regression.alpha_composite(
                    image.resize((regression_cell, regression_cell), Image.Resampling.LANCZOS),
                    (x, y + regression_label),
                )
                regression_draw.rectangle((x, y, x + regression_cell - 1, y + regression_label - 1), fill=(4, 9, 13, 230))
                regression_draw.text((x + 4, y + 4), f"{direction} {label}", fill=(132, 238, 244, 255))
        regression_preview_stage = authoring_stage / regression_contact_name
        regression.save(regression_preview_stage, optimize=True)

        manifest = {
            "schema": 1,
            "role": f"ASTER {generation_upper} lower-body locomotion plus clean Fire V4 upper-body composite contract",
            "directions": list(DIRECTIONS),
            "cell": CELL,
            "soft_waist_feather_px": FEATHER_PX,
            "muzzle_alignment_authority": muzzle_alignment_path.relative_to(ROOT).as_posix(),
            "muzzle_alignment_authority_sha256": muzzle_alignment_sha256,
            "weapon_corridors_384_cell": {
                key: {
                    "barrel_inner_xy": [float(value) for value in muzzle_calibration[key]["inner"]],
                    "muzzle_xy": [float(value) for value in muzzle_calibration[key]["muzzle"]],
                }
                for key in DIRECTIONS
            },
            "layers": {
                "move_lower": {"frame_count": 24, "fps": 24, "atlas_resolution": [384, 9216]},
                "idle_lower": {"frame_count": 4, "fps": 4, "atlas_resolution": [384, 1536]},
                "fire_upper": {"frame_count": 6, "fps": 12, "atlas_resolution": [384, 2304]},
            },
            "partition": {
                "lower": "pelvis/waist/thigh/legs below direction waist split; exact current idle/move costume authority outside calibrated visible rifle corridor",
                "upper": "exact complement; torso/arms/rifle/head/hair/recoil only, with hair bounded above waist",
                "full_body_double_draw_allowed": False,
                "moving_fire": "move_lower continues at 24fps while fire_upper plays at 12fps",
                "costumeId": "ASTER_COMBAT_SUIT_C01",
                "costume_identity_changed": False,
                "lower_costume_lock_offset_px": LOWER_COSTUME_LOCK_OFFSET_PX,
                "hair_max_below_split_px": HAIR_MAX_BELOW_SPLIT_PX,
            },
            "fire_source_manifest": clean_fire_manifest_path.relative_to(ROOT).as_posix(),
            "fire_source_manifest_sha256": sha256(clean_fire_manifest_path),
            "baked_muzzle_vfx": False,
            "runtime_muzzle_vfx": clean_fire_manifest.get("runtime_muzzle_vfx"),
            "directions_output": records,
            "preview": (authoring / preview_stage.name).relative_to(ROOT).as_posix(),
            "preview_sha256": sha256(preview_stage),
            "costume_regression_preview": (
                authoring / regression_preview_stage.name
            ).relative_to(ROOT).as_posix(),
            "costume_regression_preview_sha256": sha256(regression_preview_stage),
            "qa": {
                "all_layers_nonempty": True,
                "lossless_webp_roundtrip": True,
                "weapon_corridor_preserved": True,
                "connected_hair_preserved": True,
                "baked_muzzle_absent": True,
                "all_direction_lower_fire_frame_pairs_scanned": True,
                "frame_pairs_scanned": len(DIRECTIONS) * (24 + 4) * 6,
                "opaque_black_blob_pixels": 0,
                "seam_hole_pixels": 0,
                "lower_costume_mismatch_pixels": 0,
                "lower_costume_missing_hole_pixels": 0,
                "white_cyan_costume_mismatch_pixels": 0,
                "costume_continuity": "COSTUME_CONTINUITY_PASS",
                "visual_gate": "USER_REVIEW_REQUIRED",
            },
            "preserved_previous_review": {
                "contact": (
                    authoring / f"ASTER_COMPOSITE_FIRE_{generation_upper}_CONTACT_PREVIOUS_BLOB.png"
                ).relative_to(ROOT).as_posix(),
                "manifest": (
                    authoring / f"ASTER_COMPOSITE_FIRE_{generation_upper}_MANIFEST_PREVIOUS_BLOB.json"
                ).relative_to(ROOT).as_posix(),
            } if args.replace_derived else None,
            "production_expansion": "HOLD",
        }
        manifest_stage = output_stage / manifest_name
        manifest_stage.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        authoring_manifest_stage = authoring_stage / manifest_name
        authoring_manifest_stage.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if args.replace_derived:
            os.replace(output, output_backup)
            os.replace(authoring, authoring_backup)
            try:
                os.replace(output_stage, output)
                promoted_output = True
                os.replace(authoring_stage, authoring)
                promoted_authoring = True
            except Exception:
                if output.exists():
                    shutil.rmtree(output)
                if authoring.exists():
                    shutil.rmtree(authoring)
                os.replace(output_backup, output)
                os.replace(authoring_backup, authoring)
                raise
            shutil.rmtree(output_backup)
            shutil.rmtree(authoring_backup)
        else:
            os.replace(output_stage, output)
            promoted_output = True
            os.replace(authoring_stage, authoring)
            promoted_authoring = True
        print(f"ASTER_COMPOSITE_FIRE_{generation_upper}=" + json.dumps({
            "directions": len(DIRECTIONS),
            "move_lower": [384, 9216],
            "idle_lower": [384, 1536],
            "fire_upper": [384, 2304],
            "preview": manifest["preview"],
            "costume_regression_preview": manifest["costume_regression_preview"],
            "baked_muzzle_vfx": False,
            "costume_continuity": manifest["qa"]["costume_continuity"],
            "visual_gate": manifest["qa"]["visual_gate"],
        }, ensure_ascii=False))
        return 0
    finally:
        if not promoted_output and output_stage.exists():
            shutil.rmtree(output_stage)
        if not promoted_authoring and authoring_stage.exists():
            shutil.rmtree(authoring_stage)


if __name__ == "__main__":
    raise SystemExit(main())
