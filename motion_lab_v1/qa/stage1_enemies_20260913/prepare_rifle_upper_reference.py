"""One byte-preserving reference crop; no source repair or generated appearance."""
from pathlib import Path
import json, hashlib
from PIL import Image
lab=Path(__file__).resolve().parents[2]
source=lab/'art/site7_enemies_raw/rifle_SE_walk_1_v1.png'
out=lab/'reference/site7_rifle/SE_upper_from_walk1.png'
if out.exists(): raise FileExistsError(out)
out.parent.mkdir(parents=True,exist_ok=True)
box=(0,0,1024,840)
with Image.open(source) as im:
    if im.size!=(1024,1536): raise ValueError('Unexpected native source')
    im.crop(box).save(out)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'purpose':'Upper-body appearance/camera reference without competing leg pose',
        'source':str(source.relative_to(lab)),'sourceSHA256':digest(source),
        'crop':box,'resampling':False,'redraw':False,'output':str(out.relative_to(lab)),
        'outputSHA256':digest(out)}
out.with_suffix('.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
