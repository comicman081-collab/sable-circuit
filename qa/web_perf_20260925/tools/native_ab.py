"""Same-session native A/B of the web-performance script changes with .cache/diag/perf_op1.gd.

Versions: 'old' = the changed scripts as committed at HEAD, 'new' = the working tree. Each
round runs both, order rotated, so machine-load drift spreads over both. The working copy
is restored byte for byte at the end. The first 5 s sample of each run (loading) is dropped.
usage: python native_ab.py <rounds> <out.json>
"""
from pathlib import Path
import json
import os
import re
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
FILES = ['scripts/combat/combat_hit_geometry.gd', 'scripts/combat/cover_navigation.gd',
         'scripts/missions/site7_environment_prop.gd', 'scripts/missions/site7_battlefield.gd',
         'scripts/animation/enemy_ground_shadow.gd', 'scripts/animation/operator_ground_shadow.gd',
         'scripts/ui/tactical_minimap.gd', 'scripts/ui/cinematic_field_overlay.gd', 'scripts/ui/story_stage_hud.gd',
         'scripts/animation/operator_visual.gd',
         'scripts/combat/prototype_projectile.gd']
ROUNDS = int(sys.argv[1])
OUT = Path(sys.argv[2])
LINE = re.compile(r'PERF t=\s*(\d+)s fps=\s*([\d.]+) process_ms=\s*([\d.]+) physics_ms=\s*([\d.]+).*hostiles=(\d+)')
working = {f: (ROOT / f).read_bytes() for f in FILES}
old = {f: subprocess.run(['git', 'show', f'HEAD:{f}'], cwd=ROOT, capture_output=True, check=True).stdout for f in FILES}
VERSIONS = {'old': old, 'new': working}
env = dict(os.environ, TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'))
rows = []


def put(files):
    for name, data in files.items():
        for attempt in range(20):
            try:
                (ROOT / name).write_bytes(data)
                break
            except OSError:
                time.sleep(0.5)


try:
    names = list(VERSIONS)
    for round_index in range(ROUNDS):
        order = names[round_index % len(names):] + names[:round_index % len(names)]
        for name in order:
            put(VERSIONS[name])
            text = subprocess.run([GODOT, '--path', str(ROOT), '-s', 'res://.cache/diag/perf_op1.gd'], cwd=ROOT, env=env,
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300).stdout
            samples = [(int(t), float(f), float(p), float(ph), int(h)) for t, f, p, ph, h in LINE.findall(text)]
            kept = [s for s in samples if s[0] > 5]
            errors = [l for l in text.splitlines() if 'SCRIPT ERROR' in l]
            row = {'version': name, 'round': round_index + 1, 'fps': [s[1] for s in kept],
                   'process_ms': [s[2] for s in kept], 'physics_ms': [s[3] for s in kept],
                   'hostiles': [s[4] for s in kept], 'script_errors': len(errors)}
            rows.append(row)
            print('RUN', json.dumps(row), flush=True)
finally:
    put(working)
    assert all((ROOT / f).read_bytes() == working[f] for f in FILES)
summary = {}
for name in VERSIONS:
    pick = lambda key: [v for r in rows if r['version'] == name for v in r[key]]
    fps = pick('fps')
    summary[name] = {'samples': len(fps), 'fps_median': statistics.median(fps) if fps else None,
                     'fps_mean': round(statistics.mean(fps), 1) if fps else None,
                     'fps_min': min(fps, default=None), 'fps_max': max(fps, default=None),
                     'physics_ms_median': statistics.median(pick('physics_ms')) if fps else None,
                     'process_ms_median': statistics.median(pick('process_ms')) if fps else None,
                     'script_errors': sum(r['script_errors'] for r in rows if r['version'] == name)}
OUT.write_text(json.dumps({'rounds': ROUNDS, 'files': FILES, 'runs': rows, 'summary': summary}, indent=2), encoding='utf-8')
print('SUMMARY', json.dumps(summary), flush=True)
print('RESTORED working copy', flush=True)
