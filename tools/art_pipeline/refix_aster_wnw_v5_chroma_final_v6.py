#!/usr/bin/env python3
"""Re-finalize WNW V5 raw Blender frames with the source-authority chroma mask."""
from __future__ import annotations
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import finalize_aster_fire16_no_shoulder_blender_ual_v2 as base

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/"art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2"
RAW=PACKAGE/"blender_raw/current/WNW"
AUTH=PACKAGE/"corrections/wnw_imagegen_v5/blender_scene/ASTER_FIRE_WNW_IMAGEGEN_V5_UAL6_CORRECTION_MANIFEST.json"
OUT=PACKAGE/"corrections/wnw_imagegen_v5_chroma_final_v9"
FINAL=OUT/"final/current";RUNTIME=OUT/"runtime/current";QA=OUT/"qa/current"
EXACT=np.asarray((0,255,0),dtype=np.uint8)

def sha256(path):
 d=hashlib.sha256()
 with Path(path).open("rb") as h:
  for block in iter(lambda:h.read(1024*1024),b""):d.update(block)
 return d.hexdigest()
def rel(path):return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
def corridor_mask(rgb,dx,dy):
 background,report=base.matte_mask(rgb)
 background|=np.all(rgb==EXACT,axis=2)
 v=rgb.astype(np.int16);r,g,b=v[:,:,0],v[:,:,1],v[:,:,2]
 strict=(g>=70)&((g-r)>=25)&((g-b)>=25)&(r<=155)&(b<=155)
 yy,xx=np.indices(rgb.shape[:2],dtype=np.float32)
 p0=np.asarray((130.0+dx,60.0+dy));p1=np.asarray((736.0+dx,328.0+dy));axis=p1-p0
 distance=np.abs(axis[0]*(yy-p0[1])-axis[1]*(xx-p0[0]))/np.linalg.norm(axis)
 eye=(xx>=740+dx)&(xx<=795+dx)&(yy>=245+dy)&(yy<=275+dy)
 corridor=(xx<=760+dx)&(yy<=350+dy)&(distance<=75)&~eye
 background|=strict&corridor
 distance_to_transparent=cv2.distanceTransform((~background).astype(np.uint8),cv2.DIST_L2,5)
 hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV);h,s=hsv[:,:,0],hsv[:,:,1]
 broad=(g>=60)&((g-r)>=18)&((g-b)>=18)&(r<=175)&(b<=175)&(h>=35)&(h<=85)&(s>=35)
 fringe=broad&corridor&(distance_to_transparent<=4.01)
 background|=fringe
 report.update({"exact_green_forced_transparent":True,"weapon_corridor_strict_pixels":int(np.count_nonzero(strict&corridor)),"weapon_corridor_broad_fringe_pixels":int(np.count_nonzero(fringe))})
 return background,report
def clean_runtime_edge(rgba,dx,dy):
 out=rgba.copy();rgb=out[:,:,:3];v=rgb.astype(np.int16);r,g,b=v[:,:,0],v[:,:,1],v[:,:,2]
 hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV);h,s=hsv[:,:,0],hsv[:,:,1]
 broad=(g>=60)&((g-r)>=18)&((g-b)>=18)&(r<=175)&(b<=175)&(h>=35)&(h<=85)&(s>=35)
 scale=384.0/1254.0;yy,xx=np.indices(out.shape[:2],dtype=np.float32)
 p0=np.asarray(((130.0+dx)*scale,(60.0+dy)*scale));p1=np.asarray(((736.0+dx)*scale,(328.0+dy)*scale));axis=p1-p0
 distance_axis=np.abs(axis[0]*(yy-p0[1])-axis[1]*(xx-p0[0]))/np.linalg.norm(axis)
 eye=(xx>=(740+dx)*scale)&(xx<=(795+dx)*scale)&(yy>=(245+dy)*scale)&(yy<=(275+dy)*scale)
 corridor=(xx<=(760+dx)*scale)&(yy<=(350+dy)*scale)&(distance_axis<=75*scale)&~eye
 visible=out[:,:,3]>=16;distance=cv2.distanceTransform(visible.astype(np.uint8),cv2.DIST_L2,5)
 fringe=broad&corridor&visible&(distance<=1.30);out[fringe]=(0,0,0,0)
 return out,int(np.count_nonzero(fringe))
