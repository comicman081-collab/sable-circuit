"""Bounded Astra anatomical rig probe on the licensed Blender Studio CC0 base.

This builds real skin on an actual anatomical mesh, not cylinders or cutouts.
It is diagnostic-only: no MICA art/identity, production receipt or promotion.
Original downloaded data and installed tools remain read-only.
"""
import argparse
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

SOURCE=ROOT/'third_party/blender_studio/human_base_meshes_v1_4_1/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
LICENSE=ROOT/'third_party/blender_studio/human_base_meshes_v1_4_1/MODEL_LICENSE.json'
UAL=ROOT/'assets/external/quaternius/ual1/UAL1_Standard.glb'


def build(out):
    import bpy
    from mathutils import Vector, Matrix
    from probe_vrm_ual_retarget import world_rest, body_basis, native_pose
    wanted=['GEO-body_female_realistic','GEO-body_female_realistic.eye.L','GEO-body_female_realistic.eye.R']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(SOURCE),link=False) as (available,selected):
        if any(n not in available.objects for n in wanted): raise ValueError('EXACT_REALISTIC_BODY_AND_TWO_EYES_REQUIRED')
        selected.objects=wanted
    scene=bpy.context.scene
    for ob in selected.objects: scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    body=next(o for o in selected.objects if o.name=='GEO-body_female_realistic')
    # Apply only the imported project-local copies' transforms. Preserve original
    # topology and vertex IDs: multires detail is not silently used as sole IDs.
    for ob in selected.objects:
        for modifier in list(ob.modifiers): ob.modifiers.remove(modifier)
    points=[body.matrix_world@v.co for v in body.data.vertices]
    low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    origin=Vector(((low.x+high.x)/2,0,low.z)); scale=1.72/(high.z-low.z)
    for ob in selected.objects:
        world=ob.matrix_world.copy()
        ob.parent=None
        for v in ob.data.vertices: v.co=(world@v.co-origin)*scale
        ob.matrix_world=Matrix.Identity(4)
        ob.data.materials.clear()
        for polygon in ob.data.polygons: polygon.use_smooth=True
    material=bpy.data.materials.new('NeutralClay_DIAGNOSTIC_NOT_MICA_ART')
    material.diffuse_color=(.24,.3,.35,1)
    for ob in selected.objects: ob.data.materials.append(material)
    # Ground-truth anatomical landmark positions must be reviewed in the saved
    # native pose before production. These are initial rig authoring coordinates,
    # never evidence of actual evaluated skin/contact performance.
    h=1.72
    joints={'pelvis':((0,0,.53),(0,0,.59),None),
        'spine_01':((0,0,.59),(0,0,.65),'pelvis'),
        'spine_02':((0,0,.65),(0,0,.71),'spine_01'),
        'spine_03':((0,0,.71),(0,0,.8),'spine_02'),
        'neck_01':((0,0,.8),(0,0,.87),'spine_03'),
        'Head':((0,0,.87),(0,0,.98),'neck_01')}
    for suffix,sign in (('l',1),('r',-1)):
        joints.update({
            'thigh_'+suffix:((sign*.055,0,.53),(sign*.06,-.012,.285),'pelvis'),
            'calf_'+suffix:((sign*.06,-.012,.285),(sign*.06,.006,.055),'thigh_'+suffix),
            'foot_'+suffix:((sign*.06,.006,.055),(sign*.06,-.08,.025),'calf_'+suffix),
            'ball_'+suffix:((sign*.06,-.08,.025),(sign*.06,-.12,.023),'foot_'+suffix),
            'clavicle_'+suffix:((sign*.025,0,.785),(sign*.105,0,.79),'spine_03'),
            'upperarm_'+suffix:((sign*.105,0,.79),(sign*.19,0,.65),'clavicle_'+suffix),
            'lowerarm_'+suffix:((sign*.19,0,.65),(sign*.24,0,.51),'upperarm_'+suffix),
            'hand_'+suffix:((sign*.24,0,.51),(sign*.258,0,.46),'lowerarm_'+suffix)})
    armature=bpy.data.armatures.new('Realistic_Base_Anatomical_Rig')
    rig=bpy.data.objects.new('Realistic_Base_Anatomical_Rig',armature);scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,(head,tail,parent) in joints.items():
        bone=armature.edit_bones.new(name);bone.head=Vector(head)*h;bone.tail=Vector(tail)*h
        if parent: bone.parent=armature.edit_bones[parent]
        bone.align_roll(Vector((0,-1,0)))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    errors=[]
    for v in body.data.vertices:
        weights=[(w.group,w.weight) for w in v.groups if body.vertex_groups[w.group].name in armature.bones]
        total=sum(w for _,w in weights)
        if total<1e-8: errors.append(v.index);continue
        # Heat weights are proportional influences, not necessarily a unit sum.
        # Normalize the actual generated weights; never invent influences for a
        # vertex for which automatic skinning found no valid deformation bone.
        for group,weight in weights:body.vertex_groups[group].add([v.index],weight/total,'REPLACE')
    if errors: raise ValueError('AUTO_SKIN_UNWEIGHTED_OR_UNNORMALIZED:'+str(len(errors)))
    for ob in selected.objects:
        if ob==body:continue
        group=ob.vertex_groups.new(name='Head');group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
        modifier=ob.modifiers.new('Actual_head_skin','ARMATURE');modifier.object=rig
    soles={}
    for side,sign in (('left',1),('right',-1)):
        candidates=[v for v in body.data.vertices if v.co.x*sign>0 and v.co.z<.1]
        bottom=min(v.co.z for v in candidates)
        soles[side]=[v.index for v in candidates if v.co.z<bottom+.008]
        if len(soles[side])<3:raise ValueError('VISIBLE_ANATOMICAL_SOLES_REQUIRED')
    rest_vertices={side:[list(body.data.vertices[i].co) for i in ids] for side,ids in soles.items()}
    # UAL source is imported read-only. Bake world/rest-space rotations to this
    # rig, with original source timing; lower-body skin remains the real mesh.
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(UAL))
    source=next(o for o in scene.objects if o not in before and o.type=='ARMATURE')
    for ob in scene.objects:
        if ob not in before: ob.hide_render=True
    source.animation_data_create()
    for track in list(source.animation_data.nla_tracks): source.animation_data.nla_tracks.remove(track)
    action=bpy.data.actions['Walk_Loop'];source.animation_data.action=action
    if action.slots:source.animation_data.action_slot=action.slots[0]
    rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new('UAL_Walk_Realistic_Probe')
    names=sorted(joints,key=lambda n:len(armature.bones[n].parent_recursive))
    correction=body_basis(rig,'pelvis','thigh_l','thigh_r','Head')@body_basis(source,'pelvis','thigh_l','thigh_r','Head').inverted()
    src={n:world_rest(source,n) for n in names};dst={n:world_rest(rig,n) for n in names}
    ratio=(dst['Head'].translation-dst['pelvis'].translation).length/(src['Head'].translation-src['pelvis'].translation).length
    start,end=map(float,action.frame_range);scene.render.fps=24
    for i in range(25):
        frame=start+(end-start)*i/24;scene.frame_set(int(frame),subframe=frame-int(frame))
        for name in names:
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
            sw=source.matrix_world@source.pose.bones[name].matrix
            delta=sw.to_3x3().normalized()@src[name].to_3x3().normalized().inverted()
            rotation=correction@delta@correction.inverted()@dst[name].to_3x3().normalized()
            if name=='pelvis': head=dst[name].translation+correction@(sw.translation-src[name].translation)*ratio
            else:
                parent=pb.parent
                head=(parent.matrix@parent.bone.matrix_local.inverted())@pb.bone.head_local if parent else pb.bone.head_local
            matrix=rotation.to_4x4();matrix.translation=head;pb.matrix=matrix
            bpy.context.view_layer.update()
            for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=frame)
    playback=[]
    for i in range(25):
        frame=start+(end-start)*i/24;scene.frame_set(int(frame),subframe=frame-int(frame))
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        try:
            playback.append({'frame':frame,'time_s':(frame-start)/24,'sole_vertices_world_m':{
                side:[list(evaluated.matrix_world@mesh.vertices[j].co) for j in ids] for side,ids in soles.items()}})
        finally:evaluated.to_mesh_clear()
    scene.frame_start=int(start);scene.frame_end=math.ceil(end);scene.frame_set(int(start))
    image=native_pose(scene,selected.objects,out)
    output=out/'Realistic_Anatomical_Base_UAL_Walk_DIAGNOSTIC.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    g.write(out/'rig_probe.json',{'status':'HOLD_ANATOMY_RIG_REVIEW_NOT_MICA','production_ready':False,
        'source':g.ref(SOURCE),'license':g.ref(LICENSE),'builder':g.ref(__file__),'ual':g.ref(UAL),
        'blend':g.ref(output),'native_pose':image,'rig':rig.name,'mesh':body.name,
        'body_height_m':h,'mapping':{n:n for n in names},'source_fps':24,'source_frame_range':[start,end],
        'sole_vertex_ids':soles,'rest_sole_vertices_m':rest_vertices,'evaluated_playback':playback,
        'authoring_landmarks_normalized':joints,'unweighted_vertices':errors,
        'limitations':['Initial auto weights/joint positions need native visual review',
            'One in-place walk probe; no calibrated world contact or MICA costume',
            'No source/pose/motion receipt; cannot package or promote']})


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True)
    p.add_argument('--inside-blender',action='store_true');a=p.parse_args(args)
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_OUTPUT_REQUIRED')
    if a.inside_blender:build(out);return
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    env=os.environ.copy()
    for k in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
              'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[k]=str(cache)
    env['OMP_NUM_THREADS']='2';env['PYTHONDONTWRITEBYTECODE']='1'
    before=g.ref(SOURCE)
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
        '--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--inside-blender','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode or before!=g.ref(SOURCE):raise ValueError('RIG_PROBE_FAILED_OR_SOURCE_CHANGED')
    result=g.read(out/'rig_probe.json');g.resolve(result['blend']);g.resolve(result['native_pose'])
    g.write(out/'completion.json',{'owned_child_exited':True,'source_unchanged':True,'result':g.ref(out/'rig_probe.json'),'production_ready':False})
    print(str(out/'rig_probe.json'))


if __name__=='__main__':main()
