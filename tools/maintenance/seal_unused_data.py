"""Hash a reviewed cleanup plan and verify its isolated payload; never delete.

The separately bounded PowerShell helper is the only mover/deleter. This
one-off retirement applies to the user's explicit 2026-09-11 cleanup request.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import time
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'qa/asset_cleanup_20260911'
PAYLOAD = ROOT / 'quarantine_cleanup/20260911_unused_data/payload'
SCOPES = ['artifacts', 'art_src/characters/mica',
          'art_src/characters/_technical_generation_requests', 'art_src/pilot_v2',
          'motion_lab_v1/experiments', 'motion_lab_v1/art/aster/previous',
          'motion_lab_v1/qa', 'assets/units/operators/mica/fast_runtime_v1']


def read(name):
    return json.loads((REPORT / name).read_text(encoding='utf-8-sig'))


def write(name, value):
    (REPORT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(relative, base=ROOT):
    path = base / relative
    if not path.resolve().is_relative_to(base.resolve()) or Path(relative).is_absolute():
        raise ValueError(f'Escaping path: {relative}')
    for parent in [path, *path.parents]:
        if parent == base:
            break
        if parent.exists() and parent.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f'Reparse point: {parent}')
    return path


def hash_rows(rows, base):
    def one(row):
        path = checked(row['path'], base)
        if path.stat().st_size != row['bytes']:
            raise ValueError(f'Changed length: {row["path"]}')
        return {**row, 'sha256': sha(path)}
    result = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, row in enumerate(pool.map(one, rows), 1):
            result.append(row)
            if i % 5000 == 0:
                print(f'Hashed {i}/{len(rows)}', flush=True)
    return result


def prepare():
    if (REPORT / 'retirement_manifest.json').exists():
        raise ValueError('Sealed manifest already exists; do not overwrite retirement evidence')
    plan = read('retirement_plan.json')
    names = {row['path'] for row in plan}
    if len(names) != len(plan):
        raise ValueError('Duplicate retirement paths')
    for row in plan:
        name = row['path']
        if not any(name.startswith(scope + '/') for scope in SCOPES) and '/__pycache__/' not in name:
            raise ValueError(f'Out of retirement scope: {name}')
        if Path(name).suffix.lower() in {'.exe', '.dll', '.safetensors', '.ckpt', '.pth', '.pt', '.onnx'}:
            raise ValueError(f'Immutable runtime/weight may not be retired: {name}')

    # Original local/imported assets remain untouched; these two are archived
    # duplicate copies only. Verify their actual retained originals first.
    prefix = 'artifacts/generation_authorization_archives/mica_r6/root/'
    for row in plan:
        name = row['path']
        if name.startswith(prefix) and Path(name).suffix.lower() == '.glb':
            if sha(checked(name)) != sha(checked(name[len(prefix):])):
                raise ValueError(f'Archived reference differs from retained original: {name}')

    protected = {row['path'] for row in read('protected_candidates.json')}
    for prefix in ['scripts', 'scenes', 'assets', 'data', 'schemas',
                   'motion_lab_v1/art', 'motion_lab_v1/derived',
                   'motion_lab_v1/reference', 'motion_lab_v1/public',
                   'motion_lab_v1/dist', 'motion_lab_v1/characters']:
        protected.update(p.relative_to(ROOT).as_posix() for p in (ROOT / prefix).rglob('*') if p.is_file())
    protected.add('project.godot')
    protected.difference_update(names)
    # Live local-preview logs are preserved but may append during validation.
    protected = {n for n in protected if not (n.startswith('motion_lab_v1/qa/') and n.endswith('.log'))}
    before = hash_rows([{'path': name, 'bytes': checked(name).stat().st_size}
                        for name in sorted(protected)], ROOT)
    write('protected_before.json', before)
    print(f'Protected snapshot: {len(before)} files', flush=True)
    sealed = hash_rows(plan, ROOT)
    write('retirement_manifest.json', sealed)

    # Collapse only complete retired subtrees. Any retained or newly added file
    # prevents moving the parent directory, including hidden filesystem entries.
    def cluster(path):
        relative = path.relative_to(ROOT).as_posix()
        if path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            return False, []
        if path.is_file():
            return (True, [{'path': relative, 'kind': 'file'}]) if relative in names else (False, [])
        children = [cluster(child) for child in path.iterdir()]
        groups = [group for _, rows in children for group in rows]
        if children and all(full for full, _ in children) and groups:
            return True, [{'path': relative, 'kind': 'directory'}]
        return False, groups

    roots = list(SCOPES)
    for name in names:
        if not any(name.startswith(scope + '/') for scope in roots):
            roots.append(name.split('/__pycache__/')[0] + '/__pycache__')
    groups = [group for scope in roots if (ROOT / scope).exists() for group in cluster(ROOT / scope)[1]]
    write('move_groups.json', groups)
    receipt = {'status': 'SEALED_NOT_MOVED', 'userAuthorizationDate': '2026-09-11',
               'fileCount': len(sealed), 'bytes': sum(r['bytes'] for r in sealed),
               'protectedFileCount': len(before), 'groupCount': len(groups),
               'manifestSHA256': sha(REPORT / 'retirement_manifest.json'),
               'groupsSHA256': sha(REPORT / 'move_groups.json'),
               'protectedSHA256': sha(REPORT / 'protected_before.json')}
    write('seal.json', receipt)
    print(json.dumps(receipt), flush=True)


def verify(stage):
    seal = read('seal.json')
    for name, key in [('retirement_manifest.json', 'manifestSHA256'),
                      ('move_groups.json', 'groupsSHA256'), ('protected_before.json', 'protectedSHA256')]:
        if sha(REPORT / name) != seal[key]:
            raise ValueError(f'Seal mismatch: {name}')
    failures = []
    before = read('protected_before.json')
    after = hash_rows(before, ROOT)
    failures.extend(row['path'] for row, old in zip(after, before) if row['sha256'] != old['sha256'])
    rows = read('retirement_manifest.json')
    # Paths were boundary/reparse-checked at sealing, and the immutable seal is
    # verified above. This is an existence-only check, not a file operation.
    failures.extend('original_still_present:' + row['path'] for row in rows if (ROOT / row['path']).exists())
    if stage == 'quarantined':
        actual = {p.relative_to(PAYLOAD).as_posix() for p in PAYLOAD.rglob('*') if p.is_file()}
        expected = {row['path'] for row in rows}
        failures.extend('unexpected_payload:' + name for name in actual - expected)
        failures.extend('missing_payload:' + name for name in expected - actual)
        hashed = hash_rows(rows, PAYLOAD)
        failures.extend('payload_hash:' + row['path'] for row, old in zip(hashed, rows) if row['sha256'] != old['sha256'])
    elif PAYLOAD.exists():
        failures.append('Payload not deleted')
    result = {'status': 'PASS' if not failures else 'FAIL', 'stage': stage,
              'checkedAt': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
              'retiredFileCount': len(rows), 'retiredBytes': seal['bytes'],
              'protectedFileCount': len(before), 'failures': failures,
              'manifestSHA256': seal['manifestSHA256']}
    write(stage + '_verification.json', result)
    print(json.dumps(result), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['prepare', 'quarantined', 'purged'])
    parser.add_argument('--batch', default='asset_cleanup_20260911')
    args = parser.parse_args()
    if not re.fullmatch(r'asset_cleanup_[a-z0-9_]+', args.batch):
        raise ValueError('Invalid cleanup batch')
    REPORT = ROOT / 'qa' / args.batch
    if args.batch != 'asset_cleanup_20260911':
        PAYLOAD = ROOT / 'quarantine_cleanup' / args.batch / 'payload'
    prepare() if args.phase == 'prepare' else verify(args.phase)
