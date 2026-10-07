"""Compare regression runs (and extra playthrough samples) test by test.

usage: compare_runs.py OUT_JSON LABEL=RUN_DIR [LABEL=RUN_DIR ...] [--ops LABEL=DIR_WITH_opNN/full_operation.json ...]
"""
import json
import sys
from pathlib import Path


def playthrough(path: Path) -> dict:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    result = data.get('result', {})
    trace = data.get('trace', [])
    damage = sum(float(v) for v in data.get('damage_by_source', {}).values())
    return {'status': data.get('status'), 'outcome': result.get('outcome'),
            'elapsed_s': round(float(result.get('elapsed_seconds', 0.0)), 1),
            'hostiles_defeated': result.get('hostiles_defeated'),
            'squad_damage_taken': round(damage, 1),
            'attacks': len(data.get('attacks', [])), 'shots': len(data.get('emissions', [])),
            'cover_flank_plans': data.get('cover_flank_plans'),
            'skill_casts': sum(int(v) for v in data.get('skill_casts', {}).values()),
            'last_trace_tick': trace[-1]['tick'] if trace else None}


def main() -> None:
    out = Path(sys.argv[1])
    runs, ops = {}, {}
    target = runs
    for arg in sys.argv[2:]:
        if arg == '--ops':
            target = ops
            continue
        label, _, folder = arg.partition('=')
        target[label] = Path(folder)
    report = {'suites': {}, 'playthroughs': {}}
    for label, folder in runs.items():
        summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
        report['suites'][label] = {'run': folder.name, 'git_head': summary['git_head'][:10], 'git_dirty': summary['git_dirty'],
                                   'overall': summary['overall'], 'seconds': summary.get('seconds'),
                                   'guard': summary['guard'],
                                   'tests': {r['test']: {'status': r['status'], 'checks': r['checks'], 'seconds': r['seconds']}
                                             for r in summary['results']}}
        for i in range(1, 6):
            row = playthrough(folder / 'out' / ('full_op_0%d' % i) / 'full_operation.json')
            if row:
                report['playthroughs'].setdefault('MIS_CH01_0%d' % i, {})[label] = row
        nav = folder / 'out' / 'enemy_cover_nav' / 'check.json'
        if nav.is_file():
            cases = json.loads(nav.read_text(encoding='utf-8'))['cases']
            report.setdefault('enemy_cover_nav', {})[label] = {c['case']: {k: c.get(k) for k in (
                'end', 'path_length', 'reached_attack_lane', 'seconds', 'downed', 'longest_reposition_still_seconds')} for c in cases}
        cover = folder / 'out' / 'cover_ai' / 'check.json'
        if cover.is_file():
            report.setdefault('cover_ai', {})[label] = json.loads(cover.read_text(encoding='utf-8'))['observations']
    for label, folder in ops.items():
        for i in range(1, 6):
            row = playthrough(folder / ('op0%d' % i) / 'full_operation.json')
            if row:
                report['playthroughs'].setdefault('MIS_CH01_0%d' % i, {})[label] = row
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding='utf-8')
    labels = list(runs)
    names = []
    for label in labels:
        for name in report['suites'][label]['tests']:
            if name not in names:
                names.append(name)
    print('%-20s' % 'test' + ''.join('%-24s' % l for l in labels))
    for name in names:
        cells = []
        for label in labels:
            t = report['suites'][label]['tests'].get(name)
            cells.append('%-24s' % ('-' if t is None else '%s %s' % (t['status'], t['checks'] if t['checks'] is not None else '')))
        print('%-20s' % name + ''.join(cells))
    for section in ('enemy_cover_nav', 'cover_ai'):
        data = report.get(section, {})
        if len(data) >= 2:
            ref_label, ref = next(iter(data.items()))
            for label, rows in list(data.items())[1:]:
                same = rows == ref
                print('%s: %s vs %s -> %s' % (section, label, ref_label, 'IDENTICAL' if same else 'DIFFERENT'))
                if not same and section == 'enemy_cover_nav':
                    for case, row in rows.items():
                        if ref.get(case) != row:
                            print('   ', case)
                            print('        %-10s' % ref_label, ref.get(case))
                            print('        %-10s' % label, row)
                elif not same:
                    print('        %-10s' % ref_label, ref)
                    print('        %-10s' % label, rows)
    keys = ['outcome', 'elapsed_s', 'hostiles_defeated', 'squad_damage_taken', 'attacks', 'shots', 'cover_flank_plans', 'skill_casts']
    for mission, rows in report['playthroughs'].items():
        print(mission)
        for label, row in rows.items():
            print('   %-14s ' % label + '  '.join('%s=%s' % (k, row.get(k)) for k in keys))


if __name__ == '__main__':
    main()
