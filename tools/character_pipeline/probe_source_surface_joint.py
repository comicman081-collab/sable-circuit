"""One small knee deformation of the exact new source-surface adapter.

Implementation evidence only: no new direction, gait batch or runtime promotion.
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


def child(args):
    import bpy
    from mathutils import Quaternion
    out=g.local(args.out); inputs=g.read(out/'INPUTS.json')
    for reference in inputs.values():g.resolve(reference)
    if inputs['probe']!=g.ref(__file__):raise ValueError('EXACT_PROBE_REQUIRED')
    report=g.read(g.resolve(inputs['surface']))
    if report['blend']!=inputs['blend'] or report['builder']!=inputs['builder'] or report['closed_edge_incidence'] is not True:
        raise ValueError('EXACT_CLOSED_SOURCE_SURFACE_REQUIRED')
    g.write(out/'CHILD_CLAIM.json',{'inputs':g.ref(out/'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(inputs['blend'])),load_ui=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MICA_SourceRig'];mesh=bpy.data.objects['MICA_SourceSurface_S']
    def vertices():
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()); actual=evaluated.to_mesh()
        try:return [list(evaluated.matrix_world@vertex.co) for vertex in actual.vertices]
        finally:evaluated.to_mesh_clear()
    neutral=vertices()
    bone=rig.pose.bones['calf_l'];bone.rotation_mode='QUATERNION'
    bone.rotation_quaternion=Quaternion((1,0,0),math.radians(10))
    bpy.context.view_layer.update();posed=vertices()
    scene.render.filepath=str(out/'LEFT_KNEE_10_DEGREES_1920.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'SOURCE_SURFACE_KNEE_PROBE.blend'))
    deltas=[math.dist(a,b) for a,b in zip(neutral,posed)]
    g.write(out/'JOINT_PROBE.json',{'scope':'ONE_LEFT_KNEE_10_DEGREE_DEFORMATION_NOT_GAIT_APPROVAL',
        'inputs':g.ref(out/'INPUTS.json'),'source_surface':inputs['surface'],
        'bone':'calf_l','angle_degrees':10,'visible_frame_count':1,
        'actual_evaluated_vertex_count':len(posed),'maximum_vertex_displacement_m':max(deltas),
        'vertices_moved_over_1mm':sum(value>.001 for value in deltas),
        'native_resolution':[1920,1920],'render':g.ref(out/'LEFT_KNEE_10_DEGREES_1920.png'),
        'blend':g.ref(out/'SOURCE_SURFACE_KNEE_PROBE.blend'),'production_ready':False,
        'neutral_vertices_m':neutral,'posed_vertices_m':posed})


def run(args):
    source=g.read(args.surface);out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('IMPLEMENTATION_PROBE_OUTPUT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    g.write(out/'INPUTS.json',{'probe':g.ref(__file__),'surface':g.ref(args.surface),
        'blend':source['blend'],'builder':source['builder'],
        'generation_harness':g.ref(ROOT/'tools/character_pipeline/generation_harness.py')})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(out/'cache')
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='2')
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
        '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf8') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:raise ValueError('JOINT_PROBE_FAILED:'+str(out/'blender.log'))
    print('SINGLE_KNEE_DEFORMATION_CAPTURED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--surface')
    parser.add_argument('--out',required=True);parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
