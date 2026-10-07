from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
FILES=[
 'motion_lab_v1/prepare_enemy_asset.py','motion_lab_v1/intake_derived_frame.py',
 'motion_lab_v1/character_workflow.py','motion_lab_v1/cycle_review.py',
 'motion_lab_v1/public/qa/combat-checks.js','motion_lab_v1/public/simulation.js',
 'scripts/combat/site7_enemy_tactics.gd','scripts/combat/site7_attack_warning.gd',
 'scripts/animation/site7_machine_sprite.gd','tests/smoke/site7_attack_geometry_smoke.gd',
 'motion_lab_v1/tests/test_cycle_review.py','motion_lab_v1/tests/test_character_workflow.py',
 '.agents/skills/sable-character-studio/SKILL.md',
 '.agents/skills/sable-character-studio/references/gait-repair.md',
 '.agents/skills/sable-character-studio/references/aim-response.md']
parts=[(OUT/'review_followup_round2.md').read_text(encoding='utf-8')];rows=[]
for name in FILES:
 data=(ROOT/name).read_bytes();sha=hashlib.sha256(data).hexdigest()
 parts.append(f'\n## FILE: {name}\nSHA256: {sha}\n```text\n{data.decode("utf-8-sig")}\n```\n')
 rows.append({'path':name,'sha256':sha})
target=OUT/'gpt6pro_harness_review_round2.md'
target.write_text(''.join(parts),encoding='utf-8')
target.with_suffix('.manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(str(target));print(target.stat().st_size)
