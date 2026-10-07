"""Copy only selected, hash-verified environment assets; never mutate the library."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = Path('C:/ai_asset/karchive/2026-09-19')
DEST = ROOT/'third_party/karchive/site7_props_20260919'
QA = ROOT/'qa/karchive_props_20260919'
SELECTED = {
    'crate': 'angular-apocalypse-supply-crate-closed',
    'barrier': 'angular-apocalypse-concrete-roadblock',
    'generator': 'angular-apocalypse-portable-generator-ready',
    'cabinet': 'angular-common-infrastructure-electrical-junction-cabinet-industrial-normal',
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def copy_exact(source, destination, expected=None):
    digest = sha(source)
    if expected and digest != expected: raise ValueError('Source hash mismatch: '+str(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists(): shutil.copy2(source, destination)
    if sha(destination) != digest: raise ValueError('Retained copy changed: '+str(destination))
    return digest

def main():
    rows = {r['id']:r for r in json.loads((LIBRARY/'SABLE_SHORTLIST.json').read_text('utf-8'))}
    QA.mkdir(parents=True, exist_ok=True)
    assets = []
    for ident, source_id in SELECTED.items():
        row = rows[source_id]
        source = Path(row['local_path']).resolve()
        if not source.is_relative_to((LIBRARY/'models').resolve()): raise ValueError('Library path escape')
        target = DEST/(ident+'.glb')
        digest = copy_exact(source, target, row['sha256'])
        assets.append({'id':ident, 'original':str(source), 'copy':target.relative_to(ROOT).as_posix(),
                       'sha256':digest, 'bytes':target.stat().st_size, 'triangles':row['triangles_mesh_sum']})
    licenses=[]
    for source in [ROOT/'qa/karchive_asset_intake_20260919/bundled_LICENSE.txt', LIBRARY/'WEB_TERMS_20260919.txt', LIBRARY/'ATTRIBUTION.txt']:
        target=DEST/source.name
        licenses.append({'path':target.relative_to(ROOT).as_posix(), 'sha256':copy_exact(source,target)})
    manifest={'scope':'User-authorized environment props in SABLE, 2026-09-19; no character/enemy art or AI training',
              'commercial_project_use':True, 'modifications_allowed':True, 'raw_resale':False, 'ai_training':False,
              'attribution':'자료: kArchive\n출처: 쓰레드 dogfooter', 'assets':assets, 'licenses':licenses,
              'source_originals_unchanged':all(sha(Path(r['original']))==r['sha256'] for r in assets)}
    (DEST/'model-license-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps({'selected':len(assets),'bytes':sum(r['bytes'] for r in assets),'originals_unchanged':manifest['source_originals_unchanged']}))

if __name__=='__main__':main()
