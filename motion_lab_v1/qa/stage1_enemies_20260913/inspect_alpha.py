"""Read-only source inspection; composites are QA, never runtime art."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
root=Path(__file__).resolve().parent
source=root.parent.parent/'art/enemy_rifle/reference/rifle_master_v1.png'
im=Image.open(source).convert('RGBA')
board=Image.new('RGB',(1920,1080),'#122027')
for x,bg in [(0,'#eeeeee'),(960,'#15232b')]:
    panel=Image.new('RGBA',(960,1080),bg)
    # Native 1:1 centre crop deliberately includes background beside torso.
    crop=im.crop((0,200,960,1280))
    panel.alpha_composite(crop)
    board.paste(panel.convert('RGB'),(x,0))
board.save(root/'rifle_master_alpha_native_1920x1080.png')
print(json.dumps({'source':str(source),'native_source':im.size,'native_review':board.size,
 'sample_rgba':{str(p):im.getpixel(p) for p in [(100,750),(100,300),(800,750),(400,1400),(500,600),(900,1200)]}}))
