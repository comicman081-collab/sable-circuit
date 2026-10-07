from pathlib import Path
import subprocess, json, os, hashlib

root = Path.cwd()
folder = root / '.cache/diag/expansion_item3_20261006/weapon_controls'
folder.mkdir(parents=True, exist_ok=True)
godot = r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe'
os.environ['TEMP'] = os.environ['TMP'] = str(root / '.cache/tmp')
source = (root / 'scripts/actors/operator_actor.gd').read_text(encoding='utf-8')
test = (root / 'tests/smoke/weapon_expansion_smoke.gd').read_text(encoding='utf-8')
block = 'func _spawn_projectile' + source.split('func _spawn_projectile')[1].split('\n## Only')[0]
rows = []
for weapon in ['WPN_DMR_RAIL_01', 'WPN_SHOTGUN_NULL_01']:
    d = folder / weapon
    d.mkdir(exist_ok=True)
    rel = 'res://' + d.relative_to(root).as_posix()
    changed = 'extends "res://scripts/actors/operator_actor.gd"\n' + block
    changed += '    if equipped_weapon_id == "' + weapon + '": projectile.damage = 0.0\n'
    (d / 'actor.gd').write_text(changed, encoding='utf-8')
    insertion = '''        var identity := [actor.operator_id, actor.display_name, actor.accent_color]
        actor.set_script(load("''' + rel + '''/actor.gd"))
        actor._visual = actor.get_node("VisualRoot")
        actor.configure(identity[0], identity[1], identity[2])
'''
    case = test.replace('    for actor: OperatorActor in squad.operators:\n', '    for actor: OperatorActor in squad.operators:\n' + insertion, 1)
    (d / 'test.gd').write_text(case, encoding='utf-8')
    run = subprocess.run([godot, '--headless', '--path', str(root), '--log-file', str(d/'godot.log'), '-s', rel+'/test.gd', '--', '--out='+rel+'/measurement.json'], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
    (d/'stdout.log').write_text(run.stdout+run.stderr, encoding='utf-8')
    assert run.returncode == 1 and 'WEAPON_EXPANSION_SMOKE: FAIL' in run.stdout and 'Parse Error' not in run.stderr, (weapon, run.stdout, run.stderr)
    result = json.loads((d/'measurement.json').read_text(encoding='utf-8'))
    assert any('actual impact applies exact weapon damage' in item for item in result['failures']), result
    rows.append(dict(weapon=weapon, mutation='damage_hook_disabled', failed_checks=len(result['failures']), exit=run.returncode, actor_sha256=hashlib.sha256(changed.encode()).hexdigest()))
(folder/'summary.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print(json.dumps(rows))
