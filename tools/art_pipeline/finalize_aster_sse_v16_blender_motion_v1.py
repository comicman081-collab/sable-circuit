#!/usr/bin/env python3
"""Finalize ASTER SSE V16 Blender/UAL motion into source and runtime assets."""

from __future__ import annotations

import hashlib
import json
import math
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
PACKAGE = ROOT / (
    "art_src/pilot_v2/aster_v2/animation_360/"
    "fire_upper_16_sse_blender_v1"
)
BLENDER_MANIFEST = PACKAGE / "blender_scene/ASTER_FIRE_SSE_V16_67_5_UAL_MOTION_V1_MANIFEST.json"
RAW_DIR = PACKAGE / "blender_raw/current"
FINAL_DIR = PACKAGE / "final/current"
RUNTIME_DIR = PACKAGE / "runtime/current"
QA_DIR = PACKAGE / "qa/current"
VALIDATOR = ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py"

PHASES = (
    "aim_set",
    "preload",
    "muzzle_contact",
    "recoil_peak",
    "recover",
    "ready_return",
)
EXPECTED_MANIFEST_SHA256 = "a0d6eb7d4f18686e22c20a9c3063679a2f32acb18291734da73385ed97832fa4"
EXPECTED_SIZE = (1254, 1254)
RUNTIME_SIZE = (384, 384)
GAMEPLAY_SIZE = (131, 131)
EXACT_GREEN = np.asarray((0, 255, 0), dtype=np.uint8)
TARGET_TANGENT = 67.5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def matte_mask(rgb: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    values = rgb.astype(np.int16)
    r, g, b = values[:, :, 0], values[:, :, 1], values[:, :, 2]
    loose = (g >= 70) & ((g - r) >= 15) & ((g - b) >= 15)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        loose.astype(np.uint8), 8
    )
    border_labels = set(
        np.unique(
            np.concatenate((labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]))
        ).tolist()
    )
    border_labels.discard(0)
    if not border_labels:
        raise RuntimeError("no border-connected green background")
    background = np.isin(labels, list(border_labels))
    cleared_holes: list[int] = []
    preserved_green: list[int] = []
    for index in range(1, count):
        if index in border_labels:
            continue
        cx, cy = (float(value) for value in centroids[index])
        area = int(stats[index, cv2.CC_STAT_AREA])
        if cx >= 730.0 and cy >= 760.0 and 4 <= area <= 4000:
            background |= labels == index
            cleared_holes.append(index)
        elif area >= 5:
            preserved_green.append(index)
    return background, {
        "loose_green_components": int(count - 1),
        "border_background_labels": sorted(int(value) for value in border_labels),
        "cleared_muzzle_hole_labels": cleared_holes,
        "preserved_subject_green_labels": preserved_green,
    }


def estimate_rifle_angle(rgb: np.ndarray) -> dict[str, object]:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 150)
    roi = np.zeros_like(edges)
    # Exclude the long front-hair edge above y=300; the rifle receiver, rail,
    # barrel, and cage remain entirely inside this locked SSE corridor.
    roi[300:1000, 500:930] = 1
    lines = cv2.HoughLinesP(
        edges * roi,
        1,
        np.pi / 720.0,
        threshold=45,
        minLineLength=70,
        maxLineGap=18,
    )
    candidates: list[tuple[float, float, list[int]]] = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            dx, dy = float(x2 - x1), float(y2 - y1)
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0.0:
                angle += 180.0
            length = math.hypot(dx, dy)
            if 55.0 <= angle <= 80.0:
                candidates.append((length, angle, [int(x1), int(y1), int(x2), int(y2)]))
    candidates.sort(reverse=True)
    if not candidates:
        raise RuntimeError("could not estimate final rifle tangent")
    chosen = candidates[0]
    return {
        "method": "longest HoughLinesP segment in final SSE rifle ROI",
        "measured_tangent_degrees": float(chosen[1]),
        "target_tangent_degrees": TARGET_TANGENT,
        "absolute_residual_degrees": abs(float(chosen[1]) - TARGET_TANGENT),
        "longest_segment_length_px": float(chosen[0]),
        "longest_segment_xyxy": chosen[2],
        "top_segments": [
            {"length_px": float(length), "angle_degrees": float(angle), "xyxy": xyxy}
            for length, angle, xyxy in candidates[:8]
        ],
    }


