#!/usr/bin/env python3
"""Reconstruct and preserve the immediate pre-fix ASTER composite V5.

This is a byte-verified historical asset only.  It intentionally reproduces
the rejected pelvis-to-runtime-offset corridor and unbounded hair mask so the
user can compare the costume drift against the fixed atomic V5 family.  It is
never a runtime fallback or promotion candidate.
"""

from __future__ import annotations

import json
import importlib.util
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

_BUILDER_PATH = Path(__file__).with_name("build_aster_composite_fire_v5.py")
_BUILDER_SPEC = importlib.util.spec_from_file_location("aster_composite_builder", _BUILDER_PATH)
if _BUILDER_SPEC is None or _BUILDER_SPEC.loader is None:
    raise RuntimeError(f"cannot load builder module: {_BUILDER_PATH}")
_BUILDER = importlib.util.module_from_spec(_BUILDER_SPEC)
_BUILDER_SPEC.loader.exec_module(_BUILDER)

CELL = _BUILDER.CELL
DIRECTIONS = _BUILDER.DIRECTIONS
FEATHER_PX = _BUILDER.FEATHER_PX
ROOT = _BUILDER.ROOT
apply_partition = _BUILDER.apply_partition
clean_idle_shadow_artifact = _BUILDER.clean_idle_shadow_artifact
direction_geometry = _BUILDER.direction_geometry
distance_to_segment = _BUILDER.distance_to_segment
read_atlas = _BUILDER.read_atlas
resolved_source_specs = _BUILDER.resolved_source_specs
save_lossless_atlas = _BUILDER.save_lossless_atlas
sha256 = _BUILDER.sha256
smoothstep = _BUILDER.smoothstep


LEGACY_MUZZLE_OFFSET = {
    "E": (118.0, -30.0),
    "SE": (92.0, 48.0),
    "S": (0.0, 94.0),
    "SW": (-92.0, 48.0),
    "W": (-118.0, -18.0),
    "NW": (-88.0, -72.0),
    "N": (0.0, -104.0),
    "NE": (88.0, -72.0),
}


def legacy_connected_hair_weight(frame: np.ndarray, geometry: dict[str, float]) -> np.ndarray:
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
    y_limit = int(min(CELL - 1, geometry["split_y"] + geometry["height"] * 0.34))
    candidate[y_limit + 1 :] = False
    closed = cv2.morphologyEx(
        candidate.astype(np.uint8),
        cv2.MORPH_CLOSE,
        np.ones((5, 5), np.uint8),
    )
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


def legacy_lower_partition(
    frame: np.ndarray,
    direction: str,
    geometry: dict[str, float],
) -> np.ndarray:
    grid_y, grid_x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    split_y = geometry["split_y"]
    lower = smoothstep(
        split_y - FEATHER_PX * 0.5,
        split_y + FEATHER_PX * 0.5,
        grid_y,
    ).astype(np.float32)
    start = np.asarray(
        (geometry["pelvis_x"], geometry["top"] + geometry["height"] * 0.35),
        dtype=np.float32,
    )
    offset = LEGACY_MUZZLE_OFFSET[direction]
    end = np.asarray((CELL * 0.5 + offset[0], CELL * 0.5 + offset[1]), dtype=np.float32)
    distance = distance_to_segment(grid_x, grid_y, start, end)
    corridor = 1.0 - smoothstep(13.0, 13.0 + FEATHER_PX, distance)
    hair = legacy_connected_hair_weight(frame, geometry)
    lower *= 1.0 - np.maximum(corridor.astype(np.float32), hair)
    return np.clip(lower, 0.0, 1.0)


