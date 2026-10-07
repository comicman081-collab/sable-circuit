"""Native costume-detail reference only. No generated or repaired source pixels."""
from pathlib import Path
import json, hashlib
from PIL import Image
lab=Path(__file__).resolve().parents[2]
source=lab/'art/site7_enemies_raw/rifle_SE_walk_1_v1.png'
out=lab/'reference/site7_rifle/SE_knee_caps_from_walk1.png'
if out.exists():raise FileExistsError(out)
box=(320,895,745,1225)
with Image.open(source) as im:
    if im.size!=(1024,1536):raise ValueError('Unexpected native source')
    im.crop(box).save(out)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'purpose':'Costume-detail reference: silver/red knee caps, not pose or leg count authority',
        'source':str(source.relative_to(lab)),'sourceSHA256':digest(source),'crop':box,
        'output':str(out.relative_to(lab)),'outputSHA256':digest(out),
        'resampling':False,'redraw':False,'visualQA':False}
out.with_suffix('.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
