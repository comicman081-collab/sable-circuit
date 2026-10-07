"""Final deletion for the 2026-10-02 cleanup. The USER runs this; Claude does not.

The user asked for the useless files in the C: temp folder and in the project folder to go.
Claude moved the project's scratch media into _retired_20261002/ (retire_20261002.py, manifest
qa/asset_cleanup_20261002/retirement_manifest.jsonl) and does not delete anything permanently,
so the permanent step is this script:

    python tools/maintenance/purge_20261002.py            # dry run: prints what would go
    python tools/maintenance/purge_20261002.py --apply    # deletes

It removes
  1. the project's _retired_20261002/ folder;
  2. entries directly inside %LOCALAPPDATA%\\Temp whose newest file is at least --temp-days (2) old,
     except claude\\ (Claude Code session scratch: other projects' sessions may be live).
Links and junctions are never followed, and files that are locked (in use) are skipped and counted.
"""
import argparse
import os
import shutil
import stat
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / '_retired_20261002'
TEMP_KEEP = {'claude'}


def is_link(path: Path) -> bool:
    if path.is_symlink() or os.path.isjunction(path):
        return True
    try:
        return bool(os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def newest_and_size(path: Path) -> tuple[float, int]:
    """Newest modification time and total bytes of a file or of everything below a folder."""
    info = os.lstat(path)
    if not path.is_dir() or is_link(path):
        return info.st_mtime, info.st_size
    newest, size = info.st_mtime, 0
    for base, _dirs, names in os.walk(path):
        for name in names:
            try:
                item = os.lstat(os.path.join(base, name))
            except OSError:
                continue
            newest = max(newest, item.st_mtime)
            size += item.st_size
    return newest, size


def _clear_readonly_and_retry(function, target, _error) -> None:
    os.chmod(target, stat.S_IWRITE)
    function(target)


def remove(path: Path) -> bool:
    """Delete a file or folder; False when something is locked and stays behind."""
    try:
        if path.is_dir() and not is_link(path):
            shutil.rmtree(path, onexc=_clear_readonly_and_retry)
        else:
            os.chmod(path, stat.S_IWRITE)
            path.unlink()
    except OSError:
        pass
    return not os.path.lexists(path)


def free_gb(path: str) -> float:
    return shutil.disk_usage(path).free / 1073741824


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--apply', action='store_true', help='delete (default is a dry run)')
    parser.add_argument('--temp-days', type=float, default=2.0)
    args = parser.parse_args()
    cutoff = time.time() - args.temp_days * 86400
    mode = 'DELETING' if args.apply else 'dry run'
    print(f'[{mode}] free before: C: {free_gb("C:/"):.1f} GB, D: {free_gb(str(ROOT)):.1f} GB')

    failed = 0
    if DEST.is_dir() and DEST.parent == ROOT and DEST.name == '_retired_20261002':
        count = size = 0
        for base, _dirs, names in os.walk(DEST):
            for name in names:
                count += 1
                size += os.lstat(os.path.join(base, name)).st_size
        print(f'project: {DEST.name}/  {size / 1073741824:.2f} GB in {count} files')
        if args.apply and not remove(DEST):
            failed += 1
            print('  part of it is locked and stays; run again after closing the program that holds it')
    else:
        print('project: _retired_20261002/ not found (already purged?)')

    temp = Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp'
    if not temp.is_dir():
        print('temp: %LOCALAPPDATA%\\Temp not found')
        return 1
    picked: list[tuple[Path, float, int]] = []
    for entry in sorted(temp.iterdir()):
        if entry.name in TEMP_KEEP or is_link(entry):
            continue
        try:
            newest, size = newest_and_size(entry)
        except OSError:
            continue
        if newest < cutoff:
            picked.append((entry, newest, size))
    total = sum(size for _entry, _newest, size in picked)
    print(f'temp: {len(picked)} entries ({total / 1048576:.0f} MB) untouched for {args.temp_days:g}+ days; kept: claude\\')
    for entry, newest, size in sorted(picked, key=lambda item: -item[2])[:8]:
        print(f'  {size / 1048576:8.1f} MB  {(time.time() - newest) / 86400:5.1f} d  {entry.name}')
    if args.apply:
        left = [entry.name for entry, _newest, _size in picked if not remove(entry)]
        print(f'temp: removed {len(picked) - len(left)}, skipped (in use) {len(left)}')
        failed += bool(left)
    print(f'[{mode}] free after:  C: {free_gb("C:/"):.1f} GB, D: {free_gb(str(ROOT)):.1f} GB')
    if not args.apply:
        print('Nothing was deleted. Add --apply to delete.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
