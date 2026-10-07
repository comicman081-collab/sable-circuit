#!/usr/bin/env python3
"""Align ImageGen walk-pose sources to one stable body anchor.

The input images are immutable ImageGen masters.  This tool only creates
project-local derived cutout sources: it crops the reviewed subject matte,
uniformly scales it to the neutral-master height, and pins the subject bottom
and horizontal centre to the neutral frame.  No pixels are painted or
regenerated; the result is consumed by the Blender+UAL pose-switch renderer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask > 0)
    if len(xs) < 6000:
        raise SystemExit("walk source matte has an implausibly small subject")
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def load_pair(rgb_path: Path, mask_path: Path) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(Image.open(rgb_path).convert("RGB"), dtype=np.uint8)
    mask = np.asarray(Image.open(mask_path).convert("L"), dtype=np.uint8)
    if rgb.shape[:2] != mask.shape:
        raise SystemExit(f"source/mask dimensions differ: {rgb_path} {mask_path}")
    if rgb.shape[:2] != (1536, 1024):
        raise SystemExit(f"walk source must be 1024x1536: {rgb_path} {rgb.shape[::-1]}")
    if not np.all(rgb[0, 0] == GREEN):
        raise SystemExit(f"walk source does not have exact-green corner: {rgb_path}")
    return rgb, mask


def align_pair(
    rgb: np.ndarray,
    mask: np.ndarray,
    source_box: tuple[int, int, int, int],
    target_box: tuple[int, int, int, int],
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    sx0, sy0, sx1, sy1 = source_box
    tx0, ty0, tx1, ty1 = target_box
    source_h = sy1 - sy0
    target_h = ty1 - ty0
    scale = float(target_h) / float(source_h)
    crop_rgb = rgb[sy0:sy1, sx0:sx1]
    crop_mask = mask[sy0:sy1, sx0:sx1]
    out_w = max(1, int(round(crop_rgb.shape[1] * scale)))
    out_h = max(1, int(round(crop_rgb.shape[0] * scale)))
    resized_rgb = np.asarray(
        Image.fromarray(crop_rgb, mode="RGB").resize((out_w, out_h), Image.Resampling.LANCZOS),
        dtype=np.uint8,
    )
    resized_mask = np.asarray(
        Image.fromarray(crop_mask, mode="L").resize((out_w, out_h), Image.Resampling.NEAREST),
        dtype=np.uint8,
    )
    target_cx = (tx0 + tx1) / 2.0
    paste_x = int(round(target_cx - out_w / 2.0))
    paste_y = int(round(ty1 - out_h))
    if paste_x < 0 or paste_y < 0 or paste_x + out_w > 1024 or paste_y + out_h > 1536:
        raise SystemExit(f"aligned subject would leave the 1024x1536 canvas: {source_box} -> {target_box}")
    out_rgb = np.broadcast_to(GREEN, (1536, 1024, 3)).copy()
    out_mask = np.zeros((1536, 1024), dtype=np.uint8)
    out_rgb[paste_y : paste_y + out_h, paste_x : paste_x + out_w] = resized_rgb
    out_mask[paste_y : paste_y + out_h, paste_x : paste_x + out_w] = resized_mask
    out_rgb[out_mask == 0] = GREEN
    final_box = bbox(out_mask)
    return out_rgb, out_mask, {
        "source_bbox": list(source_box),
        "target_bbox": list(target_box),
        "output_bbox": list(final_box),
        "uniform_scale": round(scale, 8),
        "canvas_resolution": [1024, 1536],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--neutral-rgb", type=Path, required=True)
    parser.add_argument("--neutral-mask", type=Path, required=True)
    parser.add_argument("--pose-a-rgb", type=Path, required=True)
    parser.add_argument("--pose-a-mask", type=Path, required=True)
    parser.add_argument("--pose-b-rgb", type=Path, required=True)
    parser.add_argument("--pose-b-mask", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    inputs = {
        "neutral": (project_path(args.neutral_rgb, "neutral-rgb"), project_path(args.neutral_mask, "neutral-mask")),
        "pose_a": (project_path(args.pose_a_rgb, "pose-a-rgb"), project_path(args.pose_a_mask, "pose-a-mask")),
        "pose_b": (project_path(args.pose_b_rgb, "pose-b-rgb"), project_path(args.pose_b_mask, "pose-b-mask")),
    }
    output_dir = project_path(args.output_dir, "output-dir")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty pose-source directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for name, (rgb_path, mask_path) in inputs.items():
        if not rgb_path.is_file() or not mask_path.is_file():
            raise SystemExit(f"missing {name} walk source: {rgb_path} / {mask_path}")
        rgb, mask = load_pair(rgb_path, mask_path)
        loaded[name] = (rgb, mask)
        boxes[name] = bbox(mask)

    target = boxes["neutral"]
    output_rows: dict[str, dict[str, object]] = {}
    for name, (rgb, mask) in loaded.items():
        aligned_rgb, aligned_mask, alignment = align_pair(rgb, mask, boxes[name], target)
        rgb_out = output_dir / f"{name}_green.png"
        mask_out = output_dir / f"{name}_mask.png"
        Image.fromarray(aligned_rgb, mode="RGB").save(rgb_out)
        Image.fromarray(aligned_mask, mode="L").save(mask_out)
        output_rows[name] = {
            "input_rgb": inputs[name][0].relative_to(ROOT).as_posix(),
            "input_rgb_sha256": sha256(inputs[name][0]),
            "input_mask": inputs[name][1].relative_to(ROOT).as_posix(),
            "input_mask_sha256": sha256(inputs[name][1]),
            "output_rgb": rgb_out.relative_to(ROOT).as_posix(),
            "output_rgb_sha256": sha256(rgb_out),
            "output_mask": mask_out.relative_to(ROOT).as_posix(),
            "output_mask_sha256": sha256(mask_out),
            "alignment": alignment,
            "subject_pixels": int((aligned_mask > 0).sum()),
            "exact_green_corners": [aligned_rgb[y, x].tolist() for y, x in ((0, 0), (0, 1023), (1535, 0), (1535, 1023))],
        }
    qa = {
        "schema": 1,
        "role": "Project-local derived ImageGen walk-pose source alignment",
        "source_art_modified": False,
        "operation": "immutable subject matte crop, uniform height normalization, neutral bottom/centre anchor",
        "neutral_target_bbox": list(target),
        "inputs": output_rows,
        "pass": all(row["exact_green_corners"] == [[0, 255, 0]] * 4 for row in output_rows.values()),
    }
    qa_path = output_dir / "WALK_POSE_SOURCE_ALIGNMENT_QA.json"
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not qa["pass"]:
        raise SystemExit(f"walk source alignment QA failed: {qa}")
    print("WALK_POSE_SOURCE_ALIGNMENT_PASS=" + json.dumps({"output_dir": output_dir.relative_to(ROOT).as_posix(), "qa": qa_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
