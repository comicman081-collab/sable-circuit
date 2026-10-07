"""Publish this explicitly reviewed batch only; never auto-edit app registries."""
import copy, hashlib, json, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

QA=Path(__file__).resolve().parent
LAB=QA.parents[1]
ROOT=LAB.parent
OUT=ROOT/'qa/stage_enemies_20260919'
CAND=QA/'candidate_v1'
sys.path.insert(0,str(LAB))
from source_alpha_policy import inspect_master
from source_provenance import response_master
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def data(p): return json.loads(p.read_text(encoding='utf-8'))
def res(p): return ROOT/p.removeprefix('res://')
def immutable_write(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): assert path.read_bytes()==payload, f'Versioned output changed: {path}'
    else: path.write_bytes(payload)

def main():
    proof=OUT/'native_1789819039_415/check.json'
    report=data(proof)
    assert report['status']=='PASS_TECHNICAL' and not report['failures'] and not report['app_registry']
    for p,h in report['sha256'].items():
        assert sha(CAND/'specs.json' if p=='candidate_specs' else ROOT/p)==h,p
    for c in report['captures']:
        assert sha(res(c['image']))==c['sha256']
        assert Image.open(res(c['image'])).size==(1920,1080)
    assert len(report['captures'])==21
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/art_pipeline/validate_visual_evidence_1080p.py'),
        *[str(res(c['image'])) for c in report['captures']],
        '--output',str(OUT/'candidate_1080p.json')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    review=OUT/'VISUAL_REVIEW.md'
    assert review.is_file() and 'Decision:' in review.read_text(encoding='utf-8')
    selection=data(QA/'selection.json'); binding=data(CAND/'bindings.json')
    assert binding['selection_sha256']==sha(QA/'selection.json')
    assert binding['builder_sha256']==sha(QA/'build_native_candidates.py')
    specs=data(CAND/'specs.json'); published=[]
    targets={'bulwark':'bulwark/authored_yaw8_v1','ram':'cinder_ram/authored_yaw8_v1','mortar':'vesper_mortar/authored_core_v1'}
    for name,entry in selection.items():
        dest=ROOT/'assets/enemies'/targets[name]
        spec=copy.deepcopy(specs[entry['id']])
        rows=[r for r in binding['rows'] if r['name']==name]
        for row in rows:
            source=ROOT/row['source']; response=ROOT/row['response']; candidate=ROOT/row['candidate']
            for p,k in [(source,'source'),(response,'response'),(candidate,'candidate')]: assert sha(p)==row[k+'_sha256']
            assert response_master(LAB,response)==source.resolve()
            inspect_master(source)
            assert np.array_equal(np.array(Image.open(candidate)),np.array(Image.open(source).crop(row['box'])))
            target=dest/(row['direction']+'.png')
            immutable_write(target,candidate.read_bytes())
            view=spec if name=='mortar' else spec['views'][row['direction']]
            view['texture']='res://'+target.relative_to(ROOT).as_posix()
            assert view['texture_sha256']==sha(target)
        target=dest/'spec.json'
        immutable_write(target,(json.dumps(spec,indent=2)+'\n').encode())
        published.append({'enemy_id':entry['id'],'spec':'res://'+target.relative_to(ROOT).as_posix(),'sha256':sha(target)})
    receipt={'status':'VERSIONED_BUNDLES_ONLY_REGISTRY_NOT_CHANGED','bundles':published,
        'candidate_binding_sha256':sha(CAND/'bindings.json'),'candidate_check_sha256':sha(proof),
        'manual_review_sha256':sha(review),'source_count':17,'external_review':False,'luna_reproduction':False}
    (OUT/'bundle_publication.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': main()
