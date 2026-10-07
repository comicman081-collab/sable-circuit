#!/usr/bin/env python3
"""Finalize masks and an inspectable contact sheet for ASTER's E move MVP."""

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
    candidate = project_path(args.candidate)
    raw_manifest_path = candidate / "ASTER_IMAGEGEN_MOVE_E_MVP_MANIFEST.json"
    if not raw_manifest_path.is_file():
        raise SystemExit("raw movement manifest unavailable")
    output_manifest = candidate / "ASTER_IMAGEGEN_MOVE_E_MVP_GREEN_MASK_MANIFEST.json"
    if output_manifest.exists():
        raise SystemExit("refusing to overwrite finalized movement manifest")
    raw_manifest = json.loads(raw_manifest_path.read_text(encoding="utf-8"))
    records = []
    for row in raw_manifest["raw_renders"]:
        key = row["key"]
        source = candidate / "source" / f"ASTER_MOVE_E_{key.upper()}_GREEN.png"
        mask = candidate / "masks" / f"ASTER_MOVE_E_{key.upper()}_MASK.png"
        qa_path = candidate / "qa" / f"ASTER_MOVE_E_{key.upper()}_QA.json"
        if not source.is_file() or not mask.is_file() or not qa_path.is_file():
            raise SystemExit(f"missing processed pair for {key}")
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        if qa.get("exact_green_outside_ratio") != 1.0 or not qa.get("pass"):
            raise SystemExit(f"green/mask QA failed for {key}")
        records.append({
            **row,
            "source": source.relative_to(ROOT).as_posix(),
            "mask": mask.relative_to(ROOT).as_posix(),
            "qa": qa_path.relative_to(ROOT).as_posix(),
            "exact_green_outside_ratio": qa["exact_green_outside_ratio"],
        })
    preview = candidate / "previews"
    if preview.exists() and any(preview.iterdir()):
        raise SystemExit("refusing to overwrite existing move preview")
    preview.mkdir(exist_ok=True)
    canvas = Image.new("RGB", (len(records) * args.tile, args.tile), GREEN)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, row in enumerate(records):
        tile = Image.open(ROOT / row["source"]).convert("RGB").resize((args.tile, args.tile), Image.Resampling.LANCZOS)
        x = index * args.tile
        canvas.paste(tile, (x, 0))
        draw.rectangle((x + 4, 4, x + min(args.tile - 4, 130), 20), fill=(0, 20, 18))
        draw.text((x + 7, 7), row["key"], fill=(220, 255, 240), font=font)
    contact = preview / "ASTER_MOVE_E_IMAGEGEN_MVP_CONTACT_GREEN.png"
    canvas.save(contact)
    manifest = {
        "schema": 1,
        "role": "ASTER East eight-key locomotion MVP exact-green/mask export; non-final",
        "direction": "E",
        "keys": raw_manifest["keys"],
        "records": records,
        "contact": contact.relative_to(ROOT).as_posix(),
        "contact_resolution": list(canvas.size),
        "ual_source": raw_manifest["ual_source"],
        "ual_action": raw_manifest["ual_action"],
        "ual_role": raw_manifest["ual_role"],
        "visible_body_authority": raw_manifest["visible_body_authority"],
        "runtime_status": raw_manifest["runtime_status"],
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_MOVE_E_MVP_FINALIZE_PASS=" + json.dumps({"records": len(records), "contact": manifest["contact"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
