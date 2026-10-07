"""External, Pillow-capable verifier for one sealed MICA E motion pilot.

This runs under project Python before Blender.  It validates source authority
and writes the sole permit consumed by Blender's embedded Python, which must
not re-enter the Pillow-backed ImageGen intake path.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g


def _expect_ref(actual, expected, code):
    if actual != expected:
        raise ValueError(code)


def verify_static_review_bundle(plan_path, config_path, bundle_path):
    """Require hashed primary and independent reviews for the exact code plan."""
    bundle = g.read(bundle_path)
    expected_roles = {"primary_implementation_review", "independent_ponytail_review"}
    if (bundle.get("schema") != 1 or bundle.get("stage") != "motion_pilot_static_review_bundle"
            or bundle.get("plan") != g.ref(plan_path)
            or bundle.get("config") != g.ref(config_path)
            or bundle.get("exporter") != g.ref(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py")):
        raise ValueError("EXACT_MOTION_PILOT_STATIC_REVIEW_BUNDLE_REQUIRED")
    entries = bundle.get("reviews")
    if (not isinstance(entries, list) or len(entries) != 2
            or {entry.get("role") for entry in entries} != expected_roles):
        raise ValueError("MOTION_PILOT_INDEPENDENT_REVIEW_COVERAGE_REQUIRED")
    reviewers = set()
    for entry in entries:
        if set(entry) != {"role", "review"}:
            raise ValueError("HASHED_MOTION_PILOT_REVIEW_REFERENCE_REQUIRED")
        review = g.read(g.resolve(entry["review"]))
        if (review.get("schema") != 1 or review.get("stage") != "motion_pilot_static_review"
                or review.get("role") != entry["role"]
                or not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip()
                or not isinstance(review.get("reviewed_utc"), str) or not review["reviewed_utc"].strip()
                or review.get("verdict") != "PASS"
                or review.get("plan") != g.ref(plan_path)
                or review.get("config") != g.ref(config_path)
                or review.get("exporter") != g.ref(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py")):
            raise ValueError("MOTION_PILOT_REVIEW_NOT_CURRENT")
        reviewers.add(review["reviewer"])
        checks = review.get("checks")
        if not isinstance(checks, dict) or not checks or any(value != "PASS" for value in checks.values()):
            raise ValueError("MOTION_PILOT_REVIEW_CHECKS_INCOMPLETE")
        evidence = g.read(g.resolve(review["reply_evidence"]))
        if (evidence.get("schema") != 1 or evidence.get("stage") != "motion_pilot_static_review_evidence"
                or evidence.get("reviewer") != review["reviewer"]
                or evidence.get("plan") != g.ref(plan_path)
                or evidence.get("config") != g.ref(config_path)
                or evidence.get("exporter") != g.ref(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py")
                or evidence.get("checked") != checks):
            raise ValueError("MOTION_PILOT_REVIEW_EVIDENCE_BINDING_MISMATCH")
    if len(reviewers) != 2:
        raise ValueError("MOTION_PILOT_REVIEWS_REQUIRE_DISTINCT_IDENTITIES")
    return bundle


def verify(out_arg):
    out = g.local(out_arg)
    inputs_path = out / "MOTION_PILOT_INPUTS.json"
    inputs = g.read(inputs_path)
    if inputs.get("schema") != 1 or inputs.get("stage") != "camera_plane_motion_pilot_inputs":
        raise ValueError("EXACT_CAMERA_PLANE_MOTION_INPUTS_REQUIRED")
    plan_path = g.resolve(inputs["plan"])
    config_path = g.resolve(inputs["config"])
    attempt_path = g.resolve(inputs["attempt"])
    review_bundle_path = g.resolve(inputs["review_bundle"])
    plan = g.read(plan_path)
    config = g.read(config_path)
    attempt = g.read(attempt_path)
    if (plan.get("schema") != 1 or plan.get("stage") != "motion_pilot_plan"
            or plan.get("scope", {}).get("actor_id") != "MICA"
            or plan.get("scope", {}).get("direction") != "E"
            or plan.get("limits", {}).get("invocations") != 1
            or plan.get("limits", {}).get("max_frames") != 49
            or plan.get("limits", {}).get("threads") != 2
            or isinstance(plan.get("limits", {}).get("timeout_seconds"), bool)
            or not isinstance(plan.get("limits", {}).get("timeout_seconds"), int)
            or not 240 <= plan["limits"]["timeout_seconds"] <= 1200):
        raise ValueError("EXACT_E_ONLY_CAMERA_PLANE_MOTION_PLAN_REQUIRED")
    _expect_ref(plan["inputs"]["export_config"], g.ref(config_path), "PLAN_CONFIG_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["motion_exporter"], g.ref(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py"), "PLAN_EXPORTER_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["verifier"], g.ref(__file__), "PLAN_VERIFIER_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["runner"], g.ref(ROOT / "tools/character_pipeline/run_mica_E_camera_plane_motion_pilot.py"), "PLAN_RUNNER_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["blender"], g.ref(ROOT / "tools/blender/5.2.1/blender.exe"), "PLAN_BLENDER_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["generation_harness"], g.ref(ROOT / "tools/character_pipeline/generation_harness.py"), "PLAN_GENERATION_HARNESS_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["mesh_collector"], g.ref(ROOT / "tools/character_pipeline/collect_generation_mesh_preflight.py"), "PLAN_MESH_COLLECTOR_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["camera_lock_validator"], g.ref(ROOT / "tools/character_pipeline/root_locked_capture.py"), "PLAN_CAMERA_LOCK_VALIDATOR_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["pose_application_diagnostic_script"], g.ref(ROOT / "tools/character_pipeline/diagnose_mica_E_camera_plane_pose_application.py"), "PLAN_POSE_APPLICATION_DIAGNOSTIC_SCRIPT_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["fullclip_export_context_diagnostic_script"], g.ref(ROOT / "tools/character_pipeline/diagnose_mica_E_camera_plane_fullclip_context.py"), "PLAN_FULLCLIP_EXPORT_CONTEXT_DIAGNOSTIC_SCRIPT_BINDING_MISMATCH")
    if (plan.get("outputs", {}).get("root") != str(out.relative_to(ROOT))
            or plan["outputs"].get("geometry") != config.get("output")
            or plan["outputs"].get("render_receipt") != config.get("render_receipt")):
        raise ValueError("PLAN_OUTPUT_DESTINATION_BINDING_MISMATCH")
    if (inputs.get("runner") != plan["inputs"]["runner"]
            or inputs.get("verifier") != plan["inputs"]["verifier"]):
        raise ValueError("MOTION_PILOT_INPUT_RUNNER_VERIFIER_BINDING_MISMATCH")
    verify_static_review_bundle(plan_path, config_path, review_bundle_path)
    if (attempt.get("schema") != 1 or attempt.get("stage") != "camera_plane_motion_pilot_attempt"
            or attempt.get("status") != "RESERVED_ONE_BLENDER_INVOCATION"
            or attempt.get("plan") != g.ref(plan_path)
            or attempt.get("config") != g.ref(config_path)
            or attempt.get("review_bundle") != g.ref(review_bundle_path)
            or attempt.get("runner") != plan["inputs"]["runner"]
            or attempt.get("limits") != plan["limits"]):
        raise ValueError("EXACT_RESERVED_CAMERA_PLANE_MOTION_ATTEMPT_REQUIRED")
    if (config.get("qa_fixture_only") is not False or config.get("direction") != "E"
            or config.get("motion_channel") != "run/E/camera_plane_pilot"
            or len(config.get("frames", [])) != 49):
        raise ValueError("EXACT_E_ONLY_CAMERA_PLANE_MOTION_CONFIG_REQUIRED")
    receipt = g.verify_receipt(config["generation_receipt"], stage="first_pose")
    g.assert_production_source_receipt(receipt)
    if receipt.get("approved_scope") != ["E"] or config.get("subject_sha256") != receipt["subject_sha256"]:
        raise ValueError("FIRST_POSE_RECEIPT_DOES_NOT_SEAL_E_PILOT")
    if config.get("approved_scene_sha256") != receipt["scene_sha256"]:
        raise ValueError("CAMERA_PLANE_CONFIG_SCENE_BINDING_MISMATCH")
    tolerance = float(config.get("camera_plane_global_matrix_tolerance"))
    materialization_tolerance = float(config.get("camera_plane_projection_materialization_tolerance"))
    diagnostic = g.read(g.resolve(plan["inputs"]["pose_application_diagnostic"]))
    if (not 0.0 < tolerance <= 1e-5 or diagnostic.get("stage") != "camera_plane_pose_application_diagnostic"
            or diagnostic.get("production_ready") is not False
            or g.local(diagnostic.get("blend", {}).get("path", "")) != g.resolve(receipt["blend"])
            or diagnostic.get("blend", {}).get("sha256") != receipt["blend"]["sha256"]
            or diagnostic.get("source_pose_index") != 0
            or not 0.0 < float(diagnostic.get("maximum_global_matrix_error", 0)) <= tolerance):
        raise ValueError("MEASURED_CAMERA_PLANE_GLOBAL_MATRIX_TOLERANCE_REQUIRED")
    fullclip_diagnostic = g.read(g.resolve(plan["inputs"]["fullclip_export_context_diagnostic"]))
    fullclip_expected_indices = list(range(0, 97, 4))
    if (not tolerance <= materialization_tolerance <= 1.1e-5
            or fullclip_diagnostic.get("stage") != "camera_plane_fullclip_export_context_diagnostic"
            or fullclip_diagnostic.get("production_ready") is not False
            or g.local(fullclip_diagnostic.get("blend", {}).get("path", "")) != g.resolve(receipt["blend"])
            or fullclip_diagnostic.get("blend", {}).get("sha256") != receipt["blend"]["sha256"]
            or fullclip_diagnostic.get("source_pose_indices") != fullclip_expected_indices
            or fullclip_diagnostic.get("unique_source_phase_count") != len(fullclip_expected_indices)
            or fullclip_diagnostic.get("within_configured_tolerance") is not False
            or not tolerance < float(fullclip_diagnostic.get("maximum_global_matrix_error", 0)) <= materialization_tolerance):
        raise ValueError("MEASURED_FULLCLIP_CAMERA_PLANE_MATERIALIZATION_TOLERANCE_REQUIRED")
    pose_bundle = g.read(g.resolve(receipt["pose_bundle"]))
    preflight = g.read(g.resolve(pose_bundle["mesh_preflight"]))
    contract = preflight.get("contract", {})
    if contract.get("kind") != "source_preserving_surface_camera_plane_v1":
        raise ValueError("CAMERA_PLANE_SOURCE_PRESERVING_CONTRACT_REQUIRED")
    source = contract["source"]
    surface = contract["surface"]
    _expect_ref(plan["authorization"]["first_pose_receipt"], g.ref(config["generation_receipt"]), "PLAN_FIRST_POSE_RECEIPT_BINDING_MISMATCH")
    _expect_ref(plan["authorization"]["source_receipt"], receipt["source_receipt"], "PLAN_SOURCE_RECEIPT_BINDING_MISMATCH")
    _expect_ref(plan["authorization"]["sealed_blend"], receipt["blend"], "PLAN_SEALED_BLEND_BINDING_MISMATCH")
    _expect_ref(plan["authorization"]["mesh_preflight"], g.ref(g.resolve(pose_bundle["mesh_preflight"])), "PLAN_MESH_PREFLIGHT_BINDING_MISMATCH")
    if (config.get("skinned_mesh") != surface["mesh"]
            or config.get("body_coordinate_frame") != surface["rig"]
            or float(config.get("scene_unit_scale", 1)) != float(preflight["scene"]["unit_scale"])
            or [config.get("native_size", 1920)] * 2 + [100] != preflight["scene"]["render"]
            or source["source_receipt"] != receipt["source_receipt"]
            or source["raw_tripo_pose_matrices"] != g.ref(config["camera_plane_pose_matrices"])
            or source["source_skin_snapshot"] != g.ref(config["camera_plane_source_skin"])
            or source["sole_binding_evidence"] != g.ref(config["camera_plane_sole_binding_evidence"])):
        raise ValueError("CAMERA_PLANE_CONFIG_SUBSTITUTES_SEALED_SOURCE_BINDING")
    sole = g.read(g.local(config["camera_plane_sole_binding_evidence"]))
    expected_sole_ids = {
        "left": sorted({int(vertex) for triangle in sole["visible_sole_bindings"]["l"]["vertices"] for vertex in triangle}),
        "right": sorted({int(vertex) for triangle in sole["visible_sole_bindings"]["r"]["vertices"] for vertex in triangle}),
    }
    if config.get("sole_vertex_ids") != expected_sole_ids:
        raise ValueError("CAMERA_PLANE_CONFIG_SUBSTITUTES_REVIEWED_SOLE_GEOMETRY")
    schedule = g.read(g.local(config["camera_plane_support_schedule"]))
    if schedule.get("proposed_poses") != source["raw_tripo_pose_matrices"]:
        raise ValueError("SUPPORT_SCHEDULE_NOT_BOUND_TO_REVIEWED_TRIPO_MATRICES")
    _expect_ref(plan["inputs"]["tripo_matrices"], g.ref(config["camera_plane_pose_matrices"]), "PLAN_TRIPO_MATRIX_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["source_skin"], g.ref(config["camera_plane_source_skin"]), "PLAN_SOURCE_SKIN_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["support_schedule"], g.ref(config["camera_plane_support_schedule"]), "PLAN_SUPPORT_SCHEDULE_BINDING_MISMATCH")
    _expect_ref(plan["inputs"]["sole_binding_evidence"], g.ref(config["camera_plane_sole_binding_evidence"]), "PLAN_SOLE_BINDING_EVIDENCE_MISMATCH")
    indices = [row.get("source_pose_index") for row in config["frames"]]
    expected_indices = list(range(0, 97, 4)) + list(range(4, 97, 4))
    if indices != expected_indices or any(row.get("frame") != index + 1 for index, row in enumerate(config["frames"])):
        raise ValueError("EXACT_24_PHASE_CYCLIC_DIAGNOSTIC_MAP_REQUIRED")
    if any((g.local(row["master_image"]).exists() or g.local(row["image"]).exists()) for row in config["frames"]):
        raise ValueError("CAMERA_PLANE_MOTION_OUTPUT_ALREADY_EXISTS")
    if g.local(config["output"]).exists() or g.local(config["render_receipt"]).exists():
        raise ValueError("CAMERA_PLANE_MOTION_LEDGER_ALREADY_EXISTS")
    if (g.local(config["camera_plane_motion_permit"]) != out / "MOTION_PILOT_BLENDER_PERMIT.json"
            or g.local(config["camera_plane_motion_consumption"]) != out / "MOTION_PILOT_BLENDER_CONSUMPTION.json"
            or g.local(config["camera_plane_motion_inputs"]) != inputs_path
            or g.local(config["camera_plane_motion_attempt"]) != attempt_path):
        raise ValueError("EXACT_CAMERA_PLANE_MOTION_HANDOFF_DESTINATIONS_REQUIRED")
    permit = {
        "schema": 1,
        "stage": "camera_plane_motion_blender_permit",
        "config": g.ref(config_path),
        "inputs": g.ref(inputs_path),
        "attempt": g.ref(attempt_path),
        "generation_receipt": g.ref(config["generation_receipt"]),
        "sealed_blend": receipt["blend"],
        "direction": "E",
        "tripo_matrices": g.ref(config["camera_plane_pose_matrices"]),
        "source_skin": g.ref(config["camera_plane_source_skin"]),
        "support_schedule": g.ref(config["camera_plane_support_schedule"]),
        "sole_binding_evidence": g.ref(config["camera_plane_sole_binding_evidence"]),
        "scene_sha256": receipt["scene_sha256"],
        "output_root": str(out.relative_to(ROOT)),
    }
    permit_path = out / "MOTION_PILOT_BLENDER_PERMIT.json"
    if permit_path.exists():
        raise ValueError("CAMERA_PLANE_MOTION_PERMIT_ALREADY_EXISTS")
    g.write(permit_path, permit)
    return permit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    result = verify(parser.parse_args().out)
    print("CAMERA_PLANE_MOTION_PERMIT_READY", result["output_root"])
