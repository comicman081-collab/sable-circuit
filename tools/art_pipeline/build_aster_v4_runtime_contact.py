#!/usr/bin/env python3
"""Assemble the latest native Godot ASTER V4 runtime captures for review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifacts/aster_v4_runtime_capture"
OUTPUT = SOURCE / "ASTER_V4_NATIVE_RUNTIME_CONTACT.png"
MANIFEST = SOURCE / "ASTER_V4_NATIVE_RUNTIME_CONTACT.json"
ITEMS = [
    ("MOVE E", "MOVE_E_RUNTIME.png"),
    ("MOVE SE", "MOVE_SE_RUNTIME.png"),
    ("MOVE S", "MOVE_S_RUNTIME.png"),
    ("MOVE SW", "MOVE_SW_RUNTIME.png"),
    ("MOVE W", "MOVE_W_RUNTIME.png"),
    ("MOVE NW", "MOVE_NW_RUNTIME.png"),
    ("MOVE N", "MOVE_N_RUNTIME.png"),
    ("MOVE NE", "MOVE_NE_RUNTIME.png"),
    ("FIRE E · SEPARATE VFX V2", "FIRE_E_RUNTIME_SEPARATE_VFX.png"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    missing = [filename for _, filename in ITEMS if not (SOURCE / filename).is_file()]
    if missing:
        raise SystemExit("missing runtime captures: " + ", ".join(missing))

    cell_size = (640, 360)
    label_height = 30
    sheet = Image.new("RGB", (cell_size[0] * 3, (cell_size[1] + label_height) * 3), (3, 8, 11))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    records = []
    for index, (label, filename) in enumerate(ITEMS):
        source_path = SOURCE / filename
        image = Image.open(source_path).convert("RGB")
        if image.size != (1280, 720):
            raise RuntimeError(f"unexpected capture size: {filename} {image.size}")
        image = image.resize(cell_size, Image.Resampling.LANCZOS)
        column = index % 3
        row = index // 3
        x = column * cell_size[0]
        y = row * (cell_size[1] + label_height)
        sheet.paste(image, (x, y + label_height))
        draw.rectangle((x, y, x + cell_size[0], y + label_height), fill=(4, 20, 27))
        draw.text((x + 10, y + 6), label, fill=(122, 239, 255), font=font)
        records.append({
            "label": label,
            "source": source_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(source_path),
            "resolution": [1280, 720],
        })

    sheet.save(OUTPUT, format="PNG", optimize=True)
    manifest = {
        "schema": 1,
        "role": "ASTER V4 native Godot runtime contact sheet",
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT),
        "resolution": list(sheet.size),
        "captures": records,
        "move_directions": 8,
        "fire_character_frames_baked_vfx": False,
        "fire_runtime_vfx": "ASTER_MUZZLE_FLASH_E_V2_RGBA.webp",
        "krea2_used": False,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_V4_NATIVE_RUNTIME_CONTACT_PASS=" + json.dumps({
        "output": manifest["output"],
        "sha256": manifest["sha256"],
        "captures": len(records),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
