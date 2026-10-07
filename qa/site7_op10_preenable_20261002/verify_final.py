"""Final-state independent check of the committed operation 10 plates (tip e2ca52ed), 2026-10-02.
Reads: art_src/environments/site7_v2/stage10/<ID>/measurements_registered.json (Codex's committed record), the RAW/MASTER/GAME files,
data/visual/site7_plate_floors.json (what the game walks on). Writes only .cache/claude_scratch/s10_g/verify_final.json.
usage (repo root): python .cache/claude_scratch/s10_g/verify_final.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, 'tools/environment')
sys.path.insert(0, '.cache/claude_scratch/s10_f')
import verify_late as V

ART, GAME = V.ART, V.GAME
IDS = ['S10_R01', 'S10_R02', 'S10_R03', 'S10_R04', 'S10_R05', 'S10_R06', 'S10_C01', 'S10_C02', 'S10_C03', 'S10_C04', 'S10_C05', 'S10_C06', 'S10_C07', 'S10_O01', 'S10_O02']
ROOM = (1672, 941)
CONN = (1774, 887)
OUT = Path('.cache/claude_scratch/s10_g/verify_final.json')
EPS = 1e-6


def spec_for(pid):
    if pid.endswith(('_C06', '_C07')):
        return (1254, 1254)
    return CONN if ('_C' in pid or pid == 'S10_R04') else ROOM


def main():
    floors = json.loads(Path('data/visual/site7_plate_floors.json').read_text(encoding='utf-8'))
    table = floors.get('plates') or floors
    res, bad = [], []
    for pid in IDS:
        d = ART / 'stage10' / pid
        m = json.loads((d / 'measurements_registered.json').read_text(encoding='utf-8'))
        raw, mas = str(d / f'{pid}_RAW_NATIVE.png'), str(d / f'{pid}_MASTER.png')
        game = str(GAME / 'stage10' / pid / f'{pid}_GAME.png')
        r = {'plate': pid, 'verdict': m.get('status', 'ADOPTED'), 'floor': m['actual_floor_px'], 'doors': m.get('doors_px') or {},
             'rec': {k: m[k] for k in ('axis', 'luma', 'p10', 'p90', 'saturation')}, 'margin': m.get('margin_acceptance'),
             'factor': m['game_exposure_factor_srgb'], 'native': tuple(m['native_size']), 'attempt': m.get('attempt', 0),
             'raw': (raw, m['raw_sha256']), 'master': (mas, m['master_sha256']), 'game': (game, m['game_sha256'])}
        row = V.check(r, spec_for(pid))
        # the wired floor in site7_plate_floors.json must be the recorded one
        key = Path(game).as_posix()
        wired = table.get(key)
        w, h = r['native']
        row['wired_row'] = wired is not None
        if wired is not None:
            rec_floor = [[x / w, y / h] for x, y in r['floor']]
            wf = wired['floor']
            row['wired_floor_equals_record'] = len(wf) == len(rec_floor) and all(abs(a[0] - b[0]) < 2e-4 and abs(a[1] - b[1]) < 2e-4 for a, b in zip(wf, rec_floor))
            row['wired_doors'] = sorted((wired.get('doors') or {}).keys())
            row['record_doors'] = sorted(r['doors'].keys())
        res.append(row)
        probs = []
        if not row.get('files_exist'): probs.append('files missing')
        elif not (all(row['sha_ok']) and row['raw_equals_master'] and row['size_within_2px'] and row['lut_max_diff'] == 0 and row['import_exists']):
            probs.append('hash/size/lut/import')
        if row.get('files_exist') and not row['floor_matches_record']: probs.append('floor numbers differ from record')
        if row.get('files_exist') and row['problems_mine']: probs.append(f"mine {row['problems_mine']}")
        if not row['wired_row']: probs.append('no wired floor row')
        elif not row['wired_floor_equals_record']: probs.append('wired floor != record')
        elif row['wired_doors'] != row['record_doors']: probs.append(f"doors {row['wired_doors']} vs {row['record_doors']}")
        if probs:
            bad.append((pid, probs))
        f = row.get('floor', {})
        print(f"{pid} sha {all(row.get('sha_ok', [False]))} raw=master {row.get('raw_equals_master')} {row.get('mode')} {row.get('size')} lut {row.get('lut_max_diff')} imp {row.get('import_exists')} | "
              f"axis {f.get('axis', 0):.2f} luma {f.get('luma', 0):.3f} sat {f.get('saturation', 0):.3f} recmatch {row.get('floor_matches_record')} wired {row.get('wired_floor_equals_record')} | {probs or 'OK'}")
        if 'main_margins_pct' in row:
            print(f"     main m% {row['main_margins_pct']} whole m% {row['whole_margins_pct']} main area {row['main_area_px2']} aprons {row['apron_stats_mine']}")
        elif 'ends' in row:
            print(f"     L10 sat {row['ends']['L10']['saturation']} R10 sat {row['ends']['R10']['saturation']} deck perp width {row.get('deck_perp_width')}")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
    print('PROBLEMS:', bad or 'none')


if __name__ == '__main__':
    main()
