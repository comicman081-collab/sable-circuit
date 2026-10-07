#!/usr/bin/env python3
"""Extract a separate ASTER muzzle-flash sprite from retained E/VFX evidence.

The operator direction masters stay clean aim poses.  This tiny green/mask
pair is a *runtime VFX source* derived only from the already-authorized E
fire test and is never composited into an aim master.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
FIRE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire"
FLASH = FIRE_ROOT / "ASTER_FIRE_E_IMAGEGEN_V2_MUZZLE_GREEN.png"
AIM = FIRE_ROOT / "ASTER_FIRE_E_IMAGEGEN_V1_GREEN.png"
OUT = ROOT / "art_src/pilot_v2/aster_v2/vfx/muzzle_flash_e_imagegen_v1"
CROP = (1090, 355, 1254, 490)
GREEN = np.asarray((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if OUT.exists():
        raise SystemExit("refusing to overwrite existing muzzle VFX source")
    if not FLASH.is_file() or not AIM.is_file():
        raise SystemExit("retained E muzzle test or clean E aim master is unavailable")
    flash = np.asarray(Image.open(FLASH).convert("RGB"), dtype=np.int16)
    aim = np.asarray(Image.open(AIM).convert("RGB"), dtype=np.int16)
    x0, y0, x1, y1 = CROP
    delta = np.max(np.abs(flash - aim), axis=2)
    # Restrict to the known muzzle region.  The threshold retains the warm
    # core/petals/sparks while rejecting tiny ImageGen compression changes.
    alpha = (delta[y0:y1, x0:x1] >= 40)
    alpha[:24, :] = False  # keep the rifle body itself out of the VFX plate
    alpha[:, :18] = False
    if not 0.015 < float(alpha.mean()) < 0.60:
        raise SystemExit(f"muzzle VFX extraction coverage invalid: {float(alpha.mean()):.6f}")
    rgb = flash[y0:y1, x0:x1].astype(np.uint8).copy()
    rgb[~alpha] = GREEN
    OUT.mkdir(parents=True)
    source = OUT / "ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_GREEN.png"
    mask = OUT / "ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_MASK.png"
    Image.fromarray(rgb, mode="RGB").save(source)
    Image.fromarray((alpha.astype(np.uint8) * 255), mode="L").save(mask)
    report = {
        "schema": 1,
        "role": "ASTER separated muzzle VFX source; not character body art",
        "source_background": "#00FF00",
        "source_test": FLASH.relative_to(ROOT).as_posix(),
        "clean_aim_comparison": AIM.relative_to(ROOT).as_posix(),
        "crop_xyxy": list(CROP),
        "muzzle_anchor_in_crop_xy": [1128 - x0, 415 - y0],
        "resolution": [x1 - x0, y1 - y0],
        "coverage": float(alpha.mean()),
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source),
        "mask": mask.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(mask),
        "embedded_in_aim_masters": False,
        "usage_policy": "render only on muzzle_contact and recoil_peak; rotate with aim direction",
        "krea2_used": False,
        "network_used": False,
    }
    (OUT / "ASTER_MUZZLE_FLASH_E_IMAGEGEN_V1_MANIFEST.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_MUZZLE_VFX_SPRITE_PASS=" + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
