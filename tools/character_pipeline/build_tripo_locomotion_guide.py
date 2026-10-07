"""Retarget supplied Tripo motion onto licensed level-neutral reference skin.

Geometry guide only. Does not render SABLE artwork, reconstruct character
appearance, call Tripo, alter original assets, or promote runtime pointers.
"""
from __future__ import annotations
import argparse
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

PACK=ROOT/'art_src/motion_reference/tripo_run_20260908/pack_r03/completion.json'
TARGET=ROOT/'artifacts/quarantine/generation_diagnostics/realistic_base_rig_astra_r4/rig_probe.json'
MAP={'pelvis':'Hip','spine_01':'Waist','spine_02':'Spine01','spine_03':'Spine02',
    'neck_01':'NeckTwist01','Head':'Head',
    **{stem+'_'+side:prefix+native for side,prefix in [('l','L_'),('r','R_')]
       for stem,native in [('thigh','Thigh'),('calf','Calf'),('foot','Foot'),('ball','ToeBase'),
          ('clavicle','Clavicle'),('upperarm','Upperarm'),('lowerarm','Forearm'),('hand','Hand')]}}


def vec(v):return [float(x) for x in v]


def pose_basis(rig,left,right):
    from mathutils import Vector,Matrix
    l=rig.matrix_world@rig.data.bones[left].head_local-rig.matrix_world@rig.data.bones[right].head_local
    l.z=0;l.normalize();up=Vector((0,0,1));forward=l.cross(up).normalized()
    return Matrix((forward,l,up)).transposed()


def sample_vertices(mesh, ids):
    import bpy
    ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());actual=ev.to_mesh()
    try:
        if len(actual.vertices)!=len(mesh.data.vertices):raise ValueError('TOPOLOGY_CHANGED')
        return {s:[vec(ev.matrix_world@actual.vertices[i].co) for i in values] for s,values in ids.items()}
    finally:ev.to_mesh_clear()


