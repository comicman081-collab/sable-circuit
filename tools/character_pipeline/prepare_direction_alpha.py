"""Remove reviewed chroma backgrounds, including enclosed holes, from direction art.

No character RGB is repainted. Originals and prior masks remain unchanged.
This derived batch must be visually reviewed before a motion profile uses it.
"""
import argparse
from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import derive_chroma_runtime_rgba as chroma


def run(args):
    source=g.read(args.report);out=g.local(args.out)
    out.mkdir(parents=True,exist_ok=False)
    sheet=Image.new('RGB',(1920,1080),(17,25,33));draw=ImageDraw.Draw(sheet)
    draw.text((36,22),'MICA / corrected background separation / existing ImageGen source RGB preserved',fill=(211,227,232))
    battle=Image.new('RGB',(1920,1080),(17,25,33));bd=ImageDraw.Draw(battle)
    bd.text((36,22),'Battle-scale alpha check / 224 px character height / not a motion completion claim',fill=(211,227,232))
    records=[]
    for i,row in enumerate(source['directions']):
        direction=row['direction'];master=g.local(row['master'])
        if g.ref(master)['sha256']!=row['master_sha256']:raise ValueError('EXACT_SOURCE_CHANGED')
        path=out/f'{direction}_RGBA.png'
        report=chroma.derive(master,path)
        image=Image.open(path).convert('RGBA');width,height=image.size
        rgba=np.asarray(image);original=np.asarray(Image.open(master).convert('RGB'))
        old_mask=Image.open(g.local(row['mask'])).convert('L')
        if g.ref(g.local(row['mask']))['sha256']!=row['mask_sha256']:raise ValueError('OLD_MASK_CHANGED')
        removed=(np.asarray(old_mask)>0)&(rgba[:,:,3]==0)
        report['removed_previously_visible_background_pixels']=int(removed.sum())
        report['previous_mask']=g.ref(g.local(row['mask']))
        report['retained_rgb_byte_exact']=bool(np.array_equal(original[rgba[:,:,3]>0],rgba[rgba[:,:,3]>0,:3]))
        Image.fromarray(rgba[:,:,3]).save(out/f'{direction}_MASK.png')
        original_scale=Image.new('RGBA',(max(1920,width*2),max(1080,height)),(232,234,237,255))
        dark=Image.new('RGBA',(width,height),(17,25,33,255));dark.alpha_composite(image)
        original_scale.alpha_composite(image,(0,0));original_scale.alpha_composite(dark,(width,0))
        original_scale.convert('RGB').save(out/f'{direction}_ORIGINAL_SCALE_LIGHT_DARK.png')
        bbox=image.getbbox();subject=image.crop(bbox)
        thumbnail=subject.copy();thumbnail.thumbnail((380,430),Image.Resampling.LANCZOS)
        x=40+(i%4)*475;y=75+(i//4)*500
        draw.text((x,y),direction,fill=(110,227,210))
        sheet.paste(thumbnail,(x+(420-thumbnail.width)//2,y+26),thumbnail)
        small=subject.resize((round(subject.width*224/subject.height),224),Image.Resampling.LANCZOS)
        bx=180+(i%4)*460;by=230+(i//4)*490
        battle.paste(small,(bx-small.width//2,by),small)
        bd.text((bx-10,by+240),direction,fill=(110,227,210))
        report['original_scale_evidence']=g.ref(out/f'{direction}_ORIGINAL_SCALE_LIGHT_DARK.png')
        report['subject_native_bbox']=list(bbox)
        g.write(out/f'{direction}_ALPHA_QA.json',report)
        records.append({'direction':direction,'rgba':g.ref(path),'qa':g.ref(out/f'{direction}_ALPHA_QA.json'),
                        'residual_chroma_pixels':report['visible_strong_green_residual_pixels'],
                        'removed_old_visible_pixels':report['removed_previously_visible_background_pixels']})
        print(direction,'removed_old',records[-1]['removed_old_visible_pixels'],'residual',records[-1]['residual_chroma_pixels'])
    sheet.save(out/'DIRECTIONS_CLEAN_ALPHA_1920x1080.png');battle.save(out/'BATTLE_SCALE_ALPHA_1920x1080.png')
    g.write(out/'MANIFEST.json',{'source_report':g.ref(args.report),'builder':g.ref(__file__),
        'alpha_implementation':g.ref(chroma.__file__),'directions':records,
        'scope':'BACKGROUND_SEPARATION_DERIVATIVES_NOT_MOTION_APPROVAL','production_ready':False,
        'review':'PENDING_INDEPENDENT_VISUAL_REVIEW',
        'contact':g.ref(out/'DIRECTIONS_CLEAN_ALPHA_1920x1080.png'),
        'battle_scale':g.ref(out/'BATTLE_SCALE_ALPHA_1920x1080.png')})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',required=True);parser.add_argument('--out',required=True)
    run(parser.parse_args())
