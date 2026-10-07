#!/usr/bin/env python3
"""Export ASTER's non-final Idle/Move 360 source/mask pairs as RGBA WebP atlases."""

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
    premul = np.round(color * alpha[:, :, None]).astype(np.uint8)
    resized_rgb = np.asarray(Image.fromarray(premul, "RGB").resize((tile, tile), Image.Resampling.LANCZOS), dtype=np.float32)
    resized_alpha = np.asarray(Image.fromarray(np.round(alpha * 255).astype(np.uint8), "L").resize((tile, tile), Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    rgb = np.zeros_like(resized_rgb, dtype=np.uint8)
    np.divide(resized_rgb, np.maximum(resized_alpha[:, :, None], 1.0 / 255.0), out=rgb, where=resized_alpha[:, :, None] > 0, casting="unsafe")
    rgba = np.dstack((rgb, np.round(resized_alpha * 255).astype(np.uint8)))
    return Image.fromarray(rgba, "RGBA")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tile", type=int, default=384)
    args = parser.parse_args()
    candidate, output = project_path(args.candidate), project_path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite existing atlas export")
    manifest_path = candidate / "ASTER_IMAGEGEN_IDLE_MOVE_360_MVP_GREEN_MASK_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("finalized Idle/Move source manifest unavailable")
    source = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = {(row["state"], row["direction"], row["key"]): row for row in source["records"]}
    output.mkdir(parents=True)
    exported = []
    for state, detail in source["states"].items():
        keys = detail["keys"]
        for direction in source["directions"]:
            atlas = Image.new("RGBA", (args.tile, args.tile * len(keys)), (0, 0, 0, 0))
            frames = []
            for index, key in enumerate(keys):
                row = rows[(state, direction, key)]
                atlas.alpha_composite(scaled_rgba(ROOT / row["source"], ROOT / row["mask"], args.tile), (0, index * args.tile))
                frames.append({"index": index, "key": key, "source": row["source"], "mask": row["mask"]})
            path = output / state / f"ASTER_{state.upper()}_{direction}_360_MVP_ATLAS.webp"
            path.parent.mkdir(parents=True, exist_ok=True)
            atlas.save(path, "WEBP", lossless=True, method=6)
            exported.append({
                "state": state,
                "direction": direction,
                "file": path.relative_to(ROOT).as_posix(),
                "resolution": list(atlas.size),
                "frame_size": [args.tile, args.tile],
                "frames": frames,
                "sha256": sha256(path),
            })
    manifest = {
        "schema": 1,
        "role": "ASTER Idle/Move 360 RGBA atlas export for interactive review; non-final",
        "source_manifest": manifest_path.relative_to(ROOT).as_posix(),
        "format": "lossless WebP RGBA vertical atlases",
        "tile": args.tile,
        "exports": exported,
        "runtime_status": "HTML_REVIEW_READY_NOT_GODOT_CONNECTED",
        "visual_gate": "USER_REVIEW_REQUIRED",
    }
    (output / "ASTER_IDLE_MOVE_360_MVP_ATLAS_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IDLE_MOVE_360_ATLAS_EXPORT_PASS=" + json.dumps({"atlases": len(exported), "output": output.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
