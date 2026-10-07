#!/usr/bin/env python3
"""Normalize one Blender 2.5D proof into green source images and paired masks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ("ready", "inhale", "micro_weight_shift", "return")


def project_path(value: Path, label: str) -> Path:
    result = value.resolve()
    try:
        result.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"{label} must remain in project: {result}") from error
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof", required=True, type=Path)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--segmenter", required=True, type=Path)
    args = parser.parse_args()
    proof = project_path(args.proof, "proof")
    raw_dir, source_dir, mask_dir, qa_dir = proof / "raw", proof / "source", proof / "masks", proof / "qa"
    manifest_path = proof / "ASTER_2P5D_IDLE_E_MAPPING_PROOF_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"missing proof manifest: {manifest_path}")
    if any(path.exists() for path in (source_dir, mask_dir, qa_dir)):
        raise SystemExit("refusing to overwrite existing finalized proof")
    if not args.segmenter.resolve().is_dir():
        raise SystemExit("read-only local auto-mask source unavailable")
    finalizer = ROOT / "tools/art_pipeline/apply_green_matte.py"
    source_dir.mkdir()
    mask_dir.mkdir()
    qa_dir.mkdir()
    records = []
    for index, key in enumerate(EXPECTED):
        stem = f"ASTER_IDLE_E_{key.upper()}_2P5D"
        raw = raw_dir / f"{stem}_RAW.png"
        if not raw.is_file():
            raise SystemExit(f"missing expected raw proof render: {raw}")
        output = source_dir / f"{stem}_GREEN.png"
        mask = mask_dir / f"{stem}_MASK.png"
        qa = qa_dir / f"{stem}_GREEN_QA.json"
        command = [str(sys.executable), str(finalizer), "aster", "--input", str(raw), "--output", str(output), "--mask", str(mask), "--qa", str(qa), "--seed", str(args.seed + index), "--segmenter", str(args.segmenter.resolve()), "--matte-method", "edge-chroma"]
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode:
            raise SystemExit(f"green/mask finalization failed for {key}: {completed.returncode}")
        records.append({"key": key, "raw": raw.relative_to(ROOT).as_posix(), "green": output.relative_to(ROOT).as_posix(), "mask": mask.relative_to(ROOT).as_posix(), "qa": qa.relative_to(ROOT).as_posix()})
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_background"] = "#00FF00"
    manifest["finalized_source_pairs"] = records
    manifest["source_finalization"] = {"method": "local edge-chroma exact-green normalization", "cloud_inference_calls": 0, "krea2_calls": 0, "runtime_asset": False}
    manifest["next"] = "visual review of source-art mapping before any other direction/state or runtime export"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_2P5D_MAPPING_FINALIZE_PASS=" + json.dumps({"proof": proof.relative_to(ROOT).as_posix(), "source_pairs": len(records), "cloud_calls": 0, "krea2_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
