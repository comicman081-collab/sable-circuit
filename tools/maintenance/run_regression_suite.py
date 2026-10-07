#!/usr/bin/env python3
"""SABLE CIRCUIT regression suite runner.

One command runs the headless Godot regression tests (and, in the full suite,
the Motion Studio Python and JS tests). Every test output goes to
qa/regression_runs/<stamp>_<suite>/out/<test>/ through the test's --out
argument, and the run FAILS if any existing record under qa/ or
motion_lab_v1/qa/ changed, disappeared or gained a new file.

    python tools/maintenance/run_regression_suite.py                 # quick, about 2 minutes
    python tools/maintenance/run_regression_suite.py --suite full    # everything, about 45 minutes
    python tools/maintenance/run_regression_suite.py --only m13_runtime,battle_flow
    python tools/maintenance/run_regression_suite.py --list
    python tools/maintenance/run_regression_suite.py --selftest      # runner checks itself

A Godot SceneTree test that hits a script error never quits on its own, so a
"SCRIPT ERROR:" line ends the test as SCRIPT_ERROR after a short grace period
instead of waiting for the timeout. Timeouts kill the whole process tree.
Godot, Motion Studio Python and project paths can be overridden with
--godot/--python/--project or SABLE_GODOT/SABLE_MOTION_PYTHON.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_GODOT = Path(r"D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe")
DEFAULT_MOTION_PYTHON = Path(r"C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe")
RUNS_DIR = Path('qa/regression_runs')
GUARDED = (Path('qa'), Path('motion_lab_v1/qa'))
SCRIPT_ERROR_GRACE = 5.0
IMPORT_STAMP = Path('.godot/regression_import.stamp')
SKIP_DIRS = {'.git', '.godot', '.cache', 'node_modules'}


def import_needed(project: Path) -> str:
    """Why Godot must import before the tests run, or '' when its caches are current.

    A headless -s run neither imports resources nor registers a new class_name,
    so a new or edited script would otherwise fail as an undeclared identifier.
    """
    if not (project / '.godot' / 'imported').is_dir():
        return '첫 실행'
    stamp = project / IMPORT_STAMP
    if not stamp.is_file() or not (project / '.godot' / 'global_script_class_cache.cfg').is_file():
        return '스크립트 클래스 목록 갱신'
    since = stamp.stat().st_mtime
    if (project / 'project.godot').stat().st_mtime > since:
        return 'project.godot 변경'
    for folder, dirs, files in os.walk(project):
        if '.gdignore' in files:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('_retired')]
        for name in files:
            if name.endswith('.gd') and os.stat(os.path.join(folder, name)).st_mtime > since:
                return '스크립트 변경'
    return ''


@dataclass
class Test:
    name: str
    target: str               # res:// script for Godot tests; the generator for 'tool'; the test file for 'unittest';
                              # unused for the Motion Studio suites
    timeout: int
    quick: bool = False
    out: str | None = None    # None, 'dir', or the file name the test writes inside its out folder
    args: tuple = ()
    solo: bool = False        # timing-sensitive under CPU load: never runs beside another test
    kind: str = 'godot'       # 'godot', 'python' / 'node' (Motion Studio suites), 'tool' (generator --check)
                              # or 'unittest' (a project-root Python test file; it must write no file)


TESTS = [
    Test('combat_density', 'tests/smoke/combat_density_smoke.gd', 300, quick=True, out='density.json'),
    Test('cover_navigation', 'tests/smoke/cover_navigation_smoke.gd', 300, quick=True),
    Test('floor_segment', 'tests/smoke/floor_segment_smoke.gd', 400, quick=True),
    Test('combat_query_fastpath', 'tests/smoke/combat_query_fastpath_smoke.gd', 400, quick=True),
    Test('player_cover', 'tests/smoke/site7_player_cover_collision_smoke.gd', 300, quick=True),
    Test('cover_alpha_clip', 'tests/smoke/site7_cover_alpha_clip_smoke.gd', 300, quick=True),
    Test('cover_texture', 'tests/smoke/cover_texture_reduction_smoke.gd', 300, quick=True),
    Test('battle_flow', 'tests/smoke/site7_battle_flow_smoke.gd', 400, quick=True, solo=True),
    Test('combat_entry', 'tests/smoke/demo_combat_entry_regression.gd', 400, quick=True, out='entry.json', solo=True),
    Test('drone_app', 'tests/smoke/site7_drone_app_smoke.gd', 400, quick=True, out='drone_app.json'),
    Test('anchor_app', 'tests/smoke/site7_anchor_app_smoke.gd', 400, quick=True, out='anchor_app.json'),
    Test('campaign_data', 'tests/smoke/site7_campaign_data_smoke.gd', 300, quick=True),
    Test('upgrade_economy', 'tests/smoke/upgrade_economy_smoke.gd', 300, quick=True, out='save.json'),
    Test('boss_registry', 'tests/smoke/site7_boss_registry_smoke.gd', 600, quick=True),
    Test('boss_pattern', 'tests/smoke/site7_boss_pattern_smoke.gd', 400, quick=True, out='pattern.json'),
    Test('boss_duel', 'tests/smoke/site7_boss_duel_smoke.gd', 400, quick=True, out='duel.json'),
    Test('boss_room_fairness', 'tests/smoke/site7_boss_room_fairness_smoke.gd', 400, quick=True, out='room_fairness.json'),
    Test('robot_roster', 'tests/smoke/site7_robot_roster_smoke.gd', 600, quick=True),
    Test('enemy_facing', 'tests/smoke/site7_enemy_facing_smoke.gd', 300, quick=True),
    Test('machine_source', 'tests/smoke/site7_machine_source_smoke.gd', 300, quick=True),
    Test('emission_owner', 'tests/smoke/site7_emission_owner_smoke.gd', 600, quick=True, out='dir'),
    Test('m2_story', 'tests/smoke/m2_story_flow_smoke.gd', 400, quick=True),
    Test('m9_skill', 'tests/smoke/m9_operator_skill_synergy_smoke.gd', 300, quick=True),
    Test('m10_base_ui', 'tests/smoke/m10_base_ui_action_smoke.gd', 300, quick=True),
    Test('m10_persistence', 'tests/smoke/m10_persistence_smoke.gd', 300, quick=True, out='save.json'),
    Test('run_contract', 'tests/smoke/m11_run_contract_smoke.gd', 300, quick=True),
    Test('contract_offers', 'tests/smoke/run_contract_offers_smoke.gd', 120, quick=True),
    Test('contract_ui', 'tests/smoke/run_contract_ui_smoke.gd', 300, quick=True, out='dir', solo=True),
    Test('redline', 'tests/smoke/redline_smoke.gd', 300, quick=True, out='redline.json'),
    Test('contract_save', 'tests/smoke/run_contract_save_smoke.gd', 120, quick=True, out='save.json'),
    Test('intel_supply', 'tests/smoke/intel_supply_smoke.gd', 120, quick=True, out='intel_supply.json'),
    Test('module_expansion', 'tests/smoke/module_expansion_smoke.gd', 120, quick=True, out='module_expansion.json'),
    Test('weapon_expansion', 'tests/smoke/weapon_expansion_smoke.gd', 120, quick=True, out='weapon_expansion.json'),
    Test('lab_geometry', 'tests/smoke/lab_geometry_smoke.gd', 120, quick=True, out='lab_geometry.json'),
    Test('title_geometry', 'tests/smoke/title_geometry_smoke.gd', 120, quick=True, out='title_geometry.json'),
    Test('m12_revive', 'tests/smoke/m12_squad_revive_smoke.gd', 300, quick=True),
    Test('play_log', 'tests/smoke/play_session_log_smoke.gd', 300, quick=True, out='dir'),
    Test('hit_hurt_vfx', 'tests/smoke/combat_hit_hurt_vfx_smoke.gd', 300, quick=True),
    Test('combat_vfx', 'tests/smoke/combat_vfx_overhaul_smoke.gd', 300, quick=True),
    Test('elite_affix', 'tests/smoke/elite_affix_smoke.gd', 300, quick=True),
    Test('elite_expansion', 'tests/smoke/elite_expansion_smoke.gd', 300, quick=True),
    Test('zone_hazard', 'tests/smoke/zone_hazard_smoke.gd', 400, quick=True),
    Test('hazard_expansion', 'tests/smoke/hazard_expansion_smoke.gd', 600, quick=True,
         out='hazard_expansion.json', solo=True),
    Test('room_rule', 'tests/smoke/room_rule_smoke.gd', 300, quick=True, out='room_rule.json'),
    Test('firing_lane', 'tests/smoke/firing_lane_search_smoke.gd', 400, quick=True),
    Test('platform_carry', 'tests/smoke/actor_platform_carry_smoke.gd', 200, quick=True),
    Test('contact_carry', 'tests/smoke/actor_contact_carry_smoke.gd', 300, quick=True, out='contact_carry.json'),
    # Generated data must match its sources: the solved world layout, the plates'
    # mood lamps and void masks, and ASTER's walk registration.
    Test('world_layout', 'tools/environment/build_site7_world_layout.py', 300, quick=True, kind='tool'),
    Test('mood_light', 'tools/environment/build_site7_mood_light.py', 300, quick=True, kind='tool'),
    Test('walk_registration', 'tools/character_pipeline/build_walk_torso_registration.py', 300, quick=True, kind='tool'),
    Test('plate_axis', 'tests/test_site7_plate_lighting_axis.py', 120, quick=True, kind='unittest'),
    Test('variety_placement', 'tests/test_expansion_item1_placement.py', 120, quick=True, kind='unittest'),
    Test('seam_waiver', 'tests/test_site7_plate_lighting_seam_waiver.py', 300, quick=True, kind='unittest'),
    Test('mood_contact', 'tests/test_site7_mood_contact_compare.py', 120, quick=True, kind='unittest'),
    Test('deploy_warmer', 'tests/smoke/deploy_warmer_smoke.gd', 400, quick=True),
    Test('m13_migration', 'tests/smoke/m13_weapon_base_migration_smoke.gd', 300, quick=True, out='save.json'),
    Test('m13_campaign', 'tests/smoke/m13_weapon_campaign_smoke.gd', 300, quick=True),
    Test('m13_runtime', 'tests/smoke/m13_weapon_runtime_smoke.gd', 300, quick=True),
    *[Test('full_op_%02d' % i, 'tests/smoke/site7_full_operation_smoke.gd', 900, out='dir',
           args=('--mission=MIS_CH01_%02d' % i,), solo=True) for i in range(1, 11)],
    Test('traversal_audit', 'tests/smoke/site7_traversal_audit_smoke.gd', 1200, out='dir'),
    Test('enemy_cover_nav', 'tests/render/enemy_cover_navigation_regression.gd', 600, out='dir'),
    Test('cover_ai', 'tests/render/site7_cover_ai_check.gd', 400, out='dir'),
    Test('boss_capture_geometry', 'tests/render/site7_boss_pattern_capture.gd', 900, out='dir', solo=True),
    Test('lab_capture_geometry', 'tests/render/expansion_item3_capture.gd', 120, out='dir', solo=True),
    Test('boss_lineup', 'tests/render/site7_boss_lineup_capture.gd', 300, out='dir'),
    Test('variety_capture', 'tests/render/expansion_item1_capture.gd', 300, out='dir', solo=True),
    Test('world_route', 'tests/smoke/site7_world_route_navigation_smoke.gd', 400),
    Test('nav_pockets', 'tools/environment/audit_nav_pockets.gd', 400, out='nav_pockets.json', solo=True),
    # Real-time physics, 7 connectors x 2 directions x 8 missions: about 1,100 s on an idle PC (866 s before the WASD
    # probe returned to the deck centreline), so 900 s timed out at mission 7.
    Test('connector_alignment', 'tests/smoke/site7_connector_alignment_smoke.gd', 1800),
    Test('battle_geometry', 'tests/smoke/site7_battle_geometry_smoke.gd', 900),
    Test('walk_graph_capture', 'tests/render/site7_walk_graph_capture.gd', 900,
         out='dir', args=('--mission=MIS_CH01_06',)),
    Test('combat_sfx', 'tests/smoke/combat_sfx_r04_smoke.gd', 400, out='sfx.json'),
    Test('demo_integration', 'tests/render/demo_integration_check.gd', 400, out='dir'),
    Test('m7_visual', 'tests/smoke/m7_authored_visual_smoke.gd', 400),
    Test('m10_intel', 'tests/smoke/m10_intel_loadout_smoke.gd', 300),
    Test('m13_loadout', 'tests/smoke/m13_weapon_loadout_smoke.gd', 300, out='save.json'),
    Test('campaign', 'tests/smoke/site7_campaign_progression_smoke.gd', 600, out='dir'),
    Test('rook_app', 'tests/smoke/rook_motion_lab_app_smoke.gd', 400),
    Test('motion_lab_runtime', 'tests/smoke/motion_lab_character_runtime_smoke.gd', 400),
    Test('motion_lab_python', '', 1200, kind='python'),
    Test('motion_lab_js', '', 300, kind='node'),
]


@dataclass
class Result:
    test: str
    status: str
    seconds: float
    exit_code: int | None
    checks: int | None = None
    status_line: str = ''
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------- guard

def snapshot(project: Path, exclude: Path) -> dict:
    """SHA-256 of every file under the guarded record trees, except this run's folder."""
    digests = {}
    for tree in GUARDED:
        for folder, dirs, files in os.walk(project / tree):
            folder_path = Path(folder)
            if folder_path == project / RUNS_DIR:
                dirs[:] = []
                continue
            for name in files:
                path = folder_path / name
                digests[path.relative_to(project).as_posix()] = sha256(path)
    return digests


