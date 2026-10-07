"""Retain the actual returned master and inspect it without modifying pixels."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
from PIL import Image
import numpy as np

LAB = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(LAB))
from source_alpha_policy import inspect_master

response = json.loads((HERE/'S0_actual_tool_response.json').read_text('utf-8'))
source = Path(response['returnedPath'])
if not source.is_file():
    # The user requires verified managed staging duplicates to be removed.
    # Reinspection must use the retained exact-byte project master, not regenerate.
    source = (LAB / response['projectCopy']).resolve()
    assert source.is_relative_to(LAB)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == response['projectCopySHA256']
digest = hashlib.sha256(source.read_bytes()).hexdigest()
destination = LAB/'qa/site7_rifle/quarantine'/digest/'S_walk_0_20260919_native_attempt.png'
destination.parent.mkdir(parents=True,exist_ok=True)
if destination.exists():
    assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
else:
    shutil.copy2(source,destination)
assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
response.update(projectCopy=destination.relative_to(LAB).as_posix(),projectCopySHA256=digest)
(HERE/'S0_actual_tool_response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2),encoding='utf-8')
with Image.open(destination) as image:
    facts={'mode':image.mode,'native':list(image.size),'format':image.format}
    alpha=np.asarray(image.getchannel('A')) if image.mode=='RGBA' else np.full((image.height,image.width),255,dtype=np.uint8)
    facts.update(alphaMin=int(alpha.min()),alphaMax=int(alpha.max()),transparentPixels=int((alpha==0).sum()))
try:
    gate=inspect_master(destination)
except ValueError as error:
    gate={'status':'FAIL','error':str(error)}
report={'status':'HOLD_NOT_PROMOTED','slot':'S/walk/0','source':destination.relative_to(LAB).as_posix(),
        'sha256':digest,'raw':facts,'alphaGate':gate,'sourcePixelsModified':False,
        'visual_observations':['Anatomical left boot on image right leads and right-only holster stays on image left.',
            'Rifle and head remain turned toward image right rather than the required straight-front S aim.',
            'Native alpha 0..254 format passed; consult the separately recorded original-scale panel review.'],
        'active_source_and_runtime_unchanged':True,'toolResponseSHA256':hashlib.sha256((HERE/'S0_actual_tool_response.json').read_bytes()).hexdigest()}
previous_path = HERE/'S0_attempt_review.json'
if previous_path.is_file():
    previous = json.loads(previous_path.read_text('utf-8'))
    if previous.get('sha256') == digest:
        report['visual_observations'] = previous['visual_observations']
(HERE/'S0_attempt_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(HERE/'S0_actual_tool_response.json',destination.parent/'actual_tool_response.json')
shutil.copy2(HERE/'S0_attempt_request.json',destination.parent/'request.json')
print(json.dumps(report))
