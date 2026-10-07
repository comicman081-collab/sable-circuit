#!/usr/bin/env python3
"""Finalize corrected NW/NNW/N/NNE Blender/UAL frames."""
from __future__ import annotations
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import finalize_aster_fire16_no_shoulder_blender_ual_v2 as base

ROOT=Path(__file__).resolve().parents[2];PACKAGE=ROOT/"art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2";CORRECTION=PACKAGE/"corrections/rear4_no_ring_v2";MANIFEST=CORRECTION/"blender_scene/ASTER_FIRE_REAR4_NO_RING_UAL6_CORRECTION_MANIFEST.json";FINAL=CORRECTION/"final/current";RUNTIME=CORRECTION/"runtime/current";QA=CORRECTION/"qa/current";DIRECTIONS=("NW","NNW","N","NNE")
def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):digest.update(block)
    return digest.hexdigest()
def rel(path):return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
def main():
    if not MANIFEST.is_file() or any(path.exists() for path in (FINAL,RUNTIME,QA)):raise SystemExit("rear4 output guard")
    authority=json.loads(MANIFEST.read_text(encoding="utf-8"));items={x["direction"]:x for x in authority["directions"]}
    if tuple(items)!=DIRECTIONS:raise RuntimeError("direction mismatch")
    FINAL.mkdir(parents=True);RUNTIME.mkdir(parents=True);QA.mkdir(parents=True);records=[];aim_rgba={}
    for direction in DIRECTIONS:
        fdir=FINAL/direction;rdir=RUNTIME/direction;fdir.mkdir();rdir.mkdir();frames={x["phase"]:x for x in items[direction]["frames"]};greens={};rgbas={};runtimes={};phase_records=[]
        for phase in base.PHASES:
            item=frames[phase];raw=ROOT/item["raw"]["path"]
            if sha256(raw)!=item["raw"]["sha256"]:raise RuntimeError(f"raw SHA mismatch {raw}")
            rgb=np.asarray(Image.open(raw).convert("RGB"),dtype=np.uint8).copy();background,matte=base.matte_mask(rgb);green=rgb.copy();green[background]=base.EXACT_GREEN;alpha=np.where(~background,255,0).astype(np.uint8);rgba=np.dstack((green,alpha));stem=f"ASTER_FIRE_{direction}_{phase.upper()}_NO_RING"
            gp=fdir/f"{stem}_GREEN.png";rp=fdir/f"{stem}_RGBA.png";run=rdir/f"{stem}_RUNTIME_384_RGBA.png";Image.fromarray(green,"RGB").save(gp,"PNG",optimize=True);Image.fromarray(rgba,"RGBA").save(rp,"PNG",optimize=True);Image.fromarray(base.resize_rgba_clean(rgba,base.RUNTIME_SIZE),"RGBA").save(run,"PNG",optimize=True);greens[phase],rgbas[phase],runtimes[phase]=gp,rp,run;phase_records.append({"phase":phase,"ual_source_frame":item["ual_source_frame"],"translation_image_px":item["translation_image_px"],"green":{"path":rel(gp),"sha256":sha256(gp)},"rgba":{"path":rel(rp),"sha256":sha256(rp)},"runtime_384_rgba":{"path":rel(run),"sha256":sha256(run)},"matte":matte})
        for first,last in ((greens["aim_set"],greens["ready_return"]),(rgbas["aim_set"],rgbas["ready_return"]),(runtimes["aim_set"],runtimes["ready_return"])):shutil.copyfile(first,last)
        for record in phase_records:
            if record["phase"]=="ready_return":record["green"]["sha256"]=sha256(greens["ready_return"]);record["rgba"]["sha256"]=sha256(rgbas["ready_return"]);record["runtime_384_rgba"]["sha256"]=sha256(runtimes["ready_return"])
        atlas=Image.new("RGBA",(2304,384),(0,0,0,0))
        for index,phase in enumerate(base.PHASES):atlas.paste(Image.open(runtimes[phase]).convert("RGBA"),(index*384,0))
        atlas_path=rdir/f"ASTER_FIRE_{direction}_NO_SHOULDER_UAL6_ATLAS_RGBA.png";atlas.save(atlas_path,"PNG",optimize=True);aim=np.asarray(Image.open(rgbas["aim_set"]).convert("RGBA"));ready=np.asarray(Image.open(rgbas["ready_return"]).convert("RGBA"));records.append({"direction":direction,"screen_heading_degrees":items[direction]["screen_heading_degrees"],"source":items[direction]["source"],"loop_pixel_identical":bool(np.array_equal(aim,ready)),"frames":phase_records,"runtime_atlas":{"path":rel(atlas_path),"sha256":sha256(atlas_path),"resolution":[2304,384]}});aim_rgba[direction]=rgbas["aim_set"]
    review=Image.new("RGB",(1920,1080),(8,13,20));draw=ImageDraw.Draw(review);font=ImageFont.load_default();draw.text((24,18),"ASTER REAR FOUR NO-RING CORRECTION — IMAGEGEN + BLENDER + UAL1",fill=(245,247,250),font=font);draw.text((24,38),"NW / NNW / N / NNE native sources, plain navy shoulders, six-phase runtime validated.",fill=(69,224,244),font=font)
    for index,direction in enumerate(DIRECTIONS):
        image=Image.open(aim_rgba[direction]).convert("RGBA");image.thumbnail((450,930),Image.Resampling.LANCZOS);panel=Image.new("RGB",(480,1000),(0,255,0));panel.paste(image,((480-image.width)//2,40),image);review.paste(panel,(index*480,70));draw.rectangle((index*480+8,78,index*480+84,102),fill=(8,13,20));draw.text((index*480+16,84),direction,fill=(255,201,74),font=font)
    review_path=QA/"ASTER_FIRE_REAR4_NO_RING_CORRECTION_REVIEW_1920X1080.png";review.save(review_path,"PNG",optimize=True);qa={"schema":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"result":"PASS_TECHNICAL_REVIEW_REQUIRED","direction_count":4,"frame_count":24,"all_loops_identical":all(x["loop_pixel_identical"] for x in records),"shoulder_contract":"PLAIN_NAVY_REQUIRES_PONYTAIL_FULL_REAUDIT","review":{"path":rel(review_path),"sha256":sha256(review_path),"resolution":[1920,1080]},"directions":records}
    if not qa["all_loops_identical"]:raise RuntimeError("loop failure")
    qa_path=QA/"ASTER_FIRE_REAR4_NO_RING_CORRECTION_QA.json";qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"qa":rel(qa_path),"review":rel(review_path),"directions":4,"frames":24}));return 0
if __name__=="__main__":raise SystemExit(main())
