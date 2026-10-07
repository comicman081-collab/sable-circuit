"""Retain exact native returns; inspect alpha and make review evidence only."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB))
from source_alpha_policy import inspect_master, require_project_reference

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--response', type=Path, required=True)
    a = p.parse_args()
    assert a.id.replace('_', '').isalnum()
    out = LAB / 'art/stage_enemies_20260919'
    out.mkdir(parents=True, exist_ok=True)
    dest = out / (a.id + '.png')
    if dest.exists(): assert sha(dest) == sha(a.source), 'Never overwrite source'
    else: shutil.copy2(a.source, dest)
    assert sha(dest) == sha(a.source)
    require_project_reference(dest)
    raw = json.loads(a.response.read_text(encoding='utf-8'))
    raw['result'] = {'output_hint':raw['output_hint']}
    raw['returnedPath'] = str(a.source.resolve())
    raw['projectCopy'] = dest.relative_to(LAB).as_posix()
    raw['projectCopySHA256'] = sha(dest)
    raw['sourceMaster'] = {'path': dest.relative_to(LAB).as_posix(), 'sha256': sha(dest)}
    response = Path(__file__).parent / (a.id + '_tool_response.json')
    response.write_text(json.dumps(raw, indent=2), encoding='utf-8')
    from source_provenance import response_master
    assert response_master(LAB, response.resolve()) == dest.resolve()
    try: alpha = inspect_master(dest)
    except ValueError as e: alpha = {'status': 'HOLD_NATIVE_ALPHA', 'error': str(e), 'sourceSHA256': sha(dest)}
    image = Image.open(dest)
    qa = Path(__file__).parent / a.id
    qa.mkdir(exist_ok=True)
    for mode in ['fit', 'native']:
        canvas = Image.new('RGB', (1920,1080), '#14232b')
        for x, matte in [(0,'#eeeeee'),(960,'#14232b')]:
            panel = Image.new('RGBA',(960,1080),matte)
            im = image.copy()
            if mode == 'fit': im.thumbnail((928,996), Image.Resampling.LANCZOS)
            else:
                left=max(0,(im.width-928)//2); top=max(0,(im.height-996)//2)
                im=im.crop((left,top,min(im.width,left+928),min(im.height,top+996)))
            panel.alpha_composite(im,((960-im.width)//2,(1080-im.height)//2))
            canvas.paste(panel.convert('RGB'),(x,0))
        ImageDraw.Draw(canvas).text((20,16),a.id+' / '+mode+' / CANDIDATE, NOT APP APPROVAL',fill='#c17a31')
        canvas.save(qa/(mode+'_1920x1080.png'))
    report={'id':a.id,'alpha':alpha,'source':dest.relative_to(LAB).as_posix(),
        'source_sha256':sha(dest),'response_sha256':sha(response),
        'source_pixels_modified':False,'runtime_promoted':False,
        'evidence_native':[1920,1080],'native_review_is_1_to_1_crop':True}
    (qa/'intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
