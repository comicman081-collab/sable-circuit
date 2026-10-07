#!/usr/bin/env python3
"""Build a native 1920x1080 diagnostic contact sheet from a captured pose cycle."""

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


def foreground_box(image: Image.Image):
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[0] != alpha.getextrema()[1]:
        return alpha.getbbox()
    rgb = rgba.convert("RGB")
    black = Image.new("RGB", rgb.size, (0, 0, 0))
    return Image.eval(Image.merge("RGB", tuple(
        Image.eval(channel, lambda v: 255 if v > 8 else 0)
        for channel in rgb.split()
    )).convert("L"), lambda v: 255 if v else 0).getbbox() or (0, 0, image.width, image.height)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    capture_path, out, manifest = local(args.capture), local(args.out), local(args.manifest)
    if out.exists() or manifest.exists():
        raise SystemExit("refusing to overwrite diagnostic evidence")
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    rows = capture.get("frames", [])
    if not rows or len(rows) > 24:
        raise SystemExit("expected one bounded cycle of 1..24 frames")
    columns = 6
    cell_w, cell_h = 320, 320
    top = 82
    canvas = Image.new("RGB", (1920, 1080), (25, 36, 48))
    draw = ImageDraw.Draw(canvas)
    title = f"{capture.get('action')} {capture.get('screen_direction')} | COMPLETE CAPTURED CYCLE | POSE GUIDE ONLY"
    draw.text((22, 22), title, fill=(228, 238, 245))
    draw.text((22, 48), "Every native source frame is shown; select by silhouette + measured soles, never stride alone.", fill=(154, 185, 202))
    bound = []
    floor_z = capture.get("fixed_floor_world_z_m")
    for index, row in enumerate(rows):
        image_path = local(Path(row["image"]["path"])) if isinstance(row["image"], dict) else local(Path(row["image"]))
        image = Image.open(image_path).convert("RGBA")
        box = foreground_box(image)
        crop = image.crop(box)
        crop.thumbnail((280, 252), Image.Resampling.LANCZOS)
        x = (index % columns) * cell_w
        y = top + (index // columns) * cell_h
        panel = Image.new("RGBA", (cell_w, cell_h), (34, 49, 64, 255))
        panel.alpha_composite(crop, ((cell_w - crop.width) // 2, 28 + (252 - crop.height) // 2))
        canvas.paste(panel.convert("RGB"), (x, y))
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(56, 77, 96))
        phase = str(row.get("phase", "unlabeled"))
        draw.text((x + 8, y + 7), f"{phase.upper()} | SAMPLE {row.get('sample')} | F {row['frame']}", fill=(89, 220, 235))
        clearance_text = ""
        vertices = row.get("actual_sole_vertices_world_m", {})
        if isinstance(floor_z, (int, float)) and set(vertices) == {"left", "right"}:
            clearances = {
                side: 1000.0 * (min(point[2] for point in vertices[side]) - float(floor_z))
                for side in ("left", "right")
            }
            clearance_text = f" | sole L/R {clearances['left']:.1f}/{clearances['right']:.1f}mm"
        draw.text((x + 8, y + 290), f"t={row['time_s']:.3f}s{clearance_text}", fill=(188, 205, 215))
        bound.append({"index": index, "phase": phase, "sample": row.get("sample"), "frame": row["frame"], "image": row["image"], "bbox": list(box)})
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    report = {
        "schema": 1,
        "status": "DIAGNOSTIC_POSE_GUIDE_CONTACT_SHEET_NOT_VISUAL_PASS",
        "capture": {"path": capture_path.relative_to(ROOT).as_posix(), "sha256": digest(capture_path)},
        "sheet": {"path": out.relative_to(ROOT).as_posix(), "sha256": digest(out)},
        "native_resolution": [1920, 1080],
        "action": capture.get("action"),
        "screen_direction": capture.get("screen_direction"),
        "frames": bound,
        "production_ready": False,
    }
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
