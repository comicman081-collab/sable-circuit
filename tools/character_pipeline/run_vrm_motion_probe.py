"""Bounded actual VRM/UAL diagnostic, led by Astra before any Luna test."""
import argparse
import os
import subprocess
from pathlib import Path
import generation_harness as g

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-result',required=True); p.add_argument('--out',required=True)
    a=p.parse_args(); out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('UNAPPROVED_RETARGET_DIAGNOSTIC_ONLY')
    imported=g.read(a.import_result)
    if imported['errors']: raise ValueError('IMPORT_FAILED')
    g.resolve(imported['blend']); g.resolve(imported['model'])
    out.mkdir(parents=True,exist_ok=False); cache=out/'cache'; cache.mkdir()
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):
        env[key]=str(cache)
    env['OMP_NUM_THREADS']='2'; env['PYTHONDONTWRITEBYTECODE']='1'
    script=ROOT/'tools/character_pipeline/probe_vrm_ual_retarget.py'
    g.write(out/'inputs.json',{'import_result':g.ref(a.import_result),'script':g.ref(script),
        'runner':g.ref(__file__),'scope':'ONE_ASTRA_DIAGNOSTIC_WALK_NOT_PRODUCTION'})
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',str(script),
        '--','--import-result',str(g.local(a.import_result)),'--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode: raise ValueError('VRM_RETARGET_PROBE_FAILED: '+str(out/'blender.log'))
    result=g.read(out/'retarget_result.json')
    g.resolve(result['output_blend']); g.resolve(result['input_blend']); g.resolve(result['first_native_pose'])
    if len(result['baked_playback'])!=25: raise ValueError('INCOMPLETE_BAKED_PLAYBACK')
    if (result['source_duration_seconds']!=result['baked_duration_seconds'] or
            result['baked_playback'][-1]['time_s']!=result['source_duration_seconds']):
        raise ValueError('UNAUTHORIZED_CADENCE_CHANGE')
    g.write(out/'completion.json',{'status':'COMPLETE_DIAGNOSTIC_EXECUTION_NOT_MOTION_APPROVAL',
        'result':g.ref(out/'retarget_result.json'),'owned_child_exited':True,'production_ready':False})
    print(str(out/'completion.json'))


if __name__=='__main__': main()
