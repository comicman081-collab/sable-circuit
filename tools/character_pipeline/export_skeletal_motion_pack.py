"""Export evaluated Blender bones, without rasterizing or replacing character art.

The result is a reusable motion input, not a MICA model or a promotion receipt.
Only the owned Blender child opens the exact, hash-bound source blend. All
original meshes, materials, actions and installed runtimes remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def child(args):
    import bpy
    from mathutils import Matrix

    out = g.local(args.out)
    inputs = g.read(out / 'INPUTS.json')
    for reference in inputs.values():
        g.resolve(reference)
    if inputs['exporter'] != g.ref(__file__):
        raise ValueError('EXPORTER_CHANGED')
    result = g.read(g.resolve(inputs['retarget_result']))
    calibration = g.read(g.resolve(inputs['calibration']))
    if (result['output_blend'] != inputs['blend'] or calibration['input_blend'] != inputs['blend']
            or calibration['input_result'] != inputs['retarget_result']):
        raise ValueError('EXACT_RETARGET_CALIBRATION_BLEND_RELATIONSHIP_REQUIRED')
    g.write(out / 'CHILD_CLAIM.json', {'inputs': g.ref(out / 'INPUTS.json')})
    bpy.ops.wm.open_mainfile(filepath=str(g.resolve(inputs['blend'])), load_ui=False)
    mesh = bpy.data.objects[result['sole_mesh']]
    rigs = {modifier.object for modifier in mesh.modifiers
            if modifier.type == 'ARMATURE' and modifier.object is not None}
    if len(rigs) != 1:
        raise ValueError('ONE_ACTUAL_DEFORM_RIG_REQUIRED')
    rig = rigs.pop()
    # Godot X/Y/Z = Blender X/Z/-Y. This is a right-handed basis change,
    # applied to both rest and evaluated local transforms, including root scale.
    axes = Matrix(((1, 0, 0, 0), (0, 0, 1, 0),
                   (0, -1, 0, 0), (0, 0, 0, 1)))
    inverse_axes = axes.inverted()
    bones = sorted(rig.data.bones, key=lambda bone: (len(bone.parent_recursive), bone.name))
    indices = {bone.name: index for index, bone in enumerate(bones)}

    def transform(matrix):
        translation, rotation, scale = (axes @ matrix @ inverse_axes).decompose()
        if rotation.w < 0:
            rotation.negate()
        return {'p': list(translation), 'q': [rotation.x, rotation.y, rotation.z, rotation.w],
                's': list(scale)}

    rest = []
    for bone in bones:
        local = (bone.parent.matrix_local.inverted() @ bone.matrix_local
                 if bone.parent else rig.matrix_world @ bone.matrix_local)
        rest.append({'name': bone.name, 'parent': indices[bone.parent.name] if bone.parent else -1,
                     'rest': transform(local)})
    if calibration['input_result'] != inputs['retarget_result']:
        raise ValueError('CALIBRATION_FROM_ANOTHER_RETARGET')
    samples = calibration['samples']
    if not 2 <= len(samples) <= 49:
        raise ValueError('BOUNDED_TWO_TO_49_EVALUATED_SAMPLES_REQUIRED')
    if any(b['time_s'] <= a['time_s'] for a, b in zip(samples, samples[1:])):
        raise ValueError('STRICT_NATIVE_TIMESTAMPS_REQUIRED')
    first_time = samples[0]['time_s']
    duration = samples[-1]['time_s'] - first_time
    if abs(duration - result['derived_period_s']) > 1e-7:
        raise ValueError('NATIVE_PERIOD_MISMATCH')
    frames = []
    for sample in samples:
        frame = sample['frame']
        bpy.context.scene.frame_set(int(frame), subframe=frame - int(frame))
        bpy.context.view_layer.update()
        poses = []
        for bone in bones:
            posed = rig.pose.bones[bone.name]
            local = (posed.parent.matrix.inverted() @ posed.matrix
                     if posed.parent else rig.matrix_world @ posed.matrix)
            poses.append(transform(local))
        frames.append({'time_s': sample['time_s'] - first_time, 'poses': poses})
    roles = {'hips': 'pelvis', 'spine': 'spine_01', 'chest': 'spine_03', 'head': 'Head',
             **{f'{side}_{role}': f'{stem}_{side[0]}'
                for side in ('left', 'right')
                for role, stem in [('thigh', 'thigh'), ('calf', 'calf'), ('foot', 'foot'),
                                   ('toe', 'ball'), ('upperarm', 'upperarm'),
                                   ('forearm', 'lowerarm'), ('hand', 'hand')]}}
    if any(name not in indices for name in roles.values()):
        raise ValueError('HUMANOID_ROLE_MISSING')
    pack = {'schema': 1, 'representation': 'evaluated_skeleton_motion',
            'scope': 'motion_reference_only', 'production_ready': False,
            'visible_art_included': False, 'inputs': inputs, 'coordinate_system': 'godot_y_up',
            'bone_order': rest, 'humanoid_roles': roles,
            'forward_axis': [calibration['travel_axis_world'][0],
                             calibration['travel_axis_world'][2],
                             -calibration['travel_axis_world'][1]],
            'clips': {'run/forward': {'duration_s': duration, 'loop': True,
                      'distance_m': result['nominal_target_distance_per_cycle_m'],
                      'frames': frames}},
            'coverage': {'run_relative_directions': ['forward'], 'walk_relative_directions': [],
                         'rifle_aim': False, 'rifle_fire': False, 'rifle_reload': False},
            'planar_transport_removed': True, 'vertical_root_motion_preserved': True,
            'limitations': ['No character appearance or weapon is created by this exporter.',
                            'Rotating forward run is not strafe/backward aiming coverage.',
                            'Target character binding and gait/appearance reviews are separate.']}
    g.write(out / 'MOTION_PACK.json', pack)
    # Re-evaluation and export must not mutate the source on disk.
    for reference in inputs.values():
        g.resolve(reference)


def run(args):
    result = g.read(args.result)
    out = g.local(args.out)
    if not out.is_relative_to(ROOT / 'art_src/motion_reference'):
        raise ValueError('MOTION_REFERENCE_OUTPUT_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    cache = out / 'cache'
    cache.mkdir()
    inputs = {'exporter': g.ref(__file__), 'retarget_result': g.ref(args.result),
              'calibration': g.ref(args.calibration),
              'blend': result['output_blend'], 'target_license': result['target_license'],
              'target_source': result['target_model'],
              'source_pack': result['source_pack'],
              'generation_harness': g.ref(ROOT / 'tools/character_pipeline/generation_harness.py')}
    for reference in inputs.values():
        g.resolve(reference)
    license_record = g.read(g.resolve(inputs['target_license']))
    if license_record.get('license') != 'CC0-1.0' or license_record.get('source_blend') != inputs['target_source']:
        raise ValueError('EXACT_LICENSED_TARGET_REQUIRED')
    g.write(out / 'INPUTS.json', inputs)
    env = os.environ.copy()
    for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA', 'XDG_CACHE_HOME',
                'XDG_DATA_HOME', 'BLENDER_USER_CONFIG', 'BLENDER_USER_SCRIPTS', 'PYTHONPYCACHEPREFIX'):
        env[key] = str(cache)
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', OMP_NUM_THREADS='2')
    command = [str(ROOT / 'tools/blender/5.2.1/blender.exe'), '--background', '--factory-startup',
               '--disable-autoexec', '--offline-mode', '--threads', '2', '--python-exit-code', '2',
               '--python', str(Path(__file__).resolve()), '--', '--inside', '--out', str(out)]
    with (out / 'blender.log').open('w', encoding='utf8') as log:
        process = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                 timeout=240, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if process.returncode:
        raise ValueError('BLENDER_EXPORT_FAILED:' + str(out / 'blender.log'))
    pack = g.read(out / 'MOTION_PACK.json')
    g.write(out / 'COMPLETION.json', {'status': 'BONE_MOTION_EXPORTED', 'production_ready': False,
                                    'pack': g.ref(out / 'MOTION_PACK.json'),
                                    'bone_count': len(pack['bone_order']), 'owned_child_exited': True})
    print('BONE_MOTION_EXPORTED', len(pack['bone_order']), 'bones;', len(pack['clips']['run/forward']['frames']), 'samples')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result')
    parser.add_argument('--calibration')
    parser.add_argument('--out', required=True)
    parser.add_argument('--inside', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    child(args) if args.inside else run(args)
