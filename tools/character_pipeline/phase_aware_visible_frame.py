"""Current phase-aware frame audit; frozen historical verifier stays unchanged.

Normal passing/down phases are not forced into wide contact/flight silhouettes.
Optional explicit interior masks preserve source-authored green details without
altering RGB. All source, guide, permit, geometry and independent review gates
remain active. This never filters errors from a previously failed audit.
"""
from pathlib import Path
import numpy as np
from PIL import Image
import generation_harness as g
import normalize_imagegen_chroma as chroma
import derive_chroma_runtime_rgba as runtime_chroma
import derive_reviewed_chroma_rgba as protected_derivative
from visible_frame_harness import _number_pair
ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/'tools/character_pipeline/visible_frame_contract.json'
PHASE_CONTRACT=ROOT/'tools/character_pipeline/visible_frame_phase_contract.json'


def consumed_code():
    return [Path(__file__),PHASE_CONTRACT,CONTRACT,Path(g.__file__),Path(chroma.__file__),
            Path(runtime_chroma.__file__),Path(protected_derivative.__file__),
            ROOT/'tools/character_pipeline/visible_frame_harness.py']


def stride_floor_applies(direction,motion,phase):
    contract=g.read(PHASE_CONTRACT)
    if motion not in contract['profile_stride_floor_applies_to']:
        raise ValueError('UNKNOWN_MOTION')
    return direction in ('E','W') and phase in contract['profile_stride_floor_applies_to'][motion]


def audit_frame(path, audit_request):
    data = g.read(path)
    phase_contract = g.read(PHASE_CONTRACT)
    request_path = g.resolve(data["request"])
    request = g.read(request_path)
    request_audit = audit_request(request_path)
    errors = list(request_audit["errors"])
    if (data.get('frame_validation_contract') != g.ref(PHASE_CONTRACT) or
            request.get('frame_validation_contract') != data.get('frame_validation_contract')):
        errors.append('EXACT_PREGENERATION_PHASE_FRAME_CONTRACT_REQUIRED')
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
        if data.get("runtime_matting_policy") not in phase_contract["matte_policies"]:
            errors.append("VISIBLE_FRAME_EXPLICIT_RUNTIME_MATTING_POLICY_REQUIRED")
        runtime_background, _ = runtime_chroma.background_mask(normalized)
        if data.get("runtime_matting_policy") == "explicit_reviewed_interior_subject_protection":
            protection_path = g.resolve(data["protection_mask"])
            if not protection_path.is_relative_to(output_root):
                errors.append("PROTECTION_MASK_OUTSIDE_RESERVED_OUTPUT")
            refs.append(data["protection_mask"])
            protection_image = np.asarray(Image.open(protection_path))
            if protection_image.shape != mask.shape or not set(np.unique(protection_image)).issubset({0,255}):
                errors.append("NATIVE_BINARY_PROTECTION_MASK_REQUIRED")
            else:
                protection = protection_image == 255
                if not protection.any() or np.any(protection & (~runtime_background | background)):
                    errors.append("PROTECTION_MUST_RESTORE_ONLY_INTERIOR_SOURCE_SUBJECT")
                runtime_background = runtime_background & ~protection
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
                if stride_floor_applies(request["direction"],request["motion"],request["phase"]):
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
    if data.get("runtime_matting_policy") == "explicit_reviewed_interior_subject_protection":
        if (runtime_qa.get("source") != data["normalized_image"] or
                runtime_qa.get("output") != data["runtime_rgba"] or
                runtime_qa.get("protection_mask") != data["protection_mask"] or
                runtime_qa.get("generator") != g.ref(protected_derivative.__file__) or
                runtime_qa.get("base_generator") != g.ref(runtime_chroma.__file__) or
                runtime_qa.get("edge_classifier") != g.ref(chroma.__file__) or
                runtime_qa.get("visible_rgb_byte_exact") is not True or
                runtime_qa.get("outside_protection_byte_exact_to_original_derivative") is not True or
                runtime_qa.get("border_transparent") is not True):
            errors.append("EXACT_PROTECTED_DERIVATIVE_QA_REQUIRED")
    else:
        if (runtime_qa.get("input") != data["normalized_image"]["path"] or
                runtime_qa.get("input_sha256") != data["normalized_image"]["sha256"] or
                runtime_qa.get("output") != data["runtime_rgba"]["path"] or
                runtime_qa.get("output_sha256") != data["runtime_rgba"]["sha256"] or
                runtime_qa.get("visible_rgb_byte_exact") is not True or
                runtime_qa.get("visible_strong_green_alpha_boundary_residual_pixels") != 0):
            errors.append("VISIBLE_FRAME_RUNTIME_RGBA_QA_BINDING")
    bindings = dict(request_audit["bindings"])
    for item in [g.ref(path), data["attempt_permit"], *refs, *[g.ref(p) for p in consumed_code()]]:
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

