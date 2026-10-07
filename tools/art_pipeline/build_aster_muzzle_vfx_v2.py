#!/usr/bin/env python3
"""Build the clean ASTER runtime muzzle flash V2 from the green-screen source.

V1 copied the authored mask directly, which retained green-screen colour in
semi-transparent pixels.  V2 reconstructs foreground colour and alpha from a
known pure-green backing, intersects it with the authored mask, and records QA
metrics so the browser preview and Godot runtime can consume identical bytes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_imagegen_v1/ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_GREEN.png"
MASK = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_imagegen_v1/ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_MASK.png"
OUTPUT = ROOT / "assets/units/operators/aster/vfx/ASTER_MUZZLE_FLASH_E_V2_RGBA.webp"
QA_DIR = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_v2"
QA_PREVIEW = QA_DIR / "ASTER_MUZZLE_FLASH_E_V2_RGBA.png"
QA_MANIFEST = QA_DIR / "ASTER_MUZZLE_FLASH_E_V2_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct_rgba() -> Image.Image:
    observed = np.asarray(Image.open(SOURCE).convert("RGB"), dtype=np.float32) / 255.0
    authored_mask = np.asarray(Image.open(MASK).convert("L"), dtype=np.float32) / 255.0
    if observed.shape[:2] != authored_mask.shape:
        raise RuntimeError(f"source/mask mismatch: {observed.shape[:2]} vs {authored_mask.shape}")

    red = observed[..., 0]
    green = observed[..., 1]
    blue = observed[..., 2]

    # For an image composited over B=(0, 1, 0), each channel provides a lower
    # bound for foreground opacity.  Their maximum is a stable chroma-key alpha
    # for warm white/orange muzzle light without treating green spill as colour.
    chroma_alpha = np.maximum.reduce((red, blue, 1.0 - green))
    chroma_alpha = np.clip((chroma_alpha - 0.018) / 0.982, 0.0, 1.0)
    alpha = chroma_alpha * authored_mask

    safe_alpha = np.maximum(chroma_alpha, 1.0 / 255.0)
    foreground = np.empty_like(observed)
    foreground[..., 0] = red / safe_alpha
    foreground[..., 1] = (green - (1.0 - chroma_alpha)) / safe_alpha
    foreground[..., 2] = blue / safe_alpha
    foreground = np.clip(foreground, 0.0, 1.0)

    # Remove the last antialiasing fringe and guarantee that fully transparent
    # pixels carry no hidden chroma that can bleed through linear filtering.
    alpha[alpha < (2.0 / 255.0)] = 0.0
    foreground[alpha == 0.0] = 0.0

    rgba = np.dstack((foreground, alpha))
    return Image.fromarray(np.rint(rgba * 255.0).astype(np.uint8), mode="RGBA")


def main() -> int:
    if OUTPUT.exists() or QA_DIR.exists():
        raise SystemExit("refusing to overwrite current muzzle VFX V2 export")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True)

    result = reconstruct_rgba()
    result.save(OUTPUT, format="WEBP", lossless=True, quality=100, method=6)
    result.save(QA_PREVIEW, format="PNG", optimize=True)

    pixels = np.asarray(result, dtype=np.uint8)
    colour = pixels[..., :3].astype(np.int16)
    visible = pixels[..., 3] > 0
    green_dominant = visible & (colour[..., 1] > colour[..., 0] + 24) & (colour[..., 1] > colour[..., 2] + 24)
    manifest = {
        "schema": 1,
        "role": "ASTER runtime-only muzzle flash; green-screen decontaminated V2",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "authored_mask": MASK.relative_to(ROOT).as_posix(),
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT),
        "resolution": list(result.size),
        "anchor_xy": [38, 60],
        "visible_pixels": int(visible.sum()),
        "green_dominant_visible_pixels": int(green_dominant.sum()),
        "transparent_pixels_with_nonzero_rgb": int(((pixels[..., 3] == 0) & np.any(pixels[..., :3] != 0, axis=2)).sum()),
        "baked_into_character_frames": False,
        "krea2_used": False,
        "cloud_runtime_inference": False,
    }
    QA_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_MUZZLE_FLASH_V2_PASS=" + json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
