#!/usr/bin/env python3
"""Build a native-1080p, non-upscaled eight-direction source-art contact sheet.

This is a review compositor only.  It never changes an ImageGen source master:
the supplied exact-green master and deterministic matte mask are read, then the
masked subject is downsampled into a 1920x1080 evidence sheet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CANVAS_SIZE = (1920, 1080)
THUMB_SIZE = (280, 420)


def inside_project(value: Path, label: str) -> Path:
    resolved = value.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must be inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--prefix", required=True, help="e.g. ROOK_C02")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    input_dir = inside_project(args.input_dir, "input-dir")
    output = inside_project(args.output, "output")
    report = inside_project(args.report, "report")
    if output.exists() or report.exists():
        raise SystemExit("refusing to overwrite existing contact evidence")

    font = ImageFont.load_default()
    canvas = Image.new("RGBA", CANVAS_SIZE, "#0E141C")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, CANVAS_SIZE[0], 64), fill="#18222E")
    draw.text((48, 20), f"{args.prefix} · ImageGen direction authority · source/master review", fill="#F0EDE7", font=font)
    draw.text((48, 46), "Native source resolutions are recorded per direction; alpha-matte cutouts · no source upscaling", fill="#9FB1C6", font=font)

    evidence: list[dict[str, object]] = []
    for index, direction in enumerate(DIRECTIONS):
        master = input_dir / f"{args.prefix}_{direction}_IMAGEGEN_GREEN.png"
        mask = input_dir / f"{args.prefix}_{direction}_IMAGEGEN_MASK.png"
        if not master.is_file() or not mask.is_file():
            raise SystemExit(f"missing direction pair for {direction}: {master} / {mask}")
        with Image.open(master) as source:
            rgb = source.convert("RGB")
        with Image.open(mask) as source_mask:
            alpha = source_mask.convert("L")
        if rgb.size != alpha.size:
            raise SystemExit(f"master/mask size mismatch for {direction}")
        if rgb.width < THUMB_SIZE[0] or rgb.height < THUMB_SIZE[1]:
            raise SystemExit(f"refusing to upscale source master for {direction}: {rgb.size}")
        rgba = rgb.convert("RGBA")
        rgba.putalpha(alpha)
        rgba.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        column, row = index % 4, index // 4
        left = 70 + column * 455
        top = 104 + row * 478
        right, bottom = left + 420, top + 450
        panel_fill = "#17212B" if (column + row) % 2 == 0 else "#1C2733"
        draw.rounded_rectangle((left, top, right, bottom), radius=12, fill=panel_fill, outline="#324658", width=2)
        draw.text((left + 18, top + 16), direction, fill="#D39A58", font=font)
        draw.text((left + 18, top + 38), "GREEN MASTER → MATTE", fill="#B6C5D3", font=font)
        px = left + (420 - rgba.width) // 2
        py = top + 62 + (360 - rgba.height) // 2
        canvas.alpha_composite(rgba, (px, py))
        evidence.append(
            {
                "direction": direction,
                "master": master.relative_to(ROOT).as_posix(),
                "master_sha256": sha256(master),
                "mask": mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(mask),
                "source_resolution": list(rgb.size),
                "contact_display_resolution": list(rgba.size),
                "upscaled": False,
            }
        )

    draw.rectangle((0, 1032, CANVAS_SIZE[0], CANVAS_SIZE[1]), fill="#18222E")
    draw.text((48, 1045), "Identity/costume continuity is PENDING visual review.  This artifact is an authored source review frame, not runtime proof.", fill="#F0EDE7", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output)
    payload = {
        "schema": 1,
        "kind": "native_1080p_imagegen_direction_contact",
        "source_author": "built-in ImageGen",
        "operation": "read-only contact-sheet compositing from exact-green masters and technical masks",
        "directions": evidence,
        "output": output.relative_to(ROOT).as_posix(),
        "output_resolution": list(CANVAS_SIZE),
        "source_upscaled": False,
        "costume_continuity_status": "PENDING_VISUAL_REVIEW",
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DIRECTION_CONTACT_PASS=" + json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
