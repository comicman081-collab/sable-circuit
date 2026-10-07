"""One bounded, offline Blender VRM import; never a source-art/promotion route."""
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
from inspect_vrm_source import inspect


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True); p.add_argument('--license',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    report=inspect(a.model,a.license)
    if report['errors']: raise ValueError('VRM_INTAKE_FAILED:'+','.join(report['errors']))
    tools=g.read(ROOT/'tools/licenses/vroid_studio/INSTALLED_TOOL_REVIEW.json')
    evidence=tools['addon_execution_license']
    for key in ('main_license','license_text'): g.resolve(evidence[key])
    addon=Path(tools['blender_addon']['manifest_read_only']).parent
    if not (addon/'__init__.py').is_file(): raise ValueError('INSTALLED_VRM_ADDON_UNAVAILABLE')
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_IMPORT_OUTPUT_ONLY')
    out.mkdir(parents=True,exist_ok=False)
    g.write(out/'intake.json',report)
    addon_files={str(f.relative_to(addon)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in addon.rglob('*.py')}
    g.write(out/'inputs.json',{'model':g.ref(a.model),'license':g.ref(a.license),
        'tool_license':g.ref(ROOT/'tools/licenses/vroid_studio/INSTALLED_TOOL_REVIEW.json'),
        'addon_read_only':str(addon),'addon_python_files':addon_files,
        'driver':g.ref(__file__),'importer':g.ref(ROOT/'tools/character_pipeline/import_vrm_probe_blender.py')})
    env=os.environ.copy(); cache=out/'cache'; cache.mkdir()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):
        env[key]=str(cache)
    env['OMP_NUM_THREADS']='2'; env['PYTHONDONTWRITEBYTECODE']='1'
    # License confirmation is allowed only after exact-file commercial intake above.
    env['BLENDER_VRM_AUTOMATIC_LICENSE_CONFIRMATION']='true'
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',
        str(ROOT/'tools/character_pipeline/import_vrm_probe_blender.py'),'--','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode: raise RuntimeError('VRM_IMPORT_FAILED: '+str(out/'blender.log'))
    actual=g.read(out/'import_result.json')
    g.resolve(actual['blend'])
    if not actual.get('actual_weighted_meshes') or actual['errors']:
        raise ValueError('VRM_IMPORT_GEOMETRY_CHECK_FAILED')
    for name,value in addon_files.items():
        if hashlib.sha256((addon/name).read_bytes()).hexdigest()!=value: raise ValueError('ORIGINAL_ADDON_CHANGED')
    g.resolve(report['model'])
    g.write(out/'completion.json',{'status':'COMPLETE_IMPORT_ONLY_NOT_RETARGET_OR_VISUAL_PASS',
        'result':g.ref(out/'import_result.json'),'inputs':g.ref(out/'inputs.json'),
        'owned_child_exited':True,'source_and_addon_unchanged':True,'production_ready':False})
    print(str(out/'completion.json'))


if __name__=='__main__': main()
