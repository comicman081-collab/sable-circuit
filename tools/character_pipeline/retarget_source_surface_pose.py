"""One actual Tripo-derived pose transferred to the new original-art skin.

This is a measured adapter implementation probe, never a motion/HTML approval.
The source image is not reauthored and no guide-model mesh/material is imported.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def child(args):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    out=g.local(args.out);inputs=g.read(out/'INPUTS.json')
    for ref in inputs.values():g.resolve(ref)
    source=g.read(g.resolve(inputs['surface']));pack=g.read(g.resolve(inputs['motion_pack']))
    if source['blend']!=inputs['blend'] or source['builder']!=inputs['surface_builder']:
        raise ValueError('EXACT_SURFACE_BINDING_REQUIRED')
    if source['closed_edge_incidence'] is not True or pack['representation']!='evaluated_skeleton_motion':
        raise ValueError('CLOSED_SOURCE_SURFACE_AND_ACTUAL_BONE_MOTION_REQUIRED')
    if inputs['retargeter']!=g.ref(__file__):raise ValueError('EXACT_RETARGETER_REQUIRED')
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(inputs['blend'])),load_ui=False)
    if args.sample!=23:raise ValueError('THIS_PROBE_IS_EXACT_CONTACT_SAMPLE_23_ONLY')
    scene=bpy.context.scene
    rig=bpy.data.objects[source.get('rig_name','MICA_SourceRig')]
    mesh=bpy.data.objects[source.get('mesh_name','MICA_SourceSurface_S')]
    clip=pack['clips']['run/forward'];frame=clip['frames'][args.sample]
    axes=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
    def unpack(row):
        q=row['q'];matrix=Quaternion((q[3],q[0],q[1],q[2])).to_matrix().to_4x4()
        for i in range(3):
            for j in range(3):matrix[i][j]*=row['s'][j]
        matrix.translation=Vector(row['p']);return matrix
    source_rest=[];source_pose=[]
    for i,bone in enumerate(pack['bone_order']):
        parent=bone['parent'];local_rest=unpack(bone['rest']);local_pose=unpack(frame['poses'][i])
        source_rest.append(source_rest[parent]@local_rest if parent>=0 else local_rest)
        source_pose.append(source_pose[parent]@local_pose if parent>=0 else local_pose)
    rest={row['name']:axes.inverted()@source_rest[i]@axes for i,row in enumerate(pack['bone_order'])}
    pose={row['name']:axes.inverted()@source_pose[i]@axes for i,row in enumerate(pack['bone_order'])}
    target_rest={bone.name:rig.matrix_world@bone.matrix_local for bone in rig.data.bones}
    target_leg=sum((target_rest['thigh_'+s].translation-target_rest['calf_'+s].translation).length+
                   (target_rest['calf_'+s].translation-target_rest['foot_'+s].translation).length for s in ('l','r'))/2
    source_leg=sum((rest['thigh_'+s].translation-rest['calf_'+s].translation).length+
                   (rest['calf_'+s].translation-rest['foot_'+s].translation).length for s in ('l','r'))/2
    scale=target_leg/source_leg
    lower={'pelvis',*[stem+'_'+s for s in ('l','r') for stem in ('thigh','calf','foot','ball')]}
    for bone in sorted(rig.pose.bones,key=lambda b:len(b.bone.parent_recursive)):
        target=target_rest[bone.name]
        if bone.name in lower:
            delta=pose[bone.name].to_quaternion()@rest[bone.name].to_quaternion().inverted()
            rotation=delta@target.to_quaternion()
        else:
            # Neutral arms/head are intentionally retained for this lower-body
            # probe. They are not mislabeled as the rifle aim/fire layer.
            rotation=target.to_quaternion()
        if bone.name=='pelvis':
            head=target.translation+(pose['pelvis'].translation-rest['pelvis'].translation)*scale
        else:
            parent=bone.parent
            head=rig.matrix_world@(parent.matrix@parent.bone.matrix_local.inverted()@bone.bone.head_local)
        matrix=rotation.to_matrix().to_4x4();matrix.translation=head
        bone.matrix=rig.matrix_world.inverted()@matrix
        bpy.context.view_layer.update()
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());actual=evaluated.to_mesh()
    try:vertices=[list(evaluated.matrix_world@vertex.co) for vertex in actual.vertices]
    finally:evaluated.to_mesh_clear()
    scene.render.filepath=str(out/'TRIPO_CONTACT_L_SOURCE_SKIN_1920.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'MICA_TRIPO_SOURCE_SKIN_CONTACT.blend'))
    g.write(out/'RETARGET_PROBE.json',{'scope':'ONE_ACTUAL_TRIPO_DERIVED_CONTACT_POSE_NOT_GAIT_APPROVAL',
        'inputs':g.ref(out/'INPUTS.json'),'sample_index':args.sample,'source_time_s':frame['time_s'],
        'source_cycle_duration_s':clip['duration_s'],'target_source_leg_ratio':scale,
        'per_frame_root_floor_correction':False,'visible_guide_geometry_imported':False,
        'source_pixels_reauthored':False,'firing_implemented':False,'production_ready':False,
        'actual_evaluated_vertices_m':vertices,
        'actual_joints_m':{bone.name:list(rig.matrix_world@bone.head) for bone in rig.pose.bones},
        'render':g.ref(out/'TRIPO_CONTACT_L_SOURCE_SKIN_1920.png'),
        'blend':g.ref(out/'MICA_TRIPO_SOURCE_SKIN_CONTACT.blend')})


def run(args):
    source=g.read(args.surface);out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('IMPLEMENTATION_PROBE_ROOT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    g.write(out/'INPUTS.json',{'retargeter':g.ref(__file__),'surface':g.ref(args.surface),
        'surface_builder':source['builder'],'blend':source['blend'],'motion_pack':g.ref(args.pack),
        'generation_harness':g.ref(ROOT/'tools/character_pipeline/generation_harness.py')})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
        '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out),'--sample',str(args.sample)]
    with (out/'blender.log').open('w',encoding='utf8') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:raise ValueError('SOURCE_SKIN_RETARGET_PROBE_FAILED:'+str(out/'blender.log'))
    print('ACTUAL_TRIPO_CONTACT_TRANSFER_CAPTURED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--surface');parser.add_argument('--pack')
    parser.add_argument('--out',required=True);parser.add_argument('--sample',type=int,default=23)
    parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
