"""Quarantine only unreachable Git objects while preserving refs/reflogs/indexes.

No history rewriting, reflog expiry, branch deletion, reset, or network operation.
Git's own repack --expire-to writes pruned objects to a project-local backup.
Permanent disposal is a separate verified PowerShell operation.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'qa/asset_cleanup_20260911_additional'
QUARANTINE = ROOT / 'quarantine_cleanup/asset_cleanup_20260911_additional/git_cruft'
ENV = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0', 'PYTHONDONTWRITEBYTECODE': '1'}


def git(*args, input=None):
    result = subprocess.run(['git', *args], cwd=ROOT, env=ENV, input=input,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.decode('utf-8', errors='replace').strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, value):
    (REPORT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def read(name):
    return json.loads((REPORT / name).read_text(encoding='utf-8'))


def control_files():
    paths = [ROOT / '.git' / name for name in ['HEAD', 'index', 'ORIG_HEAD', 'config']]
    paths += list((ROOT / '.git/logs').rglob('*'))
    for worktree in (ROOT / '.git/worktrees').iterdir():
        paths += [worktree / name for name in ['HEAD', 'index', 'ORIG_HEAD', 'gitdir', 'commondir']]
        paths += list((worktree / 'logs').rglob('*'))
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths if p.is_file()}


def git_bytes():
    return sum(p.stat().st_size for p in (ROOT / '.git').rglob('*') if p.is_file())


def quarantine_files():
    # This installed Git exposes --expire-to as a pack PREFIX (its local -h),
    # unlike the bundled older HTML manual's directory description. Support
    # both, and never accept an empty backup when objects were retired.
    return sorted(set([p for p in QUARANTINE.rglob('*') if p.is_file()] +
                      [p for p in QUARANTINE.parent.glob(QUARANTINE.name + '-*') if p.is_file()]))


def protected_ids():
    return sorted(set(git('rev-list', '--objects', '--all', '--reflog', '--indexed-objects', '--no-object-names').splitlines()))


def audit():
    REPORT.mkdir(parents=True, exist_ok=True)
    if (REPORT / 'git_before.json').exists():
        raise ValueError('Do not overwrite Git pre-retirement snapshot')
    objects = {}
    for line in git('cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize) %(objectsize:disk)').splitlines():
        oid, kind, logical, physical = line.split()
        objects[oid] = {'oid': oid, 'type': kind, 'bytes': int(logical), 'diskBytes': int(physical)}
    protected = protected_ids()
    protected_set = set(protected)
    retired = [row for oid, row in objects.items() if oid not in protected_set]
    write('git_protected_objects.json', protected)
    write('git_unreachable_objects.json', retired)
    before = {'refs': git('for-each-ref', '--format=%(refname) %(objectname)'),
              'worktrees': git('worktree', 'list', '--porcelain'), 'controlFiles': control_files(),
              'gitBytes': git_bytes(), 'protectedObjects': len(protected),
              'unreachableObjects': len(retired), 'unreachableDiskBytes': sum(r['diskBytes'] for r in retired),
              'capturedAt': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    write('git_before.json', before)
    with (REPORT / 'git_connectivity_before.log').open('w', encoding='utf-8') as out:
        result = subprocess.run(['git', 'fsck', '--connectivity-only', '--no-dangling'], cwd=ROOT, env=ENV,
                                stdout=out, stderr=subprocess.STDOUT)
    if result.returncode:
        raise ValueError('Pre-existing Git connectivity failure; stop before repack')
    print(json.dumps({k: v for k, v in before.items() if k not in ['refs', 'worktrees', 'controlFiles']}), flush=True)


def repack():
    before = read('git_before.json')
    if QUARANTINE.exists():
        raise ValueError('Quarantine exists; inspect previous operation')
    if before['refs'] != git('for-each-ref', '--format=%(refname) %(objectname)') or before['controlFiles'] != control_files():
        raise ValueError('Repository control data changed since audit')
    locks = list((ROOT / '.git').rglob('*.lock'))
    if locks:
        raise ValueError(f'Git lock present: {locks}')
    QUARANTINE.mkdir(parents=True)
    command = ['git', '-c', 'pack.threads=2', '-c', 'gc.reflogExpire=never',
               '-c', 'gc.reflogExpireUnreachable=never', 'repack', '-a', '-d', '-m',
               '--cruft', '--cruft-expiration=now', '--window-memory=128m',
               '--expire-to=' + str(QUARANTINE)]
    write('git_repack_command.json', command)
    with (REPORT / 'git_repack.log').open('w', encoding='utf-8') as out:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=out, stderr=subprocess.STDOUT)
    if result.returncode:
        raise ValueError('Repack failed; preserve quarantine and inspect log')
    verify()


def verify(purged=False):
    before = read('git_before.json')
    protected = read('git_protected_objects.json')
    errors = []
    if before['refs'] != git('for-each-ref', '--format=%(refname) %(objectname)'):
        errors.append('Branch/tag/checkpoint ref changed')
    if before['worktrees'] != git('worktree', 'list', '--porcelain'):
        errors.append('Worktree HEAD or registration changed')
    if before['controlFiles'] != control_files():
        errors.append('Index/reflog/HEAD/config bytes changed')
    response = git('cat-file', '--batch-check=%(objectname) %(objecttype)',
                   input=('\n'.join(protected) + '\n').encode())
    if ' missing' in response or len(response.splitlines()) != len(protected):
        errors.append('A previously referenced object is missing')
    with (REPORT / 'git_connectivity_after.log').open('w', encoding='utf-8') as out:
        result = subprocess.run(['git', 'fsck', '--connectivity-only', '--no-dangling'], cwd=ROOT, env=ENV,
                                stdout=out, stderr=subprocess.STDOUT)
    if result.returncode:
        errors.append('Git connectivity check failed')
    if purged:
        if quarantine_files():
            errors.append('Git pack quarantine remains after purge')
        for row in read('git_loose_retirement.json'):
            if (ROOT / row['path']).exists() or (ROOT / row['quarantinePath']).exists():
                errors.append('Retired loose/temporary Git file remains: ' + row['path'])
        receipt = {'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
                   'beforeGitBytes': before['gitBytes'], 'afterGitBytes': git_bytes(),
                   'gitBytesReclaimed': before['gitBytes'] - git_bytes(),
                   'protectedObjectsVerified': len(protected), 'historyRewritten': False,
                   'refsReflogsIndexesUnchanged': not errors,
                   'countObjects': git('count-objects', '-vH')}
        write('git_final_verification.json', receipt)
        print(json.dumps(receipt), flush=True)
        if errors:
            raise SystemExit(1)
        return
    protected_set = set(protected)
    quarantined_ids = set()
    archived = quarantine_files()
    for idx in [p for p in archived if p.suffix == '.idx']:
        for line in git('show-index', input=idx.read_bytes()).splitlines():
            quarantined_ids.add(line.split()[1])
    if quarantined_ids & protected_set:
        errors.append('Quarantine contains a protected object')
    retired_set = {row['oid'] for row in read('git_unreachable_objects.json')}
    if quarantined_ids - retired_set:
        errors.append('Quarantine contains objects not in the original unreachable audit')
    if before['unreachableObjects'] and not quarantined_ids:
        errors.append('Expected unreachable-object backup was not found')
    rows = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)}
            for p in archived]
    write('git_quarantine_manifest.json', rows)
    receipt = {'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
               'beforeGitBytes': before['gitBytes'], 'afterGitBytes': git_bytes(),
               'quarantinedObjects': len(quarantined_ids), 'quarantinedBytes': sum(r['bytes'] for r in rows),
               'protectedObjectsVerified': len(protected), 'historyRewritten': False,
               'refsReflogsIndexesUnchanged': not errors}
    write('git_quarantine_verification.json', receipt)
    print(json.dumps(receipt), flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['audit', 'repack', 'verify', 'verify-purged'])
    args = parser.parse_args()
    {'audit': audit, 'repack': repack, 'verify': verify,
     'verify-purged': lambda: verify(purged=True)}[args.phase]()
