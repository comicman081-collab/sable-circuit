"""Candidate-only source-preserving alpha derivation with explicit protection.

Protected subject pixels require independent semantic review. This never paints,
inpaints or synthesizes RGB. It restores alpha on the exact selected raw pixels.
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import generation_harness as g
import derive_chroma_runtime_rgba as chroma
import normalize_imagegen_chroma as edge


def derive(source,mask_path,output):
    rgb=np.asarray(Image.open(source).convert('RGB'))
    mask_image=np.asarray(Image.open(mask_path))
    if mask_image.shape!=rgb.shape[:2] or not set(np.unique(mask_image)).issubset({0,255}):
        raise ValueError('NATIVE_BINARY_PROTECTION_MASK_REQUIRED')
    protect=mask_image==255
    if not protect.any():raise ValueError('NONEMPTY_PROTECTION_REQUIRED')
    original_background,_=chroma.background_mask(rgb)
    edge_background,_=edge.edge_connected_background(rgb)
    if np.any(protect & (~original_background | edge_background)):
        raise ValueError('PROTECTION_MUST_ONLY_RESTORE_EXPLICIT_INTERIOR_SUBJECT')
    background=original_background & ~protect
    rgba=np.zeros((*rgb.shape[:2],4),dtype=np.uint8)
    rgba[~background,:3]=rgb[~background];rgba[~background,3]=255
    old=rgba.copy();old[protect]=0
    changed=np.any(old!=rgba,axis=2)
    if not np.array_equal(changed,protect):raise ValueError('UNDECLARED_PIXEL_CHANGE')
    Image.fromarray(rgba).save(output)
    y,x=np.where(protect)
    return {'schema':1,'scope':'CANDIDATE_ALPHA_DERIVATIVE_NEEDS_INDEPENDENT_SUBJECT_REVIEW',
        'generator':g.ref(__file__),'base_generator':g.ref(chroma.__file__),'edge_classifier':g.ref(edge.__file__),
        'source':g.ref(source),'protection_mask':g.ref(mask_path),'output':g.ref(output),
        'native_size':[rgb.shape[1],rgb.shape[0]],'protected_subject_pixels':int(protect.sum()),
        'protected_bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
        'visible_rgb_byte_exact':bool(np.array_equal(rgba[~background,:3],rgb[~background])),
        'outside_protection_byte_exact_to_original_derivative':bool(np.array_equal(old[~protect],rgba[~protect])),
        'border_transparent':bool(np.all(rgba[0,:,3]==0) and np.all(rgba[-1,:,3]==0) and np.all(rgba[:,0,3]==0) and np.all(rgba[:,-1,3]==0)),
        'production_ready':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--mask',required=True);p.add_argument('--output',required=True);p.add_argument('--qa',required=True);a=p.parse_args()
    paths=[g.local(x) for x in (a.source,a.mask,a.output,a.qa)]
    if paths[2].exists() or paths[3].exists():raise ValueError('FRESH_OUTPUT_REQUIRED')
    paths[2].parent.mkdir(parents=True,exist_ok=True)
    g.write(paths[3],derive(*paths[:3]));print('ALPHA_DERIVATIVE_CANDIDATE_CREATED')
