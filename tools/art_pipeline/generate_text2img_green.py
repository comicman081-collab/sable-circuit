#!/usr/bin/env python3
"""Generate a single unit, segment locally, and save only exact-green candidates."""

from __future__ import annotations

import argparse
import gc
from pathlib import Path
import subprocess
import sys

import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLPipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_sdxl_pilot import COMMON, NEGATIVE, PROMPTS
from project_paths import PROJECT_ROOT, local_model_path, require_project_output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", choices=sorted(PROMPTS))
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--model", type=Path, default=local_model_path("sdxl-base-1.0"))
    parser.add_argument("--segmenter", type=Path, default=local_model_path("auto-mask"))
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "art_src/pilot_v2/raw_generation")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=34)
    parser.add_argument("--guidance", type=float, default=7.5)
    args = parser.parse_args()
    args.output = require_project_output_path(args.output, "generation output")

    model_path = args.model.resolve()
    segmenter_path = args.segmenter.resolve()
    if not (model_path / "model_index.json").is_file():
        raise SystemExit(f"local SDXL model unavailable: {model_path}")
    pipe = StableDiffusionXLPipeline.from_pretrained(
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
    pipe.enable_vae_slicing()
    pipe.to("cuda")

    def progress(_pipeline, step_index: int, timestep, callback_kwargs):
        # Progress is textual only; no un-matted image is written or exposed.
        print(f"SDXL_STEP {step_index + 1}/{args.steps}", flush=True)
        return callback_kwargs

    image = pipe(
        prompt=PROMPTS[args.unit],
        prompt_2=COMMON,
        negative_prompt=NEGATIVE,
        negative_prompt_2=NEGATIVE,
        width=args.width,
        height=args.height,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=torch.Generator(device="cuda").manual_seed(args.seed),
        callback_on_step_end=progress,
    ).images[0].convert("RGB")
    unit_dir = args.output / args.unit
    unit_dir.mkdir(parents=True, exist_ok=True)
    temporary = unit_dir / f".{args.unit}_text_seed{args.seed}_unmatted.tmp.png"
    image.save(temporary)
    del pipe
    del image
    gc.collect()
    torch.cuda.empty_cache()
    candidate = unit_dir / f"{args.unit}_authority_green_text_seed{args.seed}.png"
    mask_path = unit_dir / f"{args.unit}_authority_green_text_seed{args.seed}_mask.png"
    qa_path = unit_dir / f"{args.unit}_authority_green_text_seed{args.seed}_qa.json"
    command = [
        sys.executable,
        str(Path(__file__).with_name("apply_green_matte.py")),
        args.unit,
        "--input", str(temporary),
        "--output", str(candidate),
        "--mask", str(mask_path),
        "--qa", str(qa_path),
        "--seed", str(args.seed),
        "--segmenter", str(segmenter_path),
    ]
    result = subprocess.run(command, check=False)
    if temporary.is_file():
        temporary.unlink()
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
