#!/usr/bin/env python3
"""Finalize ASTER's no-VFX eight-direction aim masters non-destructively.

The previous direction set was authored as firing stills.  These v2 records
make the required separation explicit: body/weapon artwork is always a clean
aim pose; muzzle light belongs to a later runtime VFX layer only.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
FIRE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/directional_masters/imagegen_v1/fire"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def raw_input(direction: str) -> Path:
    # E v1 was the original clean aim pose.  The other seven v1 masters had
    # baked firing light and are deliberately superseded by narrowly edited
    # v2 aim poses.  The E muzzle-flash v2 remains evidence only.
    if direction == "E":
        return FIRE_ROOT / "ASTER_FIRE_E_IMAGEGEN_V1_GREEN.png"
    return FIRE_ROOT / f"ASTER_FIRE_{direction}_IMAGEGEN_V2_AIM_GREEN.png"


def main() -> int:
    output_root = FIRE_ROOT / "aim_master_v2"
    source_root, mask_root, qa_root = output_root / "source", output_root / "masks", output_root / "qa"
    manifest_path = output_root / "ASTER_IMAGEGEN_V2_AIM_DIRECTION_MASTER_MANIFEST.json"
    if manifest_path.exists() or output_root.exists():
        raise SystemExit("refusing to overwrite existing v2 aim-master finalization")

    finalizer = ROOT / "tools/art_pipeline/apply_green_matte.py"
    segmenter = Path(r"C:\AI_MODELS\auto-mask")
    if not finalizer.is_file() or not segmenter.is_dir():
        raise SystemExit("green-matte script or read-only local segmenter unavailable")

    source_root.mkdir(parents=True)
    mask_root.mkdir()
    qa_root.mkdir()
    records: list[dict[str, object]] = []
    for index, direction in enumerate(DIRECTIONS):
        source_input = raw_input(direction)
        if not source_input.is_file():
            raise SystemExit(f"missing no-VFX direction source: {source_input}")
        source = source_root / f"ASTER_FIRE_{direction}_DIRECTION_AIM_MASTER_V2_GREEN.png"
        mask = mask_root / f"ASTER_FIRE_{direction}_DIRECTION_AIM_MASTER_V2_MASK.png"
        qa = qa_root / f"ASTER_FIRE_{direction}_DIRECTION_AIM_MASTER_V2_QA.json"
        command = [
            str(sys.executable), str(finalizer), "aster", "--input", str(source_input),
            "--output", str(source), "--mask", str(mask), "--qa", str(qa),
            "--seed", str(251220 + index), "--segmenter", str(segmenter), "--matte-method", "edge-chroma",
        ]
        if subprocess.run(command, cwd=ROOT, check=False).returncode:
            raise SystemExit(f"exact-green/mask finalization failed for {direction}")
        image = Image.open(source).convert("RGB")
        records.append({
            "direction": direction,
            "raw_authoring_input": source_input.relative_to(ROOT).as_posix(),
            "raw_authoring_input_sha256": sha256(source_input),
            "source_green": source.relative_to(ROOT).as_posix(),
            "source_green_sha256": sha256(source),
            "mask": mask.relative_to(ROOT).as_posix(),
            "mask_sha256": sha256(mask),
            "qa": qa.relative_to(ROOT).as_posix(),
            "resolution": list(image.size),
        })

    manifest = {
        "schema": 1,
        "role": "ASTER eight-direction clean aim masters; source-authoring only",
        "directions": list(DIRECTIONS),
        "direction_count": len(DIRECTIONS),
        "state": "aim_baseline_for_fire_360",
        "source_background": "#00FF00",
        "muzzle_vfx_embedded_in_source": False,
        "muzzle_vfx_policy": "Blender/runtime VFX layer visible only on fire keyframes muzzle_contact and recoil_peak.",
        "generation_tool": "OpenAI ImageGen built-in tool; explicitly authorized by user for this directional-source task",
        "krea2_used": False,
        "cloud_generation": True,
        "runtime_asset": False,
        "visual_gate": "USER_REVIEW_REQUIRED",
        "records": records,
        "retained_prior_versions": {
            "v1_fire_masters": "retained; baked-VFX source reference only, not promoted",
            "e_v2_muzzle_test": "retained; separate transient-VFX authoring evidence, not an aim master",
        },
        "next": "Blender headless fire-360 render with a separate keyed muzzle VFX object.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_V2_AIM_DIRECTION_FINALIZE_PASS=" + json.dumps({"records": len(records), "manifest": manifest_path.relative_to(ROOT).as_posix(), "krea2_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
