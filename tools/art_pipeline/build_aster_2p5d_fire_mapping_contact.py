#!/usr/bin/env python3
"""Create retained visual and motion evidence for the ASTER fire candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
KEYS = ("aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return")


def project_path(value: Path) -> Path:
    path = value.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"candidate must remain under project: {path}") from error
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args()
    candidate = project_path(args.candidate)
    source, masks, preview = candidate / "source", candidate / "masks", candidate / "previews"
    if preview.exists() and any(preview.iterdir()):
        raise SystemExit("refusing to overwrite candidate preview")
    images, binary_masks = [], []
    for key in KEYS:
        stem = f"ASTER_FIRE_E_{key.upper()}_2P5D"
        rgb_path, mask_path = source / f"{stem}_GREEN.png", masks / f"{stem}_MASK.png"
        if not rgb_path.is_file() or not mask_path.is_file():
            raise SystemExit(f"missing finalized source pair for {key}")
        images.append(np.asarray(Image.open(rgb_path).convert("RGB")))
        binary_masks.append(np.asarray(Image.open(mask_path).convert("L")) > 0)
    preview.mkdir()
    contact = Image.new("RGB", (2048, 2048), (0, 255, 0))
    for index, image in enumerate(images):
        tile = Image.fromarray(image, mode="RGB").resize((682, 1024), Image.Resampling.LANCZOS)
        contact.paste(tile, ((index % 3) * 682, (index // 3) * 1024))
    contact_path = preview / "ASTER_FIRE_E_2P5D_CANDIDATE_CONTACT_GREEN.png"
    contact.save(contact_path)
    reference, reference_mask = images[0].astype(np.int16), binary_masks[0]
    changes = []
    for key, image, mask in zip(KEYS[1:], images[1:], binary_masks[1:]):
        union = reference_mask | mask
        delta = np.abs(image.astype(np.int16) - reference).mean(axis=2)
        changes.append({"key": key, "changed_subject_pixels": int(np.count_nonzero((delta > 3) & union)), "mean_subject_rgb_delta": float(delta[union].mean())})
    if not all(item["changed_subject_pixels"] > 0 for item in changes):
        raise SystemExit(f"fire motion evidence failed: {changes}")
    report = {
        "role": "ASTER E/fire 2.5D retained candidate contact and motion evidence; non-final",
        "contact": contact_path.relative_to(ROOT).as_posix(),
        "input_source_pairs": len(KEYS),
        "changes_from_aim_set": changes,
        "visual_gate": "UNREVIEWED",
        "retention": "retain this candidate until a later rejected candidate replaces it",
        "runtime_asset": False,
    }
    report_path = preview / "ASTER_FIRE_E_2P5D_CANDIDATE_CONTACT_QA.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_2P5D_FIRE_CANDIDATE_CONTACT_PASS=" + json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
