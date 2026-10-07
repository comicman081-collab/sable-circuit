"""Real Godot public-input regression using synthetic channel-marker atlases.

These deliberately non-character images prove clip selection/clock/socket code,
not anatomy, native visual quality or production readiness. Retain all evidence.
"""
import argparse
import os
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import motion_harness as h


def prepare(out, tripo_timing=None):
    out.mkdir(parents=True, exist_ok=False)
    cell, count = 32, 24
    assets = []
    directions = {}
    for mode in ('walk', 'run'):
        phase_values=None
        fps=24 if mode=='walk' else 32
        if mode=='run' and tripo_timing:
            timing=h.read(tripo_timing)
            if timing.get('scope')!='TRIPO_RUN_TIMING_FOR_IMPLEMENTATION_TESTS' or timing.get('production_ready') is not False:
                raise ValueError('EXPLICIT_TECHNICAL_TRIPO_TIMING_REQUIRED')
            for key in ('generator','calibration','retarget_result','source_pack'):h.verify_evidence_file(timing[key])
            count=int(timing['frames']);fps=float(timing['fps']);phase_values=h.phase_starts(timing)
        for move_index, move in enumerate(h.DIRECTIONS):
            for aim_index, aim in enumerate(h.DIRECTIONS):
                for firing in (False, True):
                    image = Image.new('RGBA', (cell, cell * count))
                    draw = ImageDraw.Draw(image)
                    points = []
                    for frame in range(count):
                        top = frame * cell
                        color = (30 + move_index * 25, 30 + aim_index * 25, 220 if firing else 80, 255)
                        draw.rectangle((3, top+3, 24, top+22), fill=color)
                        draw.rectangle((frame % 22+3, top+24, frame % 22+5, top+29), fill='white')
                        point = [25+frame % 3, 10+frame % 4]
                        points.append(point)
                        draw.point((point[0], top+point[1]), fill='red')
                        draw.point((1,top+1),fill='cyan' if mode=='run' else 'yellow')
                    path = out / f'{mode}_{move}_{aim}_{int(firing)}.png'
                    image.save(path)
                    assets.append({'mode':mode, 'move':move, 'aim':aim, 'firing':firing,
                        'path':h.rel(path), 'sha256':h.digest(path), 'cell_size':cell,
                        'frames':count, 'fps':fps, 'muzzle_xy':points,
                        **({'phase_starts':phase_values} if phase_values is not None else {})})
                    if mode == 'walk' and move == aim and not firing:
                        directions[move] = {'muzzle_xy':points[0]}
                        for state in ('idle','move','fire'):
                            directions[move][state+'_atlas'] = h.rel(path)
                            directions[move][state+'_muzzle_xy'] = points
    descriptor = {'schema':2, 'actor_id':'CHR_PROTO_03', 'costume_id':'QA_NOT_MICA',
        'qa_fixture_only':True, 'purpose':'SYNTHETIC_CHANNEL_MARKERS_NOT_CHARACTER_APPROVAL',
        'cell_size':cell, 'display_scale':1.7, 'display_offset':[13,-9],
        'states':{state:{'frames':count,'fps':24} for state in ('idle','move','fire')},
        'directions':directions, 'aim_move_policy':'authored_8x8',
        'representation':{'schema':1,'kind':'authored_8x8','assets':assets}}
    path = out / 'runtime_descriptor.json'
    if tripo_timing:
        descriptor['technical_motion_timing']={'path':h.rel(tripo_timing),'sha256':h.digest(tripo_timing)}
        timing=h.read(tripo_timing)
        refs=[{'path':h.rel(tripo_timing),'sha256':h.digest(tripo_timing)}]+[timing[k] for k in ('generator','calibration','retarget_result','source_pack')]
        h.write(out/'MOTION_BUILD_INPUTS.json',{'files':{r['path']:r['sha256'] for r in refs}})
    h.write(path, descriptor)
    return path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--godot',required=True)
    p.add_argument('--hz',type=int,choices=(30,60,120))
    p.add_argument('--tripo-timing',type=Path)
    a=p.parse_args()
    root=ROOT/'artifacts/motion_harness_audit/technical_fixtures'/('combined_'+uuid.uuid4().hex)
    os.environ['SABLE_CHANNEL_MARKER_PROBE']='1'
    descriptor=prepare(root/'input',a.tripo_timing)
    print(h.rel(root),flush=True)
    result=h.run_engine(descriptor,a.godot,root/'engine',[a.hz] if a.hz else None)
    print(result,flush=True)
    if result['gate']=='FAIL': raise SystemExit(1)


if __name__=='__main__':
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    main()