def child(args):
    import bpy
    from mathutils import Matrix,Vector,Quaternion
    import tripo_cycle_fit as periodic
    import tripo_motion_reference as inlet
    out=g.local(args.out);inputs=g.read(out/'INPUTS.json')
    for reference in inputs.values():g.resolve(reference)
    if inputs['builder']!=g.ref(__file__):raise ValueError('EXACT_BUILDER_REQUIRED')
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json'),'builder':g.ref(__file__)})
    checked=inlet.verify(PACK);target=g.read(TARGET)
    license_data=g.read(g.resolve(target['license']))
    if license_data.get('license')!='CC0-1.0' or license_data.get('source_blend')!=target['source']:
        raise ValueError('EXACT_CC0_TARGET_LICENSE_REQUIRED')
    g.resolve(target['source'])
    source_report=g.read(PACK.parent/'INSPECTION.json')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(checked['run_reference'])),load_ui=False)
    source=bpy.data.objects[source_report['rig']];source_action=source.animation_data.action
    source_rest={n:source.matrix_world@source.data.bones[n].matrix_local for n in set(MAP.values())}
    source_basis=pose_basis(source,'L_Thigh','R_Thigh')
    start,end=map(float,source_action.frame_range);fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
    duration=(end-start)/fps;period=duration/2
    raw=[]
    for i in range(49):
        frame=start+(end-start)*i/48;bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        raw.append({'frame':frame,'time_s':(frame-start)/fps,
            'matrices':{name:source.matrix_world@source.pose.bones[name].matrix for name in set(MAP.values())}})
    raw_origin=raw[0]['matrices']['Hip'].translation.copy()
    raw_end=raw[-1]['matrices']['Hip'].translation.copy()
    source_leg=sum((source_rest['L_Thigh'].translation-source_rest['L_Foot'].translation).length+
        (source_rest['R_Thigh'].translation-source_rest['R_Foot'].translation).length for _ in [0])/2
    # Load the established licensed control skin, without executing its old
    # builder or keeping any unrelated UAL source geometry visible.
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(target['blend'])),load_ui=False)
    scene=bpy.context.scene;rig=bpy.data.objects[target['rig']];mesh=bpy.data.objects[target['mesh']]
    for ob in scene.objects:
        if ob.type=='MESH':ob.hide_render=ob.name not in license_data['selected_objects']
    rig.animation_data_clear()
    for b in rig.pose.bones:
        b.matrix_basis=Matrix.Identity(4)
        for c in list(b.constraints):b.constraints.remove(c)
    rig.data.pose_position='REST';scene.frame_set(0);bpy.context.view_layer.update()
    soles=target['sole_vertex_ids'];neutral=sample_vertices(mesh,soles)
    neutral_min={s:min(p[2] for p in points) for s,points in neutral.items()};floor=min(neutral_min.values())
    if abs(neutral_min['left']-neutral_min['right'])>.008:raise ValueError('LEVEL_NEUTRAL_TARGET_REQUIRED')
    target_basis=pose_basis(rig,'thigh_l','thigh_r');correction=target_basis@source_basis.inverted()
    rest={n:rig.matrix_world@rig.data.bones[n].matrix_local for n in MAP}
    target_leg=((rest['thigh_l'].translation-rest['foot_l'].translation).length+
                (rest['thigh_r'].translation-rest['foot_r'].translation).length)/2
    ratio=target_leg/source_leg
    phases=[row['time_s']/period for row in raw]
    curves={}
    for name,native in MAP.items():
        logs=[]
        for row in raw:
            delta=row['matrices'][native].to_3x3().normalized()@source_rest[native].to_3x3().normalized().inverted()
            q=(correction@delta@correction.inverted()).to_quaternion()
            if q.w<0:q.negate()
            logs.append(vec(q.axis*q.angle))
        curves[name]=periodic.fit(phases,logs)
    hip_values=[]
    for row in raw:
        t=row['time_s']/duration;position=row['matrices']['Hip'].translation
        # Explicit planar transport split only. Absolute vertical displacement
        # stays relative to neutral, never an action-derived floor offset.
        planar=Vector((raw_origin.x+(raw_end.x-raw_origin.x)*t,
                       raw_origin.y+(raw_end.y-raw_origin.y)*t,source_rest['Hip'].translation.z))
        hip_values.append(vec(correction@(position-planar)*ratio))
    hip_curve=periodic.fit(phases,hip_values)
    rig.data.pose_position='POSE';rig.animation_data_create()
    action=bpy.data.actions.new('Tripo_Run_Periodic_Target_REFERENCE_ONLY');action.use_fake_user=True
    rig.animation_data.action=action
    scene.render.fps=24;scene.render.fps_base=1
    ordered=sorted(MAP,key=lambda n:len(rig.data.bones[n].parent_recursive))
    for i in range(49):
        phase=i/48;frame=phase*period*24;scene.frame_set(int(frame),subframe=frame-int(frame))
        for name in ordered:
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
            log=Vector(periodic.evaluate(curves[name],phase));delta=Quaternion(log.normalized(),log.length).to_matrix() if log.length>1e-9 else Matrix.Identity(3)
            rotation=delta@rest[name].to_3x3().normalized()
            if name=='pelvis':head=rest[name].translation+Vector(periodic.evaluate(hip_curve,phase))
            else:head=rig.matrix_world@((pb.parent.matrix@pb.parent.bone.matrix_local.inverted())@pb.bone.head_local)
            matrix=rotation.to_4x4();matrix.translation=head;pb.matrix=rig.matrix_world.inverted()@matrix
            bpy.context.view_layer.update()
            for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=frame)
    # Linear baked sample interpolation avoids unreviewed Bezier overshoots.
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    scene.frame_start=0;scene.frame_end=round(period*24);scene.frame_set(0)
    cam=scene.camera
    if cam is None:
        cam=bpy.data.objects.new('TripoGuideCamera',bpy.data.cameras.new('TripoGuideCamera'));scene.collection.objects.link(cam);scene.camera=cam
    center=Vector((0,0,.86));cam.location=center+Vector((-4,0,0));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.4
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1920;scene.render.resolution_y=1920;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.filepath=str(out/'FIRST_TARGET_POSE_1920.png');bpy.ops.render.render(write_still=True)
    output=out/'TRIPO_RUN_TARGET_REFERENCE.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output))
    rows=[]
    for i in range(49):
        frame=period*24*i/48;scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        rows.append({'sample':i,'frame':frame,'time_s':period*i/48,'sole_vertices_world_m':sample_vertices(mesh,soles),
            'joints_world_m':{n:vec(rig.matrix_world@rig.pose.bones[n].head) for n in MAP}})
    g.write(out/'retarget_result.json',{'schema':1,'status':'HOLD_TARGET_CONTACT_AND_VISUAL_REVIEW','production_ready':False,
        'visible_art_authority':'none','scope':'TRIPO_PERIODIC_RETARGET_REFERENCE_NOT_SABLE_ART',
        'generator':g.ref(__file__),'fit_implementation':g.ref(ROOT/'tools/character_pipeline/tripo_cycle_fit.py'),
        'source_pack':g.ref(PACK),'source_run_reference':checked['run_reference'],'target_probe':g.ref(TARGET),
        'target_license':target['license'],'target_model':target['source'],'input_blend':target['blend'],
        'output_blend':g.ref(output),'first_native_pose':g.ref(out/'FIRST_TARGET_POSE_1920.png'),
        'mapping':{n:n for n in MAP},'source_to_target_mapping':MAP,'sole_mesh':mesh.name,'sole_vertex_ids':soles,
        'baked_frame_range':[0,period*24],'source_duration_s':duration,'derived_period_s':period,
        'source_period_hypothesis':'two similar observed strides; periodic fitting is an explicit new derived motion',
        'leg_length_scale':ratio,'source_planar_displacement_m':vec(raw_end-raw_origin),
        'nominal_target_distance_per_cycle_m':math.hypot(raw_end.x-raw_origin.x,raw_end.y-raw_origin.y)*ratio/2,
        'planar_trajectory_removed_for_in_place_pose_guide':True,'per_frame_root_ground_correction':False,
        'neutral_rest_sole_vertices_world_m':neutral,'neutral_side_min_z_m':neutral_min,'fixed_floor_z_m':floor,
        'curves':curves,'hip_curve':hip_curve,'samples':rows,
        'limitations':['No transferred Tripo spear arm animation is authority for SABLE firing.','Source geometry and fit are not contact or visual PASS.']})


def main(args):
    out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_OUTPUT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    target=g.read(TARGET)
    g.write(out/'INPUTS.json',{'builder':g.ref(__file__),'periodic_fit':g.ref(ROOT/'tools/character_pipeline/tripo_cycle_fit.py'),
        'source_pack':g.ref(PACK),'target_probe':g.ref(TARGET),'target_blend':target['blend'],'target_model':target['source'],'target_license':target['license']})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1';env['OMP_NUM_THREADS']='2'
    cmd=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--out',str(out),'--inside']
    with (out/'blender.log').open('w',encoding='utf8') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:raise ValueError('RETARGET_CHILD_FAILED:'+str(out/'blender.log'))
    report=g.read(out/'retarget_result.json');g.resolve(report['output_blend'])
    g.write(out/'completion.json',{'result':g.ref(out/'retarget_result.json'),'owned_child_exited':True,'production_ready':False})
    print(str(out/'completion.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--inside',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else main(args)
