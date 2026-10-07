"""Astra-only diagnostic: actual licensed VRM skin + UAL rest-space retarget.

No MICA art, source receipt, production output, or promotion is authored here.
One explicitly selected locomotion pilot only, with one native pose render; a
full motion/aim batch is not allowed by this entry point. The saved scene is a
starting point for pose-guide review, never visible MICA art.
"""
import argparse
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

UAL=ROOT/'assets/external/quaternius/ual1/UAL1_Standard.glb'
LICENSE=ROOT/'assets/external/quaternius/licenses/UAL1_License.txt'
MAPPING={'hips':'pelvis','spine':'spine_01','chest':'spine_03','neck':'neck_01','head':'Head',
 'leftUpperLeg':'thigh_l','leftLowerLeg':'calf_l','leftFoot':'foot_l','leftToes':'ball_l',
 'rightUpperLeg':'thigh_r','rightLowerLeg':'calf_r','rightFoot':'foot_r','rightToes':'ball_r',
 'leftShoulder':'clavicle_l','leftUpperArm':'upperarm_l','leftLowerArm':'lowerarm_l','leftHand':'hand_l',
 'rightShoulder':'clavicle_r','rightUpperArm':'upperarm_r','rightLowerArm':'lowerarm_r','rightHand':'hand_r'}


def world_rest(rig,bone): return rig.matrix_world @ rig.data.bones[bone].matrix_local


def body_basis(rig,hips,left,right,head):
    l=(world_rest(rig,left).translation-world_rest(rig,right).translation).normalized()
    up=(world_rest(rig,head).translation-world_rest(rig,hips).translation).normalized()
    forward=l.cross(up).normalized(); l=up.cross(forward).normalized()
    return Matrix((forward,l,up)).transposed()


