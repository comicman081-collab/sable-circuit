"""Builds the 1080p lossless WebP evidence for the per-mission stage 3 plate rows.
Usage: make_evidence.py <out_dir>. Reads .cache/s3mood/cap/<mission>/ (plate_seam_capture.gd,
after) and qa/site7_map_kit_v2_20260927_stage3/game/ (Codex stage 3 captures, before)."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

OUT = sys.argv[1]
CAP = '.cache/s3mood/cap/'
BEFORE = 'qa/site7_map_kit_v2_20260927_stage3/game/'
M = {'MIS_CH01_03': {'S3_R01': 'R01_BREACH', 'S3_R02': 'R02_DEFENSE', 'S3_R03': 'R03_TRACE', 'S3_R04': 'R04_BULKHEAD', 'S3_R05': 'R05_ANCHOR', 'S3_R06': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'},
     'MIS_CH01_04': {'S3_R06': 'R01_ENTRY', 'S3_R04': 'R02_GATE', 'S3_R01': 'R03_TRACE', 'S3_R02': 'R04_LINE', 'S3_R05': 'R05_WARDEN', 'S3_R03': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'},
     'MIS_CH01_05': {'S3_R01': 'R01_ENTRY', 'S3_R05': 'R02_DEFENSE', 'S3_R03': 'R03_TRACE', 'S3_R04': 'R04_ARRAY', 'S3_R02': 'R05_CARRIER', 'S3_R06': 'R06_ESCAPE', 'S3_O01': 'O01_SUPPLY', 'S3_O02': 'O02_RESEARCH'}}
PLATES = list(M['MIS_CH01_03'])
NAMES = {'MIS_CH01_01': 'M1 BLACKOUT', 'MIS_CH01_02': 'M2 RECOVERY SWEEP', 'MIS_CH01_03': 'M3 CORE PRESSURE', 'MIS_CH01_04': 'M4 FORGE DESCENT', 'MIS_CH01_05': 'M5 OFFSHORE NULL'}


def load(path):
    im = Image.open(path).convert('RGB')
    assert im.size == (1920, 1080), (path, im.size)
    return im


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10 + 7 * len(text), 18), fill=(0, 0, 0))
    d.text((5, 4), text, fill=(255, 230, 0))
    return im


def save(im, name):
    assert im.size == (1920, 1080)
    im.save(os.path.join(OUT, name), 'WEBP', lossless=True, method=6)
    print('wrote', name)


def same_plates(when, part):
    c = Image.new('RGB', (1920, 1080))
    for r, plate in enumerate(PLATES[part * 4:part * 4 + 4]):
        for col, mission in enumerate(M):
            room = M[mission][plate]
            path = BEFORE + '%s_%s_a.webp' % (mission, room) if when == 'before' else CAP + '%s/%s_%s_a.png' % (mission, mission, room)
            c.paste(label(load(path).resize((640, 270), Image.LANCZOS), '%s  %s %s (%s)' % (plate, NAMES[mission][:2], room, when)), (col * 640, r * 270))
    return label(c, '')


save(same_plates('before', 0), '01_before_same_plates_R01-R04.webp')
save(same_plates('before', 1), '02_before_same_plates_R05-O02.webp')
save(same_plates('after', 0), '03_after_same_plates_R01-R04.webp')
save(same_plates('after', 1), '04_after_same_plates_R05-O02.webp')

# 05: one row per mission: entry, first combat room, connector 2, boss room.
c = Image.new('RGB', (1920, 1080))
for row, mission in enumerate(NAMES):
    route = json.load(open('data/missions/%s.json' % mission, encoding='utf-8'))['main_route']
    for col, stem in enumerate([route[0]['id'] + '_a', route[1]['id'] + '_a', 'C2', route[4]['id'] + '_a']):
        tile = load(CAP + '%s/%s_%s.png' % (mission, mission, stem)).crop((0, 135, 1920, 945)).resize((480, 216), Image.LANCZOS)
        c.paste(label(tile, '%s  %s' % (NAMES[mission], stem)), (col * 480, row * 216))
save(c, '05_mission_styles.webp')

# 06-11: original-scale captures of two shared plates in each of missions 3-5.
n = 6
for plate in ('S3_R01', 'S3_R05'):
    for mission in M:
        room = M[mission][plate]
        save(label(load(CAP + '%s/%s_%s_a.png' % (mission, mission, room)), '%s %s on %s' % (NAMES[mission], room, plate)), '%02d_%s_%s_%s.webp' % (n, mission.lower(), room, plate))
        n += 1
