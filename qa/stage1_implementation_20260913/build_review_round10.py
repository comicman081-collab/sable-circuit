"""Exact small R9-H01/H02 fix snapshot, only after complete local regression."""
from pathlib import Path
import json, hashlib, datetime
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
target=out/'gpt6pro_harness_review_round10.md'
if target.exists():raise FileExistsError(target)
log=(out/'r10_workflow_regression.stderr.log').read_text(encoding='utf-8',errors='replace')
if 'Ran 105 tests' not in log or '\nOK\n' not in log:raise RuntimeError('Actual full regression is not complete/pass')
files=['motion_lab_v1/character_workflow.py','motion_lab_v1/character_handoff.py',
       'motion_lab_v1/tests/test_reuse_improvements.py',
       '.agents/skills/sable-character-studio/references/reuse-improvements.md',
       'qa/stage1_implementation_20260913/r10_workflow_regression.stderr.log']
parts=['''# SABLE CIRCUIT Round 10 — only close R9-H01 / R9-H02

R8 boss capture fixes remain unchanged and closed. Please narrowly verify the two actual Python routing defects you reproduced in Round9, not a new architecture audit or art approval.

R9-H01: cycle_followup restricts itself to E/walk if that cycle is needs_cycle_review, stale_cycle_review or repair while all seven E source slots are approved. workflow_status still preserves explicit source repair and incomplete/unreviewed E sources first. Only after E whole-cycle approval do non-E cycle followups resume. Tests cover both pending/stale cases against competing SE repair, E source-art versus timing repair, plus existing approved-E/SE-repair positive controls.

R9-H02: common previewAffectedCycle AND prepareCycleReview commands now carry explicit --action from nextSource.action or its slot. Idle maps to walk. Tests execute the actual character_workflow.main argparse and dispatch with only cycle_preview.prepare artifact creation stubbed, so SE/run really reaches callback with run. Both cycle selection and walk/run/idle source-slot paths are checked. Command-string equality is additional, not the only proof.

Before the fix the new local reproducer showed expected SE/run callback but actual SE/walk; both E pending/stale combinations chose SE repair. The first draft fixture itself lacked a path field; that test-fixture error was corrected before obtaining the intended four failing assertions. No assertion was weakened to turn a wrong selection green. After the fix, the focused 26-test suite passed. Two scope-positive test methods were then added (E repair scope and slot action mapping), and the actual full 105-test run completed OK, attached below. The source-count and decoders are technical fixtures, not a Luna run or artistic result. Skill validation also returned Skill is valid.

Please state whether R9-H01/H02 original counterexamples are closed and whether these narrow changes regress their positive controls. Distinguish your actual execution from our supplied 105-test log. No sprites, recipes, movement speed, weapon numbers, gameplay registry or Godot boss code were changed for these two harness fixes. Separate SE source repair work continues and is NOT submitted for approval here.
'''];rows=[]
for name in files:
    data=(root/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
    rows.append({'path':name,'sha256':digest})
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n```text\n{data.decode("utf-8-sig",errors="replace")}\n```\n')
target.write_text(''.join(parts),encoding='utf-8')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,
          'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'externalReview':'NOT_YET_SUBMITTED'}
target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'path':str(target),'bytes':target.stat().st_size,**manifest}))
