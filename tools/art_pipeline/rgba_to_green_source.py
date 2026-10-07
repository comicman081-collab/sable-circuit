#!/usr/bin/env python3
"""Make an exact #00FF00 source matte from a Blender-authored RGBA render."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from project_paths import require_project_output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "green-matte output")
    args.qa = require_project_output_path(args.qa, "green-matte QA")
    rgba = Image.open(args.input).convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"))
    alpha_min, alpha_max = int(alpha.min()), int(alpha.max())
    if not (alpha_min == 0 and alpha_max == 255):
        raise SystemExit("BLENDER_ALPHA_QA_FAIL missing transparent/opaque extrema")
    green = Image.new("RGB", rgba.size, (0, 255, 0))
    green.paste(rgba, mask=rgba.getchannel("A"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    green.save(args.output)
    source = np.asarray(green)
    exact = float(np.all(source[alpha == 0] == np.asarray([0, 255, 0], dtype=np.uint8), axis=1).mean())
    qa = {
        "pass": exact == 1.0,
        "input": args.input.as_posix(),
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "output": args.output.as_posix(),
        "green_rgb": [0, 255, 0],
        "exact_green_transparent_ratio": exact,
        "alpha_extrema": [alpha_min, alpha_max],
    }
    args.qa.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print("BLENDER_GREEN_MATTE_PASS", json.dumps(qa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
