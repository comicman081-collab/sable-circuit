#!/usr/bin/env python3
"""Normalize an ImageGen walk-pose candidate to the project green/mask contract.

This is strictly deterministic chroma processing.  It preserves every
non-green subject pixel; only green-dominant backdrop pixels are replaced with
the project-authoritative flat #00FF00 and written as a separate binary mask.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[2]
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


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
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()
    source = project_path(args.input, "input")
    output = project_path(args.output, "output")
    mask_output = project_path(args.mask, "mask")
    qa_output = project_path(args.qa, "qa")
    if not source.is_file():
        raise SystemExit(f"missing ImageGen walk source: {source}")
    if output == source:
        raise SystemExit("normalizer refuses to overwrite ImageGen source")
    for target in (output, mask_output, qa_output):
        if target.exists():
            raise SystemExit(f"normalizer refuses to overwrite existing output: {target}")

    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    values = rgb.astype(np.int16)
    # ROOK has no green costume modules; this keys the generated green
    # backdrop and antialiased green fringe without repainting dark suit,
    # white hair, skin, or amber hardware.
    green_background = (
        (values[:, :, 1] >= values[:, :, 0] + 35)
        & (values[:, :, 1] >= values[:, :, 2] + 35)
        & (values[:, :, 1] >= 70)
    )
    # ImageGen can occasionally draw a thin white separator exactly on a
    # requested contact-sheet cell boundary.  Treat only near-neutral bright
    # pixels within the outer four-pixel crop border as derived background.
    # This never touches interior costume/weapon pixels and leaves the source
    # sheet immutable.
    border_band = np.zeros(green_background.shape, dtype=bool)
    border_band[:4, :] = True
    border_band[-4:, :] = True
    border_band[:, :4] = True
    border_band[:, -4:] = True
    channel_spread = values.max(axis=2) - values.min(axis=2)
    white_grid_separator = border_band & (values.min(axis=2) >= 210) & (channel_spread <= 30)
    green_background |= white_grid_separator
    if not bool(green_background[0, 0] and green_background[0, -1] and green_background[-1, 0] and green_background[-1, -1]):
        raise SystemExit("walk source border is not a usable green backdrop")
    # Sheet-cell extraction can retain disconnected fragments from a
    # neighbouring grid cell.  ROOK, weapon, and both supported hands form
    # the dominant connected component.  Discard only disconnected remnants
    # from the derived matte; the immutable ImageGen source stays untouched.
    subject = ~green_background
    labels, component_count = ndimage.label(subject, structure=np.ones((3, 3), dtype=np.uint8))
    if component_count < 1:
        raise SystemExit("walk source did not contain a non-green subject component")
    areas = np.bincount(labels.ravel())
    areas[0] = 0
    dominant_label = int(areas.argmax())
    retained_subject = labels == dominant_label
    if int(retained_subject.sum()) < 6000:
        raise SystemExit("dominant walk subject component is implausibly small")
    removed_isolated_pixels = int(subject.sum() - retained_subject.sum())
    normalized = rgb.copy()
    normalized[~retained_subject] = GREEN
    mask = np.where(retained_subject, 255, 0).astype(np.uint8)
    exact_background = np.all(normalized[~retained_subject] == GREEN, axis=1)
    corners = [normalized[0, 0].tolist(), normalized[0, -1].tolist(), normalized[-1, 0].tolist(), normalized[-1, -1].tolist()]
    qa = {
        "schema": 1,
        "role": "Deterministic ImageGen walk-source exact-green and binary-mask normalization",
        "generated_pixels_modified": False,
        "operation": "green-dominant backdrop/fringe replacement plus largest-component derived matte; immutable ImageGen input preserved",
        "input": source.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(source),
        "output": output.relative_to(ROOT).as_posix(),
        "mask": mask_output.relative_to(ROOT).as_posix(),
        "resolution": [int(rgb.shape[1]), int(rgb.shape[0])],
        "background_exact_green_ratio": float(exact_background.mean()) if exact_background.size else 0.0,
        "background_pixel_count": int((~retained_subject).sum()),
        "subject_pixel_count": int(retained_subject.sum()),
        "connected_components": int(component_count),
        "retained_component_label": dominant_label,
        "removed_disconnected_subject_pixels": removed_isolated_pixels,
        "removed_border_grid_separator_pixels": int(white_grid_separator.sum()),
        "raw_imagegen_input_unchanged": True,
        "corner_rgb": corners,
        "pass": bool(exact_background.size and exact_background.all() and all(corner == [0, 255, 0] for corner in corners)),
    }
    if not qa["pass"]:
        raise SystemExit(f"walk chroma normalization QA failed: {qa}")
    output.parent.mkdir(parents=True, exist_ok=True)
    mask_output.parent.mkdir(parents=True, exist_ok=True)
    qa_output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(normalized, "RGB").save(output)
    Image.fromarray(mask, "L").save(mask_output)
    qa_output.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("IMAGEGEN_WALK_GREEN_NORMALIZE_PASS=" + json.dumps(qa, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
