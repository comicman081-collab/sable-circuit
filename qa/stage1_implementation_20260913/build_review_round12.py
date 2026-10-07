"""Freeze actual R11 reproductions, narrow fixes and current passing tests."""
from pathlib import Path
import datetime, hashlib, json
root=Path(__file__).resolve().parents[2]
out=Path(__file__).parent
target=out/'gpt6pro_harness_review_round12.md'
if target.exists(): raise FileExistsError(target)
before='qa/stage1_implementation_20260913/biped_bridge_1789298056_896/report.json'
after='qa/stage1_implementation_20260913/biped_bridge_1789298299_626/report.json'
report=json.loads((root/after).read_text(encoding='utf-8'))
if report['status']!='PASS' or report['checks']!=876 or report['failures']: raise RuntimeError('Current actual regression required')
for name,digest in report['sha256'].items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest: raise RuntimeError('Stale report '+name)
files=list(report['sha256'])+[
    '.agents/skills/sable-character-studio/references/enemy-facing.md',
    'data/art_profiles/enemy_profiles.json',before,after,
    'qa/stage1_implementation_20260913/r11_counterexamples_before_fix.log']
for name in ['site7_biped_bridge_smoke','site7_drone_app_smoke','site7_anchor_app_smoke','site7_machine_source_smoke','motion_lab_character_runtime_smoke','rook_motion_lab_app_smoke']:
    for kind in ['stdout','stderr']:
        files.append('qa/stage1_implementation_20260913/r11_final_'+name+'.'+kind+'.log')
parts=['''# Round12 — actual R11 reproduction and narrow corrections

Please verify only closure of R11-01/02/03/04 in the attached current code and tests. Prior H01/H02 and R8 remain closed. No new framework, old harness, or art approval is requested.

Your Round11 final reply was actually read. Locally I added its concrete cases BEFORE changing the bridge/Actor. Real Godot4.7.1 run: 871 assertions, 19 failures, including empty idle/walk acceptance, same frames repacked to2 columns, padding-only changed duplicate sequence, derived overflow, and moved WINDUP/BURST continuing. The before report and actual log are attached. The underflow negative was already rejected by the previous input path; I do not claim that case was newly reproduced as a failure. Before-code hashes match the Round11 bridge/Actor. The before test had only the initial counterexamples; five later assertions add derived-scale and valid alternate-layout positive controls, not relaxed assertions.

Fixes:
- R11-01: check every USED cell for complete invisibility before publishing a visual. No artificial opaque pixels or fallback source.
- R11-02: hash ordered used RGBA cells with invisible RGB canonicalized; no page dimensions/columns/unused pixels in the semantic identity. Cache key includes actual file hash, cell, columns and frame count. Valid distinct SE4-column and NW2-column layouts still pass; distinct visible padding is ignored, not forbidden.
- R11-03: derive the cycle distance in a temporary and reject nonfinite/nonpositive results. Check derived scale and actual Vector2-scaled geometry before publishing. Cell dimensions are integral. Normal1.33*129.6/1.72 stays100.2139534883721; no gameplay speed change.
- R11-04: after real move_and_slide plus stage constraint, if an active candidate biped had nonzero measured displacement and Tactics is WINDUP/BURST, call existing interrupt(). Keep the actual position and commit that displacement; no origin snapshot masquerading as current, no silent target reacquisition during old warning. Tactics code itself is unchanged. The added test exercises actual Actor->Tactics ordering under stage correction at30/60/120Hz in WINDUP and the WINDUP-to-BURST transition, verifying cancellation, no continued emission and honest distance clock. Existing zero-displacement three-round cases remain positive controls.

Actual current Godot smoke: 876 assertions, no failures, empty stderr. Current report binds all five runtime/test hashes. Other reruns after shared Actor change: drone170, anchor271, machine436, MotionLab player PASS, ROOK1895/0. Old shutdown warnings remain in drone48, anchor78, player2 and ROOK68; warning counts vary with transient sound lifetime. They are not clean-exit or visual approval claims. The new bridge smoke cleans only its test process's own transient audio nodes.

The skill now documents the four safeguards and precise test scope: real physical wall is atdefault60Hz; explicit stage correction while locked is tested at30/60/120Hz. All synthetic64px images are technical fixtures, not character art or1080p visual evidence. The rifle art is still under a separate SE whole-cycle review. No production biped_asset pointer, no completed Stage1 MVP/deployment, no Luna end-to-end claim. Preserve the accepted three playable characters and1.8xscale.

Please distinguish your executed checks from our actual local Godot reports and static reasoning. If the four original counterexamples are closed, state that limited closure; identify any concrete remaining counterexample in this modified scope with exact code location.
''']
rows=[]
for name in files:
    data=(root/name).read_bytes();digest=hashlib.sha256(data).hexdigest()
    rows.append({'path':name,'sha256':digest})
    parts.append(f'\n## FILE: {name}\nSHA256: {digest}\n```text\n{data.decode("utf-8-sig")}\n```\n')
target.write_text(''.join(parts),encoding='utf-8')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'externalReview':'NOT_YET_SUBMITTED'}
target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'path':str(target),'bytes':target.stat().st_size,'files':len(rows),'sha256':manifest['sha256']}))
