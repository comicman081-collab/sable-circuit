"""Blender geometric preflight (not rendered/visual acceptance evidence)."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
from build_mica_skinned_pilot import choose_action

manifest_path=Path(bpy.data.filepath).with_name('rig_manifest.json')
m=json.loads(manifest_path.read_text())
mesh=bpy.data.objects[m['mesh']]
rig=bpy.data.objects[m['rig']]
output={}
for action_name in ('Walk_Loop','Jog_Fwd_Loop','Sprint_Loop'):
    action=choose_action(rig,action_name)
    end=float(action.frame_range[1])
    rows=[]
    for i in range(97):
        frame=end*i/96
        bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame))
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        vertices=evaluated.to_mesh()
        row={'phase':i/96,'time':frame/24}
        for side in ('left','right'):
            coords=[evaluated.matrix_world@vertices.vertices[j].co for j in m['sole_vertex_ids'][side]]
            mean=sum(coords,Vector())/len(coords)
            row[side]={'mean':list(mean),'min_z':min(v.z for v in coords),'max_z':max(v.z for v in coords)}
        for side in ('l','r'):
            row['foot_'+side]=list(rig.matrix_world@rig.pose.bones['foot_'+side].head)
        row['pelvis']=list(rig.matrix_world@rig.pose.bones['pelvis'].head)
        evaluated.to_mesh_clear()
        rows.append(row)
    output[action_name]={'frames':rows,'duration':end/24}
    summary={'duration':end/24}
    for side in ('left','right'):
        summary[side]={'forward_excursion':max(r[side]['mean'][1] for r in rows)-min(r[side]['mean'][1] for r in rows),
                       'min_ground':min(r[side]['min_z'] for r in rows),
                       'max_sole_mean_height':max(r[side]['mean'][2] for r in rows)}
    output[action_name]['summary']=summary
    print('GEOMETRIC_PREFLIGHT_NOT_PASS '+action_name+' '+json.dumps(summary))
out=ROOT/'artifacts/mica_rigged_v1'/manifest_path.parent.name/'geometric_preflight.json'
if out.exists():
    raise ValueError('Retain previous preflight evidence; use a fresh candidate')
out.write_text(json.dumps(output,indent=2),encoding='utf-8')