def main():
 if not AUTH.is_file() or OUT.exists():raise SystemExit("authority missing or V6 keyfix output exists")
 authority=json.loads(AUTH.read_text(encoding="utf-8"));items={x["phase"]:x for x in authority["frames"]}
 FINAL.mkdir(parents=True);RUNTIME.mkdir(parents=True);QA.mkdir(parents=True)
 native={};runtime={};records=[]
 for phase in base.PHASES:
  item=items[phase];raw=RAW/f"ASTER_FIRE_WNW_{phase.upper()}_IMAGEGEN_V5_UAL6_RAW.png"
  rgb=np.asarray(Image.open(raw).convert("RGB"),dtype=np.uint8).copy()
  dx,dy=map(float,item["translation_image_px"]);background,report=corridor_mask(rgb,dx,dy)
  green=rgb.copy();green[background]=EXACT;alpha=np.where(background,0,255).astype(np.uint8);rgba=np.dstack((green,alpha))
  stem=f"ASTER_FIRE_WNW_{phase.upper()}_IMAGEGEN_V9_NO_SHOULDER"
  gp=FINAL/f"{stem}_GREEN.png";rp=FINAL/f"{stem}_RGBA.png";tp=RUNTIME/f"{stem}_RUNTIME_384_RGBA.png"
  runtime_rgba,runtime_fringe_removed=clean_runtime_edge(base.resize_rgba_clean(rgba,base.RUNTIME_SIZE),dx,dy)
  Image.fromarray(green,"RGB").save(gp,"PNG",optimize=True);Image.fromarray(rgba,"RGBA").save(rp,"PNG",optimize=True);Image.fromarray(runtime_rgba,"RGBA").save(tp,"PNG",optimize=True)
  native[phase]=rp;runtime[phase]=tp
  a=np.asarray(Image.open(rp).convert("RGBA"))
  records.append({"phase":phase,"raw":{"path":rel(raw),"sha256":sha256(raw)},"translation_image_px":[dx,dy],"green":{"path":rel(gp),"sha256":sha256(gp)},"rgba":{"path":rel(rp),"sha256":sha256(rp)},"runtime":{"path":rel(tp),"sha256":sha256(tp)},"matte":report,"runtime_boundary_fringe_removed":runtime_fringe_removed,"exact_green_opaque":int(np.count_nonzero(np.all(a[:,:,:3]==EXACT,axis=2)&(a[:,:,3]>=16)))})
 for first,last in ((native["aim_set"],native["ready_return"]),(runtime["aim_set"],runtime["ready_return"])):shutil.copyfile(first,last)
 atlas=Image.new("RGBA",(2304,384),(0,0,0,0))
 for i,phase in enumerate(base.PHASES):atlas.paste(Image.open(runtime[phase]).convert("RGBA"),(i*384,0))
 ap=RUNTIME/"ASTER_FIRE_WNW_NO_SHOULDER_UAL6_ATLAS_RGBA.png";atlas.save(ap,"PNG",optimize=True)
 review=Image.new("RGB",(1920,1080),(8,13,20));draw=ImageDraw.Draw(review);font=ImageFont.load_default();draw.text((24,18),"ASTER WNW V6 SOURCE-AUTHORITY CHROMA FINAL",fill=(245,247,250),font=font)
 for phase,(x,y) in zip(base.PHASES,((0,60),(640,60),(1280,60),(0,570),(640,570),(1280,570))):
  sprite=Image.open(native[phase]).convert("RGBA");sprite.thumbnail((500,500),Image.Resampling.LANCZOS);panel=Image.new("RGB",(640,500),(0,255,0));panel.paste(sprite,((640-sprite.width)//2,0),sprite);review.paste(panel,(x,y));draw.text((x+14,y+14),phase.upper(),fill=(255,201,74),font=font)
 reviewp=QA/"ASTER_FIRE_WNW_IMAGEGEN_V9_CHROMA_FINAL_REVIEW_1920X1080.png";review.save(reviewp,"PNG",optimize=True)
 result="PASS" if all(x["exact_green_opaque"]==0 for x in records) else "FAIL"
 report={"schema":9,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"result":result,"operation":"V8 native key plus 384 runtime broad-green cleanup within 1.3 pixels of transparency","authority":{"path":rel(AUTH),"sha256":sha256(AUTH)},"frames":records,"atlas":{"path":rel(ap),"sha256":sha256(ap)},"review":{"path":rel(reviewp),"sha256":sha256(reviewp),"resolution":[1920,1080]}}
 qp=QA/"ASTER_FIRE_WNW_IMAGEGEN_V9_CHROMA_FINAL_QA.json";qp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 if result!="PASS":raise RuntimeError(report)
 print(json.dumps({"qa":rel(qp),"atlas":rel(ap),"review":rel(reviewp)}));return 0
if __name__=="__main__":raise SystemExit(main())
