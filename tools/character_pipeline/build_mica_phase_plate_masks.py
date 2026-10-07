#!/usr/bin/env python3
"""Build fixed-upper and lower-only masks for immutable ImageGen gait plates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()

    spec_path = project_path(args.spec, "spec")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    output_dir = project_path(spec["output_dir"], "output directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    upper_mask_path = project_path(spec["upper_mask"], "upper mask")
    seam_y = int(spec["composite"]["upper_seam_y_px"])
    upper_overlap_px = int(spec["composite"].get("upper_overlap_px", 0))

    with Image.open(upper_mask_path) as opened:
        upper_mask = opened.convert("L")
    width, height = upper_mask.size
    if seam_y <= 0 or seam_y >= height - 1:
        raise SystemExit(f"upper seam must be within 1..{height - 2}")
    if upper_overlap_px < 0 or seam_y + upper_overlap_px >= height:
        raise SystemExit("upper overlap must keep the extended upper mask inside the source image")

    upper_band = Image.new("L", (width, height), 0)
    ImageDraw.Draw(upper_band).rectangle(
        (0, 0, width - 1, seam_y + upper_overlap_px), fill=255
    )
    upper_fixed = ImageChops.multiply(upper_mask, upper_band)
    upper_output = output_dir / "UPPER_FIXED_MASK.png"
    upper_fixed.save(upper_output, optimize=True)

    lower_band = Image.new("L", (width, height), 0)
    ImageDraw.Draw(lower_band).rectangle((0, seam_y + 1, width - 1, height - 1), fill=255)
    phase_entries: dict[str, object] = {}
    for key, entry in spec["phase_plates"].items():
        source_mask_path = project_path(entry["mask"], f"{key} mask")
        with Image.open(source_mask_path) as opened:
            source_mask = opened.convert("L")
        if source_mask.size != (width, height):
            raise SystemExit(f"{key}: phase mask size mismatch")
        lower_mask = ImageChops.multiply(source_mask, lower_band)
        if lower_mask.getbbox() is None:
            raise SystemExit(f"{key}: lower phase mask is empty")
        output_path = output_dir / f"{key.upper()}_LOWER_MASK.png"
        lower_mask.save(output_path, optimize=True)
        phase_entries[key] = {
            "source_mask": source_mask_path.relative_to(ROOT).as_posix(),
            "source_mask_sha256": sha256(source_mask_path),
            "path": output_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(output_path),
            "bbox_xyxy": list(lower_mask.getbbox() or ()),
        }

    manifest = {
        "schema": 1,
        "role": "MICA immutable ImageGen phase-plate fixed-upper/lower mask set",
        "spec": spec_path.relative_to(ROOT).as_posix(),
        "upper_mask": upper_mask_path.relative_to(ROOT).as_posix(),
        "upper_fixed": {
            "path": upper_output.relative_to(ROOT).as_posix(),
            "sha256": sha256(upper_output),
            "bbox_xyxy": list(upper_fixed.getbbox() or ()),
        },
        "upper_seam_y_px": seam_y,
        "upper_overlap_px": upper_overlap_px,
        "phase_plates": phase_entries,
    }
    manifest_path = output_dir / "MICA_PHASE_PLATE_MASK_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
