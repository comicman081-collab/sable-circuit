#!/usr/bin/env python3
"""Build a native-1080p, no-upscale muzzle-socket review from packed fire atlases.

This is a deterministic technical inspection aid.  It renders no character
art; each 384px fire-contact cell is pasted at native size and marked with the
proposed projectile birth coordinate for a human visual gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
GREEN = np.array([0, 255, 0], dtype=np.uint8)


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside project: {path}") from exc
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--muzzles-json", type=Path)
    parser.add_argument("--auto-propose", action="store_true", help="derive an outward muzzle proposal from the selected exact-green fire cell")
    parser.add_argument("--frame", type=int, default=2, choices=range(6), help="fire-atlas frame to review; 2 is the UAL muzzle-contact frame")
    parser.add_argument("--review-tag", default="REVIEW", help="uppercase evidence tag used in the output filenames")
    parser.add_argument("--prefix", default="ROOK_C02", help="asset prefix used in project-local review filenames")
    args = parser.parse_args()
    if not args.review_tag.replace("_", "").isalnum() or args.review_tag != args.review_tag.upper():
        raise SystemExit("--review-tag must be uppercase alphanumeric/underscore")
    if not args.prefix.replace("_", "").isalnum() or args.prefix != args.prefix.upper():
        raise SystemExit("--prefix must be uppercase alphanumeric/underscore")
    candidate = project_path(args.candidate, "candidate")
    if bool(args.muzzles_json) == bool(args.auto_propose):
        raise SystemExit("provide exactly one of --muzzles-json or --auto-propose")
    if not candidate.is_dir():
        raise SystemExit("candidate directory must exist")
    muzzle_path = project_path(args.muzzles_json, "muzzles JSON") if args.muzzles_json else None
    if muzzle_path is not None and not muzzle_path.is_file():
        raise SystemExit("muzzles JSON must exist")
    direction_units = {
        "E": (1.0, 0.0), "SE": (0.7071, 0.7071), "S": (0.0, 1.0), "SW": (-0.7071, 0.7071),
        "W": (-1.0, 0.0), "NW": (-0.7071, -0.7071), "N": (0.0, -1.0), "NE": (0.7071, -0.7071),
    }
    def automatic_muzzle(cell: Image.Image, direction: str) -> list[float]:
        pixels = np.asarray(cell.convert("RGB"))
        opaque = ~np.all(pixels == GREEN, axis=2)
        ys, xs = np.nonzero(opaque)
        if xs.size < 80:
            raise SystemExit(f"insufficient opaque pixels for {direction}")
        dx, dy = direction_units[direction]
        center_x, center_y = 192.0, 192.0
        distances = (xs - center_x) * dx + (ys - center_y) * dy
        best = int(np.argmax(distances))
        x, y = float(xs[best]) + dx * 3.0, float(ys[best]) + dy * 3.0
        for _ in range(32):
            px, py = int(round(max(0.0, min(383.0, x)))), int(round(max(0.0, min(383.0, y))))
            if not opaque[py, px]:
                return [round(x, 4), round(y, 4)]
            x += dx
            y += dy
        raise SystemExit(f"automatic muzzle remained inside silhouette for {direction}")
    if args.auto_propose:
        muzzles = {}
        for direction in DIRECTIONS:
            atlas = candidate / direction / "fire_green.png"
            with Image.open(atlas) as image:
                cell = image.crop((0, args.frame * 384, 384, (args.frame + 1) * 384))
            muzzles[direction] = automatic_muzzle(cell, direction)
        muzzle_path = candidate / f"{args.prefix}_MUZZLE_AUTO_FRAME_{args.frame:02d}.json"
        if muzzle_path.exists():
            raise SystemExit(f"refusing to overwrite muzzle proposal: {muzzle_path}")
        muzzle_path.write_text(json.dumps(muzzles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        loaded_muzzles = json.loads(muzzle_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
        muzzles = loaded_muzzles.get("directions", loaded_muzzles) if isinstance(loaded_muzzles, dict) else loaded_muzzles
    if list(muzzles) != list(DIRECTIONS):
        raise SystemExit("muzzles JSON must contain the canonical eight directions in order")

    canvas = Image.new("RGB", (1920, 1080), (12, 20, 28))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((48, 28), f"{args.prefix} | FIRE CONTACT | MANUAL MUZZLE-SOCKET REVIEW", fill=(225, 240, 248), font=font)
    x_positions = (160, 584, 1008, 1432)
    y_positions = (92, 558)
    records: dict[str, object] = {}
    for index, direction in enumerate(DIRECTIONS):
        row, column = divmod(index, 4)
        atlas = candidate / direction / "fire_green.png"
        with Image.open(atlas) as image:
            cell = image.crop((0, args.frame * 384, 384, (args.frame + 1) * 384)).convert("RGB")
        array = np.asarray(cell)
        alpha = np.where(np.all(array == GREEN, axis=2), 0, 255).astype(np.uint8)
        subject = Image.fromarray(np.dstack((array, alpha)), mode="RGBA")
        x, y = x_positions[column], y_positions[row]
        panel = Image.new("RGB", (384, 384), (236, 240, 244) if row == 0 else (35, 42, 50))
        panel.paste(subject, (0, 0), subject)
        canvas.paste(panel, (x, y))
        point = muzzles[direction]
        if not isinstance(point, list) or len(point) != 2:
            raise SystemExit(f"invalid muzzle point: {direction}")
        px, py = float(point[0]), float(point[1])
        draw.ellipse((x + px - 7, y + py - 7, x + px + 7, y + py + 7), outline=(255, 72, 72), width=3)
        draw.line((x + px - 13, y + py, x + px + 13, y + py), fill=(255, 72, 72), width=2)
        draw.line((x + px, y + py - 13, x + px, y + py + 13), fill=(255, 72, 72), width=2)
        draw.text((x, y + 392), f"{direction}  muzzle=({px:.1f}, {py:.1f})", fill=(105, 220, 245), font=font)
        records[direction] = {"fire_atlas": atlas.relative_to(ROOT).as_posix(), "fire_sha256": digest(atlas), "fire_frame": args.frame, "muzzle_xy": [px, py]}
    draw.text((48, 1052), "Native 1920x1080 evidence. Cells are pasted at their original 384px resolution; red crosshair is a review overlay, not runtime art.", fill=(155, 175, 188), font=font)
    output = candidate / f"{args.prefix}_MUZZLE_SOCKET_{args.review_tag}_1920X1080.png"
    if output.exists():
        raise SystemExit(f"refusing to overwrite muzzle review image: {output}")
    canvas.save(output)
    report = {
        "schema": 1,
        "role": "Manual muzzle-socket visual-review evidence",
        "resolution": [1920, 1080],
        "native_cell_resolution": [384, 384],
        "no_upscale": True,
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "records": records,
        "fire_frame": args.frame,
        "muzzles_json": muzzle_path.relative_to(ROOT).as_posix(),  # type: ignore[union-attr]
        "review_status": "PENDING_HUMAN_VISUAL_CONFIRMATION",
    }
    report_path = candidate / f"{args.prefix}_MUZZLE_SOCKET_{args.review_tag}.json"
    if report_path.exists():
        raise SystemExit(f"refusing to overwrite muzzle review report: {report_path}")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"image": output.relative_to(ROOT).as_posix(), "report": report_path.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
