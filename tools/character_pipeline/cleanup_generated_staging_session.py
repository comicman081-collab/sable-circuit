#!/usr/bin/env python3
"""Remove files from one explicitly named Codex generated-image session."""

from __future__ import annotations

import argparse
from pathlib import Path


ALLOWED_ROOT = Path("C:/Users/AAA/.codex/generated_images").resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session_id")
    args = parser.parse_args()
    if not args.session_id or any(char not in "0123456789abcdef-" for char in args.session_id.lower()):
        raise SystemExit("invalid generated-image session id")
    target = (ALLOWED_ROOT / args.session_id).resolve()
    if target.parent != ALLOWED_ROOT or target.name != args.session_id or not target.is_dir():
        raise SystemExit(f"refusing unexpected staging target: {target}")
    files = [path for path in target.iterdir() if path.is_file()]
    if any(path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"} for path in files):
        raise SystemExit("refusing session with non-image files")
    for path in files:
        path.unlink()
    print(f"GENERATED_STAGING_CLEANUP_PASS={target}")
    print(f"REMOVED_FILES={len(files)}")
    print(f"REMAINING_FILES={sum(1 for path in target.iterdir() if path.is_file())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
