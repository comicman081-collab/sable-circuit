#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILES = [ROOT/'data/art_profiles/playable_profiles.json', ROOT/'data/art_profiles/enemy_profiles.json']
REQUIRED = [
    'visual_profile','master_asset','rig_sheet','silhouette','palette','motion_profile','motion_signature',
    'projectile_profile','projectile_signature','hit_vfx_profile','hit_vfx_signature',
    'fire_sfx_profile','fire_sfx_signature','impact_sfx_profile','impact_sfx_signature'
]
UNIQUE_FIELDS = [
    'visual_profile','master_asset','rig_sheet','motion_profile','motion_signature',
    'projectile_profile','projectile_signature','hit_vfx_profile','hit_vfx_signature',
    'fire_sfx_profile','fire_sfx_signature','impact_sfx_profile','impact_sfx_signature'
]
errors=[]; profiles=[]
for path in PROFILE_FILES:
    if not path.is_file():
        errors.append(f'missing art profile file: {path.relative_to(ROOT)}'); continue
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'cannot parse {path.relative_to(ROOT)}: {exc}'); continue
    if data.get('schema_version') != 1: errors.append(f'{path.relative_to(ROOT)} schema_version must be 1')
    rows=data.get('profiles')
    if not isinstance(rows,list) or not rows:
        errors.append(f'{path.relative_to(ROOT)} profiles must be non-empty'); continue
    profiles.extend(rows)

for i,p in enumerate(profiles):
    ident=p.get('actor_id') or p.get('enemy_id') or f'profile[{i}]'
    for key in REQUIRED:
        if not p.get(key): errors.append(f'{ident}: missing {key}')
    palette=p.get('palette',[])
    if not isinstance(palette,list) or len(palette)<4: errors.append(f'{ident}: palette must contain at least 4 colors')
    for asset_key in ('master_asset','rig_sheet'):
        rel=p.get(asset_key)
        if not rel: continue
        asset=ROOT/rel
        if not asset.is_file(): errors.append(f'{ident}: {asset_key} missing: {rel}')
        elif asset.suffix.lower() not in {'.svg','.png','.webp'}: errors.append(f'{ident}: unsupported {asset_key} type: {rel}')

for field in UNIQUE_FIELDS:
    seen={}
    for p in profiles:
        ident=p.get('actor_id') or p.get('enemy_id') or '?'
        value=str(p.get(field,'')).strip()
        if not value: continue
        if value in seen: errors.append(f'duplicate {field}: {value!r} used by {seen[value]} and {ident}')
        else: seen[value]=ident

# Visible final sources may not be byte-identical under different paths/names.
for asset_key in ('master_asset','rig_sheet'):
    hashes={}
    for p in profiles:
        ident=p.get('actor_id') or p.get('enemy_id') or '?'
        rel=p.get(asset_key)
        if not rel: continue
        asset=ROOT/rel
        if not asset.is_file(): continue
        digest=hashlib.sha256(asset.read_bytes()).hexdigest()
        if digest in hashes: errors.append(f'byte-identical {asset_key} reused by {hashes[digest]} and {ident}: sha256={digest}')
        else: hashes[digest]=ident

identity_ids=[]
for p in profiles:
    ident=p.get('actor_id') or p.get('enemy_id')
    if ident:
        if ident in identity_ids: errors.append(f'duplicate actor/enemy identity id: {ident}')
        identity_ids.append(ident)

if errors:
    print('UNIQUE_ART_VALIDATION: FAIL')
    for e in errors: print(' -',e)
    sys.exit(1)
print('UNIQUE_ART_VALIDATION: PASS')
print(f'validated {len(profiles)} identities with unique master art, rig sheets, motion, projectile, VFX and SFX identities')
