"""Apply inspector-exported muzzle coordinates to a source recipe, then rebuild."""
from pathlib import Path
import argparse,json,math
ROOT=Path(__file__).resolve().parent

def apply(path):
    edited=json.loads(path.read_text(encoding='utf-8-sig'));ident=edited['id']
    if not ident or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in ident):raise ValueError('Invalid id')
    recipe=ROOT/'characters'/f'{ident}.json';config=json.loads(recipe.read_text(encoding='utf-8-sig'))
    current=json.loads((ROOT/'public/assets/atlas'/ident/'profile.json').read_text());count=0
    for d,view in current['views'].items():
      for action,clip in view.items():
        if action not in ['walk','idle','run']:continue
        other=edited['views'][d][action]
        if len(other['muzzles'])!=clip['frames']:raise ValueError('Frame count mismatch')
        for i,(point,source) in enumerate(zip(other['muzzles'],clip['sources'])):
            if other['sources'][i]['sha256']!=source['sha256']:raise ValueError('Source changed; export the current profile again')
            x,y=point
            if not all(math.isfinite(v) for v in point) or not(0<=x<clip['cell'][0] and 0<=y<clip['cell'][1]):raise ValueError('Invalid muzzle coordinate')
            m=source['matrix'];a,b,tx=m[0];c,e,ty=m[1];det=a*e-b*c
            original=[(e*(x-tx)-b*(y-ty))/det,(-c*(x-tx)+a*(y-ty))/det]
            config.setdefault('annotations',{}).setdefault(d,{}).setdefault(action,{}).setdefault(str(i),{})['muzzle']=original;count+=1
    recipe.write_text(json.dumps(config,indent=2),encoding='utf-8');print(json.dumps({'recipe':str(recipe),'muzzles':count}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);a=p.parse_args();apply(a.profile)
