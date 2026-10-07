"""Native source-scale plus sequence previews; never changes runtime pointers."""
import argparse,json,hashlib,uuid
from pathlib import Path
from PIL import Image,ImageDraw
from character_workflow import ROOT,recipe,slots,sha,write
from build_atlas import build,key_image

def preview(character,direction,action='walk'):
    c=recipe(character);count=c['clips'][action]['frames'];paths=[dict(slots(c))[f'{direction}/{action}/{i}'] for i in range(count)]
    digest=hashlib.sha256(''.join(sha(p) for p in paths).encode()).hexdigest()
    out=ROOT/'qa'/character/'gait'/(digest[:16]+'_'+uuid.uuid4().hex[:8]);out.mkdir(parents=True,exist_ok=True)
    clip=build(c,direction,action,paths,c.get('annotations',{}).get(direction,{}).get(action,{}),output_root=out)
    evidence=[]
    pairs=[[0,0]] if count==1 else [[p,p+count//2] for p in range(count//2)]
    dimensions=[]
    for pair,indices in enumerate(pairs):
        images=[Image.fromarray(key_image(paths[i])) for i in indices]
        panel_width=max(960,max(im.width for im in images)+40);height=max(1080,max(im.height for im in images)+90)
        page=Image.new('RGB',(panel_width*2,height),(19,30,37));draw=ImageDraw.Draw(page)
        for side,(index,im) in enumerate(zip(indices,images)):
            x=side*panel_width+(panel_width-im.width)//2;y=60
            if side:draw.rectangle((panel_width,0,panel_width*2-1,height-1),fill=(227,230,229))
            page.paste(im,(x,y),im)
            draw.text((side*panel_width+20,20),f'{direction} {action} {index} / native {im.width}x{im.height} / {sha(paths[index])[:12]}',fill=(97,147,145))
        path=out/f'{direction}_{action}_pair{pair}_native_{page.width}x{page.height}.png';page.save(path);evidence.append(str(path.relative_to(ROOT)));dimensions.append(list(page.size))
    result={'sourceDigest':digest,'sourceFrames':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in paths],
            'nativeEvidence':dimensions,'pixelUpscaling':False,'pairEvidence':evidence,'clip':clip,
            'sequence':str((out/'reference/atlas'/character/f'{direction}_{action}.gif').relative_to(ROOT)),
            'contact':str((out/'reference/atlas'/character/f'{direction}_{action}_keyframes.png').relative_to(ROOT)),
            'visualApproval':False}
    write(out/'preview.json',result);print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True);p.add_argument('--action',default='walk');a=p.parse_args();preview(a.character,a.direction,a.action)
