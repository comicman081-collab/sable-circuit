"""Read-only, bounded Blender asset/geometry/license intake. Never a rig PASS."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def collect(source,out):
    import bpy
    from mathutils import Vector
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assets=[]
    for kind,values in (('object',bpy.data.objects),('collection',bpy.data.collections)):
        for value in values:
            if value.asset_data:
                a=value.asset_data
                assets.append({'kind':kind,'name':value.name,'author':a.author,'license':a.license,
                    'copyright':a.copyright,'description':a.description})
    objects=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH': continue
        points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        objects.append({'name':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),
            'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],
            'modifiers':[m.type for m in ob.modifiers],'groups':list(ob.vertex_groups.keys()),
            'uv_layers':list(ob.data.uv_layers.keys()),'collections':[c.name for c in ob.users_collection]})
    g.write(out/'intake.json',{'source':g.ref(source),'collector':g.ref(__file__),
        'assets':assets,'meshes':objects,'text_blocks':{t.name:t.as_string() for t in bpy.data.texts},
        'status':'READ_ONLY_INVENTORY_NOT_RIG_OR_CHARACTER_APPROVAL'})


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True);p.add_argument('--out',required=True)
    p.add_argument('--inside-blender',action='store_true');a=p.parse_args(args)
    source=g.local(a.input);out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('INTAKE_DIAGNOSTICS_ONLY')
    if a.inside_blender:
        collect(source,out);return
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):
        env[key]=str(cache)
    env['OMP_NUM_THREADS']='2';env['PYTHONDONTWRITEBYTECODE']='1'
    before=g.ref(source)
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,
        '--','--inside-blender','--input',str(source),'--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode or not (out/'intake.json').is_file() or before!=g.ref(source):
        raise ValueError('BASE_MESH_INTAKE_FAILED_OR_SOURCE_CHANGED')
    g.write(out/'completion.json',{'owned_child_exited':True,'source_unchanged':True,
        'intake':g.ref(out/'intake.json'),'production_ready':False})
    print(str(out/'intake.json'))


if __name__=='__main__':main()
