"""Verify this robot release's real source, registry, route and capture bytes."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'qa/stage_enemies_20260919'
LAB=ROOT/'motion_lab_v1'
SOURCE_QA=LAB/'qa/stage_enemies_20260919'
sys.path.insert(0,str(LAB))
from source_alpha_policy import inspect_master
from source_provenance import response_master
def inside(value):
    p=(ROOT/str(value).removeprefix('res://')).resolve(); p.relative_to(ROOT); return p
def read(p): return json.loads(inside(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(inside(p).read_bytes()).hexdigest()
def current(rows):
    for path,expected in rows.items(): assert sha(path)==expected,f'Stale evidence: {path}'

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--record',action='store_true'); args=parser.parse_args()
    manifest=QA/'delivery_manifest.json'
    if not args.record:
        report=read(manifest); current(report['sha256'])
        print('STAGE_ENEMY_DELIVERY CURRENT',len(report['sha256'])); return
    paths={Path(__file__).relative_to(ROOT).as_posix()}
    profiles={p['enemy_id']:p for p in read('data/art_profiles/enemy_profiles.json')['profiles']}
    ids=['ENM_SITE7_BULWARK_01','ENM_SITE7_RAM_01','ENM_SITE7_MORTAR_01']
    binding=read(SOURCE_QA/'candidate_v1/bindings.json')
    assert len(binding['rows'])==17
    alpha=[]
    for row in binding['rows']:
        for name in ['source','response','candidate']:
            assert sha(row[name])==row[name+'_sha256']; paths.add(row[name])
        assert response_master(LAB,inside(row['response']))==inside(row['source'])
        alpha.append(inspect_master(inside(row['source'])))
        assert np.array_equal(np.array(Image.open(inside(row['candidate']))),np.array(Image.open(inside(row['source'])).crop(row['box'])))
    for identity in ids:
        p=profiles[identity]; machine=p['machine_asset']; assert sha(machine['spec'])==machine['sha256']
        spec=read(machine['spec']); assert spec['enemy_id']==identity
        views=spec.get('views',{'ANCHORED':spec}); assert len(views)==(1 if 'MORTAR' in identity else 8)
        for direction,view in views.items():
            assert sha(view['texture'])==view['texture_sha256']; paths.add(view['texture'])
        paths.update([machine['spec'],p['master_asset']])
    runs=[]
    for number,folder,count in [(1,'operation1_verified',10),(2,'operation2_verified',7),(3,'operation3_layout2_r2',7)]:
        path=QA/folder/'full_operation.json'; r=read(path); result=r['result']
        assert r['status']=='PASS_TECHNICAL_PLAYTHROUGH' and not r['failures']
        assert result['outcome']=='EXTRACTED' and result['full_route_cleared']
        assert result['mission_id']==f'MIS_CH01_0{number}' and result['hostiles_defeated']==count
        assert result['ledger_recovered'] and result['field_supplies'] and result['carrier_fragment']
        current(r['tested_code_sha256']); paths.update(r['tested_code_sha256']); paths.add(path)
        runs.append({k:result[k] for k in ['mission_id','elapsed_seconds','hostiles_defeated','outcome']})
        m=read(f'data/missions/MIS_CH01_0{number}.json'); assert m['new_enemy_ids']==[ids[number-1]]
        active={row['enemy_id'] for room in m['main_route'] for row in room.get('encounter',[])}
        assert ids[number-1] in active
        assert all(later not in active for later in ids[number:])
    app=QA/'native_1789819637_225/check.json'; r=read(app)
    assert r['app_registry'] and r['status']=='PASS_TECHNICAL' and not r['failures']; current(r['sha256'])
    assert 'candidate_specs' not in r['sha256']
    images=[]
    for capture in r['captures']:
        assert sha(capture['image'])==capture['sha256']; images.append(inside(capture['image']))
    paths.update(r['sha256']); paths.add(app)
    native=ROOT/'qa/campaign_20260919/native_1789820340_95'
    c=read(native/'capture.json'); assert c['status']=='PASS_TECHNICAL' and not c['failures']; current(c['tested_sha256'])
    images.extend(inside(p) for p in c['captures']); paths.update(c['tested_sha256']); paths.add(native/'capture.json')
    for row in binding['rows']:
        stem=inside(row['source']).stem
        images.extend([SOURCE_QA/stem/'fit_1920x1080.png',SOURCE_QA/stem/'native_1920x1080.png'])
    images.extend(SOURCE_QA/'candidate_v1'/f'{name}_yaw8_1920x1080.png' for name in ['bulwark','ram'])
    for p in images: assert Image.open(p).size[0]>=1920 and Image.open(p).size[1]>=1080
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/art_pipeline/validate_visual_evidence_1080p.py'),*[str(p) for p in images],
        '--output',str(QA/'visual_validation.json')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    paths.update(images); paths.add(QA/'visual_validation.json')
    logs=[]
    for name in ['robots_roster_final','robots_reg_site7_drone_app_smoke','robots_reg_site7_anchor_app_smoke',
        'robots_reg_motion_lab_character_runtime_smoke','robots_reg_rook','robots_reg_cover_navigation',
        'robots_reg_cover_ai','robots_reg_machine_source','robots_reg_campaign_flow','robots_reg_cover_props','robots_reg_boss_guard']:
        path=ROOT/'qa/karchive_props_20260919'/(name+'.stdout.log'); value=path.read_text(encoding='utf-8')
        assert 'PASS' in value and 'FAIL' not in value and 'SCRIPT ERROR' not in value,name
        logs.append({'name':name,'exit_resource_warning':'resources still in use at exit' in value}); paths.add(path)
    paths.update(SOURCE_QA.glob('*_tool_response.json'))
    paths.update(SOURCE_QA.glob('*_request.json'))
    paths.update([QA/'RESULT_KO.md',QA/'staging_retirement.json',QA/'VISUAL_REVIEW.md',QA/'bundle_publication.json',SOURCE_QA/'selection.json',SOURCE_QA/'candidate_v1/bindings.json',
        ROOT/'data/art_profiles/site7_enemy_body_plan.json',ROOT/'.agents/skills/sable-character-studio/references/enemy-facing.md'])
    payload={'status':'LOCAL_APP_INTEGRATED_VERIFIED','new_archetypes':ids,'native_alpha_sources':len(alpha),'routes':runs,
        'app_fixture_checks':r['checks'],'native_review_images':len(images),'regressions':logs,
        'visual_review':'Implementing agent direct source/yaw/native scene inspection; not independent external review',
        'limitations':['Controlled capture positions are not human input playthroughs.','Tactics dt 30/60/120; collision and flight checked at native 60Hz.',
            'Existing exit resource warnings in drone/anchor/ROOK checks; operation2 also reported teardown resources. No script/runtime failure in selected checks.',
            'External GPT review, Luna reproduction and deployment were not performed.'],
        'sha256':{inside(p).relative_to(ROOT).as_posix():sha(p) for p in sorted(paths,key=str)}}
    manifest.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:payload[k] for k in ['status','routes','app_fixture_checks','native_review_images']},ensure_ascii=False))
if __name__=='__main__': main()
