#!/usr/bin/env python3
"""Create native 1920x1080 contact pages for a pose-switch candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
CANVAS = (1920, 1080)
CELL = 384
HEADER = 72
POSITIONS = tuple((column * CELL, HEADER + row * CELL) for row in range(2) for column in range(5))


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--direction", default="E")
    parser.add_argument("--state", default="move")
    args = parser.parse_args()
    candidate = project_path(args.candidate, "candidate")
    output_dir = project_path(args.output_dir, "output-dir")
    frame_dir = candidate / "blender_frames" / args.direction / args.state
    if not frame_dir.is_dir():
        raise SystemExit(f"missing frame directory: {frame_dir}")
    if output_dir.exists():
        raise SystemExit(f"refusing to overwrite review directory: {output_dir}")
    output_dir.mkdir(parents=True)
    font = ImageFont.load_default()
    pages: list[dict[str, object]] = []
    frame_paths = sorted(frame_dir.glob("*.png"), key=lambda p: int(p.stem))
    if not frame_paths:
        raise SystemExit("no frames found")
    for page_index, start in enumerate(range(0, len(frame_paths), len(POSITIONS))):
        chunk = frame_paths[start : start + len(POSITIONS)]
        canvas = Image.new("RGB", CANVAS, (12, 20, 28))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, CANVAS[0], HEADER), fill=(24, 34, 46))
        draw.text((24, 12), f"MICA C03 R17 POSE-SWITCH | {args.direction} | {args.state} | frames {start:02d}-{start + len(chunk) - 1:02d}", fill=(235, 243, 249), font=font)
        draw.text((24, 35), "Native 384px Blender frames; A/B full-body ImageGen pose sources, UAL contact schedule; no upscale.", fill=(161, 190, 211), font=font)
        rows: list[dict[str, object]] = []
        for position, path in zip(POSITIONS, chunk):
            image = Image.open(path).convert("RGBA")
            if image.size != (CELL, CELL):
                raise SystemExit(f"unexpected frame size: {path} {image.size}")
            # Blender renders a transparent world.  Composite the RGBA frame
            # onto the review slate so the silhouette and green-key edges are
            # visible instead of being mistaken for a black failed render.
            slate = Image.new("RGBA", (CELL, CELL), (36, 48, 62, 255))
            slate.alpha_composite(image)
            canvas.paste(slate.convert("RGB"), position)
            frame_index = int(path.stem)
            draw.text((position[0] + 8, position[1] + 8), f"F{frame_index:02d}", fill=(240, 215, 110), font=font)
            rows.append({"frame": frame_index, "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "position_xy": list(position)})
        output = output_dir / f"MICA_C03_R17_{args.direction}_{args.state}_F{start:02d}_REVIEW_1920X1080.png"
        canvas.save(output)
        pages.append({"frames": rows, "output": output.relative_to(ROOT).as_posix(), "sha256": sha256(output), "resolution": list(CANVAS), "native_cell": [CELL, CELL], "upscaled": False})
    manifest = {"schema": 1, "role": "MICA C03 R17 pose-switch Blender frame visual evidence", "candidate": candidate.relative_to(ROOT).as_posix(), "direction": args.direction, "state": args.state, "pages": pages, "review_status": "PENDING_PONYTAIL_FULL_AND_CHATGPT_WEB"}
    manifest_path = output_dir / "POSE_SWITCH_REVIEW_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("POSE_SWITCH_REVIEW_BUILD_PASS=" + json.dumps({"manifest": manifest_path.relative_to(ROOT).as_posix(), "pages": len(pages)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
