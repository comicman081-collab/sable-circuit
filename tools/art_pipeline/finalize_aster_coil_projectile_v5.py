#!/usr/bin/env python3
"""Finalize the reviewed ImageGen ASTER coil projectile into runtime art.

The generated source remains immutable.  This script estimates the controlled
green screen from its border, removes it with a soft dominance matte, despills
green without erasing ASTER's cyan magnetic sheath, and emits one compact
lossless WebP plus green-screen QA evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "art_src/pilot_v2/aster_v2/vfx/coil_projectile_v5_imagegen"
DEFAULT_INPUT = SOURCE_DIR / "source/ASTER_COIL_PROJECTILE_V5_IMAGEGEN_GREEN.png"
RUNTIME = ROOT / "assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V5_RGBA.webp"
RGBA_MASTER = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V5_RGBA.png"
GREEN_CONTACT = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V5_GREEN_CONTACT.png"
MASK_PREVIEW = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V5_ALPHA.png"
MANIFEST = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V5_MANIFEST.json"

OUTPUT_WIDTH = 768
OUTPUT_HEIGHT = 192
PADDING = 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inside_project(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside SABLE project: {resolved}") from exc
    return resolved


def extract_green(rgb_image: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    rgb = np.asarray(rgb_image.convert("RGB"), dtype=np.float32)
    height, width, _ = rgb.shape
    border = max(8, min(width, height) // 32)
    edge = np.concatenate(
        (
            rgb[:border].reshape(-1, 3),
            rgb[-border:].reshape(-1, 3),
            rgb[:, :border].reshape(-1, 3),
            rgb[:, -border:].reshape(-1, 3),
        ),
        axis=0,
    )
    edge_median = np.median(edge, axis=0)
    edge_dominance = float(edge_median[1] - max(edge_median[0], edge_median[2]))
    if edge_dominance < 120:
        raise RuntimeError(f"source border is not a controlled green screen: {edge_median.tolist()}")

    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    max_rb = np.maximum(red, blue)
    dominance = green - max_rb
    # ImageGen may shift the requested #00FF00 field between revisions.  Anchor
    # the dominance ramp to the measured border and intersect it with a green
    # channel ratio key.  True cyan energy survives because blue approaches
    # green; amber survives because red exceeds green.  Green backdrop noise
    # remains transparent even when its absolute luminance varies.
    dominance_cutoff = edge_dominance - 35.0
    dominance_full = max(35.0, dominance_cutoff - 93.0)
    alpha_dominance = np.clip(
        (dominance_cutoff - dominance) / max(1.0, dominance_cutoff - dominance_full),
        0.0,
        1.0,
    )
    green_ratio = green / (max_rb + 1.0)
    alpha_ratio = np.clip((2.65 - green_ratio) / 1.40, 0.0, 1.0)
    alpha = np.minimum(alpha_dominance, alpha_ratio)
    alpha = np.asarray(
        Image.fromarray(np.rint(alpha * 255.0).astype(np.uint8), mode="L").filter(
            ImageFilter.GaussianBlur(0.55)
        ),
        dtype=np.uint8,
    )

    colour = rgb.copy()
    # Remove chroma spill only where green exceeds both other channels.  Cyan
    # remains cyan because blue is allowed to stay close to green.
    ceiling = np.maximum(colour[..., 0], colour[..., 2]) * 1.035 + 3.0
    spill = colour[..., 1] > ceiling
    colour[..., 1][spill] = ceiling[spill]
    rgba = np.dstack((np.clip(colour, 0, 255).astype(np.uint8), alpha))
    rgba[alpha == 0, :3] = 0
    return Image.fromarray(rgba, mode="RGBA"), {
        "edge_median_rgb": [round(float(value), 3) for value in edge_median],
        "edge_green_dominance": round(edge_dominance, 3),
        "alpha_visible_ratio": round(float((alpha > 6).mean()), 6),
        "alpha_opaque_ratio": round(float((alpha > 245).mean()), 6),
        "matte_ramp_green_dominance": [round(dominance_cutoff, 3), round(dominance_full, 3)],
        "matte_green_ratio_ramp": [2.65, 1.25],
        "despill": "green <= max(red, blue) * 1.035 + 3",
    }


def crop_and_fit(image: Image.Image) -> tuple[Image.Image, list[int]]:
    alpha = np.asarray(image.getchannel("A"))
    # Generated green fields contain tiny low-alpha compression/colour noise at
    # the frame edge.  A 52/255 structural threshold isolates the actual energy
    # wake; generous padding below still retains the softer authored bloom.
    ys, xs = np.where(alpha > 52)
    if xs.size == 0:
        raise RuntimeError("no projectile foreground survived chroma extraction")
    left = max(0, int(xs.min()) - 34)
    top = max(0, int(ys.min()) - 34)
    right = min(image.width, int(xs.max()) + 35)
    bottom = min(image.height, int(ys.max()) + 35)
    cropped = image.crop((left, top, right, bottom))
    available = (OUTPUT_WIDTH - PADDING * 2, OUTPUT_HEIGHT - PADDING * 2)
    scale = min(available[0] / cropped.width, available[1] / cropped.height)
    fitted = cropped.resize(
        (max(1, round(cropped.width * scale)), max(1, round(cropped.height * scale))),
        Image.Resampling.LANCZOS,
    )
    output = Image.new("RGBA", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (0, 0, 0, 0))
    output.alpha_composite(
        fitted,
        ((OUTPUT_WIDTH - fitted.width) // 2, (OUTPUT_HEIGHT - fitted.height) // 2),
    )
    clean = np.asarray(output).copy()
    clean[clean[..., 3] == 0, :3] = 0
    return Image.fromarray(clean, mode="RGBA"), [left, top, right, bottom]


def build_contact(projectile: Image.Image) -> None:
    contact = Image.new("RGBA", (1280, 420), (0, 255, 0, 255))
    preview = projectile.copy()
    preview.thumbnail((1160, 300), Image.Resampling.LANCZOS)
    contact.alpha_composite(preview, ((1280 - preview.width) // 2, 68))
    draw = ImageDraw.Draw(contact)
    draw.rectangle((0, 0, 1280, 36), fill=(3, 14, 19, 255))
    draw.text(
        (12, 11),
        "ASTER COIL PROJECTILE V5 // BUILT-IN IMAGEGEN // GREEN SEPARATION QA",
        fill=(128, 244, 255, 255),
    )
    contact.convert("RGB").save(GREEN_CONTACT, format="PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source = inside_project(args.input, "ImageGen source")
    if not source.is_file():
        raise SystemExit(f"missing ImageGen source: {source}")
    outputs = (RUNTIME, RGBA_MASTER, GREEN_CONTACT, MASK_PREVIEW, MANIFEST)
    if not args.force and any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite ASTER projectile V5; pass --force for a reviewed regeneration")

    raw = Image.open(source).convert("RGB")
    extracted, matte = extract_green(raw)
    projectile, crop_box = crop_and_fit(extracted)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    projectile.save(RGBA_MASTER, format="PNG", optimize=True)
    projectile.save(RUNTIME, format="WEBP", lossless=True, quality=100, method=6)
    projectile.getchannel("A").save(MASK_PREVIEW, format="PNG", optimize=True)
    build_contact(projectile)

    pixels = np.asarray(projectile)
    rgb16 = pixels[..., :3].astype(np.int16)
    visible = pixels[..., 3] > 6
    green_dominant_visible = visible & (rgb16[..., 1] > rgb16[..., 0] + 14) & (
        rgb16[..., 1] > rgb16[..., 2] + 14
    )
    manifest = {
        "schema": 5,
        "status": "V5_VISUAL_FAIL_RETAINED_AS_IMMEDIATE_PREVIOUS; V6_IS_CURRENT_PILOT",
        "promotion": "NOT_PROMOTED",
        "asset_scope": "ASTER airborne projectile VFX only",
        "generation_mode": "Codex built-in image generation",
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source),
        "source_resolution": list(raw.size),
        "crop_box_ltrb": crop_box,
        "matte": matte,
        "runtime": {
            "file": RUNTIME.relative_to(ROOT).as_posix(),
            "resolution": list(projectile.size),
            "format": "lossless WebP RGBA",
            "travel_axis": "left_to_right",
            "tip_anchor_normalized": [0.965, 0.5],
            "sha256": sha256(RUNTIME),
        },
        "rgba_master": RGBA_MASTER.relative_to(ROOT).as_posix(),
        "alpha_preview": MASK_PREVIEW.relative_to(ROOT).as_posix(),
        "green_contact": GREEN_CONTACT.relative_to(ROOT).as_posix(),
        "green_dominant_visible_pixels": int(green_dominant_visible.sum()),
        "character_frames_baked_vfx": False,
        "krea2_used": False,
        "local_model_used": False,
        "cloud_generation": "Codex built-in image generation explicitly requested by user",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_COIL_PROJECTILE_V5_FINALIZED=" + json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
