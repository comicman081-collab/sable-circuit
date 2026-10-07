"""Summarise the rotated unmodified/fix census playthroughs, plus other playthrough samples.

usage: census_ab_summary.py CENSUS_AB_DIR OUT_JSON [LABEL=BUILD=DIR ...]
CENSUS_AB_DIR holds r<N>_<build>/opNN/ rounds (build head or fix). Each DIR holds opNN/ or
a regression run's full_op_0N/ with full_operation.json and, for census runs, contact_census.json.
"""
import json
import statistics
import sys
from pathlib import Path


def load(folder: Path, build: str, label: str, rows: list) -> None:
    for i in range(1, 6):
        op = folder / ('op0%d' % i)
        if not op.is_dir():
            op = folder / ('full_op_0%d' % i)
        full = op / 'full_operation.json'
        if not full.is_file():
            continue
        data = json.loads(full.read_text(encoding='utf-8'))
        result = data.get('result', {})
        row = {'build': build, 'sample': label, 'mission': 'MIS_CH01_0%d' % i,
               'outcome': result.get('outcome'), 'elapsed_s': round(float(result.get('elapsed_seconds', 0)), 1),
               'hostiles_defeated': result.get('hostiles_defeated'),
               'squad_damage_taken': round(sum(float(v) for v in data.get('damage_by_source', {}).values()), 1)}
        census = op / 'contact_census.json'
        if census.is_file():
            c = json.loads(census.read_text(encoding='utf-8'))
            row['floor_ticks'] = sum(r['floor_ticks'] for r in c['by_rider'].values())
            row['carried_px'] = round(sum(r['carried_px'] for r in c['by_rider'].values()), 2)
            row['applied_px'] = round(sum(r.get('applied_px', r['carried_px']) for r in c['by_rider'].values()), 2)
            row['max_step_px'] = max([r['max_step_px'] for r in c['by_rider'].values()] or [0.0])
            row['riders'] = sorted(c['by_rider'])
        rows.append(row)


def main() -> None:
    ab, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows = []
    for folder in sorted(p for p in ab.iterdir() if p.is_dir()):
        load(folder, folder.name.split('_', 1)[1], folder.name, rows)
    for extra in sys.argv[3:]:
        label, build, folder = extra.split('=', 2)
        load(Path(folder), build, label, rows)
    summary = {}
    for build in ('head', 'fix'):
        mine = [r for r in rows if r['build'] == build]
        extracted = [r for r in mine if r['outcome'] == 'EXTRACTED']
        per_op = {}
        for r in extracted:
            per_op.setdefault(r['mission'], []).append(r['squad_damage_taken'])
        summary[build] = {'runs': len(mine), 'extracted': len(extracted),
                          'not_extracted': [(r['sample'], r['mission'], r['outcome']) for r in mine if r['outcome'] != 'EXTRACTED'],
                          'damage_per_extracted_run_mean': round(statistics.mean(r['squad_damage_taken'] for r in extracted), 1) if extracted else None,
                          'damage_per_extracted_run_stdev': round(statistics.stdev(r['squad_damage_taken'] for r in extracted), 1) if len(extracted) > 1 else None,
                          'elapsed_s_mean': round(statistics.mean(r['elapsed_s'] for r in extracted), 1) if extracted else None,
                          'damage_by_mission': {m: sorted(v) for m, v in sorted(per_op.items())},
                          'census_floor_ticks': sum(r.get('floor_ticks', 0) for r in mine),
                          'census_carried_px': round(sum(r.get('carried_px', 0) for r in mine), 2),
                          'census_applied_px': round(sum(r.get('applied_px', 0) for r in mine), 2),
                          'census_max_step_px': max([r.get('max_step_px', 0) for r in mine] or [0])}
    out.write_text(json.dumps({'summary': summary, 'runs': rows}, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
