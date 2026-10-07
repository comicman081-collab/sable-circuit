#!/usr/bin/env python3
"""Generate one-unit pilot candidates on a guaranteed #00FF00 matte.

The model only paints a unit-specific silhouette mask. The compositor restores
the exact chroma matte outside that mask and refuses to save a candidate when
the matte coverage or channel values violate the production contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLInpaintPipeline
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_sdxl_pilot import COMMON, NEGATIVE, PROMPTS
from project_paths import PROJECT_ROOT, local_model_path, require_project_output_path


MODEL_DEFAULT = local_model_path("sdxl-inpaint")
GREEN = (0, 255, 0)


def humanoid_mask(size: tuple[int, int], kind: str) -> Image.Image:
    width, height = size
    sx, sy = width / 768.0, height / 1024.0
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    def ellipse(box: tuple[int, int, int, int]) -> None:
        draw.ellipse(tuple(int(v * (sx if i % 2 == 0 else sy)) for i, v in enumerate(box)), fill=255)

    def poly(points: list[tuple[int, int]]) -> None:
        draw.polygon([(int(x * sx), int(y * sy)) for x, y in points], fill=255)

    if kind == "shield_breacher":
        ellipse((276, 105, 424, 253))
        poly([(245, 220), (455, 220), (492, 530), (218, 530)])
        poly([(248, 485), (348, 485), (326, 913), (204, 913)])
        poly([(355, 485), (466, 485), (508, 913), (382, 913)])
        poly([(115, 220), (285, 200), (292, 720), (78, 760)])
        poly([(426, 260), (535, 290), (615, 520), (520, 555)])
        poly([(500, 360), (642, 350), (664, 405), (520, 430)])
    else:
        ellipse((280, 105, 418, 243))
        poly([(238, 215), (454, 215), (470, 535), (230, 535)])
        poly([(246, 490), (348, 490), (326, 905), (205, 905)])
        poly([(350, 490), (452, 490), (500, 905), (375, 905)])
        poly([(246, 245), (300, 270), (238, 545), (142, 520)])
        poly([(410, 250), (468, 270), (555, 440), (478, 478)])
        poly([(232, 306), (470, 315), (674, 355), (668, 420), (432, 388), (220, 374)])
        if kind == "aster":
            poly([(288, 112), (213, 86), (117, 203), (227, 255), (314, 193)])
            poly([(318, 118), (230, 148), (130, 314), (247, 303), (335, 190)])
        else:
            poly([(272, 112), (430, 102), (448, 244), (248, 247)])
    return mask.filter(ImageFilter.GaussianBlur(max(2, int(3 * sx))))


def drone_mask(size: tuple[int, int]) -> Image.Image:
    width, height = size
    sx, sy = width / 768.0, height / 1024.0
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((int(94 * sx), int(290 * sy), int(674 * sx), int(645 * sy)), fill=255)
    draw.ellipse((int(35 * sx), int(350 * sy), int(268 * sx), int(584 * sy)), fill=255)
    draw.ellipse((int(500 * sx), int(350 * sy), int(733 * sx), int(584 * sy)), fill=255)
    draw.polygon([(int(x * sx), int(y * sy)) for x, y in [(305, 300), (382, 165), (425, 310)]], fill=255)
    draw.polygon([(int(x * sx), int(y * sy)) for x, y in [(330, 610), (438, 610), (414, 785), (354, 785)]], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(max(2, int(3 * sx))))


def build_scaffold(unit: str, size: tuple[int, int]) -> tuple[Image.Image, Image.Image]:
    mask = drone_mask(size) if unit == "recon_drone" else humanoid_mask(size, unit)
    canvas = Image.new("RGB", size, GREEN)
    neutral = Image.new("RGB", size, (32, 42, 52))
    canvas.paste(neutral, mask=mask)
    return canvas, mask


def verify_green_matte(image: Image.Image, hard_mask: Image.Image) -> dict[str, object]:
    rgb = np.asarray(image.convert("RGB"))
    mask = np.asarray(hard_mask) > 0
    outside = rgb[~mask]
    exact = np.all(outside == np.asarray(GREEN, dtype=np.uint8), axis=1)
    exact_ratio = float(exact.mean()) if len(exact) else 0.0
    canvas_ratio = float((~mask).mean())
    passed = exact_ratio == 1.0 and canvas_ratio >= 0.30
    return {
        "exact_green_outside_ratio": exact_ratio,
        "green_canvas_ratio": canvas_ratio,
        "green_rgb": list(GREEN),
        "pass": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", choices=sorted(PROMPTS))
    parser.add_argument("--model", type=Path, default=MODEL_DEFAULT)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "art_src/pilot_v2/raw_generation")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--guidance", type=float, default=7.5)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "generation output")

    model = args.model.resolve()
    if not (model / "model_index.json").is_file():
        raise SystemExit(f"local SDXL inpaint model unavailable: {model}")
    size = (args.width, args.height)
    scaffold, soft_mask = build_scaffold(args.unit, size)
    mask = soft_mask.point(lambda value: 255 if value >= 8 else 0, mode="L")
    unit_dir = args.output / args.unit
    unit_dir.mkdir(parents=True, exist_ok=True)
    scaffold.save(unit_dir / f"{args.unit}_green_scaffold.png")
    mask.save(unit_dir / f"{args.unit}_generation_mask.png")

    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
        model,
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
        image=scaffold,
        mask_image=mask,
        width=args.width,
        height=args.height,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        strength=0.99,
        generator=torch.Generator(device="cuda").manual_seed(args.seed),
    ).images[0].convert("RGB")

    # Restore the immutable generation matte after VAE decode. The binary mask
    # forbids VAE color bleed: every background pixel is exact #00FF00.
    exact_green = Image.new("RGB", size, GREEN)
    composited = Image.composite(generated, exact_green, mask)
    qa = verify_green_matte(composited, mask)
    if not qa["pass"]:
        raise SystemExit(f"GREEN_MATTE_FAIL: {qa}")

    candidate = unit_dir / f"{args.unit}_authority_green_seed{args.seed}.png"
    composited.save(candidate)
    qa.update(
        {
            "unit": args.unit,
            "candidate": candidate.as_posix(),
            "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "seed": args.seed,
            "model": str(model),
            "network_used": False,
            "prompt": PROMPTS[args.unit],
            "prompt_2": COMMON,
        }
    )
    (unit_dir / f"{args.unit}_green_matte_qa.json").write_text(
        json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("GREEN_MATTE_PASS", json.dumps(qa, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
