from pathlib import Path
import hashlib, json, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from source_alpha_policy import inspect_master
p=ROOT/'master_imagegen_v1.png'
report=inspect_master(p)
im=Image.open(p).convert('RGBA')
for label,box in [('upper',(32,0,992,1080)),('lower',(32,456,992,1536))]:
    crop=im.crop(box)
    board=Image.new('RGB',(1920,1080))
    for x,color in [(0,'#eeeeee'),(960,'#15232b')]:
        matte=Image.new('RGBA',(960,1080),color)
        matte.alpha_composite(crop)
        board.paste(matte.convert('RGB'),(x,0))
    board.save(ROOT/f'native_{label}_1920x1080.png')
report['sourcePixelsModified']=False
report['runtimePromotion']=False
(ROOT/'alpha_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
