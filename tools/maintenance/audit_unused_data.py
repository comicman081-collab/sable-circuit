"""Plan retirement of abandoned SABLE output, never mutate source/runtime inputs.

Run from the repository. The explicit 2026-09-11 cleanup request authorizes
retirement of unused historical output, including rejected production lines.
PowerShell performs the separately reviewed, exact-manifest moves/deletions.
"""
from pathlib import Path
import collections
import hashlib
import json
import os
import re
import stat

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'qa/asset_cleanup_20260911'
if (OUT / 'seal.json').exists():
    raise SystemExit('This retirement is sealed. Preserve its evidence; use a new dated audit for any later request.')
EXCLUDED = {'.git', '.godot', 'tools', 'third_party',
            'Sable-circuit-combat-vfx', 'Sable-circuit-site7-environment-art',
            'Sable-circuit-system', 'quarantine_cleanup'}
files = {}
links = []
for directory, names, filenames in os.walk(ROOT, followlinks=False):
    base = Path(directory)
    names[:] = [name for name in names if name not in EXCLUDED]
    for name in list(names):
        path = base / name
        if path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            links.append(path.relative_to(ROOT).as_posix())
            names.remove(name)
    for name in filenames:
        path = base / name
        if path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            links.append(path.relative_to(ROOT).as_posix())
            continue
        relative = path.relative_to(ROOT).as_posix()
        files[relative] = {'bytes': path.stat().st_size}

protected = {}
queue = collections.deque()
parsed = set()
def protect(path, reason, follow=True):
    if path not in files:
        return
    if path not in protected:
        protected[path] = reason
    if follow and Path(path).suffix.lower() in {'.json', '.gd', '.tscn', '.tres'} and path not in parsed:
        queue.append(path)

def prefix(path, reason, follow=True):
    for name in files:
        if name == path or name.startswith(path.rstrip('/') + '/'):
            protect(name, reason, follow)

# Current executable code, app assets, live data and current character factory.
for name in ['scripts', 'scenes', 'assets', 'schemas', 'art_src/environments',
             'art_src/characters/rook', 'art_src/motion_reference']:
    prefix(name, 'runtime_or_active_production')
for name in files:
    if name.startswith('data/'):
        protect(name, 'game_data', name != 'data/character_pipeline/mica_runtime.json')
for name in ['motion_lab_v1/characters', 'motion_lab_v1/derived',
             'motion_lab_v1/reference', 'motion_lab_v1/public', 'motion_lab_v1/dist']:
    prefix(name, 'current_motion_studio')
for name in files:
    if name.startswith('motion_lab_v1/art/') and '/previous/' not in name:
        protect(name, 'current_source_master_and_provenance')
    if name.startswith('motion_lab_v1/qa/') and not any('/' + token + '/' in name for token in [
            'build_candidates', 'build_previous', 'package_history', 'chrome_tmp_profile',
            'chrome_tmp_profile2', 'chrome_tmp_profile3', 'chrome_tmp_profile4',
            'technical_tests', 'tmp']):
        protect(name, 'motion_review_and_source_evidence')
    if name.startswith('art_src/pilot_v2/') and Path(name).suffix.lower() in {'.py', '.ps1'}:
        protect(name, 'retained_implementation')
    if name.startswith('artifacts/rook_'):
        protect(name, 'connected_rook_review_evidence')
    if name.startswith('artifacts/') and Path(name).suffix.lower() == '.md':
        protect(name, 'historical_review_summary', False)
protect('artifacts/quarantine/motion_rejections.json', 'rejection_hash_blacklist', False)

# Keep exactly the newest pre-current compiled atlas and offline HTML for rollback.
for family in ['build_previous', 'package_history']:
    parent = ROOT / 'motion_lab_v1/qa' / family
    if parent.exists():
        for character in parent.iterdir():
            if not character.is_dir():
                continue
            entries = list(character.iterdir())
            if entries:
                latest = max(entries, key=lambda p: p.stat().st_mtime_ns)
                prefix(latest.relative_to(ROOT).as_posix(), 'immediately_previous_package')

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)

root_string = ROOT.as_posix().lower()
def resolve_reference(value, source):
    value = value.replace('\\', '/').strip()
    if value.startswith('res://'):
        value = value[6:]
    if value.lower().startswith(root_string + '/'):
        value = value[len(root_string) + 1:]
    if re.match(r'^[a-zA-Z]:|^https?://|^data:', value) or len(value) > 1024:
        return []
    choices = [value]
    if source.startswith('motion_lab_v1/'):
        choices.insert(0, 'motion_lab_v1/' + value)
    choices.append((Path(source).parent / value).as_posix())
    for ancestor in Path(source).parents:
        choices.append((ancestor / value).as_posix())
    for candidate in choices:
        # No filesystem probing outside the already enumerated project inputs.
        normalized = os.path.normpath(candidate).replace('\\', '/')
        if normalized in files:
            return [normalized]
    return []

while queue:
    source = queue.popleft()
    if source in parsed:
        continue
    parsed.add(source)
    path = ROOT / source
    if path.suffix.lower() == '.json':
        try:
            values = strings(json.loads(path.read_text(encoding='utf-8-sig')))
        except (UnicodeError, ValueError):
            continue
    else:
        try:
            values = re.findall(r'["\']([^"\'\r\n]+)["\']', path.read_text(encoding='utf-8-sig'))
        except UnicodeError:
            continue
    for value in values:
        for target in resolve_reference(value, source):
            protect(target, 'dependency:' + source)

def reason(name):
    if name.startswith('art_src/characters/mica/'):
        return 'retired_pre_motion_studio_mica_pipeline'
    if name.startswith('art_src/characters/_technical_generation_requests/'):
        return 'obsolete_generation_request_fixture'
    if name.startswith('art_src/pilot_v2/'):
        return 'unreferenced_legacy_aster_production_intermediate'
    if name.startswith('artifacts/'):
        return 'unreferenced_legacy_capture_or_harness_output'
    if name.startswith('motion_lab_v1/experiments/'):
        return 'explicitly_retired_initial_experiment'
    if name.startswith('motion_lab_v1/art/aster/previous/'):
        return 'superseded_source_copy_no_current_dependency'
    if name.startswith('motion_lab_v1/qa/'):
        return 'obsolete_build_browser_cache_or_package_history'
    if '/__pycache__/' in name:
        return 'regenerable_python_bytecode'
    return None

retired = []
kept_candidates = []
for name, info in files.items():
    category = reason(name)
    if not category:
        continue
    if name in protected:
        kept_candidates.append({'path': name, **info, 'reason': protected[name]})
    else:
        retired.append({'path': name, **info, 'reason': category})

OUT.mkdir(parents=True, exist_ok=True)
def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

grouped = collections.defaultdict(lambda: {'files': 0, 'bytes': 0})
for row in retired:
    grouped[row['reason']]['files'] += 1
    grouped[row['reason']]['bytes'] += row['bytes']
summary = {
    'root': str(ROOT), 'authorization': '2026-09-11 explicit user request to quarantine and delete never-to-be-connected unused data',
    'scope': 'historical generated project output only; current sources, app dependencies, models/tools and other git worktrees protected',
    'status': 'AUDITED_NOT_MOVED', 'fileCount': len(retired),
    'bytes': sum(row['bytes'] for row in retired), 'categories': grouped,
    'protectedCandidateCount': len(kept_candidates), 'linksSkipped': links,
}
dump('audit_summary.json', summary)
dump('retirement_plan.json', retired)
dump('protected_candidates.json', kept_candidates)
print(json.dumps(summary, ensure_ascii=False, indent=2))
