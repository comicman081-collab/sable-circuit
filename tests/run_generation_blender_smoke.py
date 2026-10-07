"""One owned Blender process; synthetic first-pose gate counterexamples only."""
import os
import subprocess
import sys
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
out=ROOT/'artifacts/generation_harness_audit/technical_fixtures'/uuid.uuid4().hex
out.mkdir(parents=True)
env=os.environ.copy()
for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
            'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):
    env[key]=str(out/'cache')
(out/'cache').mkdir(); env['OMP_NUM_THREADS']='2'
command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
         '--threads','2','--python-exit-code','2','--python',str(ROOT/'tests/blender/generation_preflight_smoke.py'),
         '--','--out',str(out)]
with (out/'blender.log').open('w',encoding='utf-8') as log:
    completed=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
        timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
if completed.returncode:
    raise SystemExit('FAIL_GENERATION_BLENDER_SMOKE: '+str(out/'blender.log'))
report=g.read(out/'result.json')
if report.get('status')!='PASS_HARNESS_REGRESSIONS_ONLY': raise ValueError('Incomplete Blender smoke')
print(str(out/'result.json'))
print(report['status'],len(report['checks']),'checks; owned Blender exited')
