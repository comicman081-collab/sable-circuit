"""One source-preserving neutral depth/REST probe. Never exports motion or promotes."""
import argparse
from collections import Counter
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import reviewed_rgba_surface_harness as authority_adapter
import source_surface_sampling as sampling


def child(args):
    import bpy
    import numpy as np
    from mathutils import Matrix,Vector
    out = g.local(args.out)
    inputs = g.read(out/'INPUTS.json')
    for reference in inputs.values():
        g.resolve(reference)
    for key,path in {'builder':__file__,'generation_harness':g.__file__,
        'authority_adapter':authority_adapter.__file__,'surface_sampler':sampling.__file__,
        'source_verifier':ROOT/'tools/character_pipeline/verify_existing_source.py',
        'source_intake':ROOT/'tools/character_pipeline/source_art_intake.py',
        'runtime_projection':ROOT/'scripts/animation/source_projection.gd',
        'runtime_viewport':ROOT/'scripts/animation/source_skin_viewport.gd',
        'runtime_player':ROOT/'scripts/animation/skeletal_motion_player.gd'}.items():
        if inputs[key] != g.ref(path):
            raise ValueError('EXACT_CONSUMED_IMPLEMENTATION_REQUIRED:'+key)
    surface = g.read(g.resolve(inputs['base_surface']))
    support = g.read(g.resolve(inputs['support']))
    ik = g.read(g.resolve(inputs['ik']))
    for record in [surface,support,ik]:
        if isinstance(record.get('inputs'),dict) and 'path' not in record['inputs']:
            for reference in record['inputs'].values():
                g.resolve(reference)
    if ik['inputs']['support'] != inputs['support'] or ik['failures']:
        raise ValueError('EXACT_FEASIBLE_SUPPORT_AND_TARGET_SOLVE_REQUIRED')
    if ik['root_floor_correction'] or ik['limb_stretch']:
        raise ValueError('ROOT_CORRECTION_OR_LIMB_STRETCH_FORBIDDEN')
    skin = g.read(g.resolve(support['inputs']['skin']))
    if skin['surface_report'] != inputs['base_surface']:
        raise ValueError('NUMERIC_SUPPORT_MUST_MATCH_ACTUAL_BASE_SURFACE')
    config = g.read(g.resolve(surface['inputs']))
    for key in ['source_receipt','source','rgba','annotation','profile','mask','depth']:
        g.resolve(config[key])
    authority = authority_adapter.checked_authority(g.resolve(config['source_receipt']),
        config['python_runtime'],out/'cache',config['python_runtime_sha256'])
    if authority['bindings'] != config['source_authority_bindings']:
        raise ValueError('SOURCE_AUTHORITY_CHANGED')
    if skin['source_rgba'] != config['rgba'] or skin['profile'] != config['profile']:
        raise ValueError('EXACT_ORIGINAL_APPEARANCE_AND_PROFILE_REQUIRED')
    joint = g.read(g.resolve(support['inputs']['joints']))
    for reference in joint['inputs'].values():
        g.resolve(reference)
    reference = g.read(g.resolve(joint['inputs']['reference']))
    for dependency in reference['inputs'].values():
        g.resolve(dependency)
    if reference['inputs']['calibration'] != ik['inputs']['calibration']:
        raise ValueError('EXACT_REFERENCE_CONTACT_CALIBRATION_REQUIRED')
    proposed = np.load(g.resolve(support['proposed_positions']),allow_pickle=False)
    rest = np.load(g.resolve(ik['proposed_rest']),allow_pickle=False)
    if proposed.shape != (len(skin['positions'])//3,3) or rest.shape != (len(skin['bone_order']),4,4):
        raise ValueError('EXACT_PROPOSED_GEOMETRY_AND_REST_SHAPES_REQUIRED')
    if not np.isfinite(proposed).all() or not np.isfinite(rest).all():
        raise ValueError('FINITE_PROPOSED_BINDING_REQUIRED')
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(surface['blend'])),load_ui=False)
    mesh = bpy.data.objects[surface['mesh_name']]
    rig = bpy.data.objects[surface['rig_name']]
    if any(o.type=='MESH' and o!=mesh and not o.hide_render for o in bpy.data.objects):
        raise ValueError('NO_OTHER_VISIBLE_GEOMETRY_ALLOWED')
    if mesh.matrix_world != Matrix.Identity(4) or rig.matrix_world != Matrix.Identity(4):
        raise ValueError('EXACT_UNTRANSFORMED_SOURCE_BINDING_REQUIRED')
    images = []
    for material in mesh.data.materials:
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:
                    if node.image.packed_file:
                        raise ValueError('PACKED_REPLACEMENT_IMAGE_FORBIDDEN')
                    images.append(g.ref(Path(bpy.path.abspath(node.image.filepath))))
    if not images or any(image != config['rgba'] for image in images):
        raise ValueError('EXACT_ORIGINAL_RGBA_MATERIAL_REQUIRED')
    front = sorted({v for face in mesh.data.polygons if face.material_index==0 for v in face.vertices})
    count = len(front)
    if front != list(range(count)) or len(mesh.data.vertices) != count*2:
        raise ValueError('EXACT_FRONT_AND_TRANSPARENT_CLOSURE_LAYOUT_REQUIRED')
    old = np.asarray([tuple(v.co) for v in mesh.data.vertices])
    axes = np.array([[1,0,0],[0,0,1],[0,-1,0]],dtype=float)
    if np.max(np.abs(old[:count]@axes.T-np.asarray(skin['positions']).reshape(-1,3)))>1e-6:
        raise ValueError('BASE_NATIVE_VERTICES_DIFFER_FROM_EXPORTED_SOURCE_SKIN')
    before_weights = [[(v.group,v.weight) for v in vertex.groups] for vertex in mesh.data.vertices]
    before_uv = [[tuple(loop.uv) for loop in layer.data] for layer in mesh.data.uv_layers]
    before_faces = [(tuple(face.vertices),face.material_index) for face in mesh.data.polygons]
    angle = math.radians(joint['configuration']['elevation_degrees'])
    sine,cosine = math.sin(angle),math.cos(angle)
    toward_camera = np.array([0,-cosine,sine])
    thickness = -old[:count,1]+old[count:,1]
    if np.any(thickness<=0):
        raise ValueError('POSITIVE_EXISTING_TRANSPARENT_CLOSURE_REQUIRED')
    all_positions = np.concatenate([proposed,proposed-thickness[:,None]*toward_camera])
    mesh.data.vertices.foreach_set('co',all_positions.astype(np.float32).ravel())
    mesh.data.update()
    rig.animation_data_clear()
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    heads = joint['blender_world_bone_heads']
    tails = {'pelvis':'spine_01','spine_01':'spine_02','spine_02':'spine_03','spine_03':'neck_01','neck_01':'Head'}
    for side in ['l','r']:
        tails.update({a+'_'+side:b+'_'+side for a,b in [('thigh','calf'),('calf','foot'),('foot','ball'),
            ('clavicle','upperarm'),('upperarm','lowerarm'),('lowerarm','hand')]})
    for i,row in enumerate(skin['bone_order']):
        bone = rig.data.edit_bones[row['name']]
        bone.matrix = Matrix(rest[i].tolist())
        bone.length = float(np.linalg.norm(np.asarray(heads[tails[row['name']]])-heads[row['name']])) if row['name'] in tails else .07
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    native_rest = np.asarray([np.asarray(rig.data.bones[row['name']].matrix_local)
        for row in skin['bone_order']])
    rest_error = float(np.max(np.abs(native_rest-rest)))
    rest_head_error = float(np.max(np.linalg.norm(native_rest[:,:3,3]-rest[:,:3,3],axis=1)))
    rest_basis_error = float(np.max(np.abs(native_rest[:,:3,:3]-rest[:,:3,:3])))
    if rest_head_error>1e-6 or rest_basis_error>1e-5:
        raise ValueError('NATIVE_REST_DOES_NOT_MATCH_NUMERIC_BINDING')
    if before_weights != [[(v.group,v.weight) for v in vertex.groups] for vertex in mesh.data.vertices]:
        raise ValueError('ORIGINAL_SOURCE_WEIGHTS_CHANGED')
    if before_uv != [[tuple(loop.uv) for loop in layer.data] for layer in mesh.data.uv_layers]:
        raise ValueError('ORIGINAL_SOURCE_UV_CHANGED')
    if before_faces != [(tuple(face.vertices),face.material_index) for face in mesh.data.polygons]:
        raise ValueError('ORIGINAL_TOPOLOGY_OR_MATERIAL_ASSIGNMENT_CHANGED')
    counts = Counter(tuple(sorted((a,b))) for face in mesh.data.polygons for a,b in zip(list(face.vertices),list(face.vertices)[1:]+list(face.vertices)[:1]))
    if not counts or any(value != 2 for value in counts.values()):
        raise ValueError('CLOSED_SOURCE_SURFACE_REQUIRED')
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data = evaluated.to_mesh()
    try:
        actual = np.asarray([tuple(v.co) for v in data.vertices])[:count]
    finally:
        evaluated.to_mesh_clear()
    if np.max(np.abs(actual-proposed))>1e-6:
        raise ValueError('NATIVE_NEUTRAL_GEOMETRY_DIFFERS_FROM_NUMERIC_SUPPORT')
    fixed_floor = min(float(sampling.sample_positions(actual,binding)[:,2].min())
                      for binding in ik['visible_sole_bindings'].values())
    if abs(fixed_floor-ik['fixed_neutral_floor_m'])>1e-6:
        raise ValueError('NATIVE_NEUTRAL_SOLE_FLOOR_DIFFERS_FROM_BOUND_PROBE')
    np.save(out/'ACTUAL_NATIVE_REST_MATRICES_BLENDER.npy',native_rest,allow_pickle=False)
    scene = bpy.context.scene
    width,height = config['native_size']
    cx,ground = config['ground_pixel']
    mpp = config['metres_per_pixel']
    center = Vector(((width*.5-cx)*mpp*cosine,0,(ground-height*.5)*mpp))
    scene.camera.location = center+Vector((0,-cosine,sine))*6
    scene.camera.rotation_euler = (center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 1920*mpp*cosine
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.render.film_transparent = True
    scene.render.filepath = str(out/'NEUTRAL_ORIGINAL_ART_1920.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'PROJECTED_SOURCE_NEUTRAL.blend'))
    projection = {'schema':1,'kind':'source_orthographic_elevation','elevation_degrees':joint['configuration']['elevation_degrees'],
        'camera_center_height_m':.875,'orthographic_size_m':2*cosine,'assumption':'rig projection, not measured source camera'}
    g.write(out/'NEUTRAL_REPORT.json',{'inputs':g.ref(out/'INPUTS.json'),'base_surface':inputs['base_surface'],
        'source_receipt':config['source_receipt'],'source_rgba':config['rgba'],'source_profile':config['profile'],
        'rig_name':rig.name,'mesh_name':mesh.name,'visible_front_vertex_count':count,
        'native_rest_max_error':rest_error,'fixed_native_neutral_sole_floor_m':fixed_floor,
        'native_rest_head_max_error_m':rest_head_error,'native_rest_basis_max_component_error':rest_basis_error,
        'native_rest_tolerances':{'head_distance_m':1e-6,'basis_component':1e-5},
        'actual_native_rest':g.ref(out/'ACTUAL_NATIVE_REST_MATRICES_BLENDER.npy'),
        'downstream_rest_authority':'actual_native_rest required; mathematical proposal is not export bind pose',
        'closed_edge_incidence':all(v==2 for v in counts.values()),'authored_projection':projection,
        'native_capture_camera_center_blender':list(center),'native_capture_orthographic_size':scene.camera.data.ortho_scale,
        'original_uv_and_weights_preserved':True,'render':g.ref(out/'NEUTRAL_ORIGINAL_ART_1920.png'),
        'blend':g.ref(out/'PROJECTED_SOURCE_NEUTRAL.blend'),'production_ready':False,
        'scope':'ONE_SOURCE_PRESERVING_NEUTRAL_DEPTH_BINDING_PROBE_NOT_MOTION_APPROVAL'})


def run(args):
    out = g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('QUARANTINED_PROBE_OUTPUT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False)
    (out/'cache').mkdir()
    g.write(out/'INPUTS.json',{'base_surface':g.ref(ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_connected_surface_r01/SURFACE_REPORT.json'),
        'support':g.ref(ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projection_surface_math_r01/PROBE.json'),
        'ik':g.ref(ROOT/'artifacts/quarantine/generation_diagnostics/mica_E_projected_visible_sole_math_r01/PROBE.json'),
        'builder':g.ref(__file__),'generation_harness':g.ref(g.__file__),
        'authority_adapter':g.ref(authority_adapter.__file__),'surface_sampler':g.ref(sampling.__file__),
        'source_verifier':g.ref(ROOT/'tools/character_pipeline/verify_existing_source.py'),
        'source_intake':g.ref(ROOT/'tools/character_pipeline/source_art_intake.py'),
        'runtime_projection':g.ref(ROOT/'scripts/animation/source_projection.gd'),
        'runtime_viewport':g.ref(ROOT/'scripts/animation/source_skin_viewport.gd'),
        'runtime_player':g.ref(ROOT/'scripts/animation/skeletal_motion_player.gd')})
    env = os.environ.copy()
    for key in ['TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX']:
        env[key] = str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    with (out/'blender.log').open('w',encoding='utf8') as log:
        subprocess.run([str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
            '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
            '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out)],
            cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True,
            creationflags=subprocess.CREATE_NO_WINDOW)
    print('ONE_NATIVE_PROJECTED_NEUTRAL_PROBE_COMPLETE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--inside',action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
