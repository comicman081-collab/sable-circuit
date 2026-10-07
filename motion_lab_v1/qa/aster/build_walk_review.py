"""Build a native-1080p display-only sheet for one reviewed walk direction."""
from pathlib import Path
import os
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DIRECTION = os.environ.get("ASTER_WALK_DIRECTION", "SE").upper()
OUT = ROOT / "qa" / "aster" / "walk" / f"ASTER_{DIRECTION}_WALK_REVIEW_1080P.png"
MANIFEST = ROOT / "qa" / "aster" / "walk" / f"ASTER_{DIRECTION}_WALK_REVIEW_1080P.json"


def key_green(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    edge = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]), axis=0).astype(np.int16)
    median = np.median(edge, axis=0)
    values = rgb.astype(np.int16)
    bg = ((np.max(np.abs(values - median.astype(np.int16)), axis=2) <= 24)
          & (values[:, :, 1] >= values[:, :, 0] + 35)
          & (values[:, :, 1] >= values[:, :, 2] + 35))
    return Image.fromarray(np.dstack((rgb, np.where(bg, 0, 255).astype(np.uint8))), "RGBA")


def main() -> None:
    font_path = ROOT.parent / "assets" / "fonts" / "Rajdhani-Medium.ttf"
    title = ImageFont.truetype(str(font_path), 34)
    label = ImageFont.truetype(str(font_path), 26)
    small = ImageFont.truetype(str(font_path), 18)
    sheet = Image.new("RGB", (1920, 1080), "#0b171e")
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 18), f"SABLE CIRCUIT  /  ASTER  /  {DIRECTION} WALK LOOP", font=title, fill="#b5e8d8")
    draw.text((1884, 28), "NATIVE 1920×1080 REVIEW", anchor="ra", font=small, fill="#789d98")
    records = []
    for i in range(6):
        source = ROOT / "art" / "aster" / f"{DIRECTION}_walk_{i}_master.png"
        if not source.is_file():
            source = ROOT / "qa" / "aster" / "imagegen" / f"{DIRECTION}_walk_{i}_realistic_raw.png"
        if not source.is_file():
            raise SystemExit(f"missing source {i}: {source}")
        image = key_green(Image.open(source))
        x = 24 + (i % 3) * 624
        y = 76 + (i // 3) * 490
        w, h = 600, 466
        draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill="#14252e", outline="#36524f", width=2)
        draw.text((x + 18, y + 12), f"{DIRECTION} / WALK / {i}", font=label, fill="#9cedd2")
        max_w, max_h = w - 34, h - 74
        scale = min(max_w / image.width, max_h / image.height)
        resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
        px = x + (w - resized.width) // 2
        py = y + 52 + (max_h - resized.height) // 2
        sheet.paste(resized, (px, py), resized)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        draw.text((x + 18, y + h - 28), digest[:12], font=small, fill="#739f94")
        records.append({"frame": i, "source": source.relative_to(ROOT).as_posix(), "sha256": digest})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    MANIFEST.write_text(json.dumps({"native": [1920, 1080], "role": "walk-source visual QA only", "direction": DIRECTION, "frames": records}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"saved {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
