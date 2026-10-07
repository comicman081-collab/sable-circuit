import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/character_pipeline/calibrate_vrm_ual_ground_contact.py"
SPEC = importlib.util.spec_from_file_location("pose_guide_contact", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
CONTRACT = json.loads((ROOT / "tools/character_pipeline/pose_guide_contact_contract.json").read_text())
CURRENT_PATH = ROOT / "tools/character_pipeline/visible_frame_harness_current.py"
CURRENT_SPEC = importlib.util.spec_from_file_location("visible_frame_current", CURRENT_PATH)
CURRENT = importlib.util.module_from_spec(CURRENT_SPEC)
assert CURRENT_SPEC.loader is not None
CURRENT_SPEC.loader.exec_module(CURRENT)


def row(sample, left_clearance, right_clearance, delta, pelvis_z, left_yaw=2.0, right_yaw=2.0):
    return {
        "sample": sample,
        "sole_clearance_m": {"left": left_clearance, "right": right_clearance},
        "left_minus_right_travel_m": delta,
        "pelvis_world_m": [0.0, 0.0, pelvis_z],
        "foot_yaw_from_travel_degrees": {"left": left_yaw, "right": right_yaw},
        "sole_vertices_world_m": {
            "left": [[float(sample), 1.0, left_clearance]],
            "right": [[float(sample), -1.0, right_clearance]],
        },
    }


class PoseGuideContactHarnessTests(unittest.TestCase):
    def valid_cycle(self):
        rows = [
            row(0, .003, .12, 1.0, 1.00),
            row(1, .006, .12, .8, .95),
            row(2, .007, .12, -.1, .98),
            row(3, .10, .11, -1.0, 1.02),
            row(4, .12, .003, -1.0, 1.00),
            row(5, .12, .006, -.8, .95),
            row(6, .12, .007, .1, .98),
            row(7, .11, .10, 1.0, 1.02),
        ]
        wrap = copy.deepcopy(rows[0])
        wrap["sample"] = 8
        rows.append(wrap)
        return rows

    def test_eight_distinct_phase_candidates_can_pass(self):
        phases, errors = MODULE._classify(self.valid_cycle(), CONTRACT)
        self.assertEqual(errors, [])
        self.assertEqual(len(phases), 8)
        self.assertEqual(len(set(phases.values())), 8)

    def test_penetration_yaw_and_duplicate_phases_fail_closed(self):
        rows = self.valid_cycle()
        rows[0]["sole_clearance_m"]["left"] = -.02
        rows[0]["foot_yaw_from_travel_degrees"]["left"] = 70.0
        rows[0]["pelvis_world_m"][2] = .9
        rows[1]["pelvis_world_m"][2] = 1.1
        rows[2]["pelvis_world_m"][2] = 1.0
        rows[0]["left_minus_right_travel_m"] = .1
        rows[2]["left_minus_right_travel_m"] = 1.2
        rows[-1]["sole_vertices_world_m"] = copy.deepcopy(rows[0]["sole_vertices_world_m"])
        _, errors = MODULE._classify(rows, CONTRACT)
        self.assertIn("FIXED_FLOOR_PENETRATION_LEFT", errors)
        self.assertIn("FOOT_YAW_EXCEEDS_TRAVEL_CONTRACT_LEFT", errors)
        self.assertIn("SUPPORT_MUST_PERSIST_THROUGH_TRUE_PASSING_LEFT", errors)

    def test_current_reserve_route_requires_calibration_for_support_phases(self):
        self.assertEqual(
            CURRENT._audit_contact_calibration({}, "E", "run", "contact_l"),
            ["FIXED_FLOOR_CONTACT_CALIBRATION_REQUIRED"],
        )
        self.assertEqual(CURRENT._audit_contact_calibration({}, "E", "run", "flight_l"), [])

    def test_current_gate_rejects_swapped_valid_json_refs(self):
        original_resolve = CURRENT.g.resolve
        original_read = CURRENT.g.read
        original_ref = CURRENT.g.ref
        original_verify = CURRENT.g.verify_reviews
        report = {
            "status": "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY",
            "errors": [],
            "production_ready": False,
            "visible_art_authority": "built_in_ImageGen_only",
            "blender_ual_role": "pose_geometry_guide_only",
            "input_result": {"path": "result", "sha256": "r"},
            "input_blend": {"path": "blend", "sha256": "b"},
            "contract": {"path": "wrong-valid.json", "sha256": "x"},
            "generator": {"path": "wrong-valid.json", "sha256": "x"},
            "phase_candidates": {},
            "samples": [],
        }
        guide = {
            "contact_calibration": {"path": "report", "sha256": "c"},
            "capture": {"path": "capture", "sha256": "p"},
            "blend": report["input_blend"],
            "current_gate": {"path": "wrong-valid.json", "sha256": "x"},
            "contact_contract": {"path": "wrong-valid.json", "sha256": "x"},
            "visual_promotion_contract": {"path": "wrong-valid.json", "sha256": "x"},
            "contact_calibrator": {"path": "wrong-valid.json", "sha256": "x"},
            "contact_calibration_phase": "contact_l",
        }
        try:
            CURRENT.g.resolve = lambda ref: ref["path"]
            CURRENT.g.read = lambda path: report if path == "report" else {
                "retarget_result": report["input_result"],
                "blend": report["input_blend"],
                "calibration": guide["contact_calibration"],
                "frames": [],
            }
            CURRENT.g.ref = lambda path: {
                "path": str(path), "sha256": "approved-" + Path(path).name
            }
            CURRENT.g.verify_reviews = lambda *args, **kwargs: []
            errors = CURRENT._audit_contact_calibration(guide, "E", "run", "contact_l")
        finally:
            CURRENT.g.resolve = original_resolve
            CURRENT.g.read = original_read
            CURRENT.g.ref = original_ref
            CURRENT.g.verify_reviews = original_verify
        self.assertIn("EXACT_CURRENT_VISIBLE_FRAME_GATE_REQUIRED", errors)
        self.assertIn("EXACT_CONTACT_CONTRACT_REQUIRED", errors)
        self.assertIn("EXACT_VISUAL_PROMOTION_CONTRACT_REQUIRED", errors)
        self.assertIn("EXACT_CONTACT_CALIBRATOR_REQUIRED", errors)
        self.assertIn("CALIBRATION_REPORT_CONTRACT_NOT_CURRENT", errors)
        self.assertIn("CALIBRATION_REPORT_GENERATOR_NOT_CURRENT", errors)

    def test_temporally_scrambled_cycle_is_rejected(self):
        valid = self.valid_cycle()[:-1]
        scrambled = [copy.deepcopy(valid[index]) for index in (0, 3, 2, 1, 4, 7, 6, 5)]
        for sample, item in enumerate(scrambled):
            item["sample"] = sample
        wrap = copy.deepcopy(scrambled[0])
        wrap["sample"] = len(scrambled)
        scrambled.append(wrap)
        _, errors = MODULE._classify(scrambled, CONTRACT)
        self.assertTrue(errors)
        self.assertTrue(any(
            token in errors for token in (
                "CYCLIC_GAIT_PHASE_ORDER_INVALID",
                "COMPLETE_EIGHT_PHASE_CANDIDATE_SET_REQUIRED",
                "SUPPORT_MUST_PERSIST_THROUGH_TRUE_PASSING_LEFT",
                "SUPPORT_MUST_PERSIST_THROUGH_TRUE_PASSING_RIGHT",
            )
        ))


if __name__ == "__main__":
    unittest.main()
