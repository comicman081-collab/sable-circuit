#!/usr/bin/env python3
"""End-to-end smoke test for the data-driven character fast pipeline."""

from __future__ import annotations

import importlib.util
import json
import math
import shutil
import uuid
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "character_pipeline" / "sable_character_pipeline.py"
SPEC = importlib.util.spec_from_file_location("sable_character_pipeline", MODULE_PATH)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_green_atlas(path: Path, cell: int, frames: int, direction: str) -> None:
    image = Image.new("RGB", (cell, cell * frames), (0, 255, 0))
    vector = pipeline.DIRECTION_VECTORS[direction]
    draw = ImageDraw.Draw(image)
    for frame in range(frames):
        y0 = frame * cell
        bob = frame % 2
        center = (cell // 2, y0 + cell // 2 + bob)
        draw.ellipse((center[0] - 34, center[1] - 55, center[0] + 34, center[1] + 55), fill=(30, 55, 82))
        tip = (center[0] + int(vector[0] * 90), center[1] + int(vector[1] * 90))
        draw.line((center[0], center[1], tip[0], tip[1]), fill=(235, 190, 90), width=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def main() -> int:
    smoke_root = ROOT / "artifacts" / "character_pipeline_smoke" / ("run_" + uuid.uuid4().hex)
    spec_path = smoke_root / "spec.json"
    candidate = smoke_root / "candidate"
    spec = {
        "schema": 1,
        "actor_id": "CHR_SMOKE_FAST",
        "slug": "smoke_fast",
        "display_name": "SMOKE FAST",
        "role": "QA",
        "costume_id": "SMOKE_FAST_C01",
        "identity_lock": {
            "adult": True,
            "faction": "QA",
            "body_type": "athletic adult",
            "face_read": "mature adult",
            "weapon_class": "rifle",
            "combat_role": "pipeline test",
        },
        "visual_lock": {
            "source_author": "built-in ImageGen",
            "generation_matte": "#00FF00",
            "palette": ["#1E3752", "#EBBE5A", "#E8F2F6"],
            "silhouette_modules": ["QA body", "QA rifle"],
            "exposure_coverage": "full QA coverage",
            "accessories": [],
            "weapon_grip_zones": ["trigger", "support"],
            "forbidden_features": [],
        },
        "runtime": {
            "cell_size": 256,
            "display_scale": 0.4,
            "display_offset": [0.0, -30.0],
            "states": {
                "idle": {"frames": 2, "fps": 4.0},
                "move": {"frames": 3, "fps": 12.0},
                "fire": {"frames": 2, "fps": 12.0},
            },
        },
        "paths": {
            "work_root": "artifacts/character_pipeline_smoke/work",
            "runtime_root": "artifacts/character_pipeline_smoke/runtime",
            "descriptor": "artifacts/character_pipeline_smoke/runtime_descriptor.json",
        },
        "muzzle_hints": {},
        "registration": {
            "visual_profile": "VIS_SMOKE",
            "master_asset": "artifacts/character_pipeline_smoke/not_registered.svg",
            "portrait_asset": "artifacts/character_pipeline_smoke/not_registered.svg",
            "rig_sheet": "artifacts/character_pipeline_smoke/not_registered.svg",
            "detail_overlay_asset": "artifacts/character_pipeline_smoke/not_registered.svg",
            "weapon_hud_asset": "artifacts/character_pipeline_smoke/not_registered.svg",
        },
    }
    for key, value in spec["paths"].items():
        spec["paths"][key] = value.replace("artifacts/character_pipeline_smoke", smoke_root.relative_to(ROOT).as_posix())
    write_json(spec_path, spec)
    write_json(candidate / "SOURCE_PROVENANCE.json", {
        "imagegen_author": "built-in ImageGen",
        "blender_ual_motion": True,
        "costume_id": spec["costume_id"],
        "costume_continuity": "PASS",
        "authority_resolution": [2048, 2048],
        "qa_fixture_only": True,
    })
    for direction in pipeline.DIRECTIONS:
        for state in pipeline.STATES:
            make_green_atlas(
                candidate / direction / f"{state}_green.png",
                spec["runtime"]["cell_size"],
                spec["runtime"]["states"][state]["frames"],
                direction,
            )

    loaded = pipeline.read_spec(spec_path)
    pipeline.init_pipeline(loaded)
    try:
        pipeline.promote_motion_candidate(loaded, str(candidate))
        raise AssertionError("promotion without all-gate receipt must fail")
    except ValueError as exc:
        assert "PROMOTION_BLOCKED" in str(exc)
    state = pipeline.build_runtime(loaded, str(candidate))
    assert state["production_pointer_changed"] is False
    assert not pipeline.spec_paths(loaded)["descriptor"].exists()
    qa = pipeline.validate_runtime(loaded, descriptor_value=state["descriptor"])
    assert qa["gate"] == "PASS_STRUCTURE_ONLY"
    descriptor = pipeline.load_json(ROOT / state["descriptor"])
    assert list(descriptor["directions"].keys()) == pipeline.DIRECTIONS
    for direction in pipeline.DIRECTIONS:
        assert len(descriptor["directions"][direction]["muzzle_xy"]) == 2
    print("SABLE_CHARACTER_PIPELINE_STAGING_AND_PROMOTION_GUARD: PASS (synthetic fixture, not artwork QA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
