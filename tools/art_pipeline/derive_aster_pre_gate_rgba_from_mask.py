#!/usr/bin/env python3
"""Derive the one ASTER pre-gate runtime texture from its locked source mask.

The source asset remains an exact-green RGB authority image.  This utility
does not key colours heuristically: it uses the retained binary subject mask,
verifies every exterior pixel is exactly #00FF00, then writes a single RGBA
derivative solely for the isolated Godot QA preview.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

# The read-only ComfyUI portable interpreter runs in isolated mode and omits
# the script directory from sys.path. Keep this project-local helper import
# explicit so the pipeline never needs to modify that interpreter.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_paths import require_project_output_path


GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "pre-gate RGBA output")
    args.qa = require_project_output_path(args.qa, "pre-gate RGBA QA")
    if not args.source.is_file() or not args.mask.is_file():
        raise SystemExit("locked green source and binary mask are both required")
    source_before = sha256(args.source)
    rgb = np.asarray(Image.open(args.source).convert("RGB"))
    mask = np.asarray(Image.open(args.mask).convert("L"))
    if rgb.shape[:2] != mask.shape or rgb.shape[:2] != (1024, 1024):
        raise SystemExit(f"source/mask must match 1024x1024: {rgb.shape[:2]}, {mask.shape}")
    values = set(np.unique(mask).tolist())
    if not values.issubset({0, 255}) or values == {0} or values == {255}:
        raise SystemExit(f"mask must be non-empty binary 0/255: {sorted(values)}")
    subject = mask == 255
    exterior = ~subject
    exact_exterior = float(np.all(rgb[exterior] == GREEN, axis=1).mean())
    opaque_green = int(np.all(rgb[subject] == GREEN, axis=1).sum())
    if exact_exterior != 1.0 or opaque_green != 0:
        raise SystemExit(f"locked green/mask contract failed: exterior={exact_exterior}, subject_green={opaque_green}")
    rgba = np.dstack((rgb, np.where(subject, 255, 0).astype(np.uint8)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, mode="RGBA").save(args.output)
    source_after = sha256(args.source)
    if source_after != source_before:
        raise SystemExit("source asset changed during RGBA derivation")
    qa = {
        "schema": 1,
        "role": "Godot PRE_GATE / NONPROMOTED / STATIC_PREVIEW derivative only",
        "source": args.source.as_posix(),
        "source_sha256_before": source_before,
        "source_sha256_after": source_after,
        "mask": args.mask.as_posix(),
        "mask_sha256": sha256(args.mask),
        "output": args.output.as_posix(),
        "output_sha256": sha256(args.output),
        "resolution": [int(rgb.shape[1]), int(rgb.shape[0])],
        "source_background_rgb": GREEN.tolist(),
        "exact_green_exterior_ratio": exact_exterior,
        "opaque_green_subject_pixels": opaque_green,
        "alpha_values": np.unique(rgba[:, :, 3]).tolist(),
        "runtime_promotion": False,
        "animation_production": False,
    }
    args.qa.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print("ASTER_PRE_GATE_RGBA_DERIVATIVE_PASS=" + json.dumps(qa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
