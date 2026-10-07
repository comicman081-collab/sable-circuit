#!/usr/bin/env python3
"""Create ASTER's locked 2048 canonical Static Master working base.

This is intentionally a deterministic construction step, not a generator: it
does not redraw, re-pose, or invent ASTER pixels.  It scales the user-selected
V3 basis and its matching mask, records fixed body/rifle anchors, and writes
non-overlapping local-retouch masks for controlled future Qwen edits.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "art_src/pilot_v2/aster_v2/visual_basis/ASTER_QWEN_V3_USER_VISUAL_BASIS_LOCK.json"
DEFAULT_OUT = ROOT / "art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1"
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
SIZE = 2048


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require_under_root(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError(f"{label} leaves project: {resolved}") from exc
    return resolved


def exact_green(rgb: np.ndarray, mask: np.ndarray) -> None:
    if rgb.shape != (SIZE, SIZE, 3) or mask.shape != (SIZE, SIZE):
        raise RuntimeError(f"expected {SIZE}×{SIZE} RGB/mask")
    if not np.all((mask == 0) | (mask == 255)):
        raise RuntimeError("canonical mask is not binary")
    if not np.all(rgb[mask == 0] == GREEN):
        raise RuntimeError("canonical source exterior is not exact #00FF00")


def binary_region(name: str, draw: ImageDraw.ImageDraw, shape: list[tuple[int, int]]) -> np.ndarray:
    image = Image.new("L", (SIZE, SIZE), 0)
    local = ImageDraw.Draw(image)
    local.polygon(shape, fill=255)
    return np.asarray(image, dtype=np.uint8)


def region_masks(subject: np.ndarray) -> dict[str, np.ndarray]:
    """Return independent edit regions in lock order with no pixel overlap.

    Shapes follow the fixed V3 composition. They deliberately preserve global
    silhouette/pose; future retouch code must restore all pixels outside its
    one selected region from the canonical working base.
    """
    regions: dict[str, np.ndarray] = {}
    # Head and all ponytail mass.
    regions["face_hair"] = binary_region("face_hair", ImageDraw.Draw(Image.new("L", (SIZE, SIZE))), [
        (760, 55), (1110, 40), (1320, 150), (1450, 460), (1500, 745),
        (1370, 930), (1220, 800), (1120, 690), (1030, 660), (850, 620),
        (700, 500), (690, 260),
    ])
    # Both grip zones plus the whole rifle silhouette; it stays one retouch unit.
    regions["hands_rifle"] = binary_region("hands_rifle", ImageDraw.Draw(Image.new("L", (SIZE, SIZE))), [
        (380, 560), (620, 560), (840, 650), (1100, 780), (1450, 1010),
        (1710, 1110), (1730, 1280), (1510, 1320), (1240, 1120), (980, 1020),
        (730, 950), (470, 820),
    ])
    # Jacket, torso and hip treatment only; intentionally excludes head/rifle/boots.
    regions["torso_garment"] = binary_region("torso_garment", ImageDraw.Draw(Image.new("L", (SIZE, SIZE))), [
        (690, 650), (1210, 610), (1390, 870), (1340, 1440), (1140, 1570),
        (760, 1480), (620, 1170),
    ])
    # Both boot/ankle shells together, excluding shin material that belongs to torso/lower-body lock.
    regions["boots"] = binary_region("boots", ImageDraw.Draw(Image.new("L", (SIZE, SIZE))), [
        (700, 1510), (965, 1510), (1060, 1740), (1010, 1930), (710, 1950),
        (600, 1840), (620, 1660), (1110, 1580), (1300, 1600), (1420, 1840),
        (1340, 1970), (1080, 1970),
    ])

    claimed = np.zeros((SIZE, SIZE), dtype=bool)
    result: dict[str, np.ndarray] = {}
    for name in ("face_hair", "hands_rifle", "torso_garment", "boots"):
        selected = (regions[name] == 255) & (subject == 255) & ~claimed
        result[name] = np.where(selected, 255, 0).astype(np.uint8)
        claimed |= selected
    if any(np.count_nonzero(item) < 128 for item in result.values()):
        raise RuntimeError("a canonical local-retouch region is unexpectedly empty")
    return result


def main() -> int:
    out = require_under_root(DEFAULT_OUT, "output")
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"refusing to overwrite canonical base: {out}")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    source = require_under_root(ROOT / lock["source"]["green_image"], "visual basis")
    source_mask = require_under_root(ROOT / lock["source"]["binary_mask"], "visual basis mask")
    if digest(source) != lock["source"]["green_image_sha256"] or digest(source_mask) != lock["source"]["binary_mask_sha256"]:
        raise RuntimeError("V3 visual-basis SHA lock mismatch")

    rgb_1024 = np.asarray(Image.open(source).convert("RGB"))
    mask_1024 = np.asarray(Image.open(source_mask).convert("L"))
    if rgb_1024.shape != (1024, 1024, 3) or mask_1024.shape != (1024, 1024):
        raise RuntimeError("locked V3 source must be 1024px")
    if not np.all((mask_1024 == 0) | (mask_1024 == 255)) or not np.all(rgb_1024[mask_1024 == 0] == GREEN):
        raise RuntimeError("locked V3 source no longer fulfills green/mask contract")

    # Premultiply before deterministic LANCZOS scale, then reapply the binary
    # source mask. This prevents #00FF00 fringe and does not synthesize detail.
    alpha = mask_1024.astype(np.float32) / 255.0
    premult = rgb_1024.astype(np.float32) * alpha[:, :, None]
    scaled_mask = np.asarray(Image.fromarray(mask_1024).resize((SIZE, SIZE), Image.Resampling.NEAREST))
    scaled_mask = np.where(scaled_mask >= 128, 255, 0).astype(np.uint8)
    scaled_rgb = np.empty((SIZE, SIZE, 3), dtype=np.uint8)
    for channel in range(3):
        scaled_rgb[:, :, channel] = np.asarray(
            Image.fromarray(np.clip(premult[:, :, channel], 0, 255).astype(np.uint8)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        )
    scaled_rgb[scaled_mask == 0] = GREEN
    exact_green(scaled_rgb, scaled_mask)

    ys, xs = np.where(scaled_mask == 255)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    body_height = bbox[3] - bbox[1] + 1
    # Coordinates are V3 composition anchors, doubled from the locked 1024
    # reference. They deliberately lock pose/silhouette rather than claim
    # semantic pose estimation from an AI model.
    anchors = {
        "head_center": [1030, 520],
        "pelvis_center": [1020, 1335],
        "left_foot_contact": [838, 1760],
        "right_foot_contact": [1170, 1875],
        "rifle_butt": [458, 675],
        "rifle_muzzle": [1655, 1190],
        "primary_grip": [794, 944],
        "support_grip": [1040, 1032],
    }
    masks = region_masks(scaled_mask)

    out.mkdir(parents=True)
    working = out / "ASTER_STATIC_MASTER_2048_WORKING_GREEN.png"
    mask_out = out / "ASTER_STATIC_MASTER_2048_WORKING_MASK.png"
    regions_dir = out / "regions"
    regions_dir.mkdir()
    Image.fromarray(scaled_rgb, mode="RGB").save(working)
    Image.fromarray(scaled_mask, mode="L").save(mask_out)
    region_info: dict[str, dict[str, object]] = {}
    for name, mask in masks.items():
        path = regions_dir / f"ASTER_2048_REGION_{name.upper()}_MASK.png"
        Image.fromarray(mask, mode="L").save(path)
        ys_region, xs_region = np.where(mask == 255)
        region_info[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "bbox": [int(xs_region.min()), int(ys_region.min()), int(xs_region.max()), int(ys_region.max())],
            "pixels": int(np.count_nonzero(mask)),
            "rule": "only this mask may differ during its single local retouch; all other pixels must be restored byte-for-byte from the immediately preceding working image",
        }
    manifest = {
        "schema": 1,
        "role": "ASTER 2048 Canonical Static Master V1 working base; no visual gate pass implied",
        "visual_basis": {
            "path": source.relative_to(ROOT).as_posix(),
            "sha256": digest(source),
            "mask": source_mask.relative_to(ROOT).as_posix(),
            "mask_sha256": digest(source_mask),
        },
        "working_rgb": {"path": working.relative_to(ROOT).as_posix(), "sha256": digest(working)},
        "working_mask": {"path": mask_out.relative_to(ROOT).as_posix(), "sha256": digest(mask_out)},
        "resolution": [SIZE, SIZE],
        "source_background": "#00FF00",
        "deterministic_scale_only": True,
        "generated_new_character_pixels": False,
        "body_bbox": bbox,
        "body_height": body_height,
        "anchor_max_drift_pixels": max(1, int(round(body_height * 0.0075))),
        "body_center_max_drift_pixels": max(1, int(round(body_height * 0.005))),
        "anchors": anchors,
        "regions": region_info,
        "global_lock": [
            "no pose or silhouette change", "no head/body proportion change", "no new accessory or costume concept",
            "no global Qwen or Blender redraw", "one region only per future retouch",
        ],
        "status": "CANONICAL_BASE_LOCKED__LOCAL_RETOUCH_NOT_STARTED__USER_VISUAL_GATE_PENDING",
        "runtime_asset": False,
        "animation_source": False,
    }
    manifest_path = out / "ASTER_STATIC_MASTER_2048_V1_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_STATIC_MASTER_2048_V1=" + json.dumps({"working": str(working), "mask": str(mask_out), "manifest": str(manifest_path), "regions": list(region_info)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
