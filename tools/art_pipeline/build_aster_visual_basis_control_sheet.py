#!/usr/bin/env python3
"""Build a fixed ASTER identity control sheet from the user-approved basis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
BASIS_LOCK = ROOT / "art_src/pilot_v2/aster_v2/visual_basis/ASTER_QWEN_V3_USER_VISUAL_BASIS_LOCK.json"
OUT_IMAGE = ROOT / "art_src/pilot_v2/aster_v2/visual_basis/ASTER_VISUAL_BASIS_IDENTITY_CONTROL_SHEET.png"
OUT_JSON = ROOT / "art_src/pilot_v2/aster_v2/visual_basis/ASTER_VISUAL_BASIS_IDENTITY_CONTROL_SHEET.json"
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
PALETTE = [
    ("SILVER HAIR", "#B8C9D4"),
    ("NAVY CLOTH", "#26324C"),
    ("WHITE ARMOR", "#DDE4E8"),
    ("CYAN ACCENT", "#43E6FF"),
    ("GOLD HARDWARE", "#CDA15B"),
    ("DARK RIFLE", "#28383D"),
    ("SKIN", "#E7B3A6"),
]
CROPS = [
    ("FACE / JAW / EYES", (407, 152, 657, 358)),
    ("HAIR MASS / PONYTAIL", (392, 30, 737, 430)),
    ("TORSO / JACKET ASYMMETRY", (305, 250, 691, 609)),
    ("RIFLE / TWO-HAND GRIP", (183, 286, 863, 657)),
    ("FULL BODY / SILHOUETTE", (154, 24, 867, 986)),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        ROOT / "assets/fonts/Rajdhani-Medium.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def subject_rgba(source: Path, mask: Path) -> Image.Image:
    rgb = np.asarray(Image.open(source).convert("RGB"))
    alpha = np.asarray(Image.open(mask).convert("L"))
    if rgb.shape[:2] != (1024, 1024) or alpha.shape != (1024, 1024):
        raise RuntimeError("visual basis must retain its locked 1024x1024 source/mask")
    if not np.array_equal(np.unique(alpha), np.asarray([0, 255], dtype=np.uint8)):
        raise RuntimeError("visual basis mask must be binary")
    exterior = alpha == 0
    if not np.all(rgb[exterior] == GREEN):
        raise RuntimeError("visual basis source exterior is no longer exact #00FF00")
    return Image.fromarray(np.dstack((rgb, alpha)), mode="RGBA")


def paste_crop(sheet: Image.Image, image: Image.Image, title: str, crop: tuple[int, int, int, int], box: tuple[int, int, int, int], title_font) -> None:
    draw = ImageDraw.Draw(sheet)
    x, y, width, height = box
    draw.rounded_rectangle((x, y, x + width, y + height), radius=16, fill="#13202A", outline="#426074", width=2)
    draw.text((x + 20, y + 16), title, font=title_font, fill="#87E9FF")
    tile = image.crop(crop)
    tile.thumbnail((width - 32, height - 68), Image.Resampling.LANCZOS)
    panel = Image.new("RGBA", (width - 32, height - 68), (7, 15, 21, 255))
    panel.alpha_composite(tile, ((panel.width - tile.width) // 2, (panel.height - tile.height) // 2))
    sheet.alpha_composite(panel, (x + 16, y + 48))


def main() -> int:
    lock = json.loads(BASIS_LOCK.read_text(encoding="utf-8"))
    if lock.get("approval", {}).get("decision") != "USE_AS_VISUAL_BASIS":
        raise RuntimeError("ASTER visual basis has no user-approved basis decision")
    source = ROOT / lock["source"]["green_image"]
    mask = ROOT / lock["source"]["binary_mask"]
    if sha256(source) != lock["source"]["green_image_sha256"] or sha256(mask) != lock["source"]["binary_mask_sha256"]:
        raise RuntimeError("ASTER visual basis hash changed; refusing identity control sheet")
    basis = subject_rgba(source, mask)
    sheet = Image.new("RGBA", (2048, 2048), (5, 11, 16, 255))
    draw = ImageDraw.Draw(sheet)
    title_font, label_font, note_font = font(42), font(24), font(20)
    draw.text((60, 46), "ASTER // USER-APPROVED VISUAL BASIS", font=title_font, fill="#9BF2FF")
    draw.text((60, 104), "IDENTITY CONTROL SHEET — QUALITY UP, DESIGN LOCKED — NOT A RUNTIME ASSET", font=label_font, fill="#F2C978")

    positions = [(60, 180, 610, 490), (710, 180, 610, 490), (1360, 180, 628, 490), (60, 710, 1248, 560), (1348, 710, 640, 1120)]
    for (title, crop), box in zip(CROPS, positions):
        paste_crop(sheet, basis, title, crop, box, label_font)

    draw.rounded_rectangle((60, 1310, 1308, 1930), radius=16, fill="#13202A", outline="#426074", width=2)
    draw.text((84, 1332), "LOCKED IDENTITY / ASYMMETRY", font=label_font, fill="#87E9FF")
    notes = [
        "1. Mature stylized adult: do not enlarge head or shorten legs.",
        "2. Silver split-comet ponytail remains a large readable rear mass.",
        "3. Navy jacket stays asymmetric; right white shoulder plate is prominent.",
        "4. White/cyan/gold placement rotates with body; never becomes symmetric.",
        "5. One narrow coil rifle: right primary grip + left forward support grip.",
        "6. Improve anatomy, face planes, hands, boots, materials, and edge quality only.",
        "7. Reject any redraw that changes hair, costume, rifle family, body type, age, or tactical role.",
    ]
    for index, line in enumerate(notes):
        draw.text((94, 1390 + index * 66), line, font=note_font, fill="#D6E5EA")

    draw.rounded_rectangle((60, 1960, 1928, 2026), radius=12, fill="#0C161E", outline="#426074", width=2)
    palette_x = 88
    for label, color in PALETTE:
        draw.rounded_rectangle((palette_x, 1975, palette_x + 42, 2013), radius=6, fill=color, outline="#D5E9F1", width=1)
        draw.text((palette_x + 56, 1981), label, font=note_font, fill="#D6E5EA")
        palette_x += 260

    OUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(OUT_IMAGE)
    report = {
        "schema": 1,
        "role": "fixed identity control sheet for 2048 manual master and later independent 8-sector redraws",
        "basis_lock": BASIS_LOCK.relative_to(ROOT).as_posix(),
        "basis_source_sha256": sha256(source),
        "basis_mask_sha256": sha256(mask),
        "output": OUT_IMAGE.relative_to(ROOT).as_posix(),
        "output_sha256": sha256(OUT_IMAGE),
        "resolution": [2048, 2048],
        "crops": [{"label": label, "source_rect": list(crop)} for label, crop in CROPS],
        "palette": [{"label": label, "hex": color} for label, color in PALETTE],
        "runtime_asset": False,
        "animation_frame": False,
        "transparent_background": False,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("ASTER_VISUAL_BASIS_CONTROL_SHEET=" + json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
