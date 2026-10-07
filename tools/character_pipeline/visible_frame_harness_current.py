#!/usr/bin/env python3
"""Current SABLE visible-frame entrypoint with fixed-floor contact closure.

The frozen ``visible_frame_harness.py`` remains the verifier for already sealed
airborne receipts.  This entrypoint monkey-patches its pose-guide audit in
memory so every new non-airborne request, permit, frame, seal, receipt verify,
and sequence audit also resolves an exact PASS contact-calibration report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import generation_harness as g
import visible_frame_harness as frozen
import calibrate_vrm_ual_ground_contact as contact
import imagegen_repair_execution_boundary as repair_boundary
import tripo_pose_guide_gate as tripo_guide
import semantic_laterality_guide as semantic_guide
import existing_frame_derivative_admission as existing_frame
import phase_aware_visible_frame as phase_frame


ROOT = Path(__file__).resolve().parents[2]
FROZEN_POSE_GUIDE_AUDIT = frozen._audit_pose_guide
FROZEN_REQUEST_AUDIT = frozen.audit_request
FROZEN_FRAME_AUDIT = frozen.audit_frame
FROZEN_FRAME_SEAL = frozen.seal_frame
AIRBORNE_PHASES = {("run", "flight_l"), ("run", "flight_r")}
CURRENT_GATE = Path(__file__).resolve()
CONTACT_CONTRACT = ROOT / "tools/character_pipeline/pose_guide_contact_contract.json"
VISUAL_PROMOTION_CONTRACT = ROOT / "tools/character_pipeline/pose_guide_visual_promotion_contract.json"
CONTACT_CALIBRATOR = ROOT / "tools/character_pipeline/calibrate_vrm_ual_ground_contact.py"
CONTACT_REVIEW_ROLES = ["visual", "Ponytail FULL"]
CONTACT_REVIEW_CHECKS = [
    "exact_current_gate_and_contract",
    "exact_calibration_report_and_capture",
    "independent_sole_vertices_match",
    "fixed_floor_contact_and_phase_semantics",
    "feet_ankles_pelvis_visual_distinction",
    "pose_guide_only_boundary",
]


def contact_calibration_subject(guide, direction, motion, phase):
    """Bind the current gate and the exact independently sampled phase row."""
    report = g.read(g.resolve(guide["contact_calibration"]))
    capture = g.read(g.resolve(guide["capture"]))
    sample_index = report["phase_candidates"][phase]
    report_row = next(row for row in report["samples"] if row.get("sample") == sample_index)
    capture_row = next(row for row in capture["frames"] if row.get("phase") == phase)
    return g.canonical({
        "current_gate": g.ref(CURRENT_GATE),
        "contact_contract": g.ref(CONTACT_CONTRACT),
        "visual_promotion_contract": g.ref(VISUAL_PROMOTION_CONTRACT),
        "contact_calibrator": g.ref(CONTACT_CALIBRATOR),
        "contact_calibration": guide["contact_calibration"],
        "capture": guide["capture"],
        "direction": direction,
        "motion": motion,
        "phase": phase,
        "report_row": report_row,
        "capture_row": capture_row,
    })


def _audit_contact_calibration(guide, direction, motion, phase):
    if (motion, phase) in AIRBORNE_PHASES:
        return []
    errors = []
    if not isinstance(guide, dict) or not isinstance(guide.get("contact_calibration"), dict):
        return ["FIXED_FLOOR_CONTACT_CALIBRATION_REQUIRED"]
    try:
        if guide.get("current_gate") != g.ref(CURRENT_GATE):
            errors.append("EXACT_CURRENT_VISIBLE_FRAME_GATE_REQUIRED")
        if guide.get("contact_contract") != g.ref(CONTACT_CONTRACT):
            errors.append("EXACT_CONTACT_CONTRACT_REQUIRED")
        if guide.get("visual_promotion_contract") != g.ref(VISUAL_PROMOTION_CONTRACT):
            errors.append("EXACT_VISUAL_PROMOTION_CONTRACT_REQUIRED")
        if guide.get("contact_calibrator") != g.ref(CONTACT_CALIBRATOR):
            errors.append("EXACT_CONTACT_CALIBRATOR_REQUIRED")
        report_path = g.resolve(guide["contact_calibration"])
        report = g.read(report_path)
        if (
            report.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY"
            or report.get("errors") != []
            or report.get("production_ready") is not False
            or report.get("visible_art_authority") != "built_in_ImageGen_only"
            or report.get("blender_ual_role") != "pose_geometry_guide_only"
        ):
            errors.append("CONTACT_CALIBRATION_NOT_EXACT_PASS")
        for key in ("input_result", "input_blend", "contract", "generator"):
            g.resolve(report[key])
        if report.get("contract") != g.ref(CONTACT_CONTRACT):
            errors.append("CALIBRATION_REPORT_CONTRACT_NOT_CURRENT")
        if report.get("generator") != g.ref(CONTACT_CALIBRATOR):
            errors.append("CALIBRATION_REPORT_GENERATOR_NOT_CURRENT")
        capture = g.read(g.resolve(guide["capture"]))
        if report.get("input_result") != capture.get("retarget_result"):
            errors.append("CONTACT_CALIBRATION_RETARGET_MISMATCH")
        if report.get("input_blend") != guide.get("blend") or capture.get("blend") != guide.get("blend"):
            errors.append("CONTACT_CALIBRATION_BLEND_MISMATCH")
        if capture.get("calibration") != guide.get("contact_calibration"):
            errors.append("CAPTURE_CALIBRATION_BINDING_REQUIRED")
        recomputed_phases, recomputed_errors = contact._classify(
            report.get("samples", []), g.read(CONTACT_CONTRACT)
        )
        if recomputed_errors or recomputed_phases != report.get("phase_candidates"):
            errors.append("CALIBRATION_ROWS_DO_NOT_REPRODUCE_REPORTED_PHASES")
        sample_index = report.get("phase_candidates", {}).get(phase)
        if not isinstance(sample_index, int) or isinstance(sample_index, bool):
            errors.append("CONTACT_CALIBRATION_EXACT_PHASE_REQUIRED")
        else:
            samples = [row for row in report.get("samples", []) if row.get("sample") == sample_index]
            if len(samples) != 1 or samples[0].get("frame") != guide.get("capture_frame"):
                errors.append("CONTACT_CALIBRATION_CAPTURE_FRAME_MISMATCH")
            capture_rows = [row for row in capture.get("frames", []) if row.get("phase") == phase]
            if len(capture_rows) != 1:
                errors.append("ONE_CAPTURE_ROW_PER_PHASE_REQUIRED")
            else:
                capture_row = capture_rows[0]
                if (
                    capture_row.get("sample") != sample_index
                    or capture_row.get("frame") != guide.get("capture_frame")
                    or capture_row.get("image") != guide.get("image")
                ):
                    errors.append("CONTACT_CALIBRATION_CAPTURE_ROW_MISMATCH")
                if len(samples) == 1 and (
                    capture_row.get("actual_sole_vertices_world_m")
                    != samples[0].get("sole_vertices_world_m")
                    or capture.get("fixed_floor_world_z_m")
                    != report.get("fixed_floor", {}).get("world_z_m")
                ):
                    errors.append("CAPTURE_ACTUAL_SOLE_GEOMETRY_MISMATCH")
            visual_contract = g.read(VISUAL_PROMOTION_CONTRACT)
            support_side = "left" if phase.endswith("_l") else "right"
            if len(samples) == 1 and samples[0].get("sole_clearance_m", {}).get(support_side, 1.0) > float(
                visual_contract["maximum_support_sole_clearance_m"]
            ):
                errors.append("VISUAL_SUPPORT_SOLE_CLEARANCE_EXCEEDED")
            if phase.startswith("down_"):
                label = "l" if support_side == "left" else "r"
                contact_sample = report.get("phase_candidates", {}).get("contact_" + label)
                contact_rows = [row for row in report.get("samples", []) if row.get("sample") == contact_sample]
                if len(contact_rows) != 1 or len(samples) != 1 or (
                    float(contact_rows[0]["pelvis_world_m"][2])
                    - float(samples[0]["pelvis_world_m"][2])
                    < float(visual_contract["minimum_contact_to_down_pelvis_drop_m"])
                ):
                    errors.append("CONTACT_TO_DOWN_PELVIS_DROP_INSUFFICIENT")
        if guide.get("contact_calibration_phase") != phase:
            errors.append("CONTACT_CALIBRATION_PHASE_BINDING_REQUIRED")
        subject = contact_calibration_subject(guide, direction, motion, phase)
        bundle = g.read(g.resolve(guide["contact_review_bundle"]))
        if bundle.get("contact_calibration_subject_sha256") != subject:
            errors.append("CONTACT_REVIEW_SUBJECT_MISMATCH")
        errors.extend(g.verify_reviews(
            bundle.get("reviews", []), subject, CONTACT_REVIEW_CHECKS, CONTACT_REVIEW_ROLES
        ))
    except (KeyError, StopIteration, TypeError, ValueError):
        errors.append("FIXED_FLOOR_CONTACT_CALIBRATION_INVALID")
    return errors


def _audit_pose_guide_current(guide, direction, motion, phase):
    if isinstance(guide, dict) and guide.get("source_kind") == tripo_guide.KIND:
        return tripo_guide.audit(guide, direction, motion, phase) + _audit_contact_calibration(
            guide, direction, motion, phase
        )
    return FROZEN_POSE_GUIDE_AUDIT(guide, direction, motion, phase) + _audit_contact_calibration(
        guide, direction, motion, phase
    )


def _audit_request_current(path):
    result = FROZEN_REQUEST_AUDIT(path)
    data = g.read(path)
    errors = list(result["errors"])
    bindings = dict(result.get("bindings", {}))
    if "frame_validation_contract" in data:
        if data["frame_validation_contract"] != g.ref(phase_frame.PHASE_CONTRACT):
            errors.append("EXACT_CURRENT_PHASE_FRAME_CONTRACT_REQUIRED")
        for path in phase_frame.consumed_code():
            bindings[path.relative_to(ROOT).as_posix()] = g.sha(path)
    guide = data.get("pose_guide", {})
    semantic = data.get("semantic_laterality_guide")
    semantic_inputs = [r for r in data.get("imagegen_input_order", [])
                       if r.get("role") == "anatomical_laterality_geometry_guide"]
    if semantic is not None or semantic_inputs:
        if not isinstance(semantic, dict):
            errors.append("SEMANTIC_GUIDE_MANIFEST_REQUIRED")
        else:
            semantic_errors, semantic_bindings = semantic_guide.audit(
                semantic, guide, data.get("direction"), data.get("motion"), data.get("phase")
            )
            errors.extend(semantic_errors)
            bindings.update(semantic_bindings)
            try:
                expected = g.read(g.resolve(semantic))["image"]
                if len(semantic_inputs) != 1 or g.resolve(semantic_inputs[0]) != g.resolve(expected):
                    errors.append("EXACT_SEMANTIC_GUIDE_IMAGEGEN_INPUT_REQUIRED")
            except (KeyError, ValueError):
                errors.append("EXACT_SEMANTIC_GUIDE_IMAGEGEN_INPUT_REQUIRED")
    if isinstance(guide, dict) and guide.get("source_kind") == tripo_guide.KIND:
        try:
            bindings.update(tripo_guide.closure(guide))
        except (KeyError, ValueError, TypeError):
            errors.append("TRIPO_GUIDE_COMPLETE_DEPENDENCY_CLOSURE_REQUIRED")
    if data.get("operation") == "repair_failed_frame":
        boundary_ref = data.get("repair_execution_boundary")
        if not isinstance(boundary_ref, dict):
            errors.append("REPAIR_EXECUTION_BOUNDARY_REQUIRED")
        else:
            boundary_errors, boundary_bindings = repair_boundary.audit_boundary(data, boundary_ref)
            errors.extend(boundary_errors)
            bindings.update(boundary_bindings)
        try:
            boundary_mask = g.read(g.resolve(boundary_ref)).get("change_mask") if isinstance(boundary_ref, dict) else None
        except (KeyError, TypeError, ValueError):
            boundary_mask = None
        if data.get("repair_change_mask") != boundary_mask:
            errors.append("REPAIR_CHANGE_MASK_BOUNDARY_BINDING_REQUIRED")
    result["errors"] = sorted(set(errors))
    result["bindings"] = bindings
    result["subject_sha256"] = g.canonical(bindings)
    result["verdict"] = "FAIL" if result["errors"] else "PASS_REQUEST_ONLY"
    return result


def _audit_frame_current(path):
    if g.read(path).get("stage") == existing_frame.STAGE:
        return existing_frame.audit(path)
    if "frame_validation_contract" in g.read(path):
        return phase_frame.audit_frame(path, _audit_request_current)
    return FROZEN_FRAME_AUDIT(path)


def _seal_frame_current(path):
    bundle = g.read(path)
    manifest = g.resolve(bundle["frame_manifest"])
    if g.read(manifest).get("stage") != existing_frame.STAGE and "frame_validation_contract" in g.read(manifest):
        audit = _audit_frame_current(manifest)
        contract = g.read(frozen.CONTRACT)
        checks = contract["frame_review_checks"] + g.read(phase_frame.PHASE_CONTRACT)["additional_frame_review_checks"]
        errors = audit["errors"] + g.verify_reviews(bundle.get("reviews", []), audit["subject_sha256"], checks, contract["frame_review_roles"])
        if errors:
            raise ValueError("PHASE_AWARE_FRAME_NOT_APPROVED:" + ",".join(errors))
        return {**audit, "schema": 1, "verdict": "PASS_ONE_VISIBLE_FRAME_ONLY",
                "frame_manifest": g.ref(manifest), "review_bundle": g.ref(path)}
    if g.read(manifest).get("stage") != existing_frame.STAGE:
        return FROZEN_FRAME_SEAL(path)
    audit = existing_frame.audit(manifest)
    contract = g.read(frozen.CONTRACT)
    errors = audit["errors"] + g.verify_reviews(
        bundle.get("reviews", []), audit["subject_sha256"],
        contract["frame_review_checks"] + existing_frame.EXTRA_CHECKS,
        contract["frame_review_roles"])
    if errors:
        raise ValueError("EXISTING_FRAME_ADMISSION_NOT_APPROVED:" + ",".join(errors))
    return {**audit, "schema": 1, "verdict": "PASS_ONE_VISIBLE_FRAME_ONLY",
            "frame_manifest": g.ref(manifest), "review_bundle": g.ref(path)}


def install_current_patches():
    """Install all current gates into every recursive frozen entrypoint."""
    frozen._audit_pose_guide = _audit_pose_guide_current
    frozen.audit_request = _audit_request_current
    frozen.audit_frame = _audit_frame_current
    frozen.seal_frame = _seal_frame_current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["request", "reserve", "frame", "seal-frame", "verify-frame", "sequence"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()

    # All downstream frozen functions resolve this global at call time, so the
    # enhanced audit applies recursively to frame seals, receipt verification,
    # and every receipt inside a sequence.
    install_current_patches()
    if args.command == "request":
        result = _audit_request_current(args.input)
    elif args.command == "reserve":
        result = frozen.reserve(args.input)
    elif args.command == "frame":
        result = frozen.audit_frame(args.input)
    elif args.command == "seal-frame":
        result = frozen.seal_frame(args.input)
    elif args.command == "verify-frame":
        result = frozen.verify_frame_receipt(args.input)
    else:
        result = frozen.audit_sequence(args.input)
    if args.out:
        g.write(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
