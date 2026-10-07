"""Claude review helper (N-1 re-check of 89d30934): stage the evidence into a folder and write its MANIFEST.json.
usage: stage_rc_evidence.py <stage dir>      (run from the project root; the stage dir is created fresh)
Text files are normalised to LF with trailing blanks removed; MANIFEST.json lists the SHA-256 and size of every staged file."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
SC = ROOT / '.cache' / 'claude_scratch'
S1 = SC / 'item1_review'
LOGS = SC / 'nav_recheck_logs'
SUITE = ROOT / 'qa' / 'regression_runs' / '20261004_150758_quick'
stage = Path(sys.argv[1])
if stage.exists():
    shutil.rmtree(stage)
for sub in ('tools', 'raw', 'raw/cases'):
    (stage / sub).mkdir(parents=True)
TEXT = {'.gd', '.py', '.sh', '.md', '.json', '.jsonl', '.log', '.txt', '.out'}
files = []


def put(src: Path, dst_rel: str):
    if not src.exists():
        raise SystemExit('missing ' + str(src))
    dst = stage / dst_rel
    if src.suffix.lower() in TEXT:
        text = src.read_bytes().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
        dst.write_bytes('\n'.join(line.rstrip(' \t') for line in text.split('\n')).encode('utf-8'))
    else:
        shutil.copy2(src, dst)
    files.append(dst_rel)


for name in ('mutate_rc.py', 'rc_matrix.sh', 'ref_fidelity_check.py', 'hazard_json_compare.py', 'make_rc_tables.py', 'stage_rc_evidence.py'):
    put(S1 / name, 'tools/' + name)
for name in ('rc_matrix.jsonl', 'rc_matrix.out', 'ref_fidelity.txt', 'hazard_json_compare.txt', 'hz_base1.json', 'hz_noblocker.json',
             'hz_smallbox.json', 'hz_smallbox_noblocker.json', 'mutations_rc.md'):
    put(LOGS / name, 'raw/' + name)
for log in sorted((LOGS / 'cases').glob('*.log')):
    put(log, 'raw/cases/' + log.name)
put(SUITE / 'SUMMARY_KO.md', 'raw/quick_89d30934_SUMMARY_KO.md')
put(SUITE / 'summary.json', 'raw/quick_89d30934_summary.json')
for name in ('combat_query_fastpath.log', 'hazard_expansion.log'):
    put(SUITE / 'logs' / name, 'raw/quick_89d30934_' + name)
put(SUITE / 'out' / 'hazard_expansion' / 'hazard_expansion.json', 'raw/quick_89d30934_hazard_expansion.json')
manifest = {
    'review': 'N-1 re-check: Codex 89d30934 (B-3 combat_query_fastpath, B-4 hazard_expansion)',
    'files': [{'path': p, 'sha256': hashlib.sha256((stage / p).read_bytes()).hexdigest(), 'bytes': (stage / p).stat().st_size} for p in sorted(files)],
}
(stage / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print('staged %d files into %s' % (len(files), stage))
