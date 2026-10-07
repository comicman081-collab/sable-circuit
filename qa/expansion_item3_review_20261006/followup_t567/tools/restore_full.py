"""Claude scratch (T-5/T-6/T-7): copy the tested full state back and prove it is byte-identical (git blob hashes).
usage: python -B restore_full.py [path ...]   (no argument: all five files)"""
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BK = ROOT / ".cache/claude_scratch/t567/state_full"
tested = {}
for line in (ROOT / ".cache/claude_scratch/t567/tested_blobs.txt").read_text(encoding="utf-8").splitlines():
    sha, path = line.split(None, 1)
    tested[path.strip()] = sha


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


rels = sys.argv[1:] or list(tested)
for rel in rels:
    shutil.copy2(BK / rel, ROOT / rel)
    ok = blob(ROOT / rel) == tested[rel]
    print("%s  %s" % ("RESTORED_EQUAL" if ok else "MISMATCH", rel))
    assert ok
