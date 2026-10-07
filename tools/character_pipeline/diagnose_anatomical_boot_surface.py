"""One bounded no-render geometry diagnostic; not a production construction."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def geometry_summary(mesh):
    from mathutils import Vector
    mesh.calc_loop_triangles()
    neighbors = {i: set() for i in range(len(mesh.polygons))}
    edges = {}
    for face in mesh.polygons:
        ids = list(face.vertices)
        for a, b in zip(ids, ids[1:] + ids[:1]):
            edges.setdefault(tuple(sorted((a, b))), []).append(face.index)
    for faces in edges.values():
        for f in faces:
            neighbors[f].update(x for x in faces if x != f)
    remaining = set(neighbors); components = []
    while remaining:
        pending = [remaining.pop()]; component = set(pending)
        while pending:
            for f in neighbors[pending.pop()] & remaining:
                remaining.remove(f); component.add(f); pending.append(f)
        ids = {i for f in component for i in mesh.polygons[f].vertices}
        volume = 0.; normal_error = 0.
        for tri in mesh.loop_triangles:
            if tri.polygon_index not in component:
                continue
            a, b, c = [mesh.vertices[i].co for i in tri.vertices]
            volume += a.dot(b.cross(c)) / 6
            n = (b-a).cross(c-a)
            if n.length > 1e-12:
                normal_error = max(normal_error, (n.normalized()-mesh.polygons[tri.polygon_index].normal).length)
        vertices = [mesh.vertices[i] for i in ids]
        bottom = min(v.co.z for v in vertices)
        down = {i for f in component if mesh.polygons[f].normal.z < -.55 for i in mesh.polygons[f].vertices}
        low = {v.index for v in vertices if v.co.z < bottom + .006}
        components.append({'faces': len(component), 'vertices': len(ids),
                           'face_ids': sorted(component), 'signed_volume_m3': volume,
                           'side_x_mean': sum(v.co.x for v in vertices)/len(vertices),
                           'boundary_edges': sum(len(v)==1 and v[0] in component for v in edges.values()),
                           'nonmanifold_edges': sum(len(v)>2 and v[0] in component for v in edges.values()),
                           'direct_vs_rna_normal_max': normal_error,
                           'lowest': len(low), 'downward': len(down), 'intersection': len(low & down)})
    return components


def fold_summary(mesh):
    mesh.calc_loop_triangles()
    total_area = 0.; opposite_area = 0.; rows = []
    for tri in mesh.loop_triangles:
        a,b,c = [mesh.vertices[i].co for i in tri.vertices]
        cross = (b-a).cross(c-a); area = cross.length/2; total_area += area
        if cross.length < 1e-12:
            continue
        dot = cross.normalized().dot(mesh.polygons[tri.polygon_index].normal)
        if dot < 0:
            opposite_area += area
            rows.append({'face': tri.polygon_index, 'ids': list(tri.vertices), 'area': area, 'dot': dot,
                         'coordinates': [list(mesh.vertices[i].co) for i in mesh.polygons[tri.polygon_index].vertices]})
    return {'opposite_triangles': len(rows), 'opposite_area_m2': opposite_area,
            'total_area_m2': total_area, 'worst': sorted(rows, key=lambda r:r['dot'])[:8]}


def collect(out):
    import bpy
    import bmesh
    from mathutils import Matrix
    import build_mica_anatomical_candidate as builder
    bpy.ops.wm.read_factory_settings(use_empty=True)
    expected = ['GEO-body_female_realistic', 'Realistic_Base_Anatomical_Rig']
    with bpy.data.libraries.load(str(builder.RIG_INPUT), link=False) as (available, selected):
        if any(n not in available.objects for n in expected):
            raise ValueError('EXACT_ANATOMICAL_INPUT_REQUIRED')
        selected.objects = list(expected)
    for ob in selected.objects:
        bpy.context.scene.collection.objects.link(ob)
    body = next(o for o in selected.objects if o.name == expected[0])
    rig = next(o for o in selected.objects if o.type == 'ARMATURE')
    rig.animation_data_clear()
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    mat = builder.material('diagnostic_not_art', (.1, .1, .1))
    offset_comparison = {'original_body': fold_summary(body.data)}
    for amount in (0., .001, .003, .006, .009):
        sampled, _ = builder.fitted_region(body, 'OFFSET_DIAGNOSTIC_'+str(amount), lambda p:p.z<.43,
                                           amount, mat, 'boots', rig, False)
        offset_comparison[str(amount)] = fold_summary(sampled.data)
    before_cap, _ = builder.fitted_region(body, 'BEFORE_CAP_DIAGNOSTIC', lambda p: p.z < .43,
                                          .009, mat, 'boots', rig, False)
    stages = {'after_mesh_object_recalc_before_cuff': geometry_summary(before_cap.data)}
    boot, source_ids = builder.fitted_region(body, 'ACTUAL_BOOT_DIAGNOSTIC', lambda p: p.z < .43,
                                             .009, mat, 'boots', rig, True)
    boot.data.update()
    stages['after_cuff_closed_recalc'] = geometry_summary(boot.data)
    report = {'production_ready': False, 'rendered': False,
              'builder': g.ref(builder.__file__), 'input': g.ref(builder.RIG_INPUT),
              'diagnostic': g.ref(__file__), 'body_vertices': len(body.data.vertices),
              'boot_vertices': len(boot.data.vertices), 'boot_faces': len(boot.data.polygons),
              'stages': stages, 'offset_comparison': offset_comparison, 'sides': {}}
    for side, sign in [('left', 1), ('right', -1)]:
        vertices = [v for v in boot.data.vertices if v.co.x * sign > 0]
        bottom = min(v.co.z for v in vertices)
        faces = [p for p in boot.data.polygons if p.center.x * sign > 0]
        downward = {i for p in faces if p.normal.z < -.55 for i in p.vertices}
        low_ids = [v.index for v in vertices if v.co.z < bottom + .006]
        report['sides'][side] = {
            'bottom': bottom, 'extent': [[min(v.co[i] for v in vertices), max(v.co[i] for v in vertices)] for i in range(3)],
            'downward_face_count': sum(p.normal.z < -.55 for p in faces),
            'downward_vertex_count': len(downward), 'lowest_vertex_count': len(low_ids),
            'intersection_ids': sorted(set(low_ids) & downward),
            'low_vertices': [{'index': i, 'source_index': source_ids[i],
                              'position': list(boot.data.vertices[i].co),
                              'source_position': list(body.data.vertices[source_ids[i]].co),
                              'source_normal': list(body.data.vertices[source_ids[i]].normal),
                              'normal': list(boot.data.vertices[i].normal),
                              'adjacent_faces': [{'id': p.index, 'normal': list(p.normal), 'area': p.area,
                                                  'center': list(p.center), 'ids': list(p.vertices)}
                                                 for p in faces if i in p.vertices]}
                             for i in low_ids],
            'lowest_24_vertices': [{'index': v.index, 'co': list(v.co), 'normal': list(v.normal)}
                                  for v in sorted(vertices, key=lambda v: v.co.z)[:24]],
        }
    # Diagnostic only: orient each already-closed component by its measured
    # signed volume. Do not move/flatten vertices or relax selection criteria.
    negative = {i for c in stages['after_cuff_closed_recalc'] if c['signed_volume_m3'] < 0 for i in c['face_ids']}
    bm = bmesh.new(); bm.from_mesh(boot.data); bm.faces.ensure_lookup_table()
    for index in negative:
        bm.faces[index].normal_flip()
    bm.normal_update(); bm.to_mesh(boot.data); bm.free(); boot.data.update()
    stages['diagnostic_component_outward_repair'] = geometry_summary(boot.data)
    g.write(out / 'BOOT_SURFACE_DIAGNOSTIC.json', report)
    print(json.dumps({k: {x: v[x] for x in ('bottom', 'downward_face_count', 'downward_vertex_count',
                                           'lowest_vertex_count', 'intersection_ids')} for k, v in report['sides'].items()}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True)
    p.add_argument('--inside-blender', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    out = g.local(a.out)
    if not out.is_relative_to(ROOT / 'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_QUARANTINE_ONLY')
    if a.inside_blender:
        collect(out)
        return
    out.mkdir(parents=True, exist_ok=False)
    cache = out / 'cache'; cache.mkdir()
    env = os.environ.copy()
    for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA', 'XDG_CACHE_HOME',
                'XDG_DATA_HOME', 'BLENDER_USER_CONFIG', 'BLENDER_USER_SCRIPTS', 'PYTHONPYCACHEPREFIX'):
        env[key] = str(cache)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '2'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    import build_mica_anatomical_candidate as builder
    before = g.ref(builder.RIG_INPUT)
    command = [str(ROOT / 'tools/blender/5.2.1/blender.exe'), '--background', '--factory-startup',
               '--disable-autoexec', '--offline-mode', '--threads', '2', '--python-exit-code', '2',
               '--python', __file__, '--', '--inside-blender', '--out', str(out)]
    with (out / 'blender.log').open('w', encoding='utf-8') as log:
        child = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                               timeout=90, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if child.returncode or before != g.ref(builder.RIG_INPUT):
        raise ValueError('DIAGNOSTIC_FAILED_OR_INPUT_CHANGED')
    g.write(out / 'completion.json', {'owned_child_exited': True, 'original_unchanged': True,
                                     'report': g.ref(out / 'BOOT_SURFACE_DIAGNOSTIC.json'), 'production_ready': False})
    print(str(out / 'BOOT_SURFACE_DIAGNOSTIC.json'))


if __name__ == '__main__':
    main()
