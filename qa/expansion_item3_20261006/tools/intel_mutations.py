from pathlib import Path
import subprocess,json,hashlib,os
root=Path.cwd(); folder=root/'.cache/diag/expansion_item3_20261006/intel_controls'; folder.mkdir(parents=True,exist_ok=True)
godot=r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
os.environ['TEMP']=os.environ['TMP']=str(root/'.cache/tmp')
helper=(root/'scripts/core/intel_samples.gd').read_text(encoding='utf-8').replace('class_name IntelSamples\n','')
test=(root/'tests/smoke/intel_supply_smoke.gd').read_text(encoding='utf-8')
award=(root/'scripts/missions/story_stage_01.gd').read_text(encoding='utf-8').split('func _award_enemy_intel')[1].split('\nfunc ')[0]
rows=[]
for name in ['generic_boss_first','missing_origin_key']:
    d=folder/name; d.mkdir(exist_ok=True)
    changed=helper.replace('    if id == "BOSS_SITE7_AERATOR_01":','    if "BOSS" in id: return "ANCHOR"\n    if id == "BOSS_SITE7_AERATOR_01":') if name=='generic_boss_first' else helper.replace(', "ORIGIN"]',']').replace(', "ORG"]',']')
    (d/'intel.gd').write_text(changed,encoding='utf-8')
    rel='res://'+d.relative_to(root).as_posix()
    (d/'stage.gd').write_text('extends "res://scripts/missions/story_stage_01.gd"\nconst MutantIntel := preload("'+rel+'/intel.gd")\nfunc _award_enemy_intel'+award.replace('IntelSamples.enemy_key','MutantIntel.enemy_key')+'\n',encoding='utf-8')
    case=test.replace('res://scripts/core/intel_samples.gd',rel+'/intel.gd').replace('var stage := StoryStage01.new()','var stage: StoryStage01 = load("'+rel+'/stage.gd").new()')
    (d/'test.gd').write_text(case,encoding='utf-8')
    run=subprocess.run([godot,'--headless','--path',str(root),'--log-file',str(d/'godot.log'),'-s',rel+'/test.gd','--','--out='+rel+'/measurement.json'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    (d/'stdout.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    assert run.returncode==1 and 'INTEL_SUPPLY_SMOKE: FAIL' in run.stdout and 'Parse Error' not in run.stderr,(name,run.stdout,run.stderr)
    evidence=json.loads((d/'measurement.json').read_text(encoding='utf-8'))
    rows.append(dict(mutation=name,exit=run.returncode,failed_checks=len(evidence['failures']),helper_sha256=hashlib.sha256(changed.encode()).hexdigest()))
(folder/'summary.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
