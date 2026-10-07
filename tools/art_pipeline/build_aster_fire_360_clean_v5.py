#!/usr/bin/env python3
"""Build a source-preserving, full-body ASTER fire atlas with decontaminated alpha.

Fire V4 is retained as the immediately previous candidate.  V5 consumes the
reviewed ImageGen green-source/mask pairs again, removes only green-dominant
pixels that the source mask admitted, and exports the same six authored full
body poses at the runtime cell size.  No body part is reconstructed or
composited from a different character family.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/imagegen_aim_fire_mvp_v3"
OUTPUT = ROOT / "assets/units/operators/aster/fire_360_clean_v5"
PREVIEW = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire_360_clean_v5/previews/ASTER_FIRE_360_CLEAN_V5_CONTACT.png"
CELL = 384
FRAME_KEYS = ("AIM_SET", "PRELOAD", "PRELOAD_RECOIL", "RECOVER_EARLY", "RECOVER", "READY_RETURN")
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
SOURCE_KEYS = ("AIM_SET", "PRELOAD", "PRELOAD", "RECOVER", "RECOVER", "READY_RETURN")
RECOIL_PIXELS = (0.0, 0.0, 4.0, 2.0, 0.0, 0.0)
VECTORS = {
    "E": (1.0, 0.0), "SE": (0.70710678, 0.70710678), "S": (0.0, 1.0),
    "SW": (-0.70710678, 0.70710678), "W": (-1.0, 0.0),
    "NW": (-0.70710678, -0.70710678), "N": (0.0, -1.0),
    "NE": (0.70710678, -0.70710678),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_pair(direction: str, key: str) -> tuple[Path, Path]:
    stem = f"ASTER_FIRE_{direction}_{key}"
    return SOURCE_ROOT / "source" / direction / f"{stem}_GREEN.png", SOURCE_ROOT / "masks" / direction / f"{stem}_MASK.png"


def clean_pair(source: Path, mask: Path) -> tuple[Image.Image, dict[str, int]]:
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    alpha = np.asarray(Image.open(mask).convert("L"), dtype=np.uint8)
    if rgb.shape[:2] != alpha.shape:
        raise RuntimeError(f"source/mask dimensions differ: {source}")
    subject = alpha > 0
    r, g, b = (rgb[:, :, i].astype(np.int16) for i in range(3))
    # ASTER's approved palette has navy, silver, cyan and restrained gold; it
    # has no saturated green.  These are therefore admitted chroma-key fringe
    # pixels, not authored costume detail.  The mask remains the authority for
    # every non-green pixel.
    green = subject & (g > 105) & (g > r * 1.32 + 18) & (g > b * 1.32 + 18)
    cleaned_alpha = alpha.copy()
    cleaned_alpha[green] = 0
    cleaned = rgb.astype(np.float32)
    cleaned[cleaned_alpha == 0] = 0
    a = cleaned_alpha.astype(np.float32) / 255.0
    premult = np.rint(np.clip(cleaned * a[:, :, None], 0, 255)).astype(np.uint8)
    pm = np.stack([
        np.asarray(Image.fromarray(premult[:, :, i], "L").resize((CELL, CELL), Image.Resampling.LANCZOS), dtype=np.float32)
        for i in range(3)
    ], axis=2)
    small_a = np.asarray(Image.fromarray(cleaned_alpha, "L").resize((CELL, CELL), Image.Resampling.LANCZOS), dtype=np.float32)
    straight = np.zeros_like(pm)
    valid = small_a > 0.5
    straight[valid] = np.clip(pm[valid] * 255.0 / small_a[valid, None], 0, 255)
    rgba = np.dstack((np.rint(straight).astype(np.uint8), np.rint(small_a).astype(np.uint8)))
    # Guard the actual runtime pixels, not only the source mask.
    out_rgb = rgba[:, :, :3].astype(np.int16)
    out_a = rgba[:, :, 3]
    visible_green = (out_a > 16) & (out_rgb[:, :, 1] > 180) & (out_rgb[:, :, 0] < 45) & (out_rgb[:, :, 2] < 85)
    rgba[visible_green, 3] = 0
    rgba[rgba[:, :, 3] == 0, :3] = 0
    return Image.fromarray(rgba, "RGBA"), {
        "source_mask_pixels": int(subject.sum()),
        "source_green_pixels_removed": int(green.sum()),
        "runtime_visible_green_pixels": int(visible_green.sum()),
        "runtime_opaque_pixels": int((rgba[:, :, 3] > 16).sum()),
    }


def translated(frame: Image.Image, direction: str, pixels: float) -> Image.Image:
    if pixels == 0:
        return frame.copy()
    dx = int(round(-VECTORS[direction][0] * pixels))
    dy = int(round(-VECTORS[direction][1] * pixels))
    result = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    result.alpha_composite(frame, (dx, dy))
    return result


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite fire_360_clean_v5")
    OUTPUT.mkdir(parents=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview = Image.new("RGBA", (CELL * 6, CELL * len(DIRECTIONS)), (10, 18, 24, 255))
    draw = ImageDraw.Draw(preview)
    records: dict[str, object] = {}
    total_removed = 0
    for row, direction in enumerate(DIRECTIONS):
        base: dict[str, Image.Image] = {}
        source_records: dict[str, dict[str, object]] = {}
        for key in sorted(set(SOURCE_KEYS)):
            source, mask = source_pair(direction, key)
            frame, stats = clean_pair(source, mask)
            base[key] = frame
            source_records[key] = {"source": source.relative_to(ROOT).as_posix(), "mask": mask.relative_to(ROOT).as_posix(), **stats}
            total_removed += int(stats["source_green_pixels_removed"])
        frames = [translated(base[key], direction, recoil) for key, recoil in zip(SOURCE_KEYS, RECOIL_PIXELS)]
        atlas = Image.new("RGBA", (CELL, CELL * len(frames)), (0, 0, 0, 0))
        frame_records = []
        for index, frame in enumerate(frames):
            atlas.alpha_composite(frame, (0, index * CELL))
            preview.alpha_composite(frame, (index * CELL, row * CELL))
            draw.text((index * CELL + 7, row * CELL + 7), f"{direction} {FRAME_KEYS[index]}", fill=(220, 248, 240, 255), stroke_width=2, stroke_fill=(2, 9, 12, 255))
            arr = np.asarray(frame)
            green = (arr[:, :, 3] > 16) & (arr[:, :, 1] > 180) & (arr[:, :, 0] < 45) & (arr[:, :, 2] < 85)
            if int(green.sum()):
                raise RuntimeError(f"{direction} frame {index} retains visible green pixels")
            frame_records.append({"index": index, "label": FRAME_KEYS[index], "source_key": SOURCE_KEYS[index], "recoil_translation_px": RECOIL_PIXELS[index], "visible_green_pixels": 0})
        path = OUTPUT / f"ASTER_FIRE_{direction}_CLEAN_V5_RGBA.webp"
        atlas.save(path, "WEBP", lossless=True, method=6, exact=True)
        decoded = np.asarray(Image.open(path).convert("RGBA"))
        expected = np.asarray(atlas)
        if not np.array_equal(decoded, expected):
            raise RuntimeError(f"lossless round-trip changed pixels: {direction}")
        records[direction] = {"atlas": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "resolution": [CELL, CELL * len(frames)], "frames": frame_records, "source_pairs": source_records}
    preview.save(PREVIEW, "PNG", optimize=True)
    manifest = {
        "schema": 1,
        "role": "ASTER full-body fire V5, green-decontaminated ImageGen source/mask derivative",
        "directions": list(DIRECTIONS), "frame_count_per_direction": 6, "atlas_cell": CELL, "fps": 12,
        "source_family": "art_src/pilot_v2/aster_v2/animation_360/imagegen_aim_fire_mvp_v3",
        "previous_candidate": "assets/units/operators/aster/fire_360_clean_v4",
        "method": "binary approved mask consumption plus source-green fringe removal before premultiplied Lanczos resize; no body-part compositing",
        "visible_green_pixels": 0, "source_green_pixels_removed_total": total_removed,
        "runtime_status": "VISUAL_REVIEW_REQUIRED",
        "atlases": records, "preview": PREVIEW.relative_to(ROOT).as_posix(), "krea2_used": False, "cloud_runtime_inference": False,
    }
    (OUTPUT / "ASTER_FIRE_360_CLEAN_V5_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "source_green_pixels_removed_total": total_removed, "preview": PREVIEW.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
