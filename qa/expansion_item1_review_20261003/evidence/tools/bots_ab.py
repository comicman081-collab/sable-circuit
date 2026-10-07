"""Claude review instrument (V-33): paired, interleaved bot playthroughs of operations 6-10 on the baseline and the reviewed snapshot.
Both snapshots hold the same fail-fast stall detector (patch_bot.py). One JSON line per run goes to bots_ab.jsonl."""
import json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAP = ROOT / '.cache' / 'claude_scratch'
LOG = SNAP / 'item1_review' / 'bots_ab.jsonl'
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
BUILDS = {'base': SNAP / 'proj_base', 'after': SNAP / 'proj_after'}

def run(build: str, op: int, pair: int, timeout=1000):
    proj = BUILDS[build]
    env = dict(os.environ)
    for k, sub in (('TMP', 'tmp'), ('TEMP', 'tmp'), ('TMPDIR', 'tmp'), ('APPDATA', 'godot_appdata'), ('LOCALAPPDATA', 'godot_localappdata')):
        d = proj / '.cache' / sub; d.mkdir(parents=True, exist_ok=True); env[k] = str(d)
    out_res = f'res://.cache/bot_out/{build}_{op:02d}_{pair}'
    cmd = [GODOT, '--headless', '--path', str(proj), '-s', 'res://tests/smoke/site7_full_operation_smoke.gd', '--',
           f'--mission=MIS_CH01_{op:02d}', f'--out={out_res}']
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=proj, capture_output=True, timeout=timeout, env=env)
        text = (p.stdout + p.stderr).decode('utf-8', 'replace'); code = p.returncode
    except subprocess.TimeoutExpired as e:
        text = 'TIMEOUT ' + ((e.stdout or b'') + (e.stderr or b'')).decode('utf-8', 'replace'); code = 124
    wall = time.time() - t0
    row = {'build': build, 'op': op, 'pair': pair, 'exit': code, 'wall_s': round(wall, 1)}
    row['stall'] = bool(re.search(r'NAV_ZERO_STALL', text))
    m = re.search(r'NAV_ZERO_STALL tick=(\d+) step=(\d+) pos=\(([-\d.]+), ([-\d.]+)\)', text)
    if m: row['stall_at'] = {'tick': int(m.group(1)), 'step': int(m.group(2)), 'pos': [float(m.group(3)), float(m.group(4))]}
    row['smoke'] = 'PASS' if 'SITE7_FULL_OPERATION_SMOKE: PASS' in text else ('FAIL' if 'SITE7_FULL_OPERATION_SMOKE: FAIL' in text else 'NONE')
    jpath = proj / '.cache' / 'bot_out' / f'{build}_{op:02d}_{pair}' / 'full_operation.json'
    if jpath.exists():
        d = json.loads(jpath.read_text(encoding='utf-8'))
        r = d.get('result', {}) or {}
        row['outcome'] = r.get('outcome', '')
        row['hostiles_defeated'] = r.get('hostiles_defeated')
        row['failures'] = d.get('failures', [])
        dmg = d.get('damage_by_source', {}) or {}
        row['damage_total'] = round(sum(float(v) for v in dmg.values()), 1)
        by_room = {}
        for k, v in dmg.items():
            step = k.split(':')[0]; by_room[step] = round(by_room.get(step, 0.0) + float(v), 1)
        row['damage_by_step'] = by_room
        hz = {k.split(':', 2)[2]: round(float(v), 1) for k, v in dmg.items() if ':HAZARD_' in k or k.split(':', 2)[-1].startswith('HAZARD')}
        row['damage_hazard'] = hz
        tr = d.get('trace', [])
        row['last_trace_tick'] = tr[-1]['tick'] if tr else None
        row['steps_reached'] = max([t['step'] for t in tr]) if tr else None
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as f: f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row

if __name__ == '__main__':
    ops = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '9,6,7,10,8').split(',')]
    pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for pair in range(1, pairs + 1):
        for op in ops:
            order = ('base', 'after') if (pair + op) % 2 == 1 else ('after', 'base')
            for build in order: run(build, op, pair)
    print('BOTS_AB_DONE', flush=True)
