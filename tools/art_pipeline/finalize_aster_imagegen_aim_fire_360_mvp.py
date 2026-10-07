#!/usr/bin/env python3
"""Normalize the headless Blender FIRE-360 MVP into green/mask source pairs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: Path) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"path must remain in project: {resolved}") from error
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args()
    candidate = project_path(args.candidate)
    manifest_path = candidate / "ASTER_IMAGEGEN_AIM_FIRE_360_MOTION_MVP_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("MVP manifest unavailable")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("muzzle_vfx", {}).get("embedded_in_source") is not False:
        raise SystemExit("invalid source: muzzle VFX must remain separate from aim masters")
    source_root, mask_root, qa_root = candidate / "source", candidate / "masks", candidate / "qa"
    if any(path.exists() for path in (source_root, mask_root, qa_root)):
        raise SystemExit("refusing to overwrite existing FIRE-360 finalization")
    finalizer = ROOT / "tools/art_pipeline/apply_green_matte.py"
    segmenter = Path(r"C:\AI_MODELS\auto-mask")
    if not finalizer.is_file() or not segmenter.is_dir():
        raise SystemExit("green-matte tool or read-only local segmenter unavailable")
    records = []
    for index, raw in enumerate(manifest.get("raw_renders", [])):
        direction, key = raw["direction"], raw["key"]
        raw_path = project_path(Path(raw["file"]))
        stem = f"ASTER_FIRE_{direction}_{key.upper()}"
        source = source_root / direction / f"{stem}_GREEN.png"
        mask = mask_root / direction / f"{stem}_MASK.png"
        qa = qa_root / direction / f"{stem}_QA.json"
        command = [
            str(sys.executable), str(finalizer), "aster", "--input", str(raw_path),
            "--output", str(source), "--mask", str(mask), "--qa", str(qa),
            "--seed", str(251300 + index), "--segmenter", str(segmenter), "--matte-method", "edge-chroma",
        ]
        if subprocess.run(command, cwd=ROOT, check=False).returncode:
            raise SystemExit(f"green/mask finalization failed: {direction}/{key}")
        report = json.loads(qa.read_text(encoding="utf-8"))
        records.append({
            "direction": direction, "key": key, "muzzle_vfx_visible": raw["muzzle_vfx_visible"],
            "raw": raw["file"], "source": source.relative_to(ROOT).as_posix(),
            "mask": mask.relative_to(ROOT).as_posix(), "qa": qa.relative_to(ROOT).as_posix(),
            "exact_green_outside_ratio": report["exact_green_outside_ratio"],
        })
    output = {
        "schema": 1,
        "role": "ASTER 8-direction Fire MVP exact-green/mask source pairs; non-runtime",
        "candidate_manifest": manifest_path.relative_to(ROOT).as_posix(),
        "source_background": "#00FF00",
        "frame_count": len(records),
        "directions": manifest["directions"],
        "keys": manifest["keys"],
        "muzzle_vfx_visible_only_on": ["muzzle_contact", "recoil_peak"],
        "records": records,
        "runtime_status": "NOT_CONNECTED_PENDING_VISUAL_AND_MOTION_REVIEW",
        "krea2_used": False,
        "network_used": False,
    }
    output_path = candidate / "ASTER_IMAGEGEN_AIM_FIRE_360_MOTION_MVP_GREEN_MASK_MANIFEST.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_IMAGEGEN_AIM_FIRE_360_FINALIZE_PASS=" + json.dumps({"frames": len(records), "manifest": output_path.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
