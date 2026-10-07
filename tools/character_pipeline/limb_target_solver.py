"""Two-link anatomical target solve with fixed root and explicit reach failure."""
import numpy as np


def solve(hip, ankle, knee_hint, thigh_length, calf_length):
    hip, ankle, knee_hint = (np.asarray(value, dtype=float) for value in (hip, ankle, knee_hint))
    if any(value.shape != (3,) or not np.isfinite(value).all() for value in (hip, ankle, knee_hint)):
        raise ValueError('FINITE_THREE_DIMENSIONAL_JOINT_TARGETS_REQUIRED')
    if not all(np.isfinite(v) and v > 0 for v in (thigh_length, calf_length)):
        raise ValueError('POSITIVE_ANATOMICAL_LIMB_LENGTHS_REQUIRED')
    offset = ankle - hip
    distance = float(np.linalg.norm(offset))
    if distance < 1e-9 or distance > thigh_length + calf_length + 1e-9 or distance < abs(thigh_length - calf_length) - 1e-9:
        raise ValueError('TARGET_OUTSIDE_FIXED_LENGTH_REACH')
    direction = offset / distance
    pole = knee_hint - hip
    pole -= direction * np.dot(pole, direction)
    pole_length = float(np.linalg.norm(pole))
    if pole_length < 1e-8:
        raise ValueError('DISTINCT_ANATOMICAL_KNEE_PLANE_REQUIRED')
    along = (thigh_length ** 2 - calf_length ** 2 + distance ** 2) / (2 * distance)
    away = np.sqrt(max(0.0, thigh_length ** 2 - along ** 2))
    knee = hip + direction * along + pole * (away / pole_length)
    return {'hip': hip.copy(), 'knee': knee, 'ankle': ankle.copy(),
            'root_translation_applied': False, 'limb_stretch_applied': False}
