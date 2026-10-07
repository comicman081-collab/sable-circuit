"""Sequential native runtime samples. Diagnostic only; no artwork or approval."""
import json
from pathlib import Path
import cv2
import numpy as np

lab = Path(__file__).resolve().parents[3]
video = lab / 'qa/rook_motion_astra_20260913.webm'
capture = json.loads(video.with_suffix('.json').read_text(encoding='utf-8'))
out = Path(__file__).resolve().parent / 'runtime_samples'
out.mkdir(exist_ok=True)
segments = {}
for row in capture['observations']:
    if row['segment']:
        segments.setdefault(row['segment'], []).append(row)
requests = []
groups = {}
for label, rows in segments.items():
    start, end = rows[0]['elapsedMs']/1000, rows[-1]['elapsedMs']/1000
    if ' / ' in label or 'stationary' in label:
        # Recorder starts after the first draw, so stay inside both end bounds.
        times = np.linspace(start+.04, end-.16, 10)
    else:
        run = ' run' in label
        times = start + (.20 if run else .25) + np.arange(20)*(.06 if run else .08)
    groups[label] = []
    requests.extend((float(t), label) for t in times)
requests.sort()
cap = cv2.VideoCapture(str(video))
assert [int(cap.get(3)), int(cap.get(4))] == [1920,1080]
for target, label in requests:
    ok, frame = cap.read()
    while ok and cap.get(cv2.CAP_PROP_POS_MSEC)/1000 < target:
        ok, frame = cap.read()
    if not ok:
        raise RuntimeError('Missing requested native frame')
    actual = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    # Fixed camera follows the actor; preserve exact source pixels in this crop.
    crop = frame[380:720, 790:1190]
    groups[label].append((actual, crop.copy()))
    if label == 'E walk' and len(groups[label]) == 1:
        (out/'runtime_native_1080p.png').write_bytes(cv2.imencode('.png',frame)[1].tobytes())
cap.release()
manifest = {'native':[1920,1080], 'crop':[790,380,400,340], 'resampled':False, 'groups':{}}
for label, frames in groups.items():
    sheet = np.full((max(1080,((len(frames)+4)//5)*368),2000,3),24,np.uint8)
    for i,(seconds,frame) in enumerate(frames):
        x,y = (i%5)*400,(i//5)*368
        sheet[y+28:y+368,x:x+400] = frame
        cv2.putText(sheet,f'{label} {seconds:.3f}s',(x+8,y+19),cv2.FONT_HERSHEY_SIMPLEX,.40,(225,225,225),1)
    name = label.replace(' / ','_').replace(' + ','_').replace(' ','_')+'.png'
    (out/name).write_bytes(cv2.imencode('.png',sheet)[1].tobytes())
    manifest['groups'][label] = {'sheet':name, 'seconds':[t for t,_ in frames]}
(out/'samples.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'groups':len(groups),'samples':len(requests),'output':str(out)}))
