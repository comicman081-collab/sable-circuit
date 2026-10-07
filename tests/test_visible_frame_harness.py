import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import visible_frame_harness as vf
import imagegen_repair_execution_boundary as boundary


class VisibleFrameHarnessTests(unittest.TestCase):
    def test_contract_is_exact_eight_by_eight(self):
        contract = vf.g.read(vf.CONTRACT)
        self.assertEqual(len(contract["directions"]), 8)
        self.assertEqual(set(contract["directions"]), {"E", "SE", "S", "SW", "W", "NW", "N", "NE"})
        self.assertEqual(len(contract["motions"]["run"]), 8)
        self.assertEqual(len(contract["motions"]["walk"]), 8)
        self.assertIn("right leg leads", contract["phase_semantics"]["run"]["flight_l"])
        self.assertIn("left leg leads", contract["phase_semantics"]["run"]["flight_r"])

    def test_painted_checker_failure_is_not_a_valid_normalizer(self):
        self.assertEqual(vf.NORMALIZER.name, "normalize_imagegen_chroma.py")
        self.assertNotIn("checker", vf.NORMALIZER.name)

    def test_sequence_verifies_receipts_before_counting(self):
        source = Path(vf.audit_sequence.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("verify_frame_receipt(g.resolve(item))", source)
        self.assertIn("len(image_hashes) != len(expected)", source)

    def test_request_closes_fixture_and_unreserved_output_routes(self):
        source = Path(vf.audit_request.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("assert_production_source_receipt", source)
        self.assertIn("expected_raw_path", source)
        self.assertIn("FRESH_EXPECTED_IMAGEGEN_RAW_PATH_REQUIRED", source)

    def test_frame_requires_reproducible_runtime_rgba(self):
        source = Path(vf.audit_frame.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("runtime_rgba", source)
        self.assertIn("VISIBLE_FRAME_RUNTIME_RGBA_NOT_REPRODUCIBLE", source)
        self.assertIn("VISIBLE_FRAME_RUNTIME_RGBA_QA_BINDING", source)
        self.assertEqual(vf.RUNTIME_DERIVER.name, "derive_chroma_runtime_rgba.py")

    def test_pose_guide_requires_exact_phase_and_independent_reviews(self):
        source = Path(vf._audit_pose_guide.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("POSE_GUIDE_PHASE_DEFINITION_MISMATCH", source)
        self.assertIn("POSE_GUIDE_EXACT_INDEPENDENT_REVIEWS_REQUIRED", source)
        self.assertIn("unclassified_grounded_window", (ROOT / "tools/character_pipeline/probe_vrm_ual_retarget.py").read_text(encoding="utf-8"))

    def test_retry_binds_prior_failure_and_mechanism_change(self):
        source = Path(vf.audit_request.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("RETRY_MUST_BIND_PREVIOUS_FAILURE", source)
        self.assertIn("RETRY_MECHANISM_CHANGES_REQUIRED", source)

    def test_request_binds_anatomical_laterality_anchors(self):
        source = Path(vf.audit_request.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("DISTINCT_ANATOMICAL_LATERALITY_ANCHORS_REQUIRED", source)
        self.assertIn("PROMPT_MUST_BIND_BOTH_LATERALITY_ANCHORS", source)

    def test_imagegen_repair_is_explicit_and_binds_failed_target(self):
        source = Path(vf.audit_request.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn("EXPLICIT_VISIBLE_FRAME_IMAGEGEN_OPERATION_REQUIRED", source)
        self.assertIn("IMAGEGEN_REPAIR_TARGET_REQUIRED", source)
        self.assertIn('exact_refs.append(data["repair_target"])', source)
        self.assertIn("REPAIR_EXACT_PRESERVE_SCOPE_REQUIRED", source)
        self.assertIn("REPAIR_MINIMAL_CHANGE_SCOPE_REQUIRED", source)
        self.assertIn("INDEPENDENT_REPAIR_TARGET_REVIEW_REQUIRED", source)
        self.assertIn("REPAIR_TARGET_QUARANTINE_MANIFEST_REQUIRED", source)
        self.assertIn("REPAIR_TARGET_NOT_EXACT_FAILED_INVENTORY_MEMBER", source)
        self.assertIn("EXACT_IMAGEGEN_INPUT_ORDER_REQUIRED", source)
        self.assertIn("REPAIR_TARGET_MUST_BE_PRIMARY_IMAGEGEN_INPUT", source)
        self.assertIn("IMAGEGEN_IDENTITY_INPUT_NOT_IN_SOURCE_RECEIPT", source)
        self.assertIn("IMAGEGEN_DIRECTION_INPUT_NOT_DECLARED", source)
        self.assertIn("IMAGEGEN_INPUT_ORDER_MUST_BE_UNIQUE", source)
        self.assertIn("repair_target_subject", source)
        subject_source = Path(vf.repair_target_subject.__code__.co_filename).read_text(encoding="utf-8")
        self.assertIn('"prompt": data.get("prompt")', subject_source)
        self.assertIn('"previous_failure": data.get("previous_failure")', subject_source)

    def test_repair_reservation_requires_real_hard_edit_mask_boundary(self):
        source = (ROOT / "tools/character_pipeline/finalize_reviewed_visible_frame_repair_request.py").read_text(encoding="utf-8")
        current_source = (ROOT / "tools/character_pipeline/visible_frame_harness_current.py").read_text(encoding="utf-8")
        boundary_source = Path(boundary.__file__).read_text(encoding="utf-8")
        self.assertIn("install_current_patches", current_source)
        self.assertIn("frozen.audit_request = _audit_request_current", current_source)
        self.assertIn("HARD_EDIT_MASK_CAPABILITY_REQUIRED", boundary_source)
        self.assertIn("REPAIR_CHANGE_MASK_REQUIRES_EDIT_AND_PROTECTED_PIXELS", boundary_source)
        self.assertIn("INDEPENDENT_STRUCTURED_REPAIR_SCOPE_REVIEWS_REQUIRED", source)
        self.assertIn("--execution-boundary", source)
        contract = vf.g.read(ROOT / "tools/character_pipeline/imagegen_repair_execution_contract.json")
        self.assertEqual(contract["pass_verdict"], "PASS_ONE_MASKED_IMAGEGEN_EDIT_ONLY")
        self.assertIn("Ponytail FULL", contract["required_review_roles"])

    def test_boundary_rejects_all_white_mask_and_missing_proof(self):
        request = {"generator": "built_in_ImageGen", "repair_target": {"path": "target", "sha256": "t"}}
        document = {
            "schema": 1, "stage": "imagegen_repair_execution_boundary",
            "contract": {"path": "contract", "sha256": "c"},
            "generator": "built_in_ImageGen", "repair_target_subject_sha256": "scope",
            "change_mask": {"path": "mask", "sha256": "m"},
            "hard_edit_mask_supported": True, "outside_mask_pixels_immutable": True,
            "verdict": "PASS_ONE_MASKED_IMAGEGEN_EDIT_ONLY", "reviews": []
        }
        contract = {
            "pass_verdict": "PASS_ONE_MASKED_IMAGEGEN_EDIT_ONLY",
            "minimum_change_mask_coverage": 0.0005, "maximum_change_mask_coverage": 0.35,
            "boundary_review_checks": ["actual_mask_parameter_exposed"],
            "required_review_roles": ["implementation", "Ponytail FULL"]
        }
        def resolve(value):
            return ROOT / ("boundary.json" if value.get("path") == "boundary" else
                           "mask.png" if value.get("path") == "mask" else "target.png")
        with patch.object(boundary.g, "read", side_effect=lambda value: contract if Path(value) == boundary.CONTRACT else document), \
             patch.object(boundary.g, "ref", side_effect=lambda value: {"path": "contract", "sha256": "c"} if Path(value) == boundary.CONTRACT else {"path": str(value), "sha256": "x"}), \
             patch.object(boundary.g, "resolve", side_effect=resolve), \
             patch.object(boundary.g, "sha", return_value="x"), \
             patch.object(boundary.g, "pixels", side_effect=[np.zeros((8, 8, 4), dtype=np.uint8), np.full((8, 8, 4), 255, dtype=np.uint8)]), \
             patch.object(boundary.frozen, "repair_target_subject", return_value="scope"), \
             patch.object(boundary.g, "verify_reviews", return_value=["INDEPENDENT_REVIEW_COVERAGE"]):
            errors, _ = boundary.audit_boundary(request, {"path": "boundary", "sha256": "b"})
        self.assertIn("REPAIR_CHANGE_MASK_REQUIRES_EDIT_AND_PROTECTED_PIXELS", errors)
        self.assertIn("EXECUTABLE_MASK_CAPABILITY_EVIDENCE_REQUIRED", errors)
        self.assertIn("INDEPENDENT_REVIEW_COVERAGE", errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
