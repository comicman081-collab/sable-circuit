#!/usr/bin/env python3
"""Create green-matte contact sheets from ASTER's non-final Blender guides."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
GUIDE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/guides/blender_360"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {
    "idle": ("ready", "inhale", "micro_weight_shift", "return"),
    "move": ("contact_a", "down_a", "passing_a", "high_a", "contact_b", "down_b", "passing_b", "high_b"),
    "fire": ("aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"),
}
GREEN = (0, 255, 0)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Path must stay inside project: {resolved}") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guides", type=Path, default=GUIDE_ROOT)
    parser.add_argument("--tile", type=int, default=256)
    args = parser.parse_args()
    if args.tile < 128 or args.tile > 512:
        raise SystemExit("tile must be between 128 and 512")
    guides = project_path(args.guides)
    output = guides / "previews"
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    results = []
    for state, keys in STATES.items():
        canvas = Image.new("RGB", (len(DIRECTIONS) * args.tile, len(keys) * args.tile), GREEN)
        draw = ImageDraw.Draw(canvas)
        for row, key in enumerate(keys):
            for column, direction in enumerate(DIRECTIONS):
                path = guides / "poses" / state / f"ASTER_GUIDE_{state}_{direction}_{key}_GREEN.png"
                if not path.is_file():
                    raise SystemExit(f"missing guide: {path}")
                tile = Image.open(path).convert("RGB").resize((args.tile, args.tile), Image.Resampling.NEAREST)
                x, y = column * args.tile, row * args.tile
                canvas.paste(tile, (x, y))
                draw.text((x + 5, y + 5), f"{direction} {key}", fill=(4, 20, 24), font=font, stroke_width=1, stroke_fill=(194, 255, 222))
        path = output / f"ASTER_360_{state.upper()}_GUIDE_CONTACT_GREEN.png"
        canvas.save(path)
        results.append({"state": state, "file": path.relative_to(ROOT).as_posix(), "resolution": list(canvas.size)})
    # A focused eight-sector muzzle-contact row is easier to inspect than the
    # full six-row fire sheet. It remains a Blender spatial guide, never final
    # ASTER sprite art.
    fire_key = "muzzle_contact"
    canvas = Image.new("RGB", (len(DIRECTIONS) * args.tile, args.tile), GREEN)
    draw = ImageDraw.Draw(canvas)
    for column, direction in enumerate(DIRECTIONS):
        path = guides / "poses" / "fire" / f"ASTER_GUIDE_fire_{direction}_{fire_key}_GREEN.png"
        if not path.is_file():
            raise SystemExit(f"missing guide: {path}")
        tile = Image.open(path).convert("RGB").resize((args.tile, args.tile), Image.Resampling.NEAREST)
        x = column * args.tile
        canvas.paste(tile, (x, 0))
        draw.text((x + 5, 5), f"{direction} {fire_key}", fill=(4, 20, 24), font=font, stroke_width=1, stroke_fill=(194, 255, 222))
    path = output / "ASTER_360_FIRE_MUZZLE_CONTACT_8_DIRECTION_GUIDE_GREEN.png"
    canvas.save(path)
    results.append({"state": "fire", "key": fire_key, "file": path.relative_to(ROOT).as_posix(), "resolution": list(canvas.size)})
    manifest = {"schema": 1, "role": "non-final Blender guide contacts", "source_matte": "#00FF00", "contacts": results}
    (output / "ASTER_360_GUIDE_CONTACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
