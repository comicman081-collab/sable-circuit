#!/usr/bin/env python3
"""Validate ASTER Fire16 segmented-upper parser and exact-rifle contract."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_segmented_rig_v1"
MANIFEST = OUTPUT / "ASTER_FIRE16_SEGMENTED_UPPER_RIG_V1_MANIFEST.json"
GUIDES = OUTPUT / "ASTER_FIRE16_SEGMENTED_UPPER_GUIDES_V1.json"
CALIBRATION_SCHEMA = OUTPUT / "ASTER_FIRE16_SEGMENTED_UPPER_CALIBRATION_SCHEMA_V1.json"
QA = OUTPUT / "ASTER_FIRE16_SEGMENTED_UPPER_RIG_V1_QA.json"
CURVES = (
    ROOT
    / "art_src/pilot_v2/aster_v2/animation_360/ual_fire_upper_v1"
    / "ASTER_UAL1_PISTOL_SHOOT_UPPER_CURVES_V1.json"
)
EXPECTED_CURVE_SHA = "e840e718121f40893d58351d35267a66cb81f30402e7df0c98137606cc13a876"
DIRECTIONS = {"SSE": 67.5, "SSW": 112.5, "NNW": 247.5, "NNE": 292.5}
PHASES = ["aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(payload: dict[str, Any], destination: Path) -> None:
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, destination)


def angular_error(measured: float, target: float) -> float:
    return abs(((measured - target + 180.0) % 360.0) - 180.0)


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(MANIFEST.is_file(), "manifest missing")
    require(GUIDES.is_file(), "guides missing")
    require(CALIBRATION_SCHEMA.is_file(), "calibration schema missing")
    require(CURVES.is_file(), "curve authority missing")
    if not MANIFEST.is_file() or not GUIDES.is_file() or not CURVES.is_file() or not CALIBRATION_SCHEMA.is_file():
        raise RuntimeError(errors)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    guides = json.loads(GUIDES.read_text(encoding="utf-8-sig"))
    curves = json.loads(CURVES.read_text(encoding="utf-8-sig"))
    calibration_schema = json.loads(CALIBRATION_SCHEMA.read_text(encoding="utf-8-sig"))

    require(sha256(CURVES) == EXPECTED_CURVE_SHA, "curve authority hash mismatch")
    require(manifest.get("curve_authority", {}).get("sha256") == EXPECTED_CURVE_SHA, "manifest curve hash mismatch")
    require(curves.get("action", {}).get("name") == "Pistol_Shoot", "curve action mismatch")
    require(curves.get("action", {}).get("sample_frames") == [0.0, 3.0, 6.0, 9.0, 12.0, 15.0], "curve sample frames mismatch")
    require(curves.get("action", {}).get("sample_labels") == PHASES, "curve phase labels mismatch")
    require(curves.get("source", {}).get("motion_only") is True, "UAL source must be motion-only")
    require(curves.get("source", {}).get("license") == "CC0-1.0", "UAL source license mismatch")

    require(manifest.get("candidate_status") == "HOLD_USER_REVIEW_REQUIRED", "candidate must remain HOLD")
    require(manifest.get("visual_gate") == "HOLD_USER_REVIEW_REQUIRED", "visual gate must remain HOLD")
    require(manifest.get("promotion_ready") is False, "promotion_ready must be false")
    require(manifest.get("runtime_eligible") is False, "runtime_eligible must be false")
    require(manifest.get("scope", {}).get("runtime_atlas_generated") is False, "runtime atlas generation prohibited")
    require(manifest.get("scope", {}).get("runtime_files_modified") is False, "runtime mutation prohibited")
    require(manifest.get("scope", {}).get("blend_file_written") is False, "blend output prohibited")
    require(manifest.get("parser_gate", {}).get("result") == "PASS", "parser gate failed")
    require(manifest.get("fixture_free_geometry_gate", {}).get("result") == "PASS", "fixture-free geometry gate failed")
    deformation_gate = manifest.get("ual_deformation_gate", {})
    require(deformation_gate.get("result") == "PASS", "UAL deformation guide gate failed")
    require(int(deformation_gate.get("nonzero_joint_guide_vectors", 0)) > 0, "UAL projection has no non-zero joint guides")
    require(float(deformation_gate.get("maximum_joint_delta_screen_norm", 0.0)) > 0.0, "maximum UAL joint delta is zero")
    require(float(deformation_gate.get("ready_return_hand_midpoint_delta_max_norm", 1.0)) <= 1.0e-3, "ready-return hand corridor does not converge")
    require(float(deformation_gate.get("source_contact_to_recoil_hand_midpoint_delta_magnitude_norm", 0.0)) > 0.0, "source recoil metric missing")
    require(deformation_gate.get("actual_extracted_curve_values_used") is True, "actual extracted UAL curves not confirmed")
    require(guides.get("ual_deformation_gate") == deformation_gate, "manifest/guide UAL deformation gate mismatch")
    require(calibration_schema.get("accepted_document_schema") == "sable.aster.fire16.segmented_upper_calibration.v1", "accepted calibration schema mismatch")
    require(calibration_schema.get("directions_required") == list(DIRECTIONS), "calibration direction order mismatch")
    require(calibration_schema.get("per_direction_required", {}).get("white_shoulder_proxy") == "required false", "calibration must prohibit white shoulder proxy")
    require(manifest.get("calibration_schema", {}).get("sha256") == sha256(CALIBRATION_SCHEMA), "calibration schema hash mismatch")

    visual = manifest.get("visual_authority", {})
    require(visual.get("costumeId") == "ASTER_COMBAT_SUIT_C01", "costume identity mismatch")
    require(visual.get("costume_redesign") is False, "costume redesign not authorized")
    require(visual.get("white_shoulder_proxy_used") is False, "white shoulder proxy prohibited")
    require(visual.get("generated_replacement_art_used") is False, "generated replacement art prohibited")
    require(manifest.get("layer_contract", {}).get("vfx_baked_into_character") is False, "baked VFX prohibited")
    require(manifest.get("motion_authority", {}).get("action") == "Pistol_Shoot", "motion authority action mismatch")
    require(manifest.get("motion_authority", {}).get("visual_mesh_rendered") == 0, "UAL mesh rendered")
    require(manifest.get("motion_authority", {}).get("custom_spatial_direction_guide_is_ual_driven") is False, "custom direction guide mislabeled UAL-driven")

    safety = manifest.get("safety", {})
    for key in (
        "ual_mesh_or_base_model_rendered",
        "qwen_calls",
        "krea2_calls",
        "image_generation_calls",
        "external_api_calls",
        "c_drive_writes",
        "c_drive_deletes",
    ):
        require(safety.get(key) == 0, f"safety {key} must be zero")
    require(safety.get("universal_base_characters_used") is False, "Universal Base Characters prohibited")
    require(safety.get("paid_assets_used") is False, "paid assets prohibited")

    records = guides.get("records", [])
    require(len(records) == 24, f"expected 24 guide records, got {len(records)}")
    seen: set[tuple[str, str]] = set()
    residuals: list[float] = []
    for record in records:
        direction = record.get("direction")
        phase = record.get("phase")
        require(direction in DIRECTIONS, f"unknown direction {direction}")
        require(phase in PHASES, f"unknown phase {phase}")
        if direction in DIRECTIONS:
            target = DIRECTIONS[direction]
            measured = float(record.get("measured_centerline_degrees", -999.0))
            residual = angular_error(measured, target)
            residuals.append(residual)
            require(abs(float(record.get("target_angle_degrees")) - target) <= 1.0e-8, f"target mismatch {direction}/{phase}")
            require(residual <= 1.0e-6, f"centerline residual {residual} at {direction}/{phase}")
            require(record.get("centerline_gate") == "PASS", f"centerline gate failed {direction}/{phase}")
            unit = record.get("rifle_centerline_unit_screen", [])
            require(len(unit) == 2 and abs(math.hypot(float(unit[0]), float(unit[1])) - 1.0) <= 1.0e-7, f"non-unit centerline {direction}/{phase}")
        seen.add((str(direction), str(phase)))
    expected = {(direction, phase) for direction in DIRECTIONS for phase in PHASES}
    require(seen == expected, f"direction/phase coverage mismatch: missing={sorted(expected-seen)} extra={sorted(seen-expected)}")
    require(guides.get("curve_authority", {}).get("sha256") == EXPECTED_CURVE_SHA, "guide curve hash mismatch")
    require(guides.get("projection_contract", {}).get("custom_direction_camera_is_ual_driven") is False, "projection overclaims UAL camera")

    renders = manifest.get("renders", [])
    input_status = manifest.get("inputs", {}).get("input_plate_status")
    if input_status == "NOT_YET_PROVIDED":
        require(manifest.get("build_status") == "BLOCKED_INPUT_PLATES__PARSER_AND_GEOMETRY_READY", "fixture-free build status mismatch")
        require(len(renders) == 0, "fixture-free validation must render zero images")
        require(manifest.get("scope", {}).get("actual_render_count") == 0, "fixture-free render count must be zero")
    else:
        require(input_status == "PRESENT", "invalid input plate status")
        require(len(renders) == 24, "production candidate must contain 24 renders")
        for record in renders:
            geometry = record.get("rifle_geometry", {})
            require(geometry.get("centerline_gate") == "PASS", "render centerline gate failed")
            require(float(geometry.get("centerline_residual_degrees", 999.0)) <= 1.0e-6, "render centerline residual exceeded")

    result = "PASS" if not errors else "FAIL"
    qa = {
        "schema": "sable.aster.fire16.segmented_upper_rig.validation.v1",
        "result": result,
        "scope": "fixture-free curve parser and exact-centerline geometry; not a visual approval",
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)},
        "guides": {"path": GUIDES.relative_to(ROOT).as_posix(), "sha256": sha256(GUIDES)},
        "curve_authority": {"path": CURVES.relative_to(ROOT).as_posix(), "sha256": sha256(CURVES)},
        "calibration_schema": {"path": CALIBRATION_SCHEMA.relative_to(ROOT).as_posix(), "sha256": sha256(CALIBRATION_SCHEMA)},
        "records_checked": len(records),
        "direction_phase_coverage": len(seen),
        "maximum_centerline_residual_degrees": max(residuals) if residuals else None,
        "visual_gate": "HOLD_USER_REVIEW_REQUIRED",
        "promotion_ready": False,
        "runtime_eligible": False,
        "errors": errors,
        "safety": {
            "image_generation_calls": 0,
            "qwen_calls": 0,
            "krea2_calls": 0,
            "external_api_calls": 0,
            "c_drive_writes": 0,
            "c_drive_deletes": 0,
        },
    }
    atomic_json(qa, QA)
    print(
        json.dumps(
            {
                "qa": QA.relative_to(ROOT).as_posix(),
                "result": result,
                "records_checked": len(records),
                "max_centerline_residual_degrees": qa["maximum_centerline_residual_degrees"],
                "visual_gate": "HOLD_USER_REVIEW_REQUIRED",
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
