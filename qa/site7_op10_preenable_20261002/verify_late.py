"""Independent check of Codex's stage E intake after the R05 decision (operation 10 R05-R06, O01-O02, C01-C0x), 2026-10-01.
Reads only: the stage E manifest (floor outlines, SHA, factors), art_src/environments/site7_v2/stage10, assets/.../stage10,
the quarantine folders, data/visual/*. Writes only .cache/claude_scratch/s10_f/verify_late.json.
usage (from the repository root): python .cache/claude_scratch/s10_f/verify_late.py
"""
import ast
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, 'tools/environment')
import numpy as np
from PIL import Image, ImageDraw
import audit_site7_plate_lighting as A

ART = Path('art_src/environments/site7_v2')
GAME = Path('assets/environments/site7_v2')
MAN = ART / 'SITE7_OP10_STAGE_E_MANIFEST.md'
OUT = Path('.cache/claude_scratch/s10_f/verify_late.json')
ROOM_SIZE = (1672, 941)
CONN_SIZE = (1774, 887)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def srgb_lut(f):
    return np.clip(np.floor(np.arange(256) * f + 0.5), 0, 255).astype(np.uint8)


def poly_area(poly):
    s = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        s += x0 * y1 - x1 * y0
    return abs(s) / 2


def margins(bounds, size):
    x0, y0, x1, y1 = bounds
    w, h = size
    return [x0 / w, y0 / h, (w - x1) / w, (h - y1) / h]


def shrink(poly, k=0.10):
    cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
    return [(cx + (x - cx) * (1 - k), cy + (y - cy) * (1 - k)) for x, y in poly]


def apron_stats(img_rgb, aprons):
    out = {}
    w, h = img_rgb.size
    for door, poly in aprons.items():
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in shrink(poly)], fill=255)
        px = np.asarray(img_rgb, np.float32)[np.asarray(m) > 0] / 255.0
        luma, sat, _ = A.colour_stats(px.mean(0))
        out[door] = {'luma': round(luma, 4), 'saturation': round(sat, 4)}
    return out


def vspan(poly, x):
    ys = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        if (ax <= x <= bx) or (bx <= x <= ax):
            if ax == bx:
                ys += [ay, by]
            else:
                t = (x - ax) / (bx - ax)
                ys.append(ay + t * (by - ay))
    return (min(ys), max(ys)) if ys else None


def conn_ends(im, poly):
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon([tuple(p) for p in poly], fill=255)
    m = np.asarray(mask) > 0
    arr = np.asarray(im, np.float32) / 255.0
    out = {}
    for name, sel in (('L10', slice(0, int(w * 0.10))), ('R10', slice(int(w * 0.90), w)), ('L20', slice(0, int(w * 0.20))), ('R20', slice(int(w * 0.80), w))):
        mm = np.zeros_like(m); mm[:, sel] = m[:, sel]
        px = arr[mm]
        luma, sat, _ = A.colour_stats(px.mean(0))
        out[name] = {'luma': round(luma, 3), 'saturation': round(sat, 3)}
    full = []
    for k in range(1, 20):
        x = k / 20 * w
        s = vspan(poly, x)
        if s and not (s[0] <= 1.5 or s[1] >= h - 1.5):
            full.append(s[1] - s[0])
    return out, full


