#!/usr/bin/env python
"""Claude review instrument: break one rule at a time on the scratch 'after' snapshot and
see which regression test notices. Never touches the repository tree.

usage: mutate.py [--only id,id] [--list]
Every mutation is (id, file, [(old, new), ...], [test scripts that SHOULD fail]).
The file is restored from git after each run (git show a6eb1d35:<file>).
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # repository root
PROJ = ROOT / '.cache' / 'claude_scratch' / 'proj_after'
GODOT = Path(r'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe')
COMMIT = 'a6eb1d35'
OUT = ROOT / '.cache' / 'claude_scratch' / 'item1_review' / 'mutations'

T_ELITE = 'tests/smoke/elite_expansion_smoke.gd'
T_ELITE_OLD = 'tests/smoke/elite_affix_smoke.gd'
T_HAZ = 'tests/smoke/hazard_expansion_smoke.gd'
T_ZONE = 'tests/smoke/zone_hazard_smoke.gd'

EL = 'scripts/combat/elite_affix.gd'
ZH = 'scripts/combat/zone_hazard.gd'
ST = 'scripts/missions/story_stage_01.gd'
OP = 'scripts/actors/operator_actor.gd'
EN = 'scripts/actors/enemy_actor.gd'
BF = 'scripts/missions/site7_battlefield.gd'
AJ = 'data/progression/elite_affixes.json'
HJ = 'data/progression/zone_hazards.json'

MUTATIONS = [
    ('boss_accepts_affix', EL, [("if enemy.enemy_id.begins_with(\"BOSS_\") or enemy.brood_generation > 0:", "if enemy.brood_generation > 0:")], [T_ELITE]),
    ('beacon_protects_itself', EL, [("source == enemy or source.health <= 0.0", "source.health <= 0.0")], [T_ELITE]),
    ('beacon_cap_removed_data_0_5', AJ, [("\"beacon_reduction\": 0.25", "\"beacon_reduction\": 0.5")], [T_ELITE]),
    ('brood_three_babies', ST, [("brood_spawn_points(parent_enemy, 2)", "brood_spawn_points(parent_enemy, 3)"), ("if points.size() != 2:", "if points.size() != 3:"), ("for index in range(2):\n        var child := ENEMY_SCENE", "for index in range(3):\n        var child := ENEMY_SCENE")], [T_ELITE]),
    ('hatch_short_0_2', ST, [("child.brood_hatch_duration = maxf(0.6, float(spec.get(\"brood_hatch_windup\", 0.6)))", "child.brood_hatch_duration = 0.2")], [T_ELITE]),
    ('hatchling_fires_during_hatch', EN, [("if brood_hatch_left > 0.0: return\n    if not dir.is_finite()", "if not dir.is_finite()"), ("if brood_hatch_left > 0.0 or _attack_cd > 0.0", "if _attack_cd > 0.0")], [T_ELITE]),
    ('spore_damage_in_warning', ZH, [("if phase == Phase.DISCHARGE and str(spec.get(\"mode\", \"burst\")) == \"continuous\": _continuous_damage(step)", "if phase != Phase.IDLE and str(spec.get(\"mode\", \"burst\")) == \"continuous\": _continuous_damage(step)")], [T_HAZ]),
    ('spore_source_unattributed', ZH, [("actor.apply_damage(float(spec.get(\"operator_dps\", 0.0)) * delta, \"HAZARD_\" + hazard_id)", "actor.apply_damage(float(spec.get(\"operator_dps\", 0.0)) * delta, \"HAZARD\")")], [T_HAZ]),
    ('spore_warning_0_8', HJ, [("\"telegraph\": 1.2,\n      \"discharge\": 3.0", "\"telegraph\": 0.8,\n      \"discharge\": 3.0")], [T_HAZ]),
    ('frost_cleanup_leaks', ST, [("if node.has_method(\"release_effects\"): node.release_effects()", "pass")], [T_HAZ]),
    ('dash_compounds_frost', OP, [("requested_velocity=_dash_requested_velocity*hazard_factor", "requested_velocity=velocity*hazard_factor")], [T_HAZ]),
    ('hazards_not_spread', BF, [("if point.distance_to(placed) < radius * 2.6: spread = false; break", "if point.distance_to(placed) < radius * 0.5: spread = false; break"), ("if point.distance_to(other.point as Vector2) < maxf(radius, float(other.radius)) * 2.6: spread = false; break", "if point.distance_to(other.point as Vector2) < 10.0: spread = false; break")], [T_HAZ, T_ZONE]),
    ('affix_tints_actor_modulate', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    (get_parent() as CanvasItem).modulate = Color(0.7, 1.0, 0.7)")], [T_ELITE]),
    ('affix_tints_sprite_modulate', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    for s in get_parent().find_children(\"*\", \"Sprite2D\", true, false): (s as Sprite2D).modulate = Color(0.7, 1.0, 0.7)")], [T_ELITE]),
    # Added for the B-1 re-check (run after Codex widens the contract to the whole ancestor chain).
    ('affix_tints_visual_root', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    var hv := get_parent().get_node_or_null(\"HighResVisualRoot\")\n    if hv is CanvasItem: (hv as CanvasItem).modulate = Color(0.7, 1.0, 0.7)")], [T_ELITE]),
    ('affix_tints_sprite_self_modulate', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    for s in get_parent().find_children(\"*\", \"Sprite2D\", true, false): (s as Sprite2D).self_modulate = Color(0.7, 1.0, 0.7)")], [T_ELITE]),
    ('affix_tints_actor_self_modulate', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    (get_parent() as CanvasItem).self_modulate = Color(0.7, 1.0, 0.7)")], [T_ELITE]),
    ('affix_clears_sprite_material', EL, [("    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")", "    if affix_id == \"BEACON\": add_to_group(\"elite_beacons\")\n    for s in get_parent().find_children(\"*\", \"Sprite2D\", true, false): (s as Sprite2D).material = null")], [T_ELITE]),
]


def git_text(rel: str) -> str:
    return subprocess.run(['git', 'show', f'{COMMIT}:{rel}'], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')


def run_test(script: str, timeout=240) -> tuple[int, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    out_json = 'res://.cache/mut_report.json'
    cmd = [str(GODOT), '--headless', '--path', str(PROJ), '-s', 'res://' + script, '--', '--out=' + out_json]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=PROJ, capture_output=True, timeout=timeout)
        text = (p.stdout + p.stderr).decode('utf-8', 'replace')
        code = p.returncode
    except subprocess.TimeoutExpired as e:
        text = 'TIMEOUT ' + ((e.stdout or b'') + (e.stderr or b'')).decode('utf-8', 'replace')
        code = 124
    summary = ''
    for line in text.splitlines():
        if re.search(r'(SMOKE|PASS|FAIL).*\(\d+ checks', line) or line.startswith('FAIL:'):
            if line.startswith('FAIL:'):
                summary += (line[:140] + ' | ') if summary.count('|') < 3 else ''
            else:
                summary = line.strip()[:160] + ' || ' + summary
    return code, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--baseline', action='store_true', help='run the unmutated tests first')
    args = ap.parse_args()
    only = set(args.only.split(',')) if args.only else None
    if args.list:
        for m in MUTATIONS: print(m[0], m[1], '->', m[3])
        return
    results = []
    if args.baseline:
        for t in (T_ELITE, T_HAZ, T_ELITE_OLD, T_ZONE):
            code, summary = run_test(t)
            print('BASELINE', t, 'exit', code, summary, flush=True)
            results.append({'mutation': 'NONE', 'test': t, 'exit': code, 'summary': summary})
    for mid, rel, edits, tests in MUTATIONS:
        if only and mid not in only: continue
        target = PROJ / rel
        original = git_text(rel)
        mutated = original
        for old, new in edits:
            if old not in mutated:
                print(f'SKIP {mid}: pattern not found in {rel}: {old[:60]!r}', flush=True)
                mutated = None
                break
            mutated = mutated.replace(old, new, 1)
        if mutated is None or mutated == original:
            results.append({'mutation': mid, 'status': 'PATTERN_MISSING'})
            continue
        target.write_bytes(mutated.encode('utf-8'))
        try:
            for t in tests:
                code, summary = run_test(t)
                verdict = 'CAUGHT' if code != 0 else 'MISSED'
                print(f'{mid:34s} {t.split("/")[-1]:34s} exit={code:<4d} {verdict}  {summary[:200]}', flush=True)
                results.append({'mutation': mid, 'test': t, 'exit': code, 'verdict': verdict, 'summary': summary})
        finally:
            target.write_bytes(original.encode('utf-8'))
    (OUT / 'results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    missed = [r for r in results if r.get('verdict') == 'MISSED']
    print('MISSED:', [(r['mutation'], r['test']) for r in missed])


if __name__ == '__main__':
    main()
