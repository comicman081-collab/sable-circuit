"""One independent saved-Blender read-only probe. No render or blend save."""
from pathlib import Path
import json
import hashlib
import math
import bpy

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'artifacts/quarantine/generation_diagnostics'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def ref(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
geometry_path = BASE/'tripo_laterality_guide_r01/GEOMETRY.json'
geometry = read(geometry_path)
result_path = ROOT/geometry['retarget_result']['path']
result = read(result_path)
report_path = ROOT/geometry['calibration']['path']
report = read(report_path)
blend = ROOT/geometry['blend']['path']
assert ref(blend) == geometry['blend'] == result['output_blend']
before = ref(blend)
bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False)
scene=bpy.context.scene
mesh=bpy.data.objects[result['sole_mesh']]
rig=next(m.object for m in mesh.modifiers if m.type=='ARMATURE')
groups={side:{mesh.vertex_groups[name+'_'+suffix].index for name in ('thigh','calf','foot','ball')} for side,suffix in [('left','l'),('right','r')]}
weights={v.index:{side:sum(g.weight for g in v.groups if g.group in ids) for side,ids in groups.items()} for v in mesh.data.vertices}
counts={'neutral':0,'left':0,'right':0}
for face in mesh.data.polygons:
    totals={s:sum(weights[i][s] for i in face.vertices)/len(face.vertices) for s in groups}
    side=max(totals,key=totals.get)
    counts[side if totals[side]>.25 else 'neutral']+=1
assert counts==geometry['polygon_counts']
sole_weights={}
for side,ids in result['sole_vertex_ids'].items():
    other='right' if side=='left' else 'left'
    sole_weights[side]={'vertex_count':len(ids),'minimum_own_chain_weight':min(weights[i][side] for i in ids),'maximum_other_chain_weight':max(weights[i][other] for i in ids)}
    assert all(weights[i][side]>.25 and weights[i][side]>weights[i][other] for i in ids)
def vertices():
    ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    try:return [tuple(ev.matrix_world@v.co) for v in data.vertices]
    finally:ev.to_mesh_clear()
def soles(vv):return {s:[list(vv[i]) for i in ids] for s,ids in result['sole_vertex_ids'].items()}
rig.data.pose_position='REST';bpy.context.view_layer.update()
rest=soles(vertices())
assert rest==report['fixed_floor']['neutral_sole_vertices_world_m']
floor=min(v[2] for arr in rest.values() for v in arr)
assert floor==geometry['fixed_floor_world_z_m']
rig.data.pose_position='POSE'
ymin=zmin=float('inf');ymax=zmax=float('-inf')
for row in report['samples']:
    frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
    vv=vertices()
    assert soles(vv)==row['sole_vertices_world_m']
    ymin=min(ymin,min(v[1] for v in vv));ymax=max(ymax,max(v[1] for v in vv))
    zmin=min(zmin,min(v[2] for v in vv));zmax=max(zmax,max(v[2] for v in vv))
zmin=min(zmin,floor)
cy=(ymin+ymax)/2;cz=(zmin+zmax)/2
scale=max((zmax-zmin)*1920/1080,ymax-ymin)*1.15
def project(point):return [960-(point[1]-cy)*1920/scale,540-(point[2]-cz)*1920/scale]
row=report['samples'][geometry['sample']]
frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
actual=soles(vertices());assert actual==geometry['actual_sole_vertices_world_m']
joints={};projected={}
for side,suffix in [('left','l'),('right','r')]:
    joints[side]={};projected[side]={}
    for stem,label in [('thigh','hip'),('calf','knee'),('foot','ankle'),('ball','toe')]:
        world=list(rig.matrix_world@rig.pose.bones[stem+'_'+suffix].head)
        assert math.dist(world,row['joint_heads_world_m'][side+'_'+label])<1e-7
        joints[side][stem]=world;projected[side][stem]=project(world)
errors=[math.dist(projected[s][k],geometry['projected_joints_px'][s][k]) for s in projected for k in projected[s]]
sole_projection_error=max(math.dist(project(point),pixel) for side in actual for point,pixel in zip(actual[side],geometry['projected_soles_px'][side]))
assert max(errors)<.001 and sole_projection_error<.001
assert abs(project([0,cy,floor])[1]-geometry['floor_y_px'])<.001
assert before==ref(blend)
out={'verdict':'PASS_READ_ONLY_NATIVE_MAPPING_ONLY','production_ready':False,'probe':ref(Path(__file__)),'blender_version':bpy.app.version_string,'blend':before,'geometry':ref(geometry_path),'result':ref(result_path),'calibration':ref(report_path),'groups':{s:{v.name:v.index for v in mesh.vertex_groups if v.index in ids} for s,ids in groups.items()},'polygon_counts':counts,'sole_weights':sole_weights,'actual_rest_floor_m':floor,'actual_rest_sole_arrays_match':True,'all49_saved_pose_sole_arrays_match':True,'exact_contact_sole_arrays_match':True,'actual_joint_heads_world_m':joints,'maximum_joint_projection_error_px':max(errors),'maximum_sole_projection_error_px':sole_projection_error,'maximum_floor_projection_error_px':abs(project([0,cy,floor])[1]-geometry['floor_y_px']),'full_cycle_camera_ortho_scale':scale,'rendered':False,'blend_saved':False,'source_blend_hash_unchanged':True}
with (OUT/'NATIVE_MAPPING_QA.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print('INDEPENDENT_NATIVE_MAPPING_QA_PASS')
