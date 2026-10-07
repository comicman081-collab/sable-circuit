"""Native-scale evidence for a source-surface neutral probe, not visual approval."""
import argparse
from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def evaluate(folder):
    folder=g.local(folder)
    source=g.pixels(folder/'SOURCE_RGBA.png')
    render=g.pixels(folder/'NEUTRAL_SOURCE_PRESERVATION_1920.png')
    h,w=source.shape[:2]; rh,rw=render.shape[:2]
    y=(rh-h)//2; x=(rw-w)//2
    crop=render[y:y+h,x:x+w]
    original=np.zeros_like(render);original[y:y+h,x:x+w]=source
    visible=source[:,:,3]==255
    opaque=visible & (crop[:,:,3]==255)
    difference=np.abs(crop[:,:,:3].astype(np.int16)-source[:,:,:3].astype(np.int16))
    source_mask=source[:,:,3]>127; rendered_mask=crop[:,:,3]>127
    intersection=np.logical_and(source_mask,rendered_mask).sum()
    union=np.logical_or(source_mask,rendered_mask).sum()
    for label,color in [('LIGHT',(230,232,235)),('DARK',(17,24,31))]:
        background=Image.new('RGBA',(rw,rh),(*color,255))
        background.alpha_composite(Image.fromarray(render))
        background.convert('RGB').save(folder/f'NEUTRAL_{label}_1920.png')
    comparison=Image.new('RGBA',(w*2,1920),(27,33,39,255))
    comparison.alpha_composite(Image.fromarray(source),(0,(1920-h)//2))
    comparison.alpha_composite(Image.fromarray(crop),(w,(1920-h)//2))
    comparison.convert('RGB').save(folder/'SOURCE_VS_RENDER_ORIGINAL_SCALE_2048x1920.png')
    g.write(folder/'NEUTRAL_COMPARISON.json',{'scope':'neutral_pixel_and_container_measurement_only',
        'source':g.ref(folder/'SOURCE_RGBA.png'),'render':g.ref(folder/'NEUTRAL_SOURCE_PRESERVATION_1920.png'),
        'evaluator':g.ref(__file__),'native_render_size':[rw,rh],'source_upsampled':False,
        'source_crop_xywh':[x,y,w,h],'silhouette_iou':float(intersection/union),
        'opaque_source_pixels':int(visible.sum()),'fully_opaque_overlap_pixels':int(opaque.sum()),
        'mean_rgb_difference_code_values':float(difference[visible].mean()),
        'max_opaque_rgb_difference_code_values':int(difference[opaque].max()),
        'production_ready':False,'motion_visual_review':'NOT_PERFORMED'})
    print('NATIVE_NEUTRAL_COMPARISON_CREATED')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--folder',required=True)
    evaluate(parser.parse_args().folder)
