from pathlib import Path
import subprocess, json, hashlib

root = Path.cwd()
base = '453d20cb'
def old(path):
    return subprocess.check_output(['git','show',f'{base}:{path}'], cwd=root)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def current(path):
    return (root/path).read_bytes()
protected = ['assets','art_src','motion_lab_v1','data/missions','data/story','data/progression/upgrades.json','data/art_profiles/enemy_profiles.json','scripts/core/game_flow.gd','scripts/core/run_contract.gd','scripts/vfx/vfx_painter.gd','scripts/actors/enemy_actor.gd','scripts/combat/site7_enemy_tactics.gd']
changed = subprocess.check_output(['git','diff',base,'--name-only','--',*protected],cwd=root).decode('utf-8').splitlines()
assert not changed, changed
# Names are taken from the runner; do not manufacture a check for a missing path.
runner=(root/'tools/maintenance/run_regression_suite.py').read_text(encoding='utf-8')
import re
mapping=dict(re.findall(r"Test\('([^']+)', '([^']+)'",runner))
ids=['upgrade_economy','m10_base_ui','m10_intel','campaign','boss_registry','boss_pattern','boss_duel','boss_room_fairness','robot_roster']
unchanged_tests=[mapping[key] for key in ids]
test_hashes={}
for path in unchanged_tests:
    assert old(path).replace(b'\r\n',b'\n')==current(path).replace(b'\r\n',b'\n'),path
    test_hashes[path]=sha(old(path))
catalogs={}
for path,key,count in [('data/progression/intel_discoveries.json','discoveries',3),('data/progression/weapons.json','weapons',6)]:
    previous=json.loads(old(path)); present=json.loads(current(path))
    # The analysis collection is actually named analyses in the source table.
    if key not in previous:key=next(k for k,v in previous.items() if isinstance(v,list))
    assert present[key][:count]==previous[key]
    catalogs[path]={'old_rows':count,'new_rows':len(present[key]),'old_rows_exact':True}
writer=subprocess.check_output(['git','rev-parse','381ef0fb:scripts/core/campaign_progression.gd'],cwd=root).decode().strip()
baseline_writer=subprocess.check_output(['git','rev-parse',f'{base}:scripts/core/campaign_progression.gd'],cwd=root).decode().strip()
assert writer==baseline_writer
result={'baseline':base,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),'protected_changes':changed,'unchanged_test_git_blob_sha256':test_hashes,'catalogs':catalogs,'v5_writer_git_blob':writer,'v5_fixture_sha256':sha(current('tests/fixtures/run_contract/save_v5.json'))}
path=root/'.cache/diag/expansion_item3_20261006/scope_audit.json'
path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
