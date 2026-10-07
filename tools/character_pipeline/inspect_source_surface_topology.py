"""Read an owned source-surface diagnostic and report actual nonmanifold edges."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]

def child(args):
    import bpy
    from collections import Counter,defaultdict
    source=json.loads(Path(args.surface).read_text(encoding='utf8'))
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/source['blend']['path']),load_ui=False)
    mesh=bpy.data.objects[source['mesh_name']].data
    incidence=defaultdict(list)
    vertex_uv={}
    for face in mesh.polygons:
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):incidence[tuple(sorted((a,b)))].append(face.index)
        for loop in face.loop_indices:
            vertex_uv[mesh.loops[loop].vertex_index]=list(mesh.uv_layers.active.data[loop].uv)
    bad=[{'vertices':list(edge),'faces':faces,
          'source_uv':[vertex_uv[v] for v in edge],
          'position_m':[list(mesh.vertices[v].co) for v in edge],
          'face_materials':[mesh.polygons[f].material_index for f in faces]}
         for edge,faces in incidence.items() if len(faces)!=2]
    report={'incidence_histogram':dict(Counter(len(v) for v in incidence.values())),
            'bad_edges':bad,'actual_mesh':source['blend']}
    (Path(args.out)/'TOPOLOGY.json').write_text(json.dumps(report,indent=2),encoding='utf8')

def main(args):
    out=(ROOT/args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    cache=out/'cache';cache.mkdir()
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
             '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
             '--python',str(Path(__file__).resolve()),'--','--inside',
             '--surface',str((ROOT/args.surface).resolve()),'--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf8') as log:
        subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,
                       timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    report=json.loads((out/'TOPOLOGY.json').read_text(encoding='utf8'))
    print(report['incidence_histogram'])
    print(json.dumps(report['bad_edges'][:5],indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--surface',required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else main(args)
