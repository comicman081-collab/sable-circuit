#!/usr/bin/env python3
"""Promote an approved exact-green source into a hard-alpha runtime PNG.

This tool intentionally has no image-generation capability.  It preserves every
non-green source pixel and makes only RGB(0,255,0) transparent, which keeps the
user-required chroma matte out of the runtime asset while making the conversion
reproducible and auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from project_paths import require_project_output_path


GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def alpha_preview(rgba: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    canvas = Image.new("RGB", rgba.size, background)
    canvas.paste(rgba, mask=rgba.getchannel("A"))
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="approved RGB #00FF00-matte source")
    parser.add_argument("--output", type=Path, required=True, help="runtime RGBA PNG")
    parser.add_argument("--qa", type=Path, required=True, help="runtime conversion QA JSON")
    parser.add_argument("--preview-light", type=Path, required=True)
    parser.add_argument("--preview-dark", type=Path, required=True)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "runtime export")
    args.qa = require_project_output_path(args.qa, "runtime export QA")
    args.preview_light = require_project_output_path(args.preview_light, "runtime preview")
    args.preview_dark = require_project_output_path(args.preview_dark, "runtime preview")

    if not args.input.is_file():
        raise SystemExit(f"approved source is unavailable: {args.input}")

    rgb = np.asarray(Image.open(args.input).convert("RGB"))
    green = np.all(rgb == GREEN, axis=2)
    green_ratio = float(green.mean())
    if not 0.15 <= green_ratio < 0.98:
        raise SystemExit(f"SOURCE_GREEN_MATTE_FAIL coverage={green_ratio:.6f}")

    alpha = np.where(green, 0, 255).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))
    result = Image.fromarray(rgba, mode="RGBA")
    for target in (args.output, args.qa, args.preview_light, args.preview_dark):
        target.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    alpha_preview(result, (238, 242, 246)).save(args.preview_light)
    alpha_preview(result, (12, 20, 28)).save(args.preview_dark)

    alpha_values = np.unique(alpha).tolist()
    opaque_rgb = rgb[~green]
    qa = {
        "pass": alpha_values == [0, 255],
        "input": args.input.as_posix(),
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "runtime_output": args.output.as_posix(),
        "runtime_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "source_green_rgb": GREEN.tolist(),
        "source_green_coverage": green_ratio,
        "alpha_values": alpha_values,
        "opaque_green_pixels": int(np.all(opaque_rgb == GREEN, axis=1).sum()),
        "previews": [args.preview_light.as_posix(), args.preview_dark.as_posix()],
    }
    args.qa.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    if not qa["pass"] or qa["opaque_green_pixels"] != 0:
        raise SystemExit("RUNTIME_ALPHA_QA_FAIL")
    print("RUNTIME_ALPHA_QA_PASS", json.dumps(qa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
