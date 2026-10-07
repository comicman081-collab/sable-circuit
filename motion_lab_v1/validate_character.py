"""Check packaging, alpha, anchors, provenance and texture limits. Not an art judge."""
import argparse,json,hashlib,re
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']

def validate(ident,output=None):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):raise ValueError('Invalid character id')
    public=ROOT/'public';path=public/'assets/atlas'/ident/'profile.json';p=json.loads(path.read_text());errors=[];rows=[]
    recipe=(ROOT/p['recipe']).resolve()
    if p['id']!=ident or not recipe.is_relative_to(ROOT) or not recipe.exists() or hashlib.sha256(recipe.read_bytes()).hexdigest()!=p['recipeSHA256']:errors.append('Recipe identity or hash changed since build')
    if set(p['views'])!=set(DIRECTIONS) or p['missingDirections']:errors.append('All eight directions are required')
    for direction,view in p['views'].items():
      for action in ['walk','run','idle']:
        if action not in view:continue
        clip=view[action];atlas_path=(public/clip['image']).resolve()
        starts=clip.get('phaseStarts')
        if starts is not None and (not isinstance(starts,list) or len(starts)!=clip['frames'] or starts[0]!=0 or any(not isinstance(value,(int,float)) or isinstance(value,bool) or not 0<=value<1 for value in starts) or any(current<=previous for previous,current in zip(starts,starts[1:]))):errors.append(f'{direction}/{action}: invalid phase starts')
        if not atlas_path.is_relative_to(ROOT) or not atlas_path.exists():errors.append('Missing/project-external atlas');continue
        atlas=Image.open(atlas_path).convert('RGBA');w,h=clip['cell'];hashes=[]
        if max(atlas.size)>4096:errors.append(f'{direction}/{action}: texture exceeds 4096')
        if len(clip['sources'])!=clip['frames'] or len(clip['muzzles'])!=clip['frames']:errors.append('Frame metadata length mismatch')
        for i,source in enumerate(clip['sources']):
            file=(ROOT/source['source']).resolve()
            if not file.is_relative_to(ROOT) or not file.exists():errors.append('Missing/project-external source');continue
            if hashlib.sha256(file.read_bytes()).hexdigest()!=source['sha256']:errors.append('Source changed since build')
            if source['scale']>1.001:errors.append(f'{direction}/{action}/{i}: original art was upscaled')
            cell=np.array(atlas.crop((i%clip['columns']*w,i//clip['columns']*h,i%clip['columns']*w+w,i//clip['columns']*h+h)))
            opaque=cell[:,:,3]>200;ys,xs=np.where(opaque)
            if len(xs)<3000:errors.append(f'{direction}/{action}/{i}: invisible character');continue
            if xs.min()<3 or xs.max()>w-4 or ys.min()<3 or ys.max()>h-4:errors.append(f'{direction}/{action}/{i}: clipped artwork')
            green=(cell[:,:,1].astype(int)-np.maximum(cell[:,:,0],cell[:,:,2]).astype(int)>45)&opaque
            if green.any():errors.append(f'{direction}/{action}/{i}: opaque chroma residue')
            mx,my=clip['muzzles'][i];ix,iy=round(mx),round(my)
            if not(3<=ix<w-3 and 3<=iy<h-3) or not np.any(opaque[max(0,iy-6):iy+7,max(0,ix-6):ix+7]):errors.append(f'{direction}/{action}/{i}: muzzle outside artwork')
            hashes.append(hashlib.sha256(cell.tobytes()).hexdigest())
        if len(set(hashes))<clip['frames']:errors.append(f'{direction}/{action}: duplicate frame pixels')
        rows.append({'direction':direction,'action':action,'frames':clip['frames'],'texture':list(atlas.size),'uniqueFrames':len(set(hashes))})
    report={'character':ident,'status':'PASS_TECHNICAL' if not errors else 'FAIL','errors':errors,'clips':rows,'scope':'Asset loading/alpha/bounds/source hashes; does not certify gait anatomy or artwork continuity.'}
    out=(output or ROOT/'qa'/ident/'asset_validation.json').resolve()
    if not out.is_relative_to(ROOT):raise ValueError('Validation output must be lab-local')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(json.dumps(report))
    return not errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',default='mica');a=p.parse_args();raise SystemExit(0 if validate(a.character) else 1)
