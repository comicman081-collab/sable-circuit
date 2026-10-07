"""Periodic fitting of supplied motion samples, with explicit source times.

No raster operations and no threshold changes. Fitted curves are new motion,
not a claim that the source GLB already contained an exact loop.
"""
import math
import numpy as np


def basis(phases, harmonics=4):
    phase=np.asarray(phases,dtype=float)
    return np.stack([np.ones_like(phase),*[f(2*math.pi*k*phase)
        for k in range(1,harmonics+1) for f in (np.cos,np.sin)]],axis=-1)


def fit(phases, values, harmonics=4):
    design=basis(phases,harmonics)
    values=np.asarray(values,dtype=float)
    if not np.isfinite(values).all() or len(values)!=len(design):
        raise ValueError('FINITE_MATCHED_MOTION_SAMPLES_REQUIRED')
    coefficients=np.linalg.lstsq(design,values,rcond=None)[0]
    error=design@coefficients-values
    return {'harmonics':harmonics,'coefficients':coefficients.tolist(),
            'rms_fit_error':float(np.sqrt(np.mean(error**2)))}


def evaluate(curve, phase):
    # Evaluating the same periodic function, not copying a receipt endpoint.
    return (basis([float(phase)%1.0],curve['harmonics'])@
            np.asarray(curve['coefficients']))[0].tolist()
