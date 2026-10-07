#!/usr/bin/env python3
"""Build non-upscaled native-1080p ROOK walk-cycle review sheets.

Each sheet holds all twelve distinct authored gait cells for one direction at
their actual 384px runtime resolution.  This is an evidence compositor only:
it reads Blender outputs and never edits ImageGen masters or runtime atlases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
CELL = 384
CANVAS = (2304, 1080)
SOURCE_INDICES = tuple(range(0, 24, 2))


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate_revision(candidate: Path) -> str:
    for token in candidate.name.split("_"):
        if token.startswith("v") and token[1:].isdigit():
            return token.upper()
    raise SystemExit(f"candidate name does not expose a revision token: {candidate.name}")


def composite(panel: Image.Image, cell: Image.Image) -> None:
    checker = Image.new("RGB", (CELL, CELL), (36, 48, 62))
    checker.paste(cell, (0, 0), cell)
    panel.paste(checker, (0, 0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prefix", default="ROOK_C02")
    parser.add_argument("--revision")
    parser.add_argument(
        "--directions",
        default=",".join(DIRECTIONS),
        help="comma-separated subset of E,SE,S,SW,W,NW,N,NE",
    )
    args = parser.parse_args()
    candidate = project_path(args.candidate, "candidate")
    output_dir = project_path(args.output_dir, "output-dir")
    if not candidate.is_dir():
        raise SystemExit(f"candidate is missing: {candidate}")
    if output_dir.exists():
        raise SystemExit(f"refusing to overwrite review output: {output_dir}")
    output_dir.mkdir(parents=True)
    revision = args.revision or candidate_revision(candidate)

    font = ImageFont.load_default()
    selected_directions = tuple(part.strip().upper() for part in args.directions.split(",") if part.strip())
    if not selected_directions or any(direction not in DIRECTIONS for direction in selected_directions):
        raise SystemExit(f"invalid --directions: {args.directions}")

    reports: list[dict[str, object]] = []
    for direction in selected_directions:
        canvas = Image.new("RGB", CANVAS, (12, 20, 28))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, CANVAS[0], 72), fill=(24, 34, 46))
        draw.text((36, 20), f"{args.prefix} {revision} | {direction} | 12-POSE FULL-BODY GAIT REVIEW", fill=(235, 243, 249), font=font)
        draw.text((36, 46), "Each cell is the actual 384x384 Blender+UAL runtime frame (no upscale).  F00/F12 are UAL left/right support windows.", fill=(161, 190, 211), font=font)
        frame_paths: list[str] = []
        for pose_index, frame_index in enumerate(SOURCE_INDICES):
            source = candidate / "blender_frames" / direction / "move" / f"{frame_index:02d}.png"
            if not source.is_file():
                raise SystemExit(f"missing move frame: {source}")
            with Image.open(source) as image:
                cell = image.convert("RGBA")
            if cell.size != (CELL, CELL):
                raise SystemExit(f"wrong cell dimensions: {source} {cell.size}")
            col, row = pose_index % 6, pose_index // 6
            x, y = col * CELL, 96 + row * 468
            composite(canvas.crop((x, y, x + CELL, y + CELL)), cell)
            # Pillow crop returns a copy, so paste the composite back on canvas.
            panel = Image.new("RGB", (CELL, CELL), (36, 48, 62))
            panel.paste(cell, (0, 0), cell)
            canvas.paste(panel, (x, y))
            support = "LEFT SUPPORT" if pose_index <= 2 else "RIGHT SUPPORT" if 6 <= pose_index <= 8 else "TRANSFER / SWING"
            draw.text((x + 10, y + 398), f"F{pose_index:02d} | UAL {frame_index:02d}-{frame_index + 1:02d}", fill=(112, 224, 248), font=font)
            draw.text((x + 10, y + 418), support, fill=(225, 192, 120), font=font)
            frame_paths.append(source.relative_to(ROOT).as_posix())
        draw.text((36, 1044), "Review purpose: visible alternating left/right step, planted support, silhouette coherence and absence of waist snap.  This is not a promotion approval by itself.", fill=(194, 211, 223), font=font)
        output = output_dir / f"{args.prefix}_{revision}_{direction}_GAIT_REVIEW_2304X1080.png"
        canvas.save(output)
        reports.append({
            "direction": direction,
            "review": output.relative_to(ROOT).as_posix(),
            "review_sha256": sha256(output),
            "resolution": list(CANVAS),
            "native_cell_resolution": [CELL, CELL],
            "frame_indices": list(SOURCE_INDICES),
            "frames": frame_paths,
            "upscaled": False,
        })
    manifest = {
        "schema": 1,
        "role": f"{args.prefix} {revision} native-cell gait review evidence",
        "revision": revision,
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "directions": reports,
        "review_status": "PENDING_PONYTAIL_FULL_TEMPORAL_REVIEW",
    }
    manifest_path = output_dir / f"{args.prefix}_{revision}_GAIT_REVIEW_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ROOK_GAIT_DIRECTION_REVIEWS_PASS=" + json.dumps({"output_dir": output_dir.relative_to(ROOT).as_posix(), "manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
