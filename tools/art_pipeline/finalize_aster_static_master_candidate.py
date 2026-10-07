#!/usr/bin/env python3
"""Record one Qwen ASTER candidate and purge only its verified intermediates.

This is intentionally a pre-gate finalizer, not a runtime exporter.  It is
used only after the exact-green matte and preview evidence have succeeded.
``--purge-intermediates`` removes the one candidate's raw Qwen output, copied
guide input, provenance record, and its project-local Comfy workspace; it can
never target a path outside this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(f"{label} must be inside project: {resolved}") from error
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--purge-intermediates", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate = project_path(args.candidate_root, "candidate root")
    guide = project_path(args.guide, "Blender guide")
    source = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_GREEN.png", "green source")
    mask = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_MASK.png", "subject mask")
    qa = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_GREEN_QA.json", "matte QA")
    provenance_path = require_file(candidate / "ASTER_STATIC_MASTER_QWEN_PROVENANCE.json", "Qwen provenance")
    require_file(guide, "Blender guide")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("network_used") is not False or provenance.get("cloud_inference_calls") != 0 or provenance.get("krea2_calls") != 0:
        raise SystemExit("candidate provenance fails the local-only / no-Krea policy")
    models = provenance.get("model_recognition", {})
    if not all(models.get(key) is True for key in ("diffusion", "text_encoder", "vae")):
        raise SystemExit("candidate provenance did not load all approved Qwen components")
    source_image = Image.open(source).convert("RGB")
    mask_image = Image.open(mask).convert("L")
    if source_image.size != mask_image.size:
        raise SystemExit("green source and binary mask dimensions differ")
    qa_data = json.loads(qa.read_text(encoding="utf-8"))
    if qa_data.get("pass") is not True or qa_data.get("exact_green_outside_ratio") != 1.0:
        raise SystemExit("green matte QA has not passed")
    relative_guide = Path(__import__("os").path.relpath(guide, candidate)).as_posix()
    previews = candidate / "previews"
    preview_files = sorted(path.relative_to(candidate).as_posix() for path in previews.glob("*") if path.is_file())
    manifest = {
        "schema": 2,
        "role": "ASTER Static Master pre-gate source candidate only",
        "status": "USER_REVIEW_REQUIRED",
        "final_runtime_eligible": False,
        "green_source": {
            "file": "candidate/ASTER_STATIC_MASTER_QWEN_GREEN.png",
            "resolution": list(source_image.size),
            "pixel_format": "RGB",
            "background_rgb": [0, 255, 0],
            "sha256": sha256(source),
        },
        "binary_subject_mask": {
            "file": "candidate/ASTER_STATIC_MASTER_QWEN_MASK.png",
            "sha256": sha256(mask),
            "source_coverage": qa_data.get("subject_coverage"),
            "largest_component_ratio": qa_data.get("mask_metrics", {}).get("largest_component_ratio"),
        },
        "matte_qa": {
            "file": "candidate/ASTER_STATIC_MASTER_QWEN_GREEN_QA.json",
            "sha256": sha256(qa),
            "exact_green_outside_ratio": qa_data.get("exact_green_outside_ratio"),
            "opaque_green_pixels": 0,
        },
        "source_control": {
            "file": relative_guide,
            "role": "Blender full-mass camera/pose/grip guide only; never final character art",
            "sha256": sha256(guide),
        },
        "generation": {
            "tool": "local Qwen Image Edit 2511",
            "diffusion": "qwen_image_edit_2511_int8_convrot.safetensors",
            "text_encoder": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "vae": "qwen_image_vae.safetensors",
            "seed": provenance.get("seed"),
            "steps": provenance.get("steps"),
            "cloud_inference_calls": 0,
            "krea2_calls": 0,
            "external_model_roots_read_only": ["C:\\AI_MODELS", "C:\\AI_ENVS"],
        },
        "review_evidence": preview_files,
        "next_gate": "User visual review. On rejection, delete this complete candidate directory before another attempt.",
    }
    destination = candidate / "ASTER_STATIC_MASTER_SOURCE_MANIFEST.json"
    destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.purge_intermediates:
        paths = [
            candidate / "candidate/ASTER_STATIC_MASTER_QWEN_RAW.png",
            candidate / "inputs",
            provenance_path,
            candidate / "_comfy_workspace",
        ]
        for path in paths:
            checked = project_path(path, "intermediate cleanup target")
            if checked.is_dir():
                shutil.rmtree(checked)
            elif checked.is_file():
                checked.unlink()
    print("ASTER_STATIC_MASTER_CANDIDATE_FINALIZED=" + json.dumps({"candidate": str(candidate), "purged": args.purge_intermediates}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
