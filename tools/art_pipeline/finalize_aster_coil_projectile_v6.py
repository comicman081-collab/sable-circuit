#!/usr/bin/env python3
"""Finalize the compact ASTER coil projectile V6 ImageGen edit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from finalize_aster_coil_projectile_v5 import ROOT, crop_and_fit, extract_green, inside_project, sha256


SOURCE_DIR = ROOT / "art_src/pilot_v2/aster_v2/vfx/coil_projectile_v6_imagegen"
DEFAULT_INPUT = SOURCE_DIR / "source/ASTER_COIL_PROJECTILE_V6_IMAGEGEN_GREEN.png"
RUNTIME = ROOT / "assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V6_RGBA.webp"
RGBA_MASTER = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V6_RGBA.png"
GREEN_CONTACT = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V6_GREEN_CONTACT.png"
MASK_PREVIEW = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V6_ALPHA.png"
MANIFEST = SOURCE_DIR / "ASTER_COIL_PROJECTILE_V6_MANIFEST.json"


def strict_despill(image: Image.Image) -> Image.Image:
    pixels = np.asarray(image.convert("RGBA")).copy()
    rgb = pixels[..., :3].astype(np.int16)
    alpha = pixels[..., 3]
    max_rb = np.maximum(rgb[..., 0], rgb[..., 2])
    spill = (alpha > 0) & (rgb[..., 1] > max_rb + 3)
    rgb[..., 1][spill] = max_rb[spill] + 3
    pixels[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    pixels[alpha <= 2] = 0
    return Image.fromarray(pixels, mode="RGBA")


def build_contact(source: Image.Image, projectile: Image.Image) -> None:
    contact_size = (1920, 1080)
    header_height = 64
    maximum_native_panel = (contact_size[0], contact_size[1] - header_height)
    if source.width > maximum_native_panel[0] or source.height > maximum_native_panel[1]:
        raise RuntimeError(
            f"source {source.size} does not fit the native 1920x1080 review panel without scaling"
        )
    contact = Image.new("RGBA", contact_size, (0, 255, 0, 255))
    contact.alpha_composite(
        source.convert("RGBA"),
        ((contact_size[0] - source.width) // 2, header_height + (maximum_native_panel[1] - source.height) // 2),
    )
    draw = ImageDraw.Draw(contact)
    draw.rectangle((0, 0, contact_size[0], header_height), fill=(3, 14, 19, 255))
    draw.text(
        (16, 18),
        f"ASTER COIL PROJECTILE V6 // SOURCE {source.width}x{source.height} 1:1 // RUNTIME {projectile.width}x{projectile.height} // NO UPSCALE",
        fill=(128, 244, 255, 255),
    )
    contact.convert("RGB").save(GREEN_CONTACT, format="PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source = inside_project(args.input, "ImageGen V6 source")
    if not source.is_file():
        raise SystemExit(f"missing ImageGen V6 source: {source}")
    outputs = (RUNTIME, RGBA_MASTER, GREEN_CONTACT, MASK_PREVIEW, MANIFEST)
    if not args.force and any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite ASTER projectile V6; pass --force for a reviewed regeneration")

    raw = Image.open(source).convert("RGB")
    extracted, matte = extract_green(raw)
    projectile, crop_box = crop_and_fit(extracted)
    projectile = strict_despill(projectile)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    projectile.save(RGBA_MASTER, format="PNG", optimize=True)
    projectile.save(RUNTIME, format="WEBP", lossless=True, quality=100, method=6)
    projectile.getchannel("A").save(MASK_PREVIEW, format="PNG", optimize=True)
    build_contact(raw, projectile)

    pixels = np.asarray(projectile)
    rgb = pixels[..., :3].astype(np.int16)
    visible = pixels[..., 3] > 6
    green_dominant = visible & (rgb[..., 1] > rgb[..., 0] + 3) & (rgb[..., 1] > rgb[..., 2] + 3)
    green_count = int(green_dominant.sum())
    if green_count != 0:
        raise RuntimeError(f"strict V6 despill failed: green_dominant_visible_pixels={green_count}")

    manifest = {
        "schema": 6,
        "status": "V6_ASSET_RETAINED; CURRENT_1080P_RUNTIME_RECAPTURE_REQUIRED; USER_VISUAL_REVIEW_NOT_RECORDED; V5_RETAINED_AS_IMMEDIATE_PREVIOUS",
        "asset_scope": "ASTER airborne projectile VFX only",
        "generation_mode": "Codex built-in image generation edit of V5",
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
            "tip_anchor_normalized": [0.862, 0.5],
            "tip_anchor_basis": "right edge of visible alpha bbox at alpha > 6",
            "recommended_world_scale": 0.102,
            "sha256": sha256(RUNTIME),
        },
        "rgba_master": RGBA_MASTER.relative_to(ROOT).as_posix(),
        "alpha_preview": MASK_PREVIEW.relative_to(ROOT).as_posix(),
        "green_contact": GREEN_CONTACT.relative_to(ROOT).as_posix(),
        "review_resolution_contract": {
            "green_contact_resolution": [1920, 1080],
            "source_panel_scale": 1.0,
            "runtime_capture_required": True,
            "minimum_runtime_capture_resolution": [1920, 1080],
            "upscale_used_as_quality_evidence": False,
        },
        "green_dominant_visible_pixels": green_count,
        "alpha_ratio_measurement_space": "full pre-crop extraction canvas",
        "final_despill": "green <= max(red, blue) + 3 for every visible pixel",
        "character_frames_baked_vfx": False,
        "runtime_layering": ["core sprite", "two opacity-stepped trailing duplicates", "restrained cyan/amber local glow"],
        "krea2_used": False,
        "local_model_used": False,
        "cloud_generation": "Codex built-in image generation explicitly requested by user",
        "external_review": {
            "reviewer": "ChatGPT web chat",
            "url": "https://chatgpt.com/c/6a939c99-57a8-83e9-8d1e-f4c35581ca1f",
            "verdict": "HISTORICAL_PILOT_PROMOTION_PASS_BEFORE_1080P_EVIDENCE_CONTRACT",
            "production_expansion": "HOLD",
            "blockers": ["Native 1920x1080 runtime recapture and renewed visual review are required."],
        },
        "review": {
            "source_visual_gate": "PASS",
            "native_runtime_readability_gate": "HOLD_1080P_RECAPTURE_REQUIRED",
            "native_8_direction_gate": "HOLD_1080P_RECAPTURE_REQUIRED",
            "technical_smoke_gate": "PASS",
            "codex_visual_qa": "PASS",
            "external_chatgpt_review": "PASS",
            "user_visual_approval": "NOT_RECORDED",
            "pilot_promotion": "HOLD_1080P_RECAPTURE_REQUIRED",
            "production_expansion": "HOLD",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_COIL_PROJECTILE_V6_FINALIZED=" + json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
