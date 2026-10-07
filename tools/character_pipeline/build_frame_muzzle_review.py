#!/usr/bin/env python3
"""Build native-resolution review sheets for frame-indexed muzzle sockets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mark(draw: ImageDraw.ImageDraw, origin: tuple[int, int], point: list[float]) -> None:
    x = origin[0] + float(point[0])
    y = origin[1] + float(point[1])
    draw.ellipse((x - 7, y - 7, x + 7, y + 7), outline=(255, 65, 65), width=3)
    draw.line((x - 14, y, x + 14, y), fill=(255, 65, 65), width=2)
    draw.line((x, y - 14, x, y + 14), fill=(255, 65, 65), width=2)


def paste_cell(canvas: Image.Image, atlas: Image.Image, frame: int, origin: tuple[int, int]) -> None:
    cell = atlas.crop((0, frame * CELL, CELL, (frame + 1) * CELL)).convert("RGBA")
    panel = Image.new("RGB", (CELL, CELL), (34, 46, 58))
    panel.paste(cell, (0, 0), cell)
    canvas.paste(panel, origin)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default="MICA_C03", help="uppercase character asset prefix")
    parser.add_argument("--revision", default="V4", help="uppercase reviewed runtime revision")
    args = parser.parse_args()
    if not args.prefix.replace("_", "").isalnum() or args.prefix != args.prefix.upper():
        raise SystemExit("--prefix must be uppercase alphanumeric/underscore")
    if not args.revision.replace("_", "").isalnum() or args.revision != args.revision.upper():
        raise SystemExit("--revision must be uppercase alphanumeric/underscore")
    descriptor_path = project_path(args.descriptor, "descriptor")
    runtime = project_path(args.runtime, "runtime")
    output = project_path(args.output, "output")
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    records: dict[str, object] = {}

    for direction in DIRECTIONS:
        entry = descriptor["directions"][direction]
        sockets = entry["move_muzzle_xy"]
        atlas_path = runtime / direction / "move.png"
        with Image.open(atlas_path) as atlas:
            canvas = Image.new("RGB", (2304, 1080), (12, 20, 28))
            draw = ImageDraw.Draw(canvas)
            draw.text((32, 24), f"{args.prefix} {args.revision} | {direction} | 12-POSE FRAME-TRACKED MUZZLE REVIEW", fill=(225, 240, 248), font=font)
            for pose in range(12):
                frame = pose * 2
                row, column = divmod(pose, 6)
                origin = (column * CELL, 86 + row * 454)
                paste_cell(canvas, atlas, frame, origin)
                mark(draw, origin, sockets[frame])
                draw.text((origin[0] + 8, origin[1] + 390), f"F{frame:02d} [{sockets[frame][0]:.1f},{sockets[frame][1]:.1f}]", fill=(105, 220, 245), font=font)
            draw.text((32, 1048), "Native 2304x1080; every 384px runtime cell is shown at 1:1. Red crosshair marks projectile birth.", fill=(155, 175, 188), font=font)
            sheet = output / f"{args.prefix}_{args.revision}_{direction}_MOVE_FRAME_MUZZLE_REVIEW_2304X1080.png"
            canvas.save(sheet)
        records[direction] = {
            "move_atlas": atlas_path.relative_to(ROOT).as_posix(),
            "move_sha256": sha256(atlas_path),
            "review": sheet.relative_to(ROOT).as_posix(),
            "review_sha256": sha256(sheet),
            "reviewed_frames": list(range(0, 24, 2)),
        }

    fire_canvas = Image.new("RGB", (1920, 1080), (12, 20, 28))
    fire_draw = ImageDraw.Draw(fire_canvas)
    fire_draw.text((48, 26), f"{args.prefix} {args.revision} | FIRE FRAME 02 | FRAME-TRACKED MUZZLE REVIEW", fill=(225, 240, 248), font=font)
    x_positions, y_positions = (160, 584, 1008, 1432), (92, 558)
    for index, direction in enumerate(DIRECTIONS):
        row, column = divmod(index, 4)
        origin = (x_positions[column], y_positions[row])
        atlas_path = runtime / direction / "fire.png"
        socket = descriptor["directions"][direction]["fire_muzzle_xy"][2]
        with Image.open(atlas_path) as atlas:
            paste_cell(fire_canvas, atlas, 2, origin)
        mark(fire_draw, origin, socket)
        fire_draw.text((origin[0], origin[1] + 390), f"{direction} [{socket[0]:.1f},{socket[1]:.1f}]", fill=(105, 220, 245), font=font)
    fire_draw.text((48, 1050), "Native 1920x1080; runtime cells shown at 1:1. Red crosshair marks projectile birth.", fill=(155, 175, 188), font=font)
    fire_sheet = output / f"{args.prefix}_{args.revision}_FIRE_FRAME_02_MUZZLE_REVIEW_1920X1080.png"
    fire_canvas.save(fire_sheet)

    report = {
        "schema": 1,
        "descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "descriptor_sha256": sha256(descriptor_path),
        "runtime": runtime.relative_to(ROOT).as_posix(),
        "native_cell_resolution": [CELL, CELL],
        "no_upscale": True,
        "fire_review": fire_sheet.relative_to(ROOT).as_posix(),
        "fire_review_sha256": sha256(fire_sheet),
        "move_reviews": records,
        "gate": "PENDING_VISUAL_REVIEW",
    }
    report_path = output / f"{args.prefix}_{args.revision}_FRAME_MUZZLE_REVIEW.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fire_review": report["fire_review"], "report": report_path.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
