"""Decode actual browser capture sequentially; no synthetic playback or approval."""
from pathlib import Path
import argparse, json, hashlib
import cv2
import numpy as np

p=argparse.ArgumentParser();p.add_argument('video',type=Path);a=p.parse_args()
lab=Path(__file__).resolve().parents[2]
video=a.video.resolve()
if not video.is_relative_to(lab):raise ValueError('Project-local video only')
out=video.parent/(video.stem+'_samples_v2');out.mkdir(exist_ok=False)
cap=cv2.VideoCapture(str(video));rows=[];frames=[]
while True:
    ok,frame=cap.read()
    if not ok:break
    if frame.shape[:2]!=(1080,1920):raise ValueError('Native capture required')
    frames.append((cap.get(cv2.CAP_PROP_POS_MSEC)/1000,frame.copy()))
cap.release()
if len(frames)<30:raise ValueError('Not a decoded temporal capture')
# E walk is 1.185185 seconds. Sample first two cycles at 100ms intervals,
# preserving the 270px live panel at its real pixels (no enlargement).
targets=np.arange(.05,min(2.5,frames[-1][0]),.1)
board=np.full((max(1080,((len(targets)+4)//5)*385),2000,3),24,np.uint8)
for i,t in enumerate(targets):
    seconds,frame=min(frames,key=lambda row:abs(row[0]-t))
    x,y=(i%5)*400,(i//5)*385
    board[y+28:y+385,x:x+400]=frame[540:897,1200:1600]
    cv2.putText(board,f'{seconds:.3f}s',(x+8,y+19),cv2.FONT_HERSHEY_SIMPLEX,.45,(225,225,225),1)
    rows.append({'requestedSeconds':float(t),'decodedSeconds':seconds})
    if i in [0,2,4,6,8,10,12]:
        ok,encoded=cv2.imencode('.png',frame)
        if not ok:raise ValueError('Native PNG encoding failed')
        (out/f'native_{i:02d}.png').write_bytes(encoded.tobytes())
ok,encoded=cv2.imencode('.png',board)
if not ok:raise ValueError('Sequence PNG encoding failed')
(out/'normal_speed_sequence.png').write_bytes(encoded.tobytes())
receipt={'videoSHA256':hashlib.sha256(video.read_bytes()).hexdigest(),'native':[1920,1080],
         'decodedFrames':len(frames),'durationSeconds':frames[-1][0],
         'crop':[1200,540,400,357],'resampling':False,'samples':rows,'visualApproval':False}
(out/'sampling.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),**receipt}))
