"""Freeze the actual changed enemy integration and source-review instructions."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
FILES = [
    '.agents/skills/sable-character-studio/SKILL.md',
    '.agents/skills/sable-character-studio/references/authoring.md',
    '.agents/skills/sable-character-studio/references/enemy-facing.md',
    '.agents/skills/sable-character-studio/references/cycle-review.md',
    'motion_lab_v1/prepare_slot_review.py',
    'motion_lab_v1/character_workflow.py',
    'motion_lab_v1/qa/site7_rifle/source_reviews.json',
    'scripts/animation/site7_machine_sprite.gd',
    'scripts/actors/enemy_actor.gd',
    'scripts/combat/site7_enemy_tactics.gd',
    'scripts/combat/site7_attack_warning.gd',
    'scripts/ui/enemy_overhead_ui.gd',
    'data/art_profiles/enemy_profiles.json',
    'assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json',
    'tests/smoke/site7_anchor_app_smoke.gd',
    'tests/smoke/site7_drone_app_smoke.gd',
    'tests/smoke/site7_machine_source_smoke.gd',
    'tests/render/site7_anchor_candidate_capture.gd',
    'qa/stage1_implementation_20260913/ANCHOR_APP_CHECK_KO.md',
]
target = OUT / 'gpt6pro_harness_review_round8.md'
if target.exists():
    raise FileExistsError('Previously submitted snapshots stay immutable')
parts = [(OUT / 'review_followup_round8.md').read_text(encoding='utf-8')]
rows = []
for name in FILES:
    data = (ROOT / name).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n```text\n{data.decode("utf-8-sig")}\n```\n')
    rows.append({'path': name, 'sha256': digest})
target.write_text(''.join(parts), encoding='utf-8')
target.with_suffix('.manifest.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print(json.dumps({'path': str(target), 'bytes': target.stat().st_size, 'files': len(rows)}))
