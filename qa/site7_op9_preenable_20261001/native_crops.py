"""Native-size review sheets for the 15 operation 9 GAME plates: four 960x540 crops per plate at 1:1 (no scaling), tiled into a
1920x1080 sheet. Rooms: their doors first, then the floor outline's corners. Connector decks: left end, 30 %, 65 % and right end
of the deck line. Reads data/visual/site7_plate_floors.json and site7_battle_art.json; writes PNGs into the folder given.

usage: python native_crops.py <out_dir>   (run from the project root)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else '.cache/claude_scratch/op9_native')
OUT.mkdir(parents=True, exist_ok=True)
MISSION = 'MIS_CH01_09'
floors = json.load(open('data/visual/site7_plate_floors.json', encoding='utf-8'))['plates']
art = json.load(open('data/visual/site7_battle_art.json', encoding='utf-8'))['missions'][MISSION]


def font(size):
    for name in ('C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT = font(22)


def crop_at(image, cx, cy, w=960, h=540):
    x0 = max(0, min(image.width - w, int(round(cx - w / 2))))
    y0 = max(0, min(image.height - h, int(round(cy - h / 2))))
    return image.crop((x0, y0, x0 + w, y0 + h)), (x0, y0)


def sheet(plate_id, image, spots):
    canvas = Image.new('RGB', (1920, 1080), (10, 10, 14))
    draw = ImageDraw.Draw(canvas)
    for index, (label, cx, cy) in enumerate(spots[:4]):
        crop, (x0, y0) = crop_at(image, cx, cy)
        ox, oy = (index % 2) * 960, (index // 2) * 540
        canvas.paste(crop, (ox, oy))
        draw.rectangle((ox + 6, oy + 6, ox + 360, oy + 34), fill=(0, 0, 0))
        draw.text((ox + 10, oy + 8), f'{plate_id} {label} native x{x0} y{y0}', fill=(255, 255, 255), font=FONT)
    canvas.save(OUT / f'{plate_id}_native_4crops.png')


for room in art['rooms']:
    plate_id = room['asset_id'].replace('ENV_S09_', 'S9_')
    image = Image.open(room['asset']).convert('RGB')
    width, height = image.size
    row = floors[room['asset']]
    spots = [(f'door {side}', d[0] * width, d[1] * height) for side, d in row.get('doors', {}).items()]
    pts = [(u * width, v * height) for u, v in row['floor']]
    top, left, right, bottom = min(pts, key=lambda p: p[1]), min(pts), max(pts), max(pts, key=lambda p: p[1])
    spots += [('floor N corner', top[0], top[1] - 60), ('floor W corner', left[0] + 40, left[1]),
              ('floor E corner', right[0] - 40, right[1]), ('floor S corner', bottom[0], bottom[1] - 40)]
    sheet(plate_id, image, spots)

for connector in art['connectors']:
    plate_id = connector['asset_id'].replace('ENV_S09_', 'S9_')
    image = Image.open(connector['asset']).convert('RGB')
    width, height = image.size
    pts = [(u * width, v * height) for u, v in floors[connector['asset']]['floor']]
    xs = [p[0] for p in pts]
    left = [p for p in pts if p[0] <= min(xs) + 1]
    right = [p for p in pts if p[0] >= max(xs) - 1]
    lc = (sum(p[0] for p in left) / len(left) + 120, sum(p[1] for p in left) / len(left))
    rc = (sum(p[0] for p in right) / len(right) - 120, sum(p[1] for p in right) / len(right))
    at = lambda t: (lc[0] + (rc[0] - lc[0]) * t, lc[1] + (rc[1] - lc[1]) * t)
    sheet(plate_id, image, [('left end', *lc), ('30% along', *at(.3)), ('65% along', *at(.65)), ('right end', *rc)])
print('wrote 15 sheets to', OUT)
