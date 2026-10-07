"""Move scratch media and recorder intermediates into _retired_20261002/ (user instruction 2026-10-02).

The user asked for the useless files in the project folder (and in the C: temp folder) to go.
Nothing is deleted here: files are renamed into the git-ignored _retired_20261002/ on the same
drive, and the user runs tools/maintenance/purge_20261002.py (or deletes the folder) when they
are happy. Every moved file gets a SHA-256 row in
qa/asset_cleanup_20261002/retirement_manifest.jsonl.

Scope (nothing tracked is touched):
  * image and video files under .cache/ (Claude scratch, Codex diagnostics, old tmp), except
    Godot's user data, the redirected AppData folders and the Python bytecode prefix;
  * the native_readback.mkv / native_mix.avi intermediates of the video recorder under qa/
    (the 1080p mp4 deliverables and the SHA-256 in their capture.json stay).
Logs, JSON, scripts and notes in .cache/ stay.

Dry run by default; --apply moves.
"""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / '_retired_20261002'
MANIFEST = ROOT / 'qa/asset_cleanup_20261002/retirement_manifest.jsonl'
IMAGES = {'.png', '.webp', '.jpg', '.jpeg', '.gif'}
VIDEOS = {'.mp4', '.mkv', '.avi', '.webm', '.mov'}
MEDIA = IMAGES | VIDEOS
# Godot user data, the AppData folders the runner redirects Godot to, and the bytecode prefix.
KEEP_CACHE = {'Godot', 'godot_appdata', 'godot_localappdata', 'python'}
INTERMEDIATES = {'native_readback.mkv', 'native_mix.avi'}
# Another agent may be working in the tree: leave anything written in the last hour.
ACTIVE_SECONDS = 3600


def git_files() -> set[str]:
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'], capture_output=True, check=True).stdout
    return {p for p in out.decode('utf-8').split('\0') if p}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def files_under(path: Path):
    for base, _dirs, names in os.walk(path):
        for name in names:
            yield Path(base) / name


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def collect(since: float):
    tracked = git_files()
    rows: list[tuple[Path, str]] = []
    skipped: list[str] = []

    def take(file: Path, reason: str) -> None:
        path = rel(file)
        if file.is_symlink() or path in tracked:
            skipped.append(path)
        elif file.stat().st_mtime > since:
            skipped.append(path)
        else:
            rows.append((file, reason))

    cache = ROOT / '.cache'
    for entry in sorted(cache.iterdir()):
        if entry.name in KEEP_CACHE:
            continue
        for file in ([entry] if entry.is_file() else files_under(entry)):
            if file.suffix.lower() in MEDIA:
                take(file, f'cache/{entry.name}')
    for file in files_under(ROOT / 'qa'):
        if file.name in INTERMEDIATES and not rel(file).startswith('qa/regression_runs/'):
            take(file, 'qa_recorder_intermediate')
    return rows, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    rows, skipped = collect(time.time() - ACTIVE_SECONDS)

    totals: dict[str, list[int]] = {}
    for file, reason in rows:
        total = totals.setdefault(reason, [0, 0])
        total[0] += 1
        total[1] += file.stat().st_size
    for reason, (count, size) in sorted(totals.items(), key=lambda item: -item[1][1]):
        print(f'{size / 1048576:10.1f} MB {count:6d}  {reason}')
    print(f'{sum(t[1] for t in totals.values()) / 1048576:10.1f} MB total in {len(rows)} files; '
          f'skipped (recent, tracked or links): {len(skipped)}')
    if not args.apply:
        return 0

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    moved: list[dict] = []
    failures: list[dict] = []
    for file, reason in rows:
        row = {'path': rel(file), 'bytes': file.stat().st_size, 'sha256': sha256(file), 'reason': reason}
        target = DEST / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.rename(file, target)
            moved.append(row)
        except OSError as error:
            failures.append({'path': row['path'], 'error': str(error)})
    stamp = time.strftime('%Y-%m-%dT%H:%M:%S')
    with MANIFEST.open('w', encoding='utf-8', newline='\n') as handle:
        for row in moved:
            handle.write(json.dumps({**row, 'retired_to': rel(DEST / row['path']), 'at': stamp}, ensure_ascii=False) + '\n')
    print(f'moved {len(moved)}; failed {len(failures)}')
    for failure in failures:
        print('FAILED', failure)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
