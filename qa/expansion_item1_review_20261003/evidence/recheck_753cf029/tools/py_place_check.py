"""Claude review instrument (V-30 / B-2 re-check): run Codex's tests/test_expansion_item1_placement.py (as committed in 753cf029)
on scratch copies of the mission data with legitimate later edits, real violations and other commit pairs.
Git is only read (GIT_DIR points at the real repository; nothing in the repository or its working tree is written).
usage: py_place_check.py [commit]   -> prints one line per case, writes py_place_results.json next to this file"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
COMMIT = sys.argv[1] if len(sys.argv) > 1 else '753cf029'
WORK = ROOT / '.cache' / 'claude_scratch' / 'py_place'
GIT_DIR = ROOT / '.git'


def git_text(path: str) -> str:
    return subprocess.run(['git', f'--git-dir={GIT_DIR}', 'show', f'{COMMIT}:{path}'], capture_output=True, check=True).stdout.decode('utf-8-sig')


def fresh_case(name: str) -> Path:
    d = WORK / name
    if d.exists():
        shutil.rmtree(d)
    (d / 'tests').mkdir(parents=True)
    (d / 'data' / 'missions').mkdir(parents=True)
    (d / 'data' / 'progression').mkdir(parents=True)
    (d / 'tests' / 'test_expansion_item1_placement.py').write_text(git_text('tests/test_expansion_item1_placement.py'), encoding='utf-8')
    for n in range(1, 11):
        (d / 'data' / 'missions' / f'MIS_CH01_{n:02d}.json').write_text(git_text(f'data/missions/MIS_CH01_{n:02d}.json'), encoding='utf-8')
    for f in ('zone_hazards.json', 'elite_affixes.json'):
        (d / 'data' / 'progression' / f).write_text(git_text(f'data/progression/{f}'), encoding='utf-8')
    return d


def load(d: Path, n: int):
    p = d / 'data' / 'missions' / f'MIS_CH01_{n:02d}.json'
    return p, json.loads(p.read_text(encoding='utf-8'))


def save(p: Path, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def affix_rows(v):
    out = []
    if isinstance(v, dict):
        if 'enemy_id' in v and 'affix' in v:
            out.append(v)
        for c in v.values():
            out += affix_rows(c)
    elif isinstance(v, list):
        for c in v:
            out += affix_rows(c)
    return out


def boss_room(m):
    return next(r for r in m['main_route'] if r['type'] == 'BOSS')


def edit_op3_health(d):
    p, m = load(d, 3)
    affix_rows(m)[0]['health'] += 1
    save(p, m)


def edit_op1_row(d):
    p, m = load(d, 1)
    for room in m['main_route']:
        for row in room.get('encounter', []):
            if 'health' in row:
                row['health'] += 1
                save(p, m)
                return
    raise SystemExit('no health row in op 1')


def edit_assets(d):
    (d / 'assets').mkdir()
    (d / 'assets' / 'legit_future.txt').write_text('x')
    (d / 'art_src').mkdir()
    (d / 'art_src' / 'new_plate.png').write_bytes(b'x')


def edit_op10_hazard(d):
    p, m = load(d, 10)
    room = next(r for r in m['main_route'] if r['type'] != 'BOSS' and r.get('hazards'))
    room['hazards'][0] = {'type': 'SPORE_CLOUD', 'count': 3}
    save(p, m)


def bad_boss_affix(d):
    p, m = load(d, 6)
    next(r for r in boss_room(m)['encounter'] if r['enemy_id'].startswith('BOSS_'))['affix'] = 'BEACON'
    save(p, m)


def bad_unknown_hazard(d):
    p, m = load(d, 7)
    room = next(r for r in m['main_route'] if r.get('hazards'))
    room['hazards'][0]['type'] = 'NO_SUCH_HAZARD'
    save(p, m)


def bad_boss_room_hazard(d):
    p, m = load(d, 8)
    boss_room(m)['hazards'] = [{'type': 'ARC_VENT', 'count': 1}]
    save(p, m)


def bad_zero_count(d):
    p, m = load(d, 9)
    room = next(r for r in m['main_route'] if r.get('hazards'))
    room['hazards'][0]['count'] = 0
    save(p, m)


def bad_unknown_affix(d):
    p, m = load(d, 9)
    affix_rows(m)[0]['affix'] = 'NO_SUCH_AFFIX'
    save(p, m)


def set_pair(commit):
    def f(d):
        t = d / 'tests' / 'test_expansion_item1_placement.py'
        s = t.read_text(encoding='utf-8')
        s2 = re.sub(r'PLACEMENT_COMMIT = "[^"]*"', f'PLACEMENT_COMMIT = "{commit}"', s, count=1)
        assert s2 != s
        t.write_text(s2, encoding='utf-8')
    return f


CASES = [
    # name, edit, expectation
    ('baseline', None, 'OK'),
    ('legit_op3_elite_health_plus1', edit_op3_health, 'OK'),
    ('legit_op1_row_health_plus1', edit_op1_row, 'OK'),
    ('legit_assets_and_art_src_added', edit_assets, 'OK'),
    ('legit_op10_themed_hazard', edit_op10_hazard, 'OK'),
    ('bad_current_boss_affix_on_disk', bad_boss_affix, 'FAIL'),
    ('bad_current_unknown_hazard_on_disk', bad_unknown_hazard, 'FAIL'),
    ('bad_current_boss_room_hazard_on_disk', bad_boss_room_hazard, 'FAIL'),
    ('bad_current_zero_count_on_disk', bad_zero_count, 'FAIL'),
    ('bad_current_unknown_affix_on_disk', bad_unknown_affix, 'FAIL'),
    ('bad_pair_hazard_code_commit_50a9dc9b', set_pair('50a9dc9b'), 'FAIL'),
    ('bad_pair_plates_commit_f2462d2e', set_pair('f2462d2e'), 'FAIL'),
    ('bad_pair_visual_commit_6b0e3eb2', set_pair('6b0e3eb2'), 'FAIL'),
    ('missing_history_skips_only_pair_class', set_pair('0' * 40), 'OK+SKIP'),
]


def main():
    env = dict(os.environ)
    env['GIT_DIR'] = str(GIT_DIR)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    results = []
    for name, edit, expect in CASES:
        d = fresh_case(name)
        if edit:
            edit(d)
        p = subprocess.run([sys.executable, '-B', str(d / 'tests' / 'test_expansion_item1_placement.py')], cwd=d, env=env,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        text = p.stdout + p.stderr
        ran = re.search(r'Ran (\d+) tests?', text)
        verdict = 'OK' if p.returncode == 0 else 'FAIL'
        skipped = re.search(r'skipped=(\d+)', text)
        failed_names = sorted(set(re.findall(r'^(?:FAIL|ERROR): (\w+) \(', text, re.M)))
        skip_reason = ''
        m = re.search(r'placement commit pair unavailable[^\n]*', text)
        if m:
            skip_reason = m.group(0)[:140]
        got = verdict + ('+SKIP' if (skipped and verdict == 'OK') else '')
        row = {'case': name, 'expect': expect, 'got': got, 'match': got == expect, 'exit': p.returncode,
               'ran': int(ran.group(1)) if ran else None, 'skipped': int(skipped.group(1)) if skipped else 0,
               'failed_tests': failed_names, 'skip_reason': skip_reason}
        results.append(row)
        print(f"{name:42s} expect={expect:8s} got={got:8s} {'OK ' if row['match'] else 'MISMATCH'} ran={row['ran']} skipped={row['skipped']} {failed_names or ''} {skip_reason}", flush=True)
        shutil.rmtree(d)
    (HERE / 'py_place_results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    bad = [r for r in results if not r['match']]
    print('MISMATCHES:', [r['case'] for r in bad] if bad else 'none')
    shutil.rmtree(WORK, ignore_errors=True)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
