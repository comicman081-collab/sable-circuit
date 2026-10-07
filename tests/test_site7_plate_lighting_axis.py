"""Exercise the branch-only axis exception through the real pixel audit."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plate_audit', ROOT / 'tools/environment/audit_site7_plate_lighting.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BranchAxisControls(unittest.TestCase):
    def measure(self, plate_id, angle):
        rise = 1254 * math.tan(math.radians(angle))
        floor = [[0, 65], [1254, 65 + rise], [1254, 397 + rise], [0, 397]]
        # Real pixel mask/statistics and axis decision, with file I/O replaced
        # by an in-memory neutral image; the test writes no record or cache.
        with patch('PIL.Image.open', return_value=Image.new('RGB', (1254, 1254), (51, 51, 51))):
            row = audit.plate_floor(SimpleNamespace(asset=f'{plate_id}_GAME.png',
                                                   floor=[(x / 1254, y / 1254) for x, y in floor]))
        self.assertAlmostEqual(row['axis'], angle, places=7)
        return row['problems']

    def test_branch_limit_is_32_5(self):
        # 31.5 until 2026-10-01; S9_C06 (32.26) and S9_C07 (about 32.0) were drawn steeper than that.
        for plate in ('S8_C06', 'S8_C07', 'S9_C06', 'S9_C07', 'S10_C06', 'S10_C07'):
            with self.subTest(plate=plate):
                self.assertEqual(self.measure(plate, 31.4), [])
                self.assertEqual(self.measure(plate, 32.4), [])
                self.assertTrue(any('floor axis' in p for p in self.measure(plate, 32.6)))
                self.assertTrue(any('floor axis' in p for p in self.measure(plate, 33.0)))

    def test_other_plates_keep_30_5_limit(self):
        for plate in ('S8_C01', 'S8_C05', 'S8_R05', 'S9_C01', 'S9_C05', 'S9_R05', 'S8_C016', 'OTHER_C06'):
            with self.subTest(plate=plate):
                self.assertTrue(any('floor axis' in p for p in self.measure(plate, 31.4)))
                self.assertEqual(self.measure(plate, 30.4), [])


if __name__ == '__main__':
    unittest.main()
