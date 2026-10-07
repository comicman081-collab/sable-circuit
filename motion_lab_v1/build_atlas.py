"""Deterministic, model-free RGBA/atlas compiler for authored ImageGen frames."""
from pathlib import Path
import json,hashlib
import numpy as np
import cv2
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def key_image(path):
    im=Image.open(path)
    if im.mode=='RGBA' and im.getextrema()[3][0]<255:
        rgba=np.array(im);rgba[rgba[:,:,3]==0,:3]=0
        return rgba
    rgb=np.array(im.convert('RGB'));f=rgb.astype(np.float32)
    excess=f[:,:,1]-np.maximum(f[:,:,0],f[:,:,2])
    alpha=np.clip(1-(excess-8)/38,0,1)
    alpha[(excess>65)&(f[:,:,1]>85)]=0
    f[:,:,1]=np.where(alpha<.98,np.minimum(f[:,:,1],np.maximum(f[:,:,0],f[:,:,2])+4),f[:,:,1])
    f[alpha==0]=0
    return np.dstack((f,alpha*255)).astype(np.uint8)

def subjects(path,count):
    """Separate complete figures even when a rifle crosses a sheet-cell border."""
    rgba=key_image(path)
    n,labels,stats,_=cv2.connectedComponentsWithStats((rgba[:,:,3]>30).astype(np.uint8))
    components=sorted(range(1,n),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]),reverse=True)[:count]
    if len(components)!=count or min(stats[i,cv2.CC_STAT_AREA] for i in components)<10000:
        raise ValueError(f'{path}: expected {count} separate complete figures')
    components.sort(key=lambda i:int(stats[i,cv2.CC_STAT_LEFT]))
    result=[]
    for i in components:
        x,y,w,h,area=map(int,stats[i]);mask=(labels==i).astype(np.uint8)
        mask=cv2.dilate(mask,np.ones((3,3),np.uint8))
        separated=rgba.copy();separated[mask==0]=0
        box=[max(0,x-12),max(0,y-12),min(rgba.shape[1],x+w+12),min(rgba.shape[0],y+h+12)]
        result.append((Image.fromarray(separated[box[1]:box[3],box[0]:box[2]]),box))
    return result

def register(path,config,direction,annotation):
    raw=key_image(path);ys,xs=np.where(raw[:,:,3]>200)
    if not len(xs):raise ValueError(f'{path}: no opaque subject')
    x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    scale=height/(y1-y0)
    anchor=annotation.get('hipX')
    if anchor is None:
        region=raw[int(y0+(y1-y0)*.39):int(y0+(y1-y0)*.47),:,3]
        valid=np.where((region>200).sum(axis=0)>region.shape[0]*.7)[0]
        anchor=float(np.median(valid))
    matrix=np.float32([[scale,0,root[0]-anchor*scale],[0,scale,root[1]-y1*scale]])
    corners=np.array([[x0,y0,1],[x1,y1,1]])@matrix.T
    if np.any(corners[0]<4) or corners[1,0]>cell[0]-4 or corners[1,1]>cell[1]-4:
        raise ValueError(f'{path}: cell too small / hip anchor invalid; bounds={corners.tolist()}')
    out=cv2.warpAffine(raw,matrix,tuple(cell),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
    if 'muzzle' in annotation:
        muzzle=(matrix@np.array([*annotation['muzzle'],1])).tolist()
    else:
        band=raw[y0:int(y0+(y1-y0)*.45),:,3];yy,xx=np.where(band>210);yy+=y0
        if direction in ['W','SW','NW']:
            edge=xx.min();choose=xx<=edge+3
        elif direction=='N':
            edge=yy.min();choose=yy<=edge+3
        elif direction=='S':
            choose=np.zeros_like(xx,dtype=bool)
            choose[np.argmin(abs(xx-anchor)+abs(yy-(y0+(y1-y0)*.32)))]=True
        else:
            edge=xx.max();choose=xx>=edge-3
        muzzle=(matrix@np.array([float(np.median(xx[choose])),float(np.median(yy[choose])),1])).tolist()
    green=(out[:,:,1].astype(int)-np.maximum(out[:,:,0],out[:,:,2]).astype(int)>45)&(out[:,:,3]>128)
    with Image.open(path) as native_image:native_size=list(native_image.size)
    note={'source':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'native':native_size,
          'bounds':[x0,y0,x1,y1],'hipX':anchor,'scale':scale,'matrix':matrix.tolist(),'muzzle':muzzle,
          'opaqueGreenPixels':int(green.sum()),'alphaBounds':corners.tolist()}
    return out,note

def build(config,direction,action,paths,annotations,output_root=None):
    output_root=output_root or ROOT
    ident=config['id'];out=output_root/'public/assets/atlas'/ident;out.mkdir(parents=True,exist_ok=True)
    pairs=[register(path,config,direction,annotations.get(str(i),{})) for i,path in enumerate(paths)]
    frames=[p[0] for p in pairs];notes=[p[1] for p in pairs]
    cell=config.get('cell',[768,768]);root=config.get('root',[384,716]);height=config.get('spriteHeight',656)
    cols=min(3,len(frames));rows=(len(frames)+cols-1)//cols;atlas=Image.new('RGBA',(cell[0]*cols,cell[1]*rows))
    for i,im in enumerate(frames):atlas.paste(Image.fromarray(im),(i%cols*cell[0],i//cols*cell[1]))
    atlas.save(out/f'{direction}_{action}.webp',lossless=True,method=5)
    preview=output_root/'reference/atlas'/ident;preview.mkdir(parents=True,exist_ok=True)
    contact=Image.new('RGB',atlas.size,(18,28,36));contact.paste(atlas,(0,0),atlas);draw=ImageDraw.Draw(contact)
    for i in range(len(frames)):
        ox=i%cols*cell[0];oy=i//cols*cell[1]
        draw.text((ox+20,oy+20),f'{direction} / {action} / {i}',fill='#b0dacc')
        draw.line((ox+20,oy+root[1],ox+cell[0]-20,oy+root[1]),fill='#35534f')
        m=notes[i]['muzzle'];draw.ellipse((ox+m[0]-4,oy+m[1]-4,ox+m[0]+4,oy+m[1]+4),outline='#ffcc70',width=2)
    contact.save(preview/f'{direction}_{action}_keyframes.png')
    anim=[]
    for im in frames:
        bg=Image.new('RGB',tuple(cell),(18,28,36));bg.paste(Image.fromarray(im),(0,0),Image.fromarray(im[:,:,3]));anim.append(bg)
    anim[0].save(preview/f'{direction}_{action}.gif',save_all=True,append_images=anim[1:],duration=round(1200/len(frames)),loop=0)
    record={'image':f'assets/atlas/{ident}/{direction}_{action}.webp','cell':cell,'columns':cols,'frames':len(frames),
            'root':root,'height':height,'authoredFrames':len(frames),'muzzles':[n['muzzle'] for n in notes],'sources':notes}
    (out/f'{direction}_{action}.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({'direction':direction,'action':action,'frames':len(frames)}),flush=True)
    return record
