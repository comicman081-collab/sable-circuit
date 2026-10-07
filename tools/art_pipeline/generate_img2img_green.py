#!/usr/bin/env python3
"""Refine repo authority art and enforce an exact green generation matte.

This is the production candidate path for the pilot: SDXL img2img preserves the
repo identity source, then local Apache-2.0 CLIPSeg separates body/equipment and
the compositor writes exact #00FF00 to every background pixel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLImg2ImgPipeline
from PIL import Image
from transformers import (
    CLIPSegForImageSegmentation,
    CLIPSegProcessor,
    Sam2VideoModel,
    Sam2VideoProcessor,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_sdxl_pilot import COMMON, NEGATIVE, PROMPTS
from project_paths import PROJECT_ROOT, local_model_path, require_project_output_path


MODEL_DEFAULT = local_model_path("sdxl-base-1.0")
SEGMENTER_DEFAULT = local_model_path("auto-mask")
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
SEGMENT_PROMPTS = {
    "aster": ["person", "human body", "woman", "silver hair", "rifle weapon", "armor boots"],
    "rifle_trooper": ["person", "human body", "soldier", "rifle weapon", "armor helmet", "radio antenna"],
    "shield_breacher": ["person", "human body", "soldier", "large shield", "armor helmet", "pistol weapon"],
    "recon_drone": ["flying drone", "machine chassis", "ducted fan", "antenna weapon"],
}


def letterbox_reference(path: Path, size: tuple[int, int], mask_path: Path | None = None) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    if mask_path is not None:
        mask = Image.open(mask_path).convert("L")
        if mask.size != source.size:
            raise ValueError(f"reference mask size does not match reference: {mask.size} != {source.size}")
        source.putalpha(mask)
    source.thumbnail((int(size[0] * 0.88), int(size[1] * 0.92)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (118, 122, 126, 255))
    x = (size[0] - source.width) // 2
    y = (size[1] - source.height) // 2
    canvas.alpha_composite(source, (x, y))
    return canvas.convert("RGB")


def segment_unit(image: Image.Image, unit: str, model_path: Path) -> Image.Image:
    prompts = SEGMENT_PROMPTS[unit]
    processor = CLIPSegProcessor.from_pretrained(model_path, local_files_only=True)
    model = CLIPSegForImageSegmentation.from_pretrained(
        model_path, local_files_only=True, torch_dtype=torch.float16
    ).to("cuda")
    batch = processor(
        text=prompts,
        images=[image] * len(prompts),
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    batch = {key: value.to("cuda") for key, value in batch.items()}
    with torch.inference_mode():
        logits = model(**batch).logits
    probabilities = torch.sigmoid(logits).float().cpu().numpy()
    combined = probabilities.max(axis=0)
    combined = cv2.resize(combined, image.size, interpolation=cv2.INTER_CUBIC)
    proposal = combined >= (0.08 if unit == "recon_drone" else 0.06)
    ys, xs = np.where(proposal)
    if len(xs) == 0:
        raise RuntimeError("CLIPSeg produced no SAM2 box proposal")
    margin = 20
    x0 = max(0, int(xs.min()) - margin)
    y0 = max(0, int(ys.min()) - margin)
    x1 = min(image.width - 1, int(xs.max()) + margin)
    y1 = min(image.height - 1, int(ys.max()) + margin)
    del model
    torch.cuda.empty_cache()

    sam_path = model_path / "sam2"
    # The installed checkpoint is explicitly a SAM2 *video* checkpoint.  Using
    # the unrelated still-image class appears to load but produces torn masks;
    # treat one source image as a one-frame video instead.
    sam_processor = Sam2VideoProcessor.from_pretrained(sam_path, local_files_only=True)
    sam_model = Sam2VideoModel.from_pretrained(
        sam_path, local_files_only=True, torch_dtype=torch.float16
    ).to("cuda")
    session = sam_processor.init_video_session(
        video=[image],
        inference_device="cuda",
        inference_state_device="cpu",
        video_storage_device="cuda",
        dtype=torch.float16,
    )
    sam_processor.add_inputs_to_inference_session(
        session,
        frame_idx=0,
        obj_ids=1,
        input_boxes=[[[float(x0), float(y0), float(x1), float(y1)]]],
    )
    with torch.inference_mode():
        outputs = sam_model(session, frame_idx=0)
    post = sam_processor.post_process_masks(
        [outputs.pred_masks.float().cpu()],
        [[image.height, image.width]],
        mask_threshold=0.0,
        max_hole_area=256.0,
        max_sprinkle_area=96.0,
    )[0]
    mask = np.asarray(post.numpy()).squeeze().astype(np.uint8) * 255
    if mask.ndim != 2:
        raise RuntimeError(f"SAM2 video mask has unexpected shape: {mask.shape}")
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, 8)
    retained = np.zeros_like(mask)
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= 140:
            retained[labels == label] = 255
    retained = cv2.dilate(retained, np.ones((3, 3), np.uint8), iterations=1)
    return Image.fromarray(retained, mode="L")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", choices=sorted(PROMPTS))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--reference-mask", type=Path)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--model", type=Path, default=MODEL_DEFAULT)
    parser.add_argument("--segmenter", type=Path, default=SEGMENTER_DEFAULT)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "art_src/pilot_v2/raw_generation")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=34)
    parser.add_argument("--strength", type=float, default=0.72)
    parser.add_argument("--guidance", type=float, default=7.5)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "generation output")

    model_path = args.model.resolve()
    segmenter_path = args.segmenter.resolve()
    if not (model_path / "model_index.json").is_file():
        raise SystemExit(f"local SDXL model unavailable: {model_path}")
    if not (segmenter_path / "model.safetensors").is_file():
        raise SystemExit(f"local CLIPSeg model unavailable: {segmenter_path}")
    if not args.reference.is_file():
        raise SystemExit(f"reference unavailable: {args.reference}")
    if args.reference_mask is not None and not args.reference_mask.is_file():
        raise SystemExit(f"reference mask unavailable: {args.reference_mask}")

    size = (args.width, args.height)
    init = letterbox_reference(args.reference, size, args.reference_mask)
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
        local_files_only=True,
        add_watermarker=False,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config, algorithm_type="sde-dpmsolver++", use_karras_sigmas=True
    )
    pipe.vae.enable_slicing()
    pipe.to("cuda")
    generated = pipe(
        prompt=PROMPTS[args.unit],
        prompt_2=COMMON,
        negative_prompt=NEGATIVE,
        negative_prompt_2=NEGATIVE,
        image=init,
        strength=args.strength,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=torch.Generator(device="cuda").manual_seed(args.seed),
    ).images[0].convert("RGB")
    del pipe
    torch.cuda.empty_cache()

    mask = segment_unit(generated, args.unit, segmenter_path)
    mask_array = np.asarray(mask) > 0
    coverage = float(mask_array.mean())
    if not 0.08 <= coverage <= 0.68:
        raise SystemExit(f"SUBJECT_MASK_FAIL coverage={coverage:.6f}")
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask_array.astype(np.uint8), 8)
    if count <= 1:
        raise SystemExit("SUBJECT_MASK_FAIL no-component")
    areas = stats[1:, cv2.CC_STAT_AREA]
    label = int(np.argmax(areas)) + 1
    x, y, width, height, area = (int(value) for value in stats[label])
    if float(area) / float(mask_array.sum()) < 0.88:
        raise SystemExit("SUBJECT_MASK_FAIL fragmented")
    touches = x <= 3 or y <= 3 or x + width >= args.width - 3 or y + height >= args.height - 3
    if touches:
        raise SystemExit("SUBJECT_MASK_FAIL frame-edge-leak")
    rgb = np.asarray(generated).copy()
    rgb[~mask_array] = GREEN
    composited = Image.fromarray(rgb, mode="RGB")
    outside = np.asarray(composited)[~mask_array]
    exact_ratio = float(np.all(outside == GREEN, axis=1).mean())
    if exact_ratio != 1.0:
        raise SystemExit(f"GREEN_MATTE_FAIL exact_ratio={exact_ratio:.9f}")

    unit_dir = args.output / args.unit
    unit_dir.mkdir(parents=True, exist_ok=True)
    candidate = unit_dir / f"{args.unit}_authority_green_refined_seed{args.seed}.png"
    mask_path = unit_dir / f"{args.unit}_authority_green_refined_seed{args.seed}_mask.png"
    composited.save(candidate)
    mask.save(mask_path)
    qa = {
        "pass": True,
        "unit": args.unit,
        "candidate": candidate.as_posix(),
        "mask": mask_path.as_posix(),
        "reference": args.reference.as_posix(),
        "reference_mask": args.reference_mask.as_posix() if args.reference_mask else None,
        "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "exact_green_outside_ratio": exact_ratio,
        "subject_coverage": coverage,
        "mask_bbox_xywh": [x, y, width, height],
        "green_rgb": GREEN.tolist(),
        "seed": args.seed,
        "model": str(model_path),
        "segmenter": str(segmenter_path),
        "network_used": False,
    }
    (unit_dir / f"{args.unit}_authority_green_refined_seed{args.seed}_qa.json").write_text(
        json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("GREEN_MATTE_PASS", json.dumps(qa, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
