"""Claude review instrument (V-30/V-31/V-32): compare the mission JSON of the placement commit with the baseline."""
import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE, HEAD = 'dca7ef20', sys.argv[1] if len(sys.argv) > 1 else 'a6eb1d35'

def load(rev, mid):
    p = subprocess.run(['git', 'show', f'{rev}:data/missions/MIS_CH01_{mid:02d}.json'], capture_output=True)
    return json.loads(p.stdout.decode('utf-8')) if p.returncode == 0 else None

def walk(a, b, path, out):
    if type(a) != type(b):
        out.append((path, a, b)); return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append((path + '/' + k, '<absent>', b[k]))
            elif k not in b: out.append((path + '/' + k, a[k], '<absent>'))
            else: walk(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path + '[len]', len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f'{path}[{i}]', out)
    elif a != b:
        out.append((path, a, b))

def hazard_total(m):
    n = 0; rows = {}
    for room in m.get('rooms', m.get('main_route', [])):
        h = room.get('hazards', [])
        rows[room.get('id')] = h
        n += sum(int(x.get('count', 1)) for x in h)
    return n, rows

def affix_rows(m):
    rows = []
    for room in m.get('rooms', m.get('main_route', [])):
        for wave_name, waves in (('encounter', [room.get('encounter', [])]), ('reinforcements', room.get('reinforcements', []))):
            for wi, wave in enumerate(waves):
                for ei, e in enumerate(wave):
                    if e.get('affix'): rows.append((room.get('id'), wave_name, wi, ei, e.get('enemy_id'), e.get('affix')))
    return rows

for mid in range(1, 11):
    a, b = load(BASE, mid), load(HEAD, mid)
    if a is None or b is None: print(mid, 'missing'); continue
    diffs = []
    walk(a, b, '', diffs)
    keys = sorted({d[0].split('/')[-1].split('[')[0] if not d[0].endswith(']') else d[0] for d in diffs})
    other = [d for d in diffs if not any(t in d[0] for t in ('/hazards', '/affix'))]
    ha, hb = hazard_total(a), hazard_total(b)
    print(f'--- MIS_CH01_{mid:02d}: changed paths {len(diffs)}, outside hazards/affix: {len(other)}; hazards {ha[0]} -> {hb[0]}; affix rows {len(affix_rows(a))} -> {len(affix_rows(b))}')
    for d in other[:6]: print('   OTHER', d)
    for room in sorted(set(ha[1]) | set(hb[1])):
        x, y = ha[1].get(room, []), hb[1].get(room, [])
        if x != y:
            print(f'   {room} hazards: {[(h.get("id"), h.get("count", 1)) for h in x]} -> {[(h.get("id"), h.get("count", 1)) for h in y]}')
    ra, rb = affix_rows(a), affix_rows(b)
    if ra != rb:
        print('   affix before:', ra); print('   affix after: ', rb)
