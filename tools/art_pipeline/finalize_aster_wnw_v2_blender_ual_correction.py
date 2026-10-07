#!/usr/bin/env python3
"""Finalize the corrected WNW direction before promotion into FIRE16."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import finalize_aster_fire16_no_shoulder_blender_ual_v2 as base


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2"
VERSION = int(os.environ.get("ASTER_WNW_IMAGEGEN_VERSION", "2"))
if VERSION not in (2, 3, 4, 5):
    raise RuntimeError(f"unsupported WNW ImageGen version: {VERSION}")
CORRECTION = PACKAGE / f"corrections/wnw_imagegen_v{VERSION}"
MANIFEST = CORRECTION / f"blender_scene/ASTER_FIRE_WNW_IMAGEGEN_V{VERSION}_UAL6_CORRECTION_MANIFEST.json"
FINAL = CORRECTION / "final/current"
RUNTIME = CORRECTION / "runtime/current"
QA = CORRECTION / "qa/current"


def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> int:
    if not MANIFEST.is_file() or any(path.exists() for path in (FINAL,RUNTIME,QA)):
        raise SystemExit("correction manifest missing or output exists")
    authority=json.loads(MANIFEST.read_text(encoding="utf-8"))
    frames={item["phase"]:item for item in authority["frames"]}
    if tuple(frames)!=base.PHASES or authority["target_screen_heading_degrees"]!=202.5:
        raise RuntimeError("correction contract mismatch")
    FINAL.mkdir(parents=True);RUNTIME.mkdir(parents=True);QA.mkdir(parents=True)
    greens={};rgbas={};runtimes={};records=[]
    for phase in base.PHASES:
        item=frames[phase];raw=ROOT/item["raw"]["path"]
        if sha256(raw)!=item["raw"]["sha256"]:raise RuntimeError(f"raw SHA mismatch: {raw}")
        rgb=np.asarray(Image.open(raw).convert("RGB"),dtype=np.uint8).copy()
        background,matte=base.matte_mask(rgb);green=rgb.copy();green[background]=base.EXACT_GREEN;alpha=np.where(~background,255,0).astype(np.uint8);rgba=np.dstack((green,alpha))
        stem=f"ASTER_FIRE_WNW_{phase.upper()}_IMAGEGEN_V{VERSION}_NO_SHOULDER"
        green_path=FINAL/f"{stem}_GREEN.png";rgba_path=FINAL/f"{stem}_RGBA.png";runtime_path=RUNTIME/f"{stem}_RUNTIME_384_RGBA.png"
        Image.fromarray(green,"RGB").save(green_path,"PNG",optimize=True);Image.fromarray(rgba,"RGBA").save(rgba_path,"PNG",optimize=True);Image.fromarray(base.resize_rgba_clean(rgba,base.RUNTIME_SIZE),"RGBA").save(runtime_path,"PNG",optimize=True)
        greens[phase],rgbas[phase],runtimes[phase]=green_path,rgba_path,runtime_path
        records.append({"phase":phase,"ual_source_frame":item["ual_source_frame"],"translation_image_px":item["translation_image_px"],"green":{"path":rel(green_path),"sha256":sha256(green_path)},"rgba":{"path":rel(rgba_path),"sha256":sha256(rgba_path)},"runtime_384_rgba":{"path":rel(runtime_path),"sha256":sha256(runtime_path)},"matte":matte})
    for first,last in ((greens["aim_set"],greens["ready_return"]),(rgbas["aim_set"],rgbas["ready_return"]),(runtimes["aim_set"],runtimes["ready_return"])):shutil.copyfile(first,last)
    for record in records:
        if record["phase"]=="ready_return":
            record["green"]["sha256"]=sha256(greens["ready_return"]);record["rgba"]["sha256"]=sha256(rgbas["ready_return"]);record["runtime_384_rgba"]["sha256"]=sha256(runtimes["ready_return"])
    atlas=Image.new("RGBA",(2304,384),(0,0,0,0))
    for index,phase in enumerate(base.PHASES):atlas.paste(Image.open(runtimes[phase]).convert("RGBA"),(index*384,0))
    atlas_path=RUNTIME/"ASTER_FIRE_WNW_NO_SHOULDER_UAL6_ATLAS_RGBA.png";atlas.save(atlas_path,"PNG",optimize=True)
    review=Image.new("RGB",(1920,1080),(8,13,20));draw=ImageDraw.Draw(review);font=ImageFont.load_default();draw.text((24,18),f"ASTER WNW IMAGEGEN V{VERSION} CORRECTION — BLENDER + UAL1 SIX PHASES",fill=(245,247,250),font=font);draw.text((24,38),"Corrected shallow 22.5-degree rise toward screen-left; both shoulders plain navy.",fill=(69,224,244),font=font)
    positions=((0,60),(640,60),(1280,60),(0,570),(640,570),(1280,570))
    for phase,(x,y) in zip(base.PHASES,positions):
        sprite=Image.open(rgbas[phase]).convert("RGBA");sprite.thumbnail((500,500),Image.Resampling.LANCZOS);panel=Image.new("RGB",(640,500),(0,255,0));panel.paste(sprite,((640-sprite.width)//2,0),sprite);review.paste(panel,(x,y));draw.rectangle((x+8,y+8,x+190,y+30),fill=(8,13,20));draw.text((x+14,y+14),phase.upper(),fill=(255,201,74),font=font)
    review_path=QA/f"ASTER_FIRE_WNW_IMAGEGEN_V{VERSION}_CORRECTION_REVIEW_1920X1080.png";review.save(review_path,"PNG",optimize=True)
    aim=np.asarray(Image.open(rgbas["aim_set"]).convert("RGBA"));ready=np.asarray(Image.open(rgbas["ready_return"]).convert("RGBA"))
    qa={"schema":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"result":"PASS_TECHNICAL_REVIEW_REQUIRED","direction":"WNW","screen_heading_degrees":202.5,"loop_pixel_identical":bool(np.array_equal(aim,ready)),"shoulder_contract":"PLAIN_NAVY_REQUIRES_PONYTAIL_FULL_AUDIT","review":{"path":rel(review_path),"sha256":sha256(review_path),"resolution":[1920,1080]},"atlas":{"path":rel(atlas_path),"sha256":sha256(atlas_path),"resolution":[2304,384]},"frames":records}
    if not qa["loop_pixel_identical"]:raise RuntimeError("loop contract failed")
    qa_path=QA/f"ASTER_FIRE_WNW_IMAGEGEN_V{VERSION}_CORRECTION_QA.json";qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"qa":rel(qa_path),"atlas":rel(atlas_path),"review":rel(review_path)}))
    return 0


if __name__=="__main__":raise SystemExit(main())
