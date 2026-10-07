"""Measure native projected-neutral preservation; never grants visual approval."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import generation_harness as g


def audit(report_path, output):
    report = g.read(report_path)
    source_path = g.resolve(report['source_rgba'])
    render_path = g.resolve(report['render'])
    source = np.asarray(Image.open(source_path).convert('RGBA'))
    render = np.asarray(Image.open(render_path).convert('RGBA'))
    height, width = source.shape[:2]
    rh, rw = render.shape[:2]
    if min(rh, rw) < 1920 or height > rh or width > rw:
        raise ValueError('NATIVE_ORIGINAL_SCALE_CAPTURE_REQUIRED')
    x, y = (rw-width)//2, (rh-height)//2
    crop = render[y:y+height,x:x+width]
    visible = source[:,:,3] == 255
    opaque = visible & (crop[:,:,3] == 255)
    sm, rm = source[:,:,3] > 127, crop[:,:,3] > 127
    union = np.logical_or(sm,rm).sum()
    if not union or not opaque.any():
        raise ValueError('VISIBLE_OPAQUE_SOURCE_AND_RENDER_REQUIRED')
    diff = np.abs(source[:,:,:3].astype(np.int16)-crop[:,:,:3].astype(np.int16))
    out = g.local(output)
    out.mkdir(parents=True,exist_ok=False)
    panels = {}
    for label, color in [('LIGHT',(230,232,235,255)),('DARK',(17,24,31,255))]:
        panel = Image.new('RGBA',(max(1920,width*2),max(1920,height)),color)
        panel.alpha_composite(Image.fromarray(source),(0,0))
        panel.alpha_composite(Image.fromarray(crop),(width,0))
        path = out/f'SOURCE_RENDER_{label}_NATIVE.png'
        panel.convert('RGB').save(path)
        panels[label] = g.ref(path)
    result = {'scope':'native preservation measurement only; independent visual review required',
        'report':g.ref(report_path),'source':g.ref(source_path),'render':g.ref(render_path),
        'auditor':g.ref(__file__),'native_render_size':[rw,rh],
        'source_crop_xywh':[x,y,width,height],'source_upsampled':False,
        'silhouette_iou':float(np.logical_and(sm,rm).sum()/union),
        'opaque_source_pixels':int(visible.sum()),'opaque_overlap_pixels':int(opaque.sum()),
        'max_opaque_rgb_difference':int(diff[opaque].max()),
        'mean_visible_rgb_difference':float(diff[visible].mean()),
        'original_scale_panels':panels,'production_ready':False}
    g.write(out/'AUDIT.json',result)
    print('NATIVE_PRESERVATION_MEASURED',result['silhouette_iou'],result['max_opaque_rgb_difference'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',required=True)
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    audit(args.report,args.out)
