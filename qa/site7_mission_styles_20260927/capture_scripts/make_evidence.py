"""Builds the 1080p lossless WebP evidence for mission styles and route structure.

Usage: make_evidence.py <out_dir>
Reads captures under .cache/structure/cap/<mission>/ (plate_seam_capture.gd),
.cache/structure/overview/ (structure_overview_capture.gd) and the stage 2 Codex
captures (before mood) under .cache/site7_v2_stage2/capture/.
"""
import colorsys
import glob
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(ROOT, '..', '..'))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CAP = os.path.join(ROOT, 'cap')
MISSIONS = ['MIS_CH01_0%d' % i for i in range(1, 6)]
NAMES = {'MIS_CH01_01': 'M1 BLACKOUT', 'MIS_CH01_02': 'M2 RECOVERY SWEEP', 'MIS_CH01_03': 'M3 CORE PRESSURE',
         'MIS_CH01_04': 'M4 FORGE DESCENT', 'MIS_CH01_05': 'M5 OFFSHORE NULL'}


def load(path):
    im = Image.open(path).convert('RGB')
    assert im.size == (1920, 1080), (path, im.size)
    return im


def label(im, text):
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 10 + 7 * len(text), 18), fill=(0, 0, 0))
    draw.text((5, 4), text, fill=(255, 230, 0))
    return im


def save(im, name):
    assert im.size == (1920, 1080)
    im.save(os.path.join(OUT, name), 'WEBP', lossless=True, method=6)
    print('wrote', name)


def room_sheet(folder, name, title):
    files = sorted(glob.glob(os.path.join(folder, 'MIS_CH01_0*.png')))
    rooms = [f for f in files if os.path.basename(f).split('_', 3)[3].startswith(('R', 'O')) and f.endswith('_a.png')]
    conns = [f for f in files if os.path.basename(f).split('_', 3)[3].startswith('C')]
    canvas = Image.new('RGB', (1920, 1080))
    for i, path in enumerate((rooms + conns)[:16]):
        tile = load(path).resize((480, 270), Image.LANCZOS)
        canvas.paste(label(tile, os.path.basename(path)[11:-4]), ((i % 4) * 480, (i // 4) * 270))
    save(label(canvas, title), name)


def floor_stats(path):
    """Mean luminance, saturation and hue of the middle half of the frame."""
    a = np.asarray(load(path), dtype=np.float32)[270:810, 480:1440] / 255.0
    lum = float((a @ np.array([0.299, 0.587, 0.114])).mean())
    mean = a.reshape(-1, 3).mean(axis=0)
    h, s, _ = colorsys.rgb_to_hsv(*mean)
    top, low = a.max(axis=2), a.min(axis=2)
    chroma = float((top - low).mean())
    sat = float(((top - low) / np.maximum(top, 1e-4)).mean())
    return {'luminance': round(lum, 3), 'saturation': round(sat, 3), 'chroma': round(chroma, 3), 'hue_deg': round(h * 360.0)}


# 01/02: mission 2 plates before (Codex stage 2 capture, no mood) and after.
room_sheet(os.path.join(PROJECT, '.cache', 'site7_v2_stage2', 'capture'), '01_m2_plates_before.webp', 'M2 before (no mood)')
room_sheet(os.path.join(CAP, 'MIS_CH01_02'), '02_m2_plates_after.webp', 'M2 after')
save(load(os.path.join(CAP, 'MIS_CH01_02', 'MIS_CH01_02_C1.png')), '03_m2_C1_flood_abyss.webp')

# 04: one row per mission: entry room, first combat room, a connector over the void, boss room.
canvas = Image.new('RGB', (1920, 1080))
stats = {}
for row, mission in enumerate(MISSIONS):
    route = json.load(open(os.path.join(PROJECT, 'data', 'missions', mission + '.json'), encoding='utf-8'))['main_route']
    picks = [route[0]['id'] + '_a', route[1]['id'] + '_a', 'C2', route[4]['id'] + '_a']
    stats[mission] = {}
    for col, stem in enumerate(picks):
        path = os.path.join(CAP, mission, '%s_%s.png' % (mission, stem))
        tile = load(path).crop((0, 135, 1920, 945)).resize((480, 216), Image.LANCZOS)
        canvas.paste(label(tile, '%s  %s' % (NAMES[mission], stem)), (col * 480, row * 216))
    for path in sorted(glob.glob(os.path.join(CAP, mission, '%s_[RO]*_a.png' % mission))):
        stats[mission][os.path.basename(path)[12:-6]] = floor_stats(path)
save(canvas, '04_mission_styles.webp')

# 05-09: each mission's whole map in the game renderer, with its route drawn over it.
for i, mission in enumerate(MISSIONS):
    save(label(load(os.path.join(ROOT, 'overview', mission + '_route.png')), NAMES[mission] + ' route (overlay drawn for review)'),
         '%02d_%s_route.webp' % (5 + i, mission.lower()))
for i, mission in enumerate(MISSIONS):
    save(load(os.path.join(ROOT, 'overview', mission + '_map.png')), '%02d_%s_map.webp' % (10 + i, mission.lower()))

# Per-mission averages of the room views.
summary = {}
for mission, rooms in stats.items():
    values = list(rooms.values())
    summary[mission] = {k: round(sum(v[k] for v in values) / len(values), 3) for k in ('luminance', 'saturation', 'chroma')}
    summary[mission]['hues_deg'] = sorted({v['hue_deg'] for v in values})
json.dump({'rooms': stats, 'missions': summary, 'method': 'middle half of each native 1920x1080 room capture (_a view); saturation = mean per-pixel HSV S ((max-min)/max); chroma = mean (max-min); hue of the mean colour'},
          open(os.path.join(OUT, 'room_view_stats.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps(summary, indent=1))
