"""Check completed native clip data and captures; never confer visual approval."""
import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def transform(row):
    matrix = np.eye(4)
    matrix[:3, :3] = Rotation.from_quat(row['q']).as_matrix() @ np.diag(row['s'])
    matrix[:3, 3] = row['p']
    return matrix


def run(args):
    completion = g.read(args.completion)
    pack = g.read(g.resolve(completion['pack']))
    evaluated = g.read(g.resolve(completion['evaluated']))
    g.resolve(completion['skin'])
    g.resolve(completion['blend'])
    inputs = g.read(g.resolve(completion['inputs']))
    for reference in inputs.values():
        g.resolve(reference)
    clip = pack['clips']['run/forward']
    frames = clip['frames']
    if len(frames) != 49 or len(evaluated['samples']) != 49:
        raise ValueError('EXACT_49_ACTUAL_SAMPLES_REQUIRED')
    maximum_error = 0.0
    for frame, sample in zip(frames, evaluated['samples']):
        global_matrices = []
        for bone, pose in zip(pack['bone_order'], frame['poses']):
            matrix = transform(pose)
            if bone['parent'] >= 0:
                matrix = global_matrices[bone['parent']] @ matrix
            global_matrices.append(matrix)
            actual = np.asarray(sample['joints_godot_m'][bone['name']])
            if not np.isfinite(matrix).all() or not np.isfinite(actual).all():
                raise ValueError('NONFINITE_ACTUAL_JOINT_SAMPLE')
            maximum_error = max(maximum_error, float(np.linalg.norm(matrix[:3, 3] - actual)))
    if not np.isfinite(maximum_error) or maximum_error > 1e-5:
        raise ValueError('EXPORTED_HIERARCHY_DIFFERS_FROM_BLENDER_EVALUATION')
    captures = evaluated['captures']
    if [row['sample_index'] for row in captures] != list(range(0, 48, 3)):
        raise ValueError('EXACT_16_PHASE_CAPTURES_REQUIRED')
    decoded = []
    images = []
    for row in captures:
        with Image.open(g.resolve(row['image'])) as image:
            if image.size != (1920, 1080):
                raise ValueError('NATIVE_1080P_REQUIRED')
            image = image.convert('RGB')
            decoded.append(hashlib.sha256(image.tobytes()).hexdigest())
            images.append(image.copy())
    if len(set(decoded)) != 16:
        raise ValueError('DUPLICATED_VISIBLE_GAIT_PHASES')
    native = evaluated['original_scale_captures']
    if [row['sample_index'] for row in native] != [0, 12, 24, 36]:
        raise ValueError('FOUR_ORIGINAL_SCALE_PHASES_REQUIRED')
    for row in native:
        with Image.open(g.resolve(row['image'])) as image:
            if image.size != (1920, 1920):
                raise ValueError('NATIVE_ORIGINAL_SCALE_CAPTURE_REQUIRED')
    output = g.local(args.out)
    output.mkdir(parents=True, exist_ok=False)
    durations = [round((i+1)*clip['duration_s']*1000/16)-round(i*clip['duration_s']*1000/16) for i in range(16)]
    animation = output / 'FORWARD_NATIVE_1920x1080.png'
    images[0].save(animation, save_all=True, append_images=images[1:], duration=durations, loop=0)
    g.write(output / 'AUDIT.json', {'completion': g.ref(args.completion), 'auditor': g.ref(__file__),
            'maximum_joint_recomposition_error_m': maximum_error, 'compared_joints': len(frames)*len(pack['bone_order']),
            'distinct_decoded_frames': len(set(decoded)), 'duration_ms': sum(durations),
            'animation': g.ref(animation), 'scope': 'export fidelity and unique native frames only',
            'visual_review': 'PENDING', 'contact_review': 'PENDING', 'production_ready': False})
    print('ACTUAL_CLIP_EXPORT_FIDELITY_PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--completion', required=True)
    parser.add_argument('--out', required=True)
    run(parser.parse_args())
