"""Freeze the new candidate-only enemy biped bridge and actual local checks."""
from pathlib import Path
import datetime, hashlib, json
root=Path(__file__).resolve().parents[2]
out=Path(__file__).parent
target=out/'gpt6pro_harness_review_round11.md'
if target.exists(): raise FileExistsError(target)
report_path='qa/stage1_implementation_20260913/biped_bridge_1789296751_766/report.json'
report=json.loads((root/report_path).read_text(encoding='utf-8'))
if report['status']!='PASS' or report['checks']!=824 or report['failures']: raise RuntimeError('Actual bridge regression not complete/pass')
for name,digest in report['sha256'].items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest: raise RuntimeError('Stale current report: '+name)
files=['scripts/animation/site7_biped_sprite.gd','scripts/actors/enemy_actor.gd',
       'scripts/combat/site7_enemy_tactics.gd','scripts/ui/enemy_overhead_ui.gd',
       'tests/smoke/site7_biped_bridge_smoke.gd',
       '.agents/skills/sable-character-studio/references/enemy-facing.md',
       'data/art_profiles/enemy_profiles.json',report_path,
       'qa/stage1_implementation_20260913/biped_bridge_final.stdout.log',
       'qa/stage1_implementation_20260913/biped_bridge_final.stderr.log']
parts=['''# Round11: new candidate-only authored enemy biped bridge

Round10 H01/H02 closure is accepted; no request to reopen those Python fixes or R8 capture fixes. This is a separate concrete implementation batch. Please review only the new Godot biped bridge, its EnemyActor hooks and biped HUD branch, test coverage and the appended skill instructions for reproducible correctness defects. No new framework or full art approval is requested.

Rifle source art is STILL incomplete/rejected in SE. No biped_asset is present in the attached production registry. This implementation does NOT promote those images. Existing E cycle/source approval, other sources and the accepted three playable characters remain untouched. The shared EnemyActor now supports explicit candidate intake and a separate future reviewed spec binding. The unmodified Tactics controller remains sole AI/shot owner; no player stats or Studio weapon cadence is copied.

Runtime contract: require eight real authored walk/idle directions before publishing a visual; verify profile/file/visible-pixel hashes, compatible cell/root/height and finite six-frame timing/muzzles. JSON numeric counts are checked by value (Godot JSON parses numbers as floats), not integer Variant type. Phase uses actual post-move_and_slide and post-stage-clamp world distance divided by walkStride*displayHeight/heightMetres. Reverse travel changes frame phase only. On warning entry the Actor has zero velocity before resolve_target(stationary=true), so idle body and idle muzzle agree. WINDUP/BURST do not re-resolve target. Three actual projectiles use frozen visible muzzle/ray; opposite target is reacquired afterward without smoothing. Inside all emitter offsets returns INF rather than reverse shots. This is the enemy telegraph contract, deliberately different from player instant input.

Actual new Godot smoke: 824 checks, zero failures; no stderr after explicit test-only transient AudioStreamPlayer teardown. Test image cells are coloured geometry fixtures (64px) under unique QA output, NOT appearance assets or 1080p visual evidence. 8x8 displacement/aim cases at 30/60/120Hz; actual Tactics/emission boundary cases at all three rates; real physical wall and actual stage clamp at DEFAULT60Hz. The latter are not claimed as 30/120Hz collision coverage. Failed/partial/changed/repeated/hidden-RGB duplicate source and first-frame facing checks included. The earlier draft had a test variable type-inference parse error, corrected without weakening assertions. Later tests increased 816->820->824 with actual bounds/collision/duplicate checks.

Other actual local regressions after shared Actor/UI changes: drone app170, anchor app271, machine436, player MotionLab runtime PASS and ROOK app1895/0. Older drone/anchor/player smokes retain pre-existing ObjectDB shutdown warnings (48/90/2/52 respectively); they are not called warning-free. The new bridge smoke performs its own transient sound cleanup and has empty stderr. Source repair continues independently; no real-biped native gameplay visual approval or Luna reproduction claim. The attached report binds current relevant code hashes. Please distinguish static reasoning, your independently executed tests and these local reported tests. If there is no concrete defect in this new narrow scope, say so without escalating to unrelated legacy pipeline work.
''']
rows=[]
for name in files:
    data=(root/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
    rows.append({'path':name,'sha256':digest})
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n```text\n{data.decode("utf-8-sig")}\n```\n')
target.write_text(''.join(parts),encoding='utf-8')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,
          'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'externalReview':'NOT_YET_SUBMITTED'}
target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'path':str(target),'bytes':target.stat().st_size,**manifest}))
