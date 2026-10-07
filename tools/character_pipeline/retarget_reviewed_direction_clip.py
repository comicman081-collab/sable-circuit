"""Bake one actual Tripo forward cycle onto a source-preserving character skin.

The profile supplies the target proportions; the reference supplies motion.
This diagnostic exports actual bones and skin data for Godot, not an atlas of
static placeholders. It does not approve missing views or firing animations.
"""
import argparse
import os
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import connected_rgba_surface_harness as adapter
import source_art_intake as intake
import source_weapon_socket as sockets


def child(args):
    import bpy
    from mathutils import Matrix,Quaternion,Vector

    out=g.local(args.out);inputs=g.read(out/'INPUTS.json')
    for reference in inputs.values():g.resolve(reference)
    if inputs['exporter']!=g.ref(__file__):raise ValueError('EXACT_EXPORTER_REQUIRED')
    surface=g.read(g.resolve(inputs['surface']));reference=g.read(g.resolve(inputs['motion_reference']))
    if surface['blend']!=inputs['blend'] or not surface['closed_edge_incidence']:
        raise ValueError('EXACT_CLOSED_SOURCE_SKIN_REQUIRED')
    if reference['representation']!='evaluated_skeleton_motion':raise ValueError('ACTUAL_MOTION_REQUIRED')
    source_config=g.read(g.resolve(surface['inputs']))
    consumed={'generation_harness':g.__file__,'adapter':adapter.__file__,'intake':intake.__file__,
              'socket_exporter':sockets.__file__, 'verifier':ROOT/'tools/character_pipeline/verify_existing_source.py'}
    for key,path in consumed.items():
        if inputs[key]!=g.ref(path):raise ValueError('EXACT_CONSUMED_IMPLEMENTATION_REQUIRED:'+key)
    if surface['builder']!=g.ref(adapter.__file__):raise ValueError('REVIEWED_CONNECTED_SURFACE_REQUIRED')
    for key in ('source','rgba','mask','depth','annotation','profile','source_receipt'):g.resolve(source_config[key])
    authority=adapter.checked_authority(g.resolve(source_config['source_receipt']),source_config['python_runtime'],out/'cache',source_config['python_runtime_sha256'])
    if authority['bindings']!=source_config['source_authority_bindings']:raise ValueError('SOURCE_AUTHORITY_CHANGED')
    profile=g.read(g.resolve(source_config['profile']))
    yaw=profile.get('reference_forward_yaw_degrees')
    if not isinstance(yaw,(int,float)) or not math.isfinite(yaw):raise ValueError('EXPLICIT_VIEW_ALIGNMENT_REQUIRED')
    alignment=Matrix.Rotation(math.radians(yaw),4,'Z')
    if inputs['motion_reference']!=g.ref(ROOT/'art_src/motion_reference/tripo_run_20260908/skeletal_pack_r04/MOTION_PACK.json'):
        raise ValueError('EXACT_R04_REFERENCE_REQUIRED')
    for ref in reference['inputs'].values():g.resolve(ref)
    if reference['coordinate_system']!='godot_y_up':raise ValueError('EXPLICIT_REFERENCE_AXES_REQUIRED')
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(inputs['blend'])),load_ui=False)
    rig=bpy.data.objects[surface['rig_name']];mesh=bpy.data.objects[surface['mesh_name']]
    consumed_images=[]
    for material in mesh.data.materials:
        if material and material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image:
                    if node.image.packed_file:raise ValueError('UNREVIEWED_PACKED_SOURCE')
                    consumed_images.append(g.ref(Path(bpy.path.abspath(node.image.filepath))))
    if consumed_images!=[source_config['rgba']]:raise ValueError('EXACT_VISIBLE_SOURCE_TEXTURE_REQUIRED')
    scene=bpy.context.scene
    scene.cycles.samples=64
    scene.cycles.use_denoising=False
    axes=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));inverse=axes.inverted()

    def unpack(row):
        q=row['q'];matrix=Quaternion((q[3],q[0],q[1],q[2])).to_matrix().to_4x4()
        for i in range(3):
            for j in range(3):matrix[i][j]*=row['s'][j]
        matrix.translation=Vector(row['p']);return matrix

    def encode(matrix):
        p,q,s=(axes@matrix@inverse).decompose()
        if q.w<0:q.negate()
        return {'p':list(p),'q':[q.x,q.y,q.z,q.w],'s':list(s)}

    def source_global(rows):
        matrices=[]
        for i,bone in enumerate(reference['bone_order']):
            local=unpack(rows[i]);parent=bone['parent']
            matrices.append(matrices[parent]@local if parent>=0 else local)
        return {b['name']:alignment@inverse@matrices[i]@axes for i,b in enumerate(reference['bone_order'])}

    rest=source_global([b['rest'] for b in reference['bone_order']])
    target_rest={bone.name:rig.matrix_world@bone.matrix_local for bone in rig.data.bones}
    def leg_length(bones):
        return sum((bones['thigh_'+s].translation-bones['calf_'+s].translation).length+
                   (bones['calf_'+s].translation-bones['foot_'+s].translation).length for s in ('l','r'))/2
    ratio=leg_length(target_rest)/leg_length(rest)
    lower={'pelvis',*[stem+'_'+side for side in ('l','r') for stem in ('thigh','calf','foot','ball')]}
    bones=sorted(rig.data.bones,key=lambda b:(len(b.parent_recursive),b.name))
    indices={bone.name:i for i,bone in enumerate(bones)}
    bone_order=[{'name':bone.name,'parent':indices[bone.parent.name] if bone.parent else -1,
                 'rest':encode(bone.parent.matrix_local.inverted()@bone.matrix_local if bone.parent
                               else rig.matrix_world@bone.matrix_local)} for bone in bones]
    clip=reference['clips']['run/forward']
    if len(clip['frames'])!=49:raise ValueError('EXACT_49_SAMPLE_REFERENCE_REQUIRED')
    frames=[];evaluated=[];captures=[];native_captures=[]
    scene.render.resolution_x=1920;scene.render.resolution_y=1080
    # Native battle-scale capture, not an enlarged couture review.
    scene.camera.data.ortho_scale=1920*1.72/224
    scene.camera.location.x=0;scene.camera.location.z=.86
    scene.camera.rotation_euler=(Vector((0,0,.86))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('BattleScaleDiagnosticWorld')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.009,.017,.024,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
    scene.render.fps=768;scene.render.fps_base=10
    # Do not insert keys while evaluating new poses: the newly active action
    # would reapply the current scene-frame key during dependency updates.
    # Capture/evaluate all manual retarget poses first, then author the action.
    rig.animation_data_clear()
    for sample,frame in enumerate(clip['frames']):
        pose=source_global(frame['poses'])
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.bone.parent_recursive)):
            target=target_rest[bone.name]
            rotation=(pose[bone.name].to_quaternion()@rest[bone.name].to_quaternion().inverted()
                      @target.to_quaternion()) if bone.name in lower else target.to_quaternion()
            if bone.name=='pelvis':
                head=target.translation+(pose['pelvis'].translation-rest['pelvis'].translation)*ratio
            else:
                parent=bone.parent
                head=rig.matrix_world@(parent.matrix@parent.bone.matrix_local.inverted()@bone.bone.head_local)
            matrix=rotation.to_matrix().to_4x4();matrix.translation=head
            bone.matrix=rig.matrix_world.inverted()@matrix
            bpy.context.view_layer.update()
        poses=[]
        for bone in bones:
            pb=rig.pose.bones[bone.name]
            local=pb.parent.matrix.inverted()@pb.matrix if pb.parent else rig.matrix_world@pb.matrix
            poses.append(encode(local))
        frames.append({'time_s':frame['time_s'],'poses':poses})
        actual=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());vertices=actual.to_mesh()
        try:
            floor=min((actual.matrix_world@v.co).z for v in vertices.vertices)
            joints={pb.name:list(axes@(rig.matrix_world@pb.head)) for pb in rig.pose.bones}
            evaluated.append({'sample_index':sample,'min_evaluated_mesh_z_m':floor,'joints_godot_m':joints})
        finally:actual.to_mesh_clear()
        if args.capture and sample%3==0 and sample<48:
            path=out/f'BATTLE_SCALE_{sample:02d}_1920x1080.png'
            scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            captures.append({'sample_index':sample,'time_s':frame['time_s'],'image':g.ref(path),
                             'native_resolution':[1920,1080],'nominal_character_height_px':224})
        if args.capture and sample in (0,12,24,36):
            scale_before=scene.camera.data.ortho_scale
            scene.render.resolution_y=1920
            scene.camera.data.ortho_scale=1920*source_config['metres_per_pixel']
            path=out/f'ORIGINAL_SCALE_{sample:02d}_1920x1920.png'
            scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            native_captures.append({'sample_index':sample,'time_s':frame['time_s'],
                'image':g.ref(path),'native_resolution':[1920,1920],
                'source_pixel_to_render_pixel_ratio':1.0,'source_upscaled':False})
            scene.render.resolution_y=1080
            scene.camera.data.ortho_scale=scale_before

    output_clip={'duration_s':clip['duration_s'],'distance_m':clip['distance_m']*ratio,'frames':frames}
    pack={'schema':1,'representation':'evaluated_skeleton_motion','coordinate_system':'godot_y_up',
          'forward_axis':list((axes@alignment@inverse).to_3x3()@Vector(reference['forward_axis'])),'bone_order':bone_order,'humanoid_roles':reference['humanoid_roles'],
          'clips':{'run/forward':output_clip},'scope':'ONE_SOURCE_VIEW_FORWARD_CLIP_DIAGNOSTIC',
          'inputs':inputs,'retarget_leg_ratio':ratio,'source_distance_scaled_by_target_leg_ratio':True,
          'production_ready':False,'missing':['walk','relative_strafe','backward','rifle_aim','fire','other_source_views']}
    g.write(out/'MOTION_PACK.json',pack)

    uv=[None]*len(mesh.data.vertices)
    for polygon in mesh.data.polygons:
        if polygon.material_index!=0:continue
        for loop in polygon.loop_indices:
            uv[mesh.data.loops[loop].vertex_index]=list(mesh.data.uv_layers.active.data[loop].uv)
    used=sorted({v for polygon in mesh.data.polygons if polygon.material_index==0 for v in polygon.vertices})
    remap={original:i for i,original in enumerate(used)}
    positions=[];texcoords=[];bone_ids=[];weights=[]
    for i in used:
        vertex=mesh.data.vertices[i]
        positions.extend(axes@(mesh.matrix_world@vertex.co))
        # Godot UV Y is top-down; Blender UV Y is bottom-up.
        texcoords.extend((uv[i][0],1-uv[i][1]))
        binding=sorted([(indices[mesh.vertex_groups[item.group].name],item.weight) for item in vertex.groups],
                       key=lambda item:-item[1])
        if len(binding)>4 or abs(sum(w for _,w in binding)-1)>1e-5:raise ValueError('NORMALIZED_FOUR_WEIGHT_SKIN_REQUIRED')
        binding.extend([(0,0)]*(4-len(binding)))
        bone_ids.extend(i for i,_ in binding);weights.extend(w for _,w in binding)
    triangles=[]
    for polygon in mesh.data.polygons:
        if polygon.material_index!=0:continue
        if len(polygon.vertices)!=3:raise ValueError('TRIANGULATED_FRONT_REQUIRED')
        triangles.extend(remap[v] for v in polygon.vertices)
    skin={'schema':1,'representation':'source_surface_skin','coordinate_system':'godot_y_up',
          'source_rgba':source_config['rgba'],'source':source_config['source'],
          'source_receipt':source_config['source_receipt'],'profile':source_config['profile'],
          'surface_report':inputs['surface'],'bone_order':bone_order,
          'positions':positions,'uv':texcoords,'bones':bone_ids,'weights':weights,'indices':triangles,
          'visible_mesh_scope':'exact source-covered front; unobserved closure intentionally omitted',
          'production_ready':False}
    skin['weapon_binding']=sockets.export(mesh,g.pixels(g.resolve(source_config['rgba'])),profile,axes)
    g.write(out/'SOURCE_SKIN.json',skin)
    g.write(out/'EVALUATED_MOTION.json',{'inputs':inputs,'samples':evaluated,
                                     'captures':captures,'original_scale_captures':native_captures,
                                     'per_frame_floor_correction':False})
    for sample,frame in enumerate(frames):
        for bone,row in zip(bones,frame['poses']):
            local_rest=(bone.parent.matrix_local.inverted()@bone.matrix_local if bone.parent
                        else rig.matrix_world@bone.matrix_local)
            local_pose=inverse@unpack(row)@axes
            basis=local_rest.inverted()@local_pose
            location,rotation,scale=basis.decompose()
            pb=rig.pose.bones[bone.name]
            pb.rotation_mode='QUATERNION';pb.location=location;pb.rotation_quaternion=rotation;pb.scale=scale
            for property_name in ('location','rotation_quaternion','scale'):
                pb.keyframe_insert(data_path=property_name,frame=sample)
    playback_error=0.0
    for sample in (0,12,24,36,48):
        scene.frame_set(sample);bpy.context.view_layer.update()
        for bone,row in zip(bones,frames[sample]['poses']):
            pb=rig.pose.bones[bone.name]
            actual=pb.parent.matrix.inverted()@pb.matrix if pb.parent else rig.matrix_world@pb.matrix
            expected=inverse@unpack(row)@axes
            playback_error=max(playback_error,max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
    if playback_error>1e-5:raise ValueError('NATIVE_KEYFRAME_PLAYBACK_DOES_NOT_MATCH_RETARGET:'+str(playback_error))
    scene.frame_start=0;scene.frame_end=47;scene.frame_set(0)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'SOURCE_SKIN_RUN.blend'))
    g.write(out/'COMPLETION.json',{'inputs':g.ref(out/'INPUTS.json'),'pack':g.ref(out/'MOTION_PACK.json'),
        'skin':g.ref(out/'SOURCE_SKIN.json'),'blend':g.ref(out/'SOURCE_SKIN_RUN.blend'),
        'evaluated':g.ref(out/'EVALUATED_MOTION.json'),'actual_bone_samples':49,'captured_frames':len(captures),
        'original_scale_captured_frames':len(native_captures),
        'native_keyframe_playback_max_matrix_error':playback_error,
        'scope':'ONE_FORWARD_RUN_SOURCE_SKIN_DIAGNOSTIC','production_ready':False})


def run(args):
    out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_OUTPUT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    surface=g.read(args.surface)
    g.write(out/'INPUTS.json',{'surface':g.ref(args.surface),'blend':surface['blend'],
                             'motion_reference':g.ref(args.pack),'exporter':g.ref(__file__),
                             'generation_harness':g.ref(g.__file__), 'adapter':g.ref(adapter.__file__),
                             'intake':g.ref(intake.__file__), 'socket_exporter':g.ref(sockets.__file__),
                             'verifier':g.ref(ROOT/'tools/character_pipeline/verify_existing_source.py')})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
             '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
             '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out)]
    if args.capture:command.append('--capture')
    with (out/'blender.log').open('w',encoding='utf8') as log:
        subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                       timeout=480,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    print('ACTUAL_SOURCE_SKIN_FORWARD_CLIP_EXPORTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--surface');parser.add_argument('--pack');parser.add_argument('--out',required=True)
    parser.add_argument('--capture',action='store_true');parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
