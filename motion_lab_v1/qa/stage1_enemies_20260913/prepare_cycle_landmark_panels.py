"""Native cell grids/observed overlays only; no source editing or approval."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageDraw
p=argparse.ArgumentParser();p.add_argument('kit',type=Path);p.add_argument('--observations',type=Path)
a=p.parse_args();lab=Path(__file__).resolve().parents[2];kit=a.kit.resolve()
if not kit.is_relative_to(lab/'qa'):raise ValueError('Project QA kit required')
preview=json.loads((kit/'cycle-preview.json').read_text(encoding='utf-8'))
clip=preview['clip'];cw,ch=clip['cell']
if [cw,ch]!=[768,768] or clip['frames']!=6:raise ValueError('This native panel layout requires six768px cells')
atlas_path=kit/'public'/clip['image'];atlas=Image.open(atlas_path).convert('RGBA')
points=json.loads(a.observations.read_text(encoding='utf-8')) if a.observations else None
out=kit/('observed_landmark_panels' if points else 'native_cell_grids');out.mkdir(exist_ok=False)
rows=[]
for index in range(6):
    col=clip['columns'];x=index%col*cw;y=index//col*ch
    cell=atlas.crop((x,y,x+cw,y+ch))
    board=Image.new('RGB',(1920,1080),'#101e27');board.paste(cell,(50,180),cell);board.paste(cell,(1020,180),cell)
    d=ImageDraw.Draw(board)
    for x in range(0,769,64):
        d.line((1020+x,180,1020+x,948),fill='#344047');d.text((1020+x,160),str(x),fill='white')
    for y in range(0,769,64):
        d.line((1020,180+y,1788,180+y),fill='#344047');d.text((985,180+y),str(y),fill='white')
    if points:
        row=points['frames'][index]['landmarks']
        for side,color in [('left','#49ffff'),('right','#ffcc36')]:
            chain=[tuple(row[side+part]) for part in ('Hip','Knee','Sole')]
            d.line([(1020+x,180+y) for x,y in chain],fill=color,width=2)
            for part,(x,y) in zip(('Hip','Knee','Sole'),chain):
                d.ellipse((1016+x,176+y,1024+x,184+y),outline=color,width=2)
                d.text((1028+x,180+y),side[0]+part,fill=color)
    d.text((50,30),f"{preview['cycleInputs']['direction']} frame{index} / native cell1:1 / OBSERVATION DRAFT NOT APPROVAL",fill='white')
    path=out/f'frame_{index}.png';board.save(path)
    rows.append({'path':path.relative_to(lab).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report={'native':[1920,1080],'sourcePixelScale':1,'atlasSHA256':hashlib.sha256(atlas_path.read_bytes()).hexdigest(),'visualApproval':False,'images':rows}
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),**report}))