def compare(before: dict, after: dict) -> dict:
    return {'changed': sorted(p for p in before if p in after and after[p] != before[p]),
            'removed': sorted(p for p in before if p not in after),
            'added': sorted(p for p in after if p not in before)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- processes

def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
    else:
        proc.kill()


def run_process(cmd: list, cwd: Path, log_path: Path, timeout: float, stop_on_script_error: bool = True) -> tuple:
    """Run one test, streaming output to its log. Returns (status, exit_code, text).

    The first-run resource import prints transient parse errors before fonts and
    textures exist, so it passes stop_on_script_error=False and only times out.
    """
    chunks = []
    script_error_at = []
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def reader():
        with open(log_path, 'wb') as log:
            for raw in proc.stdout:
                log.write(raw)
                line = raw.decode('utf-8', 'replace')
                chunks.append(line)
                if 'SCRIPT ERROR:' in line and not script_error_at:
                    script_error_at.append(time.monotonic())

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    start = time.monotonic()
    status = None
    while proc.poll() is None:
        now = time.monotonic()
        if now - start > timeout:
            status = 'TIMEOUT'
        elif stop_on_script_error and script_error_at and now - script_error_at[0] > SCRIPT_ERROR_GRACE:
            status = 'SCRIPT_ERROR'
        if status:
            kill_tree(proc)
            break
        time.sleep(0.2)
    proc.wait()
    thread.join(timeout=10)
    text = ''.join(chunks)
    if status is None:
        failed_script = script_error_at and stop_on_script_error
        status = 'SCRIPT_ERROR' if failed_script else ('PASS' if proc.returncode == 0 else 'FAIL')
    return status, proc.returncode, text


def res_path(project: Path, path: Path) -> str:
    return 'res://' + path.relative_to(project).as_posix()


def test_command(test: Test, cfg) -> tuple:
    """Build (command, cwd) and create the test's out folder."""
    out_dir = cfg.run_dir / 'out' / test.name
    if test.kind == 'python':
        return [str(cfg.python), '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'], cfg.project / 'motion_lab_v1'
    if test.kind == 'node':
        files = sorted(glob.glob(str(cfg.project / 'motion_lab_v1/tests/*.test.js')))
        return ['node', '--test', *files], cfg.project / 'motion_lab_v1'
    if test.kind == 'tool':
        return [str(cfg.python), '-B', str(cfg.project / test.target), '--check'], cfg.project
    if test.kind == 'unittest':
        return [str(cfg.python), '-B', str(cfg.project / test.target)], cfg.project
    cmd = [str(cfg.godot), '--headless', '--path', str(cfg.project),
           '--log-file', str(cfg.run_dir / 'logs' / (test.name + '.godot.log')), '-s', 'res://' + test.target]
    user_args = list(test.args)
    if test.out:
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir if test.out == 'dir' else out_dir / test.out
        user_args.append('--out=' + res_path(cfg.project, target))
    if user_args:
        cmd += ['--', *user_args]
    return cmd, cfg.project


CHECK_PATTERNS = (r'(\d+)\s+checks?\b', r'\bRan (\d+) tests?\b', r'\btests (\d+)\b')


def parse_output(text: str) -> tuple:
    checks = None
    for pattern in CHECK_PATTERNS:
        found = re.findall(pattern, text)
        if found:
            checks = int(found[-1])
            break
    if checks is None:
        # Older smokes print one "PASS: <label>" line per check and no total.
        checks = len(re.findall(r'^PASS: ', text, flags=re.M)) or None
    lines =[l.strip() for l in text.splitlines() if re.search(r'\b(PASS|FAIL|OK|FAILED)\b', l)]
    missing = sorted(set(re.findall(r'(?:Cannot open file|No loader found for resource|'
                                    r'Failed loading resource|Resource file not found)[^\n]*', text)))
    return checks, (lines[-1][:200] if lines else ''), missing[:10]


def run_test(test: Test, cfg) -> Result:
    cmd, cwd = test_command(test, cfg)
    start = time.monotonic()
    try:
        status, code, text = run_process(cmd, cwd, cfg.run_dir / 'logs' / (test.name + '.log'), test.timeout)
    except OSError as error:
        return Result(test.name, 'FAIL', 0.0, None, notes=['실행 불가: %s' % error])
    checks, status_line, missing = parse_output(text)
    notes = ['리소스 누락: ' + m for m in missing]
    if status == 'SCRIPT_ERROR':
        first = next((l for l in text.splitlines() if 'SCRIPT ERROR:' in l), '')
        notes.insert(0, first.strip()[:200])
    return Result(test.name, status, round(time.monotonic() - start, 1), code, checks, status_line, notes)


# ---------------------------------------------------------------- reporting

def git(project: Path, *args) -> str:
    proc = subprocess.run(['git', '-C', str(project), *args], capture_output=True)
    return proc.stdout.decode('utf-8', 'replace').strip()


def write_reports(cfg, meta: dict, results: list, guard: dict, overall: str) -> None:
    summary = dict(meta, overall=overall, guard=guard, results=[r.__dict__ for r in results])
    (cfg.run_dir / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding='utf-8')
    passed = sum(r.status == 'PASS' for r in results)
    lines = ['# 회귀 실행 %s' % cfg.run_dir.name, '',
             '- 결과: **%s** (%d/%d PASS)' % (overall, passed, len(results)),
             '- 묶음: %s · 커밋: `%s`%s' % (meta['suite'], meta['git_head'][:10],
                                          ' (작업 트리 변경 %d개)' % meta['git_dirty'] if meta['git_dirty'] else ''),
             '- 시작 %s · 소요 %d초' % (meta['started'], meta['seconds']), '',
             '| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |', '|---|---|---:|---:|---|']
    for r in results:
        note = '; '.join(r.notes) or r.status_line
        lines.append('| %s | %s | %s | %s | %s |' % (r.test, r.status, r.checks if r.checks is not None else '-',
                                                     r.seconds, note.replace('|', '/')[:160]))
    lines += ['', '## 기존 QA 기록 보호', '']
    violations = sum(len(v) for v in guard.values())
    if violations == 0:
        lines.append('- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건')
    else:
        for kind, label in (('changed', '변경'), ('removed', '삭제'), ('added', '추가')):
            for path in guard[kind][:50]:
                lines.append('- %s: `%s`' % (label, path))
    (cfg.run_dir / 'SUMMARY_KO.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


# ---------------------------------------------------------------- main

def resolve_config(args) -> argparse.Namespace:
    project = Path(args.project).resolve() if args.project else DEFAULT_PROJECT
    godot = Path(args.godot or os.environ.get('SABLE_GODOT') or DEFAULT_GODOT)
    python = Path(args.python or os.environ.get('SABLE_MOTION_PYTHON') or
                  (DEFAULT_MOTION_PYTHON if DEFAULT_MOTION_PYTHON.exists() else sys.executable))
    return argparse.Namespace(project=project, godot=godot, python=python)


def select(args) -> list:
    if args.only:
        wanted = [n.strip() for n in args.only.split(',') if n.strip()]
        unknown = [n for n in wanted if n not in {t.name for t in TESTS}]
        if unknown:
            raise SystemExit('알 수 없는 테스트: ' + ', '.join(unknown))
        return [t for t in TESTS if t.name in wanted]
    return [t for t in TESTS if args.suite == 'full' or t.quick]


def run_suite(cfg, tests: list, suite: str, workers: int) -> int:
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    cfg.run_dir = cfg.project / RUNS_DIR / ('%s_%s' % (stamp, suite))
    (cfg.run_dir / 'logs').mkdir(parents=True, exist_ok=True)
    reason = import_needed(cfg.project) if any(t.kind == 'godot' for t in tests) else ''
    if reason:
        print('Godot 리소스 가져오기(%s)...' % reason, flush=True)
        status, _, _ = run_process([str(cfg.godot), '--headless', '--path', str(cfg.project), '--import'],
                                   cfg.project, cfg.run_dir / 'logs' / '_import.log', 3600, stop_on_script_error=False)
        if status == 'PASS':
            (cfg.project / IMPORT_STAMP).write_text(dt.datetime.now().isoformat(timespec='seconds'), encoding='utf-8')
        print('  가져오기:', status, flush=True)
    meta = {'suite': suite, 'project': str(cfg.project), 'started': dt.datetime.now().isoformat(timespec='seconds'),
            'git_head': git(cfg.project, 'rev-parse', 'HEAD'),
            'git_dirty': len([l for l in git(cfg.project, 'status', '--porcelain').splitlines() if l.strip()]),
            'godot': str(cfg.godot), 'motion_python': str(cfg.python), 'workers': workers}
    print('실행 폴더:', cfg.run_dir.relative_to(cfg.project).as_posix(), '| 테스트 %d개' % len(tests), flush=True)
    before = snapshot(cfg.project, cfg.run_dir)
    start = time.monotonic()
    results = {}
    order = {t.name: i for i, t in enumerate(tests)}
    done = [0]

    def finish(result: Result):
        results[result.test] = result
        done[0] += 1
        print('[%2d/%d] %-12s %-20s %6s  %5.0fs  %s' % (
            done[0], len(tests), result.status, result.test,
            result.checks if result.checks is not None else '-', result.seconds,
            (result.notes[0] if result.notes else result.status_line)[:90]), flush=True)

    shared = [t for t in tests if not t.solo]
    solo = [t for t in tests if t.solo]
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for result in pool.map(lambda t: run_test(t, cfg), shared):
            finish(result)
    for test in solo:
        finish(run_test(test, cfg))
    guard = compare(before, snapshot(cfg.project, cfg.run_dir))
    ordered = sorted(results.values(), key=lambda r: order[r.test])
    clean = not any(guard.values())
    overall = 'PASS' if clean and all(r.status == 'PASS' for r in ordered) else 'FAIL'
    meta['seconds'] = round(time.monotonic() - start)
    write_reports(cfg, meta, ordered, guard, overall)
    if not clean:
        print('기존 QA 기록 변경: 변경 %d · 삭제 %d · 추가 %d' % tuple(len(guard[k]) for k in ('changed', 'removed', 'added')))
    print('REGRESSION_SUITE: %s (%d/%d PASS) -> %s' % (
        overall, sum(r.status == 'PASS' for r in ordered), len(ordered),
        (cfg.run_dir / 'SUMMARY_KO.md').relative_to(cfg.project).as_posix()), flush=True)
    return 0 if overall == 'PASS' else 1


def selftest(cfg) -> int:
    """Broken, hanging and passing probe scripts must end as SCRIPT_ERROR, TIMEOUT and PASS."""
    work = cfg.project / '.cache' / 'regression_selftest'
    work.mkdir(parents=True, exist_ok=True)
    probes = {
        'pass_probe': ('func run() -> void:\n    await process_frame\n'
                       '    print("SELFTEST_PROBE: PASS (1 checks)")\n    quit(0)\n', 'PASS', 120),
        'script_error_probe': ('func run() -> void:\n    await process_frame\n    var parts := {}\n'
                               '    var value: Node = parts["missing"]\n    print(value)\n    quit(0)\n',
                               'SCRIPT_ERROR', 120),
        'hang_probe': ('func run() -> void:\n    while true:\n        await process_frame\n', 'TIMEOUT', 15),
    }
    cfg.run_dir = work
    (work / 'logs').mkdir(exist_ok=True)
    failures = []
    for name, (body, expected, timeout) in probes.items():
        (work / (name + '.gd')).write_text('extends SceneTree\nfunc _init() -> void: call_deferred("run")\n' + body,
                                           encoding='utf-8')
        probe = Test(name, (work / (name + '.gd')).relative_to(cfg.project).as_posix(), timeout)
        result = run_test(probe, cfg)
        ok = result.status == expected and result.seconds < timeout + SCRIPT_ERROR_GRACE + 30
        print('%-20s expected %-12s got %-12s %5.1fs %s' % (name, expected, result.status, result.seconds, 'ok' if ok else 'WRONG'))
        if not ok:
            failures.append(name)
    tree = work / ('guard_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
    (tree / 'qa').mkdir(parents=True)
    (tree / 'qa' / 'kept.json').write_text('{"a":1}', encoding='utf-8')
    (tree / 'qa' / 'changed.json').write_text('{"b":1}', encoding='utf-8')
    probe_before = snapshot(tree, tree / 'none')
    (tree / 'qa' / 'changed.json').write_text('{"b":2}', encoding='utf-8')
    (tree / 'qa' / 'added.json').write_text('{}', encoding='utf-8')
    probe_guard = compare(probe_before, snapshot(tree, tree / 'none'))
    guard_ok = probe_guard['changed'] == ['qa/changed.json'] and probe_guard['added'] == ['qa/added.json']
    print('%-20s expected changed+added  got %s %s' % ('guard_probe', probe_guard, 'ok' if guard_ok else 'WRONG'))
    if not guard_ok:
        failures.append('guard_probe')
    print('REGRESSION_SELFTEST:', 'PASS' if not failures else 'FAIL ' + ', '.join(failures))
    return 0 if not failures else 1


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description='SABLE CIRCUIT regression suite')
    parser.add_argument('--suite', choices=('quick', 'full'), default='quick')
    parser.add_argument('--only', help='comma-separated test names (overrides --suite)')
    parser.add_argument('--workers', type=int, default=1, help='parallel non-solo tests (default 1)')
    parser.add_argument('--project', help='project root (default: this repository)')
    parser.add_argument('--godot')
    parser.add_argument('--python', help='Motion Studio test interpreter')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    cfg = resolve_config(args)
    # Child tests keep their temporary files inside the project (git-ignored .cache), not the system drive.
    tmp = cfg.project / '.cache' / 'tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    for name in ('TMP', 'TEMP', 'TMPDIR'):
        os.environ[name] = str(tmp)
    if args.list:
        for t in TESTS:
            print('%-20s %-5s %5ds %s%s' % (t.name, 'quick' if t.quick else 'full', t.timeout,
                                           t.target or t.kind, ' (solo)' if t.solo else ''))
        return 0
    if args.selftest:
        return selftest(cfg)
    tests = select(args)
    return run_suite(cfg, tests, 'custom' if args.only else args.suite, args.workers)


if __name__ == '__main__':
    sys.exit(main())
