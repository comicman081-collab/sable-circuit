"""Export only the user-requested SABLE harness/skill sources for GPT review."""
from pathlib import Path
import hashlib
import json
import argparse

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    '.agents/skills/sable-character-studio/SKILL.md',
    '.agents/skills/sable-character-studio/references/authoring.md',
    '.agents/skills/sable-character-studio/references/gait-repair.md',
    '.agents/skills/sable-character-studio/references/cycle-review.md',
    '.agents/skills/sable-character-studio/references/aim-response.md',
    '.agents/skills/sable-character-studio/references/browser-check.md',
    '.agents/skills/sable-character-studio/references/reuse-improvements.md',
    'motion_lab_v1/character_workflow.py',
    'motion_lab_v1/cycle_review.py',
    'motion_lab_v1/gait_contract.py',
    'motion_lab_v1/intake_frame.py',
    'motion_lab_v1/intake_pair.py',
    'motion_lab_v1/intake_derived_frame.py',
    'motion_lab_v1/prepare_enemy_asset.py',
    'motion_lab_v1/public/combat-aim.js',
    'motion_lab_v1/public/atlas-renderer.js',
    'motion_lab_v1/tests/test_cycle_review.py',
    'motion_lab_v1/tests/test_character_workflow.py',
    'scripts/combat/site7_enemy_tactics.gd',
    'scripts/combat/site7_attack_warning.gd',
    'qa/stage1_implementation_20260913/full_operation.json',
]
intro = '''# SABLE CIRCUIT actual harness/skill review — 2026-09-13

The user requests review in their existing GPT 6 Pro chat while local development continues.
Review the actual code below; do not claim to have run it or inspected unseen images/videos.
Deliver prioritized concrete defects with file/function, failure example, minimal fix and regression test.
Focus on weaker-model misuse paths, false visual approvals, repeated wrong support-leg sources,
stale evidence, provenance binding, movement/aim clock separation, and fitting humanoid rules
to new drones/anchored machines/quadrupeds. Distinguish definite code bugs from possible risks.

Non-negotiable constraints: preserve accepted ASTER/MICA/ROOK art and gait; visible source art
is built-in ImageGen only. No anatomical raster warping or primitive character replacement.
UAL/Blender guides are pose-only. Failed art is retained, no false review receipts. Native visual
evidence is >=1920x1080 with actual normal-speed temporal observation, not just still containers.
No universal success guarantee, no claim of actual Luna reproduction without a real authorized run.
Use current Motion Studio, NOT the retired legacy production harness. Do not propose broad cleanup,
new external services, global model changes or deployment. Technical tests are not visual approval.

Observed production failures, NOT hypothetical:
* Old ASTER renderer froze walk/run at frame 5 and swapped in unrelated leg-warp art during fire.
* Prior ROOK had distinct source hashes but repeated the same anatomical support leg. Cycle review
  was added; source completeness and selected-frame diversity cannot prove natural walking.
* In today's rifle-enemy pilot, two ImageGen opposite-pose pairs repeated the right planted leg in
  both figures, despite phase text. They remain unapproved. Changed to one pose per image with
  the exact colored UAL phase guide FIRST and appearance reference SECOND; E1/E2 now visually
  show the requested alternating anatomical roles. The whole cycle is NOT approved yet.
* One requested transparent image returned RGB painted checkerboard: rejected and retained.
* Current prepare_enemy_asset.py creates isolated candidates, but its tool-response validation
  appears too weak: it checks tool/result existence without binding the exact source bytes.
* New NPC tactics own attacks; an old premium boss presentation also emitted volleys. Duplicate
  old emissions were disabled after the attached technical playthrough; rerun is still pending.

Stage 1 status: 6 route rooms +2 optional, 2 reinforcement encounters, 3-phase anchor boss,
real projectile/ammo/collision bot playthrough to extraction passed with 10 kills. The attached
receipt is technical only; enemy raster assets have NOT been promoted. No visual MVP claim.

Please return (1) blocking defects, (2) minimal implementation/skill patches, (3) useful negative
tests, (4) explicit limits requiring human/observed visual judgment. Avoid generic praise or a
brand-new framework. We will apply justified changes and return actual regression results.
'''
parser = argparse.ArgumentParser()
parser.add_argument('--round', type=int, default=1)
parser.add_argument('--intro')
args = parser.parse_args()
if args.intro:
    intro = (ROOT / args.intro).read_text(encoding='utf-8')
if args.round >= 4:
    FILES += ['motion_lab_v1/source_provenance.py', 'motion_lab_v1/cycle_preview.py',
              'motion_lab_v1/cycle_live_review.js', 'motion_lab_v1/tests/test_enemy_asset_provenance.py',
              'motion_lab_v1/tests/test_reuse_improvements.py', 'motion_lab_v1/build_atlas.py']
if args.round >= 5:
    FILES = ['motion_lab_v1/cycle_review.py','motion_lab_v1/source_provenance.py',
             'motion_lab_v1/tests/test_cycle_review.py','motion_lab_v1/tests/test_enemy_asset_provenance.py',
             'motion_lab_v1/character_workflow.py','motion_lab_v1/build_atlas.py',
             'motion_lab_v1/gait_contract.py','motion_lab_v1/prepare_enemy_asset.py']
if args.round >= 6:
    FILES = ['scripts/animation/site7_machine_sprite.gd','scripts/actors/enemy_actor.gd',
             'scripts/combat/site7_enemy_tactics.gd','scripts/animation/premium_enemy_presentation.gd',
             'tests/smoke/site7_enemy_facing_smoke.gd','tests/smoke/site7_machine_source_smoke.gd',
             '.agents/skills/sable-character-studio/references/enemy-facing.md',
             'motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json']
if args.round >= 7:
    FILES += ['tests/render/site7_machine_edge_case_smoke.gd',
              'motion_lab_v1/qa/stage1_enemies_20260913/build_machine_edge_fixtures.py',
              'tests/render/site7_enemy_facing_capture.gd']
parts = [intro]
bindings = []
for name in FILES:
    path = ROOT / name
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    bindings.append({'path': name, 'sha256': digest, 'bytes': len(data)})
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n\n```text\n{data.decode("utf-8-sig")}\n```\n')
out = Path(__file__).parent / f'gpt6pro_harness_review_round{args.round}.md'
if out.exists():
    raise ValueError('Review snapshots are immutable; use a new round')
out.write_text(''.join(parts), encoding='utf-8')
out.with_suffix('.manifest.json').write_text(json.dumps({'files': bindings, 'packetSHA256': hashlib.sha256(out.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
print(out)
print(out.stat().st_size)
