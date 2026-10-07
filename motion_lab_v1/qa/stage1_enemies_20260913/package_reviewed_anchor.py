"""Package the observed fixed-core boss. No registry write or art approval."""
from pathlib import Path
import hashlib,json,shutil,sys
LAB=Path(__file__).resolve().parents[2]
PROJECT=LAB.parent
sys.path.insert(0,str(LAB))
from prepare_enemy_asset import verify_source

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=LAB/'art/site7_enemies_raw/anchor_master.png'
    response=LAB/'qa/stage1_enemies_20260913/anchor_master_tool_response.json'
    verify_source(source.resolve(),response.resolve())
    assert sha(source)=='375bc85a7513b20509b53e869578bb45d846732441ff92de6ce83613dd4c827e'
    spec_path=LAB/'qa/stage1_enemies_20260913/anchor/candidate_spec_v1.json'
    assert sha(spec_path)=='33c941e9509386f3b6eec54b69c945175d6755da5e570feee4068e93bf0bb5c3'
    spec=json.loads(spec_path.read_text())
    candidate=PROJECT/spec['texture'].removeprefix('res://')
    assert sha(candidate)==spec['texture_sha256']
    capture=PROJECT/'qa/stage1_implementation_20260913/anchor_native_1789288928_45/capture_report.json'
    assert sha(capture)=='3aa6ef89358e472dd48568ecea3f10dee8f0941be38a3f2f7f013b7f01906c0b'
    report=json.loads(capture.read_text())
    assert not report['failures'] and len(report['rows'])==22
    for path,digest in report['hashes'].items():
        assert sha(PROJECT/path.removeprefix('res://'))==digest,'Changed reviewed dependency: '+path
    for row in report['rows']:
        assert row['native']==[1920,1080]
        assert sha(PROJECT/row['path'].removeprefix('res://'))==row['sha256']
        assert row['machine']['texture_sha256']==spec['texture_sha256']
    out=PROJECT/'assets/enemies/signal_anchor_guardian/authored_core_v1'
    out.mkdir(parents=True,exist_ok=True)
    dest=out/'anchor.png'
    if dest.exists():assert sha(dest)==spec['texture_sha256']
    else:shutil.copy2(candidate,dest)
    assert sha(dest)==spec['texture_sha256']
    spec['texture']='res://'+dest.relative_to(PROJECT).as_posix()
    spec['status']='REVIEWED_LOCAL_MVP_FIXED_CORE'
    payload=(json.dumps(spec,indent=2)+'\n').encode()
    target=out/'spec.json'
    if target.exists():assert target.read_bytes()==payload
    else:target.write_bytes(payload)
    review=PROJECT/'qa/stage1_implementation_20260913/ANCHOR_VISUAL_REVIEW.md'
    receipt={'status':'PACKAGED_REVIEWED_LOCAL_ANCHOR_ONLY','registry_changed':False,
        'spec':target.relative_to(PROJECT).as_posix(),'sha256':sha(target),
        'master_sha256':sha(source),'response_sha256':sha(response),
        'candidate_spec_sha256':sha(spec_path),'capture_sha256':sha(capture),
        'visual_review':{'path':review.relative_to(PROJECT).as_posix(),'sha256':sha(review)},
        'operations':['byte-identical copy','texture path rebinding'],
        'deployment':False,'luna_reproduction':False,'independent_arm_motion':False}
    (LAB/'qa/stage1_enemies_20260913/anchor_app_package.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt))
if __name__=='__main__':main()
