#!/usr/bin/env python3
"""Finalize the 16-direction ASTER Blender/UAL render into runtime atlases."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2"
BLENDER_MANIFEST = PACKAGE / "blender_scene/ASTER_FIRE16_NO_SHOULDER_UAL6_V2_MANIFEST.json"
FINAL_DIR = PACKAGE / "final/current"
RUNTIME_DIR = PACKAGE / "runtime/current"
QA_DIR = PACKAGE / "qa/current"
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

PHASES = ("aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return")
DIRECTIONS = ("E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE")
EXPECTED_SIZE = (1254, 1254)
RUNTIME_SIZE = (384, 384)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def matte_mask(rgb: np.ndarray) -> tuple[np.ndarray, dict[str, int]]:
    values = rgb.astype(np.int16)
    r, g, b = values[:, :, 0], values[:, :, 1], values[:, :, 2]
    loose = (g >= 80) & ((g - r) >= 20) & ((g - b) >= 20)
    exact_seed = (g >= 245) & (r <= 12) & (b <= 12)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(loose.astype(np.uint8), 8)
    border_labels = set(np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))).tolist())
    border_labels.discard(0)
    background = np.isin(labels, list(border_labels))
    seeded_hole_components = 0
    preserved_green_components = 0
    for index in range(1, count):
        if index in border_labels:
            continue
        component = labels == index
        area = int(stats[index, cv2.CC_STAT_AREA])
        seed_count = int(np.count_nonzero(exact_seed & component))
        if seed_count >= 4 and area <= 12000:
            background |= component
            seeded_hole_components += 1
        else:
            preserved_green_components += 1
    return background, {
        "loose_green_components": int(count - 1),
        "border_background_components": len(border_labels),
        "seeded_hole_components": seeded_hole_components,
        "preserved_green_components": preserved_green_components,
    }


def resize_rgba_clean(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    premultiplied = rgba[:, :, :3].astype(np.float32) * alpha[:, :, None]
    resized_alpha = np.clip(cv2.resize(alpha, size, interpolation=cv2.INTER_LANCZOS4), 0.0, 1.0)
    resized_premultiplied = cv2.resize(premultiplied, size, interpolation=cv2.INTER_LANCZOS4)
    rgb = np.zeros_like(resized_premultiplied)
    visible = resized_alpha > (0.5 / 255.0)
    rgb[visible] = resized_premultiplied[visible] / resized_alpha[visible, None]
    rgb = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    alpha_u8 = np.clip(np.rint(resized_alpha * 255.0), 0, 255).astype(np.uint8)
    rgb[alpha_u8 == 0] = 0
    return np.dstack((rgb, alpha_u8))


def fit_rgba(path: Path, box: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    image.thumbnail(box, Image.Resampling.LANCZOS)
    return image


def build_contact(runtime_aim: dict[str, Path], output: Path) -> None:
    canvas = Image.new("RGB", (1920, 1080), (8, 13, 20))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 18), "ASTER FIRE16 — IMAGEGEN DIRECTIONS + BLENDER/UAL SIX-PHASE RUNTIME", fill=(245, 247, 250), font=font)
    draw.text((24, 38), "16 TRUE POSES / BOTH SHOULDERS PLAIN NAVY / NATIVE REVIEW FRAME 1920x1080", fill=(69, 224, 244), font=font)
    cell_w, cell_h, top = 480, 255, 60
    for index, direction in enumerate(DIRECTIONS):
        col, row = index % 4, index // 4
        x, y = col * cell_w, top + row * cell_h
        panel = Image.new("RGB", (cell_w, cell_h), (0, 255, 0))
        sprite = fit_rgba(runtime_aim[direction], (238, 238))
        panel.paste(sprite, ((cell_w - sprite.width) // 2, 8), sprite)
        canvas.paste(panel, (x, y))
        draw.rectangle((x + 8, y + 8, x + 74, y + 30), fill=(8, 13, 20))
        draw.text((x + 16, y + 14), direction, fill=(255, 201, 74), font=font)
    canvas.save(output, "PNG", optimize=True)


def build_native_details(green_aim: dict[str, Path], output: Path) -> None:
    choices = ("E", "SSE", "S", "W", "NW", "N", "NE", "ENE")
    canvas = Image.new("RGB", (1920, 1080), (8, 13, 20))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((24, 18), "ASTER FIRE16 NATIVE 1:1 DETAIL CROPS — FACE / SHOULDERS / TWO-HAND GRIP / RIFLE", fill=(245, 247, 250), font=font)
    draw.text((24, 38), "Each 480x480 panel is an unscaled crop from a native 1254x1254 Blender frame.", fill=(69, 224, 244), font=font)
    for index, direction in enumerate(choices):
        source = Image.open(green_aim[direction]).convert("RGB")
        crop = source.crop((360, 170, 840, 650))
        x, y = (index % 4) * 480, 70 + (index // 4) * 500
        canvas.paste(crop, (x, y))
        draw.rectangle((x + 8, y + 8, x + 74, y + 30), fill=(8, 13, 20))
        draw.text((x + 16, y + 14), direction, fill=(255, 201, 74), font=font)
    canvas.save(output, "PNG", optimize=True)


def main() -> int:
    if not BLENDER_MANIFEST.is_file():
        raise SystemExit("Blender manifest missing")
    if any(path.exists() for path in (FINAL_DIR, RUNTIME_DIR, QA_DIR)):
        raise SystemExit("final/runtime/qa output already exists; refusing overwrite")
    blender = json.loads(BLENDER_MANIFEST.read_text(encoding="utf-8"))
    if blender.get("motion_authority", {}).get("ual_mesh_rendered") is not False:
        raise RuntimeError("UAL mesh render contract failed")
    direction_items = {item["direction"]: item for item in blender["directions"]}
    if tuple(direction_items) != DIRECTIONS:
        raise RuntimeError("direction order mismatch")
    FINAL_DIR.mkdir(parents=True)
    RUNTIME_DIR.mkdir(parents=True)
    QA_DIR.mkdir(parents=True)

    records: list[dict[str, object]] = []
    green_aim: dict[str, Path] = {}
    runtime_aim: dict[str, Path] = {}
    alpha_contract_errors = 0
    for direction in DIRECTIONS:
        item = direction_items[direction]
        frame_items = {frame["phase"]: frame for frame in item["frames"]}
        if tuple(frame_items) != PHASES:
            raise RuntimeError(f"phase order mismatch: {direction}")
        final_direction = FINAL_DIR / direction
        runtime_direction = RUNTIME_DIR / direction
        final_direction.mkdir()
        runtime_direction.mkdir()
        phase_records: list[dict[str, object]] = []
        phase_green: dict[str, Path] = {}
        phase_rgba: dict[str, Path] = {}
        phase_runtime: dict[str, Path] = {}
        for phase in PHASES:
            source_frame = frame_items[phase]
            raw = ROOT / source_frame["raw"]["path"]
            if not raw.is_file() or sha256(raw) != source_frame["raw"]["sha256"]:
                raise RuntimeError(f"raw SHA mismatch: {raw}")
            with Image.open(raw) as image:
                image.load()
                if image.size != EXPECTED_SIZE:
                    raise RuntimeError(f"raw size mismatch: {raw} {image.size}")
                rgb = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
            background, matte_report = matte_mask(rgb)
            subject = ~background
            green = rgb.copy()
            green[background] = EXACT_GREEN
            alpha = np.where(subject, 255, 0).astype(np.uint8)
            rgba = np.dstack((green, alpha))
            green_path = final_direction / f"ASTER_FIRE_{direction}_{phase.upper()}_NO_SHOULDER_GREEN.png"
            rgba_path = final_direction / f"ASTER_FIRE_{direction}_{phase.upper()}_NO_SHOULDER_RGBA.png"
            runtime_path = runtime_direction / f"ASTER_FIRE_{direction}_{phase.upper()}_NO_SHOULDER_RUNTIME_384_RGBA.png"
            Image.fromarray(green, "RGB").save(green_path, "PNG", optimize=True)
            Image.fromarray(rgba, "RGBA").save(rgba_path, "PNG", optimize=True)
            Image.fromarray(resize_rgba_clean(rgba, RUNTIME_SIZE), "RGBA").save(runtime_path, "PNG", optimize=True)
            phase_green[phase], phase_rgba[phase], phase_runtime[phase] = green_path, rgba_path, runtime_path
            phase_records.append({
                "phase": phase,
                "ual_source_frame": source_frame["ual_source_frame"],
                "translation_image_px": source_frame["translation_image_px"],
                "green": {"path": rel(green_path), "sha256": sha256(green_path)},
                "rgba": {"path": rel(rgba_path), "sha256": sha256(rgba_path)},
                "runtime_384_rgba": {"path": rel(runtime_path), "sha256": sha256(runtime_path)},
                "matte": matte_report,
            })
        for first, last in ((phase_green["aim_set"], phase_green["ready_return"]), (phase_rgba["aim_set"], phase_rgba["ready_return"]), (phase_runtime["aim_set"], phase_runtime["ready_return"])):
            shutil.copyfile(first, last)
        for record in phase_records:
            if record["phase"] == "ready_return":
                record["green"]["sha256"] = sha256(phase_green["ready_return"])
                record["rgba"]["sha256"] = sha256(phase_rgba["ready_return"])
                record["runtime_384_rgba"]["sha256"] = sha256(phase_runtime["ready_return"])
        atlas = Image.new("RGBA", (RUNTIME_SIZE[0] * len(PHASES), RUNTIME_SIZE[1]), (0, 0, 0, 0))
        for index, phase in enumerate(PHASES):
            atlas.paste(Image.open(phase_runtime[phase]).convert("RGBA"), (index * RUNTIME_SIZE[0], 0))
        atlas_path = runtime_direction / f"ASTER_FIRE_{direction}_NO_SHOULDER_UAL6_ATLAS_RGBA.png"
        atlas.save(atlas_path, "PNG", optimize=True)
        aim = np.asarray(Image.open(phase_rgba["aim_set"]).convert("RGBA"), dtype=np.uint8)
        ready = np.asarray(Image.open(phase_rgba["ready_return"]).convert("RGBA"), dtype=np.uint8)
        transparent_rgb_errors = int(np.count_nonzero(np.any(aim[:, :, :3] != EXACT_GREEN, axis=2) & (aim[:, :, 3] == 0)))
        alpha_contract_errors += transparent_rgb_errors
        green_aim[direction] = phase_green["aim_set"]
        runtime_aim[direction] = phase_runtime["aim_set"]
        records.append({
            "direction": direction,
            "screen_heading_degrees": item["screen_heading_degrees"],
            "source": item["source"],
            "frames": phase_records,
            "runtime_atlas": {"path": rel(atlas_path), "sha256": sha256(atlas_path), "resolution": [2304, 384]},
            "loop_pixel_identical": bool(np.array_equal(aim, ready)),
            "transparent_rgb_contract_errors": transparent_rgb_errors,
        })

    contact = QA_DIR / "ASTER_FIRE16_NO_SHOULDER_UAL6_CONTACT_1920X1080.png"
    details = QA_DIR / "ASTER_FIRE16_NO_SHOULDER_NATIVE_DETAILS_1920X1080.png"
    build_contact(runtime_aim, contact)
    build_native_details(green_aim, details)
    evidence_records = []
    for image in (contact, details):
        evidence_path = image.with_name(image.stem + "_EVIDENCE.json")
        result = subprocess.run([sys.executable, os.fspath(VALIDATOR), os.fspath(image), "--output", os.fspath(evidence_path)], cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stdout + result.stderr)
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence.get("gate") != "PASS":
            raise RuntimeError(f"1080p evidence gate failed: {image}")
        evidence_records.append({"image": rel(image), "evidence": rel(evidence_path), "gate": evidence["gate"]})

    qa = {
        "schema": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS_TECHNICAL_REVIEW_REQUIRED",
        "direction_count": len(records), "phase_count_per_direction": len(PHASES), "frame_count": len(records) * len(PHASES),
        "native_resolution": list(EXPECTED_SIZE), "runtime_cell_resolution": list(RUNTIME_SIZE),
        "all_loops_identical": all(record["loop_pixel_identical"] for record in records),
        "transparent_rgb_contract_errors": alpha_contract_errors,
        "both_shoulders_contract": "PLAIN_NAVY_FABRIC_REQUIRES_VISUAL_AUDIT",
        "visual_pass_claimed": False,
        "review_requirements": ["Ponytail FULL audit", "existing ChatGPT planning-conversation review", "native 1920x1080 dynamic browser capture"],
    }
    if not qa["all_loops_identical"] or alpha_contract_errors != 0:
        raise RuntimeError(f"runtime contract failure: {qa}")
    qa_path = QA_DIR / "ASTER_FIRE16_NO_SHOULDER_UAL6_QA.json"
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": "ASTER true sixteen-direction no-shoulder Blender/UAL runtime package",
        "status": "REVIEW_REQUIRED", "promotion_ready": False, "runtime_asset": True, "visual_pass_claimed": False,
        "visible_source_author": "built-in ImageGen", "local_motion_tools": ["Blender 5.2.1 LTS", "UAL1 Pistol_Shoot CC0-1.0"],
        "blender_manifest": {"path": rel(BLENDER_MANIFEST), "sha256": sha256(BLENDER_MANIFEST)},
        "directions": records,
        "qa": {"path": rel(qa_path), "sha256": sha256(qa_path), "result": qa["result"]},
        "evidence": evidence_records,
        "retention": "CURRENT plus exactly one immediately previous candidate; remove older rejected intermediates after replacement verification",
    }
    manifest_path = QA_DIR / "ASTER_FIRE16_NO_SHOULDER_UAL6_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": os.fspath(manifest_path), "directions": 16, "frames": 96, "contact": os.fspath(contact)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
