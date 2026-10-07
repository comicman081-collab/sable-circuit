#!/usr/bin/env python3
"""Build ASTER's velocity-driven waist/torso bridge atlases.

The bridge is a narrow, soft, direction-specific band derived from the approved
V6 full-body locomotion frames.  It follows the 24-frame lower gait and covers
the join after an independently aimed upper sprite is translated onto the
active lower waist socket.  It is presentation-only and never changes motion,
aim, collision, speed, damage, identity, or costume authority.
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
FRAME_COUNT = 24
FPS = 24
ASSET_ROOT = ROOT / "assets" / "units" / "operators" / "aster"
COMPOSITE_MANIFEST = ASSET_ROOT / "composite_fire_v6" / "ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
OUTPUT_ROOT = ASSET_ROOT / "torso_bridge_v1"
AUTHOR_ROOT = ROOT / "art_src" / "pilot_v2" / "aster_v2" / "animation_360" / "torso_bridge_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    t = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def read_atlas(path: Path) -> np.ndarray:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if rgba.shape != (CELL * FRAME_COUNT, CELL, 4):
        raise RuntimeError(f"invalid 24-frame atlas: {path} {rgba.shape}")
    return rgba.reshape(FRAME_COUNT, CELL, CELL, 4)


def direction_geometry(frames: np.ndarray) -> dict[str, float]:
    union = np.max(frames[:, :, :, 3], axis=0) > 16
    ys, xs = np.nonzero(union)
    if not len(xs):
        raise RuntimeError("empty move authority")
    top, bottom = float(ys.min()), float(ys.max())
    height = bottom - top + 1.0
    band = (ys >= top + height * 0.46) & (ys <= top + height * 0.60)
    return {
        "pelvis_x": float(np.median(xs[band])) if np.any(band) else float(np.median(xs)),
        "split_y": top + height * 0.52,
    }


def distance_to_segment(
    x: np.ndarray, y: np.ndarray, start: np.ndarray, end: np.ndarray
) -> np.ndarray:
    segment = end - start
    denominator = max(float(np.dot(segment, segment)), 1e-6)
    t = np.clip(((x - start[0]) * segment[0] + (y - start[1]) * segment[1]) / denominator, 0.0, 1.0)
    cx = start[0] + t * segment[0]
    cy = start[1] + t * segment[1]
    return np.hypot(x - cx, y - cy)


def build_bridge(
    frame: np.ndarray,
    pelvis_x: float,
    split_y: float,
    barrel_inner: list[float],
    muzzle: list[float],
) -> np.ndarray:
    y, x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    vertical_in = smoothstep(split_y - 19.0, split_y - 9.0, y)
    vertical_out = 1.0 - smoothstep(split_y + 10.0, split_y + 19.0, y)
    horizontal = 1.0 - smoothstep(45.0, 62.0, np.abs(x - pelvis_x))
    weight = np.clip(vertical_in * vertical_out * horizontal, 0.0, 1.0)

    # Rifle pixels are owned by the independently aimed upper and must never be
    # duplicated by the lower-direction bridge.
    weapon_distance = distance_to_segment(
        x,
        y,
        np.asarray(barrel_inner, dtype=np.float32),
        np.asarray(muzzle, dtype=np.float32),
    )
    weight *= smoothstep(11.0, 17.0, weapon_distance)

    # Keep only alpha connected to the central pelvis seed.  This removes stray
    # ponytail/rifle fragments that happen to cross the narrow band.
    candidate = ((frame[:, :, 3] > 10) & (weight > 0.015)).astype(np.uint8)
    count, labels = cv2.connectedComponents(candidate, connectivity=8)
    seed_y0 = max(0, int(round(split_y)) - 5)
    seed_y1 = min(CELL, int(round(split_y)) + 11)
    seed_x0 = max(0, int(round(pelvis_x)) - 16)
    seed_x1 = min(CELL, int(round(pelvis_x)) + 17)
    seed_labels = set(
        int(value)
        for value in np.unique(labels[seed_y0:seed_y1, seed_x0:seed_x1])
        if value != 0
    )
    connected = np.zeros((CELL, CELL), dtype=np.float32)
    for label in seed_labels:
        connected[labels == label] = 1.0
    if count <= 1 or not seed_labels:
        connected = candidate.astype(np.float32)
    connected = cv2.GaussianBlur(connected, (0, 0), 0.8)
    weight *= np.clip(connected, 0.0, 1.0)

    result = frame.copy()
    result[:, :, 3] = np.rint(frame[:, :, 3].astype(np.float32) * weight).astype(np.uint8)
    result[result[:, :, 3] == 0, :3] = 0
    return result


def save_lossless_atlas(frames: list[np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atlas = np.concatenate(frames, axis=0)
    Image.fromarray(atlas, "RGBA").save(
        path, format="WEBP", lossless=True, method=6, exact=True
    )
    roundtrip = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if not np.array_equal(roundtrip, atlas):
        raise RuntimeError(f"lossless roundtrip failed: {path}")


def main() -> int:
    manifest = json.loads(COMPOSITE_MANIFEST.read_text(encoding="utf-8"))
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    AUTHOR_ROOT.mkdir(parents=True, exist_ok=True)
    records: dict[str, object] = {}
    preview = Image.new("RGBA", (CELL * 6, CELL * len(DIRECTIONS)), (8, 15, 20, 255))
    draw = ImageDraw.Draw(preview)
    phases = (0, 4, 8, 12, 16, 20)

    for row, direction in enumerate(DIRECTIONS):
        direction_record = manifest["directions_output"][direction]
        source_path = ROOT / direction_record["layers"]["move_lower"]["source"]
        source = read_atlas(source_path)
        geometry = direction_geometry(source)
        corridor = manifest["weapon_corridors_384_cell"][direction]
        frames = [
            build_bridge(
                frame,
                geometry["pelvis_x"],
                geometry["split_y"],
                corridor["barrel_inner_xy"],
                corridor["muzzle_xy"],
            )
            for frame in source
        ]
        if any(int(np.count_nonzero(frame[:, :, 3])) < 80 for frame in frames):
            raise RuntimeError(f"bridge became empty: {direction}")
        out_path = OUTPUT_ROOT / direction / f"ASTER_TORSO_BRIDGE_{direction}_V1_ATLAS.webp"
        save_lossless_atlas(frames, out_path)
        records[direction] = {
            "source": source_path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(source_path),
            "output": out_path.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(out_path),
            "pelvis_socket_source_px": [
                round(float(geometry["pelvis_x"]), 4),
                round(float(geometry["split_y"]), 4),
            ],
            "visible_pixels_min": min(int(np.count_nonzero(frame[:, :, 3])) for frame in frames),
            "visible_pixels_max": max(int(np.count_nonzero(frame[:, :, 3])) for frame in frames),
        }
        for column, phase in enumerate(phases):
            x = column * CELL
            y = row * CELL
            preview.alpha_composite(Image.fromarray(frames[phase], "RGBA"), (x, y))
            draw.rectangle((x, y, x + 120, y + 20), fill=(3, 9, 13, 240))
            draw.text((x + 5, y + 4), f"{direction} BRIDGE F{phase:02d}", fill=(102, 238, 232, 255))

    preview_path = AUTHOR_ROOT / "ASTER_TORSO_BRIDGE_V1_CONTACT.png"
    preview.save(preview_path, optimize=True)
    output = {
        "schema": 1,
        "role": "velocity-direction 24-frame waist bridge for independent ASTER upper aim",
        "costumeId": "ASTER_COMBAT_SUIT_C01",
        "identity_changed": False,
        "directions": list(DIRECTIONS),
        "frame_count": FRAME_COUNT,
        "fps": FPS,
        "cell": [CELL, CELL],
        "atlas": [CELL, CELL * FRAME_COUNT],
        "source_manifest": COMPOSITE_MANIFEST.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": sha256(COMPOSITE_MANIFEST),
        "records": records,
        "contact": preview_path.relative_to(ROOT).as_posix(),
        "contact_sha256": sha256(preview_path),
        "baked_muzzle_vfx": False,
        "runtime_authority": "presentation only",
        "visual_gate": "USER_REVIEW_REQUIRED",
        "production_expansion": "HOLD",
    }
    runtime_manifest = OUTPUT_ROOT / "ASTER_TORSO_BRIDGE_V1_MANIFEST.json"
    author_manifest = AUTHOR_ROOT / "ASTER_TORSO_BRIDGE_V1_MANIFEST.json"
    payload = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    runtime_manifest.write_text(payload, encoding="utf-8")
    author_manifest.write_text(payload, encoding="utf-8")
    print(f"ASTER_TORSO_BRIDGE_V1: BUILT contact={preview_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
