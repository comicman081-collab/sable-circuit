"""Continuous upper/pelvis attachment for exact-source semantic skin regions.

The field depends on source coordinates, so duplicate vertices at an ownership
boundary receive the same torso weights. It never alters UVs or artwork.
"""
import math


def _smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def apply(y, original, contract):
    start, pelvis, lower = contract['source_y_knots_px']
    if not all(isinstance(v, (float, int)) and math.isfinite(v) for v in (y, start, pelvis, lower)):
        raise ValueError('FINITE_SOURCE_WEIGHT_FIELD_REQUIRED')
    if not 0 <= start < pelvis < lower:
        raise ValueError('ORDERED_TORSO_TRANSITION_REQUIRED')
    upper_bone = contract['upper_bone']
    pelvis_bone = contract['pelvis_bone']
    if upper_bone == pelvis_bone:
        raise ValueError('DISTINCT_UPPER_AND_PELVIS_REQUIRED')
    if not original or any(not math.isfinite(v) or v < 0 for v in original.values()):
        raise ValueError('VALID_SOURCE_SKIN_WEIGHTS_REQUIRED')
    total = sum(original.values())
    if abs(total - 1.0) > 1e-5:
        raise ValueError('NORMALIZED_SOURCE_SKIN_WEIGHTS_REQUIRED')
    if y <= start:
        return {upper_bone: 1.0}
    if y <= pelvis:
        amount = _smooth((y-start)/(pelvis-start))
        result = {upper_bone: 1.0-amount, pelvis_bone: amount}
    elif y < lower:
        amount = _smooth((y-pelvis)/(lower-pelvis))
        result = {bone: weight*amount for bone, weight in original.items()}
        result[pelvis_bone] = result.get(pelvis_bone, 0.0) + 1.0-amount
    else:
        result = dict(original)
    # Dropping the weakest of five influences changes identity at weight ties
    # and creates a discontinuity. Require a representable union instead.
    selected = sorted(((bone, weight) for bone, weight in result.items() if weight > 0),
                      key=lambda row: (-row[1], row[0]))
    if len(selected) > 4:
        raise ValueError('CONTINUOUS_WEIGHT_UNION_EXCEEDS_FOUR_INFLUENCES')
    total = sum(weight for _, weight in selected)
    return {bone: weight/total for bone, weight in selected}
