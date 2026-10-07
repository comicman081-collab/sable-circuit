"""Synthetic regression PNGs only. Never source art or runtime assets."""
from pathlib import Path
import math, hashlib, json
from PIL import Image, ImageDraw, PngImagePlugin

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'qa/stage1_enemies_20260913/machine_edge_fixtures_v1'
NAMES=['E','SE','S','SW','W','NW','N','NE']
OUT.mkdir(parents=True,exist_ok=True)
all_specs={}
for kind in ['unique','metadata_only','hidden_rgb_only']:
    views={}
    for i,name in enumerate(NAMES):
        im=Image.new('RGBA',(1536,1024),(i*20 if kind=='hidden_rgb_only' else 0,0,0,0))
        draw=ImageDraw.Draw(im)
        draw.rectangle((700,460,836,564),fill=(180,90,80,255))
        if kind=='unique': draw.rectangle((710+i*10,480,715+i*10,485),fill=(255,255,255,255))
        meta=PngImagePlugin.PngInfo(); meta.add_text('direction-label',name)
        path=OUT/(kind+'_'+name+'.png'); im.save(path,pnginfo=meta)
        views[name]={'texture':'res://motion_lab_v1/'+path.relative_to(ROOT).as_posix(),
            'texture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'root_px':[768,512], 'emitter_px':[768+400*math.cos(i*math.pi/4),512+400*math.sin(i*math.pi/4)],
            'display_height':110}
    all_specs[kind]={'kind':'hover_machine','facing_mode':'authored_yaw8','views':views}
(OUT/'fixtures.json').write_text(json.dumps({'status':'SYNTHETIC_TEST_ONLY_NOT_ART','specs':all_specs},indent=2),encoding='utf-8')
print(OUT)
