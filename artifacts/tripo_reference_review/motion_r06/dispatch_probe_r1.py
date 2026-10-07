"""Read-only mixed-schema dispatch probe. Never produces a PASS receipt."""
from pathlib import Path
import copy
import sys
import json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import visible_frame_harness_current as current
import existing_frame_derivative_admission as admission

manifest=ROOT/'artifacts/quarantine/generation_diagnostics/mica_r6_alpha_protection_r01/ADMISSION_MANIFEST.json'
bundle=Path(__file__).resolve()
read=g.read
selected={}
def fixture_read(path):
    p=g.local(path)
    if p==bundle:
        return {'frame_manifest':g.ref(manifest),'reviews':[]}
    data=read(path)
    if p==manifest:
        data=copy.deepcopy(data)
        data['frame_validation_contract']=g.ref(current.phase_frame.PHASE_CONTRACT)
    return data
def stop_before_review(reviews,subject,checks,roles=None):
    selected.update(subject=subject,checks=checks,roles=roles)
    raise ValueError('PROBE_STOP_NO_REVIEW_OR_RECEIPT_PRODUCED')
with patch.object(g,'read',side_effect=fixture_read),patch.object(g,'verify_reviews',side_effect=stop_before_review):
    try:
        current._seal_frame_current(bundle)
    except ValueError as exc:
        selected['stopped']=str(exc)
selected['omitted_admission_checks']=sorted(set(admission.EXTRA_CHECKS)-set(selected.get('checks',[])))
selected['current_gate']=g.ref(current.__file__)
selected['scope']='IN_MEMORY_DISPATCH_TEST_NO_PRODUCTION_REVIEW_OR_RECEIPT'
selected['production_files_modified']=False
out=Path(__file__).with_name('DISPATCH_PROBE_R1.json')
assert not out.exists()
g.write(out,selected)
print(json.dumps(selected,indent=2))
