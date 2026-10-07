#!/usr/bin/env python3
"""Generate twelve smooth ASTER move frames for the seven unfinished directions.

The accepted direction artwork is never regenerated.  Instead, the lower-body
motion rhythm from the existing headless Blender 360 pose driver is sampled as
a continuous twelve-step cycle and applied as a premultiplied-alpha 2D warp.
This preserves ASTER, weapon, costume, framing, and facing direction while
removing the eight-identical-frame stutter in the earlier review atlas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
KEYS = (
    "contact_a", "down_a", "push_a", "passing_a", "high_a", "reach_a",
    "contact_b", "down_b", "push_b", "passing_b", "high_b", "reach_b",
)
SCREEN_VECTOR = {
    "E": (1.0, 0.0), "SE": (math.sqrt(0.5), math.sqrt(0.5)), "S": (0.0, 1.0),
    "SW": (-math.sqrt(0.5), math.sqrt(0.5)), "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), -math.sqrt(0.5)), "N": (0.0, -1.0),
    "NE": (math.sqrt(0.5), -math.sqrt(0.5)),
}
GREEN = np.array([0.0, 255.0, 0.0], dtype=np.float32)


def project_path(path: Path, label: str) -> Path:
    value = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        value.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {value}") from exc
    return value


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    scaled = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return scaled * scaled * (3.0 - 2.0 * scaled)


def source_alpha(rgb: np.ndarray) -> np.ndarray:
    distance = np.linalg.norm(rgb.astype(np.float32) - GREEN[None, None, :], axis=2)
    alpha = np.clip((distance - 10.0) / 42.0, 0.0, 1.0)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.65)
    return np.clip(alpha, 0.0, 1.0)


def warp_frame(rgb: np.ndarray, alpha: np.ndarray, direction: str, index: int) -> tuple[np.ndarray, np.ndarray]:
    height, width = alpha.shape
    ys, xs = np.nonzero(alpha > 0.16)
    if len(xs) == 0:
        raise RuntimeError("source artwork contains no non-green character")
    left, right = float(xs.min()), float(xs.max())
    top, bottom = float(ys.min()), float(ys.max())
    body_w, body_h = right - left + 1.0, bottom - top + 1.0
    center_x = float(np.median(xs[ys > top + body_h * 0.52]))
    hip_y = top + body_h * 0.53
    knee_y = top + body_h * 0.73

    grid_y, grid_x = np.mgrid[0:height, 0:width].astype(np.float32)
    lower = smoothstep(hip_y - body_h * 0.055, hip_y + body_h * 0.105, grid_y)
    distal = smoothstep(hip_y, bottom, grid_y)
    side = np.tanh((grid_x - center_x) / max(body_w * 0.055, 1.0))
    left_weight = lower * (1.0 - side) * 0.5
    right_weight = lower * (1.0 + side) * 0.5

    phase = 2.0 * math.pi * index / len(KEYS)
    stride = math.cos(phase)
    direction_x, direction_y = SCREEN_VECTOR[direction]
    stride_amplitude = body_h * 0.026
    leg_opposition = left_weight - right_weight
    displacement_x = leg_opposition * stride * stride_amplitude * direction_x * (0.35 + 0.65 * distal)
    displacement_y = leg_opposition * stride * stride_amplitude * direction_y * (0.35 + 0.65 * distal)

    # A passing leg rises; the opposite planted boot stays stable.  This is a
    # continuous curve, so contact frame 11 flows cleanly back to frame 0.
    lift_left = max(0.0, math.sin(phase))
    lift_right = max(0.0, -math.sin(phase))
    foot_lift = (left_weight * lift_left + right_weight * lift_right) * smoothstep(knee_y, bottom, grid_y)
    displacement_y -= foot_lift * body_h * 0.022

    # Two restrained pelvis/body beats per stride.  Upper body and rifle move
    # together, avoiding hand/weapon separation and direction flicker.
    character_weight = np.clip(alpha * 1.12, 0.0, 1.0)
    bob = body_h * (0.0035 * math.cos(2.0 * phase) - 0.0015)
    displacement_y += character_weight * bob
    displacement_x += character_weight * body_w * 0.0025 * math.sin(2.0 * phase)

    map_x = (grid_x - displacement_x).astype(np.float32)
    map_y = (grid_y - displacement_y).astype(np.float32)
    premultiplied = rgb.astype(np.float32) * alpha[:, :, None]
    warped_pm = cv2.remap(premultiplied, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped_alpha = cv2.remap(alpha, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped_alpha = np.clip(warped_alpha, 0.0, 1.0)
    straight = np.zeros_like(warped_pm)
    np.divide(warped_pm, np.maximum(warped_alpha[:, :, None], 1.0 / 255.0), out=straight, where=warped_alpha[:, :, None] > 0)
    straight = np.clip(straight, 0.0, 255.0)
    green_composite = straight * warped_alpha[:, :, None] + GREEN[None, None, :] * (1.0 - warped_alpha[:, :, None])
    green_composite[warped_alpha < 0.01] = GREEN
    return np.round(green_composite).astype(np.uint8), np.round(warped_alpha * 255.0).astype(np.uint8)


def tile_rgba(rgb: np.ndarray, alpha: np.ndarray, size: int) -> Image.Image:
    premultiplied = np.round(rgb.astype(np.float32) * (alpha[:, :, None].astype(np.float32) / 255.0)).astype(np.uint8)
    pm_small = np.asarray(Image.fromarray(premultiplied, "RGB").resize((size, size), Image.Resampling.LANCZOS), dtype=np.float32)
    a_small = np.asarray(Image.fromarray(alpha, "L").resize((size, size), Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    straight = np.zeros_like(pm_small, dtype=np.uint8)
    np.divide(pm_small, np.maximum(a_small[:, :, None], 1.0 / 255.0), out=straight, where=a_small[:, :, None] > 0, casting="unsafe")
    straight[a_small < 0.01] = 0
    return Image.fromarray(np.dstack((straight, np.round(a_small * 255.0).astype(np.uint8))), "RGBA")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/source/move"))
    parser.add_argument("--authoring-output", type=Path, default=Path("art_src/pilot_v2/aster_v2/animation_360/move_360_interpolated_v4"))
    parser.add_argument("--runtime-output", type=Path, default=Path("assets/units/operators/aster/move_360_interpolated_v4"))
    parser.add_argument("--tile", type=int, default=384)
    args = parser.parse_args()
    source_root = project_path(args.source_root, "source root")
    authoring = project_path(args.authoring_output, "authoring output")
    runtime = project_path(args.runtime_output, "runtime output")
    if authoring.exists() or runtime.exists():
        raise SystemExit("refusing to overwrite V4; keep the immediate prior result for review")

    blender_manifest = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360/ASTER_360_POSE_DRIVER_MANIFEST.json"
    blender_driver = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360/ASTER_360_POSE_DRIVER__NONFINAL.blend"
    if not blender_manifest.is_file() or not blender_driver.is_file():
        raise SystemExit("headless Blender 360 timing/pose authority is missing")
    authoring.mkdir(parents=True)
    runtime.mkdir(parents=True)
    records: list[dict[str, object]] = []
    contact_tiles: list[Image.Image] = []

    for direction in DIRECTIONS:
        source = source_root / direction / f"ASTER_MOVE_{direction}_CONTACT_A_GREEN.png"
        if not source.is_file():
            raise SystemExit(f"direction authority missing: {source}")
        rgb = np.asarray(Image.open(source).convert("RGB"))
        alpha = source_alpha(rgb)
        source_dir = authoring / direction / "source"
        mask_dir = authoring / direction / "masks"
        runtime_dir = runtime / direction
        source_dir.mkdir(parents=True)
        mask_dir.mkdir(parents=True)
        runtime_dir.mkdir(parents=True)
        atlas = Image.new("RGBA", (args.tile, args.tile * len(KEYS)), (0, 0, 0, 0))
        frame_rows = []
        hashes = []
        mask_areas = []
        for index, key in enumerate(KEYS):
            frame_rgb, frame_alpha = warp_frame(rgb, alpha, direction, index)
            frame_path = source_dir / f"ASTER_MOVE_{direction}_{key.upper()}_GREEN.png"
            mask_path = mask_dir / f"ASTER_MOVE_{direction}_{key.upper()}_MASK.png"
            Image.fromarray(frame_rgb, "RGB").save(frame_path)
            Image.fromarray(frame_alpha, "L").save(mask_path)
            tile = tile_rgba(frame_rgb, frame_alpha, args.tile)
            atlas.alpha_composite(tile, (0, index * args.tile))
            hashes.append(sha256(frame_path))
            mask_areas.append(int(np.count_nonzero(frame_alpha > 16)))
            frame_rows.append({
                "index": index,
                "key": key,
                "source": frame_path.relative_to(ROOT).as_posix(),
                "mask": mask_path.relative_to(ROOT).as_posix(),
                "source_sha256": hashes[-1],
            })
            if index == 0:
                contact_tiles.append(tile.resize((256, 256), Image.Resampling.LANCZOS))
        if len(set(hashes)) != len(KEYS):
            raise RuntimeError(f"{direction} interpolation produced duplicate frames")
        area_delta = (max(mask_areas) - min(mask_areas)) / max(np.mean(mask_areas), 1.0)
        if area_delta > 0.12:
            raise RuntimeError(f"{direction} silhouette area drift is excessive: {area_delta:.4f}")
        atlas_path = runtime_dir / f"ASTER_MOVE_{direction}_360_INTERPOLATED_V4_ATLAS.webp"
        atlas.save(atlas_path, "WEBP", lossless=True, method=6)
        manifest = {
            "schema": 1,
            "role": f"ASTER {direction} twelve-step Blender-guided 2D locomotion interpolation atlas V4; review candidate",
            "direction_authority": source.relative_to(ROOT).as_posix(),
            "direction_authority_sha256": sha256(source),
            "blender_pose_manifest": blender_manifest.relative_to(ROOT).as_posix(),
            "blender_pose_manifest_sha256": sha256(blender_manifest),
            "blender_driver": blender_driver.relative_to(ROOT).as_posix(),
            "blender_driver_sha256": sha256(blender_driver),
            "frame_size": [args.tile, args.tile],
            "atlas_resolution": list(atlas.size),
            "frames": frame_rows,
            "unique_frame_count": len(set(hashes)),
            "silhouette_area_delta_ratio": round(float(area_delta), 6),
            "atlas": atlas_path.relative_to(ROOT).as_posix(),
            "atlas_sha256": sha256(atlas_path),
            "cloud_calls": 0,
            "krea2_calls": 0,
            "visual_gate": "USER_REVIEW_REQUIRED",
        }
        manifest_path = runtime_dir / f"ASTER_MOVE_{direction}_360_INTERPOLATED_V4_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        records.append({"direction": direction, "atlas": manifest["atlas"], "manifest": manifest_path.relative_to(ROOT).as_posix(), "unique": len(set(hashes)), "area_delta": manifest["silhouette_area_delta_ratio"]})

    sheet = Image.new("RGBA", (256 * len(contact_tiles), 296), (18, 23, 30, 255))
    draw = ImageDraw.Draw(sheet)
    for index, (direction, tile) in enumerate(zip(DIRECTIONS, contact_tiles)):
        sheet.alpha_composite(tile, (index * 256, 0))
        draw.text((index * 256 + 112, 270), direction, fill=(220, 235, 242, 255))
    preview = authoring / "ASTER_MOVE_8_DIRECTION_INTERPOLATED_V4_CONTACTS.png"
    sheet.save(preview)
    root_manifest = {
        "schema": 1,
        "role": "ASTER all eight directions unified as twelve deterministic Blender-guided interpolated frames",
        "keys": list(KEYS),
        "directions": records,
        "preview": preview.relative_to(ROOT).as_posix(),
        "preview_sha256": sha256(preview),
        "preserved_previous": [
            "assets/units/operators/aster/move_e_mvp_v4",
            "assets/units/operators/aster/move_360_interpolated_v3",
        ],
        "qwen_failed_candidates_preserved": [
            "art_src/pilot_v2/aster_v2/locomotion_masters/qwen_2511_move_v2/SE/passing_a",
        ],
        "runtime_status": "HTML_REVIEW_READY_NOT_GODOT_CONNECTED",
    }
    manifest_path = authoring / "ASTER_MOVE_360_INTERPOLATED_V4_MANIFEST.json"
    manifest_path.write_text(json.dumps(root_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_MOVE_360_INTERPOLATED_V4=" + json.dumps({"directions": len(records), "frames_per_direction": len(KEYS), "preview": root_manifest["preview"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
