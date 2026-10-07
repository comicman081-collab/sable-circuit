"""Copy the exact manually reviewed drone set to a versioned app bundle.

No art synthesis, resizing, registry mutation or automatic visual approval.
Fails before copying if any master/response/candidate/capture changed.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

LAB = Path(__file__).resolve().parents[2]
PROJECT = LAB.parent
sys.path.insert(0, str(LAB))
from prepare_enemy_asset import verify_source

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    bundle = LAB / 'qa/stage1_enemies_20260913/drone_yaw8/a2a58793089e24f3'
    spec_path = bundle / 'candidate_spec.json'
    expected = 'f3cc4fb74925e0a84fb1c475911af0c4e3e0ac4467cfb4d092b0ed41dfe880a8'
    assert sha(spec_path) == expected, 'Candidate differs from observed review'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    sources = json.loads((bundle/'source_binding.json').read_text(encoding='utf-8'))
    capture = PROJECT/'qa/stage1_implementation_20260913/facing_native_1789285783_092/capture_report.json'
    evidence = json.loads(capture.read_text(encoding='utf-8'))
    assert not evidence['failures'] and len(evidence['rows']) == 24
    for row in evidence['rows']:
        image = PROJECT/row['image'].removeprefix('res://')
        assert row['native'] == [1920,1080] and sha(image) == row['sha256']
        direction = row['label'].split('_')[0]
        assert row['machine']['texture_sha256'] == spec['views'][direction]['texture_sha256']
    for direction, source in sources['sources'].items():
        master = LAB/source['source']
        response = LAB/source['toolResponse']['path']
        candidate = LAB/source['candidate']
        assert sha(master) == source['sourceSHA256']
        assert sha(response) == source['toolResponse']['sha256']
        verify_source(master.resolve(), response.resolve())
        assert sha(candidate) == source['candidateSHA256'] == spec['views'][direction]['texture_sha256']
    out = PROJECT/'assets/enemies/recon_drone/authored_yaw8_v1'
    out.mkdir(parents=True, exist_ok=True)
    for direction, view in spec['views'].items():
        source = PROJECT/view['texture'].removeprefix('res://')
        dest = out/(direction+'.png')
        if dest.exists():
            assert sha(dest) == view['texture_sha256'], 'Do not overwrite a different bundle'
        else:
            shutil.copy2(source, dest)
        assert sha(dest) == view['texture_sha256']
        view['texture'] = 'res://'+dest.relative_to(PROJECT).as_posix()
    spec['enemy_id'] = 'ENM_SITE7_DRONE_01'
    spec['schema_version'] = 1
    spec_bytes = (json.dumps(spec, indent=2)+'\n').encode()
    target = out/'spec.json'
    if target.exists():
        assert target.read_bytes() == spec_bytes, 'Versioned spec is immutable'
    else:
        target.write_bytes(spec_bytes)
    review = PROJECT/'qa/stage1_implementation_20260913/DRONE_YAW8_VISUAL_REVIEW.md'
    receipt = {
        'status':'PACKAGED_REVIEWED_LOCAL_DRONE_ONLY',
        'spec':target.relative_to(PROJECT).as_posix(), 'sha256':sha(target),
        'candidate':spec_path.relative_to(PROJECT).as_posix(), 'candidate_sha256':expected,
        'source_binding':sha(bundle/'source_binding.json'),
        'visual_review':{'path':review.relative_to(PROJECT).as_posix(),'sha256':sha(review)},
        'native_capture':{'path':capture.relative_to(PROJECT).as_posix(),'sha256':sha(capture)},
        'operations':['byte-identical copy','texture path rebinding'],
        'registry_changed':False, 'deployment':False, 'luna_reproduction':False,
    }
    (LAB/'qa/stage1_enemies_20260913/drone_app_package.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
