"""Bind the three real route runs, isolated save tests and native captures.

Does not generate/alter art or production data. All output is project-local.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--native', required=True)
parser.add_argument('--flow', required=True)
args = parser.parse_args()
qa = ROOT / 'qa/campaign_20260919'

def inside(path):
    value = (ROOT / str(path).removeprefix('res://')).resolve()
    value.relative_to(ROOT)
    return value

def read(path):
    return json.loads(inside(path).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(inside(path).read_bytes()).hexdigest()

def check_bindings(rows):
    for path, expected in rows.items():
        assert sha(path) == expected, f'Stale evidence: {path}'

routes = []
proofs = []
for number, count in [(1, 10), (2, 7), (3, 7)]:
    path = f'qa/campaign_20260919/op{number}_final/full_operation.json'
    report = read(path)
    result = report['result']
    assert report['status'] == 'PASS_TECHNICAL_PLAYTHROUGH' and not report['failures']
    assert result['mission_id'] == f'MIS_CH01_0{number}'
    assert result['outcome'] == 'EXTRACTED' and result['full_route_cleared']
    assert result['field_supplies'] and result['carrier_fragment'] and result['ledger_recovered']
    assert result['hostiles_defeated'] == count
    check_bindings(report['tested_code_sha256'])
    routes.append({k: result[k] for k in ['mission_id','hostiles_defeated','elapsed_seconds','secured_research','secured_salvage','secured_fragments','secured_intel']})
    proofs.append(path)

native = read(args.native + '/capture.json')
assert native['status'] == 'PASS_TECHNICAL' and not native['failures']
check_bindings(native['tested_sha256'])
visual = read(args.native + '/visual_validation.json')
assert visual['gate'] == 'PASS' and len(visual['evidence']) == 12
for evidence in visual['evidence']:
    assert sha(evidence['path']) == evidence['sha256']
flow = read(args.flow + '/check.json')
assert flow['status'] == 'PASS' and not flow['failures']
proofs += [args.native+'/capture.json', args.native+'/visual_validation.json', args.flow+'/check.json']

regressions = []
for test in ['m2_story_flow_smoke','m10_intel_loadout_smoke','m10_base_ui_action_smoke','m11_run_contract_smoke','m12_squad_revive_smoke','m13_weapon_campaign_smoke','m13_weapon_loadout_smoke','m13_weapon_runtime_smoke','site7_battle_flow_smoke','m10_persistence_smoke','m13_weapon_base_migration_smoke']:
    revision = 3 if test in ['m11_run_contract_smoke','m13_weapon_loadout_smoke','m13_weapon_base_migration_smoke'] else 2
    log = f'qa/karchive_props_20260919/campaign_reg{revision}_{test}.log'
    text = inside(log).read_text(encoding='utf-8')
    assert ': PASS' in text and 'FAIL' not in text and 'SCRIPT ERROR' not in text, log
    regressions.append({'test':test,'log':log,'checks':text.count('PASS: '),'test_sha256':sha('tests/smoke/'+test+'.gd')})
    proofs.append(log)

runtime = ['scripts/core/game_flow.gd','scripts/core/site7_campaign.gd','scripts/core/campaign_progression.gd','scripts/ui/base_lobby.gd','scripts/ui/briefing_screen.gd','scripts/ui/mission_results.gd','scripts/missions/story_stage_01.gd','data/story/site7_campaign.json','data/progression/intel_discoveries.json','data/art_profiles/playable_profiles.json','data/visual/site7_environment_props.json','scripts/combat/cover_navigation.gd','scripts/missions/site7_environment_props.gd','scripts/missions/site7_environment_prop.gd']
runtime += [f'data/missions/MIS_CH01_0{i}.json' for i in [1,2,3]]
manifest = {'status':'PASS_SCOPED_CAMPAIGN_INTEGRATION','recorded_utc':datetime.now(timezone.utc).isoformat(),
            'routes':routes,'flow_checks':flow['checks'],'native_checks':native['checks'],
            'native_resolution':[1920,1080],'captures':native['captures'],'regressions':regressions,
            'runtime_sha256':{p:sha(p) for p in runtime},'evidence_sha256':{p:sha(p) for p in proofs},
            'scope':['three standalone technical full-route bots with real cooldown/damage/revive/interactions',
                     'campaign/save/UI transaction fixtures separately tested','native 1080p UI + six encounter fixtures'],
            'not_claimed':['full game completion','new robot artwork approval','Luna reproduction','GPT web review','human playtest','performance benchmark','deployment'],
            'legacy_failures_retained':True,'actual_player_save_touched':False}
destination = qa/'delivery_manifest.json'
destination.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':manifest['status'],'routes':routes,'flow_checks':flow['checks'],'native_checks':native['checks'],'regression_suites':len(regressions),'regression_checks':sum(x['checks'] for x in regressions)},ensure_ascii=False))
