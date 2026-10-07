from pathlib import Path
import subprocess,json,os
root=Path.cwd(); folder=root/'.cache/diag/expansion_item3_20261006/module_controls'; folder.mkdir(parents=True,exist_ok=True)
godot=r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
os.environ['TEMP']=os.environ['TMP']=str(root/'.cache/tmp')
source=(root/'scripts/combat/operator_skill_controller.gd').read_text(encoding='utf-8')
test=(root/'tests/smoke/module_expansion_smoke.gd').read_text(encoding='utf-8'); rows=[]
cases={'SPORE_FILTER':['_bulwark_duration'],'FROST_LENS':['_q_cooldown'],'RAIL_SPOOL':['_e_cooldown','_dash_distance'],'ECHO_RELAY':['_relay_duration'],'NULL_ANCHOR':['_scatter_duration']}
for module,functions in cases.items():
    d=folder/module; d.mkdir(exist_ok=True); rel='res://'+d.relative_to(root).as_posix()
    changed='extends "res://scripts/combat/operator_skill_controller.gd"\n'
    for fn in functions:
        block='func '+fn+source.split('func '+fn)[1].split('\nfunc ')[0]
        block=block.replace('actor.has_module("MOD_'+module+'")','false')
        changed+=block+'\n'
    (d/'controller.gd').write_text(changed,encoding='utf-8')
    insert='        var controller := actor.get_node("SkillController")\n        controller.set_script(load("'+rel+'/controller.gd"))\n        controller.actor = actor; controller.squad = squad\n'
    case=test.replace('        actor.get_node("SkillController").set_process(false)\n','        actor.get_node("SkillController").set_process(false)\n'+insert)
    (d/'test.gd').write_text(case,encoding='utf-8')
    run=subprocess.run([godot,'--headless','--path',str(root),'--log-file',str(d/'godot.log'),'-s',rel+'/test.gd','--','--out='+rel+'/measurement.json'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    (d/'stdout.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    assert run.returncode==1 and 'MODULE_EXPANSION_SMOKE: FAIL' in run.stdout and 'Parse Error' not in run.stderr,(module,run.stdout,run.stderr)
    result=json.loads((d/'measurement.json').read_text(encoding='utf-8'))
    rows.append(dict(module=module,failed_checks=len(result['failures']),exit=run.returncode))
(folder/'summary.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
