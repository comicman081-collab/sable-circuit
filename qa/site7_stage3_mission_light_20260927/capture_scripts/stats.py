"""Room-view statistics for missions 1-5 and same-plate colour distance between
missions 3-5 before (Codex stage 3 captures) and after the per-mission rows."""
import colorsys, glob, itertools, json, os, sys
import numpy as np
from PIL import Image

AFTER = '.cache/s3mood/cap/'
BEFORE = 'qa/site7_map_kit_v2_20260927_stage3/game/'
M = {'MIS_CH01_03': {'S3_R01': 'R01_BREACH', 'S3_R02': 'R02_DEFENSE', 'S3_R03': 'R03_TRACE', 'S3_R04': 'R04_BULKHEAD', 'S3_R05': 'R05_ANCHOR', 'S3_R06': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'},
     'MIS_CH01_04': {'S3_R06': 'R01_ENTRY', 'S3_R04': 'R02_GATE', 'S3_R01': 'R03_TRACE', 'S3_R02': 'R04_LINE', 'S3_R05': 'R05_WARDEN', 'S3_R03': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'},
     'MIS_CH01_05': {'S3_R01': 'R01_ENTRY', 'S3_R05': 'R02_DEFENSE', 'S3_R03': 'R03_TRACE', 'S3_R04': 'R04_ARRAY', 'S3_R02': 'R05_CARRIER', 'S3_R06': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'}}


def middle(path):
    im = Image.open(path).convert('RGB')
    assert im.size == (1920, 1080), (path, im.size)
    return np.asarray(im, dtype=np.float32)[270:810, 480:1440] / 255.0


def lab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def stats(path):
    a = middle(path)
    lum = float((a @ np.array([0.299, 0.587, 0.114])).mean())
    top, low = a.max(axis=2), a.min(axis=2)
    sat = float(((top - low) / np.maximum(top, 1e-4)).mean())
    h, _, _ = colorsys.rgb_to_hsv(*a.reshape(-1, 3).mean(axis=0))
    return {'luminance': round(lum, 3), 'saturation': round(sat, 3), 'hue_deg': round(h * 360.0), 'lab': [round(float(v), 2) for v in lab(a).reshape(-1, 3).mean(axis=0)]}


result = {'method': 'middle half of each native 1920x1080 room capture (_a view, plate_seam_capture.gd); saturation = mean per-pixel HSV S; hue of the mean colour; lab = mean CIELAB (D65); distance = CIE76 delta E between the same plate\'s mean Lab in two missions', 'missions': {}, 'rooms': {}, 'same_plate': {}}
for n in range(1, 6):
    mission = 'MIS_CH01_0%d' % n
    rooms = {}
    for path in sorted(glob.glob(AFTER + '%s/%s_[RO]*_a.png' % (mission, mission))):
        rooms[os.path.basename(path)[12:-6]] = stats(path)
    result['rooms'][mission] = rooms
    v = list(rooms.values())
    result['missions'][mission] = {k: round(sum(r[k] for r in v) / len(v), 3) for k in ('luminance', 'saturation')}
    result['missions'][mission]['hues_deg'] = sorted(r['hue_deg'] for r in v)
    result['missions'][mission]['lab'] = [round(sum(r['lab'][i] for r in v) / len(v), 2) for i in range(3)]


def de(a, b):
    return float(np.linalg.norm(np.array(a) - np.array(b)))


for when, src in (('before', BEFORE), ('after', AFTER)):
    rows = {}
    for plate in M['MIS_CH01_03']:
        lab_of = {}
        for mission in M:
            path = (src + '%s_%s_a.webp' % (mission, M[mission][plate])) if when == 'before' else (src + '%s/%s_%s_a.png' % (mission, mission, M[mission][plate]))
            lab_of[mission] = stats(path)['lab']
        rows[plate] = {'%s-%s' % (a[-1], b[-1]): round(de(lab_of[a], lab_of[b]), 1) for a, b in itertools.combinations(M, 2)}
    result['same_plate'][when] = rows
    result['same_plate'][when + '_mean'] = {pair: round(sum(r[pair] for r in rows.values()) / len(rows), 1) for pair in ('3-4', '3-5', '4-5')}
out = sys.argv[1] if len(sys.argv) > 1 else '.cache/s3mood/stats.json'
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(result, f, indent=1)
    f.write('\n')
print(json.dumps(result['missions'], indent=1))
print('before', result['same_plate']['before_mean'], 'after', result['same_plate']['after_mean'])
for p in M['MIS_CH01_03']:
    print(p, result['same_plate']['before'][p], result['same_plate']['after'][p])
