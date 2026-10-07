"""Inverse orthographic projection for original-pixel deformation support.

No artwork or mesh is generated here. Physical heights are explicit inputs and
remain subject to anatomical and original-art review.
"""
import math
import numpy as np


def unproject(pixel, physical_height, *, ground_pixel, original_metres_per_pixel, elevation_degrees):
    values = [*pixel, physical_height, *ground_pixel, original_metres_per_pixel, elevation_degrees]
    if not all(math.isfinite(v) for v in values) or original_metres_per_pixel <= 0:
        raise ValueError('FINITE_SOURCE_PROJECTION_INPUTS_REQUIRED')
    if not 5 <= elevation_degrees <= 60:
        raise ValueError('CALIBRATED_NONDEGENERATE_CAMERA_ELEVATION_REQUIRED')
    angle = math.radians(elevation_degrees)
    cosine, sine = math.cos(angle), math.sin(angle)
    scale = original_metres_per_pixel * cosine
    x = (pixel[0] - ground_pixel[0]) * scale
    h = (ground_pixel[1] - pixel[1]) * scale
    y = (h - physical_height * cosine) / sine
    return np.array([x, y, physical_height])


def project(world, *, ground_pixel, original_metres_per_pixel, elevation_degrees):
    angle = math.radians(elevation_degrees)
    cosine, sine = math.cos(angle), math.sin(angle)
    scale = original_metres_per_pixel * cosine
    return np.array([world[0]/scale + ground_pixel[0],
                     ground_pixel[1] - (world[1]*sine + world[2]*cosine)/scale])
