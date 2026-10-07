"""Capture one real, time-preserved diagnostic cycle; not a runtime/visual PASS."""
import argparse
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g


def capture(args):
    import bpy
    result=g.read(args.result); blend=g.resolve(result['output_blend']); out=g.local(args.out)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene=bpy.context.scene; ob=bpy.data.objects[result['sole_mesh']]
    if scene.render.resolution_x!=1920 or scene.render.resolution_y!=1920:
        raise ValueError('EXACT_NATIVE_1920_CAMERA_REQUIRED')
    start,end=result['baked_frame_range']; frame_ids=list(range(int(start),int(end)+1))
    if len(frame_ids)>49 or start!=int(start) or end!=int(end):
        raise ValueError('ONE_INTEGER_FRAME_DIAGNOSTIC_CYCLE_REQUIRED')
    camera=[list(r) for r in scene.camera.matrix_world]; rows=[]
    for i,frame in enumerate(frame_ids):
        scene.frame_set(frame)
        if [list(r) for r in scene.camera.matrix_world]!=camera: raise ValueError('CAMERA_DRIFT')
        image=out/'frames'/f'{i:03}.png'; image.parent.mkdir(parents=True,exist_ok=True)
        if image.exists(): raise ValueError('NO_CAPTURE_OVERWRITE')
        scene.render.filepath=str(image); bpy.ops.render.render(write_still=True)
        deps=bpy.context.evaluated_depsgraph_get(); evaluated=ob.evaluated_get(deps); mesh=evaluated.to_mesh()
        try:
            soles={side:[list(evaluated.matrix_world@mesh.vertices[index].co) for index in ids]
                   for side,ids in result['sole_vertex_ids'].items()}
        finally: evaluated.to_mesh_clear()
        rows.append({'frame':frame,'time_s':(frame-start)/scene.render.fps,'image':g.ref(image),
                     'actual_sole_vertices_world_m':soles})
    action=str(result.get('action','UNKNOWN_ACTION'))
    direction=str(result.get('screen_direction','UNKNOWN_DIRECTION'))
    g.write(out/'capture.json',{'scope':'SINGLE_LICENSED_MODEL_IN_PLACE_ACTION_DIAGNOSTIC',
        'action':action,'screen_direction':direction,
        'blend':result['output_blend'],'retarget_result':g.ref(args.result),'capture_generator':g.ref(__file__),
        'camera_world_matrix':camera,'native_resolution':[1920,1920], 'fps':scene.render.fps,
        'frames':rows,'cycle_seconds':(end-start)/scene.render.fps,'production_ready':False})


def main(args):
    import av
    import numpy as np
    from PIL import Image
    result=g.read(args.result); g.resolve(result['output_blend']); g.resolve(result['first_native_pose'])
    if result['source_duration_seconds']!=result['baked_duration_seconds']:
        raise ValueError('CADENCE_NOT_PRESERVED')
    out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('NOT_A_PRODUCTION_CAPTURE_ROUTE')
    out.mkdir(parents=True,exist_ok=False); cache=out/'cache'; cache.mkdir()
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'): env[key]=str(cache)
    env['OMP_NUM_THREADS']='2'; env['PYTHONDONTWRITEBYTECODE']='1'
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
        '--offline-mode','--threads','2','--python-exit-code','2','--python',str(Path(__file__).resolve()),
        '--','--result',str(g.local(args.result)),'--out',str(out),'--blender-capture']
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
            timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode: raise ValueError('DIAGNOSTIC_CYCLE_CAPTURE_FAILED: '+str(out/'blender.log'))
    report=g.read(out/'capture.json'); rows=report['frames'][:-1] # wrap sample is evidence, not an extra held frame
    fps=report['fps']
    if len(rows)/fps!=result['source_duration_seconds']: raise ValueError('VIDEO_CADENCE_MISMATCH')
    action_token=''.join(ch if ch.isalnum() else '_' for ch in str(result.get('action','ACTION'))).strip('_').upper()
    direction_token=''.join(ch if ch.isalnum() else '_' for ch in str(result.get('screen_direction','DIR'))).strip('_').upper()
    video=out/f'ASTRA_VRM_UAL_{action_token}_{direction_token}_DIAGNOSTIC_NATIVE.mp4'
    with av.open(str(video),'w') as container:
        stream=container.add_stream('libx264',rate=fps); stream.width=stream.height=1920
        stream.pix_fmt='yuv420p'; stream.options={'crf':'18','preset':'fast','threads':'2'}
        # Repeat the single observed cycle three times for viewing; this is not
        # three independent motion tests or the final two-cycle runtime gate.
        for index,row in enumerate(rows*3):
            with Image.open(g.resolve(row['image'])) as im:
                if im.size!=(1920,1920): raise ValueError('NATIVE_IMAGE_SIZE_CHANGED')
                rgb=np.asarray(im.convert('RGB'))
            frame=av.VideoFrame.from_ndarray(rgb,format='rgb24'); frame.pts=index; frame.time_base=Fraction(1,fps)
            for packet in stream.encode(frame): container.mux(packet)
        for packet in stream.encode(): container.mux(packet)
    g.resolve(result['output_blend'])
    g.write(out/'video_manifest.json',{'status':'DIAGNOSTIC_CAPTURE_COMPLETE_NOT_RUNTIME_PASS',
        'video':g.ref(video),'capture':g.ref(out/'capture.json'),'fps':fps,'unique_frames':len(rows),
        'action':result.get('action'),'screen_direction':result.get('screen_direction'),
        'playback_repetitions':3,'duration_seconds':len(rows)*3/fps,'native_resolution':[1920,1920],
        'owned_child_exited':True,'production_ready':False,'luna_test_permitted':False})
    print(str(out/'video_manifest.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',required=True); p.add_argument('--out',required=True)
    p.add_argument('--blender-capture',action='store_true')
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    args=p.parse_args(argv)
    if args.blender_capture: capture(args)
    else: main(args)