def parse_manifest():
    text = MAN.read_text(encoding='utf-8').replace('\r\n', '\n')
    parts = re.split(r'(?m)^## ', text)
    rows = {}
    for part in parts:
        head = part.split('\n', 1)[0]
        m = re.match(r'(S10_[A-Z]\d\d) attempt (\d\d) — (SELECTED|REJECTED)', head)
        if not m:
            continue
        pid, attempt, verdict = m.group(1), int(m.group(2)), m.group(3)
        fl = re.search(r'실제 바닥: (\[\[.*?\]\]); 문 (\{.*?\})\n', part)
        if not fl:
            continue
        r = {'plate': pid, 'attempt': attempt, 'verdict': verdict, 'floor': ast.literal_eval(fl.group(1)), 'doors': ast.literal_eval(fl.group(2))}
        t = re.search(r'axis ([\d.]+)°, luma ([\d.]+), p10 ([\d.]+), p90 ([\d.]+), saturation ([\d.]+)', part)
        r['rec'] = dict(zip(('axis', 'luma', 'p10', 'p90', 'saturation'), (float(v) for v in t.groups()))) if t else None
        mm = re.search(r'여백/에이프런 측정: (\{.*\})\n', part)
        r['margin'] = ast.literal_eval(mm.group(1)) if mm else None
        f = re.search(r'계수 ([\d.]+)', part)
        r['factor'] = float(f.group(1)) if f else None
        ns = re.search(r'네이티브: \[(\d+), (\d+)\]', part)
        r['native'] = (int(ns.group(1)), int(ns.group(2))) if ns else None
        for kind in ('RAW', 'MASTER', 'GAME'):
            s = re.search(rf'- {kind} `([^`]+)` SHA-256 `([0-9a-f]{{64}})`', part)
            r[kind.lower()] = (s.group(1), s.group(2)) if s else None
        rows[(pid, attempt)] = r
    return rows


def check(r, spec):
    pid = r['plate']
    row = {'plate': f"{pid}/a{r['attempt']}", 'verdict': r['verdict']}
    raw, mas, game = (Path(r[k][0]) for k in ('raw', 'master', 'game'))
    row['files_exist'] = all(p.exists() for p in (raw, mas, game))
    if not row['files_exist']:
        return row
    row['sha_ok'] = [sha(raw) == r['raw'][1], sha(mas) == r['master'][1], sha(game) == r['game'][1]]
    row['raw_equals_master'] = raw.read_bytes() == mas.read_bytes()
    im = Image.open(game)
    row['mode'] = im.mode
    row['size'] = list(im.size)
    row['size_within_2px'] = all(abs(a - b) <= 2 for a, b in zip(im.size, spec))
    m = np.asarray(Image.open(mas).convert('RGB'))
    g = np.asarray(im.convert('RGB'))
    row['factor'] = r['factor']
    row['lut_max_diff'] = int(np.abs(srgb_lut(r['factor'])[m].astype(int) - g.astype(int)).max())
    row['import_exists'] = Path(str(game) + '.import').exists()
    poly = [list(p) for p in r['floor']]
    w, h = im.size
    plate = SimpleNamespace(asset=str(game).replace('\\', '/'), floor=[(x / w, y / h) for x, y in poly])
    pf = A.plate_floor(plate)
    row['floor'] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in pf.items() if k != 'asset'}
    rec = r['rec']
    row['floor_matches_record'] = bool(rec and abs(pf['axis'] - rec['axis']) < 0.01 and abs(pf['luma'] - rec['luma']) < 0.001 and abs(pf['saturation'] - rec['saturation']) < 0.001)
    row['floor_area_px2'] = round(poly_area([tuple(p) for p in poly]))
    wb = [min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly)]
    row['whole_bounds_wh'] = [wb[2] - wb[0], wb[3] - wb[1]]
    row['whole_margins_pct'] = [round(100 * v, 3) for v in margins(wb, im.size)]
    mg = r['margin']
    if mg and mg.get('apron_polygons_px'):
        aprons = mg['apron_polygons_px']
        drop = {tuple(p) for a in aprons.values() for p in a}
        pts = [p for p in poly if tuple(p) not in drop]
        mb = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
        row['main_margins_pct'] = [round(100 * v, 3) for v in margins(mb, im.size)]
        row['main_matches_record'] = row['main_margins_pct'] == [round(100 * v, 3) for v in mg['main_floor_margins_ltrb_fraction']]
        row['whole_matches_record'] = row['whole_margins_pct'] == [round(100 * v, 3) for v in mg['whole_floor_margins_ltrb_fraction']]
        row['apron_stats_mine'] = apron_stats(im.convert('RGB'), aprons)
        row['main_area_px2'] = round(poly_area(pts))
    else:
        ends, full = conn_ends(im.convert('RGB'), poly)
        row['ends'] = ends
        row['deck_vertical_width'] = [round(min(full), 1), round(max(full), 1)] if full else None
        if full:
            cos = math.cos(math.radians(pf['axis']))
            row['deck_perp_width'] = [round(min(full) * cos, 1), round(max(full) * cos, 1)]
    probs = []
    if not (A.FLOOR_LUMA[0] <= pf['luma'] <= A.FLOOR_LUMA[1]): probs.append('luma')
    if pf['p10'] < A.FLOOR_P10_MIN: probs.append('p10')
    if pf['p90'] > A.FLOOR_P90_MAX: probs.append('p90')
    lo, hi = A.floor_axis_limits(str(game))
    if not (lo <= pf['axis'] <= hi): probs.append('axis')
    if 'apron_stats_mine' in row and any(v['saturation'] > 0.10 for v in row['apron_stats_mine'].values()): probs.append('apron sat > 0.10')
    if 'ends' in row and any(row['ends'][k]['saturation'] > 0.10 for k in ('L10', 'R10')): probs.append('end sat > 0.10')
    row['problems_mine'] = probs
    return row


