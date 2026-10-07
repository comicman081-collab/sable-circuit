"""Extract decoded video samples at their native pixels for diagnostic review."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('video')
p.add_argument('--output', required=True)
p.add_argument('--start', type=float, default=0)
p.add_argument('--step', type=float, default=1)
p.add_argument('--count', type=int, default=12)
p.add_argument('--columns', type=int, default=3)
p.add_argument('--crop', type=int, nargs=4, metavar=('X','Y','W','H'))
a = p.parse_args()
out = Path(a.output).resolve()
out.mkdir(parents=True, exist_ok=True)
c = cv2.VideoCapture(a.video)
if not c.isOpened():
    raise SystemExit('Video cannot be decoded')
w, h = int(c.get(3)), int(c.get(4))
native = [w, h]
if a.crop:
    cx,cy,w,h = a.crop
samples = []
sheet = np.full((((a.count+a.columns-1)//a.columns)*(h+28), a.columns*w, 3), 24, np.uint8)
for i in range(a.count):
    t = a.start+i*a.step
    # Browser MediaRecorder WebM often lacks a seek index. Decode forward;
    # CAP_PROP_POS_MSEC seeking can otherwise return an unrelated keyframe.
    ok, frame = c.read()
    while ok and c.get(cv2.CAP_PROP_POS_MSEC) < t*1000:
        ok, frame = c.read()
    if not ok:
        break
    actual = c.get(cv2.CAP_PROP_POS_MSEC)/1000
    if a.crop:
        frame = frame[cy:cy+h, cx:cx+w]
    file = out/f'frame_{t:07.3f}.png'
    file.write_bytes(cv2.imencode('.png', frame)[1].tobytes())
    x, y = (i%a.columns)*w, (i//a.columns)*(h+28)
    sheet[y+28:y+28+h, x:x+w] = frame
    cv2.putText(sheet, f'{t:.3f}s / native {w}x{h}', (x+8,y+20), cv2.FONT_HERSHEY_SIMPLEX, .5, (220,220,220), 1)
    samples.append({'seconds':t,'decodedSeconds':actual,'file':str(file)})
c.release()
(out/'samples.png').write_bytes(cv2.imencode('.png', sheet)[1].tobytes())
(out/'samples.json').write_text(json.dumps({'video':a.video,'native':native,'crop':a.crop,'resampled':False,'samples':samples},indent=2),encoding='utf-8')
print(json.dumps({'native':[w,h],'samples':len(samples),'sheet':str(out/'samples.png')}))
