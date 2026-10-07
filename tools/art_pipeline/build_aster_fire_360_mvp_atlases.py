#!/usr/bin/env python3
"""Export the reviewed FIRE-only ASTER 360 MVP as Godot-ready WebP atlases.

This is an export stage, not a runtime promotion.  It remains deliberately
unconnected while Idle and Move have no matching reviewed 360 source sets.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_MANIFEST = ROOT / "art_src/pilot_v2/aster_v2/animation_360/imagegen_aim_fire_mvp_v3/ASTER_IMAGEGEN_AIM_FIRE_360_MOTION_MVP_GREEN_MASK_MANIFEST.json"
OUTPUT = ROOT / "assets/units/operators/aster/fire_360_mvp_v3"
CELL = 384


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rgba_from_pair(source: Path, mask: Path) -> Image.Image:
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32)
    alpha = np.asarray(Image.open(mask).convert("L"), dtype=np.float32) / 255.0
    # Resize in premultiplied form so the mandatory green matte cannot bleed
    # into transparent edge pixels in the Godot WebP atlas.
    channels = [
        Image.fromarray(np.clip(rgb[:, :, channel] * alpha, 0, 255).astype(np.uint8), mode="L").resize((CELL, CELL), Image.Resampling.LANCZOS)
        for channel in range(3)
    ]
    alpha_image = Image.fromarray(np.clip(alpha * 255.0, 0, 255).astype(np.uint8), mode="L").resize((CELL, CELL), Image.Resampling.LANCZOS)
    alpha_resized = np.asarray(alpha_image).astype(np.float32)
    rgb_resized = np.zeros((CELL, CELL, 3), dtype=np.uint8)
    valid = alpha_resized > 0.5
    for channel, image in enumerate(channels):
        values = np.asarray(image).astype(np.float32)
        rgb_resized[:, :, channel][valid] = np.clip(values[valid] * 255.0 / alpha_resized[valid], 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack((rgb_resized, np.asarray(alpha_image))), mode="RGBA")


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite existing FIRE-360 atlas export")
    if not SOURCE_MANIFEST.is_file():
        raise SystemExit("finalized Fire-360 source manifest unavailable")
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    directions, keys = source_manifest["directions"], source_manifest["keys"]
    records = {(row["direction"], row["key"]): row for row in source_manifest["records"]}
    if len(records) != len(directions) * len(keys):
        raise SystemExit("full Fire-360 source coverage is required")
    if any(row["exact_green_outside_ratio"] != 1.0 for row in records.values()):
        raise SystemExit("source has a non-exact green/mask pair")
    OUTPUT.mkdir(parents=True)
    atlas_records = {}
    for direction in directions:
        atlas = Image.new("RGBA", (CELL, CELL * len(keys)), (0, 0, 0, 0))
        frames = []
        for index, key in enumerate(keys):
            record = records[(direction, key)]
            rgba = rgba_from_pair(ROOT / record["source"], ROOT / record["mask"])
            atlas.alpha_composite(rgba, (0, index * CELL))
            frames.append({"key": key, "rect": [0, index * CELL, CELL, CELL], "muzzle_vfx_visible": record["muzzle_vfx_visible"], "source": record["source"], "mask": record["mask"]})
        path = OUTPUT / f"ASTER_FIRE_{direction}_RGBA.webp"
        atlas.save(path, format="WEBP", lossless=True, quality=100, method=6)
        atlas_records[direction] = {"atlas": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "resolution": [CELL, CELL * len(keys)], "frames": frames}
    manifest = {
        "schema": 1,
        "role": "ASTER Fire-360 MVP Godot WebP atlas export; not yet runtime-promoted",
        "source_manifest": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
        "directions": directions,
        "key_order": keys,
        "fps": 12,
        "atlas_cell": CELL,
        "frame_count": len(directions) * len(keys),
        "atlases": atlas_records,
        "muzzle_vfx_visible_only_on": ["muzzle_contact", "recoil_peak"],
        "runtime_status": "NOT_CONNECTED_IDLE_MOVE_360_MISSING_AND_USER_REVIEW_PENDING",
        "krea2_used": False,
        "cloud_runtime_inference": False,
    }
    manifest_path = OUTPUT / "ASTER_FIRE_360_MVP_ATLAS_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_FIRE_360_MVP_ATLAS_EXPORT_PASS=" + json.dumps({"atlases": len(atlas_records), "frames": manifest["frame_count"], "output": OUTPUT.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