def main():
    rows = parse_manifest()
    res = []
    for key in sorted(rows):
        r = rows[key]
        pid = r['plate']
        if r['verdict'] == 'REJECTED':
            # rejected candidates live in the quarantine folder; the manifest has their paths
            pass
        spec = CONN_SIZE if '_C' in pid else ROOM_SIZE
        if pid.endswith(('_C06', '_C07')):
            spec = (1254, 1254)
        if not r['raw'] or not r['master'] or not r['game'] or r['factor'] is None:
            continue
        if pid in ('S10_R01', 'S10_R02', 'S10_R03', 'S10_R04'):
            continue
        res.append(check(r, spec))
    # the R05 adoption record (user decision) is a JSON file next to the plate, like R01's adoption.json
    a = json.loads((ART / 'stage10/S10_R05/adoption.json').read_text(encoding='utf-8'))
    r05 = {'plate': 'S10_R05', 'attempt': 3, 'verdict': 'ADOPTED', 'floor': a['actual_floor_px'], 'doors': a['doors_px'],
           'rec': {'axis': a['axis'], 'luma': a['luma'], 'p10': a['p10'], 'p90': a['p90'], 'saturation': a['saturation']},
           'margin': a['margin_acceptance'], 'factor': a['game_exposure_factor_srgb'], 'native': tuple(a['native_size']),
           'raw': (str(ART / 'stage10/S10_R05/S10_R05_RAW_NATIVE.png'), a['raw_sha256']),
           'master': (str(ART / 'stage10/S10_R05/S10_R05_MASTER.png'), a['master_sha256']),
           'game': (str(GAME / 'stage10/S10_R05/S10_R05_GAME.png'), a['game_sha256'])}
    res.insert(0, check(r05, ROOM_SIZE))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
    for r in res:
        print(f"{r['plate']:14s} {r['verdict']:8s} exist {r.get('files_exist')} sha {r.get('sha_ok')} raw=master {r.get('raw_equals_master')} {r.get('mode')} {r.get('size')} ok2px {r.get('size_within_2px')} lut {r.get('lut_max_diff')} import {r.get('import_exists')}")
        if not r.get('files_exist'):
            continue
        f = r['floor']
        print(f"{'':14s} axis {f['axis']:.2f} luma {f['luma']:.3f} p10 {f['p10']:.3f} p90 {f['p90']:.3f} sat {f['saturation']:.3f} rec {r['floor_matches_record']} area {r['floor_area_px2']} whole {r['whole_bounds_wh']} wm% {r['whole_margins_pct']} {f['problems']}")
        if 'main_margins_pct' in r:
            print(f"{'':14s} main m% {r['main_margins_pct']} (rec {r['main_matches_record']}, whole rec {r['whole_matches_record']}) main area {r['main_area_px2']} aprons {r['apron_stats_mine']}")
        else:
            print(f"{'':14s} deck vwidth {r.get('deck_vertical_width')} perp {r.get('deck_perp_width')} ends {r['ends']}")
        print(f"{'':14s} problems(mine) {r['problems_mine']}")


if __name__ == '__main__':
    main()
