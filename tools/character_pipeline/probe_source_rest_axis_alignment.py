"""Read-only mathematical retarget probe; no scene, art, or runtime asset export."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import generation_harness as g
from audit_source_skin_clip import transform

ROOT = Path(__file__).resolve().parents[2]


def global_rows(rows, poses):
    result = []
    for row, pose in zip(rows, poses):
        result.append((result[row['parent']] if row['parent'] >= 0 else np.eye(4)) @ transform(pose))
    return result


def minimal_rotation(a, b):
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    cross = np.cross(a, b)
    cosine = np.clip(np.dot(a, b), -1, 1)
    if cosine < -0.999999:
        axis = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0])
        return Rotation.from_rotvec(axis / np.linalg.norm(axis) * np.pi).as_matrix()
    return Rotation.from_quat([*cross, 1 + cosine]).as_matrix()


def run():
    directory = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_forward_clip_r02'
    skin = g.read(directory / 'SOURCE_SKIN.json')
    target = g.read(directory / 'MOTION_PACK.json')
    source_path = ROOT / 'art_src/motion_reference/tripo_run_20260908/skeletal_pack_r04/MOTION_PACK.json'
    source = g.read(source_path)
    target_rest = global_rows(target['bone_order'], [r['rest'] for r in target['bone_order']])
    source_rest = global_rows(source['bone_order'], [r['rest'] for r in source['bone_order']])
    alignment = np.eye(4)
    alignment[:3, :3] = Rotation.from_euler('y', 90, degrees=True).as_matrix()
    source_rest = {r['name']: alignment @ m for r, m in zip(source['bone_order'], source_rest)}
    inverse = np.linalg.inv(target_rest)
    uv = np.asarray(skin['uv']).reshape(-1, 2) * [1024, 1536]
    points = np.c_[np.asarray(skin['positions']).reshape(-1, 3), np.ones(len(uv))]
    indices = np.asarray(skin['bones']).reshape(-1, 4)
    weights = np.asarray(skin['weights']).reshape(-1, 4)
    selections = {'left': np.where((uv[:,0]>600)&(uv[:,0]<803)&(uv[:,1]>1420)&(uv[:,1]<1475))[0],
                  'right': np.where((uv[:,0]>166)&(uv[:,0]<270)&(uv[:,1]>1470)&(uv[:,1]<1494))[0]}
    floor = min(float(points[v, 1].min()) for v in selections.values())
    results = []
    for sample, frame in enumerate(source['clips']['run/forward']['frames']):
        posed = {r['name']: alignment @ m for r, m in zip(source['bone_order'], global_rows(source['bone_order'], frame['poses']))}
        globals_out = []
        for i, row in enumerate(target['bone_order']):
            name, parent = row['name'], row['parent']
            rest = target_rest[i]
            matrix = rest.copy()
            if name.startswith(('thigh_', 'calf_', 'foot_', 'ball_')):
                # Export basis maps Blender's bone +Y to Godot's local -Z.
                matrix[:3, :3] = minimal_rotation(-rest[:3, 2], -posed[name][:3, 2]) @ rest[:3, :3]
            elif name == 'pelvis':
                matrix[:3, :3] = posed[name][:3, :3] @ np.linalg.inv(source_rest[name][:3, :3]) @ rest[:3, :3]
            if parent < 0:
                matrix[:3, 3] = rest[:3, 3] + (posed[name][:3, 3] - source_rest[name][:3, 3]) * target['retarget_leg_ratio']
            else:
                matrix[:3, 3] = (globals_out[parent] @ inverse[parent] @ rest[:, 3])[:3]
            globals_out.append(matrix)
        deformation = np.asarray(globals_out) @ inverse
        row = {'sample': sample}
        for side, selected in selections.items():
            transformed = np.einsum('nkij,nj->nki', deformation[indices[selected]], points[selected])
            positions = (transformed * weights[selected, :, None]).sum(axis=1)
            row[side + '_sole_height_m'] = float(positions[:, 1].min() - floor)
        results.append(row)
    out = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_rest_axis_math_r01'
    out.mkdir(exist_ok=False)
    g.write(out / 'PROBE.json', {'inputs': {'skin': g.ref(directory / 'SOURCE_SKIN.json'),
        'target': g.ref(directory / 'MOTION_PACK.json'), 'source': g.ref(source_path), 'probe': g.ref(__file__)},
        'source_sole_roi': {'left': [600,1420,803,1475], 'right': [166,1470,270,1494]},
        'roi_independent_review': 'PENDING', 'fixed_neutral_floor_m': floor, 'samples': results,
        'scope': 'mathematical orientation hypothesis only; no Blender evaluation, no art or motion export',
        'per_frame_floor_correction': False, 'production_ready': False})
    print(json.dumps({side: [min(r[side+'_sole_height_m'] for r in results), max(r[side+'_sole_height_m'] for r in results)] for side in selections}))


if __name__ == '__main__':
    run()
