"""Read-only audit of three known failed pilots; recoverable quarantine only."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
BASE=ROOT/'art_src/characters/mica/rigged_v1/candidates'
OUT=ROOT/'artifacts/generation_harness_audit/rejected_mica_pilots_20260907'
PILOTS=('pilot_01','pilot_02','pilot_03')


def collect_in_blender():
    import bpy
    from collect_generation_mesh_preflight import collect_scene
    for name in PILOTS:
        original=BASE/name/'MICA_C03_ACTUAL_SKIN_PILOT.blend'
        bpy.ops.wm.open_mainfile(filepath=str(original))
        g.write(OUT/(name+'_mesh.json'),collect_scene())


def main():
    import motion_harness as motion
    from collect_generation_mesh_preflight import validate_collected
    # Fail before moving if any actual runtime/source registry points at a pilot.
    prefixes=[str((BASE/name).relative_to(ROOT)).replace('\\','/').lower() for name in PILOTS]
    for folder in ('data','scripts','scenes'):
        for file in (ROOT/folder).rglob('*'):
            if file.is_file() and file.suffix in ('.json','.gd','.tscn','.tres'):
                value=file.read_text(encoding='utf-8-sig').replace('\\','/').lower()
                if any(prefix in value for prefix in prefixes):
                    raise ValueError('ACTIVE_REFERENCE_PREVENTS_QUARANTINE:'+str(file))
    if any(not (BASE/name).is_dir() for name in PILOTS): raise ValueError('EXACT_PILOT_TARGETS_REQUIRED')
    OUT.mkdir(parents=True,exist_ok=False); cache=OUT/'cache'; cache.mkdir()
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'): env[key]=str(cache)
    env['OMP_NUM_THREADS']='2'
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
        '--offline-mode','--threads','2','--python-exit-code','2','--python',str(Path(__file__).resolve()),'--','--blender-collect']
    with (OUT/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode: raise ValueError('REJECTED_PILOT_COLLECTION_INCOMPLETE')
    reports={}
    for name in PILOTS:
        mesh=validate_collected(g.read(OUT/(name+'_mesh.json')))
        poses={p.name:g.audit_pose(p) for p in (BASE/name).glob('*_NATIVE_1920.png')}
        if not mesh['errors']: raise ValueError('UNEXPECTED_TECHNICAL_RESULT_REQUIRES_REVIEW')
        reports[name]={'verdict':'FAIL_NOT_PROMOTABLE','actual_mesh':mesh,'native_pixel_checks':poses,
            'independent_visual_rejection':'Previous direct review: chroma/UV contamination, ghost hand and disconnected waist/coat. No completed replacement.'}
    g.write(OUT/'pre_move_audit.json',reports)
    locations=[]
    for name in PILOTS:
        for source in (BASE/name,ROOT/'artifacts/mica_rigged_v1'/name):
            if not source.exists(): continue
            # Resolve and constrain both ends before recursive inventory or move.
            source=source.resolve()
            if source not in ((BASE/name).resolve(),(ROOT/'artifacts/mica_rigged_v1'/name).resolve()):
                raise ValueError('UNEXPECTED_QUARANTINE_PATH')
            target=motion.quarantine(source,'Rejected MICA pilot: actual generation gate FAIL; retain until final replacement')
            inventory=g.read(target.with_suffix('.inventory.json'))
            for old,expected in inventory['files'].items():
                suffix=Path(old).relative_to(source.relative_to(ROOT))
                if g.sha(target/suffix)!=expected: raise ValueError('QUARANTINE_HASH_MISMATCH')
            locations.append({'old':str(source.relative_to(ROOT)),'retained':str(target.relative_to(ROOT)),
                              'inventory':g.ref(target.with_suffix('.inventory.json'))})
    g.write(OUT/'quarantine_result.json',{'status':'FAIL_ASSETS_RETAINED_NOT_DELETED','relocations':locations,
        'audit':g.ref(OUT/'pre_move_audit.json'),'owned_child_exited':True,'runtime_references_found':False})
    print(str(OUT/'quarantine_result.json'))


if __name__=='__main__':
    if '--blender-collect' in sys.argv: collect_in_blender()
    else: main()
