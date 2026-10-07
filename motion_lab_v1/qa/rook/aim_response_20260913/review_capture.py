"""Decode the current capture chronologically; never approve observations."""
import json
from pathlib import Path
import cv2
import numpy as np

LAB=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
capture=json.loads((LAB/'qa/rook_aim_motion_20260913.json').read_text())
groups={}
for row in capture['observations']:
    label=row.get('segment','')
    if not label:continue
    if ' / ' not in label and (' walk' in label or ' run' in label) and row.get('amount',0)<.9:continue
    groups.setdefault(label,[]).append(row['elapsedMs']/1000)
requests=[]
for label,times in groups.items():
    # MediaRecorder timestamps start slightly after the first draw. Stay away
    # from label boundaries and the last RAF after the final encoded frame.
    for i,t in enumerate(np.linspace(times[0]+.16,times[-1]-.20,6)):
        requests.append((float(t),label,i))
requests.sort()
cap=cv2.VideoCapture(str(LAB/'qa/rook_aim_motion_20260913.webm'))
sheets={};records=[]
for target,label,i in requests:
    ok,frame=cap.read()
    while ok and cap.get(cv2.CAP_PROP_POS_MSEC)<target*1000:ok,frame=cap.read()
    if not ok:raise RuntimeError('Missing frame')
    actual=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    if frame.shape[:2]!=(1080,1920):raise RuntimeError('Not native 1080p')
    # Two rows, three columns, native 640x540 regions including entire actor.
    sheet=sheets.setdefault(label,np.full((1136,1920,3),22,np.uint8))
    x=(i%3)*640;y=(i//3)*568
    sheet[y+28:y+568,x:x+640]=frame[220:760,640:1280]
    cv2.putText(sheet,f'{label} {actual:.3f}s',(x+5,y+20),cv2.FONT_HERSHEY_SIMPLEX,.43,(230,230,230),1)
    records.append({'segment':label,'seconds':actual})
cap.release()
for n,(label,sheet) in enumerate(sheets.items()):
    (OUT/f'sequence_{n:02}.png').write_bytes(cv2.imencode('.png',sheet)[1].tobytes())
(OUT/'decoded_samples.json').write_text(json.dumps({'native':[1920,1080],'resampled':False,'sheets':list(sheets),'samples':records},indent=2))
print(json.dumps({'sheets':len(sheets),'samples':len(records)}))
