#!/usr/bin/env python3
"""Assemble the eight native ASTER projectile V6 direction captures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "artifacts/aster_projectile_v6_runtime_capture"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
OUTPUT = CAPTURE / "ASTER_PROJECTILE_V6_8_DIRECTION_NATIVE_CONTACT.png"
MANIFEST = CAPTURE / "ASTER_PROJECTILE_V6_8_DIRECTION_NATIVE_CONTACT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    width, height = 640, 360
    header = 46
    contact = Image.new("RGB", (width * 4, header + height * 2), (3, 14, 19))
    draw = ImageDraw.Draw(contact)
    draw.text(
        (14, 15),
        "ASTER COIL PROJECTILE V6 // GODOT 4.7.1 NATIVE RUNTIME // 8-DIRECTION ROTATION + ANCHOR QA",
        fill=(128, 244, 255),
    )
    sources: list[dict[str, object]] = []
    for index, direction in enumerate(DIRECTIONS):
        path = CAPTURE / f"ASTER_PROJECTILE_V6_{direction}_NATIVE_RUNTIME.png"
        if not path.is_file():
            raise SystemExit(f"missing native direction capture: {path}")
        image = Image.open(path).convert("RGB")
        if image.size != (1280, 720):
            raise SystemExit(f"unexpected capture size for {direction}: {image.size}")
        thumb = image.resize((width, height), Image.Resampling.LANCZOS)
        x = (index % 4) * width
        y = header + (index // 4) * height
        contact.paste(thumb, (x, y))
        draw.rectangle((x + 8, y + 8, x + 94, y + 34), fill=(3, 14, 19))
        draw.text((x + 16, y + 16), f"{direction} // V6", fill=(128, 244, 255))
        sources.append({"direction": direction, "file": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)})
    contact.save(OUTPUT, format="PNG", optimize=True)
    record = {
        "schema": 1,
        "asset": "ASTER_COIL_PROJECTILE_V6_RGBA.webp",
        "asset_sha256": "de1c55f99f65b5a06e19b3261fec2a4e44bfaa2de0e697e38ed8e1613f5498cb",
        "engine": "Godot 4.7.1 stable",
        "tip_anchor_normalized": [0.862, 0.5],
        "tip_anchor_basis": "right edge of visible alpha bbox at alpha > 6",
        "directions": list(DIRECTIONS),
        "captures": sources,
        "contact": OUTPUT.relative_to(ROOT).as_posix(),
        "contact_sha256": sha256(OUTPUT),
        "visual_only": True,
        "spawn_hit_preserved": True,
        "spawn_hurt_called_by_projectile": False,
    }
    MANIFEST.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_PROJECTILE_V6_8_DIRECTION_CONTACT=" + json.dumps(record, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
