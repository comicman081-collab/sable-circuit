"""Native antialiased captures of the baked skin, preserving its motion/art.

Render from the actual Blender action. The 4K battle capture is reduced once
for a 1080p display; the original texture and a large native pose remain intact.
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
    from mathutils import Vector
    out=g.local(args.out);inputs=g.read(out/'INPUTS.json')
    for reference in inputs.values():g.resolve(reference)
    completion=g.read(g.resolve(inputs['completion']))
    if completion['blend']!=inputs['blend'] or inputs['capture_tool']!=g.ref(__file__):
        raise ValueError('EXACT_NATIVE_MOTION_CAPTURE_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(inputs['blend'])),load_ui=False)
    scene=bpy.context.scene;scene.frame_set(12)
    scene.cycles.samples=64;scene.cycles.use_adaptive_sampling=False
    scene.cycles.use_denoising=False
    scene.render.resolution_x=3840;scene.render.resolution_y=2160
    scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.threads_mode='FIXED';scene.render.threads=2
    for material in bpy.data.materials:
        if not material.use_nodes:continue
        for node in material.node_tree.nodes:
            if node.type=='TEX_IMAGE':node.interpolation='Linear'
    camera=scene.camera;camera.location=Vector((0,-6,.86))
    camera.rotation_euler=(Vector((0,0,.86))-camera.location).to_track_quat('-Z','Y').to_euler()
    records=[]
    for name,height in [('POSE_MASTER',1280),('BATTLE',448)]:
        camera.data.ortho_scale=3840*1.72/height
        scene.render.filepath=str(out/f'{name}_NATIVE_3840x2160.png')
        bpy.ops.render.render(write_still=True)
        records.append({'image':g.ref(scene.render.filepath),'native_resolution':[3840,2160],
                        'nominal_character_height_px':height,'samples':64,'texture_filter':'Linear',
                        'denoising':False,'source_pixels_reauthored':False,'source_upscaled':False})
    g.write(out/'CAPTURE.json',{'inputs':g.ref(out/'INPUTS.json'),'sample_index':12,'records':records,
                               'scope':'NATIVE_FILTERING_COMPARISON_NOT_FINISHED_COMBAT_ART','production_ready':False})


def run(args):
    from PIL import Image
    out=g.local(args.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_ROOT_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);(out/'cache').mkdir()
    completion=g.read(args.completion)
    g.write(out/'INPUTS.json',{'completion':g.ref(args.completion),'blend':completion['blend'],
                             'capture_tool':g.ref(__file__),'generation_harness':g.ref(g.__file__)})
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(out/'cache')
    env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2')
    with (out/'blender.log').open('w',encoding='utf8') as log:
        subprocess.run([str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup',
                        '--disable-autoexec','--offline-mode','--threads','2','--python-exit-code','2',
                        '--python',str(Path(__file__).resolve()),'--','--inside','--out',str(out)],
                       cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    battle=Image.open(out/'BATTLE_NATIVE_3840x2160.png').convert('RGBA')
    # Premultiplied-alpha resize avoids transparent black RGB leaking into edges.
    battle=battle.convert('RGBa').resize((1920,1080),Image.Resampling.LANCZOS).convert('RGBA')
    battle.save(out/'BATTLE_RGBA_1920x1080.png')
    background=Image.new('RGBA',(1920,1080),(17,25,33,255));background.alpha_composite(battle)
    background.convert('RGB').save(out/'BATTLE_DISPLAY_1920x1080.png')
    master=Image.open(out/'POSE_MASTER_NATIVE_3840x2160.png').convert('RGBA')
    # This crop is native scale, not an enlargement of the battle sprite.
    bbox=master.getbbox();original_scale=master.crop((max(0,bbox[0]-40),max(0,bbox[1]-40),min(3840,bbox[2]+40),min(2160,bbox[3]+40)))
    evidence=Image.new('RGBA',(1920,1440),(17,25,33,255))
    evidence.alpha_composite(original_scale,((1920-original_scale.width)//2,(1440-original_scale.height)//2))
    evidence.convert('RGB').save(out/'ORIGINAL_SCALE_POSE_1920x1440.png')
    g.write(out/'DERIVATIVES.json',{'capture':g.ref(out/'CAPTURE.json'),'battle_scale_downsample':2,
                                  'battle_display':g.ref(out/'BATTLE_DISPLAY_1920x1080.png'),
                                  'original_scale_crop':g.ref(out/'ORIGINAL_SCALE_POSE_1920x1440.png'),
                                  'source_repainted':False,'production_ready':False})
    print('NATIVE_4K_ANTIALIASED_POSE_AND_BATTLE_CAPTURED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--completion')
    parser.add_argument('--out',required=True);parser.add_argument('--inside',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
