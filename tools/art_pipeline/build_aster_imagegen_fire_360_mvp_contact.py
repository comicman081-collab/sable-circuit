#!/usr/bin/env python3
"""Make an inspection contact sheet for a finalized ASTER Fire-360 MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
GREEN = (0, 255, 0)


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"path must remain inside project: {resolved}") from error
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--tile", type=int, default=256)
    args = parser.parse_args()
    if args.tile < 128 or args.tile > 512:
        raise SystemExit("tile must be in 128..512")
    candidate = project_path(args.candidate)
    manifest_path = candidate / "ASTER_IMAGEGEN_AIM_FIRE_360_MOTION_MVP_GREEN_MASK_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("finalized green/mask manifest unavailable")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    directions, keys = manifest["directions"], manifest["keys"]
    records = {(row["direction"], row["key"]): row for row in manifest["records"]}
    if len(records) != len(directions) * len(keys):
        raise SystemExit("contact requires full direction/key coverage")
    output = candidate / "previews"
    if output.exists() and any(output.iterdir()):
        raise SystemExit("refusing to overwrite existing motion contact")
    output.mkdir()
    font = ImageFont.load_default()
    canvas = Image.new("RGB", (len(directions) * args.tile, len(keys) * args.tile), GREEN)
    draw = ImageDraw.Draw(canvas)
    contact_rows = []
    for row, key in enumerate(keys):
        for column, direction in enumerate(directions):
            record = records[(direction, key)]
            source = ROOT / record["source"]
            tile = Image.open(source).convert("RGB").resize((args.tile, args.tile), Image.Resampling.LANCZOS)
            x, y = column * args.tile, row * args.tile
            canvas.paste(tile, (x, y))
            text = f"{direction} {key}" + (" *" if record["muzzle_vfx_visible"] else "")
            draw.rectangle((x + 4, y + 4, x + min(args.tile - 4, 112), y + 20), fill=(0, 20, 18))
            draw.text((x + 7, y + 7), text, fill=(220, 255, 240), font=font)
            contact_rows.append({"direction": direction, "key": key, "muzzle_vfx_visible": record["muzzle_vfx_visible"], "cell_xy": [x, y]})
    contact = output / "ASTER_FIRE_360_IMAGEGEN_AIM_MVP_CONTACT_GREEN.png"
    canvas.save(contact)
    report = {
        "role": "ASTER eight-direction Fire motion MVP contact; non-runtime user visual/motion review",
        "contact": contact.relative_to(ROOT).as_posix(),
        "tile": args.tile,
        "resolution": list(canvas.size),
        "directions": directions,
        "keys": keys,
        "muzzle_marker": "* means separate VFX visible; only muzzle_contact and recoil_peak may be marked",
        "cells": contact_rows,
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    (output / "ASTER_FIRE_360_IMAGEGEN_AIM_MVP_CONTACT_QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_AIM_FIRE_360_CONTACT_PASS=" + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
