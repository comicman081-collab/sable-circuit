"""Native 1080p source-sequence review; no interpolation or generated pixels."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
profile=json.loads((ROOT/'public/assets/atlas/mica/profile.json').read_text())
font=ImageFont.truetype(str(ROOT/'public/assets/Rajdhani-Medium.ttf'),23)
small=ImageFont.truetype(str(ROOT/'public/assets/Rajdhani-Medium.ttf'),16)
atlases={d:{a:Image.open(ROOT/'public'/c['image']).convert('RGBA') for a,c in v.items() if a in ['walk','idle']} for d,v in profile['views'].items()}
out=ROOT/'qa';out.mkdir(exist_ok=True)
for action,total in [('walk',6),('idle',1)]:
    frames=[]
    for frame in range(total):
        sheet=Image.new('RGB',(1920,1080),'#0b171e');draw=ImageDraw.Draw(sheet)
        draw.text((32,18),'SABLE CIRCUIT  /  MICA  /  '+action.upper()+'  /  AUTHORED FRAME SEQUENCE',font=font,fill='#b5e8d8')
        draw.text((1886,25),f'{frame+1:02d} / {total:02d}',anchor='ra',font=small,fill='#789d98')
        for index,(d,v) in enumerate(profile['views'].items()):
            clip=v[action];w,h=clip['cell'];i=frame%clip['frames'];atlas=atlases[d][action]
            im=atlas.crop((i%clip['columns']*w,i//clip['columns']*h,i%clip['columns']*w+w,i//clip['columns']*h+h))
            scale=350/clip['height'];im=im.resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
            x=index%4*480+16;y=index//4*488+74;rx=x+222;ry=y+424
            draw.rounded_rectangle((x,y,x+448,y+468),radius=8,fill='#172832',outline='#36524f',width=1)
            draw.text((x+18,y+14),d,font=font,fill='#9cedd2')
            draw.line((x+20,ry,x+428,ry),fill='#42675c',width=1)
            sheet.paste(im,(round(rx-clip['root'][0]*scale),round(ry-clip['root'][1]*scale)),im)
            draw.text((x+18,y+439),f'{d}  /  {action.upper()}  /  KEY {i+1}',font=small,fill='#739f94')
        frames.append(sheet)
    frames[0].save(out/f'mica_8dir_{action}.png')
    if total>1:frames[0].save(out/f'mica_8dir_{action}.gif',save_all=True,append_images=frames[1:],duration=200,loop=0,optimize=False)
print('Saved native 1920x1080 authored-sequence contact images and walk GIF.')
