"""Native annotation overlays for checking reviewer coordinates, never approval."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
base=Path(__file__).parent;lab=base.parents[1]
points=json.loads((base/'rifle_e_landmarks.json').read_text())
atlas=Image.open(lab/'qa/site7_rifle/gait/afd699355069c1f1_1853e533/public/assets/atlas/site7_rifle/E_walk.webp').convert('RGBA')
out=base/'rifle_e_annotation_review_v3';out.mkdir(exist_ok=False)
for index,row in enumerate(points['frames']):
    cell=atlas.crop((index%3*768,index//3*768,(index%3+1)*768,(index//3+1)*768))
    board=Image.new('RGB',(1920,1080),'#101e27');board.paste(cell,(50,180),cell);board.paste(cell,(1020,180),cell)
    d=ImageDraw.Draw(board)
    for x in range(0,769,64):
        d.line((1020+x,180,1020+x,948),fill='#344047');d.text((1020+x,160),str(x),fill='white')
    for y in range(0,769,64):
        d.line((1020,180+y,1788,180+y),fill='#344047');d.text((985,180+y),str(y),fill='white')
    for side,color in [('left','#49ffff'),('right','#ffcc36')]:
        chain=[tuple(row[side+p]) for p in ('Hip','Knee','Sole')]
        d.line([(1020+x,180+y) for x,y in chain],fill=color,width=2)
        for part,(x,y) in zip(('Hip','Knee','Sole'),chain):
            d.ellipse((1016+x,176+y,1024+x,184+y),outline=color,width=2)
            d.text((1028+x,180+y),side[0]+part,fill=color)
    d.text((50,30),f'E frame {index} / native pixels / annotation DRAFT cyan=anatomical left, gold=anatomical right',fill='white')
    board.save(out/f'frame_{index}.png')
print(out)
