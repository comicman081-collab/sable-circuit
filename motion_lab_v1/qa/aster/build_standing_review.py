"""Build a native-1080p review sheet from the approved ASTER standing sources.

This is display-only QA: source PNGs are read without modification and their
green backdrop is keyed into a dark review panel. No runtime asset is produced.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "qa" / "aster" / "standing" / "ASTER_STANDING_V1_REVIEW_1080P.png"
MANIFEST = ROOT / "qa" / "aster" / "standing" / "ASTER_STANDING_V1_REVIEW_1080P.json"
ORDER = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def key_green(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    edge = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]), axis=0).astype(np.int16)
    median = np.median(edge, axis=0)
    values = rgb.astype(np.int16)
    bg = (
        (np.max(np.abs(values - median.astype(np.int16)), axis=2) <= 24)
        & (values[:, :, 1] >= values[:, :, 0] + 35)
        & (values[:, :, 1] >= values[:, :, 2] + 35)
    )
    rgba = np.dstack((rgb, np.where(bg, 0, 255).astype(np.uint8)))
    return Image.fromarray(rgba, "RGBA")


def main() -> None:
    font_path = ROOT.parent / "assets" / "fonts" / "Rajdhani-Medium.ttf"
    title_font = ImageFont.truetype(str(font_path), 34)
    label_font = ImageFont.truetype(str(font_path), 26)
    small_font = ImageFont.truetype(str(font_path), 18)
    sheet = Image.new("RGB", (1920, 1080), "#0b171e")
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 18), "SABLE CIRCUIT  /  ASTER  /  REALISTIC STANDING STYLE RESET", font=title_font, fill="#b5e8d8")
    draw.text((1884, 28), "NATIVE 1920×1080 REVIEW", anchor="ra", font=small_font, fill="#789d98")
    cards = []
    for index, direction in enumerate(ORDER):
        source = ROOT / "art" / "aster" / f"{direction}_idle_0_master.png"
        if not source.is_file():
            raise SystemExit(f"missing approved source: {source}")
        image = key_green(Image.open(source))
        card_x = 24 + (index % 4) * 474
        card_y = 76 + (index // 4) * 490
        card_w, card_h = 452, 466
        draw.rounded_rectangle((card_x, card_y, card_x + card_w, card_y + card_h), radius=10, fill="#14252e", outline="#36524f", width=2)
        draw.text((card_x + 18, card_y + 12), direction, font=label_font, fill="#9cedd2")
        max_w, max_h = card_w - 34, card_h - 74
        scale = min(max_w / image.width, max_h / image.height)
        resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
        x = card_x + (card_w - resized.width) // 2
        y = card_y + 52 + (max_h - resized.height) // 2
        sheet.paste(resized, (x, y), resized)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        draw.text((card_x + 18, card_y + card_h - 28), f"{direction} / IDLE / 0   {digest}", font=small_font, fill="#739f94")
        cards.append({"direction": direction, "source": source.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    MANIFEST.write_text(json.dumps({"native": [1920, 1080], "role": "standing-source visual QA only", "cards": cards}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"saved {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