def main() -> int:
    fixed_authoring = ROOT / "art_src/pilot_v2/aster_v2/animation_360/composite_fire_v5"
    original_manifest_path = fixed_authoring / "ASTER_COMPOSITE_FIRE_V5_MANIFEST_PREVIOUS_BLOB.json"
    original_contact_path = fixed_authoring / "ASTER_COMPOSITE_FIRE_V5_CONTACT_PREVIOUS_BLOB.png"
    if not original_manifest_path.is_file() or not original_contact_path.is_file():
        raise SystemExit("fixed V5 does not contain the immediate previous review blobs")
    original_manifest = json.loads(original_manifest_path.read_text(encoding="utf-8"))
    expected_contact_sha = original_manifest.get("preview_sha256")
    if sha256(original_contact_path) != expected_contact_sha:
        raise SystemExit("preserved previous contact hash does not match its manifest")

    runtime = ROOT / "assets/units/operators/aster/composite_fire_v5_costume_drift_prev"
    authoring = ROOT / "art_src/pilot_v2/aster_v2/animation_360/composite_fire_v5_costume_drift_prev"
    if runtime.exists() or authoring.exists():
        raise SystemExit("refusing to overwrite preserved immediate previous V5")
    runtime.parent.mkdir(parents=True, exist_ok=True)
    authoring.parent.mkdir(parents=True, exist_ok=True)
    runtime_stage = Path(tempfile.mkdtemp(prefix="composite_fire_v5_drift_prev_runtime_", dir=runtime.parent))
    authoring_stage = Path(tempfile.mkdtemp(prefix="composite_fire_v5_drift_prev_authoring_", dir=authoring.parent))
    promoted_runtime = False
    promoted_authoring = False
    specs = resolved_source_specs("v5")
    records: dict[str, Any] = {}
    try:
        for direction in DIRECTIONS:
            move_frames = read_atlas(ROOT / specs["move_lower"]["path"].format(direction=direction), 24)
            geometry = direction_geometry(move_frames)
            clean_move_support = cv2.dilate(
                (np.max(move_frames[:, :, :, 3], axis=0) > 8).astype(np.uint8),
                np.ones((9, 9), np.uint8),
                iterations=1,
            ) > 0
            records[direction] = {}
            for kind, spec in specs.items():
                source_frames = read_atlas(ROOT / spec["path"].format(direction=direction), int(spec["count"]))
                split_frames: list[np.ndarray] = []
                for source_frame in source_frames:
                    frame = source_frame
                    if kind == "idle_lower":
                        frame, _cleanup = clean_idle_shadow_artifact(
                            frame,
                            clean_move_support,
                            geometry["split_y"],
                        )
                    lower_weight = legacy_lower_partition(frame, direction, geometry)
                    weight = lower_weight if spec["layer"] == "lower" else 1.0 - lower_weight
                    split_frames.append(apply_partition(frame, weight))
                relative = Path(spec["output"].format(direction=direction))
                destination = runtime_stage / relative
                save_lossless_atlas(split_frames, destination)
                expected = original_manifest["directions_output"][direction]["layers"][kind]["output_sha256"]
                actual = sha256(destination)
                if actual != expected:
                    raise RuntimeError(
                        f"legacy reconstruction hash mismatch: {direction} {kind}: {actual} != {expected}"
                    )
                records[direction][kind] = {
                    "file": (runtime / relative).relative_to(ROOT).as_posix(),
                    "sha256": actual,
                    "matches_immediate_previous_manifest": True,
                }

        shutil.copy2(original_contact_path, authoring_stage / "ASTER_COMPOSITE_FIRE_V5_COSTUME_DRIFT_PREV_CONTACT.png")
        shutil.copy2(original_manifest_path, authoring_stage / "ASTER_COMPOSITE_FIRE_V5_ORIGINAL_MANIFEST.json")
        preservation = {
            "schema": 1,
            "role": "immediate previous rejected ASTER composite V5; visual comparison only",
            "runtime_eligible": False,
            "rejection": "W and other affected fire frames overwrite pelvis/thigh costume authority",
            "source_contact": (
                authoring / "ASTER_COMPOSITE_FIRE_V5_COSTUME_DRIFT_PREV_CONTACT.png"
            ).relative_to(ROOT).as_posix(),
            "source_contact_sha256": expected_contact_sha,
            "original_manifest": (
                authoring / "ASTER_COMPOSITE_FIRE_V5_ORIGINAL_MANIFEST.json"
            ).relative_to(ROOT).as_posix(),
            "all_runtime_atlases_byte_match_immediate_previous": True,
            "directions": records,
        }
        preservation_path = authoring_stage / "PRESERVATION_MANIFEST.json"
        preservation_path.write_text(
            json.dumps(preservation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(runtime_stage, runtime)
        promoted_runtime = True
        os.replace(authoring_stage, authoring)
        promoted_authoring = True
        print(
            "ASTER_COMPOSITE_FIRE_V5_DRIFT_PREV="
            + json.dumps(
                {
                    "directions": len(DIRECTIONS),
                    "atlases": len(DIRECTIONS) * len(specs),
                    "byte_match": True,
                    "runtime_eligible": False,
                    "manifest": (
                        authoring / "PRESERVATION_MANIFEST.json"
                    ).relative_to(ROOT).as_posix(),
                },
                ensure_ascii=False,
            )
        )
        return 0
    finally:
        if not promoted_runtime and runtime_stage.exists():
            shutil.rmtree(runtime_stage)
        if not promoted_authoring and authoring_stage.exists():
            shutil.rmtree(authoring_stage)


if __name__ == "__main__":
    raise SystemExit(main())
