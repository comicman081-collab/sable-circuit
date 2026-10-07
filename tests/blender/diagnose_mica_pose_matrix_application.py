"""Read-only Blender diagnostic for the rejected MICA E contact-pose attempt.

This creates no character render, never saves the historical Blend, and only
writes a project-local measurement report.  It reproduces the exact global-pose
assignment used by the bounded builder so a failed attempt can be repaired with
measured evidence instead of a blind retry.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/generation_harness_audit/mica_E_pose_matrix_application_r06/REPORT.json'
NEUTRAL = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_projected_neutral_r02/PROJECTED_SOURCE_NEUTRAL.blend'
SKIN = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_forward_clip_r02/SOURCE_SKIN.json'
POSES = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_native_dense_world_anchor_math_r03/PROPOSED_GLOBAL_MATRICES.npy'
NATIVE_POSITIONS = ROOT / 'artifacts/quarantine/generation_diagnostics/mica_E_native_binding_inspection_r01/ACTUAL_FRONT_POSITIONS_BLENDER.npy'
SAMPLE = 46

if '--' not in sys.argv:
    raise SystemExit('Blender invocation separator is required')

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix  # noqa: E402


def main():
    if OUT.exists():
        raise RuntimeError('RETAIN_EXISTING_DIAGNOSTIC_USE_FRESH_OUTPUT')
    bpy.ops.wm.open_mainfile(filepath=str(NEUTRAL))
    skin = json.loads(SKIN.read_text(encoding='utf-8'))
    poses = np.load(POSES, allow_pickle=False)
    rig = bpy.data.objects.get('CHR_PROTO_03_SourceRig')
    if rig is None:
        raise RuntimeError('EXPECTED_RIG_NOT_FOUND')
    rows = skin['bone_order']
    if poses.shape[1] != len(rows):
        raise RuntimeError('POSE_BONE_ORDER_MISMATCH')
    def reset():
        for row in rows:
            rig.pose.bones[row['name']].matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def assign_and_measure(target, update_each=False):
        reset()
        for index, row in enumerate(rows):
            rig.pose.bones[row['name']].matrix = Matrix(target[index].tolist())
            if update_each:
                bpy.context.view_layer.update()
        bpy.context.view_layer.update()
        return [{
            'name': row['name'],
            'parent': rig.pose.bones[row['name']].parent.name if rig.pose.bones[row['name']].parent else None,
            'max_component_error': float(np.max(np.abs(np.asarray(rig.pose.bones[row['name']].matrix, dtype=float) - target[index]))),
            'translation_error_m': float(np.linalg.norm(np.asarray(rig.pose.bones[row['name']].matrix, dtype=float)[:3, 3] - target[index][:3, 3])),
        } for index, row in enumerate(rows)]

    rest = np.asarray([np.asarray(rig.data.bones[row['name']].matrix_local, dtype=float) for row in rows])
    rest_values = assign_and_measure(rest)
    values = assign_and_measure(poses[SAMPLE])
    incremental_values = assign_and_measure(poses[SAMPLE], update_each=True)
    mesh = bpy.data.objects.get('CHR_PROTO_03_SourceSurface_E')
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated.to_mesh()
    try:
        actual = np.asarray([tuple(vertex.co) for vertex in evaluated_mesh.vertices], dtype=float)
    finally:
        evaluated.to_mesh_clear()
    native_positions = np.load(NATIVE_POSITIONS, allow_pickle=False)
    weights = np.asarray(skin['weights'], dtype=float).reshape(-1, 4)
    indices = np.asarray(skin['bones'], dtype=int).reshape(-1, 4)
    count = native_positions.shape[0]
    points = np.c_[native_positions, np.ones(count)]
    deform = poses[SAMPLE] @ np.linalg.inv(rest)
    predicted = (np.einsum('nkij,nj->nki', deform[indices], points) * weights[:, :, None]).sum(axis=1)[:, :3]
    vertex_error = float(np.max(np.linalg.norm(actual[:count] - predicted, axis=1)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'schema': 1,
        'kind': 'read_only_pose_matrix_assignment_diagnostic',
        'sample': SAMPLE,
        'blend': str(NEUTRAL.relative_to(ROOT)).replace('\\', '/'),
        'source_skin': str(SKIN.relative_to(ROOT)).replace('\\', '/'),
        'proposed_poses': str(POSES.relative_to(ROOT)).replace('\\', '/'),
        'native_positions': str(NATIVE_POSITIONS.relative_to(ROOT)).replace('\\', '/'),
        'rest_assignment_max_component_error': max(v['max_component_error'] for v in rest_values),
        'rest_assignment_bones': rest_values,
        'parent_to_child_incremental_pose_assignment_max_component_error': max(v['max_component_error'] for v in incremental_values),
        'parent_to_child_incremental_pose_assignment_bones': incremental_values,
        'parent_to_child_incremental_vertex_error_m': vertex_error,
        'max_component_error': max(v['max_component_error'] for v in values),
        'bones': values,
        'note': 'No render, image write, Blend save, or production approval.',
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


main()
