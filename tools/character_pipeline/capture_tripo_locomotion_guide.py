"""Capture the entire saved Tripo contact guide at native 1920x1080."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def child(a):
    import bpy
    from mathutils import Vector
    from build_tripo_locomotion_guide import sample_vertices
    out=g.local(a.out); result=g.read(a.result); report=g.read(a.calibration)
    for ref in g.read(out/'INPUTS.json').values():g.resolve(ref)
    with (out/'CHILD_CLAIM.json').open('x',encoding='utf8') as f:f.write(g.canonical(g.read(out/'INPUTS.json')))
    if report['input_result']!=g.ref(a.result) or report['input_blend']!=result['output_blend']:raise ValueError('EXACT_CALIBRATION_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(result['output_blend'])),load_ui=False)
    scene=bpy.context.scene; mesh=bpy.data.objects[result['sole_mesh']]
    floor=report['fixed_floor']['world_z_m']
    bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,floor)); plane=bpy.context.object;plane.name='Reference_fixed_REST_floor';plane.color=(.38,.4,.44,1)
    # Fit actual evaluated full-body bounds over the entire saved cycle.
    # Pose displacement can move the head well above its neutral height.
    bounds=[]
    for row in report['samples']:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
        try:bounds.extend(ev.matrix_world@v.co for v in data.vertices)
        finally:ev.to_mesh_clear()
    ymin=min(v.y for v in bounds);ymax=max(v.y for v in bounds)
    zmin=min(floor,min(v.z for v in bounds));zmax=max(v.z for v in bounds)
    center=Vector((0,(ymin+ymax)/2,(zmin+zmax)/2));scene.camera.location=center+Vector((-4,0,0))
    scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=max((zmax-zmin)*1920/1080,ymax-ymin)*1.15
    # A camera-facing reference line marks the fixed floor in an exact side
    # view, where a horizontal floor plane otherwise becomes edge-on.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.55,center.y,floor))
    line=bpy.context.object;line.name='Fixed_REST_floor_reference_line';line.dimensions=(.002,6,.003);line.color=(.8,.8,.8,1)
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='OBJECT';mesh.color=(.65,.72,.8,1)
    scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
    scene.render.film_transparent=False
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.threads_mode='FIXED';scene.render.threads=2
    frames=[]
    for row in report['samples']:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        vertices=sample_vertices(mesh,result['sole_vertex_ids'])
        if vertices!=row['sole_vertices_world_m']:raise ValueError('CAPTURE_SOLES_DIFFER_FROM_CALIBRATION')
        path=out/('frame_%03d.png'%row['sample']);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        phases=[phase for phase,index in report['phase_candidates'].items() if index==row['sample']]
        frames.append({'sample':row['sample'],'frame':frame,'time_s':row['time_s'],'phase':phases[0] if phases else None,
            'image':g.ref(path),'actual_sole_vertices_world_m':vertices})
    g.write(out/'CAPTURE.json',{'schema':1,'scope':'TRIPO_CC0_GEOMETRY_GUIDE_ONLY_NOT_SABLE_PIXELS',
        'generator':g.ref(__file__),'retarget_result':g.ref(a.result),'calibration':g.ref(a.calibration),
        'blend':result['output_blend'],'native_resolution':[1920,1080],
        'camera_fit':'actual_evaluated_entire_cycle_with_15_percent_margin',
        'fixed_floor_world_z_m':floor,'frames':frames,'production_ready':False})


def main(a):
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_ONLY')
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir()
    g.write(out/'INPUTS.json',{'builder':g.ref(__file__),'sample_helper':g.ref(ROOT/'tools/character_pipeline/build_tripo_locomotion_guide.py'),
        'result':g.ref(a.result),'calibration':g.ref(a.calibration),'blend':g.read(a.result)['output_blend']})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME','BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1';env['OMP_NUM_THREADS']='2'
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--result',str(g.local(a.result)),'--calibration',str(g.local(a.calibration)),'--out',str(out),'--inside']
    with (out/'blender.log').open('w',encoding='utf8') as log:
        p=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if p.returncode:raise ValueError('CAPTURE_FAILED:'+str(out/'blender.log'))
    for ref in g.read(out/'INPUTS.json').values():g.resolve(ref)
    g.write(out/'completion.json',{'capture':g.ref(out/'CAPTURE.json'),'owned_child_exited':True,'production_ready':False})
    print(out/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',required=True);p.add_argument('--calibration',required=True);p.add_argument('--out',required=True);p.add_argument('--inside',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(a) if a.inside else main(a)
