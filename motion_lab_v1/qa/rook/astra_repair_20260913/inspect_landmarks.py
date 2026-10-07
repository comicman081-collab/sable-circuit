"""Native QA crops and annotation diagnostics only, never runtime artwork."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[3]
kit=root/sys.argv[1]
packet=json.loads((kit/'cycle-observations.json').read_text(encoding='utf-8'))
preview=json.loads((kit/'cycle-preview.json').read_text(encoding='utf-8'))
atlas=Image.open(root/preview['atlas']['path']).convert('RGBA')
cw,ch=preview['clip']['cell'];cols=preview['clip']['columns']
for row in packet['frames']:
 i=row['index'];cell=atlas.crop((i%cols*cw,i//cols*ch,i%cols*cw+cw,i//cols*ch+ch));a=np.array(cell)
 panel=Image.new('RGB',(1920,1080),'#16252d');panel.paste(cell,(20,100),cell);panel.paste(cell,(1030,100),cell)
 draw=ImageDraw.Draw(panel)
 for x in range(0,cw,50):
  draw.line((1030+x,100,1030+x,100+ch),fill='#34434b');draw.text((1030+x,80),str(x),fill='white')
 for y in range(0,ch,50):
  draw.line((1030,100+y,1030+cw,100+y),fill='#34434b');draw.text((995,100+y),str(y),fill='white')
 for name,p in row['landmarks'].items():
  if p is None:continue
  x,y=map(int,p);ok=np.any(a[max(0,y-5):y+6,max(0,x-5):x+6,3]>128)
  if not ok:print('OFF_SUBJECT',i,name,p)
  draw.ellipse((1030+x-3,100+y-3,1030+x+3,100+y+3),fill='cyan' if name.startswith('left') else 'orange')
  draw.text((1036+x,100+y),name,fill='cyan' if name.startswith('left') else 'orange')
 draw.text((20,30),f"{packet['direction']} frame {i}: native 768px cell. Right panel coordinate grid; no upscaling.",fill='white')
 panel.save(kit/f'native_cell_{i}.png')
