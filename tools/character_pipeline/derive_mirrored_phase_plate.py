#!/usr/bin/env python3
"""Create an exact horizontal mirror of one normalized gait phase plate and mask."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str, label: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain below the project root: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rgb", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--output-rgb", required=True)
    parser.add_argument("--output-mask", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    rgb_path = project_path(args.rgb, "source rgb")
    mask_path = project_path(args.mask, "source mask")
    output_rgb = project_path(args.output_rgb, "output rgb")
    output_mask = project_path(args.output_mask, "output mask")
    manifest_path = project_path(args.manifest, "manifest")
    for output in (output_rgb, output_mask, manifest_path):
        output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(rgb_path) as opened:
        rgb = opened.convert("RGB")
    with Image.open(mask_path) as opened:
        mask = opened.convert("L")
    if rgb.size != mask.size:
        raise SystemExit("source rgb/mask dimensions differ")

    mirrored_rgb = rgb.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    mirrored_mask = mask.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    mirrored_rgb.save(output_rgb, optimize=True)
    mirrored_mask.save(output_mask, optimize=True)

    report = {
        "schema": 1,
        "role": "Exact horizontal mirror of immutable normalized gait phase",
        "operation": "horizontal_flip_only",
        "resolution": list(rgb.size),
        "source_rgb": rgb_path.relative_to(ROOT).as_posix(),
        "source_rgb_sha256": sha256(rgb_path),
        "source_mask": mask_path.relative_to(ROOT).as_posix(),
        "source_mask_sha256": sha256(mask_path),
        "output_rgb": output_rgb.relative_to(ROOT).as_posix(),
        "output_rgb_sha256": sha256(output_rgb),
        "output_mask": output_mask.relative_to(ROOT).as_posix(),
        "output_mask_sha256": sha256(output_mask),
        "source_art_repainted": False,
    }
    manifest_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
