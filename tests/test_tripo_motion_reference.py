"""Negative intake/receipt regressions; no Blender, generation or promotion."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import tripo_motion_reference as t

BASE = ROOT / "art_src/motion_reference/tripo_run_20260908"
SOURCE = BASE / "source/ORIGINAL_Run.glb"
LICENSE = BASE / "source/MODEL_LICENSE_MANIFEST.json"


class IntakeRegression(unittest.TestCase):
    def test_real_source_has_actual_skin_and_native_duration(self):
        result = t.inspect(SOURCE, LICENSE)
        self.assertEqual(result["joint_count"], 41)
        self.assertEqual(result["vertices"], 26588)
        self.assertAlmostEqual(result["duration_s"], 1.25, places=6)
        self.assertIs(result["production_ready"], False)

    def test_license_for_different_glb_is_rejected(self):
        record = t.g.read(LICENSE)
        record["model"]["sha256"] = "0"*64
        with patch.object(t.g, "read", return_value=record):
            with self.assertRaisesRegex(ValueError, "EXACT_GLB_LICENSE"):
                t.inspect(SOURCE, LICENSE)

    def test_string_paid_flag_does_not_authorize_intake(self):
        record = t.g.read(LICENSE)
        record["paid_at_generation_user_attested"] = "true"
        with patch.object(t.g, "read", return_value=record):
            with self.assertRaisesRegex(ValueError, "PAID_OUTPUT_LICENSE"):
                t.inspect(SOURCE, LICENSE)

    def test_negative_actual_weights_rejected(self):
        doc, _ = t.decode_glb(SOURCE)
        index = doc["meshes"][0]["primitives"][0]["attributes"]["WEIGHTS_0"]
        original = t.accessor
        def changed(d, b, i):
            rows = original(d, b, i)
            if i == index:
                rows[0] = (-.1, 1.1, 0, 0)
            return rows
        with patch.object(t, "accessor", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "INVALID_ACTUAL_SKIN"):
                t.inspect(SOURCE, LICENSE)

    def test_duplicate_native_timestamps_rejected(self):
        doc, _ = t.decode_glb(SOURCE)
        index = doc["animations"][0]["samplers"][0]["input"]
        original = t.accessor
        def changed(d, b, i):
            rows = original(d, b, i)
            if i == index:
                rows[1] = rows[0]
            return rows
        with patch.object(t, "accessor", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "INCREASING_NATIVE_TIMESTAMPS"):
                t.inspect(SOURCE, LICENSE)

    def test_unskinned_visible_mesh_rejected(self):
        doc, binary = t.decode_glb(SOURCE)
        doc = copy.deepcopy(doc)
        for node in doc["nodes"]:
            if "mesh" in node: node.pop("skin", None)
        with patch.object(t, "decode_glb", return_value=(doc,binary)):
            with self.assertRaisesRegex(ValueError, "UNSKINNED_MESH"):
                t.inspect(SOURCE, LICENSE)

    def test_fake_production_completion_rejected_before_files(self):
        fake = {"schema":1,"stage":"tripo_reference_pack","production_ready":True,
                "visible_art_authority":"none","owned_child_exited":True}
        with patch.object(t.g,"read",return_value=fake):
            with self.assertRaisesRegex(ValueError,"REFERENCE_ONLY_COMPLETION"):
                t.verify("fake.json")

    def test_actual_fresh_pack_verifies_without_promoting(self):
        result=t.verify(BASE / "pack_r03/completion.json")
        self.assertIs(result["production_ready"],False)
        self.assertEqual(result["visible_art_authority"],"none")
        self.assertTrue(result["contact_errors"])

    def test_foreign_map_internal_source_rejected(self):
        original=t.g.read
        def altered(path):
            result=original(path)
            if Path(path).name=="HUMANOID_MAP.json":
                result["source"]["sha256"]="0"*64
            return result
        with patch.object(t.g,"read",side_effect=altered):
            with self.assertRaisesRegex(ValueError,"HUMANOID_MAP_SOURCE_MISMATCH"):
                t.verify(BASE / "pack_r03/completion.json")

    def test_calibrator_cannot_borrow_other_scene(self):
        original=t.g.read
        def altered(path):
            result=original(path)
            if Path(path).name=="CALIBRATOR_INPUT.json":
                result["output_blend"]["sha256"]="0"*64
            return result
        with patch.object(t.g,"read",side_effect=altered):
            with self.assertRaisesRegex(ValueError,"CALIBRATOR_PACK_BINDING_MISMATCH"):
                t.verify(BASE / "pack_r03/completion.json")

    def test_claim_cannot_borrow_other_builder(self):
        original=t.g.read
        def altered(path):
            result=original(path)
            if Path(path).name=="CHILD_CLAIM.json":
                result["builder"]["sha256"]="0"*64
            return result
        with patch.object(t.g,"read",side_effect=altered):
            with self.assertRaisesRegex(ValueError,"EXACT_CONSUMED_CHILD_CLAIM"):
                t.verify(BASE / "pack_r03/completion.json")


if __name__ == "__main__": unittest.main()
