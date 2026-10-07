"""Source measurements/semantic masks, not art repainting or visual approval."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g

def main():
    work=ROOT/'art_src/characters/mica/rigged_v2/source_front_r1'
    image_path=work/'MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png'
    image=Image.open(image_path).convert('RGBA')
    if image.size!=(1024,1536):raise ValueError('ANNOTATIONS_FOR_EXACT_NATIVE_SIZE_ONLY')
    if g.sha(image_path)!='6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895':raise ValueError('EXACT_IMAGE_REQUIRED')
    polygons={
        'face':[[(493,117),(530,113),(552,142),(551,179),(532,212),(508,223),(488,207),(470,180),(479,143)]],
        'coat':[[(503,264),(538,253),(555,514),(483,514)],[(328,875),(347,880),(285,1118),(266,1109)],[(669,875),(688,871),(741,1108),(720,1118)]],
        'trousers':[[(470,653),(484,660),(480,713),(463,711)],[(535,656),(549,653),(554,714),(539,714)]],
        'boots':[[(395,1294),(441,1292),(450,1381),(433,1406),(384,1405),(379,1388)],[(577,1294),(618,1293),(633,1387),(622,1406),(570,1406),(563,1386)]]}
    regions=[];overlay=image.copy();od=ImageDraw.Draw(overlay,'RGBA')
    from PIL import ImageFilter
    allowed=Image.fromarray((~g.green(np.asarray(image))*255).astype('uint8')).filter(ImageFilter.MinFilter(7))
    colors={'face':(255,180,50,100),'coat':(240,80,120,100),'trousers':(50,150,255,100),'boots':(210,110,255,100)}
    for name,shapes in polygons.items():
        mask=Image.new('RGBA',image.size,(0,0,0,255));draw=ImageDraw.Draw(mask)
        for shape in shapes:draw.polygon(shape,fill='white')
        # Remove only chroma boundary from the measured mask, not from source
        # art. No nearest-foreground replacement or source pixel repainting.
        inclusion=(np.asarray(mask)[...,0]>127)&(np.asarray(allowed)>127)
        rgba=np.zeros((image.height,image.width,4),dtype=np.uint8);rgba[...,3]=255
        rgba[inclusion,:3]=255;mask=Image.fromarray(rgba)
        tint=Image.new('RGBA',image.size,colors[name]);tint.putalpha(Image.fromarray((inclusion*90).astype('uint8')))
        overlay=Image.alpha_composite(overlay,tint);od=ImageDraw.Draw(overlay,'RGBA')
        for shape in shapes:od.line(shape+[shape[0]],fill=(255,255,255,255),width=1)
        path=work/f'{name}_MASK_R3.png'
        if path.exists():raise ValueError('PRESERVE_MASK_REVISION')
        mask.save(path)
        regions.append({'id':name,'view':'S','mask':g.ref(path),'exclusions':[],
            'purpose':'volumetric_texture','allowed_mesh_parts':[{'face':'MICA_Head','coat':'MICA_Coat','trousers':'MICA_Trousers','boots':'MICA_Boots'}[name]]})
    points={'head_top':[509,42],'ground':[509,1424],'hip_left':[570,651],'hip_right':[448,651],
        'shoulder_left':[639,294],'shoulder_right':[381,294],'heel_left':[600,1383],'heel_right':[415,1383],
        'toe_left':[601,1422],'toe_right':[413,1422],'waist':[511,542]}
    for name,p in points.items():
        od.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='white');od.text((p[0]+6,p[1]),name,fill='white')
    annotation=work/'S_LANDMARKS_R3.json'
    g.write(annotation,{'image_sha256':g.sha(image_path),'body_facing':'S','metres_per_pixel':1.72/1382,'points':points,
        'measurement_method':'manual_original_scale_source_annotation',
        'heel_visibility':'heel locations projected through opaque boots; approximate construction landmarks, not motion contact evidence',
        'mask_scope':'Conservative visible material regions only; not a complete UV unwrap or permission to copy hands/hair into cloth.'})
    request=g.ref(work/'request.json')
    permit=g.ref(work/'generation_requests'/f"{request['sha256']}.permit.json")
    manifest={'schema':1,'actor_id':'CHR_PROTO_03','costume_id':'MICA_RECON_C03','source_author':'built_in_ImageGen',
        'request':request,'attempt_permit':permit,'views':[{'id':'S','image':g.ref(image_path),
        'annotations':g.ref(annotation),'native_size':list(image.size),'panel':[0,0,1024,1536]}],'regions':regions}
    g.write(work/'SOURCE_MANIFEST_R3.json',manifest)
    review=Image.new('RGBA',(2304,1920),(23,32,43,255));review.paste(image,(32,132));review.paste(overlay,(1190,132))
    text=ImageDraw.Draw(review)
    text.text((32,30),'MICA C03 | NEW NEUTRAL RIG SOURCE | NATIVE 1024 x 1536 (NO UPSCALE)',fill='white')
    text.text((1190,30),'MEASURED LANDMARKS + CONSERVATIVE SEMANTIC MASKS | REVIEW REQUIRED',fill='white')
    text.text((32,1740),'Single ImageGen source. Original green master retained. Not motion, not a final character.',fill='white')
    text.text((32,1780),'Right panel is annotation evidence only. Material masks do not authorize a full-face/body UV map.',fill='white')
    review.save(work/'SOURCE_REVIEW_R3_NATIVE_2304x1920.png')
    g.write(work/'SOURCE_AUDIT_R3.json',g.audit_source(work/'SOURCE_MANIFEST_R3.json'))
    data=np.asarray(image);bg=g.green(data)
    g.write(work/'IMAGEGEN_PROVENANCE_R3.json',{'tool':'built_in_ImageGen','request':request,'permit':permit,
        'output':g.ref(image_path),'native_size':list(image.size),'no_upscale':True,
        'managed_staging_copy_removed_after_exact_hash_verification':True,
        'staging_file':'C:/Users/AAA/.codex/generated_images/01a051d8-4f00-7990-b7d2-05034e37b842/exec-2788b2a3-ddcc-41ff-87b8-f5be4347e82e.png',
        'green_background_channel_min':data[bg,:3].min(axis=0).tolist(),'green_background_channel_max':data[bg,:3].max(axis=0).tolist(),
        'status':'SOURCE_VISUAL_REVIEW_PENDING_NOT_PRODUCTION_APPROVAL'})
    print(g.read(work/'SOURCE_AUDIT_R3.json'))

if __name__=='__main__':main()
