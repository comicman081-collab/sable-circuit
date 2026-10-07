"""Shared fail-closed audit for an exact masked ImageGen repair boundary.

This module does not claim that built-in ImageGen currently exposes such an
interface.  It rejects repair reservations until independently reviewed,
executable capability evidence proves that the exact native binary mask is
consumed and every protected pixel remains byte-identical.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

import generation_harness as g
import visible_frame_harness as frozen


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "tools/character_pipeline/imagegen_repair_execution_contract.json"


def boundary_subject(request, boundary):
    """Bind the reviewed boundary to exact request scope and implementation."""
    return g.canonical({
        "contract": boundary.get("contract"),
        "generator": boundary.get("generator"),
        "repair_target_subject_sha256": frozen.repair_target_subject(request),
        "change_mask": boundary.get("change_mask"),
        "capability_evidence": boundary.get("capability_evidence"),
        "hard_edit_mask_supported": boundary.get("hard_edit_mask_supported"),
        "outside_mask_pixels_immutable": boundary.get("outside_mask_pixels_immutable"),
        "verdict": boundary.get("verdict"),
    })


def audit_boundary(request, boundary_ref):
    errors = []
    bindings = {}
    contract = g.read(CONTRACT)
    try:
        boundary_path = g.resolve(boundary_ref)
        boundary = g.read(boundary_path)
        bindings[boundary_path.relative_to(ROOT).as_posix()] = g.sha(boundary_path)
        contract_ref = g.ref(CONTRACT)
        if boundary.get("schema") != 1 or boundary.get("stage") != "imagegen_repair_execution_boundary":
            errors.append("REPAIR_EXECUTION_BOUNDARY_SCHEMA")
        if boundary.get("contract") != contract_ref:
            errors.append("EXACT_REPAIR_EXECUTION_CONTRACT_REQUIRED")
        else:
            bindings[CONTRACT.relative_to(ROOT).as_posix()] = g.sha(CONTRACT)
        if boundary.get("generator") != request.get("generator"):
            errors.append("REPAIR_EXECUTION_GENERATOR_MISMATCH")
        if boundary.get("repair_target_subject_sha256") != frozen.repair_target_subject(request):
            errors.append("REPAIR_EXECUTION_SCOPE_SUBJECT_MISMATCH")
        if boundary.get("hard_edit_mask_supported") is not True:
            errors.append("HARD_EDIT_MASK_CAPABILITY_REQUIRED")
        if boundary.get("outside_mask_pixels_immutable") is not True:
            errors.append("OUTSIDE_MASK_PIXEL_IMMUTABILITY_REQUIRED")
        if boundary.get("verdict") != contract.get("pass_verdict"):
            errors.append("REPAIR_EXECUTION_BOUNDARY_NOT_PASS")

        mask_ref = boundary.get("change_mask")
        if not isinstance(mask_ref, dict):
            errors.append("EXACT_REPAIR_CHANGE_MASK_REQUIRED")
        else:
            mask_path = g.resolve(mask_ref)
            bindings[mask_path.relative_to(ROOT).as_posix()] = g.sha(mask_path)
            target = g.pixels(g.resolve(request["repair_target"]))
            mask = g.pixels(mask_path)
            if mask.shape[:2] != target.shape[:2] or mask.ndim != 3 or mask.shape[2] != 4:
                errors.append("REPAIR_CHANGE_MASK_DIMENSIONS")
            else:
                if not (np.array_equal(mask[..., 0], mask[..., 1]) and
                        np.array_equal(mask[..., 0], mask[..., 2]) and
                        np.all(mask[..., 3] == 255)):
                    errors.append("REPAIR_CHANGE_MASK_CHANNELS_NOT_OPAQUE_BINARY")
                values = set(int(value) for value in np.unique(mask[..., :3]))
                if values != {0, 255}:
                    errors.append("REPAIR_CHANGE_MASK_REQUIRES_EDIT_AND_PROTECTED_PIXELS")
                coverage = float(np.count_nonzero(mask[..., 0] == 255) / mask[..., 0].size)
                if not (float(contract["minimum_change_mask_coverage"]) <= coverage <=
                        float(contract["maximum_change_mask_coverage"])):
                    errors.append("REPAIR_CHANGE_MASK_COVERAGE_OUT_OF_RANGE")

        evidence_ref = boundary.get("capability_evidence")
        if not isinstance(evidence_ref, dict):
            errors.append("EXECUTABLE_MASK_CAPABILITY_EVIDENCE_REQUIRED")
        else:
            evidence_path = g.resolve(evidence_ref)
            evidence = g.read(evidence_path)
            bindings[evidence_path.relative_to(ROOT).as_posix()] = g.sha(evidence_path)
            if (evidence.get("schema") != 1 or
                    evidence.get("stage") != "generator_hard_mask_capability"):
                errors.append("MASK_CAPABILITY_EVIDENCE_SCHEMA")
            if evidence.get("generator") != request.get("generator"):
                errors.append("MASK_CAPABILITY_GENERATOR_MISMATCH")
            if evidence.get("supports_exact_binary_change_mask") is not True:
                errors.append("GENERATOR_EXACT_BINARY_MASK_NOT_PROVEN")
            if evidence.get("outside_mask_pixels_byte_immutable") is not True:
                errors.append("GENERATOR_PROTECTED_PIXELS_NOT_PROVEN")
            if not isinstance(evidence.get("exact_mask_argument"), str) or not evidence["exact_mask_argument"].strip():
                errors.append("GENERATOR_EXACT_MASK_ARGUMENT_REQUIRED")
            closure = evidence.get("implementation_closure")
            if not isinstance(closure, list) or not closure:
                errors.append("MASK_CAPABILITY_IMPLEMENTATION_CLOSURE_REQUIRED")
            else:
                for item in closure:
                    resolved = g.resolve(item)
                    bindings[resolved.relative_to(ROOT).as_posix()] = g.sha(resolved)

        subject = boundary_subject(request, boundary)
        if boundary.get("boundary_subject_sha256") != subject:
            errors.append("REPAIR_BOUNDARY_REVIEW_SUBJECT_MISMATCH")
        errors.extend(g.verify_reviews(
            boundary.get("reviews", []), subject,
            contract["boundary_review_checks"], contract["required_review_roles"]
        ))
    except (KeyError, TypeError, ValueError):
        errors.append("REPAIR_EXECUTION_BOUNDARY_INVALID")
    return sorted(set(errors)), bindings
