"""Luma of the abyss alone and of the void that is actually visible (plate see-through) in the shipped frames."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32) / 255.0

def luma(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

def stats(folder):
    rows = []
    for comp in sorted(Path(folder).glob('*_native_1080p.png')):
        ab = comp.with_name(comp.name.replace('_native_1080p', '_abyss_only'))
        if not ab.exists():
            continue
        c, a = load(comp), load(ab)
        visible = (np.abs(c - a).max(-1) <= 3.0 / 255.0)
        l = luma(c)
        la = luma(a)
        vis_l = l[visible]
        rows.append({
            'view': comp.name.split('_')[1],
            'void_visible_%': round(100.0 * visible.mean(), 1),
            'void_luma_mean': round(float(vis_l.mean()), 4) if vis_l.size else None,
            'void_luma_p5': round(float(np.percentile(vis_l, 5)), 4) if vis_l.size else None,
            'void_luma_p95': round(float(np.percentile(vis_l, 95)), 4) if vis_l.size else None,
            'void_rgb255': [round(float(v) * 255, 1) for v in c[visible].mean(0)] if vis_l.size else None,
            'abyss_luma_mean': round(float(la.mean()), 4),
        })
    return rows

if __name__ == '__main__':
    for folder in sys.argv[1:]:
        rows = stats(folder)
        print(folder)
        for r in rows:
            print('  ', r)
        vals = [r['void_luma_mean'] for r in rows if r['void_luma_mean'] is not None]
        ab = [r['abyss_luma_mean'] for r in rows]
        print('   mean void luma over views: %.4f  mean abyss-only luma: %.4f' % (sum(vals) / len(vals), sum(ab) / len(ab)))