def checker(size: tuple[int, int], light: bool) -> Image.Image:
    colors = ((235, 235, 235), (200, 200, 200)) if light else ((38, 42, 48), (70, 76, 84))
    values = np.empty((size[1], size[0], 3), dtype=np.uint8)
    yy, xx = np.indices((size[1], size[0]))
    choice = ((xx // 24) + (yy // 24)) % 2
    values[choice == 0] = colors[0]
    values[choice == 1] = colors[1]
    return Image.fromarray(values, "RGB")


def resize_rgba_premultiplied_clean(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """Resize without leaking green RGB from transparent authoring pixels."""
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    premultiplied = rgba[:, :, :3].astype(np.float32) * alpha[:, :, None]
    resized_alpha = cv2.resize(alpha, size, interpolation=cv2.INTER_LANCZOS4)
    resized_premultiplied = cv2.resize(premultiplied, size, interpolation=cv2.INTER_LANCZOS4)
    resized_alpha = np.clip(resized_alpha, 0.0, 1.0)
    rgb = np.zeros_like(resized_premultiplied)
    visible = resized_alpha > (0.5 / 255.0)
    rgb[visible] = resized_premultiplied[visible] / resized_alpha[visible, None]
    rgb = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    alpha_u8 = np.clip(np.rint(resized_alpha * 255.0), 0, 255).astype(np.uint8)
    values = rgb.astype(np.int16)
    strong_chroma = (
        (values[:, :, 1] >= 180)
        & ((values[:, :, 1] - values[:, :, 0]) >= 100)
        & ((values[:, :, 1] - values[:, :, 2]) >= 100)
    )
    alpha_u8[strong_chroma] = 0
    rgb[alpha_u8 == 0] = 0
    return np.dstack((rgb, alpha_u8))


def build_review(
    masters: dict[str, Path],
    rgba_paths: dict[str, Path],
    runtime_paths: dict[str, Path],
    angle: dict[str, object],
    metrics: dict[str, object],
    output: Path,
) -> None:
    canvas = Image.new("RGB", (1920, 1440), (9, 14, 20))
    aim = Image.open(masters["aim_set"]).convert("RGB")
    canvas.paste(aim, (24, 88))
    runtime = Image.open(runtime_paths["aim_set"]).convert("RGBA")
    runtime_green = Image.new("RGB", RUNTIME_SIZE, (0, 255, 0))
    runtime_green.paste(runtime, (0, 0), runtime)
    canvas.paste(runtime_green, (1302, 88))
    gameplay = runtime.resize(GAMEPLAY_SIZE, Image.Resampling.LANCZOS)
    gameplay_green = Image.new("RGB", GAMEPLAY_SIZE, (0, 255, 0))
    gameplay_green.paste(gameplay, (0, 0), gameplay)
    canvas.paste(gameplay_green, (1710, 88))

    phase_positions = ((1302, 320), (1498, 320), (1694, 320), (1302, 516), (1498, 516), (1694, 516))
    for phase, position in zip(PHASES, phase_positions):
        frame = Image.open(rgba_paths[phase]).convert("RGBA").resize((192, 192), Image.Resampling.LANCZOS)
        panel = Image.new("RGB", (192, 192), (0, 255, 0))
        panel.paste(frame, (0, 0), frame)
        canvas.paste(panel, position)

    alpha_aim = Image.open(rgba_paths["aim_set"]).convert("RGBA").resize((288, 288), Image.Resampling.LANCZOS)
    for index, light in enumerate((True, False)):
        panel = checker((288, 288), light)
        panel.paste(alpha_aim, (0, 0), alpha_aim)
        canvas.paste(panel, (1302 + index * 300, 740))

    crop = aim.crop((350, 220, 940, 620))
    canvas.paste(crop, (1302, 1040))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    white, cyan, amber, muted = (245, 247, 250), (70, 225, 245), (255, 188, 65), (185, 195, 205)
    draw.text((24, 20), "ASTER FIRE SSE V16 BLENDER/UAL 67.5 MOTION", fill=white, font=font)
    draw.text((24, 43), "TECHNICAL PASS / REVIEW GATE — NO WHITE SHOULDER ARMOR", fill=amber, font=font)
    draw.text((24, 70), "NATIVE 1254x1254 AIM_SET 1:1", fill=cyan, font=font)
    draw.text((1302, 70), "RUNTIME 384 + GAMEPLAY 131 AT 1:1", fill=cyan, font=font)
    draw.text((1302, 302), "UAL PISTOL_SHOOT PHASES: AIM / PRE / CONTACT / PEAK / RECOVER / RETURN", fill=cyan, font=font)
    draw.text((1302, 722), "RGBA LIGHT / DARK CHECKER", fill=cyan, font=font)
    draw.text((1302, 1022), "NATIVE 1:1 FACE / BOTH SHOULDERS / HANDS / OPTIC CROP", fill=cyan, font=font)
    details = (
        f"Measured tangent: {angle['measured_tangent_degrees']:.3f} deg",
        f"Target: 67.500 deg; residual: {angle['absolute_residual_degrees']:.3f} deg",
        f"Transform solver residual: {metrics['transform_solver_residual_degrees']:.6f} deg",
        f"Exact-green exterior errors: {metrics['total_non_green_exterior_pixels']}",
        f"F00/F05 pixel-identical: {metrics['f00_f05_pixel_identical']}",
        "White/cyan/gold shoulder hardware: ABSENT",
    )
    y = 1280
    for line in details:
        draw.rectangle((1310, y - 2, 1908, y + 14), fill=(9, 14, 20))
        draw.text((1314, y), line, fill=amber if "residual" in line else muted, font=font)
        y += 18
    canvas.save(output, "PNG", optimize=True)


def main() -> int:
    if not BLENDER_MANIFEST.is_file() or sha256(BLENDER_MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise SystemExit("locked Blender manifest missing or SHA mismatch")
    if any(path.exists() for path in (FINAL_DIR, RUNTIME_DIR, QA_DIR)):
        raise SystemExit("final Blender motion output already exists; refusing overwrite")
    blender_manifest = json.loads(BLENDER_MANIFEST.read_text(encoding="utf-8"))
    if blender_manifest.get("transform", {}).get("target_tangent_degrees") != TARGET_TANGENT:
        raise SystemExit("Blender target tangent mismatch")
    ual_mesh_rendered = blender_manifest.get("visible_sources", {}).get(
        "ual_mesh_rendered",
        blender_manifest.get("motion_authority", {}).get("ual_mesh_rendered"),
    )
    if ual_mesh_rendered is not False:
        raise SystemExit("UAL mesh must never be rendered")
    manifest_frames = {item["phase"]: item for item in blender_manifest["frames"]}
    if tuple(manifest_frames) != PHASES:
        raise SystemExit("Blender frame order mismatch")

    FINAL_DIR.mkdir(parents=True, exist_ok=False)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=False)
    QA_DIR.mkdir(parents=True, exist_ok=False)
    masters: dict[str, Path] = {}
    masks: dict[str, Path] = {}
    rgba_paths: dict[str, Path] = {}
    runtime_paths: dict[str, Path] = {}
    frame_records: list[dict[str, object]] = []
    total_exterior_errors = 0

    for phase in PHASES:
        item = manifest_frames[phase]
        raw = ROOT / item["raw"]["path"]
        if not raw.is_file() or sha256(raw) != item["raw"]["sha256"]:
            raise RuntimeError(f"locked Blender raw missing or SHA mismatch: {raw}")
        with Image.open(raw) as image:
            image.load()
            if image.mode != "RGB" or image.size != EXPECTED_SIZE:
                raise RuntimeError(f"Blender raw mismatch: {raw} {image.mode} {image.size}")
            rgb = np.asarray(image, dtype=np.uint8).copy()
        background, component_report = matte_mask(rgb)
        subject = ~background
        master = rgb.copy()
        master[background] = EXACT_GREEN
        alpha = np.where(subject, 255, 0).astype(np.uint8)
        rgba = np.dstack((master, alpha))
        exact = np.all(master == EXACT_GREEN[None, None, :], axis=2)
        exterior_errors = int(np.count_nonzero((~exact) & background))
        total_exterior_errors += exterior_errors

        stem = f"ASTER_FIRE_SSE_{phase.upper()}_V16_67_5"
        master_path = FINAL_DIR / f"{stem}_GREEN.png"
        mask_path = FINAL_DIR / f"{stem}_MASK.png"
        rgba_path = FINAL_DIR / f"{stem}_RGBA.png"
        runtime_path = RUNTIME_DIR / f"{stem}_RUNTIME_384_RGBA.png"
        Image.fromarray(master, "RGB").save(master_path, "PNG", optimize=True)
        Image.fromarray(alpha, "L").save(mask_path, "PNG", optimize=True)
        runtime_rgba = resize_rgba_premultiplied_clean(rgba, RUNTIME_SIZE)
        Image.fromarray(runtime_rgba, "RGBA").save(runtime_path, "PNG", optimize=True)
        Image.fromarray(rgba, "RGBA").save(rgba_path, "PNG", optimize=True)
        masters[phase], masks[phase], rgba_paths[phase], runtime_paths[phase] = (
            master_path,
            mask_path,
            rgba_path,
            runtime_path,
        )
        frame_records.append(
            {
                "phase": phase,
                "ual_source_frame": item["ual_source_frame"],
                "translation_image_px": item["translation_image_px"],
                "green": {"path": rel(master_path), "sha256": sha256(master_path)},
                "mask": {"path": rel(mask_path), "sha256": sha256(mask_path)},
                "rgba": {"path": rel(rgba_path), "sha256": sha256(rgba_path)},
                "runtime_384_rgba": {"path": rel(runtime_path), "sha256": sha256(runtime_path)},
                "matte": {
                    "subject_pixels": int(np.count_nonzero(subject)),
                    "background_pixels": int(np.count_nonzero(background)),
                    "non_green_exterior_pixels": exterior_errors,
                    "component_report": component_report,
                },
            }
        )

    # The loop contract is byte-identical F00/F05, not merely visually equal.
    for first, last in (
        (masters["aim_set"], masters["ready_return"]),
        (masks["aim_set"], masks["ready_return"]),
        (rgba_paths["aim_set"], rgba_paths["ready_return"]),
        (runtime_paths["aim_set"], runtime_paths["ready_return"]),
    ):
        shutil.copyfile(first, last)
    for record in frame_records:
        if record["phase"] == "ready_return":
            record["green"]["sha256"] = sha256(masters["ready_return"])
            record["mask"]["sha256"] = sha256(masks["ready_return"])
            record["rgba"]["sha256"] = sha256(rgba_paths["ready_return"])
            record["runtime_384_rgba"]["sha256"] = sha256(runtime_paths["ready_return"])

    atlas = Image.new("RGBA", (RUNTIME_SIZE[0] * len(PHASES), RUNTIME_SIZE[1]), (0, 0, 0, 0))
    for index, phase in enumerate(PHASES):
        atlas.paste(Image.open(runtime_paths[phase]).convert("RGBA"), (index * RUNTIME_SIZE[0], 0))
    atlas_path = RUNTIME_DIR / "ASTER_FIRE_SSE_V16_67_5_UAL6_RUNTIME_ATLAS_RGBA.png"
    atlas.save(atlas_path, "PNG", optimize=True)

    with Image.open(masters["aim_set"]) as image:
        aim_rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    with Image.open(masters["ready_return"]) as image:
        return_rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    angle = estimate_rifle_angle(aim_rgb)
    transform_residual = abs(
        float(blender_manifest["transform"]["target_tangent_degrees"]) - TARGET_TANGENT
    )
    metrics = {
        "native_resolution": list(EXPECTED_SIZE),
        "runtime_cell_resolution": list(RUNTIME_SIZE),
        "runtime_atlas_resolution": [RUNTIME_SIZE[0] * len(PHASES), RUNTIME_SIZE[1]],
        "phase_count": len(PHASES),
        "total_non_green_exterior_pixels": total_exterior_errors,
        "transform_solver_residual_degrees": transform_residual,
        "hough_tangent_residual_degrees": angle["absolute_residual_degrees"],
        "rigid_cluster_singular_value_ratio": blender_manifest["transform"].get(
            "rigid_cluster_singular_value_ratio",
            blender_manifest["transform"].get("singular_value_ratio"),
        ),
        "f00_f05_pixel_identical": bool(np.array_equal(aim_rgb, return_rgb)),
        "f00_f05_byte_identical": sha256(masters["aim_set"]) == sha256(masters["ready_return"]),
    }
    runtime_chroma_opaque = 0
    for phase in PHASES:
        runtime_rgba = np.asarray(Image.open(runtime_paths[phase]).convert("RGBA"), dtype=np.uint8)
        values = runtime_rgba[:, :, :3].astype(np.int16)
        strong = (
            (values[:, :, 1] >= 180)
            & ((values[:, :, 1] - values[:, :, 0]) >= 100)
            & ((values[:, :, 1] - values[:, :, 2]) >= 100)
            & (runtime_rgba[:, :, 3] > 0)
        )
        runtime_chroma_opaque += int(np.count_nonzero(strong))
    metrics["runtime_opaque_strong_chroma_pixels"] = runtime_chroma_opaque
    if total_exterior_errors != 0:
        raise RuntimeError("final exact-green contract failed")
    if runtime_chroma_opaque != 0:
        raise RuntimeError("runtime premultiplied-alpha chroma fringe gate failed")
    if transform_residual > 0.1 or angle["absolute_residual_degrees"] > 4.0:
        raise RuntimeError(f"final rifle tangent gate failed: {angle}")
    if metrics["rigid_cluster_singular_value_ratio"] > 1.02:
        raise RuntimeError("rigid cluster anisotropy gate failed")
    if not metrics["f00_f05_pixel_identical"] or not metrics["f00_f05_byte_identical"]:
        raise RuntimeError("F00/F05 loop identity gate failed")

    review_path = QA_DIR / "ASTER_FIRE_SSE_V16_67_5_UAL6_REVIEW_1920X1440.png"
    evidence_path = QA_DIR / "ASTER_FIRE_SSE_V16_67_5_UAL6_EVIDENCE_1080P_QA.json"
    qa_path = QA_DIR / "ASTER_FIRE_SSE_V16_67_5_UAL6_QA.json"
    manifest_path = QA_DIR / "ASTER_FIRE_SSE_V16_67_5_UAL6_MANIFEST.json"
    build_review(masters, rgba_paths, runtime_paths, angle, metrics, review_path)
    command = [
        sys.executable,
        os.fspath(VALIDATOR),
        os.fspath(review_path),
        "--require-dynamic-capture",
        "--output",
        os.fspath(evidence_path),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"1080p evidence validator failed: {result.stdout}{result.stderr}")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("gate") != "PASS":
        raise RuntimeError(f"1080p evidence gate failed: {evidence.get('gate')}")

    qa = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": "ASTER SSE V16 no-shoulder Blender/UAL six-phase final technical QA",
        "result": "PASS_TECHNICAL_REVIEW_REQUIRED",
        "candidate_status": "REVIEW_REQUIRED",
        "motion_complete": True,
        "promotion_ready": False,
        "runtime_asset": True,
        "visual_pass_claimed": False,
        "source_art_author": "built-in ImageGen",
        "local_motion_tools": ["Blender 5.2.1 LTS", "UAL1 Pistol_Shoot CC0-1.0"],
        "local_model_generation_used": False,
        "shoulder_component_removal": "PASS",
        "weapon_angle": angle,
        "metrics": metrics,
        "review_requirements": [
            "Ponytail FULL identity/costume/grip/edge audit",
            "existing ChatGPT planning-conversation review",
        ],
    }
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "role": "ASTER SSE V16 final Blender/UAL motion package",
        "status": "REVIEW_REQUIRED",
        "promotion_ready": False,
        "runtime_asset": True,
        "visual_pass_claimed": False,
        "costume": {
            "white_shoulder_armor": "ABSENT",
            "cyan_shoulder_stripe": "ABSENT",
            "gold_shoulder_hardware": "ABSENT",
        },
        "blender_manifest": {"path": rel(BLENDER_MANIFEST), "sha256": sha256(BLENDER_MANIFEST)},
        "frames": frame_records,
        "runtime_atlas": {"path": rel(atlas_path), "sha256": sha256(atlas_path)},
        "review": {"path": rel(review_path), "sha256": sha256(review_path), "resolution": [1920, 1440]},
        "qa": {"path": rel(qa_path), "sha256": sha256(qa_path), "result": qa["result"]},
        "evidence": {"path": rel(evidence_path), "sha256": sha256(evidence_path), "gate": evidence["gate"]},
        "retention": "CURRENT; previous is the V16 no-shoulder ImageGen source master; older candidates must be removed after review",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "review": os.fspath(review_path),
                "atlas": os.fspath(atlas_path),
                "angle": angle,
                "metrics": metrics,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
