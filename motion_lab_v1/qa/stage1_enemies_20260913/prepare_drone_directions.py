"""Prepare native ImageGen yaw sources; generate QA specs, never app approval."""
from pathlib import Path
import sys, json, hashlib, io, contextlib
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from prepare_enemy_asset import prepare, sha
from PIL import Image, ImageDraw

# Observed spherical magenta emitter centers in the actual generated masters.
# These are manually observed visible-art coordinates, not the prompt's wishes.
SOURCES = {
    'E':('drone_E_v1',[1240,740]),
    'SE':('drone_omni',[897,810]),
    'S':('drone_S_v1',[769,830]),
    'SW':('drone_SW_v2',[643,834]),
    'W':('drone_W_v1',[151,697]),
    'NW':('drone_NW_v1',[233,373]),
    'N':('drone_N_v2',[768,663]),
    'NE':('drone_NE_v1',[1249,557]),
}

def main():
    reports={}; views={}
    for direction,(name,emitter) in SOURCES.items():
        source=ROOT/'art/site7_enemies_raw'/f'{name}.png'
        response=(ROOT/'qa/stage1_enemies_20260913/drone_omni_tool_response.json' if direction=='SE'
                  else ROOT/'art/site7_enemies_raw'/f'{name}_tool_response.json')
        saved=io.StringIO()
        with contextlib.redirect_stdout(saved): prepare('drone_yaw_'+direction.lower(),source,response)
        report=json.loads(saved.getvalue()); reports[direction]=report
        width,height=report['candidateNative']; x0,y0=report['box'][:2]
        views[direction]={'texture':'res://motion_lab_v1/'+report['candidate'].replace('\\','/'),
            'texture_sha256':report['candidateSHA256'],'display_height':110,
            'root_px':[width/2,height*1.35],'emitter_px':[emitter[0]-x0,emitter[1]-y0],
            'emitter_visible':True}
    signature=hashlib.sha256(json.dumps({'sources':reports,'helper':sha(Path(__file__))},sort_keys=True).encode()).hexdigest()
    out=ROOT/'qa/stage1_enemies_20260913/drone_yaw8'/signature[:16]
    out.mkdir(parents=True,exist_ok=True)
    spec={'kind':'hover_machine','facing_mode':'authored_yaw8','views':views}
    (out/'candidate_spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
    (out/'source_binding.json').write_text(json.dumps({'status':'CANDIDATE_NOT_APPROVED','sources':reports,
        'helperSHA256':sha(Path(__file__)),'nativeSources':[1536,1024],
        'note':'Independent direction illustrations; no runtime flip/bitmap yaw, no anatomical motion claim.'},indent=2),encoding='utf-8')
    board=Image.new('RGB',(1920,1080),'#15232b'); draw=ImageDraw.Draw(board)
    for i,(direction,report) in enumerate(reports.items()):
        im=Image.open(ROOT/report['candidate']).convert('RGBA'); im.thumbnail((450,420),Image.Resampling.LANCZOS)
        x=(i%4)*480+(480-im.width)//2; y=(i//4)*540+60+(420-im.height)//2
        board.paste(im,(x,y),im); draw.text(((i%4)*480+20,(i//4)*540+20),direction+' / SOURCE DIRECTION CANDIDATE',fill='#b0dacc')
    board.save(out/'yaw8_1920x1080.png')
    # Additional original-scale emitter panels, without resizing source pixels.
    for direction,report in reports.items():
        im=Image.open(ROOT/report['candidate']).convert('RGBA'); e=views[direction]['emitter_px']
        panel=Image.new('RGB',(1920,1080),'#17262f')
        for x,color in [(0,'#eeeeee'),(960,'#17262f')]:
            crop=im.crop((max(0,int(e[0])-460),max(0,int(e[1])-500),min(im.width,int(e[0])+460),min(im.height,int(e[1])+500)))
            matte=Image.new('RGBA',(960,1080),color); matte.alpha_composite(crop,((960-crop.width)//2,(1080-crop.height)//2));panel.paste(matte.convert('RGB'),(x,0))
        panel.save(out/f'{direction}_emitter_native_1920x1080.png')
    print(json.dumps({'status':'CANDIDATE_NOT_APPROVED','directory':str(out),'spec':str(out/'candidate_spec.json')}))

if __name__=='__main__': main()
