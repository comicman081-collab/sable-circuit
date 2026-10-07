"""Read-only master inspection on two mattes; these panels are NOT source art."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

here=Path(__file__).resolve().parent
lab=here.parents[1]
report=json.loads((here/'S0_attempt_review.json').read_text('utf-8'))
source=lab/report['source']
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['sha256']
im=Image.open(source)
assert im.mode=='RGBA'
rows=[]
for label,top in [('native_upper',0),('native_lower',im.height-1000)]:
    board=Image.new('RGB',(1920,1080),'#15232b')
    crop=im.crop((42,top,982,top+1000))
    for x,color in [(0,'#eeeeee'),(960,'#15232b')]:
        panel=Image.new('RGBA',(960,1080),color)
        panel.alpha_composite(crop,(10,60))
        board.paste(panel.convert('RGB'),(x,0))
    ImageDraw.Draw(board).text((20,16),'S0 / '+label+' / original-scale alpha inspection / NOT APPROVED',fill='#b98743')
    path=here/(label+'_raw_1920x1080.png')
    board.save(path)
    rows.append({'path':str(path.relative_to(lab)),'native':[1920,1080],
                 'source_pixel_scale':1,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(here/'raw_panel_manifest.json').write_text(json.dumps({'source':report['source'],
    'source_sha256':report['sha256'],'source_modified':False,'panels':rows},indent=2),encoding='utf-8')
