"""Native-alpha crop + metadata only. No generation, keying or promotion."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

QA=Path(__file__).resolve().parent
LAB=QA.parents[1]
PROJECT=LAB.parent
sys.path.insert(0,str(LAB))
from source_alpha_policy import inspect_master
from source_provenance import response_master
from intake_native import main as unused_intake_entry

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    selection=json.loads((QA/'selection.json').read_text())
    out=QA/'candidate_v1'; out.mkdir(exist_ok=True)
    specs={}; profiles=[]; bindings=[]
    for name,entry in selection.items():
        views={}
        for direction,row in entry['views'].items():
            source=LAB/'art/stage_enemies_20260919'/(row['file']+'.png')
            response=QA/(row['file']+'_tool_response.json')
            assert response_master(LAB,response)==source.resolve()
            alpha=inspect_master(source)
            im=Image.open(source); box=im.getbbox(); crop=im.crop(box)
            target=out/(name+'_'+direction+'.png'); crop.save(target)
            assert np.array_equal(np.asarray(Image.open(target)),np.asarray(im)[box[1]:box[3],box[0]:box[2]])
            scale=entry['native_scale']
            root=row.get('root',[im.width/2,box[3]+(160 if name=='ram' else -65)])
            emitter=row['emitter']
            view={'texture':'res://'+target.relative_to(PROJECT).as_posix(),'texture_sha256':sha(target),
                'display_height':crop.height*scale,'root_px':[root[0]-box[0],root[1]-box[1]],
                'emitter_px':[emitter[0]-box[0],emitter[1]-box[1]],'emitter_visible':row.get('visible',True)}
            views[direction]=view
            bindings.append({'name':name,'direction':direction,'source':source.relative_to(PROJECT).as_posix(),
                'source_sha256':sha(source),'response':response.relative_to(PROJECT).as_posix(),'response_sha256':sha(response),
                'candidate':target.relative_to(PROJECT).as_posix(),'candidate_sha256':sha(target),'box':box,
                'operation':'lossless native-alpha crop only; no resample, key, clamp, mirror or redraw','alpha':alpha})
        spec={'enemy_id':entry['id'],'kind':entry['kind'],'schema_version':1}
        if entry['kind']=='anchored_machine': spec.update(views['ANCHORED'])
        else: spec.update({'facing_mode':'authored_yaw8','views':views})
        specs[entry['id']]=spec
        profiles.append({'enemy_id':entry['id'],'name':entry['name'],'tier':'NORMAL','body_plan':'robot','runtime_enabled':True,
            'motion_profile':'MOT_'+name.upper(),'projectile_profile':entry['projectile'],
            'fire_sfx_profile':'SFX_FIRE_ENM_SHIELD_01','impact_sfx_profile':'SFX_HIT_ENM_SHIELD_01',
            'palette':entry['palette'],'silhouette':entry['design'],'master_asset':'','rig_sheet':''})
        if len(views)==8:
            board=Image.new('RGB',(1920,1080),'#15232b'); draw=ImageDraw.Draw(board)
            for i,d in enumerate(['E','SE','S','SW','W','NW','N','NE']):
                im=Image.open(out/(name+'_'+d+'.png')); im.thumbnail((450,440),Image.Resampling.LANCZOS)
                x=i%4*480+(480-im.width)//2; y=i//4*540+70+(440-im.height)//2
                board.paste(im,(x,y),im); draw.text((i%4*480+16,i//4*540+18),name+' / '+d,fill='#c8dfdd')
            board.save(out/(name+'_yaw8_1920x1080.png'))
    (out/'specs.json').write_text(json.dumps(specs,indent=2))
    (out/'profiles.json').write_text(json.dumps({'profiles':profiles},indent=2))
    (out/'bindings.json').write_text(json.dumps({'status':'CANDIDATE_ONLY','rows':bindings,'selection_sha256':sha(QA/'selection.json'),'builder_sha256':sha(Path(__file__))},indent=2))
    print(json.dumps({'status':'CANDIDATE_ONLY','count':len(bindings),'path':str(out)}))

if __name__=='__main__': main()
