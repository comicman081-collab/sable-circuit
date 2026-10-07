"""Claude review helper (N-1): collect the evidence of the navigation review into a staging folder, normalise text line ends
to LF, and write MANIFEST.json (sha256 + size of every staged file; the big direction CSVs are listed but not copied).
usage: stage_n1_evidence.py <stage dir>   (run from the project root)"""
import hashlib, json, re, shutil, sys
from pathlib import Path

ROOT = Path.cwd()
SC = ROOT / '.cache' / 'claude_scratch'
S1 = SC / 'item1_review'
LOGS = SC / 'nav_review_logs'
HEAD = SC / 'proj_navhead' / '.cache'
FIX = SC / 'proj_navfix' / '.cache'
MUT = SC / 'proj_navmut' / '.cache'
M4 = SC / 'proj_navm4' / '.cache'
SUITE = ROOT / 'qa' / 'regression_runs' / '20261003_170533_full'
RERUN = ROOT / 'qa' / 'regression_runs' / '20261003_183628_custom'
stage = Path(sys.argv[1])
if stage.exists():
    shutil.rmtree(stage)
(stage / 'evidence' / 'tools').mkdir(parents=True)
(stage / 'evidence' / 'raw').mkdir(parents=True)
TEXT = {'.gd', '.py', '.sh', '.md', '.json', '.jsonl', '.log', '.csv', '.txt'}
copied = []
skipped = []
missing = []


def put(src: Path, dst_rel: str, optional=False):
    if not src.exists():
        if optional:
            missing.append(str(src))
            return
        raise SystemExit('missing ' + str(src))
    dst = stage / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in TEXT:
        data = src.read_bytes()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('cp949', 'replace')
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = '\n'.join(line.rstrip(' \t') for line in text.split('\n'))
        dst.write_bytes(text.encode('utf-8'))
    else:
        shutil.copy2(src, dst)
    copied.append(dst_rel)


def hash_only(src: Path, note: str):
    h = hashlib.sha256(src.read_bytes()).hexdigest()
    skipped.append({'source': str(src.relative_to(ROOT)).replace('\\', '/'), 'sha256': h, 'bytes': src.stat().st_size, 'note': note})


def key_lines(src: Path, pattern, dst_rel: str):
    text = src.read_bytes().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
    keep = [ln.rstrip() for ln in text.split('\n') if re.search(pattern, ln)]
    dst = stage / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text('\n'.join(keep) + '\n', encoding='utf-8', newline='\n')
    copied.append(dst_rel)


tools = ['nav_walkout.gd', 'nav_direction_dump2.gd', 'nav_dump_diff2.py', 'nav_cells_select.py', 'nav_plan_timing.gd', 'spawn_slots_dump.gd',
         'lane_pocket_probe.gd', 'mutate_nav.py', 'm4_chain.sh', 'n03_tests.sh', 'bots_nav.py', 'patch_bot_nav.py', 'bot_pairs.sh', 'ab_serial.sh',
         'timing_ab.sh', 'timing_pairs.sh', 'robot_dumps.sh', 'make_fastpath_probe.py', 'fastpath_probe.gd', 'fastpath_chain.sh',
         'post_suite_chain.sh', 'hazard_causality.sh', 'stage_n1_evidence.py']
for name in tools:
    put(S1 / name, 'evidence/tools/' + name, optional=True)

R = 'evidence/raw/'
put(HEAD / 'out' / 'audit12.json', R + 'audit12_prefix.json', optional=True)
put(FIX / 'out' / 'audit12.json', R + 'audit12_fix.json', optional=True)
put(FIX / 'out' / 'audit8.json', R + 'audit8_fix.json', optional=True)
for name, label in (('audit12_head', 'audit12_prefix'), ('audit12_fix', 'audit12_fix'), ('audit8_fix', 'audit8_fix')):
    put(LOGS / (name + '.log'), R + 'logs/' + label + '.log', optional=True)
put(LOGS / 'dump2_diff.json', R + 'dump2_diff_operator.json', optional=True)
put(LOGS / 'dump2_robot_diff.json', R + 'dump2_diff_robot.json', optional=True)
cells = LOGS / 'cells'
if cells.exists():
    for path in sorted(cells.glob('*')):
        put(path, R + 'cells/' + path.name)
put(FIX / 'out' / 'walk_all.json', R + 'walk_all_fix.json', optional=True)
put(HEAD / 'out' / 'walk_all.json', R + 'walk_all_prefix.json', optional=True)
put(HEAD / 'out' / 'lane_probe.json', R + 'lane_probe_prefix.json', optional=True)
put(FIX / 'out' / 'lane_probe.json', R + 'lane_probe_fix.json', optional=True)
put(MUT / 'out' / 'lane_probe.json', R + 'lane_probe_laneroutes_reverted.json', optional=True)
put(HEAD / 'out' / 'spawn_slots2.csv', R + 'spawn_slots2_prefix.csv', optional=True)
put(FIX / 'out' / 'spawn_slots2.csv', R + 'spawn_slots2_fix.csv', optional=True)
for big, label in ((HEAD / 'out' / 'dump2_op.csv', 'operator direction dump, pre-fix'), (FIX / 'out' / 'dump2_op.csv', 'operator direction dump, fix'),
                   (HEAD / 'out' / 'dump2_robot.csv', 'robot direction dump, pre-fix'), (FIX / 'out' / 'dump2_robot.csv', 'robot direction dump, fix')):
    if big.exists():
        hash_only(big, label)
