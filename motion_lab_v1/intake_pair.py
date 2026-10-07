"""Import a real ImageGen opposite-pose pair, preserving the native RGBA master.

Deterministic subject separation only: no resynthesis, limb warp, resizing or
upscaling. The exact generated pair and tool metadata remain the provenance.
"""
import argparse,json,hashlib,shutil,datetime
from pathlib import Path
from PIL import Image
from build_atlas import subjects
from character_workflow import ROOT,recipe,local,binding,write,sha,DIRECTIONS

def intake(character,direction,action,pair,generated,tool_response,side_filter=None):
    c=recipe(character);count=c['clips'][action]['frames']
    if c.get('workflowVersion')!=1:raise ValueError('Explicit source migration required before historical source replacement')
    if direction not in DIRECTIONS or count!=6 or not 0<=pair<3:raise ValueError('Use an existing six-frame recipe and pair 0/1/2')
    from cycle_review import require_pilot
    require_pilot(character,direction,action)
    proof=local(tool_response);generated=Path(generated).resolve()
    from source_provenance import response_master
    original=response_master(ROOT,proof)
    if sha(original)!=sha(generated):raise ValueError('Pair input differs from preserved returned master')
    from source_alpha_policy import inspect_master
    inspect_master(original)
    with Image.open(generated) as im:
        native=list(im.size)
        if min(native)<1024 or max(native)<1536:raise ValueError('Pair must be native 1536x1024 or larger')
    digest=sha(generated);masters=ROOT/'art'/character/'gait_v8'/'native_pairs';masters.mkdir(parents=True,exist_ok=True)
    master=masters/f'{direction}_{action}_pair{pair}_{digest[:12]}.png'
    if not master.exists():shutil.copy2(generated,master)
    if sha(master)!=digest:raise ValueError('Master copy hash mismatch')
    extracted=[(side,im,box) for side,(im,box) in enumerate(subjects(master,2)) if side_filter is None or side==side_filter]
    if not extracted or any(im.height<800 for _,im,_ in extracted):raise ValueError('Subject is too small for the current 656px atlas; request a native pair')
    # Validate every selected half before the first active-slot write.
    rows=[]
    for side,im,box in extracted:
        # Kept at original pixel density. A native image is not upscaled to
        # pretend that a low-resolution sheet cell was a high-resolution source.
        if im.height<800:raise ValueError('Subject is too small for the current 656px atlas; request a native pair')
        index=pair+side*3;folder=local(c['source']);target=folder/f'{direction}_{action}_{index}_master.png'
        override=folder/f'{direction}_{action}_{index}_override.png'
        if override.exists():target=override
        if target.exists():
            previous=ROOT/'qa'/character/'quarantine'/sha(target);previous.mkdir(parents=True,exist_ok=True)
            for old in [target,target.with_suffix('.source.json')]:
                if old.exists() and not (previous/old.name).exists():shutil.copy2(old,previous/old.name)
        im.save(target)
        receipt={'generator':'Codex built-in ImageGen','importedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'sha256':sha(target),'native':list(im.size),'destination':target.relative_to(ROOT).as_posix(),
                 'toolResponse':binding(proof),'sourceMaster':binding(master),'masterNative':native,
                 'derivation':{'kind':'chroma-key and connected-subject crop only','box':box,'resampling':False,'anatomicalWarp':False}}
        write(target.with_suffix('.source.json'),receipt);rows.append(receipt)
    from character_workflow import invalidate_delivery
    invalidate_delivery(character,'Source or provenance changed: '+direction+'/'+action+'/pair'+str(pair))
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',default='walk');p.add_argument('--pair',type=int,required=True);p.add_argument('--generated',required=True);p.add_argument('--tool-response',required=True)
    p.add_argument('--side',type=int,choices=[0,1],help='Import only an actually reviewed half; a failed partner is not promoted')
    a=p.parse_args();print(json.dumps(intake(a.character,a.direction,a.action,a.pair,a.generated,a.tool_response,a.side),ensure_ascii=False))
