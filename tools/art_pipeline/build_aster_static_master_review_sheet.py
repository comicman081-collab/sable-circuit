#!/usr/bin/env python3
"""Build the deterministic before/after review sheet for the ASTER static chain.

This creates a review-only image.  It does not promote either image to a
runtime asset or modify the locked canonical source.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "art_src/pilot_v2/aster_v2/static_master/canonical_2048_v1"
BASE = CANONICAL / "ASTER_STATIC_MASTER_2048_WORKING_GREEN.png"
FINAL = CANONICAL / "retouch_candidates/torso_garment_v1_seed251142/candidate/ASTER_STATIC_MASTER_2048_TORSO_GARMENT_PATCH_GREEN.png"
OUT = CANONICAL / "reviews"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not BASE.is_file() or not FINAL.is_file():
        raise SystemExit("Canonical base or retained static-chain candidate is missing")
    before = Image.open(BASE).convert("RGB")
    after = Image.open(FINAL).convert("RGB")
    if before.size != (2048, 2048) or after.size != (2048, 2048):
        raise SystemExit("Review inputs must both be 2048x2048")
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (4120, 2088), (0, 255, 0))
    sheet.paste(before, (8, 32))
    sheet.paste(after, (2064, 32))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((2048, 0, 2071, 2087), fill=(0, 0, 0))
    draw.text((8, 8), "CANONICAL V3-DERIVED BASE / NOT FINAL", fill=(0, 0, 0))
    draw.text((2064, 8), "CONTROLLED PATCH CHAIN / USER REVIEW REQUIRED", fill=(0, 0, 0))
    output = OUT / "ASTER_STATIC_MASTER_CHAIN_REVIEW_GREEN.png"
    sheet.save(output)
    manifest = {
        "role": "ASTER Static Master visual review sheet only; not runtime or approval",
        "left": {"path": BASE.relative_to(ROOT).as_posix(), "sha256": sha256(BASE)},
        "right": {"path": FINAL.relative_to(ROOT).as_posix(), "sha256": sha256(FINAL)},
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": sha256(output),
        "resolution": list(sheet.size),
        "source_background": "#00FF00",
        "static_visual_gate": "USER_REVIEW_REQUIRED",
        "runtime_asset": False,
    }
    (OUT / "ASTER_STATIC_MASTER_CHAIN_REVIEW.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
