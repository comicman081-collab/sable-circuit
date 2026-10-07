from pathlib import Path
import hashlib,json
root=Path.cwd()
out=root/'.cache/diag/expansion_item2_20261004/counter_double'
out.mkdir(parents=True,exist_ok=True)
source=(root/'scripts/missions/story_stage_01.gd').read_text(encoding='utf-8')
start=source.index('func _spawn_wave(')
end=source.index('\nfunc ',start+1)
fn=source[start:end]
line='        enemy.apply_run_modifiers(RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity))'
assert fn.count(line)==1
fn=fn.replace(line,line+'\n'+line)
prefix='res://.cache/diag/expansion_item2_20261004/counter_double/'
(out/'double_stage.gd').write_text('extends "res://scripts/missions/story_stage_01.gd"\n\n'+fn+'\n',encoding='utf-8')
scene=(root/'scenes/mission/StoryStage01.tscn').read_text(encoding='utf-8')
assert scene.count('res://scripts/missions/story_stage_01.gd')==1
(out/'DoubleStage.tscn').write_text(scene.replace('res://scripts/missions/story_stage_01.gd',prefix+'double_stage.gd'),encoding='utf-8')
test=(root/'tests/smoke/redline_smoke.gd').read_text(encoding='utf-8')
(out/'counter_smoke.gd').write_text(test.replace('res://scenes/mission/StoryStage01.tscn',prefix+'DoubleStage.tscn'),encoding='utf-8')
rows={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'double_stage.gd',out/'DoubleStage.tscn',out/'counter_smoke.gd']}
(out/'generation.json').write_text(json.dumps({'mutation':'Apply the identical run modifier twice at each real encounter spawn; original scene/test inherit all other runtime behavior. Expected: HP checks FAIL, not parse/runtime errors.','original_stage_sha256':hashlib.sha256((root/'scripts/missions/story_stage_01.gd').read_bytes()).hexdigest(),'original_test_sha256':hashlib.sha256((root/'tests/smoke/redline_smoke.gd').read_bytes()).hexdigest(),'sha256':rows},ensure_ascii=False,indent=2),encoding='utf-8')
