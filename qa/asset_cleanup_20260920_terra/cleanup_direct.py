"""Bounded, exact-file synthetic-fixture retirement. No production asset removal."""
from pathlib import Path
import gzip, hashlib, json, os, re, subprocess, sys, time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
BASE = ROOT / 'motion_lab_v1/qa/technical_tests'
MANIFEST = OUT / 'direct_retirement.jsonl.gz'
SOUND = OUT / 'direct_sound_preserved.json'
MEDIA = {'.avi','.mp4','.mkv','.mov','.webm','.m4v','.wav','.ogg','.mp3','.flac','.aac','.aif','.aiff','.m4a','.opus','.wma','.mid','.midi'}
PREFIX = re.compile(r'^(cycle_|workflow_|native_alpha_|derived_integrity_|enemy_proof_|html_evidence_|preview_codec_)')

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def safe(path, base=BASE):
    absolute = Path(os.path.abspath(path))
    if not absolute.is_relative_to(base) or absolute == base or absolute.resolve() != absolute:
        raise RuntimeError(f'Unsafe path: {path}')
    if absolute.is_symlink() or absolute.is_junction():
        raise RuntimeError(f'Link: {path}')
    return absolute

def files(folder):
    for current, dirs, names in os.walk(folder, followlinks=False):
        for name in dirs:
            safe(Path(current)/name)
        for name in names:
            yield safe(Path(current)/name)

def runtime_check():
    result = subprocess.run(['rg','--hidden','--no-ignore','-l','-g','*.gd','-g','*.json','-g','*.tscn','-g','*.tres','-g','*.godot','-F','qa/technical_tests',
                             'project.godot','scripts','scenes','data','assets'],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 1:
        raise RuntimeError(f'Runtime reference or scan failure: {result.stdout} {result.stderr}')

def record(path):
    return {'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':digest(path)}

def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def preserved_sound():
    result=[]
    for relative in ['assets/audio','art_src/audio','scripts/audio','tools/audio','qa/sfx_integration_20260919']:
        folder=ROOT/relative
        if folder.exists():
            for path in folder.rglob('*'):
                if path.is_file():
                    safe(path, ROOT)
                    result.append(record(path))
    return result

runtime_check()
if '--execute' not in sys.argv:
    if MANIFEST.exists():
        raise RuntimeError('Existing manifest; do not replace retirement evidence')
    sound = preserved_sound()
    save(SOUND,sound)
    count=total=kept=0
    kept_dirs=[]
    with gzip.open(MANIFEST,'wt',encoding='utf-8') as manifest:
        for folder in sorted(BASE.iterdir()):
            safe(folder)
            if not folder.is_dir() or not PREFIX.match(folder.name):
                kept_dirs.append(folder.name); continue
            entries=list(files(folder))
            if any(p.suffix.lower() in MEDIA or re.search(r'audio|sound|sfx|music|voice',p.relative_to(BASE).as_posix(),re.I) for p in entries):
                kept += len(entries); kept_dirs.append(folder.name); continue
            for path in entries:
                row=record(path)
                manifest.write(json.dumps(row,ensure_ascii=False)+'\n')
                count+=1; total+=row['bytes']
            if count and count%10000 < len(entries):
                print(f'Manifest: {count} files',flush=True)
    save(OUT/'direct_prepared.json',{'files':count,'bytes':total,'protected_sound_files':len(sound),
         'kept_media_files':kept,'kept_fixture_directories':kept_dirs,'manifest_sha256':digest(MANIFEST),
         'scope':'Only named mkdtemp synthetic fixtures, no audio/video-containing fixture directories',
         'deleted':False})
    print(f'PREPARED {count} files, {total} bytes',flush=True)
else:
    prepared=json.loads((OUT/'direct_prepared.json').read_text(encoding='utf-8'))
    if digest(MANIFEST)!=prepared['manifest_sha256']:
        raise RuntimeError('Manifest changed')
    with gzip.open(MANIFEST,'rt',encoding='utf-8') as f:
        rows=[json.loads(line) for line in f]
    for row in rows:
        path=safe(ROOT/row['path'])
        if path.stat().st_size!=row['bytes'] or digest(path)!=row['sha256']:
            raise RuntimeError(f'Changed file: {path}')
    print(f'PREDELETE_HASH_CHECK_PASS {len(rows)}',flush=True)
    for i,row in enumerate(rows,1):
        safe(ROOT/row['path']).unlink()
        if i%25000==0: print(f'DELETED {i}',flush=True)
    if any((ROOT/row['path']).exists() for row in rows):
        raise RuntimeError('Deletion incomplete')
    sound=json.loads(SOUND.read_text(encoding='utf-8'))
    for row in sound:
        path=ROOT/row['path']
        if not path.is_file() or digest(path)!=row['sha256']:
            raise RuntimeError(f'Sound changed: {path}')
    runtime_check()
    result={'deleted_files':len(rows),'deleted_bytes':sum(r['bytes'] for r in rows),
            'retirement_manifest':MANIFEST.name,'manifest_sha256':digest(MANIFEST),
            'protected_sound_files':len(sound),'sound_hash_check':'PASS','remaining_deleted_targets':0,
            'runtime_reference_check':'PASS_ZERO','method':'Exact resolved file paths; no recursive deletion',
            'protected':'All production/quarantine/source assets and all media-containing fixture directories'}
    save(OUT/'direct_result.json',result)
    print(json.dumps(result),flush=True)
