#!/usr/bin/env python3
"""Build an ordered eight-direction ASTER ImageGen fire-master contact sheet."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
ROOT_DIR = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire"
MANIFEST = ROOT_DIR / "ASTER_IMAGEGEN_V1_FIRE_DIRECTION_MASTER_MANIFEST.json"
OUT = ROOT_DIR / "previews"
ORDER = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def main() -> int:
    if not MANIFEST.is_file():
        raise SystemExit("direction-master manifest missing")
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit("refusing to overwrite ImageGen direction contact")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = {record["direction"]: record for record in manifest.get("records", [])}
    if tuple(items) != ORDER:
        raise SystemExit(f"direction coverage mismatch: {sorted(items)}")
    OUT.mkdir()
    contact = Image.new("RGB", (2048, 2048), (0, 255, 0))
    labels = ImageDraw.Draw(contact)
    layout = []
    for index, direction in enumerate(ORDER):
        image = Image.open(ROOT / items[direction]["source_green"]).convert("RGB")
        tile = image.resize((512, 512), Image.Resampling.LANCZOS)
        x, y = (index % 4) * 512, (index // 4) * 1024
        contact.paste(tile, (x, y))
        labels.rectangle((x + 10, y + 10, x + 100, y + 52), fill=(0, 0, 0))
        labels.text((x + 22, y + 18), direction, fill=(255, 255, 255), stroke_width=1)
        layout.append({"direction": direction, "cell_xy": [x, y], "source": items[direction]["source_green"]})
    path = OUT / "ASTER_FIRE_8_DIRECTION_IMAGEGEN_V1_CONTACT_GREEN.png"
    contact.save(path)
    report = {
        "role": "ASTER ImageGen v1 8-direction fire master review contact; non-runtime",
        "contact": path.relative_to(ROOT).as_posix(),
        "directions": list(ORDER),
        "layout": layout,
        "visual_gate": "USER_REVIEW_REQUIRED",
        "next": "user visual review before any animation or runtime export",
    }
    (OUT / "ASTER_FIRE_8_DIRECTION_IMAGEGEN_V1_CONTACT_QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_V1_FIRE_DIRECTION_CONTACT=" + json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
