#!/usr/bin/env python3
"""Build 1080p QA contact sheets; source and runtime art remain untouched."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SIZE = (1920, 1080)
SOURCES = {
    "relay_sentinel": (
        "motion_lab_v1/art/site7_enemies_raw/relay_sentinel_master.png",
        "assets/enemies/stage2_relay_sentinel/authored_core_v1/RELAY_SENTINEL.png",
    ),
    "resonance_remnant": (
        "motion_lab_v1/art/site7_enemies_raw/resonance_remnant_master.png",
        "assets/enemies/stage3_resonance_remnant/authored_core_v1/RESONANCE_REMNANT.png",
    ),
}
LINEUP = [
    ("ANCHOR", "assets/enemies/signal_anchor_guardian/authored_core_v1/anchor.png"),
    ("RELAY", SOURCES["relay_sentinel"][1]),
    ("REMNANT", SOURCES["resonance_remnant"][1]),
    ("FORGE", "assets/enemies/stage4_forge_warden/authored_core_v1/FORGE_WARDEN.png"),
    ("CARRIER", "assets/enemies/stage5_carrier_null/authored_core_v1/CARRIER_NULL.png"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paste_native_crop(canvas: Image.Image, art: Image.Image, box: tuple[int, int, int, int], xy: tuple[int, int]) -> None:
    crop = art.crop(box)
    canvas.alpha_composite(crop, xy)


def source_sheet(art: Image.Image, light: bool) -> Image.Image:
    background = (222, 225, 225, 255) if light else (16, 20, 27, 255)
    canvas = Image.new("RGBA", SIZE, background)
    # Full source at fit scale on the left; two 1:1 native-pixel crops on the right.
    scale = min(900 / art.width, 950 / art.height)
    whole = art.resize((round(art.width * scale), round(art.height * scale)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(whole, (470 - whole.width // 2, 540 - whole.height // 2))
    crop_width, crop_height = 450, 900
    center_y = max(0, (art.height - crop_height) // 2)
    paste_native_crop(canvas, art, (0, center_y, crop_width, center_y + crop_height), (970, 90))
    right_x = art.width - crop_width
    paste_native_crop(canvas, art, (right_x, center_y, art.width, center_y + crop_height), (1440, 90))
    return canvas.convert("RGB")


def lineup_sheet() -> Image.Image:
    canvas = Image.new("RGBA", SIZE, (27, 35, 44, 255))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=26)
    for index, (name, relative) in enumerate(LINEUP):
        path = ROOT / relative
        with Image.open(path) as loaded:
            art = loaded.convert("RGBA")
        bbox = art.getchannel("A").point(lambda alpha: 255 if alpha > 10 else 0).getbbox()
        if bbox is None:
            raise ValueError(f"empty silhouette: {path}")
        art = art.crop(bbox)
        scale = 235 / art.height
        art = art.resize((round(art.width * scale), 235), Image.Resampling.LANCZOS)
        center_x = 220 + index * 370
        canvas.alpha_composite(art, (center_x - art.width // 2, 500))
        draw.text((center_x, 755), name, font=font, fill=(226, 235, 244), anchor="mt")
    return canvas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Project-local output directory")
    args = parser.parse_args()
    out = (ROOT / args.out).resolve()
    out.relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (source_relative, runtime_relative) in SOURCES.items():
        source, runtime = ROOT / source_relative, ROOT / runtime_relative
        digest = sha256(source)
        if sha256(runtime) != digest:
            raise ValueError(f"runtime differs from source: {name}")
        with Image.open(source) as loaded:
            art = loaded.convert("RGBA")
        for light in (True, False):
            path = out / f"{name}_{'light' if light else 'dark'}_native_crops.png"
            source_sheet(art, light).save(path)
            rows.append({"name": name, "sheet": path.relative_to(ROOT).as_posix(), "source": source_relative,
                         "runtime": runtime_relative, "source_sha256": digest, "source_size": art.size,
                         "native_pixel_crops": True, "full_view_scaled_for_review_only": True,
                         "runtime_unchanged": True})
    lineup = out / "five_bosses_equal_height.png"
    lineup_sheet().save(lineup)
    (out / "review_manifest.json").write_text(json.dumps({"resolution": SIZE, "sheets": rows,
        "lineup": lineup.relative_to(ROOT).as_posix(), "lineup_silhouette_height_px": 235},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SITE7_BOSS_REVIEW: PASS {out}")


if __name__ == "__main__":
    main()