put(LOGS / 'timing_pairs.log', R + 'timing/timing_pairs.log', optional=True)
put(LOGS / 'timing_pairs_round1_interrupted.log', R + 'timing/timing_pairs_round1_interrupted.log', optional=True)
put(LOGS / 'timing_ab.log', R + 'timing/timing_ab_first_method.log', optional=True)
for rnd in (1, 2, 3):
    put(HEAD / 'out' / f'timingp_r{rnd}.json', R + f'timing/paired_prefix_r{rnd}.json', optional=True)
    put(FIX / 'out' / f'timingp_r{rnd}.json', R + f'timing/paired_fix_r{rnd}.json', optional=True)
for v in ('over', 'nophys', 'nonodes', 'noswap', 'nomargin'):
    put(M4 / 'out' / f'm4_{v}.json', R + f'mutations/m4_{v}_audit.json', optional=True)

# key lines of the logs, so a reader does not have to open 50 KB of engine output
pat = re.compile(r'NAV_POCKET_AUDIT|COVER_NAVIGATION_SMOKE|ENEMY_COVER_NAVIGATION|SITE7_COVER_AI|SITE7_WORLD_ROUTE|FIRING_LANE_SEARCH_SMOKE|LANE_POCKET_PROBE|COMBAT_QUERY_FASTPATH|HAZARD_EXPANSION_SMOKE|HAZARD_ESCAPE_GRID|^FAIL:|PROBE_MISSION|PROBE ')
lines = []
for path in sorted(LOGS.glob('*.log')):
    if path.name.startswith(('timing_proj', 'timingp_', 'bot_')):
        continue
    try:
        text = path.read_bytes().decode('utf-8', 'replace')
    except OSError:
        continue
    hits = [ln.strip() for ln in text.replace('\r', '').split('\n') if pat.search(ln)]
    if hits:
        lines.append('## ' + path.name)
        lines.extend('    ' + ln[:260] for ln in hits[:30])
(stage / R / 'log_key_lines.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
copied.append(R + 'log_key_lines.txt')
for name, label in (('fastpath_head', 'fastpath_prefix'), ('fastpath_fix', 'fastpath_fix'), ('fastpath_probe_fix', 'fastpath_probe_fix'),
                    ('hazard_expansion_proj_navhead', 'hazard_expansion_prefix'), ('hazard_expansion_proj_navfix', 'hazard_expansion_fix')):
    src = LOGS / (name + '.log')
    if src.exists():
        key_lines(src, r'FAIL|PASS|PROBE|COMBAT_QUERY_FASTPATH|HAZARD_EXPANSION', R + 'logs/' + label + '.txt')
for snap, tag in ((HEAD, 'prefix'), (FIX, 'fix')):
    put(snap / 'out' / 'hazard25.json', R + f'hazard/hazard25_{tag}.json', optional=True)
    put(snap / 'out' / 'hazard10.json', R + f'hazard/hazard10_{tag}.json', optional=True)

# bots
put(S1 / 'bots_nav.jsonl', R + 'bots/bots_nav.jsonl', optional=True)
for snap, tag in ((HEAD, 'prefix'), (FIX, 'fix')):
    bot_out = snap / 'bot_out'
    if bot_out.exists():
        for run in sorted(bot_out.glob('*')):
            j = run / 'full_operation.json'
            if j.exists():
                put(j, R + f'bots/runs_{tag}/{run.name}.json')

# the whole-suite gate on 4e3ac9e6
put(SUITE / 'SUMMARY_KO.md', R + 'full_suite_4e3ac9e6/SUMMARY_KO.md', optional=True)
put(SUITE / 'summary.json', R + 'full_suite_4e3ac9e6/summary.json', optional=True)
put(S1 / 'full_suite_4e3ac9e6.log', R + 'full_suite_4e3ac9e6/runner_stdout.log', optional=True)
for name in ('combat_query_fastpath', 'hazard_expansion'):
    src = SUITE / 'logs' / (name + '.log')
    if src.exists():
        key_lines(src, r'FAIL|PASS|COMBAT_QUERY_FASTPATH|HAZARD_EXPANSION', R + f'full_suite_4e3ac9e6/{name}_key_lines.txt')
for op in ('06', '08'):
    put(SUITE / 'out' / f'full_op_{op}' / 'full_operation.json', R + f'full_suite_4e3ac9e6/full_op_{op}_wiped.json', optional=True)
put(RERUN / 'SUMMARY_KO.md', R + 'rerun_full_op_06_08/SUMMARY_KO.md', optional=True)
put(RERUN / 'summary.json', R + 'rerun_full_op_06_08/summary.json', optional=True)
for op in ('06', '08'):
    put(RERUN / 'out' / f'full_op_{op}' / 'full_operation.json', R + f'rerun_full_op_06_08/full_op_{op}.json', optional=True)

# manifest
files = []
for path in sorted(stage.rglob('*')):
    if path.is_file() and path.name != 'MANIFEST.json':
        data = path.read_bytes()
        files.append({'path': str(path.relative_to(stage)).replace('\\', '/'), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
manifest = {'review': 'N-1 navigation pockets, fix 48a0bd28 / record 4e3ac9e6', 'files': files, 'not_copied': skipped}
(stage / 'evidence' / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print('staged', len(files), 'files,', len(skipped), 'hash-only,', sum(f['bytes'] for f in files), 'bytes')
if missing:
    print('missing optional sources:')
    for m in missing:
        print('  ', m)
