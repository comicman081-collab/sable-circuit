"""Measure how evenly the SITE-7 background plates are lit, as a gate for new or
repainted plate art.

Each plate was painted under its own lighting. The runtime seam light
(build_site7_world_layout.py, site7_seam_light.json) corrects brightness and
saturation where a connector deck meets a room floor, but it never shifts hue and
cannot hide a hot spot, a black hole or a strong colour cast painted on the floor.
This tool reports, from the plates' own pixels:

- per plate, its walkable floor (site7_plate_floors.json, or the mission battle
  layout for combat rooms): mean luminance, the 10th/90th percentile luminance,
  the mean colour's saturation and hue, and the slope of its floor edges (the
  camera: every plate should share one 2:1 dimetric floor axis);
- per seam (each connector end lying on a room floor), the same blurred colours
  the seam light is fitted from: the brightness step in stops, both saturations
  and the hue difference.

Everything is measured on the unlit plates, before the seam light. FLOOR_* and
SEAM_* are the targets for new art; `--strict` exits 1 when any plate or seam
misses them. SEAM_WAIVERS names the few seams the user accepted although the raw
plates miss the targets; each is judged again with the shipped seam light applied
and stays a failure unless it meets the targets there. `--out` writes the full
report as JSON (use a project-local path such as .cache/...). It writes nothing else.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('site7_world_layout', ROOT / 'tools/environment/build_site7_world_layout.py')
wl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wl)

# Walkable floor: a mid-dark, near-neutral steel floor with no black holes and no
# blown pools. Luminance is sRGB-encoded 0-1 (Rec. 601 weights, as the shader).
FLOOR_LUMA = (0.17, 0.24)
FLOOR_P10_MIN = 0.07
FLOOR_P90_MAX = 0.38
FLOOR_SAT_MAX = 0.15
# Floor edges run at the 2:1 dimetric slope (26.6 degrees) within this range;
# edges steeper than 60 or flatter than 5 degrees (image-border cuts, wall bases
# seen end-on) are not counted.
FLOOR_AXIS = (22.5, 30.5)
# User-approved 2026-09-30 (up to 31.5) and raised 2026-10-01 (up to 32.5): only authored descending C06/C07 branch
# plates. ImageGen draws these decks 30.7-33.5 deg whatever the prompt asks (operation 8 C06 and C07, operation 9 C06
# and C07), and the shipped decks of operations 4-6 are painted at 30-35 deg; their registered outline is the untraced
# standard (28.65 / 28.19 deg), so only newly traced plates ever met the limit.
BRANCH_FLOOR_AXIS = (22.5, 32.5)
# Seams: at most SEAM_STEP_MAX stops apart; saturations within SEAM_SAT_RATIO of
# each other unless both are below GREY; hues within SEAM_HUE_MAX degrees unless
# either side is below GREY (a grey has no hue to disagree with).
SEAM_STEP_MAX = 0.35
SEAM_SAT_RATIO = 1.5
SEAM_HUE_MAX = 30.0
GREY = 0.15
# User-approved 2026-09-30 (option "b" of qa/site7_op8_preenable_20260930/README_KO.md, chosen instead of
# regenerating the decks): three operation-8 decks sit further from their room floor than the targets allow.
# A seam is listed by (mission, plate, room) with the widest raw brightness step and saturation ratio it may
# show, each a little above what was measured, and counts as waived only while the shipped runtime seam light
# (site7_seam_light.json) brings the same seam inside SEAM_STEP_MAX and SEAM_SAT_RATIO on screen (measured
# 0.04 stops / 1.41x, 0.00 / 1.28x and 0.01 / 1.27x). Any other seam, or a listed one past its own limits or
# left off target by the seam light, fails as before. Hue is never waived.
SEAM_WAIVERS = {
    ('MIS_CH01_08', 'S8_C01', 'R01_GATE'): {'saturation_ratio': 1.95},
    ('MIS_CH01_08', 'S8_C03', 'R04_JUNCTION'): {'saturation_ratio': 2.1},
    ('MIS_CH01_08', 'S8_C05', 'R05_TERMINAL'): {'step': 0.40, 'saturation_ratio': 1.9},
}


def colour_stats(rgb):
    """Luminance, saturation (chroma length relative to luminance) and hue in
    degrees (0 = magenta-red side of the (B-Y, R-Y) plane, ~140 amber, ~-45 cyan)."""
    luma = sum(c * w for c, w in zip(rgb, wl.LUMA))
    cb, cr = float(rgb[2] - luma), float(rgb[0] - luma)
    return float(luma), math.hypot(cb, cr) / (float(luma) + wl.LIGHT_EPSILON), math.degrees(math.atan2(cr, cb))


def hue_gap(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def floor_axis(points) -> float:
    """Length-weighted mean slope (degrees, 0-90) of the floor polygon's edges
    that are neither near-flat nor near-vertical; 0 when there are none."""
    total = weight = 0.0
    for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
        length = math.hypot(bx - ax, by - ay)
        slope = math.degrees(math.atan2(abs(by - ay), abs(bx - ax)))
        if 5.0 <= slope <= 60.0:
            total, weight = total + slope * length, weight + length
    return total / weight if weight else 0.0


def floor_axis_limits(asset: str) -> tuple[float, float]:
    # Match the plate ID, never a containing folder or another corridor number.
    stem = Path(asset).stem
    return BRANCH_FLOOR_AXIS if re.fullmatch(r'S\d+_C0[67]_GAME', stem) else FLOOR_AXIS


def plate_floor(plate) -> dict:
    import numpy as np
    from PIL import Image, ImageDraw
    image = Image.open(ROOT / plate.asset).convert('RGB')
    w, h = image.size
    points = [(x * w, y * h) for x, y in plate.floor]
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    pixels = np.asarray(image, np.float32)[np.asarray(mask) > 0] / 255.0
    luma, sat, hue = colour_stats(pixels.mean(0))
    each = (pixels * np.asarray(wl.LUMA, np.float32)).sum(-1)
    row = {'asset': plate.asset, 'luma': luma, 'p10': float(np.percentile(each, 10)), 'p90': float(np.percentile(each, 90)),
           'saturation': sat, 'hue': hue, 'axis': floor_axis(points)}
    axis_limits = floor_axis_limits(plate.asset)
    row['problems'] = [p for p, bad in (
        (f'floor luminance {luma:.3f} outside {FLOOR_LUMA}', not FLOOR_LUMA[0] <= luma <= FLOOR_LUMA[1]),
        (f'dark holes: p10 {row["p10"]:.3f} < {FLOOR_P10_MIN}', row['p10'] < FLOOR_P10_MIN),
        (f'hot spots: p90 {row["p90"]:.3f} > {FLOOR_P90_MAX}', row['p90'] > FLOOR_P90_MAX),
        (f'colour cast: saturation {sat:.2f} > {FLOOR_SAT_MAX}', sat > FLOOR_SAT_MAX),
        (f'floor axis {row["axis"]:.1f} deg outside {axis_limits}', not axis_limits[0] <= row['axis'] <= axis_limits[1])) if bad]
    return row


def plate_id(asset: str) -> str:
    """'assets/environments/site7_v2/stage08/S8_C01/S8_C01_GAME.png' -> 'S8_C01'."""
    stem = Path(asset).stem
    return stem[:-len('_GAME')] if stem.endswith('_GAME') else stem


_SHIPPED_LIGHT: dict = {}


def shipped_light(mission_id: str, index: int):
    """The runtime seam light of one connector (rows x columns x gain, saturation), decoded; None without one."""
    import base64
    import numpy as np
    if not _SHIPPED_LIGHT:
        _SHIPPED_LIGHT.update(json.loads((ROOT / 'data/visual/site7_seam_light.json').read_text(encoding='utf-8')))
    encoded = _SHIPPED_LIGHT['missions'].get(mission_id, {}).get(f'C{index}')
    if not encoded:
        return None
    columns, rows = _SHIPPED_LIGHT['grid']
    return wl.decode_light(np.frombuffer(base64.b64decode(encoded), np.uint8).reshape(rows, columns, 2))


def saturation_ratio(ds: float, rs: float) -> float:
    return (max(ds, rs) + wl.LIGHT_EPSILON) / (min(ds, rs) + wl.LIGHT_EPSILON)


def seam_problems(step, ds, rs, dh, rh, step_limit=SEAM_STEP_MAX, ratio_limit=SEAM_SAT_RATIO) -> list:
    """What is off target at one seam: brightness step (stops), the deck's and the room floor's saturation and hue."""
    coloured = min(ds, rs) >= GREY
    return [p for p, bad in (
        (f'brightness step {step:+.2f} stops', abs(step) > step_limit),
        (f'saturation {ds:.2f} vs {rs:.2f}', max(ds, rs) >= GREY and saturation_ratio(ds, rs) > ratio_limit),
        (f'hue {dh:.0f} vs {rh:.0f} ({hue_gap(dh, rh):.0f} deg)', coloured and hue_gap(dh, rh) > SEAM_HUE_MAX)) if bad]


def seams(solved: dict, mission_id: str = '') -> list:
    rows = []
    for index, a, b in solved['links']:
        conn = solved['connectors'][index]
        u, v = wl.light_cells(conn)
        xs, ys = wl.texture_to_world(conn, u, v)
        on_deck = wl.points_inside(conn.floor_world(), xs, ys)
        deck, deck_cover = wl.sample_blurred(conn, *wl.texture_to_world(conn, *wl.visible_along_deck(conn, u, v)))
        for room_id in (a, b):
            room = solved['rooms'][room_id]
            floor, floor_cover = wl.sample_blurred(room, xs, ys)
            known = on_deck & wl.points_inside(room.floor_world(), xs, ys) & (deck_cover > 0.5) & (floor_cover > 0.5)
            row = {'connector': f'C{index}', 'asset': conn.asset, 'room': room_id, 'mirror': conn.mirror, 'cells': int(known.sum())}
            if row['cells'] == 0:
                row['problems'] = ['deck never reaches the room floor']
                rows.append(row)
                continue
            dl, ds, dh = colour_stats(deck[known].mean(0))
            rl, rs, rh = colour_stats(floor[known].mean(0))
            row.update(step=math.log2((rl + wl.LIGHT_EPSILON) / (dl + wl.LIGHT_EPSILON)), deck_saturation=ds, room_saturation=rs,
                       saturation_ratio=saturation_ratio(ds, rs), deck_hue=dh, room_hue=rh, hue_gap=hue_gap(dh, rh))
            row['problems'] = problems = seam_problems(row['step'], ds, rs, dh, rh)
            row['waived'] = []
            waiver = SEAM_WAIVERS.get((mission_id, plate_id(conn.asset), room_id))
            if problems and waiver:
                past = seam_problems(row['step'], ds, rs, dh, rh, waiver.get('step', SEAM_STEP_MAX),
                                     waiver.get('saturation_ratio', SEAM_SAT_RATIO))
                light = shipped_light(mission_id, index)
                unfixed = ['no seam light ships for this connector']
                if light is not None:
                    lit_l, lit_s, lit_h = colour_stats(wl.apply_light(deck[known], light[known]).mean(0))
                    step = math.log2((rl + wl.LIGHT_EPSILON) / (lit_l + wl.LIGHT_EPSILON))
                    row['with_seam_light'] = {'step': step, 'deck_saturation': lit_s, 'saturation_ratio': saturation_ratio(lit_s, rs)}
                    unfixed = seam_problems(step, lit_s, rs, lit_h, rh)
                if past or unfixed:
                    row['problems'] = problems + [f'past its waiver: {p}' for p in past] + [f'with the seam light: {p}' for p in unfixed]
                else:
                    row['waived'], row['problems'] = problems, []
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--mission', action='append', help='mission id (repeatable); default: every mission')
    parser.add_argument('--out', type=Path, help='write the report as JSON here')
    parser.add_argument('--strict', action='store_true', help='exit 1 if any plate or seam misses the targets')
    args = parser.parse_args()
    art, layouts, floors = wl.load(wl.ART), wl.load(wl.LAYOUTS), wl.load(wl.PLATE_FLOORS)['plates']
    report = {'targets': {'floor_luma': FLOOR_LUMA, 'floor_p10_min': FLOOR_P10_MIN, 'floor_p90_max': FLOOR_P90_MAX,
                          'floor_saturation_max': FLOOR_SAT_MAX, 'floor_axis': FLOOR_AXIS,
                          'branch_C06_C07_floor_axis': BRANCH_FLOOR_AXIS, 'seam_step_max': SEAM_STEP_MAX,
                          'seam_saturation_ratio': SEAM_SAT_RATIO, 'seam_hue_max': SEAM_HUE_MAX, 'grey': GREY,
                          'seam_waivers': [dict(zip(('mission', 'plate', 'room'), key), **limits)
                                           for key, limits in SEAM_WAIVERS.items()]},
              'plates': {}, 'missions': {}}
    failed = waived = 0
    for mission_id in args.mission or sorted(art['missions']):
        solved = wl.solve(mission_id, art, layouts, floors)
        for plate in list(solved['rooms'].values()) + solved['connectors']:
            if plate.asset not in report['plates']:
                row = report['plates'][plate.asset] = plate_floor(plate)
                failed += bool(row['problems'])
                print(f"PLATE {'FAIL' if row['problems'] else 'PASS'} {Path(plate.asset).name}: luma {row['luma']:.3f} "
                      f"p10 {row['p10']:.3f} p90 {row['p90']:.3f} sat {row['saturation']:.2f} hue {row['hue']:.0f} axis {row['axis']:.1f}"
                      + (' | ' + '; '.join(row['problems']) if row['problems'] else ''))
        report['missions'][mission_id] = seams(solved, mission_id)
        for row in report['missions'][mission_id]:
            failed += bool(row['problems'])
            waived += bool(row.get('waived'))
            status = 'FAIL' if row['problems'] else 'WAIVED' if row.get('waived') else 'PASS'
            light = row.get('with_seam_light')
            print(f"SEAM {status} {mission_id} {row['connector']} -> {row['room']}"
                  + (' | ' + '; '.join(row['problems']) if row['problems'] else '')
                  + (' | waived: ' + '; '.join(row['waived']) if row.get('waived') else '')
                  + (f" | with the seam light: step {light['step']:+.2f}, saturation ratio {light['saturation_ratio']:.2f}"
                     if light and (row['problems'] or row.get('waived')) else ''))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('SITE7_PLATE_LIGHTING', 'FAIL' if failed else 'PASS',
          f'({failed} plates/seams off target' + (f', {waived} seams waived' if waived else '') + ')')
    raise SystemExit(1 if failed and args.strict else 0)


if __name__ == '__main__':
    main()
