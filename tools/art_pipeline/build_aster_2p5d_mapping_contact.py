#!/usr/bin/env python3
"""Build a compact preview and motion-difference evidence for one 2.5D proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
KEYS = ("ready", "inhale", "micro_weight_shift", "return")


def project_path(value: Path) -> Path:
    resolved = value.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"proof must remain under project: {resolved}") from error
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof", required=True, type=Path)
    args = parser.parse_args()
    proof = project_path(args.proof)
    source, masks = proof / "source", proof / "masks"
    preview = proof / "previews"
    if preview.exists() and any(preview.iterdir()):
        raise SystemExit("refusing to overwrite preview evidence")
    full_images, full_masks = [], []
    for key in KEYS:
        prefix = f"ASTER_IDLE_E_{key.upper()}_2P5D"
        image, mask = source / f"{prefix}_GREEN.png", masks / f"{prefix}_MASK.png"
        if not image.is_file() or not mask.is_file():
            raise SystemExit(f"missing finalized pair for {key}")
        full_images.append(np.asarray(Image.open(image).convert("RGB")))
        full_masks.append(np.asarray(Image.open(mask).convert("L")) > 0)
    preview.mkdir()
    contact = Image.new("RGB", (2048, 2048), (0, 255, 0))
    for index, data in enumerate(full_images):
        tile = Image.fromarray(data, mode="RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
        contact.paste(tile, ((index % 2) * 1024, (index // 2) * 1024))
    contact_path = preview / "ASTER_IDLE_E_2P5D_CONTACT_GREEN.png"
    contact.save(contact_path)
    reference, reference_mask = full_images[0].astype(np.int16), full_masks[0]
    changes = []
    for key, image, mask in zip(KEYS[1:], full_images[1:], full_masks[1:]):
        union = reference_mask | mask
        delta = np.abs(image.astype(np.int16) - reference).mean(axis=2)
        changes.append({"key": key, "changed_subject_pixels": int(np.count_nonzero((delta > 3) & union)), "mean_subject_rgb_delta": float(delta[union].mean())})
    if not all(item["changed_subject_pixels"] > 0 for item in changes):
        raise SystemExit(f"motion-proof fail: no source-art pixel change: {changes}")
    report = {"role": "ASTER 2.5D E/idle non-final contact and motion evidence", "contact": contact_path.relative_to(ROOT).as_posix(), "input_source_pairs": 4, "changes_from_ready": changes, "runtime_asset": False}
    report_path = preview / "ASTER_IDLE_E_2P5D_CONTACT_QA.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_2P5D_CONTACT_PASS=" + json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
