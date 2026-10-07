#!/usr/bin/env python3
"""Generate SABLE pilot authority candidates with an installed local SDXL model.

No network call is made. The script deliberately refuses a missing local model
instead of allowing Diffusers to download a fallback.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLPipeline

from project_paths import PROJECT_ROOT, local_model_path, require_project_output_path

MODEL_DEFAULT = local_model_path("sdxl-base-1.0")
NEGATIVE = (
    "child, chibi, oversized head, short legs, toy, mannequin, paper cutout, thick outline, blurry, cropped, "
    "duplicate, extra limbs, broken hands, floating weapon, text, logo, UI, scenery, floor, shadow, "
    "green clothing, heavy white armor, high heels, catalog pose, one-hand rifle"
)

COMMON = (
    "single full-body unit, 3/4 top-down combat view, premium mature anime sci-fi RPG, "
    "crisp detailed 3D game render with clean 2D planes, readable silhouette, centered, "
    "dynamic combat pose, one figure only, no turnaround, isolated on flat pure #00FF00 "
    "green background, no floor, no shadow"
)

PROMPTS = {
    "aster": (
        "ASTER, slender athletic adult woman precision rifle operator, 3/4 overhead combat view, silver comet high "
        "ponytail, small head and five-head battle proportions, deep navy asymmetric tactical jacket, right shoulder "
        "plate, charcoal undersuit, cyan piping, gold details, low armored boots, long narrow coil precision rifle "
        "aimed across body, correct two-hand shoulder firing grip"
    ),
    "rifle_trooper": (
        "SITE-7 Rifle Trooper, adult man security soldier, five-head proportions, narrow hazard "
        "hood, sealed mask, offset radio mast, white slate segmented armor, red marks, split knee "
        "armor, long bullpup rifle, disciplined two-hand grip, cautious trained stance"
    ),
    "shield_breacher": (
        "SITE-7 Shield Breacher, adult man elite heavy operator, five-head proportions, massive "
        "tall slab shield, wedge helmet, bulky white dark-steel armor, exposed hydraulic arm, "
        "amber lamps, compact ram pistol, shield-first braced advance, grounded stance"
    ),
    "recon_drone": (
        "SITE-7 Recon Drone, small nonhumanoid floating machine, flat crescent chassis, three "
        "unequal magenta sensor eyes, twin ducted fans, asymmetric antenna, dangling thruster, "
        "underbody emitter, silver graphite panels, cyan lamps, banked hover, no limbs"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("units", nargs="+", choices=sorted(PROMPTS))
    parser.add_argument("--model", type=Path, default=MODEL_DEFAULT)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "art_src/pilot_v2/raw_generation")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--guidance", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=740210)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output = require_project_output_path(args.output, "generation output")
    model = args.model.resolve()
    if not (model / "model_index.json").is_file():
        raise SystemExit(f"local SDXL model is unavailable: {model}")
    if args.width % 8 or args.height % 8:
        raise SystemExit("width and height must be divisible by 8")

    pipe = StableDiffusionXLPipeline.from_pretrained(
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
    pipe.enable_vae_slicing()
    pipe.to("cuda")

    args.output.mkdir(parents=True, exist_ok=True)
    provenance_path = args.output / "sdxl_generation_provenance.json"
    provenance = []
    if provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    for index, unit in enumerate(args.units):
        unit_seed = args.seed + index * 1009
        generator = torch.Generator(device="cuda").manual_seed(unit_seed)
        result = pipe(
            prompt=PROMPTS[unit],
            prompt_2=COMMON,
            negative_prompt=NEGATIVE,
            negative_prompt_2=NEGATIVE,
            width=args.width,
            height=args.height,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance,
            generator=generator,
        ).images[0]
        unit_dir = args.output / unit
        unit_dir.mkdir(parents=True, exist_ok=True)
        path = unit_dir / f"{unit}_authority_raw_seed{unit_seed}.png"
        result.save(path)
        provenance.append(
            {
                "unit": unit,
                "file": path.as_posix(),
                "seed": unit_seed,
                "model": str(model),
                "width": args.width,
                "height": args.height,
                "steps": args.steps,
                "guidance": args.guidance,
                "prompt": PROMPTS[unit],
                "prompt_2": COMMON,
                "negative_prompt": NEGATIVE,
                "network_used": False,
            }
        )
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
