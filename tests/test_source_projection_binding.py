import pathlib
import sys
import unittest
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools/character_pipeline'))
from source_projection_binding import project, unproject


class ProjectionTests(unittest.TestCase):
    def test_physical_depth_does_not_change_original_pixel(self):
        for elevation in [15,30,45]:
            config = dict(ground_pixel=[473,1492], original_metres_per_pixel=1.72/1450,
                          elevation_degrees=elevation)
            for pixel in [[442,42],[499,710],[334,1003],[213,1482]]:
                for height in [0,.095,.49,.9116,1.72]:
                    point = unproject(pixel, height, **config)
                    np.testing.assert_allclose(project(point, **config), pixel, atol=1e-10)
                    self.assertEqual(point[2], height)

    def test_coplanar_sole_points_can_preserve_different_image_rows(self):
        config = dict(ground_pixel=[473,1492], original_metres_per_pixel=1.72/1450,
                      elevation_degrees=30)
        first = unproject([210,1490], 0, **config)
        second = unproject([770,1465], 0, **config)
        self.assertEqual(first[2], second[2])
        self.assertNotEqual(first[1], second[1])

    def test_degenerate_camera_fails(self):
        with self.assertRaises(ValueError):
            unproject([0,0], 0, ground_pixel=[0,0], original_metres_per_pixel=.001, elevation_degrees=0)


if __name__ == '__main__':
    unittest.main()
