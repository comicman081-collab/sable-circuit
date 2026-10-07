"""Bounded no-render shoe-envelope diagnostic on actual anatomical feet."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
import generation_harness as g


def surface_record(mesh):
    from mathutils.bvhtree import BVHTree
    from mesh_surface_orientation import closed_component_orientation
    from triangle_surface_checks import triangles_intersect
    mesh.calc_loop_triangles()
    vertices = [list(v.co) for v in mesh.vertices]
    faces = [list(p.vertices) for p in mesh.polygons]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    bvh = BVHTree.FromPolygons(vertices, tris, all_triangles=True, epsilon=0.)
    overlap = [(a,b) for a,b in bvh.overlap(bvh) if a<b and not set(tris[a]) & set(tris[b])]
    intersections = [(a,b) for a,b in overlap if triangles_intersect([vertices[i] for i in tris[a]],
                                                                    [vertices[i] for i in tris[b]])]
    topology_error=None
    try: components = closed_component_orientation(vertices, faces)
    except ValueError as exc:
        from diagnose_anatomical_boot_surface import geometry_summary
        topology_error=str(exc); components=geometry_summary(mesh)
    return {'vertices': len(vertices), 'faces': len(faces),
            'components': [{k:v for k,v in c.items() if k not in ('face_ids','vertex_ids')} for c in components],
            'topology_error':topology_error,
            'bvh_candidate_pairs': len(overlap), 'nonadjacent_actual_triangle_intersections':len(intersections),
            'intersection_examples': intersections[:12],
            'extent': [[min(v[i] for v in vertices), max(v[i] for v in vertices)] for i in range(3)]}


def collect(out):
    import bpy
    import bmesh
    from mathutils import Matrix
    import build_mica_anatomical_candidate as b
    from diagnose_anatomical_boot_surface import fold_summary
    bpy.ops.wm.read_factory_settings(use_empty=True)
    names = ['GEO-body_female_realistic', 'Realistic_Base_Anatomical_Rig']
    with bpy.data.libraries.load(str(b.RIG_INPUT), link=False) as (_, selected):
        selected.objects = list(names)
    for ob in selected.objects: bpy.context.scene.collection.objects.link(ob)
    body = next(o for o in selected.objects if o.name==names[0])
    rig = next(o for o in selected.objects if o.type=='ARMATURE')
    rig.animation_data_clear()
    for pb in rig.pose.bones: pb.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    boot,_ = b.fitted_region(body,'DIAGNOSTIC_BOOT',lambda p:p.z<.43,.009,
                             b.material('diagnostic_not_art',(.1,.1,.1)),'boots',rig,True)
    report = {'production_ready':False, 'rendered':False, 'source':g.ref(b.RIG_INPUT),
              'builder':g.ref(b.__file__), 'diagnostic':g.ref(__file__),
              'before':surface_record(boot.data), 'fold_before':fold_summary(boot.data)}
    from anatomical_boot_envelope import rebuild_envelope
    weights,construction=rebuild_envelope(boot,body)
    b.skin(boot,rig,weights)
    report['construction']=construction
    report['adapter']=g.ref(ROOT/'tools/character_pipeline/anatomical_boot_envelope.py')
    report['orientation']=g.ref(ROOT/'tools/character_pipeline/mesh_surface_orientation.py')
    report['narrowphase']=g.ref(ROOT/'tools/character_pipeline/triangle_surface_checks.py')
    report['skin']={'unweighted':sum(not r for r in weights),
                    'weight_sum_max_error':max(abs(sum(r.values())-1) for r in weights),
                    'invalid_bones':sorted({n for r in weights for n in r if n not in rig.data.bones})}
    report['after_voxel'] = surface_record(boot.data)
    report['fold_after'] = fold_summary(boot.data)
    g.write(out/'VOLUME_DIAGNOSTIC.json',report)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out',required=True)
    p.add_argument('--inside-blender',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):
        raise ValueError('DIAGNOSTIC_OUTPUT_ONLY')
    if a.inside_blender: collect(out);return
    out.mkdir(parents=True,exist_ok=False); cache=out/'cache';cache.mkdir();env=os.environ.copy()
    for k in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
              'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[k]=str(cache)
    for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='2'
    env['PYTHONDONTWRITEBYTECODE']='1'
    import build_mica_anatomical_candidate as b
    before=g.ref(b.RIG_INPUT)
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
             '--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--inside-blender','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                             timeout=90,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode or before!=g.ref(b.RIG_INPUT):raise ValueError('FAILED_ORIGINAL_CHANGED')
    g.write(out/'completion.json',{'owned_child_exited':True,'original_unchanged':True,
                                  'production_ready':False,'report':g.ref(out/'VOLUME_DIAGNOSTIC.json')})
    print(str(out/'VOLUME_DIAGNOSTIC.json'))


if __name__=='__main__':main()
