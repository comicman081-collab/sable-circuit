"""Solve Tripo-derived reference legs against the target's immutable REST floor.

Creates new diagnostic motion only; no SABLE pixels or runtime approval.
"""
import argparse
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def child(a):
    import bpy
    from mathutils import Vector, Matrix
    from build_tripo_locomotion_guide import sample_vertices
    out = g.local(a.out)
    inputs = g.read(out / 'INPUTS.json')
    for ref in inputs.values(): g.resolve(ref)
    if inputs['builder'] != g.ref(__file__): raise ValueError('BUILDER_CHANGED')
    claim = out / 'CHILD_CLAIM.json'
    with claim.open('x', encoding='utf8') as f:
        import json
        json.dump({'inputs': g.ref(out / 'INPUTS.json')}, f)
    source = g.read(a.result); calibration = g.read(a.calibration)
    if calibration['input_result'] != g.ref(a.result): raise ValueError('CALIBRATION_MISMATCH')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(source['output_blend'])), load_ui=False)
    scene = bpy.context.scene; mesh = bpy.data.objects[source['sole_mesh']]
    rig = next(m.object for m in mesh.modifiers if m.type == 'ARMATURE')
    ids = source['sole_vertex_ids']; floor = calibration['fixed_floor']['world_z_m']
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    rest = sample_vertices(mesh, ids)
    if abs(min(v[2] for rows in rest.values() for v in rows)-floor) > 1e-7:
        raise ValueError('FIXED_REST_FLOOR_CHANGED')
    rig.data.pose_position = 'POSE'
    rows = calibration['samples'][:-1]; n = len(rows)
    original = []
    for row in rows:
        frame = row['frame']; scene.frame_set(int(frame), subframe=frame-int(frame))
        bpy.context.view_layer.update()
        original.append({b.name: (rig.matrix_world @ b.matrix).copy() for b in rig.pose.bones})
    # Contact starts before the observed down point, at >=22mm pelvis loading.
    # Toe-off follows passing; shorten the airborne transition only through
    # explicit leg IK. Nothing relabels the measured source phases as approved.
    windows = {}
    for side in ('left', 'right'):
        suffix = side[0]; down = calibration['phase_candidates']['down_'+suffix]
        contact = down
        for back in range(1, n//4):
            index = (down-back) % n
            contact = index
            if rows[index]['pelvis_world_m'][2]-rows[down]['pelvis_world_m'][2] >= .022:
                break
        passing = calibration['phase_candidates']['passing_'+suffix]
        toeoff = (passing+6) % n
        windows[side] = {'contact': contact, 'down': down, 'passing': passing, 'toeoff': toeoff}
    def cyclic_distance(start, index): return (index-start) % n
    def desired_clearance(side, index):
        window = windows[side]; t = cyclic_distance(window['contact'], index)
        length = cyclic_distance(window['contact'], window['toeoff'])
        if t <= length: return .002
        # A continuous periodic swing envelope, with real sole measurements
        # providing extra clearance if the source already lifts higher.
        swing = (t-length)/(n-length)
        envelope = .002 + .105*math.sin(math.pi*swing)**.7
        return max(envelope, rows[index]['sole_clearance_m'][side])
    def set_world(name, matrix):
        rig.pose.bones[name].matrix = rig.matrix_world.inverted() @ matrix
        bpy.context.view_layer.update()
    def solve_leg(base, side, ankle):
        suffix = side[0]; thigh = 'thigh_'+suffix; calf = 'calf_'+suffix; foot = 'foot_'+suffix
        h = base[thigh].translation; k = base[calf].translation; end = base[foot].translation
        upper = (k-h).length; lower = (end-k).length
        axis = ankle-h; requested = axis.length
        distance = min(upper+lower-1e-6, max(abs(upper-lower)+1e-6, requested))
        axis.normalize(); along = (upper*upper-lower*lower+distance*distance)/(2*distance)
        pole = k-h-axis*(k-h).dot(axis)
        if pole.length < 1e-6: pole = Vector((0,-1,0))-axis*axis.dot(Vector((0,-1,0)))
        pole.normalize(); knee = h+axis*along+pole*math.sqrt(max(0,upper*upper-along*along))
        endpoint = h+axis*distance
        for name, old_dir, new_dir, head in ((thigh,k-h,knee-h,h),(calf,end-k,endpoint-knee,knee)):
            rotation = old_dir.rotation_difference(new_dir).to_matrix() @ base[name].to_3x3()
            mat = rotation.to_4x4(); mat.translation = head; set_world(name,mat)
        mat = base[foot].copy(); mat.translation = endpoint; set_world(foot,mat)
        # Preserve toe local rest relation under the corrected ankle heading.
        toe = 'ball_'+suffix
        mat = mat @ base[foot].inverted() @ base[toe]; set_world(toe, mat)
        return max(0, requested-distance)
    rig.animation_data_clear(); rig.animation_data_create()
    action = bpy.data.actions.new('Tripo_Run_Contact_IK_REFERENCE_ONLY'); action.use_fake_user = True
    rig.animation_data.action = action
    ordered = sorted(rig.pose.bones, key=lambda b: len(b.bone.parent_recursive))
    measured=[]; max_reach=0
    for i in range(n+1):
        index=i % n; frame=source['baked_frame_range'][1]*i/n
        scene.frame_set(int(frame),subframe=frame-int(frame))
        base={name:mat.copy() for name,mat in original[index].items()}
        # World-up yaw straightening keeps the source ankle pitch and toe curl.
        for side in ('left','right'):
            suffix=side[0]; name='foot_'+suffix; toe='ball_'+suffix
            vector=base[toe].translation-base[name].translation
            yaw=math.atan2(vector.x,-vector.y)
            pivot=base[name].translation
            correction=Matrix.Translation(pivot) @ Matrix.Rotation(-yaw,4,'Z') @ Matrix.Translation(-pivot)
            base[name]=correction @ base[name]; base[toe]=correction @ base[toe]
        for pb in ordered: set_world(pb.name,base[pb.name])
        targets={s:base['foot_'+s[0]].translation.copy() for s in ('left','right')}
        for iteration in range(18):
            vertices=sample_vertices(mesh,ids); error_max=0
            for side in ('left','right'):
                actual=min(v[2] for v in vertices[side])-floor
                error=desired_clearance(side,index)-actual; error_max=max(error_max,abs(error))
                targets[side].z+=error
                max_reach=max(max_reach,solve_leg(base,side,targets[side]))
            if error_max < .00025: break
        actual=sample_vertices(mesh,ids)
        measured.append({'sample':i,'frame':frame,'iterations':iteration+1,
            'desired_clearance_m':{s:desired_clearance(s,index) for s in targets},
            'actual_clearance_m':{s:min(v[2] for v in actual[s])-floor for s in targets}})
        for pb in ordered:
            pb.rotation_mode='QUATERNION'
            for prop in ('location','rotation_quaternion','scale'): pb.keyframe_insert(prop,frame=frame)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points: key.interpolation='LINEAR'
    scene.frame_set(0)
    blend=out/'TRIPO_CONTACT_REFERENCE.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    result=dict(source)
    result.update({'status':'HOLD_NEW_CONTACT_IK_REQUIRES_CALIBRATION_AND_REVIEW',
        'generator':g.ref(__file__),'output_blend':g.ref(blend),
        'previous_retarget':g.ref(a.result),'input_calibration':g.ref(a.calibration),
        'contact_ik':{'fixed_floor_z_m':floor,'per_frame_root_translation':False,
            'method':'analytic_two_bone_with_observed_knee_plane_and_evaluated_full_sole_feedback',
            'windows':windows,'measurements':measured,'max_unreachable_distance_m':max_reach}})
    # Source samples describe the preceding stage only; downstream must sample
    # this saved Blender file afresh instead of treating those rows as current.
    result.pop('samples',None); result.pop('first_native_pose',None)
    g.write(out/'retarget_result.json',result)


def main(a):
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'): raise ValueError('DIAGNOSTIC_ONLY')
    out.mkdir(parents=True,exist_ok=False); cache=out/'cache'; cache.mkdir()
    source=g.read(a.result)
    g.write(out/'INPUTS.json',{'builder':g.ref(__file__),'sample_helper':g.ref(ROOT/'tools/character_pipeline/build_tripo_locomotion_guide.py'),
        'result':g.ref(a.result),'calibration':g.ref(a.calibration),'blend':source['output_blend']})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'): env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1'; env['OMP_NUM_THREADS']='2'
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--result',str(g.local(a.result)),'--calibration',str(g.local(a.calibration)),'--out',str(out),'--inside']
    with (out/'blender.log').open('w',encoding='utf8') as log:
        p=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if p.returncode: raise ValueError('CONTACT_CHILD_FAILED:'+str(out/'blender.log'))
    for reference in g.read(out/'INPUTS.json').values(): g.resolve(reference)
    g.resolve(g.read(out/'retarget_result.json')['output_blend'])
    g.write(out/'completion.json',{'result':g.ref(out/'retarget_result.json'),'owned_child_exited':True,'production_ready':False})
    print(out/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--result',required=True); p.add_argument('--calibration',required=True); p.add_argument('--out',required=True); p.add_argument('--inside',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(a) if a.inside else main(a)
