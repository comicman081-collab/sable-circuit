"""Solve where each SITE-7 room and connector plate sits in its mission's world.

Main-route decks climb up and to the right. A mission walks them that way unless
its connectors are marked "reverse" (site7_battle_art.json): then each deck meets
the room before it at its upper-right end, so the route descends down and to the
left. Each optional room hangs from the main room its "from" names (by default
the room two ahead of it). Authored v2 descending decks leave their parent room
down and to the right without mirroring. Only legacy v1 branch art is mirrored
during the partial conversion. No plate is ever rotated. Authored doorway
centres own the joins; legacy rooms retain the lit-floor fit.

Each connector is pushed into both rooms until its deck end, and the part of the
deck its seam fade makes translucent, lie inside the room's painted floor. Walking
from a room onto the deck then never leaves painted floor, and the runtime needs
no route capsules across painted walls. Only the lit part of a room's floor counts:
the plates darken toward their borders, so a deck end that met the floor there
faded out over a near-black band.

Each plate was painted with its own lighting, so a deck is often brighter, darker
or more or less saturated than the room floor it runs into. Every connector
therefore gets a light map (site7_seam_light.json): a coarse grid over its texture
of brightness gains and saturation factors. Where the deck lies on a room's floor
they bring the connector's locally averaged colour to the room's brightness and
saturation there. Hue is never shifted: pulling an orange deck toward a cyan room
channel by channel passed through green, so against an opposite hue the deck is
desaturated instead. Away from the seams the map blends those cells by distance,
room by room, and eases back to nothing LIGHT_REACH px out, so a long deck keeps
its own painted colour in the middle. Walls and lamps beside the deck keep their
saturation and are only ever darkened, and pixels past LIGHT_KNEE are neither
brightened nor resaturated, so lamps and glows keep their look. The runtime
applies it in the plate shader (site7_room_art_layer.gd). Averaging first keeps a
highlight or a shadow on the deck from being pushed further. Source pixels are
never changed.

Writes data/visual/site7_world_layout.json and site7_seam_light.json. `--preview
DIR` also renders the composite (runtime draw order, seam fade, floor masks and
light maps) with the floors drawn on top, for review only.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'data/visual/site7_battle_art.json'
LAYOUTS = ROOT / 'data/visual/site7_battle_layouts.json'
PLATE_FLOORS = ROOT / 'data/visual/site7_plate_floors.json'
MISSIONS = ROOT / 'data/missions'
OUT = ROOT / 'data/visual/site7_world_layout.json'

ENTRY_CENTER = (1680.0, 470.0)
# The runtime insets every floor by 20 px (ACTOR_EDGE_CLEARANCE). The middle of a
# deck end sits this far inside the raw room floor; its corners may miss the floor
# by END_SLACK, which narrow corridor rooms need (their painted axis is steeper
# than the connector's) and which leaves only a sliver of faded deck outside it.
END_MARGIN = 60.0
END_SLACK = 40.0
BAND_INSIDE = 0.9
EXTRA_OVERLAP = 20.0
# Seam fade: the runtime connector shader fades the outer 12% of each end.
FADE_BAND = 0.10
SEAM_FADE = 0.12
DECK_SAMPLE_INSET = 20.0
SAMPLE_STEP = 12.0
# The plates' vignette darkens the outer ~10-15 % of each side. The runtime floor
# masks (site7_room_art_layer.gd MASK_EDGE_FADE) fade out over the same band.
LIT_INSET = 0.15
# Connector top/bottom borders fade over this fraction of their height except on
# their own deck (site7_room_art_layer.gd CAP_FADE), feathered 20 px into the deck.
CAP_FADE = 0.1
CAP_FEATHER = 20.0
# Room plates fade out over this fraction of every side (ROOM_EDGE_FADE).
ROOM_EDGE_FADE = 0.05
# Seam light maps: LIGHT_GRID cells (about 21 world px) over each connector
# texture, colours averaged over about LIGHT_BLUR world px; gain and saturation
# stored as log2 in [-LIGHT_LOG_RANGE, LIGHT_LOG_RANGE] mapped to a byte each. A
# room needs at least LIGHT_MIN_CELLS cells of deck on its floor; LIGHT_EPSILON
# keeps near-black colours from producing huge ratios. Saturation changes by at
# most LIGHT_SAT_RANGE stops, and a colour below LIGHT_GREY relative chroma
# counts as hueless. The map fades out LIGHT_REACH world px from the nearest seam
# cell. As a pixel's brightest channel crosses LIGHT_KNEE it stops being
# brightened or resaturated (the shader repeats it).
SEAM_LIGHT_OUT = ROOT / 'data/visual/site7_seam_light.json'
LIGHT_GRID = (64, 36)
LIGHT_BLUR = 32.0
LIGHT_LOG_RANGE = 2.0
LIGHT_MIN_CELLS = 4
LIGHT_EPSILON = 0.02
LIGHT_REACH = 480.0
LIGHT_SAT_RANGE = 1.0
LIGHT_GREY = 0.08
LIGHT_KNEE = (0.45, 0.85)
LUMA = (0.299, 0.587, 0.114)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def png_size(path: Path) -> tuple[int, int]:
    with open(path, 'rb') as handle:
        head = handle.read(24)
    assert head[:8] == b'\x89PNG\r\n\x1a\n', path
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def norm(a):
    length = math.hypot(a[0], a[1])
    return (a[0] / length, a[1] / length)


def inside(point, poly) -> bool:
    x, y = point
    result = False
    count = len(poly)
    for i in range(count):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % count]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            result = not result
    return result


def edge_distance(point, poly) -> float:
    best = math.inf
    count = len(poly)
    for i in range(count):
        a, b = poly[i], poly[(i + 1) % count]
        ab = sub(b, a)
        t = max(0.0, min(1.0, dot(sub(point, a), ab) / max(1e-9, dot(ab, ab))))
        best = min(best, math.dist(point, add(a, mul(ab, t))))
    return best


def inside_by(point, poly, margin) -> bool:
    return inside(point, poly) and edge_distance(point, poly) >= margin


def centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def ray_exit(poly, origin, direction):
    best = None
    count = len(poly)
    for i in range(count):
        a, b = poly[i], poly[(i + 1) % count]
        e = sub(b, a)
        den = direction[0] * e[1] - direction[1] * e[0]
        if abs(den) < 1e-9:
            continue
        w = sub(a, origin)
        t = (w[0] * e[1] - w[1] * e[0]) / den
        s = (w[0] * direction[1] - w[1] * direction[0]) / den
        if t > 0 and 0 <= s <= 1 and (best is None or t > best):
            best = t
    return add(origin, mul(direction, best))


def segments_cross(p, q, a, b) -> bool:
    def orient(o, m, n): return (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0])
    d1, d2, d3, d4 = orient(a, b, p), orient(a, b, q), orient(p, q, a), orient(p, q, b)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)


def clip_to_rect(poly, rect):
    """Sutherland-Hodgman clip of `poly` to the axis-aligned `rect` (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = rect
    edges = [(lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
             (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))]
    out = list(poly)
    for keep, cut in edges:
        source, out = out, []
        for i, current in enumerate(source):
            previous = source[i - 1]
            if keep(current):
                if not keep(previous):
                    out.append(cut(previous, current))
                out.append(current)
            elif keep(previous):
                out.append(cut(previous, current))
    return out


def polygons_overlap(a, b) -> bool:
    for i in range(len(a)):
        for j in range(len(b)):
            if segments_cross(a[i], a[(i + 1) % len(a)], b[j], b[(j + 1) % len(b)]):
                return True
    return inside(a[0], b) or inside(b[0], a)


class Plate:
    def __init__(self, name: str, asset: str, scale: float, floor: list, mirror: bool = False, doors: dict | None = None, deck: str = '', seam_fade: float = SEAM_FADE, reverse: bool = False):
        self.name, self.asset, self.scale, self.floor, self.mirror = name, asset, scale, floor, mirror
        self.reverse = reverse
        self.size = png_size(ROOT / asset)
        self.center = (0.0, 0.0)
        self.doors = doors or {}
        self.deck = deck
        self.seam_fade = seam_fade
        self.anchors = []

    def local(self, p):
        x = (p[0] - 0.5) * self.size[0] * self.scale
        y = (p[1] - 0.5) * self.size[1] * self.scale
        return (-x if self.mirror else x, y)

    def world(self, p): return add(self.center, self.local(p))
    def floor_local(self): return [self.local(p) for p in self.floor]
    def floor_world(self): return [self.world(p) for p in self.floor]

    def lit_floor_local(self):
        """Floor clipped to the plate's lit interior (LIT_INSET in from each side)."""
        w, h = self.size[0] * self.scale, self.size[1] * self.scale
        lit = clip_to_rect(self.floor_local(), (-w / 2 + LIT_INSET * w, -h / 2 + LIT_INSET * h, w / 2 - LIT_INSET * w, h / 2 - LIT_INSET * h))
        return lit if len(lit) >= 3 else self.floor_local()

    def rect(self):
        w, h = self.size[0] * self.scale, self.size[1] * self.scale
        return (self.center[0] - w / 2, self.center[1] - h / 2, self.center[0] + w / 2, self.center[1] + h / 2)


def deck_ends(conn: Plate):
    """Local points of the deck's image-left and image-right ends."""
    xs = [p[0] for p in conn.floor]
    lo, hi = min(xs), max(xs)
    left = [conn.local(p) for p in conn.floor if p[0] <= lo + 0.05]
    right = [conn.local(p) for p in conn.floor if p[0] >= hi - 0.05]
    return left, right


def fade_samples(conn: Plate, image_left: bool):
    """Local points of the walkable deck inside one end's seam-fade band."""
    poly = conn.floor_local()
    w, h = conn.size[0] * conn.scale, conn.size[1] * conn.scale
    points = []
    y = -h / 2
    while y <= h / 2:
        x = -w / 2
        while x <= w / 2:
            u = x / w + 0.5
            if conn.mirror:
                u = 1.0 - u
            in_band = u <= FADE_BAND if image_left else u >= 1.0 - FADE_BAND
            if in_band and inside_by((x, y), poly, DECK_SAMPLE_INSET):
                points.append((x, y))
            x += SAMPLE_STEP
        y += SAMPLE_STEP
    return points


LATERAL = [0.0] + [s * k for k in range(1, 9) for s in (20.0, -20.0)]


def fits(offset, ends: list, band: list, floor: list) -> bool:
    """`ends`/`band` (local points shifted by `offset`) enter `floor` far enough."""
    if not inside_by(add(offset, centroid(ends)), floor, END_MARGIN):
        return False
    for e in ends:
        point = add(offset, e)
        if not inside(point, floor) and edge_distance(point, floor) > END_SLACK:
            return False
    if not band:
        return True
    return sum(inside(add(offset, b), floor) for b in band) >= BAND_INSIDE * len(band)


def attach_connector(room: Plate, conn: Plate, ends: list, band: list, direction) -> None:
    """Place `conn` so `ends` and `band` (its local points) lie in `room`'s floor."""
    floor = [add(room.center, p) for p in room.lit_floor_local()]
    exit_point = ray_exit(floor, centroid(floor), direction)
    anchor = centroid(ends)
    side = (-direction[1], direction[0])
    for t in range(0, 900, 5):
        for s in LATERAL:
            center = sub(add(sub(exit_point, mul(direction, t)), mul(side, s)), anchor)
            if fits(center, ends, band, floor):
                conn.center = sub(center, mul(direction, EXTRA_OVERLAP))
                return
    raise SystemExit(f'{conn.name}: deck end cannot enter {room.name}')


def attach_room(conn: Plate, room: Plate, ends: list, band: list, direction) -> None:
    """Place `room` so `conn`'s placed `ends` and `band` lie in its floor."""
    floor = room.lit_floor_local()
    entry = ray_exit(floor, centroid(floor), mul(direction, -1.0))
    target = add(conn.center, centroid(ends))
    side = (-direction[1], direction[0])
    for t in range(0, 900, 5):
        for s in LATERAL:
            local_point = add(add(entry, mul(direction, t)), mul(side, s))
            center = sub(target, local_point)
            world = [add(center, p) for p in floor]
            if fits(conn.center, ends, band, world):
                room.center = add(center, mul(direction, EXTRA_OVERLAP))
                return
    raise SystemExit(f'{room.name}: cannot receive {conn.name}')


_blurred: dict = {}


def blur_axis(values, radius: int, axis: int):
    """Box blur of `values` along `axis` (edge-padded), by running sums."""
    import numpy as np
    if radius < 1:
        return values
    pad = [(0, 0)] * values.ndim
    pad[axis] = (radius + 1, radius)
    total = np.cumsum(np.pad(values, pad, mode='edge'), axis=axis, dtype=np.float64)
    size = values.shape[axis]
    upper = np.take(total, np.arange(2 * radius + 1, 2 * radius + 1 + size), axis=axis)
    lower = np.take(total, np.arange(0, size), axis=axis)
    return ((upper - lower) / (2 * radius + 1)).astype(np.float32)


def blurred_plate(plate: Plate):
    """`plate`'s colour averaged over about LIGHT_BLUR world px (three box passes
    on a 1/4-size copy, alpha-weighted), with its coverage."""
    import numpy as np
    from PIL import Image
    if plate.asset not in _blurred:
        small = Image.open(ROOT / plate.asset).convert('RGBA').reduce(4)
        rgba = np.asarray(small, np.float32) / 255.0
        weighted = np.concatenate([rgba[..., :3] * rgba[..., 3:], rgba[..., 3:]], -1)
        radius = max(1, int(round(LIGHT_BLUR / plate.scale / 4 / 1.7)))
        for _ in range(3):
            weighted = blur_axis(blur_axis(weighted, radius, 0), radius, 1)
        coverage = weighted[..., 3]
        _blurred[plate.asset] = (weighted[..., :3] / np.maximum(coverage, 1e-4)[..., None], coverage)
    return _blurred[plate.asset]


def sample_blurred(plate: Plate, xs, ys):
    """Averaged colour and coverage of `plate` at world points."""
    import numpy as np
    colour, coverage = blurred_plate(plate)
    h, w = coverage.shape
    u = (xs - plate.center[0]) / (plate.size[0] * plate.scale)
    if plate.mirror:
        u = -u
    v = (ys - plate.center[1]) / (plate.size[1] * plate.scale)
    col = np.clip(((u + 0.5) * w).astype(int), 0, w - 1)
    row = np.clip(((v + 0.5) * h).astype(int), 0, h - 1)
    return colour[row, col], coverage[row, col]


def points_inside(poly, xs, ys):
    """Even-odd test of many points against `poly`."""
    import numpy as np
    result = np.zeros(xs.shape, bool)
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        if ay == by:
            continue
        crosses = (ay > ys) != (by > ys)
        result ^= crosses & (xs < (bx - ax) * (ys - ay) / (by - ay) + ax)
    return result


def texture_to_world(plate: Plate, u, v):
    """World points of texture coordinates (a mirrored plate's texture runs right
    to left in the world)."""
    x = (u - 0.5) * plate.size[0] * plate.scale
    y = (v - 0.5) * plate.size[1] * plate.scale
    return plate.center[0] + (-x if plate.mirror else x), plate.center[1] + y


def light_cells(conn: Plate):
    """Texture coordinates of the connector's light-map cell centres, row by row."""
    import numpy as np
    columns, rows = LIGHT_GRID
    return np.meshgrid((np.arange(columns) + 0.5) / columns, (np.arange(rows) + 0.5) / rows)


def visible_along_deck(conn: Plate, u, v):
    """Texture points moved back along the deck until they leave the seam fade at
    the plate's cut ends: the deck there is painted dark but never shown, so the
    colour the room meets is the deck's where it becomes visible."""
    import numpy as np
    left, right = deck_ends(conn)
    start = centroid([(p[0] if not conn.mirror else -p[0], p[1]) for p in left])
    finish = centroid([(p[0] if not conn.mirror else -p[0], p[1]) for p in right])
    du = (finish[0] - start[0]) / (conn.size[0] * conn.scale)
    dv = (finish[1] - start[1]) / (conn.size[1] * conn.scale)
    fade = conn.seam_fade
    back = np.where(u > 1.0 - fade, (u - (1.0 - fade)) / du, np.where(u < fade, (u - fade) / du, 0.0))
    return u - back * du, v - back * dv


def luma_chroma(rgb):
    """Luminance of averaged colours, and their chroma (B - Y, R - Y) relative
    to it, whose length is the saturation."""
    import numpy as np
    luma = (rgb * np.asarray(LUMA, np.float32)).sum(-1)
    return luma, np.stack([rgb[..., 2] - luma, rgb[..., 0] - luma], -1) / (luma[..., None] + LIGHT_EPSILON)


def seam_light(conn: Plate, rooms: list):
    """Light map for `conn`: per cell a brightness gain and a saturation factor
    (log2) that bring the connector's averaged colour to the room's brightness
    and saturation where its deck lies on a room floor; elsewhere a
    distance-weighted blend of those, room by room, easing to none LIGHT_REACH px
    from them. None when no room gives enough cells."""
    import numpy as np
    u, v = light_cells(conn)
    xs, ys = texture_to_world(conn, u, v)
    deck = conn.floor_world()
    on_deck = points_inside(deck, xs, ys)
    source, source_cover = sample_blurred(conn, *texture_to_world(conn, *visible_along_deck(conn, u, v)))
    source_luma, source_chroma = luma_chroma(source)
    cell = conn.size[0] * conn.scale / LIGHT_GRID[0]
    fields, gaps = [], []
    for room in rooms:
        target, target_cover = sample_blurred(room, xs, ys)
        known = on_deck & points_inside(room.floor_world(), xs, ys) & (source_cover > 0.5) & (target_cover > 0.5)
        if known.sum() < LIGHT_MIN_CELLS:
            continue
        target_luma, target_chroma = luma_chroma(target[known])
        gain = (target_luma + LIGHT_EPSILON) / (source_luma[known] + LIGHT_EPSILON)
        # Saturation only, never hue: pulling an orange deck toward a cyan room
        # channel by channel passed through green. Saturation rises only as far as
        # the two hues agree; against an opposite hue it falls instead, so the seam
        # meets in grey. A near-grey colour has no hue to agree with.
        target_sat = np.linalg.norm(target_chroma, axis=-1)
        source_sat = np.linalg.norm(source_chroma[known], axis=-1)
        agree = (target_chroma * source_chroma[known]).sum(-1) / np.maximum(target_sat * source_sat, 1e-6)
        agree *= np.clip(np.minimum(target_sat, source_sat) / LIGHT_GREY, 0.0, 1.0)
        sat = (target_sat + LIGHT_EPSILON) / (source_sat + LIGHT_EPSILON)
        sat = np.where(sat > 1.0, 1.0 + (sat - 1.0) * agree, sat)
        change = np.stack([
            np.log2(np.clip(gain, 2.0 ** -LIGHT_LOG_RANGE, 2.0 ** LIGHT_LOG_RANGE)),
            np.log2(np.clip(sat, 2.0 ** -LIGHT_SAT_RANGE, 2.0 ** LIGHT_SAT_RANGE)),
        ], -1)
        distance2 = (xs[..., None] - xs[known]) ** 2 + (ys[..., None] - ys[known]) ** 2
        near = 1.0 / np.maximum(distance2, cell * cell)
        fields.append((near[..., None] * change).sum(-2) / near.sum(-1)[..., None])
        gaps.append(np.sqrt(np.maximum(distance2.min(-1), cell * cell)))
    if not fields:
        return None
    weights = [1.0 / (gap * gap) for gap in gaps]
    log_light = sum(f * (w / sum(weights))[..., None] for f, w in zip(fields, weights))
    # Past the seams the light eases back to none, so the middle of a long deck
    # keeps its painted colour instead of an average of two rooms' corrections.
    reach = np.clip(1.0 - np.minimum.reduce(gaps) / LIGHT_REACH, 0.0, 1.0)
    log_light *= (reach * reach * (3.0 - 2.0 * reach))[..., None]
    # Both were measured on the deck. Walls and lamps beside it carry other colours
    # and glows, so off the deck, one cell of feather out, they keep their
    # saturation and may only be darkened: lifting a dark purple deck to R05's
    # brighter floor also doubled the purple glow around its pillars.
    deck_share = blur_axis(blur_axis(on_deck.astype(np.float32), 1, 0), 1, 1)
    log_light[..., 1] *= deck_share
    log_light[..., 0] = np.where(log_light[..., 0] > 0.0, log_light[..., 0] * deck_share, log_light[..., 0])
    return np.round((log_light / LIGHT_LOG_RANGE + 1.0) * 0.5 * 255.0).clip(0, 255).astype(np.uint8)


def decode_light(encoded):
    import numpy as np
    return 2.0 ** ((encoded.astype(np.float32) / 255.0 * 2.0 - 1.0) * LIGHT_LOG_RANGE)


def apply_light(rgb, light):
    """Runtime (site7_room_art_layer.gd): multiply by the gain (light[..., 0])
    and scale the colour around its luminance by the saturation (light[..., 1]),
    except that as the brightest channel crosses LIGHT_KNEE a pixel is no longer
    brightened or resaturated, so lamps and glows (bright but often low in
    luminance, like purple) keep their look. 0-1 colour."""
    import numpy as np
    peak = rgb.max(-1, keepdims=True)
    t = np.clip((peak - LIGHT_KNEE[0]) / (LIGHT_KNEE[1] - LIGHT_KNEE[0]), 0.0, 1.0)
    keep = t * t * (3.0 - 2.0 * t)
    gain, sat = light[..., :1], light[..., 1:2]
    lit = rgb * (gain + (np.minimum(gain, 1.0) - gain) * keep)
    luma = (lit * np.asarray(LUMA, np.float32)).sum(-1, keepdims=True)
    return np.clip(luma + (lit - luma) * (sat + (1.0 - sat) * keep), 0.0, 1.0)


def seam_lights(solved: dict) -> dict:
    """Connector index -> encoded light map (rows x columns x gain, saturation bytes)."""
    lights = {}
    for index, a, b in solved['links']:
        encoded = seam_light(solved['connectors'][index], [solved['rooms'][a], solved['rooms'][b]])
        if encoded is not None:
            lights[index] = encoded
    return lights


def link(a: Plate, conn: Plate, b: Plate) -> None:
    """Places `conn` against placed room `a`, then room `b` against `conn`."""
    left, right = deck_ends(conn)
    # Authored decks start at image-left in either direction. A legacy mirrored
    # branch starts at image-right (world upper left). A reversed deck meets `a`
    # at its finish, so the route runs back down it.
    start, finish = (right, left) if conn.mirror else (left, right)
    near_a, near_b = (finish, start) if conn.reverse else (start, finish)
    end_a, end_b = ('finish', 'start') if conn.reverse else ('start', 'finish')
    band_a_left = conn.mirror == conn.reverse
    direction = norm(sub(centroid(near_b), centroid(near_a)))
    # An authored v2 doorway owns the join: `a`'s door faces along the deck, `b`'s
    # back up it. Legacy rooms keep their existing floor-fit placement.
    side_a = ('S' if direction[1] > 0 else 'N') + ('E' if direction[0] > 0 else 'W')
    side_b = ('N' if direction[1] > 0 else 'S') + ('W' if direction[0] > 0 else 'E')
    if side_a in a.doors:
        target = a.world(a.doors[side_a][:2])
        conn.center = sub(target, centroid(near_a))
        conn.anchors.append({'room': a.name, 'side': side_a, 'end': end_a, 'position': target})
    else:
        attach_connector(a, conn, near_a, fade_samples(conn, image_left=band_a_left), direction)
    if side_b in b.doors:
        target = add(conn.center, centroid(near_b))
        b.center = sub(target, b.local(b.doors[side_b][:2]))
        conn.anchors.append({'room': b.name, 'side': side_b, 'end': end_b, 'position': target})
    else:
        attach_room(conn, b, near_b, fade_samples(conn, image_left=not band_a_left), direction)


def branch_parents(mission: dict) -> list[str]:
    """The main room each optional room hangs from: its "from", else the room two ahead."""
    main = [row['id'] for row in mission['main_route']]
    parents = []
    for j, row in enumerate(mission['optional_rooms']):
        parent = row.get('from', main[min(j + 2, len(main) - 1)])
        if parent not in main:
            raise SystemExit(f'{row["id"]}: branch parent {parent} is not on the main route')
        parents.append(parent)
    return parents


def solve(mission_id: str, art: dict, layouts: dict, floors: dict) -> dict:
    mission = load(MISSIONS / f'{mission_id}.json')
    manifest = art['missions'][mission_id]
    authored = layouts['missions'].get(mission_id, {})
    rooms: dict[str, Plate] = {}
    for row in manifest['rooms']:
        room_id = row['room_id']
        floor = authored.get(room_id, {}).get('floor') or floors[row['asset']]['floor']
        rooms[room_id] = Plate(room_id, row['asset'], float(row.get('scale', 0.88)), floor, doors=floors.get(row['asset'], {}).get('doors', {}))
    connectors = []
    for i, row in enumerate(manifest['connectors']):
        deck = row.get('deck', '')
        if deck not in ('', 'ascending', 'descending'):
            raise ValueError(f'Unknown deck direction: {deck}')
        # Only v1 branches need a mirror; v2 descending art is authored that way.
        mirror = i >= 5 and not deck
        connectors.append(Plate('C%d' % i, row['asset'], float(row.get('scale', 0.84)), floors[row['asset']]['floor'], mirror=mirror, deck=deck,
                                seam_fade=float(row.get('seam_fade', SEAM_FADE)), reverse=bool(row.get('reverse', False))))
    main = [row['id'] for row in mission['main_route']]
    optional = [row['id'] for row in mission['optional_rooms']]
    parents = branch_parents(mission)
    rooms[main[0]].center = ENTRY_CENTER
    links = [(i, main[i], main[i + 1]) for i in range(len(main) - 1)]
    links += [(5 + j, parents[j], room_id) for j, room_id in enumerate(optional)]
    for index, a, b in links:
        link(rooms[a], connectors[index], rooms[b])
    return {'mission': mission, 'rooms': rooms, 'connectors': connectors, 'main': main, 'optional': optional, 'parents': parents, 'links': links}


def validate(solved: dict) -> list[str]:
    rooms, connectors, main, optional, parents = solved['rooms'], solved['connectors'], solved['main'], solved['optional'], solved['parents']
    problems = []
    for room_id, room in rooms.items():
        # The objective marker is the plate centre; it only has to be reachable
        # within the stage's interaction radius (150 px), as before this layout.
        floor = room.floor_world()
        if not inside(room.center, floor) and edge_distance(room.center, floor) > 100.0:
            problems.append(f'{room_id} centre marker is off its floor')
    adjacent = set()
    for i in range(len(main) - 1):
        adjacent |= {(main[i], f'C{i}'), (f'C{i}', main[i + 1])}
    for j, room_id in enumerate(optional):
        adjacent |= {(parents[j], f'C{5 + j}'), (f'C{5 + j}', room_id)}
    plates = list(rooms.values()) + connectors
    for conn in connectors:
        left, right = deck_ends(conn)
        start, finish = (right, left) if conn.mirror else (left, right)
        delta = sub(centroid(finish), centroid(start))
        if conn.deck and ((delta[1] > 0) != (conn.deck == 'descending') or delta[0] <= 0):
            problems.append(f'{conn.name}: traced floor disagrees with authored {conn.deck} deck')
        for anchor in conn.anchors:
            endpoint = start if anchor['end'] == 'start' else finish
            if math.dist(add(conn.center, centroid(endpoint)), anchor['position']) > 0.5:
                problems.append(f'{conn.name}: authored doorway is not aligned')
    for i, a in enumerate(plates):
        for b in plates[i + 1:]:
            if (a.name, b.name) in adjacent or (b.name, a.name) in adjacent:
                continue
            if a.name.startswith('C') and b.name.startswith('C'):
                continue  # decks meeting inside a shared room
            if polygons_overlap(a.floor_world(), b.floor_world()):
                problems.append(f'{a.name} floor overlaps non-adjacent {b.name}')
    return problems


def to_json(solved: dict) -> dict:
    r = lambda v: [round(v[0], 1), round(v[1], 1)]
    return {
        'rooms': {room_id: r(plate.center) for room_id, plate in solved['rooms'].items()},
        'connectors': [dict({'position': r(c.center), 'scale': c.scale, 'mirror': c.mirror},
                           **({'reverse': True} if c.reverse else {}),
                           **({'deck': c.deck} if c.deck else {}),
                           **({'seam_fade': c.seam_fade} if c.seam_fade != SEAM_FADE else {}),
                           **({'door_anchors': [dict(a, position=r(a['position'])) for a in c.anchors]} if c.anchors else {}))
                       for c in solved['connectors']],
    }


def render_preview(solved: dict, out_dir: Path, mission_id: str) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    rooms, connectors = solved['rooms'], solved['connectors']
    order = [rooms[r] for r in solved['main'] + solved['optional']] + connectors
    rects = [p.rect() for p in order]
    x0, y0 = min(r[0] for r in rects), min(r[1] for r in rects)
    x1, y1 = max(r[2] for r in rects), max(r[3] for r in rects)

    def draw(k, box, name):
        bx0, by0, bx1, by1 = box
        W, H = round((bx1 - bx0) * k), round((by1 - by0) * k)
        canvas = np.zeros((H, W, 3), np.float32)
        earlier: list = []
        for plate in order:
            w, h = int(plate.size[0] * plate.scale * k), int(plate.size[1] * plate.scale * k)
            im = Image.open(ROOT / plate.asset).convert('RGB')
            if plate.mirror:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            rgb = np.asarray(im.resize((w, h), Image.BILINEAR), np.float32)
            alpha = np.ones((h, w), np.float32)
            px, py = int((plate.center[0] - plate.size[0] * plate.scale / 2 - bx0) * k), int((plate.center[1] - plate.size[1] * plate.scale / 2 - by0) * k)
            if plate in connectors:
                xs = (np.arange(w) + 0.5) / w
                ramp = lambda t: np.clip(t / plate.seam_fade, 0, 1) ** 2 * (3 - 2 * np.clip(t / plate.seam_fade, 0, 1))
                alpha *= (ramp(xs) * ramp(1 - xs))[None, :]
                ys = (np.arange(h) + 0.5) / h
                cap_ramp = lambda t: np.clip(t / CAP_FADE, 0, 1) ** 2 * (3 - 2 * np.clip(t / CAP_FADE, 0, 1))
                cap = np.repeat((cap_ramp(ys) * cap_ramp(1 - ys))[:, None], w, axis=1)
                deck = Image.new('L', (w, h), 0)
                ImageDraw.Draw(deck).polygon([((q[0] - bx0) * k - px, (q[1] - by0) * k - py) for q in plate.floor_world()], fill=255)
                feather = max(1, int(CAP_FEATHER * k))
                inside = np.asarray(deck.filter(ImageFilter.MinFilter(2 * (feather // 2) + 1)).filter(ImageFilter.GaussianBlur(feather / 2)), np.float32) / 255.0
                alpha *= np.maximum(cap, inside)
            else:
                edge = lambda t: np.clip(t / ROOM_EDGE_FADE, 0, 1) ** 2 * (3 - 2 * np.clip(t / ROOM_EDGE_FADE, 0, 1))
                xs = (np.arange(w) + 0.5) / w
                ys = (np.arange(h) + 0.5) / h
                alpha *= (edge(ys) * edge(1 - ys))[:, None] * (edge(xs) * edge(1 - xs))[None, :]
            hide = np.zeros((h, w), np.float32)
            gx = (np.arange(w) + 0.5) / k + (px / k + bx0)
            gy = (np.arange(h) + 0.5) / k + (py / k + by0)
            for poly, (rx0, ry0, rx1, ry1) in earlier:
                mask = Image.new('L', (w, h), 0)
                ImageDraw.Draw(mask).polygon([((q[0] - bx0) * k - px, (q[1] - by0) * k - py) for q in poly], fill=255)
                fade_x = np.clip(np.minimum(gx - rx0, rx1 - gx) / (LIT_INSET * (rx1 - rx0)), 0, 1)
                fade_y = np.clip(np.minimum(gy - ry0, ry1 - gy) / (LIT_INSET * (ry1 - ry0)), 0, 1)
                smooth = lambda t: t * t * (3 - 2 * t)
                hide = np.maximum(hide, np.asarray(mask, np.float32) / 255.0 * smooth(fade_y)[:, None] * smooth(fade_x)[None, :])
            alpha *= 1.0 - hide
            encoded = solved.get('lights', {}).get(connectors.index(plate)) if plate in connectors else None
            if encoded is not None:
                # Runtime: bilinear over the cell grid, then apply_light.
                fields = [Image.fromarray(np.ascontiguousarray(encoded[..., i]), 'L').resize((w, h), Image.BILINEAR) for i in range(2)]
                if plate.mirror:
                    fields = [field.transpose(Image.FLIP_LEFT_RIGHT) for field in fields]
                rgb = apply_light(rgb / 255.0, decode_light(np.stack([np.asarray(field) for field in fields], -1))) * 255.0
            earlier.append((plate.floor_world(), plate.rect()))
            sx0, sy0 = max(0, px), max(0, py)
            sx1, sy1 = min(W, px + w), min(H, py + h)
            if sx1 <= sx0 or sy1 <= sy0:
                continue
            region = (slice(sy0 - py, sy1 - py), slice(sx0 - px, sx1 - px))
            a = alpha[region][..., None]
            canvas[sy0:sy1, sx0:sx1] = canvas[sy0:sy1, sx0:sx1] * (1 - a) + rgb[region] * a
        image = Image.fromarray(canvas.clip(0, 255).astype(np.uint8))
        dr = ImageDraw.Draw(image)
        for plate in order:
            pts = [((q[0] - bx0) * k, (q[1] - by0) * k) for q in plate.floor_world()]
            dr.line(pts + [pts[0]], fill=(40, 255, 80), width=2)
        for room_id in solved['main'] + solved['optional']:
            c = rooms[room_id].center
            dr.text(((c[0] - bx0) * k, (c[1] - by0) * k), room_id, fill=(255, 230, 0))
        image.save(out_dir / f'{mission_id}_{name}.png')

    out_dir.mkdir(parents=True, exist_ok=True)
    k = min(1920 / (x1 - x0), 1080 / (y1 - y0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw(k, (cx - 960 / k, cy - 540 / k, cx + 960 / k, cy + 540 / k), 'overview')
    main, optional = solved['main'], solved['optional']
    pairs = [(main[i], main[i + 1], f'link{i}') for i in range(len(main) - 1)]
    pairs += [(solved['parents'][j], room_id, f'branch{j}') for j, room_id in enumerate(optional)]
    for a, b, name in pairs:
        ca, cb = rooms[a].center, rooms[b].center
        mx, my = (ca[0] + cb[0]) / 2, (ca[1] + cb[1]) / 2
        draw(0.5, (mx - 1920, my - 1080, mx + 1920, my + 1080), name)


def same_lights(stored: str, lights: dict) -> bool:
    """Whether stored seam lights match fresh ones to within one step per byte:
    another numpy build (the regression runner's interpreter) rounds a few
    blurred averages the other way."""
    import numpy as np
    try:
        old = json.loads(stored)
    except ValueError:
        return False
    if {k: v for k, v in old.items() if k != 'missions'} != {k: v for k, v in lights.items() if k != 'missions'}:
        return False
    if {m: sorted(c) for m, c in old.get('missions', {}).items()} != {m: sorted(c) for m, c in lights['missions'].items()}:
        return False
    for mission_id, connectors in lights['missions'].items():
        for key, encoded in connectors.items():
            a = np.frombuffer(base64.b64decode(old['missions'][mission_id][key]), np.uint8).astype(int)
            b = np.frombuffer(base64.b64decode(encoded), np.uint8).astype(int)
            if a.shape != b.shape or np.abs(a - b).max(initial=0) > 1:
                return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--preview', type=Path, help='render review composites into this folder')
    parser.add_argument('--check', action='store_true', help='fail if the stored layout or seam lights differ from a fresh solve')
    args = parser.parse_args()
    art, layouts, floors = load(ART), load(LAYOUTS), load(PLATE_FLOORS)['plates']
    result = {
        'schema': 1,
        'source': 'tools/environment/build_site7_world_layout.py',
        'coordinate_space': 'world px; plate centres. No rotations. Authored deck direction is unmirrored; only legacy branches mirror. Door anchors are world-pixel threshold centres.',
        'missions': {},
    }
    lights = {
        'schema': 1,
        'source': 'tools/environment/build_site7_world_layout.py',
        'grid': list(LIGHT_GRID),
        'log2_range': LIGHT_LOG_RANGE,
        'encoding': 'per connector: base64 of grid rows x columns x (brightness gain, saturation) bytes over its texture (top row first); value = 2 ** ((byte / 255 * 2 - 1) * log2_range)',
        'missions': {},
    }
    failures = []
    for mission_id in sorted(art['missions']):
        solved = solve(mission_id, art, layouts, floors)
        failures += [f'{mission_id}: {p}' for p in validate(solved)]
        solved['lights'] = seam_lights(solved)
        failures += [f'{mission_id}: C{i} has no seam light' for i, _, _ in solved['links'] if i not in solved['lights']]
        lights['missions'][mission_id] = {f'C{i}': base64.b64encode(encoded.tobytes()).decode('ascii')
                                          for i, encoded in sorted(solved['lights'].items())}
        result['missions'][mission_id] = to_json(solved)
        if args.preview:
            render_preview(solved, args.preview, mission_id)
    for path, data in ((OUT, result), (SEAM_LIGHT_OUT, lights)):
        text = json.dumps(data, indent=2) + '\n'
        if args.check:
            stored = path.read_text(encoding='utf-8') if path.exists() else ''
            if stored != text and not (path == SEAM_LIGHT_OUT and same_lights(stored, lights)):
                raise SystemExit(f'{path.name} is stale; rerun build_site7_world_layout.py')
        else:
            path.write_text(text, encoding='utf-8', newline='\n')
    for failure in failures:
        print('LAYOUT_PROBLEM', failure)
    print('SITE7_WORLD_LAYOUT', 'PASS' if not failures else 'FAIL', len(result['missions']), 'missions')
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
