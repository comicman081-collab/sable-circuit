import sys
import unittest
import uuid
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import normalize_painted_checker_to_green as normalizer


class CheckerNormalizerTests(unittest.TestCase):
    def setUp(self):
        self.work = ROOT / "artifacts/generation_harness_audit/unit_fixtures/checker" / uuid.uuid4().hex
        self.work.mkdir(parents=True)

    def test_enclosed_bright_component_fails_closed(self):
        rgb = np.empty((64, 64, 3), dtype=np.uint8)
        for y in range(64):
            for x in range(64):
                value = 246 if (x // 8 + y // 8) % 2 else 254
                rgb[y, x] = [value, value, value]
        rgb[14:58, 22:44] = [25, 31, 38]
        rgb[25:35, 28:38] = [225, 190, 155]
        # An enclosed checker window and a costume highlight are not reliably
        # distinguishable by colour.  The tool must refuse both, never erase.
        rgb[30:46, 27:39] = [246, 246, 246]
        rgb[16:20, 24:28] = [242, 242, 242]
        source = self.work / "source.png"
        output = self.work / "green.png"
        mask = self.work / "mask.png"
        Image.fromarray(rgb, "RGB").save(source)
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS_ENCLOSED_BRIGHT_COMPONENTS"):
            normalizer.normalize(source, output, mask)
        self.assertFalse(output.exists())
        self.assertFalse(mask.exists())

    def test_edge_connected_only_preserves_isolated_subject(self):
        rgb = np.full((64, 64, 3), 246, dtype=np.uint8)
        rgb[12:58, 20:46] = [25, 31, 38]
        rgb[20:24, 26:30] = [242, 242, 242]
        source = self.work / "source.png"
        output = self.work / "green.png"
        mask = self.work / "mask.png"
        Image.fromarray(rgb, "RGB").save(source)
        report = normalizer.normalize(source, output, mask)
        result = np.asarray(Image.open(output).convert("RGB"))
        self.assertTrue(report["subject_pixels_byte_exact"])
        self.assertTrue(np.array_equal(result[12:58, 20:46], rgb[12:58, 20:46]))
        self.assertEqual(report["accepted_enclosed_checker_pixels"], 0)

    def test_non_checker_input_fails_closed(self):
        source = self.work / "source.png"
        Image.new("RGB", (64, 64), (20, 30, 40)).save(source)
        with self.assertRaisesRegex(ValueError, "COVERAGE"):
            normalizer.normalize(source, self.work / "green.png", self.work / "mask.png")


if __name__ == "__main__":
    unittest.main(verbosity=2)
