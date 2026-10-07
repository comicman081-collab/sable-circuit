"""Split ownership masks losslessly. No painting, generation, or resized sources."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, numpy as np, hashlib

ROOT=Path(__file__).resolve().parent
def segment_distance(xx,yy,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/(dx*dx+dy*dy+1e-12),0,1)
    return (xx-a[0]-t*dx)**2+(yy-a[1]-t*dy)**2

def prepare(profile_path):
    profile=json.loads(profile_path.read_text(encoding='utf-8'))
    evidence={}
    for direction,v in profile['views'].items():
        image=ROOT/'public'/v['image'];rgba=np.asarray(Image.open(image).convert('RGBA'))
        h,w=rgba.shape[:2];yy,xx=np.indices((h,w));owner=np.zeros((h,w),np.uint8)
        distances=[]
        for i in range(2):
            chain=[v['hips'][i],v['knees'][i],v['ankles'][i],v['soles'][i]]
            distances.append(np.minimum.reduce([segment_distance(xx,yy,a,b) for a,b in zip(chain,chain[1:])]))
        lower=yy>v['waistY']+v['height']*.035
        owner[lower]=np.where(distances[0][lower]<distances[1][lower],2,3)
        coat=Image.new('L',(w,h));dr=ImageDraw.Draw(coat)
        for poly in v['coatPolygons']:dr.polygon([tuple(p) for p in poly],fill=255)
        owner[(np.asarray(coat)>0)&lower]=1
        # The rifle can cross below the pelvis; its complete tip remains on the upper rig.
        mx,my=v['muzzle'];weapon=(xx-mx)**2+(yy-my)**2<(v['height']*.07)**2
        owner[weapon]=0
        outputs=[];reconstructed=np.zeros_like(rgba);counts={}
        for n in range(4):
            mask=owner==n;layer=np.zeros_like(rgba);layer[mask]=rgba[mask]
            output=image.with_name(f'{direction}_layer{n}.png');Image.fromarray(layer).save(output)
            reconstructed[mask]=layer[mask];outputs.append(output.relative_to(ROOT/'public').as_posix())
            counts[n]=int(np.count_nonzero(layer[...,3]))
        assert np.array_equal(reconstructed,rgba)
        v['layers']=outputs
        evidence[direction]={'nativeSize':[w,h],'sourceSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'exactSourceReconstruction':True,'visiblePixelsByLayer':counts}
    profile_path.write_text(json.dumps(profile,indent=2),encoding='utf-8')
    (ROOT/'reference'/'layer_pixel_evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':prepare(ROOT/'public/assets/mica/profile.json')
