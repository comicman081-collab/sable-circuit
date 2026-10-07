"""Preserve rejected yaw masters and provenance. Never delete their lineage."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'art/quarantine/site7_drone_yaw_failures_20260913'
CASES = {
    'drone_N_v1': 'FAIL_NOT_PROMOTABLE: four thrusters instead of the established two',
    'drone_SW_v1': 'FAIL_NOT_PROMOTABLE: reversed asymmetrical front sensor arrangement',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / 'rejections.json'
    if manifest.exists():
        raise SystemExit('Existing rejection ledger retained; do not overwrite it')
    rows = []
    for stem, reason in CASES.items():
        files = []
        for suffix in ['.png', '_tool_response.json']:
            source = ROOT / 'art/site7_enemies_raw' / (stem + suffix)
            target = OUT / source.name
            if target.exists():
                raise SystemExit('Quarantine payload already exists')
            before = sha(source)
            shutil.copy2(source, target)
            if sha(target) != before:
                raise RuntimeError('Copy differs from original')
            files.append({'source':source.relative_to(ROOT).as_posix(),
                          'quarantine':target.relative_to(ROOT).as_posix(), 'sha256':before})
        rows.append({'candidate':stem,'decision':'FAIL_NOT_PROMOTABLE','reason':reason,'files':files})
    manifest.write_text(json.dumps({'status':'QUARANTINED_RETAINED_NOT_DISPOSED','candidates':rows,
        'lineage':'Raw source copies are retained as exact repair inputs. No runtime pointer uses these candidates.',
        'disposal':'Not authorized by candidate replacement; final replacement gates remain separate.'},indent=2),encoding='utf-8')
    print(manifest)

if __name__ == '__main__':
    main()
