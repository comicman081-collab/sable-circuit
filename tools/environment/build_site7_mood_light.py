"""Find the lamps painted on the SITE-7 background plates, for the runtime mood light.

The v2 plates are painted under one neutral light so their seams match; a room's
mood (its colour, its darkness, pools of light under its lamps) is added at
runtime instead (site7_room_art_layer.gd, data/visual/site7_mood.json). A pool
belongs under each lamp the plate already shows, in that lamp's colour, so this
tool reads them from the pixels:

- a lamp is a blob of pixels at least LAMP_CORE of the plate's white (its
  brightest channel values; a GAME plate is exposure-scaled, so its white is
  below 1) off the walkable floor (site7_plate_floors.json), inside a coloured
  glow: the pixels around it (LAMP_HALO px) have a brightness-weighted
  saturation of at least LAMP_GLOW_SAT. A white highlight on bare metal has no
  such glow. Blobs under LAMP_MIN_AREA px are specks;
- its colour is the brightness-weighted mean of that glow, scaled so the
  strongest channel is 1;
- its pool sits on the floor below it: straight down the image (walls stand
  vertically in the dimetric view) to the first floor at least FLOOR_INSET px
  inside the floor's edge, then POOL_DROP px further. A lamp on a front railing
  has no floor below it, so its pool is found above it instead;
- pools closer than LAMP_MERGE px (floor metric: vertical distance doubled) merge,
  brightness-weighted; a plate keeps its LAMP_MAX strongest, weighted 0-1
  relative to the strongest.

Only plates with a "lamps" row in site7_mood.json are read. Writes
data/visual/site7_mood_lamps.json: per plate, [u, v, r, g, b, weight] rows in
texture coordinates.

The v2 plates are painted on a flat near-black void outside their architecture.
In the game that void is see-through, so the abyss behind the level
(site7_abyss_backdrop.gd) shows instead of a black card. Every plate in
site7_mood.json (unless "void": false) gets a void mask: the pixels no brighter
than VOID_MAX (8-bit, brightest channel) that connect to the image border, so a
dark gap inside the architecture stays opaque; never the walkable floor. The
mask is softened by VOID_SOFT px and stored at VOID_SCALE of the plate size as
a greyscale PNG (255 = void) in data/visual/site7_void_masks.json. A mission's
abyss.contact_shadow_px optionally derives a soft distance field around the
same silhouette, in site7_contact_shadows.json. It shades the abyss only and
does not change the void threshold, plate alpha, floor or wall pixels.

A near-black wall can reach the border through a narrow dark gap, so the dark
recesses between its pipes and pillars count as void and, with a lit abyss
behind, show it through the wall as blue-grey patches (operation 10, 2026-10-02).
A mission's abyss.void_fill_px (operation 10: 28) keeps void narrower than twice
that opaque, so only the wide outer void is see-through; those pixels are no
brighter than VOID_MAX, so it only makes the wall render as painted. Missions
without the row keep the plain rule.

`--check` fails if either file is stale; `--preview DIR` draws each plate's
lamps and pools, with its void tinted, for review.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOOD = ROOT / 'data/visual/site7_mood.json'
PLATE_FLOORS = ROOT / 'data/visual/site7_plate_floors.json'
OUT = ROOT / 'data/visual/site7_mood_lamps.json'
VOID_OUT = ROOT / 'data/visual/site7_void_masks.json'
CONTACT_OUT = ROOT / 'data/visual/site7_contact_shadows.json'
CONTACT_SCALE = 0.25

LAMP_CORE = 0.7
LAMP_GLOW_SAT = 0.25
LAMP_MIN_AREA = 12
LAMP_HALO = 8
FLOOR_INSET = 24.0
POOL_DROP = 30.0
LAMP_MERGE = 160.0
LAMP_MAX = 6
VOID_MAX = 12
VOID_SOFT = 1.2
VOID_SCALE = 0.5
# --check: another numpy/scipy build may round a mean differently.
TOLERANCE = 0.002


def floor_mask(size, floor):
    from PIL import Image, ImageDraw
    import numpy as np
    w, h = size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon([(x * w, y * h) for x, y in floor], fill=255)
    return np.asarray(mask) > 0


def pool_under(x: int, y: float, inner, h: int):
    """Floor point below (or, failing that, above) image point (x, y)."""
    column = inner[:, x]
    below = [row for row in range(int(y), h) if column[row]]
    if below:
        foot = below[0] + POOL_DROP
        return foot if foot < h and column[int(foot)] else float(below[0])
    above = [row for row in range(int(y), -1, -1) if column[row]]
    if above:
        foot = above[0] - POOL_DROP
        return foot if foot >= 0 and column[int(foot)] else float(above[0])
    return None


def detect(asset: str, floor) -> list:
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    rgb = np.asarray(Image.open(ROOT / asset).convert('RGB'), np.float32) / 255.0
    h, w = rgb.shape[:2]
    peak, low = rgb.max(-1), rgb.min(-1)
    saturation = (peak - low) / np.maximum(peak, 1e-4)
    walkable = floor_mask((w, h), floor)
    inner = ndimage.distance_transform_edt(walkable) >= FLOOR_INSET
    white = float(np.percentile(peak, 99.95))
    labels, count = ndimage.label((peak >= LAMP_CORE * white) & ~walkable, structure=np.ones((3, 3)))
    lamps = []
    for index, box in enumerate(ndimage.find_objects(labels), start=1):
        blob = labels[box] == index
        if blob.sum() < LAMP_MIN_AREA:
            continue
        rows, cols = np.nonzero(blob)
        cy, cx = rows.mean() + box[0].start, cols.mean() + box[1].start
        y0, y1 = max(0, box[0].start - LAMP_HALO), min(h, box[0].stop + LAMP_HALO)
        x0, x1 = max(0, box[1].start - LAMP_HALO), min(w, box[1].stop + LAMP_HALO)
        glow = (labels[y0:y1, x0:x1] != index) * peak[y0:y1, x0:x1]
        if (saturation[y0:y1, x0:x1] * glow).sum() < LAMP_GLOW_SAT * max(1e-4, glow.sum()):
            continue
        tinted = glow * (saturation[y0:y1, x0:x1] >= 0.5 * LAMP_GLOW_SAT)
        colour = (rgb[y0:y1, x0:x1] * tinted[..., None]).sum((0, 1)) / max(1e-4, tinted.sum())
        foot = pool_under(int(round(cx)), cy, inner, h)
        if foot is None:
            continue
        lamps.append({'x': cx, 'y': foot, 'colour': colour / max(1e-4, colour.max()), 'weight': float(peak[box][blob].sum() / white)})
    lamps.sort(key=lambda lamp: -lamp['weight'])
    pools = []
    for lamp in lamps:
        for pool in pools:
            if math.hypot(lamp['x'] - pool['x'], 2.0 * (lamp['y'] - pool['y'])) < LAMP_MERGE:
                total = pool['weight'] + lamp['weight']
                for key in ('x', 'y'):
                    pool[key] = (pool[key] * pool['weight'] + lamp[key] * lamp['weight']) / total
                pool['colour'] = (pool['colour'] * pool['weight'] + lamp['colour'] * lamp['weight']) / total
                pool['weight'] = total
                break
        else:
            pools.append(dict(lamp))
    pools = sorted(pools, key=lambda pool: -pool['weight'])[:LAMP_MAX]
    strongest = max((pool['weight'] for pool in pools), default=1.0)
    return [[round(pool['x'] / w, 4), round(pool['y'] / h, 4)] + [round(float(c), 3) for c in pool['colour'] / max(1e-4, pool['colour'].max())]
            + [round(pool['weight'] / strongest, 3)] for pool in pools]


def outer_void(void, radius: float):
    """The part of the boolean `void` that reaches the image border through passages
    wider than twice `radius` px: an opening by a disk of that radius drops narrow
    gaps and pockets, and a recess that only its narrow neck joined to the outside
    is no longer connected to it. Euclidean erosion and dilation through distance
    transforms, so a full plate is fast; the image border counts as void."""
    import numpy as np
    from scipy import ndimage
    if radius <= 0.0:
        return void
    pad = math.ceil(radius) + 2
    padded = np.pad(void, pad, constant_values=True)
    core = ndimage.distance_transform_edt(padded) > radius
    opened = (ndimage.distance_transform_edt(~core) <= radius) & padded
    labels, _ = ndimage.label(opened)
    ring = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    return np.isin(labels, ring[ring > 0])[pad:-pad, pad:-pad]


def void_mask(asset: str, floor, fill: float = 0.0):
    """Greyscale mask (VOID_SCALE of the plate size, 255 = void) of the plate's
    flat outer void; `fill` (px, an abyss row's void_fill_px) leaves void narrower
    than twice that opaque."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    rgb = np.asarray(Image.open(ROOT / asset).convert('RGB'))
    h, w = rgb.shape[:2]
    labels, _ = ndimage.label(rgb.max(-1) <= VOID_MAX)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    void = np.isin(labels, border[border > 0]) & ~floor_mask((w, h), floor)
    void = outer_void(void, fill)
    soft = ndimage.gaussian_filter(void.astype(np.float32), VOID_SOFT)
    image = Image.fromarray(np.round(soft * 255.0).clip(0, 255).astype(np.uint8), 'L')
    return image.resize((max(1, round(w * VOID_SCALE)), max(1, round(h * VOID_SCALE))), Image.BOX)


def contact_shadow(mask, size, width: float) -> dict:
    """Distance field for the backdrop, never a replacement plate alpha mask.
    Three widths of padding bring the Gaussian to zero at the atlas boundary.
    Native plate pixels set the distance; the smooth field stores at quarter size.
    """
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    padding = math.ceil(3.0 * width)
    outside = np.asarray(mask.resize(size, Image.NEAREST)) >= 128
    outside = np.pad(outside, padding, constant_values=True)
    distance = ndimage.distance_transform_edt(outside)
    shade = np.exp(-np.square(distance / width))
    image = Image.fromarray(np.round(shade * 255.0).astype(np.uint8), 'L')
    image = image.resize((round(image.width * CONTACT_SCALE), round(image.height * CONTACT_SCALE)), Image.BOX)
    return {'padding_px': padding, 'scale': CONTACT_SCALE, 'mask': encode_png(image)}


def encode_png(image) -> str:
    import base64
    import io
    buffer = io.BytesIO()
    image.save(buffer, 'PNG', optimize=True)
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def same_masks(stored: dict, fresh: dict) -> bool:
    """Decoded masks equal to within one step per pixel (the blur may round the
    other way on another build); the PNG bytes may differ between zlib builds."""
    import base64
    import io
    import numpy as np
    from PIL import Image
    if set(stored.get('plates', {})) != set(fresh['plates']):
        return False
    for asset, encoded in fresh['plates'].items():
        a = np.asarray(Image.open(io.BytesIO(base64.b64decode(stored['plates'][asset]))), np.int16)
        b = np.asarray(Image.open(io.BytesIO(base64.b64decode(encoded))), np.int16)
        if a.shape != b.shape or np.abs(a - b).max(initial=0) > 1:
            return False
    return {k: v for k, v in stored.items() if k != 'plates'} == {k: v for k, v in fresh.items() if k != 'plates'}


def same_contacts(stored: dict, fresh: dict) -> bool:
    """Decoded contact fields equal to within one step per pixel (the distance
    transform and the box resize may round the other way on another build); the
    PNG bytes may differ between zlib builds, so they are never compared."""
    import base64
    import io
    import numpy as np
    from PIL import Image
    if set(stored.get('plates', {})) != set(fresh['plates']):
        return False
    for asset, row in fresh['plates'].items():
        old = stored['plates'][asset]
        if {k: v for k, v in old.items() if k != 'mask'} != {k: v for k, v in row.items() if k != 'mask'}:
            return False
        a = np.asarray(Image.open(io.BytesIO(base64.b64decode(old['mask']))), np.int16)
        b = np.asarray(Image.open(io.BytesIO(base64.b64decode(row['mask']))), np.int16)
        if a.shape != b.shape or np.abs(a - b).max(initial=0) > 1:
            return False
    return {k: v for k, v in stored.items() if k != 'plates'} == {k: v for k, v in fresh.items() if k != 'plates'}


def same_lamps(stored: dict, fresh: dict) -> bool:
    if set(stored.get('plates', {})) != set(fresh['plates']):
        return False
    for asset, rows in fresh['plates'].items():
        old = stored['plates'][asset]
        if len(old) != len(rows):
            return False
        for a, b in zip(old, rows):
            if len(a) != len(b) or max(abs(p - q) for p, q in zip(a[:2], b[:2])) > TOLERANCE \
                    or max(abs(p - q) for p, q in zip(a[2:], b[2:])) > 5 * TOLERANCE:
                return False
    return {k: v for k, v in stored.items() if k != 'plates'} == {k: v for k, v in fresh.items() if k != 'plates'}


def preview(asset: str, rows: list, settings: dict, mask, out_dir: Path) -> None:
    from PIL import Image, ImageDraw
    image = Image.open(ROOT / asset).convert('RGB')
    w, h = image.size
    if mask is not None:
        image = Image.composite(Image.new('RGB', (w, h), (60, 0, 90)), image, mask.resize((w, h), Image.BILINEAR))
    draw = ImageDraw.Draw(image)
    radius = float(settings.get('radius', 200.0))
    for u, v, r, g, b, weight in rows:
        x, y = u * w, v * h
        colour = (int(r * 255), int(g * 255), int(b * 255))
        draw.ellipse((x - radius, y - radius / 2, x + radius, y + radius / 2), outline=colour, width=3)
        draw.text((x + 6, y - 14), f'{weight:.2f}', fill=(255, 255, 255))
    out_dir.mkdir(parents=True, exist_ok=True)
    image.save(out_dir / (Path(asset).stem + '_lamps.png'))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='fail if lamps, void masks or contact-shadow fields differ from a fresh build')
    parser.add_argument('--preview', type=Path, help='draw each plate with its lamps and pools into this folder')
    args = parser.parse_args()
    mood = json.loads(MOOD.read_text(encoding='utf-8'))
    floors = json.loads(PLATE_FLOORS.read_text(encoding='utf-8'))['plates']
    result = {
        'schema': 1,
        'source': 'tools/environment/build_site7_mood_light.py',
        'encoding': 'per plate: [u, v, r, g, b, weight] pools in texture coordinates; colour scaled to a strongest channel of 1; weight relative to the plate\'s strongest lamp',
        'plates': {},
    }
    masks = {
        'schema': 1,
        'source': 'tools/environment/build_site7_mood_light.py',
        'scale': VOID_SCALE,
        'encoding': 'per plate: base64 of a greyscale PNG over its texture, 255 where the flat outer void is see-through',
        'plates': {},
    }
    contacts = {'schema': 1, 'source': 'tools/environment/build_site7_mood_light.py',
                'encoding': 'per plate: padded quarter-size Gaussian distance field from its unchanged void mask; backdrop only', 'plates': {}}
    problems = []
    # A mission may relight a shared plate ("plates" in its row); it can only
    # tune plates listed here, whose lamps and void this tool finds.
    lamp_plates = {asset for asset, settings in mood['plates'].items() if 'lamps' in settings}
    contact_by_asset = {}
    fill_by_asset = {}
    for mission, row in sorted(mood.get('missions', {}).items()):
        abyss = row.get('abyss', {})
        width = float(abyss.get('contact_shadow_px', 0.0))
        fill = float(abyss.get('void_fill_px', 0.0))
        contact = abyss.get('style') == 'dawn' and width > 0.0
        if contact or fill > 0.0:
            art = json.loads((ROOT / 'data/visual/site7_battle_art.json').read_text(encoding='utf-8'))['missions'][mission]
            for plate in art['rooms'] + art['connectors']:
                if contact:
                    contact_by_asset[plate['asset']] = width
                if fill > 0.0:
                    fill_by_asset[plate['asset']] = fill
        for asset, settings in sorted(row.get('plates', {}).items()):
            if asset not in mood['plates']:
                problems.append(f'{mission}: {asset} is not in the shared plate list')
            elif 'lamps' in settings:
                lamp_plates.add(asset)
    for asset, settings in sorted(mood['plates'].items()):
        if asset not in floors:
            problems.append(f'{asset}: no floor in site7_plate_floors.json')
            continue
        mask = void_mask(asset, floors[asset]['floor'], fill_by_asset.get(asset, 0.0)) if settings.get('void', True) else None
        if mask is not None:
            masks['plates'][asset] = encode_png(mask)
            if asset in contact_by_asset:
                from PIL import Image
                with Image.open(ROOT / asset) as source:
                    contacts['plates'][asset] = contact_shadow(mask, source.size, contact_by_asset[asset])
        if asset in lamp_plates:
            result['plates'][asset] = detect(asset, floors[asset]['floor'])
        if args.preview:
            preview(asset, result['plates'].get(asset, []), settings.get('lamps', {}), mask, args.preview)
    for path, data, same in ((OUT, result, same_lamps), (VOID_OUT, masks, same_masks),
                             (CONTACT_OUT, contacts, same_contacts)):
        if args.check:
            stored = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
            if not same(stored, data):
                raise SystemExit(f'{path.name} is stale; rerun build_site7_mood_light.py')
        elif not args.preview:
            path.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')
    for problem in problems:
        print('MOOD_PROBLEM', problem)
    print('SITE7_MOOD_LIGHT', 'FAIL' if problems else 'PASS', len(result['plates']), 'plates',
          sum(len(rows) for rows in result['plates'].values()), 'pools', len(masks['plates']), 'void masks', len(contacts['plates']), 'contact shadows')
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
