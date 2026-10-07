#!/usr/bin/env python3
"""Export ASTER's twelve distinct East locomotion keys as a decontaminated RGBA atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"path must remain inside project: {resolved}") from error
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scaled_rgba(source: Path, mask: Path, tile: int) -> Image.Image:
    color = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32)
    alpha = np.asarray(Image.open(mask).convert("L"), dtype=np.float32) / 255.0
    premultiplied = np.round(color * alpha[:, :, None]).astype(np.uint8)
    rgb = np.asarray(
        Image.fromarray(premultiplied, "RGB").resize((tile, tile), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    alpha = np.asarray(
        Image.fromarray(np.round(alpha * 255).astype(np.uint8), "L").resize((tile, tile), Image.Resampling.LANCZOS),
        dtype=np.float32,
    ) / 255.0
    unpremultiplied = np.zeros_like(rgb, dtype=np.uint8)
    np.divide(rgb, np.maximum(alpha[:, :, None], 1.0 / 255.0), out=unpremultiplied, where=alpha[:, :, None] > 0, casting="unsafe")
    # The exact-green authoring backdrop can leak into semi-transparent edge
    # samples during downscale.  Remove only chroma-green, not ASTER's cyan
    # emissives (which retain a comparable blue component).
    red, green, blue = (unpremultiplied[:, :, index].astype(np.int16) for index in range(3))
    green_fringe = (green >= 120) & (green > red * 1.35) & (green > blue * 1.35)
    alpha[green_fringe] = 0.0
    unpremultiplied[green_fringe] = 0
    return Image.fromarray(np.dstack((unpremultiplied, np.round(alpha * 255).astype(np.uint8))), "RGBA")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tile", default=384, type=int)
    args = parser.parse_args()
    candidate, output = project_path(args.candidate), project_path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite existing V4 atlas export")
    manifest_path = candidate / "ASTER_IMAGEGEN_MOVE_E_MVP_GREEN_MASK_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("finalized East movement source manifest unavailable")
    source = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = source["records"]
    atlas = Image.new("RGBA", (args.tile, args.tile * len(records)), (0, 0, 0, 0))
    frames = []
    for index, row in enumerate(records):
        atlas.alpha_composite(scaled_rgba(ROOT / row["source"], ROOT / row["mask"], args.tile), (0, index * args.tile))
        frames.append({"index": index, "key": row["key"], "source": row["source"], "mask": row["mask"]})
    output.mkdir(parents=True)
    atlas_path = output / "ASTER_MOVE_E_360_MVP_ATLAS.webp"
    atlas.save(atlas_path, "WEBP", lossless=True, method=6)
    manifest = {
        "schema": 1,
        "role": "ASTER East twelve-distinct-key locomotion RGBA atlas V4, chroma-fringe-cleaned for interactive review; non-final",
        "source_manifest": manifest_path.relative_to(ROOT).as_posix(),
        "format": "lossless WebP RGBA vertical atlas",
        "resolution": list(atlas.size),
        "frame_size": [args.tile, args.tile],
        "frames": frames,
        "file": atlas_path.relative_to(ROOT).as_posix(),
        "sha256": sha256(atlas_path),
        "runtime_status": "HTML_REVIEW_READY_NOT_GODOT_CONNECTED",
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    (output / "ASTER_MOVE_E_360_MVP_ATLAS_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_MOVE_E_V4_ATLAS_EXPORT_PASS=" + json.dumps({"frames": len(frames), "output": output.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