def native_pose(scene,meshes,out,screen_direction):
    points=[ob.matrix_world@Vector(c) for ob in meshes for c in ob.bound_box]
    low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center=(low+high)*.5; height=high.z-low.z
    camera_data=bpy.data.cameras.new('Diagnostic_Profile_Camera')
    camera=bpy.data.objects.new('Diagnostic_Profile_Camera',camera_data)
    scene.collection.objects.link(camera); scene.camera=camera
    # The original +X camera reads the UAL forward axis toward screen-left.
    # Use the opposite side for an east/screen-right guide and record it.
    camera_x=-5 if screen_direction=='E' else 5
    camera.location=center+Vector((camera_x,-.1,.6))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO'; camera_data.ortho_scale=max(height,high.x-low.x)*1.35
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    if scene.world is None: scene.world=bpy.data.worlds.new('DiagnosticWorld')
    scene.display.shading.background_type='WORLD'; scene.world.color=(.035,.045,.065)
    scene.render.resolution_x=1920; scene.render.resolution_y=1920
    scene.render.resolution_percentage=100; scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
    scene.render.filepath=str(out/'FIRST_RETARGET_POSE_NATIVE_1920.png')
    scene.render.threads_mode='FIXED'; scene.render.threads=2
    bpy.ops.render.render(write_still=True)
    return g.ref(scene.render.filepath)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-result',required=True); p.add_argument('--out',required=True)
    p.add_argument('--action',choices=('Walk_Loop','Jog_Fwd_Loop','Sprint_Loop'),default='Walk_Loop')
    p.add_argument('--screen-direction',choices=('E','W'),default='E')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('UNREVIEWED_RETARGET_DIAGNOSTIC_ONLY')
    if (out/'retarget_result.json').exists(): raise ValueError('FRESH_PROBE_REQUIRED')
    imported=g.read(a.import_result)
    if imported['errors']: raise ValueError('IMPORT_HAS_UNRESOLVED_ERRORS')
    blend=g.resolve(imported['blend'])
    if 'CC0 1.0' not in LICENSE.read_text(encoding='utf-8'): raise ValueError('UAL_LICENSE_NOT_CLEARED')
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    target=bpy.data.objects[imported['rig']]; target.name='SeedSan_Licensed_Target_Rig'
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    # The reference model retains its real weighted geometry and material slots.
    # Workbench is anatomy diagnostics only, not MICA/ImageGen texture production.
    bpy.ops.import_scene.gltf(filepath=str(UAL))
    source=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o!=target)
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and ob not in meshes: ob.hide_render=True
    source.animation_data_create()
    for track in list(source.animation_data.nla_tracks): source.animation_data.nla_tracks.remove(track)
    action=bpy.data.actions[a.action]; source.animation_data.action=action
    if action.slots: source.animation_data.action_slot=action.slots[0]
    target.animation_data_clear()
    target.animation_data_create()
    baked=bpy.data.actions.new('SeedSan_UAL_'+a.action+'_REVIEW_REQUIRED'); target.animation_data.action=baked
    roles=imported['humanoid_mapping']
    mapping={roles[k]:v for k,v in MAPPING.items()}
    if any(s not in source.data.bones or t not in target.data.bones for t,s in mapping.items()):
        raise ValueError('EXPLICIT_HUMANOID_MAPPING_NOT_PRESENT')
    s_basis=body_basis(source,'pelvis','thigh_l','thigh_r','Head')
    t_basis=body_basis(target,roles['hips'],roles['leftUpperLeg'],roles['rightUpperLeg'],roles['head'])
    correction=t_basis @ s_basis.inverted()
    src_rest={s:world_rest(source,s) for s in mapping.values()}
    dst_rest={t:world_rest(target,t) for t in mapping}
    scale=(dst_rest[roles['head']].translation-dst_rest[roles['hips']].translation).length/(
        src_rest['Head'].translation-src_rest['pelvis'].translation).length
    scene=bpy.context.scene; scene.render.fps=24
    end=float(action.frame_range[1]); start=float(action.frame_range[0])
    ordered=sorted(mapping,key=lambda name:len(target.data.bones[name].parent_recursive))
    # Observe actual boot vertices, chosen once in the unposed imported mesh.
    soles={}; sole_mesh=next(ob for ob in meshes if all(roles[k] in ob.vertex_groups for k in ('leftFoot','rightFoot')))
    for side in ('left','right'):
        bone=roles[side+'Foot']; group=sole_mesh.vertex_groups[bone].index
        vertices=[v for v in sole_mesh.data.vertices if any(w.group==group and w.weight>.5 for w in v.groups)]
        if not vertices: raise ValueError('NO_REAL_WEIGHTED_FOOT_VERTICES:'+side)
        z=min((sole_mesh.matrix_world@v.co).z for v in vertices)
        soles[side]=[v.index for v in vertices if (sole_mesh.matrix_world@v.co).z<z+.012]
    frames=[]; max_rotation_error=0.0
    for i in range(25):
        frame=start+(end-start)*i/24
        scene.frame_set(int(frame),subframe=frame-int(frame))
        desired={}
        for target_name in ordered:
            source_name=mapping[target_name]; pb=target.pose.bones[target_name]
            pb.rotation_mode='QUATERNION'
            sw=source.matrix_world@source.pose.bones[source_name].matrix
            delta=sw.to_3x3().normalized()@src_rest[source_name].to_3x3().normalized().inverted()
            rotation=correction@delta@correction.inverted()@dst_rest[target_name].to_3x3().normalized()
            if target_name==roles['hips']:
                head=dst_rest[target_name].translation+correction@(sw.translation-src_rest[source_name].translation)*scale
            else:
                parent=pb.parent
                parent_deform=parent.matrix@parent.bone.matrix_local.inverted() if parent else Matrix.Identity(4)
                head=target.matrix_world@(parent_deform@pb.bone.head_local)
            world=rotation.to_4x4(); world.translation=head
            pb.matrix=target.matrix_world.inverted()@world
            bpy.context.view_layer.update()
            actual=(target.matrix_world@pb.matrix).to_quaternion()
            error=math.degrees(actual.rotation_difference(rotation.to_quaternion()).angle)
            max_rotation_error=max(max_rotation_error,min(error,360-error))
            desired[target_name]=[list(r) for r in world]
            # Preserve the UAL timeline: 0..32 @24Hz must remain 1.333s, not
            # become a 0..24 @24Hz (1s) clip merely because we sampled 25 poses.
            pb.keyframe_insert('location',frame=frame); pb.keyframe_insert('rotation_quaternion',frame=frame)
            pb.keyframe_insert('scale',frame=frame)
        deps=scene.evaluated_depsgraph_get() if hasattr(scene,'evaluated_depsgraph_get') else bpy.context.evaluated_depsgraph_get()
        evaluated=sole_mesh.evaluated_get(deps); mesh=evaluated.to_mesh()
        try:
            positions={side:[list(evaluated.matrix_world@mesh.vertices[index].co) for index in ids] for side,ids in soles.items()}
        finally: evaluated.to_mesh_clear()
        frames.append({'sample':i,'source_frame':frame,'actual_sole_vertices_world_m':positions})
    # Re-evaluate baked playback; intended retarget matrices are not skin evidence.
    playback=[]
    for i in range(25):
        frame=start+(end-start)*i/24
        scene.frame_set(int(frame),subframe=frame-int(frame)); deps=bpy.context.evaluated_depsgraph_get()
        evaluated=sole_mesh.evaluated_get(deps); mesh=evaluated.to_mesh()
        try:
            positions={side:[list(evaluated.matrix_world@mesh.vertices[index].co) for index in ids]
                       for side,ids in soles.items()}
            centres={side:[sum(p[i] for p in positions[side])/len(positions[side]) for i in range(3)]
                     for side in ('left','right')}
            playback.append({'frame':frame,'time_s':(frame-start)/scene.render.fps,
                'actual_sole_vertices_world_m':positions,'sole_centres_world_m':centres,
                'sole_min_z_m':{side:min(p[2] for p in positions[side]) for side in ('left','right')},
                'horizontal_stride_m':math.dist(centres['left'][:2],centres['right'][:2])})
        finally: evaluated.to_mesh_clear()
    global_ground=min(row['sole_min_z_m'][side] for row in playback for side in ('left','right'))
    planted=[row for row in playback if min(row['sole_min_z_m'].values())<=global_ground+.012]
    selected=max(planted,key=lambda row:row['horizontal_stride_m'])
    support=min(selected['sole_min_z_m'],key=selected['sole_min_z_m'].get)
    # This is only a grounded-window probe.  A low sole does not identify
    # contact/down/passing by itself; phase naming requires the whole cycle,
    # temporal ordering and an independent visual review.
    selected_phase='unclassified_grounded_window'
    source.hide_render=True
    scene.frame_start=int(start); scene.frame_end=math.ceil(end)
    selected_frame=selected['frame']; scene.frame_set(int(selected_frame),subframe=selected_frame-int(selected_frame))
    image=native_pose(scene,meshes,out,a.screen_direction)
    output_blend=out/('SeedSan_UAL_'+a.action+'_DIAGNOSTIC.blend')
    if output_blend.exists(): raise ValueError('NO_BLEND_OVERWRITE')
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    g.write(out/'retarget_result.json',{'status':'HOLD_NATIVE_POSE_AND_RETARGET_REVIEW','production_ready':False,
        'model':imported['model'],'input_blend':imported['blend'],'output_blend':g.ref(output_blend),
        'generator':g.ref(__file__),'ual':g.ref(UAL),'ual_license':g.ref(LICENSE),'action':a.action,
        'source_frame_range':[start,end],'source_fps':24,'baked_frame_range':[start,end],'baked_fps':24,
        'source_duration_seconds':(end-start)/24,'baked_duration_seconds':(end-start)/24,
        'cadence_transform':'identity_preserve_source_time',
        'screen_direction':a.screen_direction,'selected_pose_frame':selected_frame,
        'selected_pose_phase':selected_phase,'selected_support_foot':support,
        'selected_horizontal_stride_m':selected['horizontal_stride_m'],'global_ground_z_m':global_ground,
        'mapping':mapping,'source_body_basis':[list(r) for r in s_basis],
        'target_body_basis':[list(r) for r in t_basis],'translation_scale':scale,
        'max_assigned_bone_orientation_error_degrees':max_rotation_error,
        'sole_mesh':sole_mesh.name,'sole_vertex_ids':soles,'frames':frames,'baked_playback':playback,'first_native_pose':image,
        'limitations':['One diagnostic locomotion action only; not MICA appearance','No source/pose production receipt',
            'Not world-contact/cadence calibrated','No 8-direction, fire or runtime approval',
            'Workbench material colors are anatomy diagnostics, not source-art replacement']})


if __name__=='__main__': main()
