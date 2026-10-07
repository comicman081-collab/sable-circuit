"""Bounded hidden tool execution; all writable runtime locations stay in this project."""
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'qa/karchive_props_20260919'
env=os.environ.copy()
for key,folder in {'TEMP':'tmp','TMP':'tmp','BLENDER_USER_RESOURCES':'blender_user',
                   'BLENDER_USER_CONFIG':'blender_user/config','BLENDER_USER_DATAFILES':'blender_user/datafiles',
                   'XDG_CACHE_HOME':'cache','PYTHONPYCACHEPREFIX':'pycache'}.items():
    path=QA/folder;path.mkdir(parents=True,exist_ok=True);env[key]=str(path)
env['PYTHONDONTWRITEBYTECODE']='1'
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
mode=sys.argv[1]
if mode in ('render','prop_metadata'):
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
             '--python-exit-code','1','--python',str(ROOT/'tools/environment/render_karchive_props.py')]
    if mode=='prop_metadata': command.extend(['--','--metadata-only'])
else:
    command=['D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe','--path',str(ROOT),*sys.argv[2:]]
with (QA/(mode+'.stdout.log')).open('w',encoding='utf-8') as stream:
    result=subprocess.run(command,cwd=ROOT,env=env,startupinfo=startup,stdout=stream,stderr=subprocess.STDOUT,timeout=600)
print('OWNED_TOOL_EXIT',mode,result.returncode)
sys.exit(result.returncode)
