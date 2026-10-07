"""Which change makes tests/render/site7_cover_ai_check.gd fail? Runs the test headless (as the
regression runner does) with variants of the changed scripts: all new, all HEAD, and all new
but one file at HEAD. The working copy is restored byte for byte at the end.
usage: python coverai_bisect.py <repeats> <variant> [<variant> ...]
variants: new, old, or old:<path> (that one file at HEAD, rest new)
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
FILES = ['scripts/combat/combat_hit_geometry.gd', 'scripts/combat/cover_navigation.gd',
         'scripts/missions/site7_environment_prop.gd', 'scripts/missions/site7_battlefield.gd',
         'scripts/animation/enemy_ground_shadow.gd', 'scripts/animation/operator_ground_shadow.gd',
         'scripts/ui/tactical_minimap.gd', 'scripts/ui/cinematic_field_overlay.gd', 'scripts/ui/story_stage_hud.gd',
         'scripts/animation/operator_visual.gd', 'scripts/combat/prototype_projectile.gd']
REPEATS = int(sys.argv[1])
VARIANTS = sys.argv[2:]
working = {f: (ROOT / f).read_bytes() for f in FILES}
head = {f: subprocess.run(['git', 'show', f'HEAD:{f}'], cwd=ROOT, capture_output=True, check=True).stdout for f in FILES}
env = dict(os.environ, TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'))
EXTRA = os.environ.get('SABLE_EXTRA', '').split()
OUT = ROOT / '.cache/coverai'


def put(files):
    for name, data in files.items():
        for attempt in range(20):
            try:
                (ROOT / name).write_bytes(data)
                break
            except OSError:
                time.sleep(0.5)


def files_for(variant):
    if variant == 'new':
        return dict(working)
    if variant == 'old':
        return dict(head)
    if variant.startswith('old:'):
        files = dict(working)
        files[variant[4:]] = head[variant[4:]]
        return files
    raise SystemExit('unknown variant ' + variant)


results = []
try:
    for repeat in range(REPEATS):
        for variant in VARIANTS:
            put(files_for(variant))
            tag = f"{variant.replace(':', '_').replace('/', '_')}_{repeat + 1}{'_fixed' if EXTRA else ''}"
            out = OUT / tag
            out.mkdir(parents=True, exist_ok=True)
            text = subprocess.run([GODOT, '--headless', *EXTRA, '--path', str(ROOT), '-s', 'res://tests/render/site7_cover_ai_check.gd',
                                   '--', f'--out=res://.cache/coverai/{tag}'], cwd=ROOT, env=env, capture_output=True,
                                  text=True, encoding='utf-8', errors='replace', timeout=400).stdout
            status = next((l for l in text.splitlines() if l.startswith('SITE7_COVER_AI')), 'NO RESULT')
            check = out / 'check.json'
            obs = []
            if check.exists():
                data = json.loads(check.read_text(encoding='utf-8'))
                obs = [(o['hz'], round(o['end_distance'], 1), round(o['side_travel'], 1)) for o in data['observations'] if o['kind'] == 'follower_path']
                fails = data['failures']
            else:
                fails = []
            row = {'variant': variant, 'repeat': repeat + 1, 'status': status, 'follower': obs, 'failures': fails}
            results.append(row)
            print('RUN', json.dumps(row), flush=True)
finally:
    put(working)
    assert all((ROOT / f).read_bytes() == working[f] for f in FILES)
(OUT / 'bisect.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print('RESTORED working copy', flush=True)
