"""Run the unchanged live app and current character source checks after isolation."""
from contextlib import redirect_stdout
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'qa/asset_cleanup_20260911'
if len(sys.argv) > 1:
    if not re.fullmatch(r'asset_cleanup_[a-z0-9_]+', sys.argv[1]):
        raise ValueError('Invalid cleanup batch')
    REPORT = ROOT / 'qa' / sys.argv[1]
GODOT = Path('D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe')
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
checks = []


def run(name, command):
    print(f'Running {name}', flush=True)
    log = REPORT / (name + '.log')
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=120,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    content = log.read_text(encoding='utf-8', errors='replace')
    passed = result.returncode == 0 and ': PASS' in content and 'SCRIPT ERROR:' not in content and 'ERROR:' not in content
    checks.append({'name': name, 'passed': passed, 'exitCode': result.returncode,
                   'log': log.relative_to(ROOT).as_posix()})
    print(f'{name}: {"PASS" if passed else "FAIL"}', flush=True)


run('project_static', [sys.executable, '-B', 'tools/validate_project.py'])
for name in ['motion_lab_character_runtime_smoke', 'm7_authored_visual_smoke',
             'prototype_smoke', 'm2_story_flow_smoke', 'rook_c02_fast_runtime_smoke']:
    run(name, [str(GODOT), '--headless', '--path', str(ROOT), '--script', f'res://tests/smoke/{name}.gd'])

spec = importlib.util.spec_from_file_location('cleanup_character_validation', ROOT / 'motion_lab_v1/validate_character.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for ident in ['aster', 'mica']:
    output = ROOT / f'motion_lab_v1/qa/{REPORT.name}/{ident}_asset_validation.json'
    with (REPORT / f'{ident}_asset_validation.log').open('w', encoding='utf-8') as stream, redirect_stdout(stream):
        passed = module.validate(ident, output)
    checks.append({'name': ident + '_asset_validation', 'passed': passed,
                   'report': output.relative_to(ROOT).as_posix()})
    print(f'{ident}_asset_validation: {"PASS" if passed else "FAIL"}', flush=True)

result = {'status': 'PASS' if all(row['passed'] for row in checks) else 'FAIL',
          'scope': 'Unmodified runtime and exact source assets after cleanup; no new artistic/visual approval',
          'checks': checks}
(REPORT / 'runtime_validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result), flush=True)
raise SystemExit(0 if result['status'] == 'PASS' else 1)
