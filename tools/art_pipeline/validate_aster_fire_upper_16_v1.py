#!/usr/bin/env python3
"""Validate the ASTER upper-only 16-direction Fire V1 candidate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
CELL = 384
FRAME_COUNT = 6
DIRECTIONS = (
    "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE",
)
MID = ("ESE", "SSE", "SSW", "WSW", "WNW", "NNW", "NNE", "ENE")
AXIAL = ("SSE", "SSW", "NNW", "NNE")
ANGLES = {direction: index * 22.5 for index, direction in enumerate(DIRECTIONS)}
RUNTIME = ROOT / "assets/units/operators/aster/fire_upper_16_v1"
AUTHOR = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_v1"
MANIFEST = RUNTIME / "ASTER_FIRE_UPPER_16_V1_MANIFEST.json"
AUTHOR_MANIFEST = AUTHOR / "ASTER_FIRE_UPPER_16_V1_MANIFEST.json"
ALIGNMENT = RUNTIME / "ASTER_MUZZLE_ALIGNMENT_16_V1.json"
AUTHOR_ALIGNMENT = AUTHOR / "ASTER_MUZZLE_ALIGNMENT_16_V1.json"
QA_PATH = AUTHOR / "ASTER_FIRE_UPPER_16_V1_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(relative: str) -> Path:
    return ROOT / Path(relative)


def angle(start: np.ndarray, end: np.ndarray) -> float:
    delta = end - start
    return math.degrees(math.atan2(float(delta[1]), float(delta[0]))) % 360.0


def difference(first: float, second: float) -> float:
    return abs((first - second + 180.0) % 360.0 - 180.0)


def raster_barrel(frame: np.ndarray, inner: np.ndarray, muzzle: np.ndarray) -> dict[str, float]:
    grid_y, grid_x = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    vector = muzzle - inner
    length2 = max(float(np.dot(vector, vector)), 1e-6)
    projection = ((grid_x - inner[0]) * vector[0] + (grid_y - inner[1]) * vector[1]) / length2
    closest_x = inner[0] + np.clip(projection, 0.0, 1.0) * vector[0]
    closest_y = inner[1] + np.clip(projection, 0.0, 1.0) * vector[1]
    distance = np.sqrt((grid_x - closest_x) ** 2 + (grid_y - closest_y) ** 2)
    corridor = (projection >= 0.08) & (projection <= 0.96) & (distance <= 5.5)
    visible = corridor & (frame[:, :, 3] > 18)
    support = float(np.count_nonzero(visible)) / max(float(np.count_nonzero(corridor)), 1.0)
    ys, xs = np.nonzero(visible)
    if len(xs) < 10:
        return {"support": support, "tangent": angle(inner, muzzle), "residual": 180.0}
    coordinates = np.column_stack((xs.astype(np.float32), ys.astype(np.float32)))
    coordinates -= coordinates.mean(axis=0, keepdims=True)
    _, vectors = np.linalg.eigh(coordinates.T @ coordinates)
    axis = vectors[:, -1]
    tangent = math.degrees(math.atan2(float(axis[1]), float(axis[0]))) % 180.0
    target = angle(inner, muzzle) % 180.0
    residual = abs((tangent - target + 90.0) % 180.0 - 90.0)
    return {"support": support, "tangent": tangent, "residual": residual}


def alpha_connection(frame: np.ndarray, hand: np.ndarray, inner: np.ndarray, muzzle: np.ndarray) -> dict[str, Any]:
    import cv2

    mask = frame[:, :, 3] > 12
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)

    def nearby_label(point: np.ndarray, radius: int) -> int:
        x, y = int(round(float(point[0]))), int(round(float(point[1])))
        x0, x1 = max(0, x - radius), min(CELL, x + radius + 1)
        y0, y1 = max(0, y - radius), min(CELL, y + radius + 1)
        values = labels[y0:y1, x0:x1]
        values = values[values > 0]
        return int(np.bincount(values).argmax()) if len(values) else 0

    hand_label = nearby_label(hand, 14)
    inner_label = nearby_label(inner, 10)
    muzzle_label = nearby_label(muzzle, 14)
    yy, xx = np.mgrid[0:CELL, 0:CELL]
    muzzle_roi = ((xx - muzzle[0]) ** 2 + (yy - muzzle[1]) ** 2) <= 30.0 ** 2
    global_muzzle_labels = np.unique(labels[muzzle_roi & mask])
    global_muzzle_labels = global_muzzle_labels[global_muzzle_labels > 0]
    local = (mask & muzzle_roi).astype(np.uint8)
    local = cv2.morphologyEx(local, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    local = cv2.dilate(local, np.ones((5, 5), np.uint8), iterations=1)
    local_count, _ = cv2.connectedComponents(local, connectivity=8)
    endpoint_envelopes = local_count - 1
    connected = hand_label != 0 and hand_label == inner_label == muzzle_label
    return {
        "alpha_components": count - 1,
        "hand_inner_muzzle_same_component": connected,
        "muzzle_global_component_count": int(len(global_muzzle_labels)),
        "muzzle_endpoint_envelope_clusters": int(endpoint_envelopes),
        "muzzle_hardware_clusters": int(endpoint_envelopes),
        "single_rifle_topology": connected and len(global_muzzle_labels) == 1 and endpoint_envelopes == 1,
    }


def main() -> int:
    failures: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    author_manifest = json.loads(AUTHOR_MANIFEST.read_text(encoding="utf-8"))
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    author_alignment = json.loads(AUTHOR_ALIGNMENT.read_text(encoding="utf-8"))
    if manifest != author_manifest:
        failures.append("runtime and author manifests differ")
    if alignment != author_alignment:
        failures.append("runtime and author 16-direction alignment differ")
    if tuple(manifest.get("directions", ())) != DIRECTIONS:
        failures.append("manifest direction order mismatch")
    if tuple(alignment.get("directions", ())) != DIRECTIONS:
        failures.append("alignment direction order mismatch")
    if manifest.get("costumeId") != "ASTER_COMBAT_SUIT_C01":
        failures.append("costumeId drift")
    qwen_authority = manifest.get("qwen_axial_static_master_authority", {})
    if (
        qwen_authority.get("direction_count") != 4
        or qwen_authority.get("native_resolution") != [1254, 1254]
        or qwen_authority.get("qwen_patch_resize_used") is not False
        or qwen_authority.get("local_qwen_only") is not True
        or qwen_authority.get("cloud_inference_calls") != 0
        or qwen_authority.get("krea2_calls") != 0
        or qwen_authority.get("c_drive_model_or_runtime_writes_by_pipeline") != 0
        or qwen_authority.get("c_drive_models_and_runtime_read_only") is not True
        or qwen_authority.get("work_products_inside_project") is not True
    ):
        failures.append("Qwen axial static-master/local-read-only contract invalid")
    upper_contract = manifest.get("upper_only_contract", {})
    if (
        upper_contract.get("approved_full_body_source_read_for_connected_upper_derivation") is not True
        or upper_contract.get("new_full_body_or_lower_generation") is not False
        or upper_contract.get("lower_asset_written") is not False
        or upper_contract.get("lower_pixels_output") is not False
    ):
        failures.append("upper-only/lower isolation contract is not locked")
    if upper_contract.get("baked_muzzle_vfx") is not False:
        failures.append("muzzle VFX marked baked")
    if manifest.get("muzzle_alignment_16_v1_sha256") != sha256(ALIGNMENT):
        failures.append("16-direction alignment SHA mismatch")
    if manifest.get("muzzle_alignment_16_v1") != ALIGNMENT.relative_to(ROOT).as_posix():
        failures.append("16-direction alignment path mismatch")

    contact = resolve(manifest["qa"]["contact"])
    barrel_contact = resolve(manifest["qa"]["barrel_contact"])
    affected_contact = resolve(manifest["qa"]["axial_mid_original_resolution_contact"])
    if sha256(contact) != manifest["qa"]["contact_sha256"]:
        failures.append("contact SHA mismatch")
    if sha256(barrel_contact) != manifest["qa"]["barrel_contact_sha256"]:
        failures.append("barrel contact SHA mismatch")
    if sha256(affected_contact) != manifest["qa"]["axial_mid_original_resolution_contact_sha256"]:
        failures.append("axial mid original-resolution contact SHA mismatch")
    for evidence_direction in AXIAL:
        evidence = manifest["qa"].get("native_runtime_gameplay_reviews", {}).get(evidence_direction)
        if evidence is None:
            failures.append(f"{evidence_direction}: missing native/runtime/gameplay review evidence")
            continue
        evidence_path = resolve(evidence["path"])
        if not evidence_path.is_file() or sha256(evidence_path) != evidence["sha256"]:
            failures.append(f"{evidence_direction}: review evidence missing or SHA mismatch")
            continue
        if Image.open(evidence_path).size != (1920, 1440):
            failures.append(f"{evidence_direction}: review evidence is not 1920x1440")
        if evidence.get("native_panel") != [1254, 1254] or evidence.get("runtime_panel") != [384, 384] or evidence.get("gameplay_panel") != [131, 131] or evidence.get("upscale_used") is not False:
            failures.append(f"{evidence_direction}: exact-scale review panel contract invalid")

    maximum_mid_endpoint_residual = 0.0
    maximum_mid_raster_residual = 0.0
    minimum_mid_support = 1.0
    rgba_files = 0
    transparent_rgb_violations = 0
    cardinal_byte_matches = 0
    connected_mid_frames = 0
    frame_results: dict[str, list[dict[str, Any]]] = {}
    for direction in DIRECTIONS:
        expected_angle = ANGLES[direction]
        if float(manifest["angles_degrees"].get(direction, -999)) != expected_angle:
            failures.append(f"{direction}: angle table mismatch")
        record = manifest["directions_output"].get(direction)
        calibration = alignment["calibration"].get(direction)
        if record is None or calibration is None:
            failures.append(f"{direction}: missing output/alignment record")
            continue
        if direction in AXIAL:
            for key in ("qwen_static_master", "qwen_static_master_sha256", "qwen_patch_donor", "qwen_patch_donor_sha256", "native_authority", "native_authority_sha256", "blender_guide", "blender_guide_sha256"):
                if key not in record:
                    failures.append(f"{direction}: missing {key} lineage")
            for path_key, hash_key in (("qwen_static_master", "qwen_static_master_sha256"), ("qwen_patch_donor", "qwen_patch_donor_sha256"), ("native_authority", "native_authority_sha256"), ("blender_guide", "blender_guide_sha256")):
                if path_key in record and (not resolve(record[path_key]).is_file() or sha256(resolve(record[path_key])) != record[hash_key]):
                    failures.append(f"{direction}: {path_key} missing or hash mismatch")
        atlas_path = resolve(record["output_atlas"])
        if not atlas_path.is_file() or sha256(atlas_path) != record["output_sha256"]:
            failures.append(f"{direction}: atlas missing or SHA mismatch")
            continue
        image = Image.open(atlas_path)
        if image.mode != "RGBA" or image.size != (CELL, CELL * FRAME_COUNT):
            failures.append(f"{direction}: atlas mode/size invalid: {image.mode} {image.size}")
            continue
        rgba_files += 1
        atlas = np.asarray(image.convert("RGBA"), dtype=np.uint8).reshape(FRAME_COUNT, CELL, CELL, 4)
        alpha_values = np.unique(atlas[:, :, :, 3])
        if 0 not in alpha_values or 255 not in alpha_values:
            failures.append(f"{direction}: alpha extrema do not contain 0 and 255")
        transparent = atlas[:, :, :, 3] == 0
        nonzero_transparent = int(np.count_nonzero(atlas[:, :, :, :3][transparent]))
        transparent_rgb_violations += nonzero_transparent
        if direction in MID and nonzero_transparent:
            failures.append(f"{direction}: transparent RGB is not zero ({nonzero_transparent})")
        if direction not in MID:
            source = resolve(record["source_atlas"])
            if sha256(source) == sha256(atlas_path) == record["source_sha256"]:
                cardinal_byte_matches += 1
            else:
                failures.append(f"{direction}: approved cardinal is not byte-identical")

        direction_frames: list[dict[str, Any]] = []
        for frame_index, frame_record in enumerate(record["frames"]):
            if frame_record.get("baked_muzzle_vfx") is not False:
                failures.append(f"{direction} F{frame_index:02d}: baked muzzle VFX")
            inner = np.asarray(frame_record["barrel_inner_xy"], dtype=np.float32)
            muzzle = np.asarray(frame_record["muzzle_xy"], dtype=np.float32)
            endpoint_tangent = angle(inner, muzzle)
            endpoint_residual = difference(endpoint_tangent, expected_angle)
            raster = raster_barrel(atlas[frame_index], inner, muzzle)
            hand = np.asarray(frame_record["hand_anchor_xy"], dtype=np.float32)
            connection = alpha_connection(atlas[frame_index], hand, inner, muzzle)
            if abs(raster["residual"] - float(frame_record["barrel_raster_residual_degrees"])) > 0.02:
                failures.append(f"{direction} F{frame_index:02d}: raster residual manifest drift")
            if direction in MID:
                maximum_mid_endpoint_residual = max(maximum_mid_endpoint_residual, endpoint_residual)
                maximum_mid_raster_residual = max(maximum_mid_raster_residual, raster["residual"])
                minimum_mid_support = min(minimum_mid_support, raster["support"])
                if endpoint_residual > 4.0 + 1e-5:
                    failures.append(f"{direction} F{frame_index:02d}: endpoint tangent residual {endpoint_residual:.3f} > 4")
                if raster["residual"] > 4.0 + 1e-5:
                    failures.append(f"{direction} F{frame_index:02d}: raster tangent residual {raster['residual']:.3f} > 4")
                if not connection["single_rifle_topology"]:
                    failures.append(f"{direction} F{frame_index:02d}: hand/inner/muzzle not one single-rifle alpha topology")
                else:
                    connected_mid_frames += 1
            direction_frames.append({
                "index": frame_index,
                "endpoint_tangent_degrees": round(endpoint_tangent, 4),
                "endpoint_target_residual_degrees": round(endpoint_residual, 4),
                "raster_tangent_degrees": round(raster["tangent"], 4),
                "raster_residual_degrees": round(raster["residual"], 4),
                "barrel_support_ratio": round(raster["support"], 6),
                "waist_anchor_xy": frame_record["waist_anchor_xy"],
                "single_rifle_topology": connection["single_rifle_topology"],
                "muzzle_global_component_count": connection["muzzle_global_component_count"],
                "muzzle_endpoint_envelope_clusters": connection["muzzle_endpoint_envelope_clusters"],
                "muzzle_hardware_clusters": connection["muzzle_hardware_clusters"],
            })
        frame_results[direction] = direction_frames

        contact_frame = record["frames"][2]
        for key in ("muzzle_xy", "barrel_inner_xy", "barrel_tangent_degrees", "waist_anchor_xy", "hand_anchor_xy"):
            if calibration.get(key) != contact_frame.get(key):
                failures.append(f"{direction}: alignment/contact frame {key} mismatch")

    if cardinal_byte_matches != 8:
        failures.append(f"approved cardinal byte matches {cardinal_byte_matches}/8")
    if manifest.get("visual_gate") != "HOLD_USER_REVIEW_REQUIRED" or manifest.get("candidate_status") != "HOLD":
        failures.append("candidate improperly claims visual promotion")
    if manifest.get("promotion_ready") is not False or alignment.get("promotion_ready") is not False:
        failures.append("candidate improperly claims promotion readiness")
    silhouette = manifest.get("qa", {}).get("silhouette_transition", {})
    if silhouette.get("gameplay_scale") != [131, 131] or silhouette.get("half_jump_max_ratio_of_original_45") != 0.8 or silhouette.get("imbalance_max_ratio") != 1.4:
        failures.append("silhouette midpoint gate contract missing")
    if silhouette.get("gate_pass") is not True:
        failures.append("silhouette midpoint gate failed")

    qa = {
        "schema": 1,
        "role": "ASTER fire_upper_16_v1 upper-only technical and tangent QA",
        "result": "PASS" if not failures else "FAIL",
        "candidate_status": "HOLD",
        "costumeId": manifest.get("costumeId"),
        "directions_validated": len(DIRECTIONS),
        "intermediate_frames_validated": len(MID) * FRAME_COUNT,
        "rgba_atlases": rgba_files,
        "approved_cardinal_byte_matches": cardinal_byte_matches,
        "connected_single_rifle_intermediate_frames": connected_mid_frames,
        "maximum_mid_endpoint_tangent_residual_degrees": round(maximum_mid_endpoint_residual, 4),
        "maximum_mid_raster_tangent_residual_degrees": round(maximum_mid_raster_residual, 4),
        "minimum_mid_barrel_support_ratio": round(minimum_mid_support, 6),
        "transparent_rgb_nonzero_channel_values": transparent_rgb_violations,
        "alignment": ALIGNMENT.relative_to(ROOT).as_posix(),
        "alignment_sha256": sha256(ALIGNMENT),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256(MANIFEST),
        "frames": frame_results,
        "failures": failures,
        "visual_gate": "HOLD_USER_REVIEW_REQUIRED",
        "production_expansion": "HOLD",
    }
    QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ASTER_FIRE_UPPER_16_V1_QA=" + json.dumps({
        "result": qa["result"],
        "candidate_status": qa["candidate_status"],
        "maximum_mid_raster_tangent_residual_degrees": qa["maximum_mid_raster_tangent_residual_degrees"],
        "minimum_mid_barrel_support_ratio": qa["minimum_mid_barrel_support_ratio"],
        "failures": len(failures),
        "qa": QA_PATH.relative_to(ROOT).as_posix(),
    }))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
