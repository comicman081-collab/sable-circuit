#!/usr/bin/env python3
"""Apply an exact ``#00FF00`` matte without amputating generated artwork.

For Qwen authoring candidates the requested green backdrop is already present
as one green-dominant RGB field, but Qwen may alter its exact numeric value.
An edge/chroma extraction is therefore the primary matte path: it preserves
every non-background pixel before changing only the detected backdrop.  The
older text-prompted SAM2 path remains available for images that have no
controlled green backdrop, but it is never silently used for SABLE Qwen
frames because semantic segmentation can remove arms, torso, or weapon parts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_img2img_green import GREEN, segment_unit
from generate_sdxl_pilot import PROMPTS
from project_paths import local_model_path, require_project_output_path


def validate_unit_mask(mask_array: np.ndarray, unit: str) -> dict[str, object]:
    binary = mask_array.astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    if count <= 1:
        raise RuntimeError("SUBJECT_MASK_FAIL no connected component")
    areas = stats[1:, cv2.CC_STAT_AREA]
    label = int(np.argmax(areas)) + 1
    x, y, width, height, area = (int(value) for value in stats[label])
    coverage = float(mask_array.mean())
    component_ratio = float(area) / float(max(1, mask_array.sum()))
    touches = {
        "left": x <= 3,
        "top": y <= 3,
        "right": x + width >= mask_array.shape[1] - 3,
        "bottom": y + height >= mask_array.shape[0] - 3,
    }
    if component_ratio < 0.88:
        raise RuntimeError(f"SUBJECT_MASK_FAIL fragmented={component_ratio:.4f}")
    if sum(touches.values()) >= 2:
        raise RuntimeError(f"SUBJECT_MASK_FAIL background-leak edges={touches}")
    if unit != "recon_drone" and not (0.42 <= height / mask_array.shape[0] <= 0.98):
        raise RuntimeError(f"SUBJECT_MASK_FAIL human-height={height / mask_array.shape[0]:.4f}")
    return {
        "coverage": coverage,
        "largest_component_ratio": component_ratio,
        "bbox_xywh": [x, y, width, height],
        "touches_frame": touches,
    }


def chroma_background_mask(rgb: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    """Return the source's controlled green backdrop, never a semantic guess.

    A robust edge median anchors the expected backdrop color.  We then keep
    only pixels that are both near that color and strongly green-dominant.
    This removes Qwen's non-exact green exterior while retaining the full
    operator silhouette, including dark fabric, pale skin, and cyan details.
    Isolated matching holes in a weapon remain background too, which is the
    intended alpha result for a true through-hole.
    """
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise RuntimeError(f"Expected RGB image for chroma matte, got {rgb.shape}")
    height, width, _ = rgb.shape
    edges = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]), axis=0).astype(np.int16)
    median = np.median(edges, axis=0)
    dominance = median[1] - max(median[0], median[2])
    if dominance < 35:
        raise RuntimeError(f"CHROMA_MATTE_FAIL edge backdrop is not green-dominant: {median.tolist()}")
    values = rgb.astype(np.int16)
    near = np.max(np.abs(values - median.astype(np.int16)), axis=2) <= 24
    green_dominant = (values[:, :, 1] >= values[:, :, 0] + 35) & (values[:, :, 1] >= values[:, :, 2] + 35)
    background = near & green_dominant
    if float(background.mean()) < 0.10:
        raise RuntimeError(f"CHROMA_MATTE_FAIL insufficient controlled backdrop={background.mean():.6f}")
    return background, {
        "method": "edge-median controlled chroma background extraction",
        "edge_median_rgb": [int(value) for value in median],
        "edge_green_dominance": int(dominance),
        "background_coverage": float(background.mean()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", choices=sorted(PROMPTS))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--segmenter", type=Path, default=local_model_path("auto-mask"))
    parser.add_argument(
        "--matte-method",
        choices=("edge-chroma", "sam2"),
        default="edge-chroma",
        help="Use edge-chroma for controlled Qwen green backdrops; SAM2 is explicit fallback only.",
    )
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "matte output")
    args.mask = require_project_output_path(args.mask, "matte mask")
    args.qa = require_project_output_path(args.qa, "matte QA")
    if not args.input.is_file():
        raise SystemExit(f"input candidate is unavailable: {args.input}")

    image = Image.open(args.input).convert("RGB")
    raw_rgb = np.asarray(image)
    if args.matte_method == "edge-chroma":
        background_array, matte_details = chroma_background_mask(raw_rgb)
        mask_array = ~background_array
        mask = Image.fromarray((mask_array.astype(np.uint8) * 255), mode="L")
    else:
        mask = segment_unit(image, args.unit, args.segmenter.resolve())
        mask_array = np.asarray(mask) > 0
        matte_details = {"method": "explicit SAM2 semantic separation"}
    metrics = validate_unit_mask(mask_array, args.unit)
    coverage = metrics["coverage"]
    if not 0.08 <= coverage <= 0.68:
        raise SystemExit(f"SUBJECT_MASK_FAIL coverage={coverage:.6f}")
    rgb = np.asarray(image).copy()
    rgb[~mask_array] = GREEN
    composited = Image.fromarray(rgb, mode="RGB")
    exact_ratio = float(np.all(np.asarray(composited)[~mask_array] == GREEN, axis=1).mean())
    if exact_ratio != 1.0:
        raise SystemExit(f"GREEN_MATTE_FAIL exact_ratio={exact_ratio:.9f}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.mask.parent.mkdir(parents=True, exist_ok=True)
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    composited.save(args.output)
    mask.save(args.mask)
    qa = {
        "pass": True,
        "unit": args.unit,
        "candidate": args.output.as_posix(),
        "mask": args.mask.as_posix(),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "exact_green_outside_ratio": exact_ratio,
        "subject_coverage": coverage,
        "mask_metrics": metrics,
        "green_rgb": GREEN.tolist(),
        "seed": args.seed,
        "matte_method": args.matte_method,
        "matte_details": matte_details,
        "segmenter": str(args.segmenter.resolve()),
        "network_used": False,
    }
    args.qa.write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GREEN_MATTE_PASS", json.dumps(qa, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
