"""Embed a reviewed character and the shared runtime into one offline HTML file."""
from pathlib import Path
import argparse,base64,json,re,hashlib
ROOT=Path(__file__).resolve().parent
RUNTIME_FILES=['simulation.js','atlas-renderer.js','keyboard-input.js','combat-aim.js','studio.js']
DIRECTIONS={'E','SE','S','SW','W','NW','N','NE'}
REQUIRED_ATLAS_MARKERS=('class AtlasRenderer','window.__MOTION_BUILD__')
RETIRED_MESH_MARKERS=('class CharacterRenderer','function deformPoint')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def bundle_inputs(ident, atlas_public=None, runtime_public=None):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):raise ValueError('Invalid character id')
    # Candidate builds may be read from an isolated build stage while the
    # shared runtime remains the reviewed project copy.  This keeps a partial
    # atlas out of the live public pointer until all runtime gates pass.
    public=(atlas_public or ROOT/'public').resolve()
    runtime=(runtime_public or ROOT/'public').resolve()
    path=public/'assets/atlas'/ident/'profile.json'
    profile=json.loads(path.read_text(encoding='utf-8-sig'))
    if profile['id']!=ident or set(profile['views'])!=DIRECTIONS or profile['missingDirections']:
        raise ValueError('Cannot bundle incomplete or mismatched directions')
    recipe=(ROOT/profile['recipe']).resolve()
    if not recipe.is_relative_to(ROOT) or sha(recipe)!=profile['recipeSHA256']:raise ValueError('Recipe changed since the atlas build')
    paths=[path,recipe,public/'assets/atlas'/ident/'portrait.png',runtime/'assets/Rajdhani-Medium.ttf',runtime/'style.css',runtime/'index.html']
    # ASTER's current runtime family is a single full-body texture per frame.
    # Keep the old split fire manifest out of the standalone package; it is a
    # quarantined diagnostic candidate and must not be silently re-promoted.
    motion_manifest_path=public/'assets/atlas'/ident/'coherent'/'manifest.json'
    if not motion_manifest_path.exists():
        motion_manifest_path=public/'assets/atlas'/ident/'fire'/'manifest.json'
    if motion_manifest_path.exists() and profile.get('animation',{}).get('presentation')!='authored_frames':
        motion_manifest=json.loads(motion_manifest_path.read_text(encoding='utf-8-sig'))
        paths.append(motion_manifest_path)
        for entry in motion_manifest.get('directions',{}).values():
            for key in ('idle','walk','run','move','fire','upper','idleLower','moveLower'):
                value=entry.get(key)
                if value:paths.append((public/value).resolve())
    paths.extend(runtime/name for name in RUNTIME_FILES)
    for view in profile['views'].values():
        if 'walk' not in view:raise ValueError('Every direction needs an authored walk clip')
        for action in ['walk','run','idle']:
            if action not in view:continue
            clip=view[action]
            if clip['frames']<1 or len(clip['sources'])!=clip['frames'] or len(clip['muzzles'])!=clip['frames']:
                raise ValueError('Incomplete clip metadata')
            paths.append((public/clip['image']).resolve())
    if any(not path.resolve().is_relative_to(ROOT) for path in paths):raise ValueError('Bundle input escaped the lab')
    return {path.relative_to(ROOT).as_posix():sha(path) for path in paths}

def data_uri(path,mime):return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def require_whole_body_runtime(html):
    """Refuse to publish the retired per-limb mesh preview as a character page.

    The old ``renderer.js`` warped legs against a moving root and could make a
    valid six-frame atlas look like it was skating.  A packaged Motion Studio
    page must always use the shared whole-body AtlasRenderer instead.
    """
    missing=[marker for marker in REQUIRED_ATLAS_MARKERS if marker not in html]
    retired=[marker for marker in RETIRED_MESH_MARKERS if marker in html]
    if missing or retired:
        details=[]
        if missing:details.append('missing '+', '.join(missing))
        if retired:details.append('contains retired '+', '.join(retired))
        raise ValueError('Standalone runtime must use whole-body atlas: '+'; '.join(details))

def embedded_fire_bundle(public,ident):
    profile=json.loads((public/'assets/atlas'/ident/'profile.json').read_text(encoding='utf-8-sig'))
    if profile.get('animation',{}).get('presentation')=='authored_frames':return None
    manifest_path=public/'assets/atlas'/ident/'coherent'/'manifest.json'
    if not manifest_path.exists():
        manifest_path=public/'assets/atlas'/ident/'fire'/'manifest.json'
    if not manifest_path.exists():return None
    bundle=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    for entry in bundle.get('directions',{}).values():
        for key in ('idle','walk','run','move','fire','upper','idleLower','moveLower'):
            value=entry.get(key)
            if not value:continue
            source=(public/value).resolve()
            if not source.is_relative_to(ROOT):raise ValueError('Fire bundle input escaped the lab')
            mime='image/png' if source.suffix.lower()=='.png' else 'image/webp'
            entry[key]=data_uri(source,mime)
    return bundle

