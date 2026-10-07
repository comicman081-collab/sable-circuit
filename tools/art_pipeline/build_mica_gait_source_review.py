#!/usr/bin/env python3
"""Build native-cell 1080p visual evidence for one MICA gait-source set.

This is an evidence compositor only.  It reads immutable ImageGen gait cells
and their deterministic mattes, then places six 512px cells per 1920x1080
review page without resampling.  It never rewrites any source art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
CELL = 512
CANVAS = (1920, 1080)
POSITIONS = ((192, 56), (704, 56), (1216, 56), (192, 568), (704, 568), (1216, 568))


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_cell(source_dir: Path, prefix: str, direction: str, index: int) -> tuple[Path, Path]:
    stem = f"{prefix}_{direction}_GAIT_F{index:02d}_IMAGEGEN_GREEN"
    rgb = source_dir / "normalized" / f"{stem}_EXACT_GREEN.png"
    mask = source_dir / "normalized" / f"{stem}_MASK.png"
    if not rgb.is_file() or not mask.is_file():
        raise SystemExit(f"missing normalized immutable source/matte for F{index:02d}")
    return rgb, mask


def composited_cell(rgb_path: Path, mask_path: Path) -> Image.Image:
    with Image.open(rgb_path) as image:
        rgb = image.convert("RGB")
    with Image.open(mask_path) as image:
        mask = image.convert("L")
    if rgb.size != (CELL, CELL) or mask.size != (CELL, CELL):
        raise SystemExit(f"review requires native {CELL}px source cells: {rgb_path}")
    background = Image.new("RGB", (CELL, CELL), (36, 48, 62))
    background.paste(rgb, (0, 0), mask)
    return background


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prefix", default="MICA_C03")
    parser.add_argument("--direction", default="E")
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    source_dir = project_path(args.source_dir, "source-dir")
    output_dir = project_path(args.output_dir, "output-dir")
    if not source_dir.is_dir():
        raise SystemExit(f"source directory is missing: {source_dir}")
    if output_dir.exists():
        raise SystemExit(f"refusing to overwrite review output: {output_dir}")
    output_dir.mkdir(parents=True)
    font = ImageFont.load_default()
    pages: list[dict[str, object]] = []
    for page_index, start in enumerate((0, 6)):
        canvas = Image.new("RGB", CANVAS, (12, 20, 28))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, CANVAS[0], 56), fill=(24, 34, 46))
        draw.text((32, 12), f"{args.prefix} {args.revision} | {args.direction} | IMAGEGEN FULL-BODY LOW-STRIDE GAIT SOURCE | F{start:02d}-F{start + 5:02d}", fill=(235, 243, 249), font=font)
        draw.text((32, 32), "Each pose is an actual 512x512 source cell, composited over matte only: no scale, repaint, rig deformation, or root transform.", fill=(161, 190, 211), font=font)
        frames: list[dict[str, object]] = []
        for offset, (x, y) in enumerate(POSITIONS):
            index = start + offset
            rgb, mask = source_cell(source_dir, args.prefix, args.direction, index)
            canvas.paste(composited_cell(rgb, mask), (x, y))
            frames.append({
                "index": index,
                "rgb": rgb.relative_to(ROOT).as_posix(),
                "rgb_sha256": sha256(rgb),
                "mask": mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(mask),
                "native_cell_resolution": [CELL, CELL],
                "review_position_xy": [x, y],
            })
        output = output_dir / f"{args.prefix}_{args.revision}_{args.direction}_SOURCE_F{start:02d}_F{start + 5:02d}_REVIEW_1920X1080.png"
        canvas.save(output)
        pages.append({
            "frame_indices": list(range(start, start + 6)),
            "review": output.relative_to(ROOT).as_posix(),
            "review_sha256": sha256(output),
            "resolution": list(CANVAS),
            "upscaled": False,
            "frames": frames,
        })
    manifest = {
        "schema": 1,
        "role": "MICA immutable full-body ImageGen gait-source visual evidence",
        "review_status": "PENDING_PONYTAIL_FULL_SOURCE_GAIT_REVIEW",
        "source_art_modified": False,
        "source_dir": source_dir.relative_to(ROOT).as_posix(),
        "direction": args.direction,
        "revision": args.revision,
        "pages": pages,
    }
    manifest_path = output_dir / f"{args.prefix}_{args.revision}_{args.direction}_SOURCE_GAIT_REVIEW_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MICA_GAIT_SOURCE_REVIEW_PASS=" + json.dumps({"manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
