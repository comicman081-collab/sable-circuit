"""Check that every picture the user approved on 2026-10-07 still has the approved SHA-256 (Claude, 2026-10-07).

    python qa/art_approval_20261007/tools/verify_hashes.py

Exit 0 when every approved file is present and unchanged, 1 otherwise. A mismatch is not a game error: the file is new
art the user has not seen, so the approval no longer covers it (AGENTS.md, "All shipped art approved"). Pictures that
are tracked now but are not in the record are listed as NEW; they are not approved either, but adding a picture is not a
failure here. It only reads files; it writes nothing."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path(__file__).resolve().parents[1] / 'approved_art.json'
ROOTS = ['assets', 'motion_lab_v1/public/assets/atlas']
EXTS = ('.png', '.webp')


def tracked_pictures():
    out = subprocess.run(['git', 'ls-files', '-z', '--'] + ROOTS, cwd=ROOT, capture_output=True, check=True).stdout
    return {p for p in out.decode('utf-8').split('\0') if p.lower().endswith(EXTS)}


def main() -> int:
    record = json.loads(RECORD.read_text(encoding='utf-8'))
    bad = 0
    for row in record['files']:
        path = ROOT / row['path']
        if not path.is_file():
            print('MISSING  %s' % row['path'])
            bad += 1
            continue
        now = hashlib.sha256(path.read_bytes()).hexdigest()
        if now != row['sha256']:
            print('CHANGED  %s  approved %s  now %s' % (row['path'], row['sha256'][:12], now[:12]))
            bad += 1
    new = sorted(tracked_pictures() - {row['path'] for row in record['files']})
    for path in new:
        print('NEW      %s  (not approved)' % path)
    print('%d of %d approved files unchanged; %d new picture(s) not covered' % (len(record['files']) - bad, len(record['files']), len(new)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
