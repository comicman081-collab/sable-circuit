"""Copy an actual selected ImageGen output into its recipe slot, preserving source."""
from pathlib import Path
import argparse,json,hashlib,shutil,datetime,re
from PIL import Image
ROOT=Path(__file__).resolve().parent

def intake(ident,direction,action,frame,source,tool_response=None):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):raise ValueError('Invalid character id')
    config=json.loads((ROOT/'characters'/f'{ident}.json').read_text(encoding='utf-8-sig'))
    if direction not in ['E','SE','S','SW','W','NW','N','NE'] or action not in config['clips'] or not 0<=frame<config['clips'][action]['frames']:raise ValueError('Invalid recipe slot')
    from cycle_review import require_pilot
    require_pilot(ident,direction,action)
    with Image.open(source) as image:
        native=list(image.size)
        image.verify()
    if max(native)<1024:raise ValueError('A native high-resolution original is required')
    folder=(ROOT/config['source']).resolve()
    if folder!=ROOT/'art'/ident:raise ValueError('Source folder must be art/CHARACTER')
    if config.get('workflowVersion')!=1:raise ValueError('Explicit source migration is required before replacing historical sources')
    if tool_response is None:raise ValueError('Supply --tool-response with the actual saved ImageGen tool response')
    proof=None
    if tool_response is not None:
        tool_response=tool_response.resolve()
        if not tool_response.is_relative_to(ROOT):raise ValueError('Copy the tool response into this lab first')
        from source_provenance import response_master,digest
        master=response_master(ROOT,tool_response)
        if digest(source)!=digest(master):raise ValueError('Input differs from the preserved returned master')
        proof={'path':tool_response.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(tool_response.read_bytes()).hexdigest()}
    from source_alpha_policy import inspect_master
    inspect_master(master)
    target=folder/f'{direction}_{action}_{frame}_master.png'
    override=folder/f'{direction}_{action}_{frame}_override.png'
    if override.exists():target=override
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()==digest and target.with_suffix('.source.json').exists():
            current=json.loads(target.with_suffix('.source.json').read_text(encoding='utf-8-sig'))
            from source_provenance import validate_slot
            try:
                validate_slot(ROOT,target,current)
                if current.get('toolResponse')==proof:return target
            except (ValueError,KeyError,TypeError,OSError):pass
        history=folder/'previous';history.mkdir(exist_ok=True);old=hashlib.sha256(target.read_bytes()).hexdigest()[:12];shutil.copy2(target,history/(target.stem+'_'+old+target.suffix))
        previous_receipt=target.with_suffix('.source.json')
        if previous_receipt.exists():shutil.copy2(previous_receipt,history/(target.stem+'_'+old+'.source.json'))
    if source.resolve()!=target:shutil.copy2(source,target)
    receipt={'generator':'Codex built-in ImageGen','importedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source.resolve()),'native':native,'sha256':digest,'destination':target.relative_to(ROOT).as_posix(),'sourceMaster':{'path':master.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(master.read_bytes()).hexdigest()}}
    if proof:receipt['toolResponse']=proof
    target.with_suffix('.source.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
    from character_workflow import invalidate_delivery
    invalidate_delivery(ident,'Source or provenance changed: '+direction+'/'+action+'/'+str(frame))
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--generated',type=Path,required=True);p.add_argument('--tool-response',type=Path);a=p.parse_args();intake(a.character,a.direction,a.action,a.frame,a.generated,a.tool_response)
