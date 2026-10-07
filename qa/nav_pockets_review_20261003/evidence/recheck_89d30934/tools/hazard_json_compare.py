"""Claude review helper (N-1 re-check): what did Codex's B-4 repair change in the hazard_expansion result?

usage: hazard_json_compare.py <result json A> <result json B> [<result json C> ...]   (run from the project root)
Prints every leaf value that differs between A and each later file, the per-hazard control flags and the search limits that
decide which hazards the negative control can reach (the box half-size is 500 px).
"""
import json
import sys


def load(path):
    return json.load(open(path, encoding='utf-8'))


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + '/' + k, a.get(k), b.get(k)))
            else:
                walk(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + '[%d]' % i, out)
    elif a != b:
        out.append((path, a, b))


files = sys.argv[1:]
base = load(files[0])
print('A = %s: status %s, checks %s, hazards %d, standable spots %d, failed spots %d' % (
    files[0], base['status'], base['checks'], sum(len(r['hazard_escapes']) for r in base['rooms']),
    sum(r['standable_spots'] for r in base['rooms']), sum(r['failed_spots'] for r in base['rooms'])))
for other in files[1:]:
    data = load(other)
    out = []
    walk(base, data, '', out)
    print('\nB = %s: status %s; differing leaf values vs A: %d' % (other, data['status'], len(out)))
    for p, a, b in out[:40]:
        print('   %s : %s -> %s' % (p, a, b))
reach = {}
for room in base['rooms']:
    for h in room['hazard_escapes']:
        reach.setdefault((h['escape_kind'], round(h['search_span_px'])), []).append(room['room'].split()[-1] + ':' + h['hazard'])
print('\nsearch limit per hazard kind (px). A candidate point lies inside the 500 px box wherever the limit is below 500:')
for (kind, limit), names in sorted(reach.items(), key=lambda kv: kv[0][1]):
    print('   %-20s limit %5d px  hazards %2d  %s' % (kind, limit, len(names), 'inside the box -> the control never reaches _clear_ground' if limit < 500 else 'reaches past the box -> the control exercises _clear_ground'))
