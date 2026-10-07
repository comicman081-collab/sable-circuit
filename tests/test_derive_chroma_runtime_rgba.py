import sys
import unittest
import uuid
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import derive_chroma_runtime_rgba as derive


class ChromaRuntimeDerivationTests(unittest.TestCase):
    def test_connected_spill_removed_cyan_subject_preserved(self):
        work = ROOT / "artifacts/generation_harness_audit/unit_fixtures/chroma_rgba" / uuid.uuid4().hex
        work.mkdir(parents=True)
        rgb = np.full((64, 64, 3), [0, 255, 0], dtype=np.uint8)
        rgb[10:54, 16:48] = [20, 30, 40]
        rgb[10, 16:48] = [20, 180, 20]
        rgb[30:34, 24:28] = [20, 180, 20]
        rgb[40:42, 24:28] = [2, 79, 4]
        rgb[42:44, 24:28] = [7, 28, 7]
        rgb[20:24, 20:30] = [0, 220, 220]
        rgb[24:28, 20:30] = [0, 80, 70]
        # Cyan/teal antialiasing can have a large G-R delta while B remains
        # close to G. It must stay opaque even when touching chroma background.
        rgb[8:10, 48:52] = [140, 233, 217]
        source, output = work / "green.png", work / "runtime.png"
        Image.fromarray(rgb, "RGB").save(source)
        report = derive.derive(source, output)
        rgba = np.asarray(Image.open(output).convert("RGBA"))
        self.assertTrue(np.all(rgba[10, 16:48, 3] == 0))
        self.assertTrue(np.all(rgba[30:34, 24:28, 3] == 0))
        self.assertTrue(np.all(rgba[40:42, 24:28, 3] == 0))
        self.assertTrue(np.all(rgba[42:44, 24:28, 3] == 0))
        self.assertTrue(np.all(rgba[20:24, 20:30, 3] == 255))
        self.assertTrue(np.all(rgba[20:24, 20:30, :3] == [0, 220, 220]))
        self.assertTrue(np.all(rgba[24:28, 20:30, 3] == 255))
        self.assertTrue(np.all(rgba[24:28, 20:30, :3] == [0, 80, 70]))
        self.assertTrue(np.all(rgba[8:10, 48:52, 3] == 255))
        self.assertTrue(np.all(rgba[8:10, 48:52, :3] == [140, 233, 217]))
        self.assertTrue(report["visible_rgb_byte_exact"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
