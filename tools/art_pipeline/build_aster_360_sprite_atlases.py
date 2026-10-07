#!/usr/bin/env python3
"""Build deterministic, mask-derived ASTER 360-degree WebP sprite atlases.

This tool has no generative path.  It accepts only manually authored exact
#00FF00 source frames and matching binary masks, and is hard-blocked until the
user has accepted the ASTER Static Master.  It is intentionally not wired to
the current runtime until all 144 frames pass visual and motion review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aster_static_master_gate import evaluate_static_master_gate

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/source"
MASK_ROOT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/masks"
OUTPUT_ROOT = ROOT / "assets/units/operators/aster/v2_360"
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
CELL_SIZE_DEFAULT = 384
DIRECTIONS = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
STATES = {
    "idle": ["ready", "inhale", "micro_weight_shift", "return"],
    "move": ["contact_a", "down_a", "passing_a", "high_a", "contact_b", "down_b", "passing_b", "high_b"],
    "fire": ["aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_frame_paths(state: str, direction: str, key: str) -> tuple[Path, Path]:
    stem = f"ASTER_{state}_{direction}_{key}"
    return (
        SOURCE_ROOT / state / f"{stem}_GREEN.png",
        MASK_ROOT / state / f"{stem}_MASK.png",
    )


def verify_green_source(source_path: Path, mask_path: Path) -> tuple[np.ndarray, dict]:
    if not source_path.is_file() or not mask_path.is_file():
        raise ValueError(f"missing source/mask pair: {source_path.name}")
    rgb = np.asarray(Image.open(source_path).convert("RGB"))
    mask = np.asarray(Image.open(mask_path).convert("L"))
    if rgb.shape[:2] != (2048, 2048) or mask.shape != (2048, 2048):
        raise ValueError(f"source/mask must both be 2048x2048: {source_path.name}")
    values = set(np.unique(mask).tolist())
    if not values.issubset({0, 255}) or values in ({0}, {255}):
        raise ValueError(f"mask must be nonempty binary 0/255: {mask_path.name}")
    subject = mask == 255
    exterior = ~subject
    exterior_ratio = float(np.all(rgb[exterior] == GREEN, axis=1).mean())
    opaque_green = int(np.all(rgb[subject] == GREEN, axis=1).sum())
    if exterior_ratio != 1.0 or opaque_green != 0:
        raise ValueError(f"exact #00FF00/mask contract fails: {source_path.name}")
    rgba = np.dstack((rgb, mask))
    return rgba, {
        "source": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source_path),
        "mask": mask_path.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(mask_path),
        "exact_green_exterior_ratio": exterior_ratio,
        "opaque_green_subject_pixels": opaque_green,
    }


def downsample_premultiplied(rgba: np.ndarray, cell_size: int) -> Image.Image:
    """Downsample without leaking green matte RGB through semitransparent edges."""
    rgb = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    premult = rgb * alpha[:, :, None]
    channels = [
        Image.fromarray(np.clip(premult[:, :, index], 0, 255).astype(np.uint8), mode="L").resize(
            (cell_size, cell_size), Image.Resampling.LANCZOS
        )
        for index in range(3)
    ]
    alpha_image = Image.fromarray(np.clip(alpha * 255.0, 0, 255).astype(np.uint8), mode="L").resize(
        (cell_size, cell_size), Image.Resampling.LANCZOS
    )
    alpha_array = np.asarray(alpha_image).astype(np.float32)
    rgb_out = np.zeros((cell_size, cell_size, 3), dtype=np.uint8)
    valid = alpha_array > 0.5
    for index, channel in enumerate(channels):
        channel_array = np.asarray(channel).astype(np.float32)
        rgb_out[:, :, index][valid] = np.clip(channel_array[valid] * 255.0 / alpha_array[valid], 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack((rgb_out, np.asarray(alpha_image))), mode="RGBA")


def require_project_output(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Output must stay in project: {resolved}") from exc
    return resolved


def build(cell_size: int, dry_run: bool) -> dict:
    gate = evaluate_static_master_gate()
    if not gate["accepted"]:
        raise PermissionError("HOLD: ASTER Static Master has no explicit user PASS; atlas generation is forbidden")

    source_records: dict[str, dict] = {}
    for state, keys in STATES.items():
        for direction in DIRECTIONS:
            for key in keys:
                source, mask = expected_frame_paths(state, direction, key)
                rgba, record = verify_green_source(source, mask)
                source_records[f"{state}/{direction}/{key}"] = record
                # Verify resizing now, even in dry-run mode, to catch green edge
                # contamination and invalid image modes before production output.
                downsample_premultiplied(rgba, cell_size)

    if dry_run:
        return {
            "dry_run": True,
            "static_gate": gate,
            "frame_count": len(source_records),
            "cell_size": cell_size,
            "output_created": False,
        }

    output_root = require_project_output(OUTPUT_ROOT)
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite an existing ASTER v2_360 export: {output_root}")
    staging = require_project_output(output_root.parent / f".v2_360_staging_{uuid.uuid4().hex}")
    try:
        manifest_states: dict[str, dict] = {}
        for state, keys in STATES.items():
            state_rows = {}
            for direction in DIRECTIONS:
                atlas = Image.new("RGBA", (cell_size, cell_size * len(keys)), (0, 0, 0, 0))
                frames = []
                for index, key in enumerate(keys):
                    source, mask = expected_frame_paths(state, direction, key)
                    rgba, record = verify_green_source(source, mask)
                    atlas.alpha_composite(downsample_premultiplied(rgba, cell_size), (0, index * cell_size))
                    frames.append({"key": key, "rect": [0, index * cell_size, cell_size, cell_size], **record})
                relative = Path(state) / f"ASTER_{state}_{direction}_RGBA.webp"
                atlas_path = staging / relative
                atlas_path.parent.mkdir(parents=True, exist_ok=True)
                atlas.save(atlas_path, format="WEBP", lossless=True, quality=100, method=6)
                state_rows[direction] = {
                    "atlas": relative.as_posix(),
                    "atlas_sha256": sha256(atlas_path),
                    "resolution": [cell_size, cell_size * len(keys)],
                    "frames": frames,
                }
            manifest_states[state] = {"fps": {"idle": 8, "move": 12, "fire": 12}[state], "directions": state_rows}
        manifest = {
            "schema": 1,
            "pipeline": "ASTER_2D_360_COMBAT_SPRITE_V1",
            "static_gate": gate,
            "source_background": "#00FF00",
            "mask_required": True,
            "cell_size": cell_size,
            "directions": DIRECTIONS,
            "states": manifest_states,
            "frame_count": len(source_records),
            "runtime_status": "NOT_CONNECTED_PENDING_MOTION_QA",
            "visual_mesh_promoted": False,
            "krea_or_cloud_used": False,
        }
        manifest_path = staging / "ASTER_360_ATLAS_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        staging.rename(output_root)
        return {"dry_run": False, "output": output_root.relative_to(ROOT).as_posix(), "manifest": manifest, "frame_count": len(source_records)}
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell-size", type=int, default=CELL_SIZE_DEFAULT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.cell_size < 256 or args.cell_size > 1024 or args.cell_size % 2:
        raise SystemExit("cell size must be an even value in 256..1024")
    try:
        report = build(args.cell_size, args.dry_run)
    except PermissionError as error:
        print("ASTER_360_ATLAS_BUILD: HOLD - " + str(error))
        return 2
    except Exception as error:
        print("ASTER_360_ATLAS_BUILD: FAIL - " + str(error))
        return 1
    print("ASTER_360_ATLAS_BUILD: PASS " + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
