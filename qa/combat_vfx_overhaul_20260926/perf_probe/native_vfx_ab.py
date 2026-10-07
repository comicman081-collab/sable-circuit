"""Same-session native A/B of the VFX overhaul against HEAD with perf_op1_vfx.gd.

Swaps every changed runtime file (scripts/, data/) between its HEAD bytes and the working
bytes, rotating the order each round so machine-load drift spreads over both. New files
stay in place (HEAD code never references them). The working copy is backed up under
.cache/diag/vfx/ab_backup and restored byte for byte at the end.
usage: python native_vfx_overhaul_ab.py <rounds> <out.json>
"""
from pathlib import Path
import json
import re
import shutil
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
GODOT = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
ROUNDS = int(sys.argv[1])
OUT = Path(sys.argv[2])
changed = [p for p in subprocess.run(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
           if p.startswith(('scripts/', 'data/'))]
working = {p: (ROOT / p).read_bytes() for p in changed}
head = {p: subprocess.run(['git', 'show', 'HEAD:' + p], cwd=ROOT, capture_output=True, check=True).stdout for p in changed}
backup = ROOT / '.cache/diag/vfx/ab_backup'
for p, data in working.items():
    (backup / p).parent.mkdir(parents=True, exist_ok=True)
    (backup / p).write_bytes(data)
VERSIONS = {'head': head, 'overhaul': working}
LINE = re.compile(r'PERF t=\s*(\d+)s fps=\s*([\d.]+).*vfx_avg=([\d.]+) vfx_max=(\d+)')
rows = []


def put(files):
    for p, data in files.items():
        for attempt in range(20):
            try:
                (ROOT / p).write_bytes(data)
                break
            except OSError:
                time.sleep(0.5)


try:
    names = list(VERSIONS)
    for round_index in range(ROUNDS):
        order = names[round_index % 2:] + names[:round_index % 2]
        for name in order:
            put(VERSIONS[name])
            text = subprocess.run([GODOT, '--path', str(ROOT), '-s', 'res://.cache/diag/vfx/perf_op1_detail.gd'], cwd=ROOT,
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300).stdout
            samples = [(int(t), float(f), float(a), int(m)) for t, f, a, m in LINE.findall(text)]
            kept = [s for s in samples if s[0] > 5]
            row = {'version': name, 'round': round_index + 1, 'fps': [s[1] for s in kept],
                   'vfx_avg': [s[2] for s in kept], 'vfx_max': max((s[3] for s in kept), default=None)}
            rows.append(row)
            print('RUN', json.dumps(row), flush=True)
            for line in text.splitlines():
                if line.startswith(('PERF', 'DETAIL')): print(name, line, flush=True)
finally:
    put(working)
    assert all((ROOT / p).read_bytes() == data for p, data in working.items())
summary = {}
for name in VERSIONS:
    fps = [f for r in rows if r['version'] == name for f in r['fps']]
    live = [a for r in rows if r['version'] == name for a in r['vfx_avg']]
    summary[name] = {'samples': len(fps), 'fps_median': statistics.median(fps) if fps else None,
                     'fps_min': min(fps, default=None), 'fps_max': max(fps, default=None),
                     'live_vfx_avg_median': statistics.median(live) if live else None}
OUT.write_text(json.dumps({'rounds': ROUNDS, 'changed_files': changed, 'runs': rows, 'summary': summary}, indent=2), encoding='utf-8')
print('SUMMARY', json.dumps(summary), flush=True)
print('RESTORED working copy', flush=True)
