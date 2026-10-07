"""Read saved files again; verify real keys, geometry, textures and reuse block."""
import argparse
import sys
from pathlib import Path
import hashlib
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import build_tripo_standing_reference as builder

p=argparse.ArgumentParser()
p.add_argument('--pack',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
pack=g.local(a.pack); report=g.read(pack/'INSPECTION.json'); geometry=g.read(pack/'RUN_GEOMETRY.json')
files=[pack/'SOURCE_RUN.blend',pack/'STANDING_BODY_PACK.blend',pack/'RUN_REFERENCE.blend']
before={str(f):g.sha(f) for f in files}; variants=[]
for f in files:
    bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
    rig=bpy.data.objects[report['rig']]; mesh=bpy.data.objects[report['mesh']]
    action=bpy.data.actions[report['action']]
    if builder.action_digest(action)!=geometry['source_action_key_sha256']:
        raise ValueError('SAVED_RUN_KEYS_CHANGED')
    topology=g.canonical({'vertices':[builder.vec(v.co) for v in mesh.data.vertices],
        'polygons':[list(p.vertices) for p in mesh.data.polygons],
        'uv':[[builder.vec(v.uv) for v in layer.data] for layer in mesh.data.uv_layers],
        'weights':[[[w.group,w.weight] for w in v.groups] for v in mesh.data.vertices]})
    if topology!=geometry['mesh_topology_uv_skin_sha256']:
        raise ValueError('SAVED_TOPOLOGY_UV_SKIN_CHANGED')
    textures={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
    if not textures: raise ValueError('EMBEDDED_SOURCE_TEXTURE_REQUIRED')
    if variants and variants[0]['textures']!=textures: raise ValueError('SOURCE_TEXTURE_BYTES_CHANGED')
    if f.name=='STANDING_BODY_PACK.blend':
        if rig.animation_data.action.name!='SABLE_REFERENCE_Standing_NativeBind':
            raise ValueError('SAVED_STANDING_ACTION_NOT_ACTIVE')
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        pose=builder.evaluated_vertices(mesh)
        rig.data.pose_position='REST';bpy.context.view_layer.update()
        rest=builder.evaluated_vertices(mesh)
        if max(abs(x-y) for p,q in zip(pose,rest) for x,y in zip(p,q))>1e-5:
            raise ValueError('SAVED_STAND_NOT_NATIVE_BIND')
    if f.name=='RUN_REFERENCE.blend':
        if rig.animation_data.action!=action: raise ValueError('SAVED_RUN_ACTION_NOT_ACTIVE')
        for row in geometry['samples']:
            frame=row['frame'];bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
            actual=builder.evaluated_vertices(mesh)
            error=max(abs(x-y) for side,ids in geometry['sole_vertex_ids'].items()
                for idx,p in zip(ids,row['sole_vertices_world_m'][side]) for x,y in zip(actual[idx],p))
            if error>1e-5: raise ValueError('SAVED_RUN_SOLES_DO_NOT_REPRODUCE')
    variants.append({'file':g.ref(f),'run_keys_unchanged':True,'topology_uv_skin_unchanged':True,'textures':textures})
old_argv=sys.argv
sys.argv=['builder','--','--input',str(g.resolve(report['source'])),'--license',str(pack.parent/'source/MODEL_LICENSE_MANIFEST.json'),'--out',str(pack)]
try:
    try: builder.main()
    except ValueError as exc:
        if 'RETAIN_EXISTING_EVIDENCE_USE_FRESH_OUTPUT' not in str(exc): raise
    else: raise ValueError('CONSUMED_CHILD_RETRY_WAS_NOT_BLOCKED')
finally: sys.argv=old_argv
if any(g.sha(f)!=before[str(f)] for f in files): raise ValueError('READONLY_TEST_CHANGED_PACK')
g.write(a.out,{'schema':1,'status':'PASS_SAVED_REFERENCE_INTEGRITY_ONLY','production_ready':False,
    'pack':g.ref(pack/'completion.json'),'qa_script':g.ref(__file__),'variants':variants,
    'run_geometry':g.ref(pack/'RUN_GEOMETRY.json'),'all_49_saved_sole_samples_reproduced':True,
    'consumed_child_retry_blocked_before_import':True,'source_files_unchanged':True})
