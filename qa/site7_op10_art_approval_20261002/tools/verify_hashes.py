"""Check that every file the user approved on 2026-10-02 still has the approved SHA-256 (Claude, 2026-10-02).

    python qa/site7_op10_art_approval_20261002/tools/verify_hashes.py

Exit 0 when all match, 1 otherwise. A mismatch is not a game error: the file is new art the user has not seen, so the
approval no longer covers it (AGENTS.md, "Operation 10 art approved"). It only reads files; it writes nothing."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path(__file__).resolve().parents[1] / 'approved_art.json'


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
    print('%d of %d approved files unchanged' % (len(record['files']) - bad, len(record['files'])))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
