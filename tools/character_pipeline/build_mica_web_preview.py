"""Export an isolated Godot web preview with byte-exact runtime source copies.

This technical build uses explicit synthetic atlases until a reviewed motion
descriptor is supplied by the production harness. It never invents MICA frames.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2),encoding='utf-8')


def main(a):
    out=(ROOT/a.out).resolve()
    if not out.is_relative_to(ROOT/'artifacts/web_runtime') or out.exists():raise ValueError('FRESH_PROJECT_WEB_OUTPUT_REQUIRED')
    descriptor=(ROOT/a.descriptor).resolve()
    if not descriptor.is_relative_to(ROOT):raise ValueError('PROJECT_DESCRIPTOR_REQUIRED')
    d=json.loads(descriptor.read_text(encoding='utf-8'))
    source_preview=d.get('preview_mode')=='reviewed_single_pose_controls'
    if source_preview:
        sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
        import generation_harness as g
        import visible_frame_harness_current as gate
        gate.install_current_patches()
        receipt=gate.frozen.verify_frame_receipt(g.resolve(d['source_frame_receipt']))
        manifest=g.read(g.resolve(receipt['frame_manifest']))
        approved=g.resolve(manifest['runtime_rgba'])
        if d.get('production_ready') is not False or d.get('motion_art_complete') is not False:
            raise ValueError('SINGLE_POSE_PREVIEW_CANNOT_CLAIM_MOTION_APPROVAL')
        for row in d['directions'].values():
            for state in ('idle','move','fire'):
                if g.local(row[state+'_atlas'])!=approved or d['states'][state]['frames']!=1:
                    raise ValueError('EXACT_REVIEWED_SINGLE_POSE_ONLY')
        scope='MICA SOURCE PREVIEW - 8-WAY CONTROLS / ANIMATION ART IN PROGRESS'
    else:
        if d.get('qa_fixture_only') is not True:raise ValueError('PRODUCTION_RECEIPT_ADAPTER_REQUIRED')
        scope='CONTROLS TEST - SYNTHETIC MARKERS / MICA MOTION ART NOT APPROVED'
    project=out/'project';public=out/'public';cache=out/'cache'
    for p in (project,public,cache):p.mkdir(parents=True)
    class_paths={}
    for p in (ROOT/'scripts').rglob('*.gd'):
        match=re.search(r'^class_name\s+(\w+)',p.read_text(encoding='utf-8-sig'),re.M)
        if match:class_paths[match[1]]=p
    queue=[ROOT/'scenes/qa/MicaMovementFireWeb.tscn'];seen=set();files={}
    while queue:
        p=queue.pop()
        if p in seen:continue
        if not p.is_file() or not p.is_relative_to(ROOT):raise ValueError('MISSING_SOURCE:'+str(p))
        seen.add(p);text=p.read_text(encoding='utf-8-sig')
        target=project/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);files[p.relative_to(ROOT).as_posix()]=digest(p)
        for name,path in class_paths.items():
            if re.search(r'\b'+name+r'\b',text):queue.append(path)
        for ref in re.findall(r'res://([^\s\"\'\)]+)',text):
            path=ROOT/ref
            if path.is_file() and path.suffix in ('.gd','.tscn','.tres','.gdshader','.json'):
                if path.suffix in ('.gd','.tscn','.tres','.gdshader'):queue.append(path)
                else:
                    dst=project/ref;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dst);files[ref]=digest(path)
    refs=[descriptor]+[ROOT/row['path'] for row in d.get('representation',{}).get('assets',[])]
    refs+=list({ROOT/row[state+'_atlas'] for row in d['directions'].values() for state in ('idle','move','fire')})
    for source in refs:
        dest=project/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);files[source.relative_to(ROOT).as_posix()]=digest(source)
        # Runtime intentionally decodes and hashes original PNG bytes. The
        # default texture importer removes those bytes from exported PCKs.
        if source.suffix=='.png':
            Path(str(dest)+'.import').write_text('[remap]\nimporter="keep"\n',encoding='utf-8')
    descriptor_res='res://'+descriptor.relative_to(ROOT).as_posix()
    (project/'project.godot').write_text('''config_version=5
[application]
config/name="SABLE CIRCUIT / MICA FIELD TEST"
run/main_scene="res://scenes/qa/MicaMovementFireWeb.tscn"
[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/stretch/mode="canvas_items"
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
[physics]
common/physics_ticks_per_second=60
[sable_web]
descriptor="'''+descriptor_res+'''"
asset_scope="'''+scope+'''"
''',encoding='utf-8')
    (project/'export_presets.cfg').write_text('''[preset.0]
name="Web"
platform="Web"
runnable=true
export_filter="all_resources"
include_filter="*.json,*.png"
exclude_filter=""
export_path="../public/index.html"
script_export_mode=1
[preset.0.options]
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
progressive_web_app/enabled=false
''',encoding='utf-8')
    env=os.environ.copy()
    for key in ('TEMP','TMP','TMPDIR','XDG_CACHE_HOME','XDG_DATA_HOME'):env[key]=str(cache)
    env['PYTHONDONTWRITEBYTECODE']='1'
    write(out/'SOURCE_SNAPSHOT.json',{'files':files,'descriptor':descriptor.relative_to(ROOT).as_posix(),'descriptor_sha256':digest(descriptor),'scope':'TECHNICAL_WEB_PREVIEW_NOT_MICA_VISUAL_APPROVAL','production_ready':False})
    for name,cmd in [('import',[a.godot,'--headless','--path',str(project),'--editor','--import']),('export',[a.godot,'--headless','--path',str(project),'--export-debug','Web',str(public/'index.html')])]:
        with (out/(name+'.log')).open('w',encoding='utf-8') as log:
            p=subprocess.run(cmd,cwd=project,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        if p.returncode:raise ValueError(name.upper()+'_FAILED:'+str(out/(name+'.log')))
    for path,sha in files.items():
        if digest(ROOT/path)!=sha or digest(project/path)!=sha:raise ValueError('SOURCE_CHANGED_DURING_EXPORT:'+path)
    required=[public/('index'+suffix) for suffix in ('.html','.js','.wasm','.pck')]
    if any(not p.is_file() or p.stat().st_size==0 for p in required):raise ValueError('INCOMPLETE_WEB_EXPORT')
    write(out/'BUILD.json',{'scope':'TECHNICAL_WEB_EXPORT_NEEDS_BROWSER_TEST','source_snapshot_sha256':digest(out/'SOURCE_SNAPSHOT.json'),'outputs':{p.relative_to(out).as_posix():digest(p) for p in required},'production_ready':False})
    print(out.relative_to(ROOT).as_posix(),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--descriptor',required=True);p.add_argument('--out',required=True);p.add_argument('--godot',required=True);main(p.parse_args())
