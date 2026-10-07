"""Bounded 49-sample native reference video; no character/runtime export."""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inspection",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    report=g.read(a.inspection)
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'art_src/motion_reference'):
        raise ValueError('REFERENCE_REVIEW_OUTPUT_REQUIRED')
    if list(out.glob('*.png')) or (out/'CAPTURE.json').exists():
        raise ValueError('FRESH_CAPTURE_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(report['pack']['run_reference'])),load_ui=False)
    geometry=g.read(g.resolve(report['pack']['run_geometry']))
    scene=bpy.context.scene; cam=scene.camera
    scene.render.resolution_x=1920; scene.render.resolution_y=1080
    scene.render.resolution_percentage=100; cam.data.ortho_scale=3.8
    scene.render.engine='BLENDER_WORKBENCH'
    first=geometry['samples'][0]['joints_world_m']['hips']
    last=geometry['samples'][-1]['joints_world_m']['hips']
    # Fit the entire supplied mesh (including spear) over the whole action in
    # camera space before locking scale/height. No pose is cropped to hide data.
    mesh=bpy.data.objects[report['mesh']]
    ys=[];zs=[]
    for row in geometry['samples']:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame))
        bpy.context.view_layer.update()
        t=row['time_s']/geometry['duration_s']
        origin_y=first[1]+(last[1]-first[1])*t
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());actual=evaluated.to_mesh()
        try:
            for v in actual.vertices:
                point=evaluated.matrix_world@v.co
                ys.append(float(point.y-origin_y));zs.append(float(point.z))
        finally:evaluated.to_mesh_clear()
    center_y=(min(ys)+max(ys))/2;center_z=(min(zs)+max(zs))/2
    cam.data.ortho_scale=max(max(ys)-min(ys),(max(zs)-min(zs))*1920/1080)*1.12
    samples=[]
    for index,row in enumerate(geometry['samples']):
        frame=row['frame']; scene.frame_set(int(frame),subframe=frame-int(frame))
        # Deliberately documented diagnostic camera translation only. It follows
        # linear net planar travel, never animated height, yaw, sway, or zoom.
        t=row['time_s']/geometry['duration_s']
        center=Vector((first[0]+(last[0]-first[0])*t,first[1]+(last[1]-first[1])*t+center_y,center_z))
        cam.location=center+Vector((-4,0,0))
        cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/f'RUN_{index:03}.png')
        bpy.ops.render.render(write_still=True)
        samples.append({'sample':index,'time_s':row['time_s'],'source_frame':frame,
            'image':g.ref(scene.render.filepath),'camera_world_matrix':[list(v) for v in cam.matrix_world]})
    g.write(out/'CAPTURE.json',{'schema':1,'stage':'tripo_reference_review_capture',
        'production_ready':False,'visible_art_authority':'none','inspection':g.ref(a.inspection),
        'run_reference':report['pack']['run_reference'],'geometry':report['pack']['run_geometry'],
        'generator':g.ref(__file__),'native_resolution':[1920,1080],
        'camera_follow':'linear_net_pelvis_XY_only_for_diagnostic_framing_not_contact_evidence',
        'whole_action_mesh_bounds_in_camera_plane':{'horizontal':[min(ys),max(ys)],'vertical':[min(zs),max(zs)]},
        'locked_ortho_scale':cam.data.ortho_scale,'fit_margin':1.12,
        'samples':samples,'action_duration_s':geometry['duration_s'],
        'note':'Unmodified supplied forward Run, full action; cycle count/contact/loop remain unapproved.'})


if __name__=='__main__': main()
