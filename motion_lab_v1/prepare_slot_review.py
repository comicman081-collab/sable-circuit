"""Native source-slot evidence on light/dark mattes. Never grants approval."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageDraw
from build_atlas import key_image
from character_workflow import ROOT, recipe, slots, sha, write
from source_provenance import validate_slot

def prepare(character, slot):
    source = dict(slots(recipe(character)))[slot]
    receipt = json.loads(source.with_suffix('.source.json').read_text(encoding='utf-8'))
    validate_slot(ROOT, source, receipt)
    rgba = Image.fromarray(key_image(source))
    dependencies = {p.name:sha(p) for p in [Path(__file__),ROOT/'build_atlas.py',ROOT/'source_provenance.py']}
    implementation = hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()[:8]
    signature = sha(source)[:12]+'_'+implementation
    out = ROOT/'qa'/character/'source_panels'/signature
    out.mkdir(parents=True, exist_ok=True)
    rgba.save(out/'candidate_rgba.png')
    rows = []
    for label in ['full','native_upper','native_lower']:
        board = Image.new('RGB',(1920,1080),'#15232b')
        for x, color in [(0,'#eeeeee'),(960,'#15232b')]:
            panel = Image.new('RGBA',(960,1080),color)
            im = rgba.copy()
            if label == 'full':
                im.thumbnail((930,1010),Image.Resampling.LANCZOS)
            else:
                left = max(0,(im.width-940)//2)
                top = 0 if label=='native_upper' else max(0,im.height-1010)
                im = im.crop((left,top,min(im.width,left+940),min(im.height,top+1010)))
            panel.alpha_composite(im,((960-im.width)//2,45+(1010-im.height)//2))
            board.paste(panel.convert('RGB'),(x,0))
        ImageDraw.Draw(board).text((20,14),character+' / '+slot+' / '+label+' / NOT APPROVED',fill='#bb874f')
        target = out/(label+'_1920x1080.png')
        board.save(target)
        rows.append({'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'native':[1920,1080],'source_pixel_scale':1 if label!='full' else 'fit-down-only'})
    report={'status':'PREPARED_NOT_APPROVED','source':source.relative_to(ROOT).as_posix(),'sourceSHA256':sha(source),'sourceNative':list(rgba.size),'provenanceSHA256':sha(source.with_suffix('.source.json')),'images':rows,'implementationDependencies':dependencies}
    write(out/'report.json',report)
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--slot',required=True)
    a=p.parse_args();prepare(a.character,a.slot)
