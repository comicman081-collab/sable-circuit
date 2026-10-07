"""Redraw census (.cache/diag/redraw_census.gd) with the changed scripts at HEAD ('old') and
in the working tree ('new'). The working copy is restored byte for byte.
usage: python census_ab.py <out.json>
"""
from pathlib import Path
import json
import os
import re
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
OUT = Path(sys.argv[1])
working = {f: (ROOT / f).read_bytes() for f in FILES}
old = {f: subprocess.run(['git', 'show', f'HEAD:{f}'], cwd=ROOT, capture_output=True, check=True).stdout for f in FILES}
env = dict(os.environ, TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'))
report = {}


def put(files):
    for name, data in files.items():
        for attempt in range(20):
            try:
                (ROOT / name).write_bytes(data)
                break
            except OSError:
                time.sleep(0.5)


try:
    for name, files in (('old', old), ('new', working)):
        put(files)
        text = subprocess.run([GODOT, '--path', str(ROOT), '-s', 'res://.cache/diag/redraw_census.gd'], cwd=ROOT, env=env,
                              capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300).stdout
        head = re.search(r'CENSUS frames=(\d+) redraws_per_frame=([\d.]+) hostiles=(\d+)', text)
        rows = [{'script': m[0], 'per_frame': float(m[1]), 'nodes': int(m[2])}
                for m in re.findall(r'CENSUS_ROW (\S+)\s+([\d.]+) per frame  nodes=(\d+)', text)]
        report[name] = {'frames': int(head[1]), 'redraws_per_frame': float(head[2]), 'hostiles': int(head[3]),
                        'rows': rows, 'script_errors': text.count('SCRIPT ERROR')} if head else {'raw_tail': text[-3000:]}
        print(name, json.dumps(report[name])[:1500], flush=True)
finally:
    put(working)
    assert all((ROOT / f).read_bytes() == working[f] for f in FILES)
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('RESTORED working copy', flush=True)
