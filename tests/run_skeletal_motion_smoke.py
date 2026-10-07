"""Run the actual Blender-bone player in a bounded isolated Godot project."""
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
    inputs={'player':g.ref(ROOT/'scripts/animation/skeletal_motion_player.gd'),
            'test':g.ref(ROOT/'tests/smoke/skeletal_motion_player_smoke.gd'),
            'pack':g.ref(args.pack),'runner':g.ref(__file__),
            'projection':g.ref(ROOT/'scripts/animation/source_projection.gd')}
    for key,name in [('player','skeletal_motion_player.gd'),('test','smoke.gd'),('pack','MOTION_PACK.json'),
                     ('projection','scripts/animation/source_projection.gd')]:
        (out/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(g.resolve(inputs[key]),out/name)
    (out/'project.godot').write_text('[application]\nconfig/name="Actual skeletal motion test"\n'
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',encoding='utf8')
    g.write(out/'INPUTS.json',inputs)
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME'):
        env[key]=str(out/'cache')
    command=[args.godot,'--headless','--path',str(out),'--script','smoke.gd']
    with (out/'godot.log').open('w',encoding='utf8') as log:
        process=subprocess.run(command,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    text=(out/'godot.log').read_text(encoding='utf8')
    if process.returncode or 'SCRIPT ERROR' in text or 'ERROR:' in text or not (out/'RESULT.json').exists():
        raise ValueError('GODOT_TEST_EXECUTION_FAILED:'+str(out/'godot.log'))
    result=g.read(out/'RESULT.json')
    if result['case_count']!=24 or result['failures']:
        raise ValueError('SKELETAL_REGRESSION_FAILED')
    for reference in inputs.values():g.resolve(reference)
    g.write(out/'COMPLETION.json',{'scope':'actual_bone_playback_technical_only','inputs':g.ref(out/'INPUTS.json'),
        'result':g.ref(out/'RESULT.json'),'log':g.ref(out/'godot.log'),'case_count':24,'errors':[],
        'production_ready':False,'owned_child_exited':True})
    print('ACTUAL_BONE_TESTS 24 PASS; character motion/HTML unapproved')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pack',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--godot',default='D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64_console.exe')
    run(parser.parse_args())
