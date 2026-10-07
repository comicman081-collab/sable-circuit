"""Run actual source-skin viewport wiring in an isolated Godot project."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def run(args):
    out = g.local(args.out)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'cache').mkdir()
    skin = g.read(args.skin)
    inputs = {'SOURCE_SKIN.json': g.ref(args.skin),
              'MOTION_PACK.json': g.ref(args.pack),
              'SOURCE_RGBA.png': skin['source_rgba'],
              'smoke.gd': g.ref(ROOT / 'tests/smoke/source_skin_viewport_smoke.gd')}
    for name in ('skeletal_motion_player', 'source_skin_view', 'source_skin_viewport',
                 'source_skin_weapon_binding', 'source_projection'):
        path = f'scripts/animation/{name}.gd'
        inputs[path] = g.ref(ROOT / path)
    for name, reference in inputs.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(g.resolve(reference), target)
    g.write(out / 'INPUTS.json', {'files': inputs, 'runner': g.ref(__file__)})
    (out / 'project.godot').write_text(
        '[application]\nconfig/name="Source viewport wiring"\n'
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n', encoding='utf8')
    env = os.environ.copy()
    for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA', 'XDG_CACHE_HOME', 'XDG_DATA_HOME'):
        env[key] = str(out / 'cache')
    with (out / 'godot.log').open('w', encoding='utf8') as log:
        result = subprocess.run([args.godot, '--headless', '--path', str(out), '--script', 'smoke.gd'],
                                cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    log = (out / 'godot.log').read_text(encoding='utf8')
    if result.returncode or 'SCRIPT ERROR' in log or 'ERROR:' in log:
        raise ValueError('VIEWPORT_TEST_FAILED: ' + str(out / 'godot.log'))
    if g.read(out / 'RESULT.json')['failures']:
        raise ValueError('VIEWPORT_TEST_ASSERTIONS_FAILED')
    for reference in inputs.values():
        g.resolve(reference)
    g.write(out / 'COMPLETION.json', {'inputs': g.ref(out / 'INPUTS.json'),
            'result': g.ref(out / 'RESULT.json'), 'production_ready': False,
            'scope': 'actual viewport wiring; no GPU visual approval'})
    print('SOURCE_VIEWPORT_WIRING_PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin', required=True)
    parser.add_argument('--pack', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--godot', default='D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe')
    run(parser.parse_args())
