"""Freeze actual R8 fixes and evidence; never invent an external review reply."""
from pathlib import Path
import hashlib, json, datetime

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
FILES=[
    'tests/render/site7_anchor_candidate_capture.gd',
    'tests/render/site7_anchor_capture_smoke.gd',
    'qa/stage1_implementation_20260913/r8_fixtures/no_warning_tactics.gd',
    'qa/stage1_implementation_20260913/r8_fixtures/malformed_spec.json',
    'scripts/combat/site7_enemy_tactics.gd',
    'scripts/combat/site7_attack_warning.gd',
    'scripts/animation/site7_machine_sprite.gd',
    'motion_lab_v1/character_workflow.py',
    'motion_lab_v1/character_handoff.py',
    'motion_lab_v1/tests/test_reuse_improvements.py',
    '.agents/skills/sable-character-studio/references/reuse-improvements.md',
    '.agents/skills/sable-character-studio/references/enemy-facing.md',
    'qa/stage1_implementation_20260913/anchor_capture_edges_1789292477_647/report.json',
    'qa/stage1_implementation_20260913/anchor_native_1789292550_916/capture_report.json',
    'qa/stage1_implementation_20260913/r8_captures_native_1080p.json',
    'qa/stage1_implementation_20260913/r9_workflow_regression_v2.stderr.log',
]
target=OUT/'gpt6pro_harness_review_round9.md'
if target.exists():raise FileExistsError('Submitted snapshots remain immutable')
log=(OUT/'r9_workflow_regression_v2.stderr.log').read_text(encoding='utf-8',errors='replace')
if '\nOK\n' not in log or 'Ran 101 tests' not in log:
    raise RuntimeError('Wait for the actual complete 101-test run; do not snapshot a partial pass')
header='''# SABLE CIRCUIT Round 9 — narrow re-review of actual R8 fixes

Please verify the attached current code for R8-01/02/03 and the additional real resume-routing regression below. Do not repeat a general architecture audit or infer art/MVP completion. Reply with defect IDs, exact evidence, small actionable fixes, and separate code review from supplied runtime evidence. The intentionally malformed JSON and no-warning tactics subclass are test-only negative fixtures, never runtime registry inputs.

R8-01: Capture now checks actual source-owned warning nodes: phase 2 one circle; phase 3 one circle plus four lanes. It checks visible/fired/elapsed/windup state and bounds polling to the actual fired window; captures include real HP before/after. The new real Godot test forces a no-warning attack that still enters RECOVER with zero projectiles; the new predicate rejects it. Tests run warning clocks at 30/60/120 Hz.

R8-02: Actual machine Sprite2D.is_visible_in_tree plus global_transform_with_canvas emitter-in-viewport checks. Test hides the sprite, hides an ancestor, and moves it offscreen; restores a real visible baseline. No mock predicate bypass.

R8-03: Normal --app-registry capture does not read candidate JSON at all, even if an explicit --candidate-spec path is missing or malformed. Candidate mode requires existing parseable Dictionary JSON. Captured spec hashes are taken from the actually selected actor profile. Full normal-app capture succeeded with an intentionally missing candidate argument, candidate_input_read=false.

Actual validation: Godot capture-edge smoke PASS 52 checks; native normal-app capture PASS_CAPTURE_ONLY, 22 WebP images at 1920x1080; native validator 24 containers passed (including hidden/visible negative-test PNG evidence). Main agent viewed phase 2 warning, phase 2 impact, phase 3 impact. Phase2 HP96->76, phase3 HP96->56, with actual fired warnings. A first fixture run failed two onscreen positives because a fixture position was assigned after _ready; this fixture was corrected to spawn at its real home BEFORE insertion, and the failed evidence is retained. No combat gameplay speeds, damage, player art, or registry pointers changed in this fix batch.

Additional actual harness defect: after a non-E whole-cycle source rejection, old handoff requested a missing unrelated direction, ignoring SE/walk/3..5 that were still rejected by cycle evidence although isolated source reviews were approved. cycle_followup now selects those exact failed slots first and queues completed but unreviewed cycles before new directions. Non-art rejection requests review/repair of that mechanism, not new artwork. Explicit source rejection and incomplete/unreviewed E pilot retain priority. The full initial run caught a pilot priority regression; it was fixed without weakening the existing test. Current complete re-run is 101 tests OK. This is technical fixture evidence, not a Luna character-generation run.

SE 3/4/5 whole-cycle weapon/torso projection repair is ongoing, not approved. The prior two-leg isolated source fix is not being called a whole-cycle PASS. Other enemy assets remain incomplete. No delivery, deployment, blanket quality approval, or claimed Luna end-to-end success is requested.
'''
parts=[header];rows=[]
for name in FILES:
    data=(ROOT/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n```text\n{data.decode("utf-8-sig",errors="replace")}\n```\n')
    rows.append({'path':name,'sha256':digest})
target.write_text(''.join(parts),encoding='utf-8')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,
          'packageSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'externalReviewStatus':'NOT_YET_SUBMITTED'}
target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'path':str(target),'files':len(rows),'bytes':target.stat().st_size,**manifest}))
