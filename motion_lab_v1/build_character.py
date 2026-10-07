"""Compile a character from a JSON recipe, without changing runtime code."""
from pathlib import Path
import argparse,json,uuid
from PIL import Image
from build_atlas import build,ROOT,DIRECTIONS,subjects,sha

def phase_starts(spec,count):
    """Validate and retain optional authored frame timing in atlas metadata."""
    starts=spec.get('phaseStarts')
    if starts is None:return None
    if (not isinstance(starts,list) or len(starts)!=count or starts[0]!=0 or
        any(not isinstance(value,(int,float)) or isinstance(value,bool) for value in starts) or
        any(not 0<=value<1 for value in starts) or
        any(current<=previous for previous,current in zip(starts,starts[1:]))):
        raise ValueError('phaseStarts must begin at 0 and contain one increasing phase start per frame')
    return starts

def compile_character(config_path,partial=False):
    config=json.loads(config_path.read_text(encoding='utf-8-sig'))
    ident=config['id']
    if not ident or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in ident):
        raise ValueError('id must contain lowercase ASCII letters, digits, _ or -')
    canonical=ROOT/'characters'/f'{ident}.json'
    canonical_modern=canonical.is_file() and json.loads(canonical.read_text(encoding='utf-8-sig')).get('workflowVersion')==1
    if (config.get('workflowVersion')==1 or canonical_modern) and not partial:
        if config_path.resolve()!=canonical.resolve():
            raise ValueError('Active build must use the exact canonical reviewed character recipe; use --partial for alternate diagnostics')
        from cycle_review import require_build
        require_build(ident)
    folder=(ROOT/config['source']).resolve()
    if not folder.is_relative_to(ROOT):raise ValueError('Source must be project-local')
    stage=ROOT/'qa/build_candidates'/ident/uuid.uuid4().hex
    derived=stage/'derived'/ident;derived.mkdir(parents=True,exist_ok=True)
    views={};missing=[];provenance=[]
    for d in DIRECTIONS:
        views[d]={}
        for action,spec in config.get('clips',{'walk':{'frames':6}}).items():
            count=spec['frames'];paths=[None]*count
            for pair in range(count//2):
                source=folder/f'{d}_{action}_pair{pair}.png'
                if not source.exists():continue
                for side,(image,box) in enumerate(subjects(source,2)):
                    i=pair+side*(count//2);path=derived/f'{d}_{action}_{i}.png';image.save(path);paths[i]=path
                    provenance.append({'master':str(source.relative_to(ROOT)),'sha256':sha(source),'native':list(Image.open(source).size),'subjectBox':box,'frame':str(path.relative_to(ROOT))})
            for i in range(count):
                override=folder/f'{d}_{action}_{i}_override.png'
                single=folder/f'{d}_{action}_{i}_master.png'
                if override.exists():paths[i]=override
                elif single.exists():paths[i]=single
            if any(p is None for p in paths):missing.append(d+'/'+action);continue
            annotations=config.get('annotations',{}).get(d,{}).get(action,{})
            record=build(config,d,action,paths,annotations,output_root=stage)
            starts=phase_starts(spec,count)
            if starts is not None:record['phaseStarts']=starts
            views[d][action]=record
        if not views[d]:del views[d]
    if missing and not partial:raise SystemExit('Missing authored frames: '+', '.join(missing))
    profile={k:config[k] for k in ['id','name','heightMetres','radius','locomotion','weapon']}
    profile.update({'schema':3,'appearance':'Codex ImageGen','motionReference':'Blender / Quaternius UAL1',
        'directions':DIRECTIONS,'availableDirections':list(views),'missingDirections':missing,'views':views,
        'animation':{'kind':'authored_keyframes','presentation':'authored_frames','separateRunArt':all('run' in v for v in views.values()),'interpolation':'none'},
        'recipe':str(config_path.relative_to(ROOT)),'recipeSHA256':sha(config_path)})
    out=stage/'public/assets/atlas'/ident
    out.mkdir(parents=True,exist_ok=True)
    (out/'profile.json').write_text(json.dumps(profile,indent=2),encoding='utf-8')
    (derived/'source_provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    # Single-frame imports never create derived/S_walk_0.png. Build a portrait
    # from the compiled selected character, not a leftover MICA derivative.
    front=views.get('S',{}).get('idle') or views.get('S',{}).get('walk')
    if front:
        portrait=Image.open(stage/'public'/front['image']).convert('RGBA').crop((0,0,*front['cell']))
        portrait.thumbnail((512,512));portrait.save(out/'portrait.png')
    if partial:
        print(json.dumps({'profile':str(out/'profile.json'),'candidateOnly':True,'missing':missing}),flush=True)
        return profile
    # No incomplete or failed atlas replaces the existing character folder.
    # Preserve the prior package, then swap the complete staged folder with a
    # rollback if the final rename fails. No source or failed candidate deletion.
    destination=ROOT/'public/assets/atlas'/ident
    previous=ROOT/'qa/build_previous'/ident/stage.name
    if not destination.resolve().is_relative_to(ROOT/'public/assets/atlas') or not previous.resolve().is_relative_to(ROOT/'qa/build_previous'):
        raise ValueError('Build activation escaped its scoped character folders')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():previous.parent.mkdir(parents=True,exist_ok=True);destination.rename(previous)
    try:out.rename(destination)
    except OSError:
        if previous.exists():previous.rename(destination)
        raise
    print(json.dumps({'profile':str(destination/'profile.json'),'reviewPreviews':str(stage/'reference/atlas'/ident),'ready':list(views),'missing':missing}),flush=True)
    return profile

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'characters/mica.json');p.add_argument('--partial',action='store_true');a=p.parse_args()
    compile_character(a.config.resolve(),a.partial)
