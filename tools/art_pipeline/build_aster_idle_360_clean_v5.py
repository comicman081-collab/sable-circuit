#!/usr/bin/env python3
"""Re-export ASTER's four-frame idle atlases without V1 matte corruption.

The immutable green sources and masks remain authority.  This rebuild uses
premultiplied-alpha downsampling, removes only exterior near-black matte residue
guarded by the accepted clean V5 move silhouette, and writes a new V5 family.
It never overwrites the visually failed V1 atlases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
KEYS = ("ready", "inhale", "micro_weight_shift", "return")
CELL = 384
GREEN = np.array([0, 255, 0], dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    t = np.clip((values - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def tile_rgba(source: Path, mask: Path) -> tuple[np.ndarray, dict[str, Any]]:
    if not source.is_file() or not mask.is_file():
        raise SystemExit(f"idle authority incomplete: {source} / {mask}")
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    alpha_u8 = np.asarray(Image.open(mask).convert("L"), dtype=np.uint8)
    if rgb.shape[:2] != alpha_u8.shape:
        raise SystemExit(f"idle source/mask dimensions differ: {source}")
    alpha = alpha_u8.astype(np.float32) / 255.0
    premultiplied = np.rint(rgb.astype(np.float32) * alpha[:, :, None]).astype(np.uint8)
    pm_small = np.asarray(
        Image.fromarray(premultiplied, "RGB").resize((CELL, CELL), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    alpha_small = np.asarray(
        Image.fromarray(alpha_u8, "L").resize((CELL, CELL), Image.Resampling.LANCZOS),
        dtype=np.float32,
    ) / 255.0
    straight = np.zeros_like(pm_small, dtype=np.float32)
    np.divide(
        pm_small,
        np.maximum(alpha_small[:, :, None], 1.0 / 255.0),
        out=straight,
        where=alpha_small[:, :, None] > 0,
    )
    straight[alpha_small < (1.0 / 255.0)] = 0
    rgba = np.dstack(
        (
            np.rint(np.clip(straight, 0.0, 255.0)).astype(np.uint8),
            np.rint(alpha_small * 255.0).astype(np.uint8),
        )
    )
    return rgba, {
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source),
        "mask": mask.relative_to(ROOT).as_posix(),
        "mask_sha256": sha256(mask),
    }


def clean_exterior_matte(frame: np.ndarray, clean_support: np.ndarray) -> tuple[np.ndarray, dict[str, int | bool]]:
    result = frame.copy()
    outside_distance = cv2.distanceTransform(
        (~clean_support).astype(np.uint8), cv2.DIST_L2, 3
    ).astype(np.float32)
    maximum = np.max(frame[:, :, :3], axis=2).astype(np.float32)
    darkness = 1.0 - smoothstep(18.0, 76.0, maximum)
    spatial = smoothstep(0.25, 4.5, outside_distance)
    removal = np.clip(darkness * spatial, 0.0, 1.0)
    original_alpha = frame[:, :, 3].astype(np.float32)
    cleaned_alpha = np.rint(original_alpha * (1.0 - removal)).astype(np.uint8)
    black_core = (
        (maximum < 34.0)
        & (outside_distance > 0.0)
        & (frame[:, :, 3] > 8)
    )
    cleaned_alpha[black_core] = 0
    low_alpha_green_matte = (
        (frame[:, :, 1] > 180)
        & (frame[:, :, 0] < 45)
        & (frame[:, :, 2] < 85)
        & (cleaned_alpha < 80)
    )
    # ASTER's locked palette has cyan emissives and gold hardware, but no
    # saturated green.  Strong green-dominant pixels are therefore chroma-key
    # contamination even when the idle mask accidentally places them inside
    # the move silhouette.  Remove by colour contract rather than eroding the
    # silhouette; cyan is protected because its blue channel is high.
    chroma_green_matte = (
        (frame[:, :, 1] > 24)
        & (frame[:, :, 1].astype(np.int16) > frame[:, :, 0].astype(np.int16) * 2 + 16)
        & (frame[:, :, 1].astype(np.int16) > frame[:, :, 2].astype(np.int16) * 2 + 16)
        & (frame[:, :, 0] < 40)
        & (frame[:, :, 2] < 60)
    )
    cleaned_alpha[low_alpha_green_matte | chroma_green_matte] = 0
    # Lanczos can turn a disconnected matte fleck into a tiny opaque island.
    # Keep every island that overlaps the accepted move silhouette, and keep
    # detached authored details large enough to be intentional.  Only tiny,
    # wholly exterior components are removed; the main character is untouched.
    component_mask = (cleaned_alpha > 8).astype(np.uint8)
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        component_mask, connectivity=8
    )
    tiny_exterior_components = 0
    tiny_exterior_pixels = 0
    for label in range(1, component_count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= 32:
            continue
        component = labels == label
        if np.any(clean_support & component):
            continue
        tiny_exterior_components += 1
        tiny_exterior_pixels += area
        cleaned_alpha[component] = 0
    result[:, :, 3] = cleaned_alpha
    result[cleaned_alpha == 0, :3] = 0
    residual_black = (
        (np.max(result[:, :, :3], axis=2) < 24)
        & (result[:, :, 3] > 32)
        & (~clean_support)
    )
    green_visible = (
        (result[:, :, 3] > 16)
        & (result[:, :, 1] > 180)
        & (result[:, :, 0] < 45)
        & (result[:, :, 2] < 85)
    )
    return result, {
        "source_modified": False,
        "derived_exterior_matte_cleanup": True,
        "pixels_alpha_reduced": int(np.count_nonzero(cleaned_alpha < frame[:, :, 3])),
        "removed_alpha_sum": int(np.sum(frame[:, :, 3].astype(np.int64) - cleaned_alpha.astype(np.int64))),
        "tiny_exterior_components_removed": tiny_exterior_components,
        "tiny_exterior_component_pixels_removed": tiny_exterior_pixels,
        "residual_opaque_near_black_outside_support": int(np.count_nonzero(residual_black)),
        "visible_near_green_pixels": int(np.count_nonzero(green_visible)),
    }


def green_authoring(frame: np.ndarray) -> np.ndarray:
    alpha = frame[:, :, 3].astype(np.float32) / 255.0
    rgb = frame[:, :, :3].astype(np.float32) * alpha[:, :, None] + GREEN.astype(np.float32)[None, None, :] * (1.0 - alpha[:, :, None])
    rgb[frame[:, :, 3] == 0] = GREEN
    return np.rint(np.clip(rgb, 0.0, 255.0)).astype(np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace-derived",
        action="store_true",
        help="atomically replace only idle_360_clean_v5 and preserve prior contact/manifest",
    )
    args = parser.parse_args()
    output = ROOT / "assets/units/operators/aster/idle_360_clean_v5"
    authoring = ROOT / "art_src/pilot_v2/aster_v2/animation_360/idle_360_clean_v5"
    if (output.exists() or authoring.exists()) and not args.replace_derived:
        raise SystemExit("refusing to overwrite idle_360_clean_v5")
    if args.replace_derived and (not output.is_dir() or not authoring.is_dir()):
        raise SystemExit("--replace-derived requires both existing idle_360_clean_v5 directories")
    output.parent.mkdir(parents=True, exist_ok=True)
    authoring.parent.mkdir(parents=True, exist_ok=True)
    output_stage = Path(tempfile.mkdtemp(prefix="idle_360_clean_v5_runtime_", dir=output.parent))
    authoring_stage = Path(tempfile.mkdtemp(prefix="idle_360_clean_v5_authoring_", dir=authoring.parent))
    promoted_output = False
    promoted_authoring = False
    output_backup = output.with_name(output.name + "__replace_backup")
    authoring_backup = authoring.with_name(authoring.name + "__replace_backup")
    try:
        if args.replace_derived:
            if output_backup.exists() or authoring_backup.exists():
                raise SystemExit("stale idle_360_clean_v5 replacement backup exists")
            previous_contact = authoring / "ASTER_IDLE_360_CLEAN_V5_CONTACT.png"
            previous_manifest = authoring / "ASTER_IDLE_360_CLEAN_V5_MANIFEST.json"
            if not previous_contact.is_file() or not previous_manifest.is_file():
                raise SystemExit("existing clean-idle review evidence is incomplete")
            shutil.copy2(previous_contact, authoring_stage / "ASTER_IDLE_360_CLEAN_V5_CONTACT_PREVIOUS_MATTE.png")
            shutil.copy2(previous_manifest, authoring_stage / "ASTER_IDLE_360_CLEAN_V5_MANIFEST_PREVIOUS_MATTE.json")
        records: dict[str, Any] = {}
        previews: list[tuple[str, str, Image.Image]] = []
        for direction in DIRECTIONS:
            move_path = ROOT / f"assets/units/operators/aster/move_360_ual_v5/{direction}/ASTER_MOVE_{direction}_360_UAL_V5_ATLAS.webp"
            move = np.asarray(Image.open(move_path).convert("RGBA"), dtype=np.uint8).reshape(24, CELL, CELL, 4)
            clean_support = move[0, :, :, 3] > 8
            frames: list[np.ndarray] = []
            frame_records: list[dict[str, Any]] = []
            for index, key in enumerate(KEYS):
                source = ROOT / f"art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/source/idle/{direction}/ASTER_IDLE_{direction}_{key.upper()}_GREEN.png"
                mask = ROOT / f"art_src/pilot_v2/aster_v2/animation_360/imagegen_idle_move_360_mvp_v1/masks/idle/{direction}/ASTER_IDLE_{direction}_{key.upper()}_MASK.png"
                frame, authority = tile_rgba(source, mask)
                frame, cleanup = clean_exterior_matte(frame, clean_support)
                if cleanup["residual_opaque_near_black_outside_support"] != 0:
                    raise RuntimeError(f"{direction} {key} retains exterior black matte")
                if cleanup["visible_near_green_pixels"] > 48:
                    raise RuntimeError(f"{direction} {key} retains visible green matte: {cleanup['visible_near_green_pixels']}")
                row_occupancy = np.mean(frame[:, :, 3] > 16, axis=1)
                full_width_band_rows = int(np.count_nonzero(row_occupancy > 0.88))
                if full_width_band_rows:
                    raise RuntimeError(f"{direction} {key} contains opaque horizontal bands")
                source_dir = authoring_stage / "source" / direction
                mask_dir = authoring_stage / "masks" / direction
                source_dir.mkdir(parents=True, exist_ok=True)
                mask_dir.mkdir(parents=True, exist_ok=True)
                green_path = source_dir / f"ASTER_IDLE_{direction}_{key.upper()}_CLEAN_V5_GREEN.png"
                alpha_path = mask_dir / f"ASTER_IDLE_{direction}_{key.upper()}_CLEAN_V5_MASK.png"
                Image.fromarray(green_authoring(frame), "RGB").save(green_path, optimize=True)
                Image.fromarray(frame[:, :, 3], "L").save(alpha_path, optimize=True)
                frames.append(frame)
                previews.append((direction, key, Image.fromarray(frame, "RGBA")))
                frame_records.append({
                    "index": index,
                    "key": key,
                    **authority,
                    "derived_green": (authoring / "source" / direction / green_path.name).relative_to(ROOT).as_posix(),
                    "derived_green_sha256": sha256(green_path),
                    "derived_mask": (authoring / "masks" / direction / alpha_path.name).relative_to(ROOT).as_posix(),
                    "derived_mask_sha256": sha256(alpha_path),
                    "cleanup": cleanup,
                    "full_width_band_rows": full_width_band_rows,
                })
            decoded_hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames]
            if len(set(decoded_hashes)) < 2:
                raise RuntimeError(f"{direction} clean idle has no visible breathing variation")
            runtime_dir = output_stage / direction
            runtime_dir.mkdir(parents=True)
            atlas_stage = runtime_dir / f"ASTER_IDLE_{direction}_CLEAN_V5_ATLAS.webp"
            atlas = np.concatenate(frames, axis=0)
            Image.fromarray(atlas, "RGBA").save(atlas_stage, "WEBP", lossless=True, method=6, exact=True)
            decoded = np.asarray(Image.open(atlas_stage).convert("RGBA"), dtype=np.uint8)
            if not np.array_equal(decoded, atlas):
                raise RuntimeError(f"{direction} clean idle WebP round-trip changed pixels")
            atlas_path = output / direction / atlas_stage.name
            records[direction] = {
                "atlas": atlas_path.relative_to(ROOT).as_posix(),
                "atlas_sha256": sha256(atlas_stage),
                "resolution": [CELL, CELL * len(KEYS)],
                "frame_count": len(KEYS),
                "fps": 4,
                "frames": frame_records,
                "unique_decoded_frames": len(set(decoded_hashes)),
                "lossless_webp_roundtrip": True,
            }

        preview = Image.new("RGBA", (256 * len(DIRECTIONS), 276 * len(KEYS)), (16, 22, 29, 255))
        draw = ImageDraw.Draw(preview)
        lookup = {(direction, key): image for direction, key, image in previews}
        for row, key in enumerate(KEYS):
            for column, direction in enumerate(DIRECTIONS):
                x, y = column * 256, row * 276
                preview.alpha_composite(lookup[(direction, key)].resize((256, 256), Image.Resampling.LANCZOS), (x, y))
                draw.rectangle((x, y, x + 118, y + 20), fill=(4, 9, 13, 230))
                draw.text((x + 5, y + 4), f"{direction} {key.upper()}", fill=(132, 238, 244, 255))
        preview_stage = authoring_stage / "ASTER_IDLE_360_CLEAN_V5_CONTACT.png"
        preview.save(preview_stage, optimize=True)
        manifest = {
            "schema": 1,
            "role": "ASTER 8-direction four-frame artifact-free idle V5 runtime family",
            "directions": list(DIRECTIONS),
            "keys": list(KEYS),
            "frame_size": [CELL, CELL],
            "atlas_resolution": [CELL, CELL * len(KEYS)],
            "frame_count_per_direction": len(KEYS),
            "fps": 4,
            "method": "immutable green authority + mask, premultiplied-alpha Lanczos export, clean V5 silhouette guarded exterior matte cleanup",
            "source_modified": False,
            "baked_muzzle_vfx": False,
            "directions_output": records,
            "preview": (authoring / preview_stage.name).relative_to(ROOT).as_posix(),
            "preview_sha256": sha256(preview_stage),
            "preserved_immediate_previous_visual_fail": "assets/units/operators/aster/idle_move_360_mvp_v1/idle",
            "qa": {
                "minimum_unique_frames_per_direction": 2,
                "ready_return_duplicate_allowed_as_loop_anchor": True,
                "full_width_alpha_band_rows": 0,
                "residual_opaque_exterior_black_matte": 0,
                "lossless_webp_roundtrip": True,
                "visual_gate": "USER_REVIEW_REQUIRED",
            },
            "preserved_previous_review": {
                "contact": "art_src/pilot_v2/aster_v2/animation_360/idle_360_clean_v5/ASTER_IDLE_360_CLEAN_V5_CONTACT_PREVIOUS_MATTE.png",
                "manifest": "art_src/pilot_v2/aster_v2/animation_360/idle_360_clean_v5/ASTER_IDLE_360_CLEAN_V5_MANIFEST_PREVIOUS_MATTE.json",
            } if args.replace_derived else None,
            "production_expansion": "HOLD",
        }
        runtime_manifest = output_stage / "ASTER_IDLE_360_CLEAN_V5_MANIFEST.json"
        authoring_manifest = authoring_stage / "ASTER_IDLE_360_CLEAN_V5_MANIFEST.json"
        runtime_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        authoring_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.replace_derived:
            os.replace(output, output_backup)
            os.replace(authoring, authoring_backup)
            try:
                os.replace(output_stage, output)
                promoted_output = True
                os.replace(authoring_stage, authoring)
                promoted_authoring = True
            except Exception:
                if output.exists():
                    shutil.rmtree(output)
                if authoring.exists():
                    shutil.rmtree(authoring)
                os.replace(output_backup, output)
                os.replace(authoring_backup, authoring)
                raise
            shutil.rmtree(output_backup)
            shutil.rmtree(authoring_backup)
        else:
            os.replace(output_stage, output)
            promoted_output = True
            os.replace(authoring_stage, authoring)
            promoted_authoring = True
        print("ASTER_IDLE_360_CLEAN_V5=" + json.dumps({
            "directions": len(DIRECTIONS),
            "frames_per_direction": len(KEYS),
            "fps": 4,
            "atlas_resolution": [384, 1536],
            "preview": manifest["preview"],
            "visual_gate": manifest["qa"]["visual_gate"],
        }, ensure_ascii=False))
        return 0
    finally:
        if not promoted_output and output_stage.exists():
            shutil.rmtree(output_stage)
        if not promoted_authoring and authoring_stage.exists():
            shutil.rmtree(authoring_stage)


if __name__ == "__main__":
    raise SystemExit(main())
