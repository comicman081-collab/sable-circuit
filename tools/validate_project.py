#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
required_files = [
    'project.godot','README.md','.gitignore','.gitattributes',
    '.github/workflows/validate.yml',
    'assets/external/manifest.json','schemas/repository_layout.json',
    'scenes/bootstrap/Bootstrap.tscn','scripts/core/bootstrap.gd',
    'docs/GDD_v0.1.md','docs/TECH_ARCHITECTURE_v0.1.md','docs/ANIMATION_SPEC_v0.1.md',
    'docs/FOLDER_STRUCTURE.md','docs/GITHUB_ACTIONS_POLICY.md','docs/VALIDATION_REPORT.md','docs/TITLE_AND_REPO.md'
]
errors=[]
for f in required_files:
    if not (ROOT/f).is_file():
        errors.append(f'missing required file: {f}')

# Machine-readable repository layout contract.
layout_path=ROOT/'schemas/repository_layout.json'
if layout_path.exists():
    try:
        layout=json.loads(layout_path.read_text(encoding='utf-8'))
        dirs=layout.get('directories')
        if layout.get('schema_version') != 1: errors.append('repository layout schema_version must be 1')
        if layout.get('project_root') != 'repository-root': errors.append('project_root must be repository-root')
        if not isinstance(dirs, list) or not dirs: errors.append('repository layout directories must be a non-empty list')
        else:
            if len(dirs) != len(set(dirs)): errors.append('repository layout contains duplicate directory entries')
            for d in dirs:
                if not isinstance(d, str) or d.startswith('/') or '..' in Path(d).parts:
                    errors.append(f'invalid repository layout directory: {d!r}')
        if 'game' not in layout.get('forbidden_roots', []): errors.append('repository layout must forbid game/ root wrapper')
    except Exception as e:
        errors.append(f'repository layout parse error: {e}')

# Root/main-scene contract.
project_text=(ROOT/'project.godot').read_text(encoding='utf-8') if (ROOT/'project.godot').exists() else ''
if 'run/main_scene="res://scenes/bootstrap/Bootstrap.tscn"' not in project_text:
    errors.append('project.godot must point to the CI-safe Bootstrap.tscn main scene')
if (ROOT/'game').exists():
    errors.append('forbidden root wrapper: game/ (project.godot must remain at repository root)')

# External manifest integrity contract.
mp=ROOT/'assets/external/manifest.json'
if mp.exists():
    try:
        data=json.loads(mp.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1: errors.append('external manifest schema_version must be 1')
        if not isinstance(data.get('assets'), list): errors.append('external manifest assets must be a list')
        else:
            ids=set()
            for i,a in enumerate(data['assets']):
                for k in ('id','name','origin','version','license','destination','sha256'):
                    if k not in a: errors.append(f'external asset[{i}] missing {k}')
                if 'id' in a:
                    if a['id'] in ids: errors.append(f'duplicate external asset id: {a["id"]}')
                    ids.add(a['id'])
                sha=a.get('sha256','')
                if sha and not re.fullmatch(r'[0-9a-fA-F]{64}', sha): errors.append(f'invalid sha256 for external asset[{i}]')
    except Exception as e:
        errors.append(f'external manifest parse error: {e}')

# No Pages deployment during pre-production.
wfdir=ROOT/'.github/workflows'
if wfdir.exists():
    for p in wfdir.glob('*.y*ml'):
        text=p.read_text(encoding='utf-8', errors='replace').lower()
        if 'actions/deploy-pages' in text or 'pages: write' in text or 'github-pages' in text:
            errors.append(f'pages deployment is forbidden in pre-production: {p.relative_to(ROOT)}')

if errors:
    print('VALIDATION: FAIL')
    for e in errors: print(' -', e)
    sys.exit(1)
print('VALIDATION: PASS')
print(f'checked {len(required_files)} required files and repository layout manifest')
