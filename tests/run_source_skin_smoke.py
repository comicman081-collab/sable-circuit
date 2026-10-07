"""Exercise Blender skin data through the actual Godot renderer/bone interfaces."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

def run(args):
    out=g.local(args.out);out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    skin=g.read(args.skin)
    inputs={'skin':g.ref(args.skin),'pack':g.ref(args.pack),'rgba':skin['source_rgba'],
            'view':g.ref(ROOT/'scripts/animation/source_skin_view.gd'),
            'player':g.ref(ROOT/'scripts/animation/skeletal_motion_player.gd'),
            'projection':g.ref(ROOT/'scripts/animation/source_projection.gd'),
            'test':g.ref(ROOT/'tests/smoke/source_skin_view_smoke.gd'),'runner':g.ref(__file__)}
    for key,path in [('skin','SOURCE_SKIN.json'),('pack','MOTION_PACK.json'),('rgba','SOURCE_RGBA.png'),
                     ('view','scripts/animation/source_skin_view.gd'),('player','scripts/animation/skeletal_motion_player.gd'),
                     ('projection','scripts/animation/source_projection.gd'),('test','smoke.gd')]:
        target=out/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(g.resolve(inputs[key]),target)
    (out/'project.godot').write_text('[application]\nconfig/name="Actual source skin test"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',encoding='utf8')
    g.write(out/'INPUTS.json',inputs)
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME'):env[key]=str(out/'cache')
    with (out/'godot.log').open('w',encoding='utf8') as log:
        result=subprocess.run([args.godot,'--headless','--path',str(out),'--script','smoke.gd'],
                              cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    log=(out/'godot.log').read_text(encoding='utf8')
    if result.returncode or 'SCRIPT ERROR' in log or 'ERROR:' in log or not (out/'RESULT.json').exists():
        raise ValueError('SOURCE_SKIN_RUNTIME_TEST_FAILED:'+str(out/'godot.log'))
    report=g.read(out/'RESULT.json')
    if report['failures'] or report['metrics']['sampled_vertices']<100:raise ValueError('SKIN_BINDING_INCOMPLETE')
    for reference in inputs.values():g.resolve(reference)
    g.write(out/'COMPLETION.json',{'inputs':g.ref(out/'INPUTS.json'),'result':g.ref(out/'RESULT.json'),
                                 'scope':'ACTUAL_SKIN_BINDING_TECHNICAL_ONLY','production_ready':False})
    print('ACTUAL_SOURCE_SKIN_GODOT_BINDING_PASS')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin',required=True);parser.add_argument('--pack',required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--godot',default='D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe')
    run(parser.parse_args())
