#!/usr/bin/env python3
"""Validate one ASTER Static Master source candidate without promoting it.

This validator deliberately has no visual-quality heuristic.  It proves the
repeatable technical contract only: project-local outputs, exact ``#00FF00``
exterior, a binary subject mask, local-Qwen provenance, and review-only
evidence.  The output status is always ``USER_REVIEW_REQUIRED``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE = ROOT / "art_src/pilot_v2/aster_v2/qwen_edits/qwen_static_master_fullmass_v3_seed251114"
GREEN = np.array([0, 255, 0], dtype=np.uint8)


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
    parser.add_argument("--candidate-root", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate = project_path(args.candidate_root, "candidate root")
    output = project_path(args.output or candidate / "PIPELINE_VALIDATION.json", "validation output")
    source = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_GREEN.png", "green source")
    mask_file = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_MASK.png", "subject mask")
    qa_file = require_file(candidate / "candidate/ASTER_STATIC_MASTER_QWEN_GREEN_QA.json", "matte QA")
    manifest_file = require_file(candidate / "ASTER_STATIC_MASTER_SOURCE_MANIFEST.json", "source manifest")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    qa = json.loads(qa_file.read_text(encoding="utf-8"))
    if manifest.get("status") != "USER_REVIEW_REQUIRED":
        raise SystemExit("candidate status must remain USER_REVIEW_REQUIRED before a human visual decision")
    if manifest.get("final_runtime_eligible") is not False:
        raise SystemExit("a static candidate cannot be runtime eligible")
    generation = manifest.get("generation", {})
    approved_models = {
        "diffusion": "qwen_image_edit_2511_int8_convrot.safetensors",
        "text_encoder": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
        "vae": "qwen_image_vae.safetensors",
    }
    if {key: generation.get(key) for key in approved_models} != approved_models:
        raise SystemExit("candidate does not declare the approved Qwen 2511 base model set")
    if generation.get("cloud_inference_calls") != 0 or generation.get("krea2_calls") != 0:
        raise SystemExit("cloud or Krea usage is prohibited")
    roots = generation.get("external_model_roots_read_only", [])
    if any("krea" in str(item).lower() for item in roots):
        raise SystemExit("Krea must not appear in candidate model roots")

    source_image = Image.open(source).convert("RGB")
    mask_image = Image.open(mask_file).convert("L")
    if source_image.size != mask_image.size or source_image.size != (1024, 1024):
        raise SystemExit(f"source/mask dimensions must be matching 1024x1024: {source_image.size}, {mask_image.size}")
    pixels = np.asarray(source_image)
    mask = np.asarray(mask_image)
    values = set(np.unique(mask).tolist())
    if not values.issubset({0, 255}) or values == {0} or values == {255}:
        raise SystemExit(f"mask must be non-empty binary 0/255: {sorted(values)}")
    subject = mask == 255
    exterior = ~subject
    exact_green_outside = float(np.all(pixels[exterior] == GREEN, axis=1).mean())
    opaque_green = int(np.all(pixels[subject] == GREEN, axis=1).sum())
    if exact_green_outside != 1.0 or opaque_green != 0:
        raise SystemExit(f"exact green contract failed: exterior={exact_green_outside}, subject_green={opaque_green}")
    if qa.get("pass") is not True or qa.get("exact_green_outside_ratio") != 1.0:
        raise SystemExit("matte QA record does not prove the green contract")
    if sha256(source) != manifest.get("green_source", {}).get("sha256"):
        raise SystemExit("green source SHA-256 differs from manifest")
    if sha256(mask_file) != manifest.get("binary_subject_mask", {}).get("sha256"):
        raise SystemExit("mask SHA-256 differs from manifest")

    source_control = manifest.get("source_control", {})
    guide_value = source_control.get("file")
    if not guide_value:
        raise SystemExit("source-control guide is not recorded")
    guide = project_path(candidate / guide_value, "source-control guide")
    require_file(guide, "source-control guide")
    if sha256(guide) != source_control.get("sha256"):
        raise SystemExit("source-control guide SHA-256 differs from manifest")

    previews = candidate / "previews"
    review_files = {
        "image_a_mockup": list(previews.glob("*_IMAGE_A_SCALE_MOCKUP_NOT_RUNTIME.png")),
        "gameplay_scale": list(previews.glob("*_GAMEPLAY_SCALE_GREEN.png")),
        "preview_manifest": list(previews.glob("*_PREVIEW_MANIFEST.json")),
    }
    if any(len(files) != 1 for files in review_files.values()):
        raise SystemExit("candidate needs exactly one review-only Image A mockup, gameplay-scale preview, and preview manifest")

    result = {
        "schema": 1,
        "pass": True,
        "candidate_root": candidate.as_posix(),
        "technical_contract": {
            "outputs_project_local": True,
            "external_model_roots_read_only": roots,
            "krea2_calls": 0,
            "cloud_inference_calls": 0,
            "source_resolution": list(source_image.size),
            "green_rgb": GREEN.tolist(),
            "exact_green_outside_ratio": exact_green_outside,
            "opaque_green_subject_pixels": opaque_green,
            "source_coverage": float(subject.mean()),
        },
        "evidence": {key: files[0].relative_to(candidate).as_posix() for key, files in review_files.items()},
        "gate": "USER_REVIEW_REQUIRED",
        "runtime_or_animation_promotion": "HOLD",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ASTER_STATIC_MASTER_PIPELINE_VALID=" + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
