"""Claude review helper (item 2 review of e091e25f/b4aa2ae0): stage the evidence into a folder and write its MANIFEST.json.
usage: stage_item2_evidence.py <stage dir>      (run from the project root; the stage dir is created fresh)
Text files are normalised to LF with trailing blanks removed; MANIFEST.json lists the SHA-256 and size of every staged file.
Large dumps that are reproducible from the tools (the two 10 MB offers dumps) are listed by hash only."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
SC = ROOT / '.cache' / 'claude_scratch'
S1 = SC / 'item1_review'
R = SC / 'item2_review'
OUT_IC = SC / 'proj_ic' / '.cache' / 'out'
OUT_HEAD = SC / 'proj_head' / '.cache' / 'out'
LOGS = SC / 'item2_logs'
RUNS = ROOT / 'qa' / 'regression_runs'
stage = Path(sys.argv[1])
if stage.exists():
    shutil.rmtree(stage)
for sub in ('tools', 'raw', 'raw/cases', 'raw/save_probes', 'raw/runs'):
    (stage / sub).mkdir(parents=True)
TEXT = {'.gd', '.py', '.sh', '.md', '.json', '.jsonl', '.log', '.txt', '.out', '.done'}
files = []
hash_only = []


def put(src: Path, dst_rel: str, optional: bool = False):
    if not src.exists():
        if optional:
            return
        raise SystemExit('missing ' + str(src))
    dst = stage / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in TEXT:
        text = src.read_bytes().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
        dst.write_bytes('\n'.join(line.rstrip(' \t') for line in text.split('\n')).encode('utf-8'))
    else:
        shutil.copy2(src, dst)
    files.append(dst_rel)


for name in ('mutate_ic.py', 'ic_matrix.sh', 'make_ic_tables.py', 'analyze_offers.py', 'compare_saves.py', 'save_matrix.sh',
             'golden_dump.gd', 'offers_dump.gd', 'save_probe.gd', 'make_old_save.gd', 'make_new_save.gd', 'flow_audit.gd',
             'bot_arms.gd', 'bot_arms.sh', 'bots_arms_report.py', 'stage_item2_evidence.py'):
    put(R / name, 'tools/' + name, optional=True)
for name in ('make_snapshot.sh', 'run_godot_low.sh', 'drop_snapshot.sh', 'lowrun.py'):
    put(S1 / name, 'tools/' + name)

# analyses and matrices
for name in ('offers_analysis.md', 'save_matrix.md', 'visual_validation_mine.json', 'mutations_ic.md', 'bots_arms.md', 'targeted_full_only.md'):
    put(R / 'evidence' / name, 'raw/' + name, optional=True)
put(R / 'ic_matrix.jsonl', 'raw/ic_matrix.jsonl')
put(R / 'bots_arms.jsonl', 'raw/bots_arms.jsonl', optional=True)
put(OUT_HEAD / 'build_old.json', 'raw/build_472_ids_7b26a152.json')
put(OUT_IC / 'flow_audit_headless.json', 'raw/flow_audit_headless.json')
for p in sorted(OUT_IC.glob('bot_*_*_*/full_operation.json')):
    put(p, 'raw/bot_runs/%s.json' % p.parent.name)
for p in sorted(OUT_IC.glob('probe_new__*.json')):
    put(p, 'raw/save_probes/' + p.name)
for p in sorted(OUT_HEAD.glob('probe_old__*.json')):
    put(p, 'raw/save_probes/' + p.name)
for name in ('quick_mine.log', 'only_campaign.log', 'ic_base_fix.log', 'ic_all.log', 'flow_audit_headless.log', 'flow_audit_choice_short.log',
             'targeted_full_only.log', 'm8_proj_head.log', 'm8_proj_ic.log', 'bot_arms.log'):
    put(LOGS / name, 'raw/' + name, optional=True)
put(OUT_IC / 'flow_audit_choice_short.json', 'raw/flow_audit_choice_short.json', optional=True)
# the runner records of my own runs
for stamp, tag in (('20261004_172313_quick', 'quick_b4aa2ae0'), ('20261004_173328_custom', 'campaign_b4aa2ae0')):
    put(RUNS / stamp / 'SUMMARY_KO.md', 'raw/runs/%s_SUMMARY_KO.md' % tag)
    put(RUNS / stamp / 'summary.json', 'raw/runs/%s_summary.json' % tag)
for extra in sorted(RUNS.glob('*_custom')):
    # later targeted reruns (campaign / m10_intel / m13_loadout ...) are staged too when they were made after 17:40
    if extra.name >= '20261004_18':
        put(extra / 'SUMMARY_KO.md', 'raw/runs/%s_SUMMARY_KO.md' % extra.name)
        put(extra / 'summary.json', 'raw/runs/%s_summary.json' % extra.name)
# case logs: every failing/script-error case, every base case, and the FIX case; passing mutant cases are in the JSONL
failing = set()
for line in (R / 'ic_matrix.jsonl').read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    key = {'contract_offers': 'o', 'contract_ui': 'u', 'redline': 'r', 'contract_save': 's', 'run_contract': 'm', 'play_log': 'p',
           'boss_duel': 'b', 'campaign': 'c'}[row['test']]
    bad = row['exit'] != '0' or int(row['script_errors']) > 0 or 'FAIL' in (row['result'] or '')
    if bad or row['mutant'] in ('base', 'mission_id_restored'):
        failing.add('%s__%s.log' % (row['mutant'], key))
for name in sorted(failing):
    put(R / 'logs' / 'cases' / name, 'raw/cases/' + name, optional=True)
for name in ('offers_a.json', 'offers_b.json'):
    p = OUT_IC / name
    if p.exists():
        hash_only.append({'path': 'raw/%s (not staged: 10 MB, reproduce with tools/offers_dump.gd)' % name,
                          'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
p = OUT_IC / 'build_new.json'
if p.exists():
    hash_only.append({'path': 'raw/build_472_ids_b4aa2ae0.json (not staged: byte-identical to build_472_ids_7b26a152.json, same SHA-256)',
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
manifest = {
    'review': 'item 2 (contract choice + REDLINE): Codex e091e25f / b4aa2ae0',
    'files': [{'path': p, 'sha256': hashlib.sha256((stage / p).read_bytes()).hexdigest(), 'bytes': (stage / p).stat().st_size} for p in sorted(files)],
    'hash_only': hash_only,
}
(stage / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print('staged %d files (+%d hash-only) into %s' % (len(files), len(hash_only), stage))
