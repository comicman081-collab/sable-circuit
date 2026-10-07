"""Trace every CoverNavigation plan in tests/render/site7_cover_ai_check.gd with the new scripts
and with HEAD. The same trace line is inserted into both versions of cover_navigation.gd;
everything is restored byte for byte at the end.
usage: python coverai_trace.py
"""
from pathlib import Path
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
FILES = ['scripts/combat/combat_hit_geometry.gd', 'scripts/combat/cover_navigation.gd',
         'scripts/missions/site7_environment_prop.gd', 'scripts/missions/site7_battlefield.gd']
NAV = 'scripts/combat/cover_navigation.gd'
ANCHOR = b'    var free_goal := _free_goal(actor,goal,obstacles)\n'
TRACE = (b'    print("NAVTRACE %s %s" % [actor.name, var_to_str([actor.global_position, goal, free_goal, obstacles])'
         b'.replace("\\n", " ")])\n')
working = {f: (ROOT / f).read_bytes() for f in FILES}
head = {f: subprocess.run(['git', 'show', f'HEAD:{f}'], cwd=ROOT, capture_output=True, check=True).stdout for f in FILES}
env = dict(os.environ, TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'))
OUT = ROOT / '.cache/coverai'
import sys
EXTRA = sys.argv[1:]  # e.g. --fixed-fps 60
SUFFIX = '_fixed' if EXTRA else ''
OUT.mkdir(parents=True, exist_ok=True)


def put(files):
    for name, data in files.items():
        for attempt in range(20):
            try:
                (ROOT / name).write_bytes(data)
                break
            except OSError:
                time.sleep(0.5)


def instrument(files):
    files = dict(files)
    nav = files[NAV]
    assert nav.count(ANCHOR) == 1
    files[NAV] = nav.replace(ANCHOR, ANCHOR + TRACE)
    return files


try:
    for label, files in (('new', working), ('old', head)):
        put(instrument(files))
        text = subprocess.run([GODOT, '--headless', *EXTRA, '--path', str(ROOT), '-s', 'res://tests/render/site7_cover_ai_check.gd',
                               '--', f'--out=res://.cache/coverai/trace_{label}{SUFFIX}'], cwd=ROOT, env=env, capture_output=True,
                              text=True, encoding='utf-8', errors='replace', timeout=400).stdout
        lines = [l for l in text.splitlines() if l.startswith('NAVTRACE') or l.startswith('SITE7_COVER_AI')]
        (OUT / f'trace_{label}{SUFFIX}.txt').write_text('\n'.join(lines), encoding='utf-8')
        print(label, len(lines), lines[-1] if lines else '')
finally:
    put(working)
    assert all((ROOT / f).read_bytes() == working[f] for f in FILES)
print('RESTORED working copy')
