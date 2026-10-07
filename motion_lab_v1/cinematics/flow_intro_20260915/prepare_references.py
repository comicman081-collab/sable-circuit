"""Copy existing SABLE references; PNG repack preserves every decoded RGBA pixel."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'references'
OUT.mkdir(parents=True, exist_ok=True)
rows = []
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
for name in ['aster', 'rook', 'mica']:
    source = ROOT / f'motion_lab_v1/public/assets/atlas/{name}/SE_idle.webp'
    target = OUT / f'{name.upper()}_standing_RGBA.png'
    with Image.open(source) as image:
        assert image.mode == 'RGBA'
        assert image.getchannel('A').getextrema() == (0, 255)
        image.save(target)
        with Image.open(target) as check:
            assert check.tobytes() == image.tobytes()
        size = list(image.size)
    rows.append(dict(kind='character',name=name,source=str(source.relative_to(ROOT)),file=str(target.relative_to(ROOT)),source_sha256=digest(source),sha256=digest(target),resolution=size,operation='lossless container conversion only; existing approved runtime standing pixels, not newly authored source'))
backgrounds = ['outer_gate/01_OUTER_GATE_GAME.png','decon_corridor/02_DECON_CORRIDOR_GAME.png','archive_annex/03_ARCHIVE_ANNEX_GAME.png','containment_junction/04_CONTAINMENT_JUNCTION_GAME.png','core_c/05_CORE_C_GAME.png','emergency_lift/06_EMERGENCY_LIFT_GAME.png']
for name in backgrounds:
    source = ROOT / 'assets/environments/site7' / name
    target = OUT / source.name
    shutil.copy2(source, target)
    assert digest(source) == digest(target)
    with Image.open(source) as image:
        size = list(image.size)
    rows.append(dict(kind='background',source=str(source.relative_to(ROOT)),file=str(target.relative_to(ROOT)),sha256=digest(target),resolution=size,operation='byte-identical copy'))
(HERE / 'references.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
