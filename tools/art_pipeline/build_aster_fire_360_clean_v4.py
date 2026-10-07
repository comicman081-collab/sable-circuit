#!/usr/bin/env python3
"""Build ASTER Fire V4 character atlases with no baked muzzle flash.

The reviewed V3 set baked the flash into source frames 2 and 3.  V4 never
copies those pixels.  It derives recoil frames from the adjacent clean poses
using a small whole-body translation, then exports the muzzle crop separately
for runtime-only display at the authoritative projectile socket.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/units/operators/aster/fire_360_mvp_v3"
OUTPUT = ROOT / "assets/units/operators/aster/fire_360_clean_v4"
VFX_SOURCE = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_imagegen_v1/ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_GREEN.png"
VFX_MASK = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_imagegen_v1/ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_MASK.png"
VFX_OUTPUT = ROOT / "assets/units/operators/aster/vfx/ASTER_MUZZLE_FLASH_E_V1_RGBA.webp"
PREVIEW = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire_360_clean_v4/previews/ASTER_FIRE_360_CLEAN_V4_CONTACT.png"

CELL = 384
FRAME_COUNT = 6
DIRECTIONS = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
DIRECTION_VECTORS = {
    "E": (1.0, 0.0),
    "SE": (0.70710678, 0.70710678),
    "S": (0.0, 1.0),
    "SW": (-0.70710678, 0.70710678),
    "W": (-1.0, 0.0),
    "NW": (-0.70710678, -0.70710678),
    "N": (0.0, -1.0),
    "NE": (0.70710678, -0.70710678),
}
FRAME_LABELS = ["aim", "preload", "recoil_contact_clean", "recover_early_clean", "recover", "ready_return"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atlas_frames(path: Path) -> list[Image.Image]:
    atlas = Image.open(path).convert("RGBA")
    if atlas.size != (CELL, CELL * FRAME_COUNT):
        raise RuntimeError(f"invalid V3 atlas dimensions: {path} {atlas.size}")
    return [atlas.crop((0, index * CELL, CELL, (index + 1) * CELL)) for index in range(FRAME_COUNT)]


def translated(frame: Image.Image, direction: tuple[float, float], recoil_pixels: float) -> Image.Image:
    dx = int(round(-direction[0] * recoil_pixels))
    dy = int(round(-direction[1] * recoil_pixels))
    result = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    result.alpha_composite(frame, (dx, dy))
    return result


def build_clean_frames(source_frames: list[Image.Image], direction: str) -> list[Image.Image]:
    # Source indices 2 and 3 are deliberately excluded: both contain baked VFX.
    vector = DIRECTION_VECTORS[direction]
    return [
        source_frames[0].copy(),
        source_frames[1].copy(),
        translated(source_frames[1], vector, 4.0),
        translated(source_frames[4], vector, 2.0),
        source_frames[4].copy(),
        source_frames[5].copy(),
    ]


def rgba_vfx() -> Image.Image:
    rgb = np.asarray(Image.open(VFX_SOURCE).convert("RGB"), dtype=np.uint8)
    alpha = np.asarray(Image.open(VFX_MASK).convert("L"), dtype=np.uint8)
    if rgb.shape[:2] != alpha.shape:
        raise RuntimeError(f"muzzle source/mask mismatch: {rgb.shape[:2]} vs {alpha.shape}")
    rgba = np.dstack((rgb, alpha))
    rgba[alpha == 0, :3] = 0
    return Image.fromarray(rgba, mode="RGBA")


def main() -> int:
    if OUTPUT.exists() or VFX_OUTPUT.exists():
        raise SystemExit("refusing to overwrite current Fire V4/VFX export")
    OUTPUT.mkdir(parents=True)
    VFX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)

    preview = Image.new("RGBA", (CELL * FRAME_COUNT, CELL * len(DIRECTIONS)), (0, 255, 0, 255))
    draw = ImageDraw.Draw(preview)
    records: dict[str, object] = {}
    for row, direction in enumerate(DIRECTIONS):
        source_path = SOURCE / f"ASTER_FIRE_{direction}_RGBA.webp"
        source_frames = atlas_frames(source_path)
        clean_frames = build_clean_frames(source_frames, direction)
        atlas = Image.new("RGBA", (CELL, CELL * FRAME_COUNT), (0, 0, 0, 0))
        frame_records = []
        for index, frame in enumerate(clean_frames):
            atlas.alpha_composite(frame, (0, index * CELL))
            preview.alpha_composite(frame, (index * CELL, row * CELL))
            draw.text((index * CELL + 7, row * CELL + 7), f"{direction} {FRAME_LABELS[index]}", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
            frame_records.append({
                "index": index,
                "label": FRAME_LABELS[index],
                "baked_muzzle_vfx": False,
                "source_v3_index": [0, 1, 1, 4, 4, 5][index],
                "recoil_translation_px": [0, 0, 4, 2, 0, 0][index],
            })
        output_path = OUTPUT / f"ASTER_FIRE_{direction}_CLEAN_RGBA.webp"
        atlas.save(output_path, format="WEBP", lossless=True, quality=100, method=6)
        records[direction] = {
            "source": source_path.relative_to(ROOT).as_posix(),
            "output": output_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(output_path),
            "resolution": list(atlas.size),
            "frames": frame_records,
        }

    vfx = rgba_vfx()
    vfx.save(VFX_OUTPUT, format="WEBP", lossless=True, quality=100, method=6)
    preview.convert("RGB").save(PREVIEW, format="PNG", optimize=True)
    manifest = {
        "schema": 1,
        "role": "ASTER Fire V4 character-only atlases plus separate runtime muzzle VFX",
        "directions": DIRECTIONS,
        "frame_count_per_direction": FRAME_COUNT,
        "atlas_cell": CELL,
        "fps": 12,
        "baked_muzzle_vfx": False,
        "excluded_v3_source_indices": [2, 3],
        "runtime_muzzle_frame": 2,
        "runtime_muzzle_vfx": {
            "source": VFX_SOURCE.relative_to(ROOT).as_posix(),
            "mask": VFX_MASK.relative_to(ROOT).as_posix(),
            "output": VFX_OUTPUT.relative_to(ROOT).as_posix(),
            "sha256": sha256(VFX_OUTPUT),
            "resolution": list(vfx.size),
            "anchor_xy": [38, 60],
        },
        "atlases": records,
        "preview": PREVIEW.relative_to(ROOT).as_posix(),
        "krea2_used": False,
        "cloud_runtime_inference": False,
    }
    manifest_path = OUTPUT / "ASTER_FIRE_360_CLEAN_V4_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_FIRE_360_CLEAN_V4_PASS=" + json.dumps({
        "atlases": len(records),
        "baked_muzzle_vfx": False,
        "runtime_vfx": VFX_OUTPUT.relative_to(ROOT).as_posix(),
        "preview": PREVIEW.relative_to(ROOT).as_posix(),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
