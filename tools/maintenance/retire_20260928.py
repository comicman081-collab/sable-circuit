"""Move retired payloads into _retired_20260928/ (user instruction 2026-09-28).

The user asked for every unneeded asset and test copy to go, QA videos and the
Motion Studio test fixtures included. Nothing is deleted here: payloads are
renamed into the git-ignored _retired_20260928/ on the same drive and the user
deletes that folder. Files get a SHA-256 row; scratch folders (.cache, old
Claude worktrees, regression runs) get a file count and byte total.

Dry run by default; --apply moves and writes
qa/asset_cleanup_20260928/retirement_manifest.jsonl.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / '_retired_20260928'
MANIFEST = ROOT / 'qa/asset_cleanup_20260928/retirement_manifest.jsonl'
IMAGES = {'.png', '.webp', '.jpg', '.jpeg', '.gif'}
VIDEOS = {'.mp4', '.mkv', '.avi', '.webm', '.mov'}
MEDIA = IMAGES | VIDEOS | {'.html'}
# Another agent may be working in the tree: leave anything written in the last hour.
ACTIVE_SECONDS = 3600
# Godot user data and export templates, the web build temp dir, and Codex's live diagnostics.
KEEP_CACHE = {'Godot', 'tmp', 'sites_tmp', 'diag'}
MOTION_FIXTURES = [
    'motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json',
    'motion_lab_v1/qa/stage1_enemies_20260913/machine_edge_fixtures_v1/',
    'motion_lab_v1/qa/stage1_enemies_20260913/anchor/candidate_spec_v1.json',
    'motion_lab_v1/qa/stage_enemies_20260919/candidate_v1/',
]
FIXTURE_TESTS = [
    'tests/render/site7_machine_candidate_capture.gd',
    'tests/render/site7_machine_edge_case_smoke.gd',
]
# v1 plates: all five missions draw v2 plates. The base lobby still shows one v1 plate,
# and the v1 props, room outlines and quality reference stay.
V1_ASSETS_KEEP = ('assets/environments/site7/karchive_props_v1/', 'assets/environments/site7/props/',
                  'assets/environments/site7/room_art/',
                  'assets/environments/site7/stage02/reserve_field_cache/S02_07_RESERVE_FIELD_CACHE_CONTINUITY.png')
V1_SOURCE_KEEP = ('art_src/environments/site7/references/', 'art_src/environments/site7/stage02/reserve_field_cache/')
ATTEMPT = re.compile(r'_attempt\d\d_RAW_NATIVE\.png$')


def git_files(*args: str) -> set[str]:
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', *args], capture_output=True, check=True).stdout
    return {p for p in out.decode('utf-8').split('\0') if p}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def files_under(path: Path):
    for base, _dirs, names in os.walk(path):
        for name in names:
            yield Path(base) / name


def recently_written(path: Path, since: float) -> bool:
    if path.is_file():
        return path.stat().st_mtime > since
    for file in files_under(path):
        try:
            if file.stat().st_mtime > since:
                return True
        except OSError:
            pass
    return False


def doc_referenced_media() -> set[str]:
    pattern = re.compile(r'(?:motion_lab_v1/)?qa/[A-Za-z0-9_./-]+\.(?:png|webp|jpe?g|gif|html|mp4)')
    found: set[str] = set()
    for base in [ROOT / 'docs', ROOT / '.agents']:
        for file in files_under(base):
            if file.suffix == '.md':
                found.update(pattern.findall(file.read_text(encoding='utf-8', errors='ignore')))
    for name in ['AGENTS.md', 'CLAUDE.md']:
        if (ROOT / name).exists():
            found.update(pattern.findall((ROOT / name).read_text(encoding='utf-8', errors='ignore')))
    return found


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def collect(since: float):
    tracked = git_files()
    dirs: list[tuple[Path, str]] = []
    files: list[tuple[Path, str]] = []
    skipped: list[str] = []

    cache = ROOT / '.cache'
    for entry in sorted(cache.iterdir()):
        if entry.name in KEEP_CACHE:
            continue
        if recently_written(entry, since):
            skipped.append(rel(entry))
            continue
        (dirs if entry.is_dir() else files).append((entry, 'cache'))
    worktrees = ROOT / '.claude/worktrees'
    if worktrees.exists():
        for entry in sorted(worktrees.iterdir()):
            if recently_written(entry / '.git', since):
                skipped.append(rel(entry))
                continue
            dirs.append((entry, 'old_claude_worktree'))
    runs = ROOT / 'qa/regression_runs'
    if runs.exists():
        for entry in sorted(runs.iterdir()):
            if recently_written(entry, since):
                skipped.append(rel(entry))
                continue
            (dirs if entry.is_dir() else files).append((entry, 'regression_run'))

    keep_media = doc_referenced_media()
    for file in files_under(ROOT / 'qa'):
        path = rel(file)
        if path.startswith('qa/regression_runs/') or file.suffix.lower() not in MEDIA or path in keep_media:
            continue
        if file.stat().st_mtime > since:
            skipped.append(path)
            continue
        files.append((file, 'qa_video' if file.suffix.lower() in VIDEOS else 'qa_capture'))

    motion_qa = ROOT / 'motion_lab_v1/qa'
    fixture_files: set[Path] = set()
    for file in files_under(motion_qa):
        if file.suffix.lower() in MEDIA:
            fixture_files.add(file)
    for item in MOTION_FIXTURES:
        path = ROOT / item
        if path.is_dir():
            fixture_files.update(files_under(path))
        elif path.exists():
            fixture_files.add(path)
    files.extend((file, 'motion_studio_test_fixture') for file in sorted(fixture_files))
    files.extend((ROOT / item, 'fixture_only_test') for item in FIXTURE_TESTS if (ROOT / item).exists())

    v2 = ROOT / 'art_src/environments/site7_v2'
    for file in files_under(v2):
        path = rel(file)
        in_holding = '/_quarantine/' in path or '/_superseded/' in path
        if in_holding and file.suffix.lower() in IMAGES:
            files.append((file, 'rejected_or_superseded_plate'))
        elif ATTEMPT.search(path):
            files.append((file, 'plate_generation_attempt'))

    for file in files_under(ROOT / 'art_src/environments/site7'):
        path = rel(file)
        if file.suffix.lower() in IMAGES and not path.startswith(V1_SOURCE_KEEP):
            files.append((file, 'v1_plate_source'))
    for file in files_under(ROOT / 'assets/environments/site7'):
        path = rel(file)
        image = path.removesuffix('.import')
        if Path(image).suffix.lower() in IMAGES and not path.startswith(V1_ASSETS_KEEP):
            files.append((file, 'v1_plate_runtime'))
    return tracked, dirs, files, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    since = time.time() - ACTIVE_SECONDS
    tracked, dirs, files, skipped = collect(since)

    rows: list[dict] = []
    totals: dict[str, list[int]] = {}
    for path, reason in dirs:
        count = size = 0
        for file in files_under(path):
            try:
                size += file.stat().st_size
                count += 1
            except OSError:
                pass
        rows.append({'path': rel(path), 'kind': 'dir', 'files': count, 'bytes': size, 'reason': reason})
    for path, reason in files:
        rows.append({'path': rel(path), 'kind': 'file', 'bytes': path.stat().st_size, 'tracked': rel(path) in tracked,
                     'reason': reason})
    for row in rows:
        total = totals.setdefault(row['reason'], [0, 0])
        total[0] += row.get('files', 1)
        total[1] += row['bytes']
    for reason, (count, size) in sorted(totals.items(), key=lambda item: -item[1][1]):
        print(f'{size / 1048576:10.1f} MB {count:7d}  {reason}')
    print(f'{sum(t[1] for t in totals.values()) / 1048576:10.1f} MB total; '
          f'{sum(1 for r in rows if r.get("tracked"))} tracked files; skipped (recent): {skipped}')
    if not args.apply:
        return 0

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    moved = []
    for row in rows:
        source = ROOT / row['path']
        if row['kind'] == 'file':
            row['sha256'] = sha256(source)
        target = DEST / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.rename(source, target)
            moved.append(row)
        except OSError as error:
            failures.append({'path': row['path'], 'error': str(error)})
    stamp = time.strftime('%Y-%m-%dT%H:%M:%S')
    with MANIFEST.open('w', encoding='utf-8', newline='\n') as handle:
        for row in moved:
            handle.write(json.dumps({**row, 'retired_to': rel(DEST / row['path']), 'at': stamp}, ensure_ascii=False) + '\n')
    (MANIFEST.parent / 'tracked_removed.txt').write_text(
        ''.join(row['path'] + '\n' for row in moved if row.get('tracked')), encoding='utf-8', newline='\n')
    print(f'moved {len(moved)}; failed {len(failures)}')
    for failure in failures:
        print('FAILED', failure)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
