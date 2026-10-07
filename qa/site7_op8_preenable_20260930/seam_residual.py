"""Scratch: seam mismatch of every mission-8 seam (and, for reference, missions 1-7) before and after the shipped
runtime seam light (data/visual/site7_seam_light.json), using the audit's own colour statistics and the layout tool's
apply_light (the Python twin of the plate shader).

Usage: python -B .cache/claude_scratch/seam_residual.py [MIS_CH01_08 ...] --out <json>
"""
import base64
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load_module('plate_audit', 'tools/environment/audit_site7_plate_lighting.py')
wl = audit.wl


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('missions', nargs='*')
    parser.add_argument('--out', type=Path)
    parsed = parser.parse_args()
    args, out = parsed.missions, parsed.out
    art, layouts, floors = wl.load(wl.ART), wl.load(wl.LAYOUTS), wl.load(wl.PLATE_FLOORS)['plates']
    shipped = json.loads((ROOT / 'data/visual/site7_seam_light.json').read_text(encoding='utf-8'))
    columns, rows_n = shipped['grid']
    result = {}
    for mission_id in args or ['MIS_CH01_08']:
        solved = wl.solve(mission_id, art, layouts, floors)
        rows = []
        for index, a, b in solved['links']:
            conn = solved['connectors'][index]
            encoded = shipped['missions'][mission_id].get(f'C{index}')
            light = None
            if encoded:
                grid = np.frombuffer(base64.b64decode(encoded), np.uint8).reshape(rows_n, columns, 2)
                light = wl.decode_light(grid)
            u, v = wl.light_cells(conn)
            xs, ys = wl.texture_to_world(conn, u, v)
            on_deck = wl.points_inside(conn.floor_world(), xs, ys)
            deck, deck_cover = wl.sample_blurred(conn, *wl.texture_to_world(conn, *wl.visible_along_deck(conn, u, v)))
            for room_id in (a, b):
                room = solved['rooms'][room_id]
                floor, floor_cover = wl.sample_blurred(room, xs, ys)
                known = on_deck & wl.points_inside(room.floor_world(), xs, ys) & (deck_cover > 0.5) & (floor_cover > 0.5)
                if not known.sum():
                    continue
                dl, ds, dh = audit.colour_stats(deck[known].mean(0))
                rl, rs, rh = audit.colour_stats(floor[known].mean(0))
                eps = wl.LIGHT_EPSILON
                row = {'connector': f'C{index}', 'plate': Path(conn.asset).stem.replace('_GAME', ''), 'room': room_id,
                       'raw_step': math.log2((rl + eps) / (dl + eps)),
                       'raw_sat_ratio': (max(ds, rs) + eps) / (min(ds, rs) + eps),
                       'deck_saturation': ds, 'room_saturation': rs, 'raw_hue_gap': audit.hue_gap(dh, rh)}
                if light is not None:
                    lit = wl.apply_light(deck[known], light[known])
                    ll, ls, lh = audit.colour_stats(lit.mean(0))
                    row.update(lit_step=math.log2((rl + eps) / (ll + eps)),
                               lit_sat_ratio=(max(ls, rs) + eps) / (min(ls, rs) + eps),
                               lit_deck_saturation=ls, lit_hue_gap=audit.hue_gap(lh, rh))
                rows.append(row)
        result[mission_id] = rows
        for row in rows:
            tail = ''
            if 'lit_step' in row:
                tail = f" | after seam light: step {row['lit_step']:+.3f} sat x{row['lit_sat_ratio']:.2f} (deck sat {row['lit_deck_saturation']:.3f})"
            print(f"{mission_id} {row['plate']:7s} {row['room']:15s} raw step {row['raw_step']:+.3f} sat x{row['raw_sat_ratio']:.2f}{tail}")
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
