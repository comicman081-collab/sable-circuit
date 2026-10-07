"""Add fixed world support anchors to an existing Tripo contact guide.

Reference geometry only. The independent planar transport comes from the raw
Tripo Hip trajectory and limb scale, never from sliding foot measurements.
"""
import argparse
import math
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def child(a):
    import bpy
    from mathutils import Vector,Matrix
    from build_tripo_locomotion_guide import sample_vertices
    out=g.local(a.out); source=g.read(a.result); calibration=g.read(a.calibration)
    for ref in g.read(out/'INPUTS.json').values():g.resolve(ref)
    with (out/'CHILD_CLAIM.json').open('x',encoding='utf8') as f:f.write(g.canonical(g.read(out/'INPUTS.json')))
    if calibration['input_result']!=g.ref(a.result):raise ValueError('CALIBRATION_MISMATCH')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(source['output_blend'])),load_ui=False)
    scene=bpy.context.scene;mesh=bpy.data.objects[source['sole_mesh']]
    rig=next(m.object for m in mesh.modifiers if m.type=='ARMATURE')
    ids=source['sole_vertex_ids'];floor=calibration['fixed_floor']['world_z_m']
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    rest_vertices=sample_vertices(mesh,ids)
    if abs(min(v[2] for values in rest_vertices.values() for v in values)-floor)>1e-7:raise ValueError('FIXED_REST_FLOOR_CHANGED')
    rest={b.name:rig.matrix_world@b.matrix_local for b in rig.data.bones}
    rig.data.pose_position='POSE';rows=calibration['samples'][:-1];n=len(rows)
    period=source['derived_period_s'];speed=source['nominal_target_distance_per_cycle_m']/period
    travel=Vector(calibration['travel_axis_world']);travel.normalize()
    original=[]
    for row in rows:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        original.append({b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones})
    windows={side:dict(window) for side,window in source['contact_ik']['windows'].items()}
    ordered=sorted(rig.pose.bones,key=lambda b:len(b.bone.parent_recursive))
    def set_world(name,matrix):
        rig.pose.bones[name].matrix=rig.matrix_world.inverted()@matrix;bpy.context.view_layer.update()
    def support_weight(side,i):
        start=windows[side]['contact'];end=windows[side]['toeoff'];length=(end-start)%n;t=(i-start)%n
        if t<=length:return 1.
        return max(0.,1-min(t-length,n-t)/4)
    def adjusted_base(i):
        base={name:m.copy() for name,m in original[i].items()}
        for side in ('left','right'):
            foot='foot_'+side[0];toe='ball_'+side[0];weight=support_weight(side,i)
            neutral=rest[foot].copy();axis=rest[toe].translation-rest[foot].translation
            yaw=math.atan2(axis.x,-axis.y)
            neutral_rotation=Matrix.Rotation(-yaw,3,'Z')@neutral.to_3x3().normalized()
            q=base[foot].to_quaternion().slerp(neutral_rotation.to_quaternion(),weight)
            m=q.to_matrix().to_4x4();m.translation=base[foot].translation;base[foot]=m
            local_toe=rest[foot].inverted()@rest[toe]
            base[toe]=m@local_toe
        return base
    # Anchor vertices are chosen from the actual evaluated contact-pose sole,
    # then remain the same vertex IDs for the entire support interval.
    anchors={};anchor_ids={}
    for side in ('left','right'):
        i=windows[side]['contact'];base=adjusted_base(i)
        for pb in ordered:set_world(pb.name,base[pb.name])
        actual=sample_vertices(mesh,ids)[side]
        index=min(range(len(actual)),key=lambda j:actual[j][2])
        anchor=Vector(actual[index]);anchor.z=floor+.002
        anchors[side]=anchor;anchor_ids[side]=index
    # End support before the actual target leg reaches full extension. This
    # changes toe-off timing explicitly; it neither lengthens bones nor shifts
    # the root/floor to make an unreachable planted ankle appear valid.
    reach_adjustments=[]
    for side in ('left','right'):
        while True:
            index=windows[side]['toeoff'];base=adjusted_base(index)
            for pb in ordered:set_world(pb.name,base[pb.name])
            actual=sample_vertices(mesh,ids)[side]
            elapsed=(index-windows[side]['contact'])%n
            wanted=anchors[side]-travel*speed*period*elapsed/n
            foot='foot_'+side[0];calf='calf_'+side[0];thigh='thigh_'+side[0]
            ankle=base[foot].translation+(wanted-Vector(actual[anchor_ids[side]]))
            length=(base[calf].translation-base[thigh].translation).length+(base[foot].translation-base[calf].translation).length
            if (ankle-base[thigh].translation).length<=length*.995:break
            if index==windows[side]['passing']:raise ValueError('CONTACT_PATH_UNREACHABLE_BEFORE_PASSING')
            reach_adjustments.append({'side':side,'previous_toeoff':index,'required_leg_distance_m':(ankle-base[thigh].translation).length,'actual_leg_length_m':length})
            windows[side]['toeoff']=(index-1)%n
    def solve(base,side,ankle):
        thigh='thigh_'+side[0];calf='calf_'+side[0];foot='foot_'+side[0];toe='ball_'+side[0]
        hip=base[thigh].translation;knee=base[calf].translation;end=base[foot].translation
        upper=(knee-hip).length;lower=(end-knee).length
        axis=ankle-hip;requested=axis.length;distance=min(upper+lower-1e-6,max(abs(upper-lower)+1e-6,requested));axis.normalize()
        along=(upper*upper-lower*lower+distance*distance)/(2*distance)
        pole=knee-hip-axis*(knee-hip).dot(axis)
        if pole.length<1e-6:pole=Vector((0,-1,0))-axis*axis.dot(Vector((0,-1,0)))
        pole.normalize();new_knee=hip+axis*along+pole*math.sqrt(max(0,upper*upper-along*along));new_end=hip+axis*distance
        for name,old_vec,new_vec,head in ((thigh,knee-hip,new_knee-hip,hip),(calf,end-knee,new_end-new_knee,new_knee)):
            m=(old_vec.rotation_difference(new_vec).to_matrix()@base[name].to_3x3()).to_4x4();m.translation=head;set_world(name,m)
        m=base[foot].copy();m.translation=new_end;set_world(foot,m);set_world(toe,m@base[foot].inverted()@base[toe])
        return max(0,requested-distance)
    rig.animation_data_clear();rig.animation_data_create()
    action=bpy.data.actions.new('Tripo_Run_World_Anchored_REFERENCE_ONLY');action.use_fake_user=True;rig.animation_data.action=action
    measurements=[];max_reach=0.
    for i in range(n+1):
        index=i%n;frame=source['baked_frame_range'][1]*i/n
        scene.frame_set(int(frame),subframe=frame-int(frame));base=adjusted_base(index)
        for pb in ordered:set_world(pb.name,base[pb.name])
        desired={};targets={s:base['foot_'+s[0]].translation.copy() for s in ('left','right')}
        actual=sample_vertices(mesh,ids)
        for side in targets:
            weight=support_weight(side,index)
            elapsed=(index-windows[side]['contact'])%n
            # Pre-contact blending approaches the next anchor, rather than
            # the same foot's anchor from almost a complete cycle earlier.
            if elapsed>n-4:elapsed-=n
            wanted=anchors[side]-travel*speed*period*elapsed/n
            original_point=Vector(actual[side][anchor_ids[side]])
            desired[side]=original_point.lerp(wanted,weight)
        for iteration in range(24):
            actual=sample_vertices(mesh,ids);max_error=0.
            for side in targets:
                weight=support_weight(side,index)
                point=Vector(actual[side][anchor_ids[side]])
                error=desired[side]-point
                # Keep all actual sole vertices above the independently fixed
                # floor, including geometry influenced by the shin weights.
                clearance=min(v[2] for v in actual[side])-floor
                wanted_z=.002 if weight==1 else max(.002,rows[index]['sole_clearance_m'][side])
                error.z=wanted_z-clearance
                targets[side]+=error;max_error=max(max_error,error.length)
                max_reach=max(max_reach,solve(base,side,targets[side]))
            if max_error<.0002:break
        actual=sample_vertices(mesh,ids)
        measurements.append({'sample':i,'frame':frame,'iterations':iteration+1,
            'support_weight':{s:support_weight(s,index) for s in targets},
            'actual_clearance_m':{s:min(v[2] for v in actual[s])-floor for s in targets},
            'horizontal_anchor_error_m':{s:math.hypot(actual[s][anchor_ids[s]][0]-desired[s].x,actual[s][anchor_ids[s]][1]-desired[s].y) for s in targets}})
        for pb in ordered:
            pb.rotation_mode='QUATERNION'
            for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=frame)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(0);blend=out/'TRIPO_SUPPORT_ANCHORED_REFERENCE.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    result=dict(source);result.update({'status':'HOLD_SUPPORT_ANCHORS_REQUIRE_INDEPENDENT_NO_SLIP_AND_VISUAL_REVIEW',
        'generator':g.ref(__file__),'previous_retarget':g.ref(a.result),'input_calibration':g.ref(a.calibration),
        'output_blend':g.ref(blend),'support_anchor':{'fixed_floor_z_m':floor,'per_frame_root_translation':False,
            'transport_speed_m_s':speed,'transport_authority':'raw_Tripo_Hip_planar_distance_times_target_limb_scale_over_source_duration',
            'runtime_game_scale_calibration':'PENDING_APPROVED_VISIBLE_ART',
            'anchor_vertex_ids':{s:ids[s][anchor_ids[s]] for s in anchors},'anchors_world_m':{s:list(v) for s,v in anchors.items()},
            'windows':windows,'toeoff_reach_adjustments':reach_adjustments,
            'measurements':measurements,'max_unreachable_distance_m':max_reach}})
    g.write(out/'retarget_result.json',result)


def main(a):
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_ONLY')
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    g.write(out/'INPUTS.json',{'builder':g.ref(__file__),'helper':g.ref(ROOT/'tools/character_pipeline/build_tripo_locomotion_guide.py'),
        'result':g.ref(a.result),'calibration':g.ref(a.calibration),'blend':g.read(a.result)['output_blend']})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1';env['OMP_NUM_THREADS']='2'
    cmd=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--result',str(g.local(a.result)),'--calibration',str(g.local(a.calibration)),'--out',str(out),'--inside']
    with (out/'blender.log').open('w',encoding='utf8') as log:
        process=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if process.returncode:raise ValueError('SUPPORT_ANCHOR_CHILD_FAILED:'+str(out/'blender.log'))
    for ref in g.read(out/'INPUTS.json').values():g.resolve(ref)
    g.resolve(g.read(out/'retarget_result.json')['output_blend'])
    g.write(out/'completion.json',{'result':g.ref(out/'retarget_result.json'),'owned_child_exited':True,'production_ready':False});print(out/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',required=True);p.add_argument('--calibration',required=True);p.add_argument('--out',required=True);p.add_argument('--inside',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(a) if a.inside else main(a)
