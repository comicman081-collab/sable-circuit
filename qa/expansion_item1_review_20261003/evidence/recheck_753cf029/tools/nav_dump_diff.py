"""Claude review instrument (N-1 differential): compare two nav_direction_dump.gd CSV files cell by cell.
usage: nav_dump_diff.py <before.csv> <after.csv> [--json out.json]

Reports, per room and in total: cells, identical vectors, cells that were dead and now route (the fix), cells that were
routing and are now dead (a regression), and cells whose direction changed (max / mean turn in degrees, count over 1 / 5 / 20 degrees).
A fix that only repairs dead cells shows zero changed routing cells; a larger set shows how far the change reaches."""
import json, math, sys
from collections import defaultdict


def read(path):
    rows = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            mission, room, step, x, y, dx, dy = line.split(',')
            rows[(mission, room, int(step), x, y)] = (float(dx), float(dy))
    return rows


def angle(a, b):
    la, lb = math.hypot(*a), math.hypot(*b)
    if la < 1e-6 or lb < 1e-6:
        return None
    c = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (la * lb)))
    return math.degrees(math.acos(c))


def main():
    before, after = read(sys.argv[1]), read(sys.argv[2])
    out_json = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    only_b = [k for k in before if k not in after]
    only_a = [k for k in after if k not in before]
    rooms = defaultdict(lambda: {'cells': 0, 'identical': 0, 'fixed': 0, 'broken': 0, 'changed': 0, 'turns': []})
    changed_samples = []
    for k, vb in before.items():
        if k not in after:
            continue
        va = after[k]
        r = rooms[(k[0], k[1])]
        r['cells'] += 1
        db, da = math.hypot(*vb) < 0.01, math.hypot(*va) < 0.01
        if db and da:
            r['identical'] += 1            # dead both times: counted as not fixed below
            r.setdefault('still_dead', 0)
            r['still_dead'] += 1
        elif db and not da:
            r['fixed'] += 1
        elif da and not db:
            r['broken'] += 1
        elif abs(vb[0] - va[0]) < 1e-4 and abs(vb[1] - va[1]) < 1e-4:
            r['identical'] += 1
        else:
            r['changed'] += 1
            t = angle(vb, va)
            r['turns'].append(t if t is not None else 0.0)
            if len(changed_samples) < 12:
                changed_samples.append({'cell': list(k), 'before': vb, 'after': va, 'turn_deg': round(t or 0.0, 2)})
    tot = {'cells': 0, 'identical': 0, 'fixed': 0, 'broken': 0, 'changed': 0, 'still_dead': 0}
    allturns = []
    per_room = []
    for (mission, room), r in sorted(rooms.items()):
        for key in tot:
            tot[key] += r.get(key, 0)
        allturns += r['turns']
        if r['fixed'] or r['broken'] or r['changed'] or r.get('still_dead'):
            per_room.append({'mission': mission, 'room': room, **{k: r.get(k, 0) for k in ('cells', 'fixed', 'broken', 'changed', 'still_dead')},
                             'max_turn_deg': round(max(r['turns']), 2) if r['turns'] else 0.0})
    summary = {'before_rows': len(before), 'after_rows': len(after), 'only_in_before': len(only_b), 'only_in_after': len(only_a), 'total': tot,
               'changed_turn_deg': {'max': round(max(allturns), 2) if allturns else 0.0, 'mean': round(sum(allturns) / len(allturns), 2) if allturns else 0.0,
                                    'over_1': sum(1 for t in allturns if t > 1), 'over_5': sum(1 for t in allturns if t > 5), 'over_20': sum(1 for t in allturns if t > 20)},
               'rooms_with_any_difference': per_room, 'changed_samples': changed_samples}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if out_json:
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    sys.exit(1 if (tot['broken'] or only_b or only_a) else 0)


if __name__ == '__main__':
    main()
