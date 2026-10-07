#!/usr/bin/env python3
"""Finalize user-authorized ImageGen ASTER fire direction masters.

The input files are kept intact as generation evidence.  This produces new
exact-green source files and paired binary masks without altering the inputs.
It does not claim that these 8 static masters are animation frames or runtime
assets; the next gate is a human contact-sheet review.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ROOT_DIR = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    source, masks, qa = ROOT_DIR / "source", ROOT_DIR / "masks", ROOT_DIR / "qa"
    manifest_path = ROOT_DIR / "ASTER_IMAGEGEN_V1_FIRE_DIRECTION_MASTER_MANIFEST.json"
    if manifest_path.exists() or any(path.exists() for path in (source, masks, qa)):
        raise SystemExit("refusing to overwrite ImageGen direction-master finalization")
    finalizer = ROOT / "tools/art_pipeline/apply_green_matte.py"
    segmenter = Path(r"C:\AI_MODELS\auto-mask")
    if not finalizer.is_file() or not segmenter.is_dir():
        raise SystemExit("local green-matte tool or read-only segmenter unavailable")
    source.mkdir(); masks.mkdir(); qa.mkdir()
    records = []
    for index, direction in enumerate(DIRECTIONS):
        original = ROOT_DIR / f"ASTER_FIRE_{direction}_IMAGEGEN_V1_GREEN.png"
        if not original.is_file():
            raise SystemExit(f"missing ImageGen directional master: {original}")
        output = source / f"ASTER_FIRE_{direction}_DIRECTION_MASTER_V1_GREEN.png"
        mask = masks / f"ASTER_FIRE_{direction}_DIRECTION_MASTER_V1_MASK.png"
        report = qa / f"ASTER_FIRE_{direction}_DIRECTION_MASTER_V1_GREEN_QA.json"
        command = [str(sys.executable), str(finalizer), "aster", "--input", str(original), "--output", str(output), "--mask", str(mask), "--qa", str(report), "--seed", str(251180 + index), "--segmenter", str(segmenter), "--matte-method", "edge-chroma"]
        if subprocess.run(command, cwd=ROOT, check=False).returncode:
            raise SystemExit(f"exact-green/mask finalization failed for {direction}")
        image = Image.open(output).convert("RGB")
        records.append({
            "direction": direction,
            "original": original.relative_to(ROOT).as_posix(),
            "original_sha256": sha256(original),
            "source_green": output.relative_to(ROOT).as_posix(),
            "source_green_sha256": sha256(output),
            "mask": mask.relative_to(ROOT).as_posix(),
            "mask_sha256": sha256(mask),
            "qa": report.relative_to(ROOT).as_posix(),
            "resolution": list(image.size),
        })
    manifest = {
        "schema": 1,
        "role": "ASTER ImageGen v1 eight-direction fire static master set; source-authoring only",
        "directions": list(DIRECTIONS),
        "direction_count": len(DIRECTIONS),
        "state": "fire_static_master",
        "source_background": "#00FF00",
        "generation_tool": "OpenAI ImageGen built-in tool; explicitly authorized by user for this directional-source task",
        "krea2_used": False,
        "cloud_generation": True,
        "runtime_asset": False,
        "visual_gate": "USER_REVIEW_REQUIRED",
        "records": records,
        "prohibitions": ["no runtime export", "no animation expansion until directional visual review", "no replacement of user-approved original static master"],
        "next": "build and inspect eight-direction contact sheet; then decide source-master promotion or retain/reject",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_V1_FIRE_DIRECTION_FINALIZE_PASS=" + json.dumps({"records": len(records), "manifest": manifest_path.relative_to(ROOT).as_posix(), "krea2_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
