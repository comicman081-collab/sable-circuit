#!/usr/bin/env python3
"""Reject ASTER locomotion atlases whose legs only *technically* advance.

This is a visual-motion regression gate, not an atlas-cursor test.  For each
of the eight authored directions it:

1. decodes all 24 atlas cells;
2. registers every frame to frame zero using only the upper-body alpha
   silhouette (removing rigid whole-character bob);
3. finds a direction-specific lower-body split from the actual alpha mask;
4. tracks two disconnected leg silhouettes and derives knee, boot and toe
   proxy landmarks from their pixels;
5. measures the landmark travel at the real Godot display scale (0.34);
6. rejects duplicate/near-static frames and excessive silhouette drift; and
7. writes an annotated contact/plant/swing-up montage plus JSON evidence.

The gate intentionally evaluates eight full-body facing atlases only.  It
does not claim true aim-relative strafe/backpedal coverage.  The current
runtime selects the lower atlas from aim/facing, not velocity.  Cross-facing
upper/lower raster splices are explicitly outside this validator because they
create a visible waist discontinuity.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label as connected_components


REPO_ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
FRAME_COUNT = 24
CELL_SIZE = 384
RUNTIME_DISPLAY_SCALE = 0.34
ALPHA_THRESHOLD = 24
SAMPLE_FRAMES = (0, 4, 8, 12, 16, 20)
SAMPLE_LABELS = (
    "L CONTACT",
    "L PLANT",
    "R SWING / UP",
    "R CONTACT",
    "R PLANT",
    "L SWING / UP",
)

# These are intentionally strict visual thresholds.  V5's whole-body bob was
# ~3.7 runtime px while most boot transitions were below 0.5 px.  A V6 pass
# must make *both* legs visibly articulate at gameplay scale.
THRESHOLDS: dict[str, float | int] = {
    "decoded_unique_frames_min": FRAME_COUNT,
    "aligned_leg_unique_frames_min": 22,
    "boot_p2p_runtime_px_each_min": 10.0,
    "boot_adjacent_p75_runtime_px_each_min": 0.80,
    "knee_p2p_runtime_px_each_min": 4.0,
    "knee_p2p_runtime_px_peak_min": 6.0,
    "toe_vertical_p2p_runtime_px_each_min": 3.0,
    "toe_vertical_p2p_runtime_px_peak_min": 5.0,
    "boot_to_upper_bob_ratio_min": 1.75,
    "leg_silhouette_adjacent_change_p75_min": 0.010,
    "full_silhouette_area_drift_ratio_max": 0.18,
    # This is measured below a fixed pelvis cut.  A high swing legitimately
    # moves pixels above that cut, so it is a secondary gross-corruption guard;
    # the full-silhouette 0.18 limit remains the strict shape-stability gate.
    "tracked_lower_cut_area_drift_ratio_max": 0.50,
    "near_duplicate_adjacent_pairs_max": 2,
    "north_south_interfoot_separation_range_runtime_px_min": 5.0,
    "w_panel_white_pixels_min": 500,
    "w_panel_cyan_pixels_min": 200,
    "w_panel_min_to_median_ratio_min": 0.60,
    "w_panel_max_adjacent_change_ratio_max": 0.30,
}


@dataclass
class LegObservation:
    area: int
    boot: np.ndarray
    knee: np.ndarray
    toe: np.ndarray
    mask: np.ndarray


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_json_ready(item) for item in value.tolist()]
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return round(number, 6) if math.isfinite(number) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, Path):
        try:
            return value.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            return str(value.resolve())
    return value


def _shift_array(source: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """Translate without wraparound, retaining source dtype/channels."""

    result = np.zeros_like(source)
    height, width = source.shape[:2]
    src_x0, src_x1 = max(0, -dx), min(width, width - dx)
    dst_x0, dst_x1 = max(0, dx), min(width, width + dx)
    src_y0, src_y1 = max(0, -dy), min(height, height - dy)
    dst_y0, dst_y1 = max(0, dy), min(height, height + dy)
    if src_x1 > src_x0 and src_y1 > src_y0:
        result[dst_y0:dst_y1, dst_x0:dst_x1] = source[
            src_y0:src_y1, src_x0:src_x1
        ]
    return result


def _pairwise_span(points: np.ndarray) -> float:
    if len(points) < 2:
        return 0.0
    delta = points[:, None, :] - points[None, :, :]
    return float(np.linalg.norm(delta, axis=2).max())


def _range_ratio(values: Iterable[float]) -> float:
    array = np.asarray(tuple(values), dtype=np.float64)
    median = float(np.median(array))
    return float(np.ptp(array) / max(median, 1.0))


def _atlas_path(asset_root: Path, direction: str) -> Path:
    direction_root = asset_root / direction
    matches = sorted(direction_root.glob(f"ASTER_MOVE_{direction}_360_UAL_V*_ATLAS.webp"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected exactly one {direction} UAL atlas in {direction_root}, found {len(matches)}"
        )
    return matches[0]


def _atlas_version(asset_root: Path, atlas_paths: Iterable[Path]) -> str:
    for text in (asset_root.name, *(path.name for path in atlas_paths)):
        match = re.search(r"(?:UAL[_-]?|ual[_-]?)(v?\d+)", text)
        if match:
            token = match.group(1).upper()
            return token if token.startswith("V") else f"V{token}"
    return "UNKNOWN"


def _direction_manifest_support(atlas_path: Path) -> dict[str, Any]:
    manifest_name = atlas_path.name.replace("_ATLAS.webp", "_MANIFEST.json")
    manifest_path = atlas_path.with_name(manifest_name)
    if not manifest_path.exists():
        return {
            "present": False,
            "path": manifest_path,
            "atlas_sha256_matches": False,
            "qa": {},
        }
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "present": True,
            "path": manifest_path,
            "sha256": sha256_file(manifest_path),
            "readable": False,
            "atlas_sha256_matches": False,
            "qa": {},
        }
    expected_atlas_sha = str(payload.get("atlas_sha256", "")).lower()
    actual_atlas_sha = sha256_file(atlas_path)
    return {
        "present": True,
        "path": manifest_path,
        "sha256": sha256_file(manifest_path),
        "readable": True,
        "atlas_sha256_matches": expected_atlas_sha == actual_atlas_sha,
        "qa": payload.get("qa", {}) if isinstance(payload.get("qa"), dict) else {},
    }


def _w_panel_retention(
    aligned_rgba: np.ndarray,
    leg_masks: np.ndarray,
    bbox: tuple[int, int, int, int],
    cut_y: int,
) -> dict[str, Any]:
    """Track W's white/cyan thigh-panel material across all 24 frames.

    The measurement is limited to the upper 65% of the alpha-derived lower
    body so white boots cannot hide a missing thigh panel.
    """

    _, _, _, body_y1 = bbox
    panel_y1 = int(round(cut_y + 0.65 * (body_y1 - cut_y)))
    roi = np.zeros((CELL_SIZE, CELL_SIZE), dtype=bool)
    roi[cut_y : panel_y1 + 1] = True
    rgb = aligned_rgba[..., :3].astype(np.int16)
    alpha = aligned_rgba[..., 3] > ALPHA_THRESHOLD
    channel_range = rgb.max(axis=3) - rgb.min(axis=3)
    white = (rgb.min(axis=3) > 130) & (channel_range < 75)
    cyan = (
        (rgb[..., 2] > 120)
        & (rgb[..., 1] > 90)
        & ((rgb[..., 2] - rgb[..., 0]) > 20)
    )

    def material_metrics(material: np.ndarray) -> dict[str, Any]:
        counts = np.count_nonzero(
            material & alpha & leg_masks & roi[None, ...], axis=(1, 2)
        ).astype(np.int64)
        adjacent_ratio = np.abs(np.roll(counts, -1) - counts) / np.maximum(
            np.maximum(counts, np.roll(counts, -1)), 1
        )
        median = max(float(np.median(counts)), 1.0)
        return {
            "counts_by_frame": counts,
            "min_pixels": int(counts.min()),
            "median_pixels": float(np.median(counts)),
            "min_to_median_ratio": float(counts.min()) / median,
            "max_adjacent_change_ratio": float(adjacent_ratio.max()),
        }

    white_metrics = material_metrics(white)
    cyan_metrics = material_metrics(cyan)
    checks = {
        "white_panel_present_every_frame": white_metrics["min_pixels"]
        >= int(THRESHOLDS["w_panel_white_pixels_min"]),
        "cyan_panel_present_every_frame": cyan_metrics["min_pixels"]
        >= int(THRESHOLDS["w_panel_cyan_pixels_min"]),
        "white_panel_retention_ratio": white_metrics["min_to_median_ratio"]
        >= float(THRESHOLDS["w_panel_min_to_median_ratio_min"]),
        "cyan_panel_retention_ratio": cyan_metrics["min_to_median_ratio"]
        >= float(THRESHOLDS["w_panel_min_to_median_ratio_min"]),
        "white_panel_no_abrupt_dropout": white_metrics["max_adjacent_change_ratio"]
        <= float(THRESHOLDS["w_panel_max_adjacent_change_ratio_max"]),
        "cyan_panel_no_abrupt_dropout": cyan_metrics["max_adjacent_change_ratio"]
        <= float(THRESHOLDS["w_panel_max_adjacent_change_ratio_max"]),
    }
    return {
        "method": "white/cyan material pixels inside tracked legs and thigh-only vertical ROI",
        "roi_y_atlas_px": [cut_y, panel_y1],
        "white": white_metrics,
        "cyan": cyan_metrics,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
    }


def _load_atlas(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    expected = (CELL_SIZE * FRAME_COUNT, CELL_SIZE, 4)
    if rgba.shape != expected:
        raise ValueError(f"{path}: expected decoded shape {expected}, got {rgba.shape}")
    return rgba.reshape(FRAME_COUNT, CELL_SIZE, CELL_SIZE, 4)


def _alpha_bbox(masks: np.ndarray) -> tuple[int, int, int, int]:
    union = masks.any(axis=0)
    ys, xs = np.where(union)
    if not len(xs):
        raise ValueError("atlas contains no visible alpha")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _register_to_upper(
    rgba: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, tuple[int, int, int, int], int, list[dict[str, int | float]]]:
    """Integer-register frames using upper-body alpha only.

    An alpha-centroid estimate gives the coarse displacement, followed by a
    small exhaustive XOR search.  No interpolation is used, so the alignment
    itself cannot manufacture motion or blur.
    """

    masks = rgba[..., 3] > ALPHA_THRESHOLD
    x0, y0, x1, y1 = _alpha_bbox(masks)
    body_height = y1 - y0 + 1
    upper_y1 = min(CELL_SIZE - 1, int(round(y0 + body_height * 0.55)))
    reference = masks[0]
    reference_upper = reference[y0 : upper_y1 + 1, x0 : x1 + 1]
    ref_y, ref_x = np.where(reference_upper)
    if not len(ref_x):
        raise ValueError("upper-body registration region is empty")
    reference_centroid = np.array([ref_x.mean(), ref_y.mean()])

    aligned_rgba: list[np.ndarray] = []
    aligned_masks: list[np.ndarray] = []
    shifts: list[dict[str, int | float]] = []
    for frame_index, (frame, mask) in enumerate(zip(rgba, masks, strict=True)):
        upper = mask[y0 : upper_y1 + 1, x0 : x1 + 1]
        ys, xs = np.where(upper)
        if not len(xs):
            raise ValueError(f"frame {frame_index}: empty upper-body registration region")
        current_centroid = np.array([xs.mean(), ys.mean()])
        initial_dx, initial_dy = np.rint(reference_centroid - current_centroid).astype(int)
        best: tuple[int, int, int, np.ndarray] | None = None
        for dy in range(int(initial_dy) - 3, int(initial_dy) + 4):
            for dx in range(int(initial_dx) - 3, int(initial_dx) + 4):
                shifted = _shift_array(mask, dx, dy)
                candidate = shifted[y0 : upper_y1 + 1, x0 : x1 + 1]
                xor_pixels = int(np.count_nonzero(reference_upper ^ candidate))
                # Deterministic tie break: prefer the smaller correction.
                score = (xor_pixels, abs(dx) + abs(dy), abs(dy), abs(dx))
                if best is None or score < (best[0], abs(best[1]) + abs(best[2]), abs(best[2]), abs(best[1])):
                    best = (xor_pixels, dx, dy, shifted)
        assert best is not None
        xor_pixels, dx, dy, shifted_mask = best
        aligned_masks.append(shifted_mask)
        aligned_rgba.append(_shift_array(frame, dx, dy))
        shifts.append(
            {
                "frame": frame_index,
                "dx_atlas_px": dx,
                "dy_atlas_px": dy,
                "upper_alpha_xor_pixels": xor_pixels,
                "upper_alpha_xor_ratio": xor_pixels / max(int(reference_upper.sum()), 1),
            }
        )
    return (
        np.asarray(aligned_rgba),
        np.asarray(aligned_masks),
        (x0, y0, x1, y1),
        upper_y1,
        shifts,
    )


def _component_observations(
    mask: np.ndarray,
    cut_y: int,
    required_bottom_y: float,
) -> list[LegObservation]:
    lower = mask.copy()
    lower[:cut_y] = False
    labels, count = connected_components(lower)
    observations: list[LegObservation] = []
    for component_id in range(1, count + 1):
        component_mask = labels == component_id
        ys, xs = np.where(component_mask)
        if len(xs) <= 150 or float(ys.max()) < required_bottom_y:
            continue
        height = max(1.0, float(ys.max() - ys.min()))
        boot_pixels = ys >= ys.min() + 0.72 * height
        knee_pixels = (ys >= ys.min() + 0.30 * height) & (ys <= ys.min() + 0.56 * height)
        toe_pixels = ys >= ys.min() + 0.90 * height
        if not (boot_pixels.any() and knee_pixels.any() and toe_pixels.any()):
            continue
        observations.append(
            LegObservation(
                area=int(len(xs)),
                boot=np.array([xs[boot_pixels].mean(), ys[boot_pixels].mean()]),
                knee=np.array([xs[knee_pixels].mean(), ys[knee_pixels].mean()]),
                toe=np.array([xs[toe_pixels].mean(), ys[toe_pixels].mean()]),
                mask=component_mask,
            )
        )
    return sorted(observations, key=lambda item: item.area, reverse=True)


def _find_lower_split(
    aligned_masks: np.ndarray,
    bbox: tuple[int, int, int, int],
) -> tuple[float, int, list[list[LegObservation]]]:
    _, y0, _, y1 = bbox
    body_height = y1 - y0 + 1
    # A real swing/up pose can lift a complete boot well above the bottom 20%
    # of the standing silhouette.  Requiring 0.80 (which happened to work for
    # frozen V5) incorrectly discarded the strongest V6 swing frames.  0.65
    # remains below the pelvis split while retaining the raised leg.
    required_bottom_y = y0 + 0.65 * body_height
    for fraction in np.arange(0.56, 0.801, 0.01):
        cut_y = int(round(y0 + float(fraction) * body_height))
        candidates = [
            _component_observations(mask, cut_y, required_bottom_y)
            for mask in aligned_masks
        ]
        if min(len(items) for items in candidates) >= 2:
            return float(fraction), cut_y, candidates
    counts = [
        len(_component_observations(mask, int(round(y0 + 0.80 * body_height)), required_bottom_y))
        for mask in aligned_masks
    ]
    raise ValueError(f"could not isolate two leg silhouettes in all frames; counts={counts}")


def _track_legs(
    candidates: list[list[LegObservation]],
) -> tuple[list[list[LegObservation]], list[dict[str, Any]]]:
    first = sorted(candidates[0][:2], key=lambda item: float(item.boot[0]))
    tracks: list[list[LegObservation]] = [[first[0]], [first[1]]]
    assignments: list[dict[str, Any]] = [
        {
            "frame": 0,
            "candidate_count": len(candidates[0]),
            "assignment_cost_atlas_px": 0.0,
        }
    ]
    previous = first
    for frame_index in range(1, FRAME_COUNT):
        frame_candidates = candidates[frame_index][:4]
        best: tuple[float, int, int] | None = None
        for first_index, second_index in itertools.permutations(range(len(frame_candidates)), 2):
            selected = (frame_candidates[first_index], frame_candidates[second_index])
            cost = 0.0
            for prior, current in zip(previous, selected, strict=True):
                cost += float(np.linalg.norm(current.boot - prior.boot))
                cost += 0.25 * float(np.linalg.norm(current.knee - prior.knee))
                cost += 0.08 * abs(current.area - prior.area) / max(prior.area, 1)
            if best is None or cost < best[0]:
                best = (cost, first_index, second_index)
        if best is None:
            raise ValueError(f"frame {frame_index}: unable to assign two leg components")
        chosen = [frame_candidates[best[1]], frame_candidates[best[2]]]
        tracks[0].append(chosen[0])
        tracks[1].append(chosen[1])
        previous = chosen
        assignments.append(
            {
                "frame": frame_index,
                "candidate_count": len(candidates[frame_index]),
                "assignment_cost_atlas_px": best[0],
            }
        )
    return tracks, assignments


def _trajectory_metrics(points: np.ndarray) -> dict[str, Any]:
    adjacent = np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1)
    return {
        "p2p_atlas_px": _pairwise_span(points),
        "p2p_runtime_px": _pairwise_span(points) * RUNTIME_DISPLAY_SCALE,
        "x_range_runtime_px": float(np.ptp(points[:, 0])) * RUNTIME_DISPLAY_SCALE,
        "y_range_runtime_px": float(np.ptp(points[:, 1])) * RUNTIME_DISPLAY_SCALE,
        "adjacent_runtime_px": {
            "min": float(adjacent.min()) * RUNTIME_DISPLAY_SCALE,
            "median": float(np.median(adjacent)) * RUNTIME_DISPLAY_SCALE,
            "p75": float(np.percentile(adjacent, 75)) * RUNTIME_DISPLAY_SCALE,
            "max": float(adjacent.max()) * RUNTIME_DISPLAY_SCALE,
        },
        "points_atlas_px": points,
    }


def _evaluate_direction(direction: str, atlas_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    rgba = _load_atlas(atlas_path)
    manifest_support = _direction_manifest_support(atlas_path)
    is_v6 = "UAL_V6" in atlas_path.name.upper()
    decoded_hashes = [sha256_bytes(frame.tobytes()) for frame in rgba]
    aligned_rgba, aligned_masks, bbox, upper_y1, shifts = _register_to_upper(rgba)
    lower_fraction, cut_y, candidates = _find_lower_split(aligned_masks, bbox)
    tracks, assignments = _track_legs(candidates)

    boot_tracks = [np.asarray([item.boot for item in track]) for track in tracks]
    knee_tracks = [np.asarray([item.knee for item in track]) for track in tracks]
    toe_tracks = [np.asarray([item.toe for item in track]) for track in tracks]
    boot_metrics = [_trajectory_metrics(points) for points in boot_tracks]
    knee_metrics = [_trajectory_metrics(points) for points in knee_tracks]
    toe_metrics = [_trajectory_metrics(points) for points in toe_tracks]

    leg_masks: list[np.ndarray] = []
    tracked_leg_areas: list[int] = []
    for frame_index in range(FRAME_COUNT):
        frame_leg_mask = tracks[0][frame_index].mask | tracks[1][frame_index].mask
        leg_masks.append(frame_leg_mask)
        tracked_leg_areas.append(int(frame_leg_mask.sum()))
    leg_masks_array = np.asarray(leg_masks)
    packed_leg_hashes = [
        sha256_bytes(np.packbits(mask[cut_y:]).tobytes()) for mask in leg_masks_array
    ]

    adjacent_leg_changes: list[float] = []
    near_duplicate_pairs: list[list[int]] = []
    median_leg_area = max(float(np.median(tracked_leg_areas)), 1.0)
    for frame_index in range(FRAME_COUNT):
        next_index = (frame_index + 1) % FRAME_COUNT
        difference = int(np.count_nonzero(leg_masks_array[frame_index] ^ leg_masks_array[next_index]))
        ratio = difference / median_leg_area
        adjacent_leg_changes.append(ratio)
        if ratio < 0.003:
            near_duplicate_pairs.append([frame_index, next_index])

    full_areas = [int(mask.sum()) for mask in aligned_masks]
    shift_points = np.asarray(
        [[float(item["dx_atlas_px"]), float(item["dy_atlas_px"])] for item in shifts]
    )
    upper_bob_runtime = _pairwise_span(shift_points) * RUNTIME_DISPLAY_SCALE
    boot_p2p = [float(item["p2p_runtime_px"]) for item in boot_metrics]
    boot_adjacent_p75 = [
        float(item["adjacent_runtime_px"]["p75"]) for item in boot_metrics
    ]
    knee_p2p = [float(item["p2p_runtime_px"]) for item in knee_metrics]
    toe_vertical_p2p = [float(item["y_range_runtime_px"]) for item in toe_metrics]
    interfoot = np.linalg.norm(boot_tracks[0] - boot_tracks[1], axis=1) * RUNTIME_DISPLAY_SCALE
    interfoot_range = float(np.ptp(interfoot))
    boot_to_upper_ratio = min(boot_p2p) / max(upper_bob_runtime, 0.001)

    checks: dict[str, bool] = {
        "decoded_all_24_frames_unique": len(set(decoded_hashes))
        >= int(THRESHOLDS["decoded_unique_frames_min"]),
        "aligned_leg_frames_substantially_unique": len(set(packed_leg_hashes))
        >= int(THRESHOLDS["aligned_leg_unique_frames_min"]),
        "both_boots_travel_at_least_10_runtime_px": min(boot_p2p)
        >= float(THRESHOLDS["boot_p2p_runtime_px_each_min"]),
        "both_boots_have_visible_adjacent_swing": min(boot_adjacent_p75)
        >= float(THRESHOLDS["boot_adjacent_p75_runtime_px_each_min"]),
        "both_knees_articulate": min(knee_p2p)
        >= float(THRESHOLDS["knee_p2p_runtime_px_each_min"]),
        "at_least_one_knee_has_strong_articulation": max(knee_p2p)
        >= float(THRESHOLDS["knee_p2p_runtime_px_peak_min"]),
        "both_toes_lift": min(toe_vertical_p2p)
        >= float(THRESHOLDS["toe_vertical_p2p_runtime_px_each_min"]),
        "at_least_one_toe_has_clear_lift": max(toe_vertical_p2p)
        >= float(THRESHOLDS["toe_vertical_p2p_runtime_px_peak_min"]),
        "leg_motion_dominates_rigid_upper_bob": boot_to_upper_ratio
        >= float(THRESHOLDS["boot_to_upper_bob_ratio_min"]),
        "leg_silhouette_changes_between_frames": float(np.percentile(adjacent_leg_changes, 75))
        >= float(THRESHOLDS["leg_silhouette_adjacent_change_p75_min"]),
        "full_silhouette_area_stable": _range_ratio(full_areas)
        <= float(THRESHOLDS["full_silhouette_area_drift_ratio_max"]),
        "tracked_lower_cut_area_reasonable": _range_ratio(tracked_leg_areas)
        <= float(THRESHOLDS["tracked_lower_cut_area_drift_ratio_max"]),
        "no_excessive_near_duplicate_adjacent_frames": len(near_duplicate_pairs)
        <= int(THRESHOLDS["near_duplicate_adjacent_pairs_max"]),
    }
    if direction in ("N", "S"):
        checks["north_south_depth_separation_changes"] = interfoot_range >= float(
            THRESHOLDS["north_south_interfoot_separation_range_runtime_px_min"]
        )
    primary_checks = dict(checks)
    auxiliary_checks: dict[str, bool] = {}

    w_panel_support: dict[str, Any] | None = None
    if direction == "W":
        w_panel_support = _w_panel_retention(
            aligned_rgba, leg_masks_array, bbox, cut_y
        )
        auxiliary_checks.update(
            {
                f"w_material_{name}": bool(passed)
                for name, passed in w_panel_support["checks"].items()
            }
        )

    s_weapon_support: dict[str, Any] | None = None
    if direction == "S" and is_v6:
        authoring_qa = manifest_support.get("qa", {})
        weapon_rgb_delta = authoring_qa.get("weapon_core_max_rgb_delta")
        weapon_alpha_delta = authoring_qa.get("weapon_core_max_alpha_delta")
        weapon_stable = authoring_qa.get("weapon_corridor_pixel_stable")
        green_residual = authoring_qa.get("visible_green_residual_pixels")
        s_weapon_checks = {
            "manifest_pins_evaluated_atlas": bool(
                manifest_support.get("atlas_sha256_matches", False)
            ),
            "weapon_core_rgb_delta_lte_1": isinstance(weapon_rgb_delta, (int, float))
            and float(weapon_rgb_delta) <= 1.0,
            "weapon_core_alpha_delta_lte_1": isinstance(weapon_alpha_delta, (int, float))
            and float(weapon_alpha_delta) <= 1.0,
            "weapon_corridor_marked_pixel_stable": weapon_stable is True,
            "weapon_corridor_has_no_visible_green_residual": green_residual == 0,
        }
        auxiliary_checks.update(
            {
                f"s_weapon_{name}": bool(passed)
                for name, passed in s_weapon_checks.items()
            }
        )
        s_weapon_support = {
            "role": "generator-authored supporting QA pinned to the exact atlas SHA; independent leg metrics remain primary",
            "weapon_core_max_rgb_delta": weapon_rgb_delta,
            "weapon_core_max_alpha_delta": weapon_alpha_delta,
            "weapon_corridor_pixel_stable": weapon_stable,
            "visible_green_residual_pixels": green_residual,
            "checks": s_weapon_checks,
            "gate": "PASS" if all(s_weapon_checks.values()) else "FAIL",
        }

    primary_gate = "PASS" if all(primary_checks.values()) else "FAIL"
    auxiliary_gate = "PASS" if all(auxiliary_checks.values()) else "FAIL"
    combined_gate = "PASS" if primary_gate == "PASS" and auxiliary_gate == "PASS" else "FAIL"

    report = {
        "direction": direction,
        "atlas": atlas_path,
        "atlas_sha256": sha256_file(atlas_path),
        "authoring_manifest_support": manifest_support,
        "decoded_unique_frames": len(set(decoded_hashes)),
        "aligned_leg_unique_frames": len(set(packed_leg_hashes)),
        "alpha_bbox_atlas_px": list(bbox),
        "upper_registration_y_max_atlas_px": upper_y1,
        "lower_split": {
            "fraction_of_body_height": lower_fraction,
            "y_atlas_px": cut_y,
            "derivation": "first alpha cut separating two lower-reaching components in all 24 aligned frames",
        },
        "upper_rigid_bob_removed": {
            "translation_p2p_atlas_px": _pairwise_span(shift_points),
            "translation_p2p_runtime_px": upper_bob_runtime,
            "shifts": shifts,
        },
        "landmark_authority": {
            "type": "direction-specific alpha-derived leg component proxies",
            "frame_0": [
                {
                    "track": track_index,
                    "knee_atlas_px": knee_tracks[track_index][0],
                    "boot_atlas_px": boot_tracks[track_index][0],
                    "toe_atlas_px": toe_tracks[track_index][0],
                }
                for track_index in range(2)
            ],
        },
        "boot_tracks": boot_metrics,
        "knee_tracks": knee_metrics,
        "toe_tracks": toe_metrics,
        "interfoot_separation_runtime_px": {
            "min": float(interfoot.min()),
            "max": float(interfoot.max()),
            "range": interfoot_range,
        },
        "boot_to_upper_bob_ratio_using_weaker_boot": boot_to_upper_ratio,
        "leg_silhouette_adjacent_change_ratio": {
            "min": float(np.min(adjacent_leg_changes)),
            "median": float(np.median(adjacent_leg_changes)),
            "p75": float(np.percentile(adjacent_leg_changes, 75)),
            "max": float(np.max(adjacent_leg_changes)),
        },
        "silhouette_area_drift": {
            "full_ratio": _range_ratio(full_areas),
            "tracked_lower_cut_ratio": _range_ratio(tracked_leg_areas),
        },
        "near_duplicate_adjacent_pairs": near_duplicate_pairs,
        "component_assignments": assignments,
        "w_white_cyan_thigh_panel_retention": w_panel_support,
        "s_weapon_cage_stability": s_weapon_support,
        "primary_leg_motion_checks": primary_checks,
        "auxiliary_costume_weapon_checks": auxiliary_checks,
        "primary_leg_motion_gate": primary_gate,
        "auxiliary_costume_weapon_gate": auxiliary_gate,
        "combined_visible_asset_gate": combined_gate,
        # Backward-compatible alias used by the montage renderer and older
        # one-gate callers.  It intentionally means the primary leg gate.
        "visible_motion_gate": primary_gate,
        "failed_checks": [
            name for name, passed in primary_checks.items() if not passed
        ],
        "failed_auxiliary_checks": [
            name for name, passed in auxiliary_checks.items() if not passed
        ],
    }
    drawing = {
        "aligned_rgba": aligned_rgba,
        "cut_y": cut_y,
        "boot_tracks": boot_tracks,
        "knee_tracks": knee_tracks,
        "toe_tracks": toe_tracks,
        "visible_motion_gate": report["visible_motion_gate"],
        "boot_p2p": boot_p2p,
        "knee_p2p": knee_p2p,
    }
    return report, drawing


def _font(size: int) -> ImageFont.ImageFont:
    font_candidates = (
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    )
    for candidate in font_candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def _build_montage(
    direction_drawings: dict[str, dict[str, Any]],
    output_path: Path,
    version: str,
) -> None:
    cell = 192
    header = 58
    label_height = 42
    width = cell * len(SAMPLE_FRAMES)
    height = header + (cell + label_height) * len(DIRECTIONS)
    sheet = Image.new("RGB", (width, height), (8, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title_font = _font(18)
    label_font = _font(11)
    tiny_font = _font(9)
    draw.text(
        (12, 8),
        f"ASTER MOVE 360 UAL {version} — VISIBLE LEG MOTION GATE (runtime scale {RUNTIME_DISPLAY_SCALE:.2f})",
        fill=(90, 235, 238),
        font=title_font,
    )
    draw.text(
        (12, 32),
        "Upper rigid bob removed before alpha-derived knee / boot / toe tracking",
        fill=(170, 187, 196),
        font=label_font,
    )

    colors = ((255, 177, 47), (62, 232, 255))
    for row, direction in enumerate(DIRECTIONS):
        info = direction_drawings[direction]
        row_y = header + row * (cell + label_height)
        aligned = info["aligned_rgba"]
        cut_y = int(info["cut_y"])
        for column, (frame_index, sample_label) in enumerate(zip(SAMPLE_FRAMES, SAMPLE_LABELS, strict=True)):
            frame = Image.fromarray(aligned[frame_index], "RGBA")
            overlay = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (8, 15, 20, 255))
            overlay.alpha_composite(frame)
            frame_draw = ImageDraw.Draw(overlay)
            frame_draw.line((0, cut_y, CELL_SIZE, cut_y), fill=(235, 75, 86, 150), width=2)
            for track_index, color in enumerate(colors):
                boot_points = info["boot_tracks"][track_index]
                knee_points = info["knee_tracks"][track_index]
                toe_points = info["toe_tracks"][track_index]
                trajectory = [tuple(map(float, point)) for point in boot_points]
                frame_draw.line(trajectory + [trajectory[0]], fill=(*color, 105), width=2)
                for point, radius in (
                    (knee_points[frame_index], 5),
                    (boot_points[frame_index], 7),
                    (toe_points[frame_index], 4),
                ):
                    x, y = map(float, point)
                    frame_draw.ellipse(
                        (x - radius, y - radius, x + radius, y + radius),
                        outline=(*color, 255),
                        width=3,
                    )
            resized = overlay.convert("RGB").resize((cell, cell), Image.Resampling.LANCZOS)
            x = column * cell
            sheet.paste(resized, (x, row_y))
            draw.rectangle((x, row_y, x + 53, row_y + 17), fill=(0, 0, 0))
            draw.text(
                (x + 4, row_y + 3),
                f"{direction} F{frame_index:02d}",
                fill=(95, 235, 238),
                font=tiny_font,
            )
            draw.text(
                (x + 5, row_y + cell + 2),
                sample_label,
                fill=(205, 216, 222),
                font=tiny_font,
            )
        gate_color = (82, 232, 146) if info["visible_motion_gate"] == "PASS" else (255, 95, 95)
        metric = (
            f"{direction} {info['visible_motion_gate']}  "
            f"BOOT {min(info['boot_p2p']):.1f}/{max(info['boot_p2p']):.1f}px  "
            f"KNEE {min(info['knee_p2p']):.1f}/{max(info['knee_p2p']):.1f}px"
        )
        draw.text((5, row_y + cell + 19), metric, fill=gate_color, font=tiny_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=True)


def evaluate(asset_root: Path, qa_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    atlas_paths = [_atlas_path(asset_root, direction) for direction in DIRECTIONS]
    version = _atlas_version(asset_root, atlas_paths)
    reports: dict[str, Any] = {}
    drawings: dict[str, Any] = {}
    for direction, atlas_path in zip(DIRECTIONS, atlas_paths, strict=True):
        report, drawing = _evaluate_direction(direction, atlas_path)
        reports[direction] = report
        drawings[direction] = drawing

    all_primary_pass = all(
        item["primary_leg_motion_gate"] == "PASS" for item in reports.values()
    )
    all_auxiliary_pass = all(
        item["auxiliary_costume_weapon_gate"] == "PASS"
        for item in reports.values()
    )
    all_combined_pass = all_primary_pass and all_auxiliary_pass
    stem = f"ASTER_MOVE_360_UAL_{version}_VISIBLE_MOTION"
    montage_path = qa_dir / f"{stem}_CONTACT_PASSING_UP_MONTAGE.png"
    report_path = qa_dir / f"{stem}_QA.json"
    _build_montage(drawings, montage_path, version)

    overall = {
        "schema": 1,
        "role": "ASTER UAL locomotion visible-leg regression evidence",
        "version": version,
        "asset_root": asset_root,
        "runtime_contract": {
            "atlas_cell_size": [CELL_SIZE, CELL_SIZE],
            "frame_count_per_direction": FRAME_COUNT,
            "runtime_display_scale": RUNTIME_DISPLAY_SCALE,
            "measurements_reported_in_runtime_pixels": True,
        },
        "method": {
            "upper_body_registration": "integer alpha-silhouette registration; no resampling",
            "lower_landmarks": "direction-specific connected alpha components with knee/boot/toe pixel centroids",
            "motion_source": "decoded atlas pixels, never atlas cursor/frame index",
        },
        "thresholds": THRESHOLDS,
        "directions": reports,
        "all_eight_directions_present": set(reports) == set(DIRECTIONS),
        "visible_leg_motion_gate": "PASS" if all_primary_pass else "FAIL",
        "auxiliary_costume_weapon_gate": "PASS" if all_auxiliary_pass else "FAIL",
        "combined_visible_asset_gate": "PASS" if all_combined_pass else "FAIL",
        "human_visual_review": "REQUIRED_AFTER_METRIC_GATE",
        "failed_directions": [
            direction
            for direction, item in reports.items()
            if item["primary_leg_motion_gate"] != "PASS"
        ],
        "failed_auxiliary_directions": [
            direction
            for direction, item in reports.items()
            if item["auxiliary_costume_weapon_gate"] != "PASS"
        ],
        "montage": montage_path,
        "scope_contract": {
            "eight_direction_full_body_evaluated": True,
            "true_strafe_backpedal_runtime_gate": "FAIL_HOLD_NOT_PROVEN",
            "reason": "current runtime lower atlas selection follows aim/facing sector rather than velocity sector",
            "cross_direction_upper_lower_splice_allowed": False,
            "cross_direction_splice_rejection_reason": "mixing unrelated raster authorities creates a visible waist gap/discontinuity",
        },
        "production_expansion": "HOLD",
    }
    qa_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(_json_ready(overall), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return overall, report_path, montage_path


def _default_paths() -> tuple[Path, Path, Path]:
    v6_root = REPO_ROOT / "assets/units/operators/aster/move_360_ual_v6"
    v5_root = REPO_ROOT / "assets/units/operators/aster/move_360_ual_v5"
    # Keep QA outside the generator's final V6 destination.  The generator
    # uses an atomic promote and correctly refuses to replace a pre-existing
    # ``move_360_ual_v6`` directory.
    qa_dir = REPO_ROOT / "artifacts/aster_ual_v6_visible_leg_audit"
    return v6_root, v5_root, qa_dir


def main() -> int:
    default_v6, default_v5, default_qa = _default_paths()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--asset-root",
        type=Path,
        default=None,
        help="Eight-direction atlas root. Defaults to V6; if absent, audits V5 as a rejected baseline.",
    )
    parser.add_argument("--qa-dir", type=Path, default=default_qa)
    parser.add_argument(
        "--expect-fail",
        action="store_true",
        help="Return success only when the evaluated atlas fails (for the frozen-leg V5 regression fixture).",
    )
    args = parser.parse_args()

    explicit_root = args.asset_root is not None
    asset_root = (args.asset_root or default_v6).resolve()
    evaluated_v5_fallback = False
    if not asset_root.exists() and not explicit_root:
        print(f"V6 asset root not ready: {asset_root}")
        print(f"Auditing known-rejected V5 baseline instead: {default_v5}")
        asset_root = default_v5.resolve()
        evaluated_v5_fallback = True

    try:
        overall, report_path, montage_path = evaluate(asset_root, args.qa_dir.resolve())
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"ASTER_UAL_VISIBLE_MOTION_GATE: ERROR: {error}", file=sys.stderr)
        return 2

    primary_gate = overall["visible_leg_motion_gate"]
    auxiliary_gate = overall["auxiliary_costume_weapon_gate"]
    gate = overall["combined_visible_asset_gate"]
    print(
        f"ASTER_UAL_{overall['version']}_PRIMARY_VISIBLE_LEG_MOTION_GATE: "
        f"{primary_gate}"
    )
    print(
        f"ASTER_UAL_{overall['version']}_AUXILIARY_COSTUME_WEAPON_GATE: "
        f"{auxiliary_gate}"
    )
    print(f"ASTER_UAL_{overall['version']}_COMBINED_VISIBLE_ASSET_GATE: {gate}")
    for direction in DIRECTIONS:
        item = overall["directions"][direction]
        boots = [track["p2p_runtime_px"] for track in item["boot_tracks"]]
        knees = [track["p2p_runtime_px"] for track in item["knee_tracks"]]
        print(
            f"  {direction}: primary={item['primary_leg_motion_gate']} "
            f"aux={item['auxiliary_costume_weapon_gate']} | "
            f"boots={boots[0]:.2f}/{boots[1]:.2f}px | "
            f"knees={knees[0]:.2f}/{knees[1]:.2f}px | "
            f"primary_failed={','.join(item['failed_checks']) or 'none'} | "
            f"aux_failed={','.join(item['failed_auxiliary_checks']) or 'none'}"
        )
    print(f"QA JSON: {report_path}")
    print(f"Montage: {montage_path}")
    print("TRUE_STRAFE_BACKPEDAL_RUNTIME_GATE: FAIL_HOLD_NOT_PROVEN")

    if args.expect_fail:
        return 0 if gate == "FAIL" else 1
    if evaluated_v5_fallback:
        print("V6_VISIBLE_MOTION_GATE: NOT_READY (V5 rejection reconfirmed)")
        return 3
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
