"""Second cleanup: current production dependencies, not historical evidence cycles."""
from pathlib import Path
import collections
import json
import os
import re
import stat
import argparse

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--batch', default='asset_cleanup_20260911_additional')
args = parser.parse_args()
if not re.fullmatch(r'asset_cleanup_[a-z0-9_]+', args.batch):
    raise ValueError('Invalid batch')
OUT = ROOT / 'qa' / args.batch
if (OUT / 'seal.json').exists():
    raise SystemExit('Already sealed; do not overwrite this cleanup evidence')
EXCLUDED = {'.git', '.godot', 'tools', 'third_party', 'quarantine_cleanup',
            'Sable-circuit-combat-vfx', 'Sable-circuit-system', 'Sable-circuit-site7-environment-art'}
files = {}
for directory, names, filenames in os.walk(ROOT, followlinks=False):
    base = Path(directory)
    names[:] = [n for n in names if n not in EXCLUDED and not
                ((base / n).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
    for name in filenames:
        path = base / name
        if path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f'Reparse file: {path}')
        files[path.relative_to(ROOT).as_posix()] = path.stat().st_size

protected = {}
queue = collections.deque()
parsed = set()


def keep(name, why, follow=True):
    if name not in files:
        return
    protected.setdefault(name, why)
    if follow and name.endswith(('.json', '.gd', '.tscn', '.tres', '.js')) and name not in parsed:
        queue.append(name)


def tree(prefix, why, follow=True):
    for name in files:
        if name == prefix or name.startswith(prefix + '/'):
            keep(name, why, follow)


for prefix in ['scripts', 'scenes', 'data', 'schemas', 'assets', 'art_src/environments',
               'art_src/characters/rook', 'art_src/motion_reference']:
    # Original motion references remain, but old diagnostic reports do not make
    # their rejected renders a dependency of today's UAL-only Motion Studio.
    tree(prefix, 'current_app_or_retained_original', follow=prefix != 'art_src/motion_reference')
for name in list(protected):
    if name.startswith('assets/units/operators/mica/fast_runtime_v1/'):
        del protected[name]
queue = collections.deque(n for n in queue if not n.startswith('assets/units/operators/mica/fast_runtime_v1/'))
for prefix in ['motion_lab_v1/art', 'motion_lab_v1/derived', 'motion_lab_v1/reference',
               'motion_lab_v1/characters', 'motion_lab_v1/public', 'motion_lab_v1/dist']:
    tree(prefix, 'current_motion_studio_source_or_rebuild')
for prefix in ['motion_lab_v1/qa/build_previous', 'motion_lab_v1/qa/package_history',
               'motion_lab_v1/qa/aster', 'motion_lab_v1/qa/mica',
               'motion_lab_v1/qa/recovery_runtime', 'motion_lab_v1/qa/cleanup_20260911']:
    tree(prefix, 'current_character_evidence_or_previous_package')

for name in files:
    if name.startswith('art_src/pilot_v2/') and name.endswith(('.py', '.ps1')):
        keep(name, 'implementation_source', False)
    if name.startswith('artifacts/rook_'):
        keep(name, 'connected_rook_evidence')
    if name.startswith(('artifacts/', 'motion_lab_v1/qa/')) and name.endswith(('.md', '.py', '.log')):
        keep(name, 'historical_text_summary_or_implementation', False)
keep('artifacts/quarantine/motion_rejections.json', 'rejection_blacklist', False)
for name in ['mica_8dir_idle.png', 'mica_8dir_walk.gif', 'mica_8dir_walk.png',
             'mica_runtime_20260910_1080p.png', 'mica_combat_browser_final_20260910.json',
             'keyboard_recovery_browser_20260910.json', 'asset_validation.json',
             'aster_runtime_v8_native.png', 'aster_motion_v8_native.webm',
             'aster_motion_v8_native.json', 'aster_motion_v8_bound.webm',
             'aster_motion_v8_bound.json', 'aster_combat_v8_browser.json',
             'aster_locomotion_v8_browser.json']:
    keep('motion_lab_v1/qa/' + name, 'current_review_reference')


def values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from values(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from values(child)


def resolve(value, source):
    value = value.strip().replace('\\', '/')
    if len(value) > 1024 or not re.search(r'[/\\.]', value):
        return None
    if value.startswith('res://'):
        value = value[6:]
    if value.lower().startswith(ROOT.as_posix().lower() + '/'):
        value = value[len(ROOT.as_posix()) + 1:]
    if re.match(r'^[A-Za-z]:|^https?://|^data:', value):
        return None
    choices = [value, str(Path(source).parent / value)]
    if source.startswith('motion_lab_v1/'):
        choices.insert(0, 'motion_lab_v1/' + value)
    for choice in choices:
        candidate = os.path.normpath(choice).replace('\\', '/')
        if candidate in files:
            return candidate
    return None


while queue:
    name = queue.popleft()
    if name in parsed:
        continue
    parsed.add(name)
    # Retired descriptors and historical diagnostic receipts are documentation,
    # not executable dependency roots. Never let their cycles keep failed pixels.
    if name == 'data/character_pipeline/mica_runtime.json' or name.startswith('artifacts/'):
        continue
    try:
        content = (ROOT / name).read_text(encoding='utf-8-sig')
        refs = values(json.loads(content)) if name.endswith('.json') else re.findall(r'["\']([^"\'\r\n]+)["\']', content)
        for value in refs:
            target = resolve(value, name)
            if target and not target.startswith('assets/units/operators/mica/fast_runtime_v1/'):
                # Referenced text stays available; old evidence cannot recursively
                # admit failed source meshes/renders into today's build graph.
                keep(target, 'dependency:' + name, not target.startswith('artifacts/'))
    except (ValueError, UnicodeError):
        pass


def reason(name):
    if name.startswith('assets/units/operators/mica/fast_runtime_v1/'):
        return 'inactive_rejected_mica_atlas_superseded_by_motion_studio'
    if name.startswith('art_src/characters/mica/'):
        return 'retired_mica_production_not_current_source'
    if name.startswith('artifacts/'):
        return 'historical_evidence_cycle_not_current_build_dependency'
    if name.startswith('art_src/pilot_v2/'):
        return 'unused_legacy_aster_intermediate'
    if name.startswith('motion_lab_v1/qa/'):
        return 'superseded_unbound_review_capture'
    return None


retired = [{'path': name, 'bytes': size, 'reason': reason(name)} for name, size in files.items()
           if reason(name) and name not in protected]
kept = [{'path': name, 'bytes': files[name], 'reason': why} for name, why in protected.items() if reason(name)]
grouped = collections.defaultdict(lambda: {'files': 0, 'bytes': 0})
for row in retired:
    grouped[row['reason']]['files'] += 1
    grouped[row['reason']]['bytes'] += row['bytes']
OUT.mkdir(parents=True, exist_ok=True)
for filename, data in [('retirement_plan.json', retired), ('protected_candidates.json', kept),
                       ('audit_summary.json', {'status': 'AUDITED_NOT_MOVED', 'fileCount': len(retired),
                        'bytes': sum(r['bytes'] for r in retired), 'categories': grouped})]:
    (OUT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'files': len(retired), 'bytes': sum(r['bytes'] for r in retired), 'categories': grouped}), flush=True)
