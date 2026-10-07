"""Reference-only crop to keep a rejected leg pose out of an art repair input.

No generated or runtime pixels are authored here. Original pixels are copied
at native density and provenance is recorded; all new visible art is ImageGen.
"""
from pathlib import Path
import hashlib
import json
import argparse
from PIL import Image

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--source', default='art/rook/E_walk_1_master.png')
parser.add_argument('--box', type=int, nargs=4, default=[0, 0, 741, 432])
parser.add_argument('--name', default='E_upper_appearance_reference')
args = parser.parse_args()
source = root / args.source
out = Path(__file__).resolve().parent
box = tuple(args.box)
with Image.open(source) as im:
    crop = im.crop(box)
    # Neutral opaque matte avoids a checkerboard-looking reference.
    bg = Image.new('RGB', crop.size, '#203039')
    bg.paste(crop, (0, 0), crop.getchannel('A') if crop.mode == 'RGBA' else None)
    bg.save(out / (args.name + '.png'))
(out / (args.name + '.json')).write_text(json.dumps({
    'role': 'appearance-only cropped reference; not visible runtime art',
    'source': str(source.relative_to(root)),
    'sourceSHA256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'crop': box, 'resampled': False,
    'outputSHA256': hashlib.sha256((out / (args.name + '.png')).read_bytes()).hexdigest()
}, indent=2), encoding='utf-8')
