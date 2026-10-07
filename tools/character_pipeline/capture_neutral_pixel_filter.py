"""One same-scene native neutral QA capture; changes only pixel filter settings."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def child(args):
    import bpy
    out=g.local(args.out)
    inputs=g.read(out/'INPUTS.json')
    for reference in inputs.values():g.resolve(reference)
    if inputs['capture'] != g.ref(__file__) or inputs['harness'] != g.ref(g.__file__):raise ValueError('EXACT_CAPTURE_REQUIRED')
    report=g.read(g.resolve(inputs['neutral']))
    for key in ['blend','source_rgba','actual_native_rest']:
        if inputs[key] != report[key]:raise ValueError('EXACT_NEUTRAL_CAPTURE_DEPENDENCY_REQUIRED:'+key)
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(report['blend'])),load_ui=False)
    scene=bpy.context.scene
    if (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.cycles.samples)!=(1920,1920,100,64):
        raise ValueError('EXACT_EXISTING_NATIVE_CAPTURE_REQUIRED')
    old={'type':scene.cycles.pixel_filter_type,'width':scene.cycles.filter_width}
    scene.cycles.pixel_filter_type='BOX'
    scene.cycles.filter_width=1.0
    scene.render.filepath=str(out/'NEUTRAL_BOX_NATIVE_1920.png')
    bpy.ops.render.render(write_still=True)
    result=dict(report)
    result['render']=g.ref(out/'NEUTRAL_BOX_NATIVE_1920.png')
    result['qa_capture_inputs']=g.ref(out/'INPUTS.json')
    result['qa_capture_claim']=g.ref(out/'CHILD_CLAIM.json')
    result['pixel_filter_change']={'before':old,'after':{'type':'BOX','width':1.0}}
    result['scope']='same neutral scene QA capture only; no rig, material, UV, image or motion changes'
    result['production_ready']=False
    g.write(out/'CAPTURE_REPORT.json',result)


def run(args):
    out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('QUARANTINED_CAPTURE_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    report=g.read(args.neutral)
    g.write(out/'INPUTS.json',{'neutral':g.ref(args.neutral),'capture':g.ref(__file__),'harness':g.ref(g.__file__),
        'blend':report['blend'],'source_rgba':report['source_rgba'],'actual_native_rest':report['actual_native_rest']})
    env=os.environ.copy()
    for key in ['TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX']:
        env[key]=str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    with (out/'blender.log').open('w',encoding='utf8') as log:
        subprocess.run([str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
            '--offline-mode','--threads','2','--python-exit-code','2','--python',str(Path(__file__).resolve()),
            '--','--inside','--out',str(out)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=180,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    print('ONE_SAME_NEUTRAL_PIXEL_FILTER_CAPTURE_COMPLETE')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--neutral');parser.add_argument('--out',required=True);parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
