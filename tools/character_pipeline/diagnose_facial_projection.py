"""Bounded repair diagnostic on the preserved failed R3 scene, with no render."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
SOURCE=ROOT/'artifacts/quarantine/generation_diagnostics/mica_anatomical_model_r03/MICA_ANATOMICAL_NEUTRAL.blend'


def collect(out):
    import bpy
    from facial_overlay_projection import resolve_front_overlay
    from collect_generation_mesh_preflight import collect_scene,validate_collected
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
    source_before=g.ref(SOURCE)
    # Quarantine moved the old blend without changing its bytes. Its former
    # relative links must be restored only in this derived scene and only from
    # the content-bound approved chart refs; never search/substitute by filename.
    charts=json.loads(bpy.context.scene['generation_source_charts']);relinks=[]
    for ob in bpy.context.scene.objects:
        chart_ids=json.loads(ob.get('generation_chart_table','{}'))
        if not chart_ids:continue
        refs={json.dumps(charts[n]['image'],sort_keys=True) for n in chart_ids.values()}
        if len(refs)!=1:raise ValueError('EXPLICIT_SINGLE_CHART_IMAGE_REQUIRED')
        ref=json.loads(next(iter(refs)));expected=g.resolve(ref)
        for slot in ob.material_slots:
            if not slot.material or not slot.material.use_nodes:continue
            for node in slot.material.node_tree.nodes:
                if node.type!='TEX_IMAGE':continue
                relinks.append({'object':ob.name,'previous_path':node.image.filepath,'approved_image':ref})
                node.image.filepath=str(expected);node.image.reload()
    result=resolve_front_overlay(bpy.data.objects['MICA_Head'],bpy.data.objects['MICA_Anatomical_Body'],1024,1536)
    bpy.context.scene['diagnostic_only']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'PROJECTED_FACE_DIAGNOSTIC.blend'),relative_remap=False)
    raw=collect_scene();g.write(out/'MESH_PREFLIGHT_RAW.json',raw)
    audit=validate_collected(raw);g.write(out/'MESH_PREFLIGHT_AUDIT.json',audit)
    g.write(out/'PROJECTION_DIAGNOSTIC.json',{'production_ready':False,'rendered':False,
        'source':source_before,'source_unchanged':source_before==g.ref(SOURCE),
        'helper':g.ref(ROOT/'tools/character_pipeline/facial_overlay_projection.py'),
        'diagnostic':g.ref(__file__),'construction':result,'audit':g.ref(out/'MESH_PREFLIGHT_AUDIT.json'),
        'approved_image_relinks_in_derived_scene':relinks,
        'preflight_errors':audit['errors']})
    if audit['errors']:raise ValueError('PROJECTION_DIAGNOSTIC_FAIL:'+str(audit['errors']))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True)
    p.add_argument('--inside-blender',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    out=g.local(a.out)
    if not out.is_relative_to(ROOT/'artifacts/quarantine/generation_diagnostics'):raise ValueError('DIAGNOSTIC_ONLY')
    if a.inside_blender:collect(out);return
    out.mkdir(parents=True,exist_ok=False);cache=out/'cache';cache.mkdir();env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA','XDG_CACHE_HOME','XDG_DATA_HOME',
                'BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','PYTHONPYCACHEPREFIX'):env[key]=str(cache)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='2'
    env['PYTHONDONTWRITEBYTECODE']='1';before=g.ref(SOURCE)
    command=[str(ROOT/'tools/blender/5.2.1/blender.exe'),'--background','--factory-startup','--disable-autoexec',
             '--offline-mode','--threads','2','--python-exit-code','2','--python',__file__,'--','--inside-blender','--out',str(out)]
    with (out/'blender.log').open('w',encoding='utf-8') as log:
        child=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                             timeout=90,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if child.returncode or before!=g.ref(SOURCE):raise ValueError('DIAGNOSTIC_FAILED_OR_SOURCE_CHANGED')
    g.write(out/'completion.json',{'owned_child_exited':True,'source_unchanged':True,
                                  'production_ready':False,'report':g.ref(out/'PROJECTION_DIAGNOSTIC.json')})
    print(str(out/'PROJECTION_DIAGNOSTIC.json'))


if __name__=='__main__':main()
