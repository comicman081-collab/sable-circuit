"""Native Blender regression fixtures. Never character art or review approval."""
import argparse
import json
import runpy
import sys
from pathlib import Path
from unittest.mock import patch
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import collect_generation_mesh_preflight as collector
p=argparse.ArgumentParser(); p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); out=g.local(a.out)
if not out.is_relative_to(ROOT/'artifacts/generation_harness_audit/technical_fixtures'):
    raise ValueError('FIXTURE_ROOT_REQUIRED')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.unit_settings.scale_length=1
rig_data=bpy.data.armatures.new('rig'); rig=bpy.data.objects.new('rig',rig_data)
scene.collection.objects.link(rig); bpy.context.view_layer.objects.active=rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bone=rig_data.edit_bones.new('foot'); bone.head=(0,0,0); bone.tail=(0,0,1)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0.5))
body=bpy.context.object; body.name='body'; body['generation_role']='body'
group=body.vertex_groups.new(name='foot'); group.add(list(range(8)),1,'REPLACE')
modifier=body.modifiers.new('skin','ARMATURE'); modifier.object=rig
for frame in (1,2):
    rig.pose.bones['foot'].location=(frame*.02,0,0)
    rig.pose.bones['foot'].keyframe_insert('location',frame=frame)
material=bpy.data.materials.new('synthetic_material'); material.use_nodes=True
body.data.materials.append(material)
image=bpy.data.images.new('synthetic_texture',width=64,height=64)
image.pixels=[.1,.08,.3,1]*4096; image.filepath_raw=str(out/'texture.png'); image.file_format='PNG'; image.save()
bpy.data.images.remove(image); image=bpy.data.images.load(str(out/'texture.png'))
mask=bpy.data.images.new('synthetic_region',width=64,height=64)
mask.pixels=[1,1,1,1]*4096; mask.filepath_raw=str(out/'mask.png'); mask.file_format='PNG'; mask.save(); bpy.data.images.remove(mask)
texture=material.node_tree.nodes.new('ShaderNodeTexImage'); texture.image=image
principled=material.node_tree.nodes.get('Principled BSDF')
material.node_tree.links.new(texture.outputs['Color'],principled.inputs['Base Color'])
uv=body.data.uv_layers.active
for loop in uv.data: loop.uv=loop.uv*.2+Vector((.4,.4))
attribute=body.data.attributes.new('generation_chart_id','INT','FACE')
body['generation_chart_table']=json.dumps({'0':'body'})
scene['generation_source_charts']=json.dumps({'body':{'mask':g.ref(out/'mask.png'),'image':g.ref(out/'texture.png'),
    'purpose':'volumetric_texture','allowed_mesh_parts':['body']}})
ground=bpy.data.objects.new('ground',None); scene.collection.objects.link(ground)
scene['generation_mesh_contract']=json.dumps({'body_height_m':1.78,'required_parts':{'body':'body'},
    'sole_mesh':'body','sole_vertex_ids':{'left':[0,1,2],'right':[4,5,6]},
    'attachments':[{'id':'synthetic_attachment','a':{'object':'body','vertices':[0,1,2]},'b':{'object':'body','vertices':[0,1,2]}}],
    'body_coordinate_frame':'ground','body_axes_world':{'forward':[1,0,0],'left':[0,1,0],'up':[0,0,1]},'ground_origin_world_m':[0,0,0]})
scene['generation_view']='E'
bpy.ops.object.camera_add(location=(3,-4,3)); camera=bpy.context.object; scene.camera=camera
camera.rotation_euler=(Vector((0,0,.5))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=3
camera.keyframe_insert('location',frame=1); camera.location.x+=.5; camera.keyframe_insert('location',frame=2)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1920; scene.render.resolution_y=1920
scene.render.resolution_percentage=100; scene.render.film_transparent=True
scene.frame_set(1)
blend=out/'SYNTHETIC_REGRESSION_NOT_CHARACTER.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(blend))
checks=[]
raw=collector.collect_scene(); report=collector.validate_collected(raw)
g.write(out/'mesh_raw.json',raw); g.write(out/'mesh_report.json',report)
assert not report['errors'],report['errors']; checks.append('actual_closed_weighted_mesh_is_technical_HOLD_not_visual_PASS')
decoy=material.node_tree.nodes.new('ShaderNodeTexImage'); decoy.image=image
assert 'DISCONNECTED_DECOY_TEXTURE' in collector.material_graph(material,'body')[1]
checks.append('disconnected_approved_texture_cannot_cover_unreviewed_output'); material.node_tree.nodes.remove(decoy)
node_group=material.node_tree.nodes.new('ShaderNodeGroup')
tree=bpy.data.node_groups.new('unreviewed','ShaderNodeTree')
tree.interface.new_socket(name='Shader',in_out='OUTPUT',socket_type='NodeSocketShader'); node_group.node_tree=tree
output=next(n for n in material.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
material.node_tree.links.new(node_group.outputs[0],output.inputs['Surface'])
assert any('UNSUPPORTED_CONNECTED_SHADER_NODE:GROUP'==e for e in collector.material_graph(material,'body')[1])
checks.append('nested_unreviewed_material_group_is_blocked')
material.node_tree.nodes.remove(node_group); material.node_tree.links.new(principled.outputs[0],output.inputs['Surface'])
principled.inputs['Alpha'].default_value=0
assert 'ANATOMICAL_MESH_CANNOT_BE_ALPHA_ERASED' in collector.material_graph(material,'body')[1]
checks.append('invisible_anatomical_material_is_blocked'); principled.inputs['Alpha'].default_value=1
# Poison only memory, not the immutable saved scene. Mock JUST the independent
# approval checker for this isolated reload test; this is not production proof.
body.hide_render=True; body.data.vertices[0].co.z+=100
config={'generation_receipt':'synthetic authorization mocked only for isolated test',
    'skinned_mesh':'body','body_coordinate_frame':'ground','sole_vertex_ids':{'left':[0,1,2],'right':[4,5,6]},
    'direction':'E','subject_sha256':'SYNTHETIC_TEST_NOT_PROMOTABLE','native_size':1920,'runtime_cell':384,
    'output':str(out/'geometry.json'),'render_receipt':str(out/'render.json'),
    'frames':[{'frame':i,'time_s':(i-1)/24,'master_image':str(out/f'native_{i}.png'),'image':str(out/f'cell_{i}.png')} for i in (1,2)]}
g.write(out/'config.json',config)
sys.argv=['blender','--','--config',str(out/'config.json')]
with patch.object(g,'authorize_animation',return_value=None):
    try:
        runpy.run_path(str(ROOT/'tools/character_pipeline/export_evaluated_motion_geometry.py'),run_name='__main__')
        raise AssertionError('Animated camera escaped lock')
    except ValueError as exc:
        assert 'CAMERA_CHANGED' in str(exc),str(exc)
assert not bpy.data.objects['body'].hide_render and bpy.data.objects['body'].data.vertices[0].co.z<2
checks.append('approved_file_reload_discards_live_mesh_and_visibility_edits')
assert (out/'native_1.png').is_file() and not (out/'native_2.png').exists() and not (out/'geometry.json').exists()
checks.append('later_camera_keyframe_blocked_before_second_render_and_completion')
g.write(out/'result.json',{'status':'PASS_HARNESS_REGRESSIONS_ONLY','checks':checks,
    'artwork_status':'SYNTHETIC_DO_NOT_PROMOTE','authorization_mocked_for_reload_test':True,
    'native_resolution':[1920,1920],'complete_motion_receipt_created':False})
print('GENERATION_PREFLIGHT_BLENDER_REGRESSIONS_COMPLETE')
