#!/usr/bin/env python3
"""Fail-closed gate for ImageGen-authored SABLE visible motion frames.

Blender/UAL material is accepted only as a licensed pose guide.  It can never
become visible runtime art.  One request reserves exactly one ImageGen output;
one independently reviewed frame receipt covers exactly one direction/phase.
The sequence gate requires 8 directions x 8 distinct phase receipts and is
still only a prerequisite for runtime/gait promotion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import generation_harness as g
import normalize_imagegen_chroma as chroma
import derive_chroma_runtime_rgba as runtime_chroma


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "tools/character_pipeline/visible_frame_contract.json"
NORMALIZER = ROOT / "tools/character_pipeline/normalize_imagegen_chroma.py"
RUNTIME_DERIVER = ROOT / "tools/character_pipeline/derive_chroma_runtime_rgba.py"
CODE = (Path(__file__), CONTRACT, NORMALIZER, RUNTIME_DERIVER)


def _refs(value):
    return value if isinstance(value, list) else []


def _capture_has_frame(capture, image_ref):
    return any(row.get("image") == image_ref for row in capture.get("frames", []))


def pose_guide_subject(guide, direction, motion, phase):
    capture = g.read(g.resolve(guide["capture"]))
    guide_bindings = {}
    for key in ("image", "capture", "blend", "license"):
        resolved = g.resolve(guide[key])
        guide_bindings[resolved.relative_to(ROOT).as_posix()] = g.sha(resolved)
    for key in ("retarget_result", "capture_generator"):
        resolved = g.resolve(capture[key])
        guide_bindings[resolved.relative_to(ROOT).as_posix()] = g.sha(resolved)
    return g.canonical({
        "bindings": guide_bindings,
        "direction": direction,
        "motion": motion,
        "phase": phase,
        "phase_definition": guide.get("phase_definition"),
        "capture_frame": guide.get("capture_frame"),
    })


def repair_target_subject(data):
    """Bind the exact failed pixels and the narrowly reviewed edit contract."""
    target = g.resolve(data["repair_target"])
    return g.canonical({
        "repair_target": g.ref(target),
        "repair_target_quarantine_manifest": data.get("repair_target_quarantine_manifest"),
        "prompt": data.get("prompt"),
        "source_receipt": data.get("source_receipt"),
        "previous_failure": data.get("previous_failure"),
        "direction": data.get("direction"),
        "motion": data.get("motion"),
        "phase": data.get("phase"),
        "phase_definition": data.get("phase_definition"),
        "anatomical_laterality_anchors": data.get("anatomical_laterality_anchors"),
        "preserve_exact": data.get("repair_preserve_exact"),
        "change_only": data.get("repair_change_only"),
        "imagegen_input_order": data.get("imagegen_input_order"),
    })


def _audit_pose_guide(guide, direction, motion, phase):
    errors = []
    required = ("image", "capture", "blend", "license", "review_bundle")
    if not isinstance(guide, dict) or any(k not in guide for k in required):
        return ["COMPLETE_LICENSED_POSE_GUIDE_REQUIRED"]
    for key in required:
        g.resolve(guide[key])
    capture = g.read(g.resolve(guide["capture"]))
    if capture.get("blend") != guide["blend"]:
        errors.append("POSE_GUIDE_BLEND_NOT_BOUND_TO_CAPTURE")
    if not _capture_has_frame(capture, guide["image"]):
        errors.append("POSE_GUIDE_IMAGE_NOT_BOUND_TO_CAPTURE")
    if capture.get("production_ready") is not False:
        errors.append("POSE_GUIDE_MUST_NOT_CLAIM_PRODUCTION_ART")
    for key in ("retarget_result", "capture_generator"):
        if key not in capture:
            errors.append("POSE_GUIDE_CAPTURE_PROVENANCE_REQUIRED:" + key)
        else:
            g.resolve(capture[key])
    retarget = g.read(g.resolve(capture["retarget_result"])) if "retarget_result" in capture else {}
    for key in ("generator", "ual", "ual_license", "model", "input_blend", "output_blend"):
        if key not in retarget:
            errors.append("POSE_GUIDE_RETARGET_PROVENANCE_REQUIRED:" + key)
        else:
            g.resolve(retarget[key])
    if guide.get("screen_direction") != direction or capture.get("screen_direction") != direction or retarget.get("screen_direction") != direction:
        errors.append("POSE_GUIDE_EXACT_DIRECTION_MISMATCH")
    expected_action = {"run": "Sprint_Loop", "walk": "Walk_Loop"}.get(motion)
    if guide.get("action") != expected_action or capture.get("action") != expected_action or retarget.get("action") != expected_action:
        errors.append("POSE_GUIDE_ACTION_MISMATCH")
    if guide.get("phase") != phase:
        errors.append("POSE_GUIDE_PHASE_MISMATCH")
    if guide.get("phase_definition") != g.read(CONTRACT).get("phase_semantics", {}).get(motion, {}).get(phase):
        errors.append("POSE_GUIDE_PHASE_DEFINITION_MISMATCH")
    frame = guide.get("capture_frame")
    if not any(row.get("frame") == frame and row.get("image") == guide.get("image") for row in capture.get("frames", [])):
        errors.append("POSE_GUIDE_FRAME_NOT_BOUND_TO_CAPTURE")
    license_data = g.read(g.resolve(guide["license"]))
    if (license_data.get("commercial_use") != "ALLOW" or
            license_data.get("rendered_game_distribution") != "ALLOW"):
        errors.append("POSE_GUIDE_COMMERCIAL_LICENSE_REQUIRED")
    for item in license_data.get("evidence", []):
        g.resolve(item)
    if "model" not in license_data:
        errors.append("POSE_GUIDE_LICENSE_MODEL_BINDING_REQUIRED")
    else:
        g.resolve(license_data["model"])
    if guide.get("visual_role") != "pose_guide_only_not_runtime_art":
        errors.append("POSE_GUIDE_ROLE_MUST_EXCLUDE_VISIBLE_ART")
    try:
        guide_subject = pose_guide_subject(guide, direction, motion, phase)
        bundle = g.read(g.resolve(guide["review_bundle"]))
        if bundle.get("pose_guide_subject_sha256") != guide_subject:
            errors.append("POSE_GUIDE_REVIEW_SUBJECT_MISMATCH")
        errors.extend(g.verify_reviews(bundle.get("reviews", []), guide_subject,
            g.read(CONTRACT)["pose_guide_review_checks"], g.read(CONTRACT)["pose_guide_review_roles"]))
    except (KeyError, ValueError):
        errors.append("POSE_GUIDE_EXACT_INDEPENDENT_REVIEWS_REQUIRED")
    return errors


def audit_request(path):
    data = g.read(path)
    contract = g.read(CONTRACT)
    errors = []
    if data.get("schema") != 1 or data.get("stage") != "visible_frame_request":
        errors.append("VISIBLE_FRAME_REQUEST_SCHEMA_REQUIRED")
    if data.get("generator") != "built_in_ImageGen":
        errors.append("BUILT_IN_IMAGEGEN_VISIBLE_ART_REQUIRED")
    operation = data.get("operation")
    if operation not in ("author_new_frame", "repair_failed_frame"):
        errors.append("EXPLICIT_VISIBLE_FRAME_IMAGEGEN_OPERATION_REQUIRED")
    if type(data.get("qa_fixture_only", False)) is not bool or data.get("qa_fixture_only") is not False:
        errors.append("PRODUCTION_FRAME_CANNOT_BE_SYNTHETIC")
    if data.get("max_unreviewed_outputs") != 1:
        errors.append("ONE_UNREVIEWED_VISIBLE_FRAME_ONLY")
    attempt_revision = data.get("attempt_revision")
    if not isinstance(attempt_revision, int) or isinstance(attempt_revision, bool) or attempt_revision < 1:
        errors.append("POSITIVE_VISIBLE_FRAME_ATTEMPT_REVISION_REQUIRED")
    if isinstance(attempt_revision, int) and not isinstance(attempt_revision, bool) and attempt_revision > 1:
        if "previous_failure" not in data:
            errors.append("RETRY_MUST_BIND_PREVIOUS_FAILURE")
        else:
            g.resolve(data["previous_failure"])
        changes = data.get("mechanism_changes")
        if not isinstance(changes, list) or not changes or any(not isinstance(v, str) or not v.strip() for v in changes):
            errors.append("RETRY_MECHANISM_CHANGES_REQUIRED")
    if operation == "repair_failed_frame":
        if not isinstance(attempt_revision, int) or isinstance(attempt_revision, bool) or attempt_revision <= 1:
            errors.append("REPAIR_OPERATION_REQUIRES_RETRY_REVISION")
        if "repair_target" not in data:
            errors.append("IMAGEGEN_REPAIR_TARGET_REQUIRED")
        else:
            g.resolve(data["repair_target"])
        target_quarantine_ref = data.get("repair_target_quarantine_manifest")
        if not isinstance(target_quarantine_ref, dict):
            errors.append("REPAIR_TARGET_QUARANTINE_MANIFEST_REQUIRED")
        elif "repair_target" in data:
            try:
                target = g.resolve(data["repair_target"])
                target_quarantine = g.read(g.resolve(target_quarantine_ref))
                quarantine_root = g.local(target_quarantine["quarantine_path"])
                target_relative = target.relative_to(quarantine_root).as_posix()
                inventory = target_quarantine.get("files", [])
                inventory_match = any(
                    item.get("path") == target_relative and item.get("sha256") == g.sha(target)
                    for item in inventory if isinstance(item, dict))
                if (not str(target_quarantine.get("status", "")).startswith("FAIL_NOT_PROMOTABLE") or
                        target_quarantine.get("actor_id") != data.get("actor_id") or
                        target_quarantine.get("costume_id") != data.get("costume_id") or
                        target_quarantine.get("disposal_allowed") is not False or
                        not inventory_match):
                    errors.append("REPAIR_TARGET_NOT_EXACT_FAILED_INVENTORY_MEMBER")
            except (KeyError, ValueError):
                errors.append("REPAIR_TARGET_NOT_EXACT_FAILED_INVENTORY_MEMBER")
        preserve = data.get("repair_preserve_exact")
        change = data.get("repair_change_only")
        if (not isinstance(preserve, list) or not preserve or
                any(not isinstance(v, str) or not v.strip() for v in preserve)):
            errors.append("REPAIR_EXACT_PRESERVE_SCOPE_REQUIRED")
        if (not isinstance(change, list) or not change or
                any(not isinstance(v, str) or not v.strip() for v in change)):
            errors.append("REPAIR_MINIMAL_CHANGE_SCOPE_REQUIRED")
        if isinstance(preserve, list) and isinstance(change, list) and set(preserve) & set(change):
            errors.append("REPAIR_PRESERVE_AND_CHANGE_SCOPE_MUST_BE_DISJOINT")
        input_order = data.get("imagegen_input_order")
        allowed_input_roles = {
            "repair_target_primary", "approved_source_identity",
            "licensed_pose_guide", "direction_reference",
            "supporting_failed_visual_only"
        }
        if (not isinstance(input_order, list) or not 2 <= len(input_order) <= 5 or
                any(not isinstance(item, dict) or item.get("role") not in allowed_input_roles
                    for item in input_order)):
            errors.append("EXACT_IMAGEGEN_INPUT_ORDER_REQUIRED")
        else:
            for item in input_order:
                g.resolve(item)
            if (input_order[0].get("role") != "repair_target_primary" or
                    "repair_target" not in data or
                    g.resolve(input_order[0]) != g.resolve(data["repair_target"])):
                errors.append("REPAIR_TARGET_MUST_BE_PRIMARY_IMAGEGEN_INPUT")
            resolved_inputs = [g.resolve(item) for item in input_order]
            if len(resolved_inputs) != len(set(resolved_inputs)):
                errors.append("IMAGEGEN_INPUT_ORDER_MUST_BE_UNIQUE")
            source_binding_paths = set(g.read(g.resolve(data["source_receipt"])).get("bindings", {}))
            guide_image = g.resolve(data["pose_guide"]["image"]) if isinstance(data.get("pose_guide"), dict) else None
            supporting_by_role = {
                role: {g.resolve(item) for item in _refs(data.get("supporting_references"))
                       if item.get("role") == role}
                for role in ("direction_reference", "previous_failed_frame_visual_reference_only")
            }
            for item, resolved_input in zip(input_order, resolved_inputs):
                rel = resolved_input.relative_to(ROOT).as_posix()
                role = item["role"]
                if role == "approved_source_identity" and rel not in source_binding_paths:
                    errors.append("IMAGEGEN_IDENTITY_INPUT_NOT_IN_SOURCE_RECEIPT")
                elif role == "direction_reference" and (rel not in source_binding_paths and
                        resolved_input not in supporting_by_role["direction_reference"]):
                    errors.append("IMAGEGEN_DIRECTION_INPUT_NOT_DECLARED")
                elif role == "licensed_pose_guide" and resolved_input != guide_image:
                    errors.append("IMAGEGEN_POSE_INPUT_NOT_EXACT_GUIDE")
                elif role == "supporting_failed_visual_only" and resolved_input not in supporting_by_role[
                        "previous_failed_frame_visual_reference_only"]:
                    errors.append("IMAGEGEN_FAILED_VISUAL_INPUT_NOT_DECLARED")
            if not any(item.get("role") == "approved_source_identity" for item in input_order):
                errors.append("IMAGEGEN_APPROVED_IDENTITY_INPUT_REQUIRED")
        bundle_ref = data.get("repair_target_review_bundle")
        if not isinstance(bundle_ref, dict):
            errors.append("INDEPENDENT_REPAIR_TARGET_REVIEW_REQUIRED")
        else:
            try:
                bundle = g.read(g.resolve(bundle_ref))
                subject = repair_target_subject(data)
                if (bundle.get("repair_target_subject_sha256") != subject or
                        bundle.get("verdict") != "PASS_REPAIR_TARGET_SCOPE_ONLY"):
                    errors.append("REPAIR_TARGET_REVIEW_SUBJECT_MISMATCH")
                errors.extend(g.verify_reviews(
                    bundle.get("reviews", []), subject,
                    contract["repair_target_review_checks"],
                    contract["repair_target_review_roles"]))
            except (KeyError, ValueError):
                errors.append("INDEPENDENT_REPAIR_TARGET_REVIEW_REQUIRED")
    direction = data.get("direction")
    motion = data.get("motion")
    phase = data.get("phase")
    if direction not in contract["directions"]:
        errors.append("INVALID_FRAME_DIRECTION")
    if motion not in contract["motions"] or phase not in contract["motions"].get(motion, []):
        errors.append("INVALID_EXPLICIT_GAIT_PHASE")
    phase_definition = contract.get("phase_semantics", {}).get(motion, {}).get(phase)
    if data.get("phase_definition") != phase_definition:
        errors.append("EXACT_GAIT_PHASE_DEFINITION_REQUIRED")
    anchors = data.get("anatomical_laterality_anchors")
    if (not isinstance(anchors, dict) or set(anchors) != {"left", "right"} or
            any(not isinstance(v, str) or not v.strip() for v in anchors.values()) or
            (isinstance(anchors, dict) and anchors.get("left") == anchors.get("right"))):
        errors.append("DISTINCT_ANATOMICAL_LATERALITY_ANCHORS_REQUIRED")
    receipt = g.resolve(data["source_receipt"])
    source = g.source_authority(receipt)
    g.assert_production_source_receipt({"source_receipt": g.ref(receipt)})
    if any(data.get(k) != source[k] for k in ("actor_id", "costume_id")):
        errors.append("FRAME_SOURCE_IDENTITY_MISMATCH")
    output_root = g.local(data.get("output_root", "artifacts/invalid"))
    if not output_root.is_relative_to(ROOT / "art_src/characters"):
        errors.append("VISIBLE_FRAME_OUTPUT_MUST_BE_PROJECT_CHARACTER_ART")
    expected_raw = g.local(data.get("expected_raw_path", "artifacts/invalid"))
    if not expected_raw.is_relative_to(output_root) or expected_raw.suffix.lower() != ".png":
        errors.append("EXACT_PROJECT_RAW_OUTPUT_PATH_REQUIRED")
    prompt = g.resolve(data["prompt"])
    prompt_text = prompt.read_text(encoding="utf-8")
    if not prompt_text.strip():
        errors.append("EMPTY_VISIBLE_FRAME_PROMPT")
    elif isinstance(anchors, dict) and any(str(v) not in prompt_text for v in anchors.values()):
        errors.append("PROMPT_MUST_BIND_BOTH_LATERALITY_ANCHORS")
    errors.extend(_audit_pose_guide(data.get("pose_guide"), direction, motion, phase))
    refs = _refs(data.get("supporting_references"))
    if any(r.get("role") not in ("direction_reference", "weapon_reference", "previous_reviewed_frame",
                                        "previous_failed_frame_visual_reference_only") for r in refs):
        errors.append("UNSCOPED_VISIBLE_REFERENCE")
    for item in refs:
        g.resolve(item)
    if data.get("background") != "uniform_chroma_green":
        errors.append("VISIBLE_FRAME_REQUIRES_UNIFORM_CHROMA_GREEN")
    bindings = {}
    guide = data.get("pose_guide") if isinstance(data.get("pose_guide"), dict) else {}
    exact_refs = [g.ref(path), data["source_receipt"], data["prompt"],
                  *[guide[k] for k in ("image", "capture", "blend", "license", "review_bundle") if k in guide],
                  *refs, *[g.ref(p) for p in CODE]]
    if "previous_failure" in data:
        exact_refs.append(data["previous_failure"])
    if "repair_target" in data:
        exact_refs.append(data["repair_target"])
    if "repair_target_review_bundle" in data:
        exact_refs.append(data["repair_target_review_bundle"])
    if "repair_target_quarantine_manifest" in data:
        exact_refs.append(data["repair_target_quarantine_manifest"])
    exact_refs.extend(_refs(data.get("imagegen_input_order")))
    for item in exact_refs:
        resolved = g.resolve(item)
        bindings[resolved.relative_to(ROOT).as_posix()] = g.sha(resolved)
    return {
        "stage": "visible_frame_request",
        "verdict": "FAIL" if errors else "PASS_REQUEST_ONLY",
        "errors": sorted(set(errors)),
        "request": g.ref(path),
        "bindings": bindings,
        "subject_sha256": g.canonical(bindings),
        "note": "Allows one ImageGen output only; not a visual or motion PASS."
    }


def reserve(path):
    audit = audit_request(path)
    if audit["errors"]:
        raise ValueError("VISIBLE_FRAME_REQUEST_NOT_READY:" + ",".join(audit["errors"]))
    data = g.read(path)
    expected_raw = g.local(data["expected_raw_path"])
    if expected_raw.exists():
        raise ValueError("FRESH_EXPECTED_IMAGEGEN_RAW_PATH_REQUIRED")
    permit_path = g.local(data["output_root"]) / "generation_requests" / (g.sha(path) + ".permit.json")
    g.write(permit_path, {
        "schema": 1,
        "stage": "visible_frame_attempt",
        "verdict": "RESERVED_SINGLE_IMAGEGEN_FRAME_ATTEMPT",
        "request": g.ref(path),
        "request_subject_sha256": audit["subject_sha256"],
        "output_root": data["output_root"],
        "expected_raw_path": data["expected_raw_path"],
        "max_outputs": 1
    })
    return {"stage": "visible_frame_attempt", "permit": g.ref(permit_path)}


def _number_pair(value, label):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(label + "_PAIR_REQUIRED")
    return np.asarray([g.finite(v) for v in value], dtype=np.float64)


def audit_frame(path):
    data = g.read(path)
    request_path = g.resolve(data["request"])
    request = g.read(request_path)
    request_audit = audit_request(request_path)
    errors = list(request_audit["errors"])
    permit = g.read(g.resolve(data["attempt_permit"]))
    expected_permit = {
        "schema": 1, "stage": "visible_frame_attempt",
        "verdict": "RESERVED_SINGLE_IMAGEGEN_FRAME_ATTEMPT",
        "request": g.ref(request_path),
        "request_subject_sha256": request_audit["subject_sha256"],
        "output_root": request["output_root"], "expected_raw_path": request["expected_raw_path"],
        "max_outputs": 1
    }
    if permit != expected_permit:
        errors.append("VISIBLE_FRAME_HAS_NO_EXACT_PREGENERATION_PERMIT")
    if any(data.get(k) != request.get(k) for k in ("actor_id", "costume_id", "direction", "motion", "phase")):
        errors.append("VISIBLE_FRAME_SCOPE_MISMATCH")
    if data.get("source_author") != "built_in_ImageGen":
        errors.append("VISIBLE_FRAME_SOURCE_AUTHOR_MISMATCH")
    output_root = g.local(request["output_root"])
    refs = [data[k] for k in ("raw_image", "normalized_image", "subject_mask", "normalization_qa",
                              "runtime_rgba", "runtime_rgba_qa", "annotations")]
    resolved = [g.resolve(item) for item in refs]
    if any(not p.is_relative_to(output_root) for p in resolved):
        errors.append("VISIBLE_FRAME_ARTIFACT_OUTSIDE_RESERVED_OUTPUT")
    if data["raw_image"].get("path") != request.get("expected_raw_path"):
        errors.append("VISIBLE_FRAME_RAW_NOT_AT_RESERVED_EXACT_PATH")

    raw = g.pixels(resolved[0])[..., :3]
    normalized = g.pixels(resolved[1])[..., :3]
    edge_mask = g.pixels(resolved[2])[..., 0] > 127
    runtime_rgba = g.pixels(resolved[4])
    mask = runtime_rgba[..., 3] > 127
    if (raw.shape != normalized.shape or raw.shape[:2] != edge_mask.shape or
            raw.shape[:2] != runtime_rgba.shape[:2] or runtime_rgba.shape[2] != 4):
        errors.append("VISIBLE_FRAME_DERIVATIVE_DIMENSIONS")
    else:
        background, _ = chroma.edge_connected_background(raw)
        expected = raw.copy()
        expected[background] = np.asarray([0, 255, 0], dtype=np.uint8)
        if not np.array_equal(normalized, expected) or not np.array_equal(edge_mask, ~background):
            errors.append("VISIBLE_FRAME_NORMALIZATION_NOT_REPRODUCIBLE")
        if not np.array_equal(normalized[edge_mask], raw[edge_mask]):
            errors.append("VISIBLE_FRAME_SUBJECT_PIXELS_CHANGED")
        if data.get("runtime_matting_policy") != "connected_chroma_green_costume_excludes_chroma_green":
            errors.append("VISIBLE_FRAME_EXPLICIT_RUNTIME_MATTING_POLICY_REQUIRED")
        runtime_background, _ = runtime_chroma.background_mask(normalized)
        expected_rgba = np.zeros_like(runtime_rgba)
        expected_rgba[..., :3] = normalized
        expected_rgba[..., 3] = np.where(runtime_background, 0, 255).astype(np.uint8)
        expected_rgba[runtime_background, :3] = 0
        if not np.array_equal(runtime_rgba, expected_rgba):
            errors.append("VISIBLE_FRAME_RUNTIME_RGBA_NOT_REPRODUCIBLE")
        if not np.array_equal(runtime_rgba[mask, :3], normalized[mask]):
            errors.append("VISIBLE_FRAME_RUNTIME_VISIBLE_PIXELS_CHANGED")
        if any(bool(mask[y, x]) for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
            errors.append("VISIBLE_FRAME_RUNTIME_BORDER_NOT_TRANSPARENT")
        h, w = raw.shape[:2]
        if [w, h] != data.get("native_size") or w < g.read(CONTRACT)["minimum_canvas"][0] or h < g.read(CONTRACT)["minimum_canvas"][1]:
            errors.append("VISIBLE_FRAME_NATIVE_RESOLUTION")
        yy, xx = np.where(mask)
        if len(xx) == 0:
            errors.append("VISIBLE_FRAME_EMPTY_SUBJECT")
        else:
            bbox = [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())]
            if data.get("bbox_xyxy") != bbox:
                errors.append("VISIBLE_FRAME_BBOX_NOT_MEASURED_FROM_MASK")
            height = bbox[3] - bbox[1] + 1
            if height < g.read(CONTRACT)["minimum_subject_height_pixels"]:
                errors.append("VISIBLE_FRAME_SUBJECT_TOO_SMALL")
            ann = g.read(resolved[6])
            if ann.get("normalized_image_sha256") != data["normalized_image"]["sha256"]:
                errors.append("VISIBLE_FRAME_STALE_ANNOTATIONS")
            if ann.get("anatomical_laterality_anchors") != request.get("anatomical_laterality_anchors"):
                errors.append("VISIBLE_FRAME_LATERALITY_ANCHORS_NOT_ANNOTATED")
            points = ann.get("points", {})
            needed = ("foot_left", "foot_right", "muzzle_base", "muzzle_tip")
            if any(name not in points for name in needed):
                errors.append("VISIBLE_FRAME_LANDMARKS_REQUIRED")
            else:
                left, right = _number_pair(points["foot_left"], "FOOT_LEFT"), _number_pair(points["foot_right"], "FOOT_RIGHT")
                base, tip = _number_pair(points["muzzle_base"], "MUZZLE_BASE"), _number_pair(points["muzzle_tip"], "MUZZLE_TIP")
                stride = float(np.linalg.norm(left - right) / height)
                if request["direction"] in ("E", "W"):
                    floor = g.read(CONTRACT)[request["motion"] + "_profile_stride_over_height_min"]
                    if stride < floor:
                        errors.append("PROFILE_GAIT_STRIDE_TOO_NARROW")
                axis = tip - base
                expected_sign = 1 if request["direction"] in ("E", "SE", "NE") else -1 if request["direction"] in ("W", "SW", "NW") else 0
                if np.linalg.norm(axis) / height < g.read(CONTRACT)["minimum_visible_muzzle_axis_over_height"]:
                    errors.append("VISIBLE_MUZZLE_AXIS_TOO_SHORT")
                if expected_sign and axis[0] * expected_sign <= 0:
                    errors.append("VISIBLE_MUZZLE_POINTS_OPPOSITE_BODY_DIRECTION")
    qa = g.read(resolved[3])
    if (qa.get("input") != data["raw_image"]["path"] or qa.get("input_sha256") != data["raw_image"]["sha256"] or
            qa.get("output") != data["normalized_image"]["path"] or qa.get("output_sha256") != data["normalized_image"]["sha256"] or
            qa.get("mask") != data["subject_mask"]["path"] or qa.get("mask_sha256") != data["subject_mask"]["sha256"]):
        errors.append("VISIBLE_FRAME_NORMALIZATION_QA_BINDING")
    runtime_qa = g.read(resolved[5])
    if (runtime_qa.get("input") != data["normalized_image"]["path"] or
            runtime_qa.get("input_sha256") != data["normalized_image"]["sha256"] or
            runtime_qa.get("output") != data["runtime_rgba"]["path"] or
            runtime_qa.get("output_sha256") != data["runtime_rgba"]["sha256"] or
            runtime_qa.get("visible_rgb_byte_exact") is not True or
            runtime_qa.get("visible_strong_green_alpha_boundary_residual_pixels") != 0):
        errors.append("VISIBLE_FRAME_RUNTIME_RGBA_QA_BINDING")
    bindings = dict(request_audit["bindings"])
    for item in [g.ref(path), data["attempt_permit"], *refs]:
        p = g.resolve(item)
        bindings[p.relative_to(ROOT).as_posix()] = g.sha(p)
    return {
        "stage": "visible_frame", "verdict": "FAIL" if errors else "HOLD_VISIBLE_FRAME_REVIEW",
        "errors": sorted(set(errors)), "bindings": bindings,
        "subject_sha256": g.canonical(bindings), "request": g.ref(request_path),
        "actor_id": request.get("actor_id"), "costume_id": request.get("costume_id"),
        "direction": request.get("direction"), "motion": request.get("motion"), "phase": request.get("phase"),
        "note": "Technical geometry and byte checks cannot approve anatomy, contact, identity or motion quality."
    }


def seal_frame(path):
    bundle = g.read(path)
    manifest = g.resolve(bundle["frame_manifest"])
    audit = audit_frame(manifest)
    contract = g.read(CONTRACT)
    errors = audit["errors"] + g.verify_reviews(bundle.get("reviews", []), audit["subject_sha256"],
        contract["frame_review_checks"], contract["frame_review_roles"])
    if errors:
        raise ValueError("VISIBLE_FRAME_NOT_APPROVED:" + ",".join(errors))
    return {**audit, "schema": 1, "verdict": "PASS_ONE_VISIBLE_FRAME_ONLY",
            "frame_manifest": g.ref(manifest), "review_bundle": g.ref(path)}


def verify_frame_receipt(path):
    receipt = g.read(path)
    if receipt.get("verdict") != "PASS_ONE_VISIBLE_FRAME_ONLY":
        raise ValueError("APPROVED_VISIBLE_FRAME_RECEIPT_REQUIRED")
    actual = seal_frame(g.resolve(receipt["review_bundle"]))
    if actual != receipt:
        raise ValueError("STALE_OR_FORGED_VISIBLE_FRAME_RECEIPT")
    return receipt


def audit_sequence(path):
    data = g.read(path)
    contract = g.read(CONTRACT)
    errors = []
    receipts = data.get("frame_receipts", [])
    expected = {(direction, phase) for direction in contract["directions"] for phase in contract["motions"].get(data.get("motion"), [])}
    seen = []
    source_receipts = set()
    image_hashes = set()
    for item in receipts:
        receipt = verify_frame_receipt(g.resolve(item))
        seen.append((receipt["direction"], receipt["phase"]))
        request = g.read(g.resolve(receipt["request"]))
        source_receipts.add(json.dumps(request["source_receipt"], sort_keys=True))
        manifest = g.read(g.resolve(receipt["frame_manifest"]))
        image_hashes.add(manifest["runtime_rgba"]["sha256"])
        if any(receipt.get(k) != data.get(k) for k in ("actor_id", "costume_id", "motion")):
            errors.append("VISIBLE_SEQUENCE_IDENTITY_OR_MOTION_MISMATCH")
    if len(receipts) != len(expected) or set(seen) != expected or len(seen) != len(set(seen)):
        errors.append("VISIBLE_SEQUENCE_REQUIRES_EXACT_8X8_PHASE_COVERAGE")
    if len(image_hashes) != len(expected):
        errors.append("VISIBLE_SEQUENCE_REUSED_DUPLICATE_IMAGES")
    if len(source_receipts) != 1:
        errors.append("VISIBLE_SEQUENCE_SOURCE_AUTHORITY_MISMATCH")
    return {"stage": "visible_sequence", "verdict": "FAIL" if errors else "HOLD_RUNTIME_MOTION_REVIEW",
            "errors": sorted(set(errors)), "covered": sorted([list(v) for v in set(seen)]),
            "note": "Still requires temporal gait, contact, firing, runtime matrix and HTML parity review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["request", "reserve", "frame", "seal-frame", "verify-frame", "sequence"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.command == "request": result = audit_request(args.input)
    elif args.command == "reserve": result = reserve(args.input)
    elif args.command == "frame": result = audit_frame(args.input)
    elif args.command == "seal-frame": result = seal_frame(args.input)
    elif args.command == "verify-frame": result = verify_frame_receipt(args.input)
    else: result = audit_sequence(args.input)
    if args.out:
        g.write(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
