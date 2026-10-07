"""Deterministic enemy matte/crop and native QA. Never activates an app asset.

Uses the established model-free compiler. Source artwork stays byte-immutable.
No leg segmentation, anatomical warp, local model or synthetic missing pixels.
"""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image, ImageDraw
import numpy as np
from build_atlas import key_image

ROOT=Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_source(source, response):
    """Bind the exact retained master, not just the name of its generator.

    This is local provenance consistency, not cryptographic provider attestation
    or an artistic approval. The original tool response must be recorded honestly.
    """
    from source_provenance import response_master
    if response_master(ROOT,response)!=source:
        raise ValueError('Tool response must bind this exact project copy')
    return json.loads(response.read_text(encoding='utf-8-sig'))

def prepare(ident, source, response):
    if not re.fullmatch(r'[a-z0-9_-]+',ident):
        raise ValueError('Use an asset id, not a path')
    source=source.resolve(); response=response.resolve()
    if not source.is_relative_to(ROOT) or not response.is_relative_to(ROOT):
        raise ValueError('Project-local source and actual tool response required')
    verify_source(source,response)
    with Image.open(source) as opened:raw=opened.copy()
    if max(raw.size)<1024:
        raise ValueError('Native high-resolution generated master required')
    rgba=key_image(source)
    yy,xx=np.where(rgba[:,:,3]>30)
    if not len(xx):
        raise ValueError('Empty separated subject; retain as failed source')
    # Keep previous QA bytes when the preparation implementation changes.
    dependencies={'preparation':sha(Path(__file__)),'matte':sha(ROOT/'build_atlas.py'),'provenance':sha(ROOT/'source_provenance.py')}
    implementation=hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()[:8]
    out=ROOT/'qa/stage1_enemies_20260913'/ident/(sha(source)[:12]+'_'+implementation)
    out.mkdir(parents=True,exist_ok=True)
    box=[max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(raw.width,int(xx.max())+13),min(raw.height,int(yy.max())+13)]
    cut=Image.fromarray(rgba).crop(box)
    target=out/'candidate_rgba.png'; cut.save(target)
    # A 1:1 native crop on each matte is deliberately separate from fit previews.
    for label,native in [('native',True),('full',False)]:
        board=Image.new('RGB',(1920,1080),'#15232b')
        for ox,color in [(0,'#eeeeee'),(960,'#15232b')]:
            panel=Image.new('RGBA',(960,1080),color)
            im=cut.copy()
            if native:
                left=max(0,(im.width-940)//2); top=max(0,(im.height-1040)//2)
                im=im.crop((left,top,min(im.width,left+940),min(im.height,top+1040)))
            else: im.thumbnail((930,1030),Image.Resampling.LANCZOS)
            panel.alpha_composite(im,((960-im.width)//2,(1080-im.height)//2))
            board.paste(panel.convert('RGB'),(ox,0))
        ImageDraw.Draw(board).text((16,16),ident+' / '+('1:1 ORIGINAL PIXEL CROP' if native else 'FULL SUBJECT FIT'),fill='#e5974d')
        board.save(out/f'{label}_1920x1080.png')
    report={'id':ident,'status':'CANDIDATE_NOT_REVIEWED','source':str(source.relative_to(ROOT)),
            'sourceSHA256':sha(source),'toolResponse':{'path':str(response.relative_to(ROOT)),'sha256':sha(response)},
            'sourceNative':[raw.width,raw.height],'box':box,'candidate':str(target.relative_to(ROOT)),
            'candidateSHA256':sha(target),'candidateNative':list(cut.size),'native_review':[1920,1080],
            'operation':'existing key_image chroma/alpha separation then native crop only',
            'preparationCodeSHA256':sha(Path(__file__)),
            'matteCodeSHA256':sha(ROOT/'build_atlas.py'),
            'implementationDependencies':dependencies,
            'resampling':False,'anatomicalWarp':False,'runtimePromotion':False}
    (out/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--tool-response',type=Path,required=True)
    a=p.parse_args();prepare(a.id,a.source,a.tool_response)