def package(ident,activate_preview=False,atlas_public=None,runtime_public=None,output_dir=None,preview_dir=ROOT/'public'/'standalone'):
    atlas_public=(atlas_public or ROOT/'public').resolve()
    runtime_public=(runtime_public or ROOT/'public').resolve()
    if activate_preview and atlas_public!=(ROOT/'public').resolve():
        raise ValueError('Candidate atlas cannot activate the live preview pointer')
    inputs=bundle_inputs(ident,atlas_public=atlas_public,runtime_public=runtime_public)
    build={'character':ident,'inputs':inputs,'inputSHA256':hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()}
    public=atlas_public;runtime=runtime_public
    profile=json.loads((public/'assets/atlas'/ident/'profile.json').read_text())
    fire_bundle=embedded_fire_bundle(public,ident)
    if profile['missingDirections']:raise ValueError('Cannot bundle incomplete directions')
    for view in profile['views'].values():
        for action in ['walk','run','idle']:
            if action in view:view[action]['image']=data_uri(public/view[action]['image'],'image/webp')
    css=(runtime/'style.css').read_text(encoding='utf-8-sig')
    css=css.replace("assets/Rajdhani-Medium.ttf",data_uri(runtime/'assets/Rajdhani-Medium.ttf','font/ttf'))
    # The portrait also comes from the selected package, including on file://.
    css=re.sub(r"url\('assets/mica/S\.png'\)",'none',css)
    sources=[]
    for filename in RUNTIME_FILES:
        script=(runtime/filename).read_text(encoding='utf-8-sig')
        script=re.sub(r'^import .*?;\s*','',script,flags=re.MULTILINE).replace('export class ','class ').replace('export function ','function ').replace('export const ','const ')
        sources.append(script)
    payload='window.__MOTION_BUILD__='+json.dumps(build,separators=(',',':'))+';\n'
    payload+='window.__MOTION_PROFILE__='+json.dumps(profile,separators=(',',':'))+';\n'
    payload+='window.__MOTION_PORTRAIT__='+json.dumps(data_uri(public/'assets/atlas'/ident/'portrait.png','image/png'))+';\n'
    if fire_bundle is not None:payload+='window.__MOTION_FIRE_BUNDLE__='+json.dumps(fire_bundle,separators=(',',':'))+';\n'
    payload+='(async()=>{\n'+'\n'.join(sources)+'\n})().catch(error=>{const e=document.querySelector("#loading");if(e)e.textContent="실행 오류: "+error.message;console.error(error);});'
    html=(runtime/'index.html').read_text(encoding='utf-8-sig')
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
    html=html.replace('<script type="module" src="studio.js"></script>','<script>'+payload.replace('</script','<\\/script')+'</script>')
    html=html.replace('href="./"','href="#"')
    require_whole_body_runtime(html)
    out=(output_dir or ROOT/'dist').resolve()
    if not out.is_relative_to(ROOT):raise ValueError('Package output escaped the lab')
    out.mkdir(parents=True,exist_ok=True);destination=out/(ident.upper()+'_Motion_Studio.html')
    if destination.exists() and destination.read_text(encoding='utf-8')!=html:
        history=ROOT/'qa/package_history'/ident;history.mkdir(parents=True,exist_ok=True)
        previous=history/(sha(destination)+'.html')
        if not previous.exists():previous.write_bytes(destination.read_bytes())
    destination.write_text(html,encoding='utf-8')
    if preview_dir is not None:
        preview=Path(preview_dir).resolve()
        if not preview.is_relative_to(ROOT):raise ValueError('Preview output escaped the lab')
        preview.mkdir(parents=True,exist_ok=True)
        (preview/f'{ident}.html').write_text(html,encoding='utf-8')
    report={'path':destination.relative_to(ROOT).as_posix(),'bytes':destination.stat().st_size,'sha256':sha(destination),'networkDependencies':0,**build}
    (out/f'{ident}.package.json').write_text(json.dumps(report,indent=2))
    if activate_preview:
        (public/'standalone.html').write_text(html,encoding='utf-8')
        (out/'package.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='inputs'}))
    return destination

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',default='mica');p.add_argument('--activate-preview',action='store_true');p.add_argument('--candidate-stage',help='Read atlas/profile from an isolated build-candidate directory under the lab');p.add_argument('--output-dir',help='Package output directory, kept under the lab');a=p.parse_args()
    stage=Path(a.candidate_stage).resolve() if a.candidate_stage else None
    if stage is not None:
        if not stage.is_relative_to(ROOT) or not (stage/'public').is_dir():raise ValueError('Candidate stage must be project-local and contain public/')
    package(a.character,a.activate_preview,atlas_public=(stage/'public' if stage else None),output_dir=(Path(a.output_dir) if a.output_dir else None),preview_dir=None if stage else ROOT/'public'/'standalone')
