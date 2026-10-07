"""Scaffold a character recipe and explicit ImageGen shot list. No API calls."""
from pathlib import Path
import argparse,json,shutil,hashlib
from gait_contract import PHASES as GAIT_PHASES, WALK_PHASE_STARTS, digest as contract_digest
from source_alpha_policy import (PROMPT as ALPHA_PROMPT,
                                 requirement as alpha_requirement,
                                 require_project_reference)
ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']
VIEWS=['right side','front-right three-quarter','straight front','front-left three-quarter','left side','back-left three-quarter','straight back','back-right three-quarter']
PHASES=[p['prompt'] for p in GAIT_PHASES]

def scaffold(ident,name,reference,run_art=False):
    if not ident or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in ident):raise ValueError('Use an ASCII character id')
    from enemy_body_plan import require_biped_authoring
    require_biped_authoring(ident)
    recipe=ROOT/'characters'/f'{ident}.json'
    if recipe.exists():raise FileExistsError(f'Recipe already exists: {recipe}')
    reference=require_project_reference(reference, 'identity reference', ROOT.parent)
    folder=ROOT/'art'/ident
    if folder.exists() and any(folder.iterdir()):raise FileExistsError(f'Art folder is not empty: {folder}')
    folder.mkdir(parents=True,exist_ok=True)
    copy=folder/('identity_reference'+reference.suffix.lower());shutil.copy2(reference,copy)
    config=json.loads((ROOT/'characters/mica.json').read_text(encoding='utf-8-sig'))
    config.update({'id':ident,'name':name,'source':folder.relative_to(ROOT).as_posix(),'annotations':{}})
    config.update({'workflowVersion':1,'identityReference':copy.relative_to(ROOT).as_posix(),'referenceSHA256':hashlib.sha256(copy.read_bytes()).hexdigest()})
    config['clips']={'walk':{'frames':6,'phaseStarts':list(WALK_PHASE_STARTS)},'idle':{'frames':1}}
    config['gaitContractSHA256']=contract_digest()
    if run_art:config['clips']['run']={'frames':6}
    recipe.write_text(json.dumps(config,indent=2),encoding='utf-8')
    requests=[]
    for d,view in zip(DIRECTIONS,VIEWS):
      for action,spec in config['clips'].items():
        for frame in range(spec['frames']):
            phase='stationary, both soles planted, relaxed two-handed weapon aim' if action=='idle' else PHASES[frame]
            guide=None if action=='idle' else f'reference/ual_guides/{d}_{"Jog_Fwd_Loop" if action=="run" else "Walk_Loop"}_{frame}.png'
            request={'direction':d,'action':action,'frame':frame,'reference':copy.relative_to(ROOT).as_posix(),'poseGuide':guide,
                'gaitContractSHA256':contract_digest(), 'phaseName':None if action=='idle' else GAIT_PHASES[frame]['name'],
                'destination':f'art/{ident}/{d}_{action}_{frame}_master.png','state':'NEEDS_IMAGEGEN',
                'background':'transparent_alpha',
                'sourceArtPolicy':alpha_requirement(),
                'prompt':f'One native high-resolution complete character frame. Exact supplied identity and costume. Camera: {view}. Motion: {action}; {phase}. Use Blender guide for pose, original reference for appearance. Two connected anatomical legs. Stable rifle/face scale. Entire weapon, hair and both boots inside canvas with generous margins. At least 1300px tall subject. Use Codex built-in ImageGen only. '+ALPHA_PROMPT}
            from source_alpha_policy import validate_request_references
            # Request paths are motion_lab-relative; keep all inputs inside
            # this lab while the scaffold is assembled.
            validate_request_references(request, ROOT)
            requests.append(request)
    (folder/'requests.json').write_text(json.dumps(requests,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'recipe':str(recipe),'requests':len(requests),'art':str(folder)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--name',required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--run-art',action='store_true');a=p.parse_args();scaffold(a.id,a.name,a.reference,a.run_art)
