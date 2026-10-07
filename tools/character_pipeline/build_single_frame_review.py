#!/usr/bin/env python3
"""Build native >=1920x1080, 1:1 (never upscaled) visible-frame reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]


def local(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or path == ROOT:
        raise SystemExit("project-local non-root path required")
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--runtime-rgba", type=Path)
    parser.add_argument("--green-out", type=Path, required=True)
    parser.add_argument("--dark-out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    image_path, mask_path = local(args.image), local(args.mask)
    runtime_path = local(args.runtime_rgba) if args.runtime_rgba else None
    green_out, dark_out, manifest = local(args.green_out), local(args.dark_out), local(args.manifest)
    if any(path.exists() for path in (green_out, dark_out, manifest)):
        raise SystemExit("refusing to overwrite review evidence")
    image = Image.open(image_path).convert("RGB")
    mask = Image.open(mask_path).convert("L")
    runtime = Image.open(runtime_path).convert("RGBA") if runtime_path else None
    if runtime is not None:
        if runtime.size != image.size:
            raise SystemExit("runtime RGBA and green master dimensions differ")
        mask = runtime.getchannel("A")
    if image.size != mask.size or image.width > 1920 or image.height > 2104:
        raise SystemExit("1:1 source must fit the bounded 1920px-wide review canvas")
    canvas_height = max(1080, image.height + 56)
    offset = ((1920 - image.width) // 2, 28)
    for output, dark in ((green_out, False), (dark_out, True)):
        canvas = Image.new("RGB", (1920, canvas_height), (12, 20, 28))
        if dark:
            layer = Image.new("RGB", image.size, (30, 42, 54))
            layer.paste(runtime.convert("RGB") if runtime else image, (0, 0), mask)
            canvas.paste(layer, offset)
        else:
            canvas.paste(image, offset)
        draw = ImageDraw.Draw(canvas)
        draw.text((18, 8), args.title + (" | DARK MASK REVIEW" if dark else " | EXACT-GREEN 1:1 REVIEW"), fill=(225, 235, 242))
        draw.text((18, canvas_height - 24), f"source {image.width}x{image.height} shown 1:1; no upscale", fill=(160, 180, 195))
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output)
    report = {
        "schema": 1,
        "source": {"path": image_path.relative_to(ROOT).as_posix(), "sha256": digest(image_path)},
        "mask": {"path": mask_path.relative_to(ROOT).as_posix(), "sha256": digest(mask_path)},
        "runtime_rgba": ({"path": runtime_path.relative_to(ROOT).as_posix(), "sha256": digest(runtime_path)}
                         if runtime_path else None),
        "source_size": list(image.size),
        "review_size": [1920, canvas_height],
        "scale": 1.0,
        "offset_xy": list(offset),
        "green_review": {"path": green_out.relative_to(ROOT).as_posix(), "sha256": digest(green_out)},
        "dark_review": {"path": dark_out.relative_to(ROOT).as_posix(), "sha256": digest(dark_out)},
        "quality_verdict": "HOLD_INDEPENDENT_VISUAL_REVIEW"
    }
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
