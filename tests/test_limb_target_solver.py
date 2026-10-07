import pathlib
import sys
import unittest
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools/character_pipeline'))
from limb_target_solver import solve


class LimbSolverTests(unittest.TestCase):
    def test_preserves_lengths_root_and_contact_target(self):
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            hip = np.array([0.0, .8, 0.0])
            ankle = np.array([.3*np.cos(angle), 0, .3*np.sin(angle)])
            result = solve(hip, ankle, hip + [np.cos(angle), 0, np.sin(angle)], .5, .45)
            np.testing.assert_array_equal(result['hip'], hip)
            np.testing.assert_array_equal(result['ankle'], ankle)
            self.assertAlmostEqual(np.linalg.norm(result['knee']-hip), .5)
            self.assertAlmostEqual(np.linalg.norm(ankle-result['knee']), .45)
            self.assertFalse(result['root_translation_applied'])
            self.assertFalse(result['limb_stretch_applied'])

    def test_unreachable_is_not_silently_stretched_or_lifted(self):
        with self.assertRaisesRegex(ValueError, 'OUTSIDE_FIXED_LENGTH_REACH'):
            solve([0, 1, 0], [0, 0, 0], [1, .5, 0], .4, .4)

    def test_knee_bend_uses_given_anatomical_plane(self):
        left = solve([0,0,0], [1,0,0], [0,1,0], .7, .7)
        right = solve([0,0,0], [1,0,0], [0,-1,0], .7, .7)
        self.assertGreater(left['knee'][1], 0)
        self.assertLess(right['knee'][1], 0)

    def test_invalid_inputs_fail_closed(self):
        for target in ([float('nan'), 0, 0], [0, 0], [0,0,0]):
            with self.assertRaises(ValueError):
                solve([0,0,0], target, [0,1,0], .7, .7)
        with self.assertRaisesRegex(ValueError, 'KNEE_PLANE'):
            solve([0,0,0], [1,0,0], [.5,0,0], .7, .7)


if __name__ == '__main__':
    unittest.main()
