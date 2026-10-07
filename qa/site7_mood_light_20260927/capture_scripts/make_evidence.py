"""Builds the 1080p lossless WebP evidence of the SITE-7 mood light into an output folder."""
import glob
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
STAGE1 = sys.argv[2]  # the stage 1 QA game captures (before)
os.makedirs(OUT, exist_ok=True)
NAMES = ['R01_ENTRY_a', 'R02_CORRIDOR_a', 'R03_ARCHIVE_a', 'R04_CONTAINMENT_a', 'R05_CORE_a', 'R06_EXTRACTION_a',
         'O01_SUPPLY_a', 'O02_RESEARCH_a', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'R04_CONTAINMENT_b']


def find(folder, stem):
    hits = glob.glob(os.path.join(folder, stem + '.*'))
    assert hits, (folder, stem)
    return hits[0]


def tile(path, size, label):
    im = Image.open(path).convert('RGB')
    assert im.size == (1920, 1080), (path, im.size)
    im = im.resize(size, Image.LANCZOS)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 8 + 7 * len(label), 16), fill=(0, 0, 0))
    draw.text((4, 3), label, fill=(255, 230, 0))
    return im


def save(im, name):
    assert im.size == (1920, 1080)
    im.save(os.path.join(OUT, name), 'WEBP', lossless=True, method=6)
    print('wrote', name)


def sheet(folder, prefix, name):
    canvas = Image.new('RGB', (1920, 1080))
    for i, stem in enumerate(NAMES):
        canvas.paste(tile(find(folder, prefix + stem), (480, 270), stem), ((i % 4) * 480, (i // 4) * 270))
    save(canvas, name)


def copy(path, name):
    im = Image.open(path).convert('RGB')
    save(im, name)


sheet(STAGE1, 'MIS_CH01_01_', '01_m1_plates_before.webp')
sheet(os.path.join(ROOT, 'final_m01'), 'MIS_CH01_01_', '02_m1_plates_after.webp')
for step, room in ((1, 'R02'), (3, 'R04'), (4, 'R05')):
    copy(os.path.join(ROOT, 'final_actors', f'step{step}_flat.png'), f'03_m1_actors_{room}_mood_off.webp')
    copy(os.path.join(ROOT, 'final_actors', f'step{step}_mood.png'), f'03_m1_actors_{room}_mood_on.webp')
copy(find(STAGE1, 'MIS_CH01_01_C4'), '05_m1_C4_void_before.webp')
copy(os.path.join(ROOT, 'final_m01', 'MIS_CH01_01_C4.png'), '06_m1_C4_abyss_after.webp')
copy(os.path.join(ROOT, 'final_m01', 'MIS_CH01_01_C2.png'), '07_m1_C2_cyan_to_red_after.webp')
# Missions 3-5 share the v1 stage 3 plates: before (no mood) against each mission's grade.
canvas = Image.new('RGB', (1920, 1080))
columns = [('m03_before', 'no mood (M3-5 before)'), ('final_m03', 'M3 CORE PRESSURE'), ('final_m04', 'M4 FORGE DESCENT'), ('final_m05', 'M5 OFFSHORE NULL')]
for col, (folder, label) in enumerate(columns):
    for row, pattern in enumerate(['MIS_CH01_0*_R01_*_a', 'MIS_CH01_0*_R05_*_a', 'MIS_CH01_0*_C2', 'MIS_CH01_0*_C5']):
        path = sorted(glob.glob(os.path.join(ROOT, folder, pattern + '.png')))[0]
        canvas.paste(tile(path, (480, 270), label + ' ' + os.path.basename(path)[11:-4]), (col * 480, row * 270))
save(canvas, '08_m345_mission_grades.webp')
copy(os.path.join(ROOT, 'final_m04', 'MIS_CH01_04_C2.png'), '09_m4_C2_gap_after.webp')
