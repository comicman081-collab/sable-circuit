#!/usr/bin/env python3
"""Rebuild FIRE16 evidence after WNW/rear-four no-ring corrections."""
from __future__ import annotations
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
import finalize_aster_fire16_no_shoulder_blender_ual_v2 as base

ROOT=Path(__file__).resolve().parents[2];PACKAGE=ROOT/"art_src/pilot_v2/aster_v2/animation_360/fire16_no_shoulder_blender_ual_v2";FINAL=PACKAGE/"final/current";RUNTIME=PACKAGE/"runtime/current";QA=PACKAGE/"qa/current";VALIDATOR=ROOT/"tools/art_pipeline/validate_visual_evidence_1080p.py";DIRECTIONS=base.DIRECTIONS
VERSION=int(os.environ.get("ASTER_FIRE16_EVIDENCE_VERSION","3"))
if VERSION not in (3,4,5,6,7,8,9):raise RuntimeError(f"unsupported evidence version: {VERSION}")
def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):digest.update(block)
    return digest.hexdigest()
def rel(path):return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
def one(directory,pattern):
    matches=tuple(Path(directory).glob(pattern))
    if len(matches)!=1:raise RuntimeError(f"expected one {pattern} in {directory}, got {len(matches)}")
    return matches[0]
def main():
    contact=QA/f"ASTER_FIRE16_NO_SHOULDER_UAL6_CONTACT_V{VERSION}_1920X1080.png";details=QA/f"ASTER_FIRE16_NO_SHOULDER_NATIVE_DETAILS_V{VERSION}_1920X1080.png";qa_path=QA/f"ASTER_FIRE16_NO_SHOULDER_UAL6_QA_V{VERSION}.json";manifest_path=QA/f"ASTER_FIRE16_NO_SHOULDER_UAL6_MANIFEST_V{VERSION}.json"
    if any(path.exists() for path in (contact,details,qa_path,manifest_path)):raise SystemExit(f"V{VERSION} evidence exists")
    runtime_aim={d:one(RUNTIME/d,"*AIM_SET*RUNTIME_384_RGBA.png") for d in DIRECTIONS};green_aim={d:one(FINAL/d,"*AIM_SET*GREEN.png") for d in DIRECTIONS}
    base.build_contact(runtime_aim,contact);base.build_native_details(green_aim,details);evidence=[]
    for image in (contact,details):
        output=image.with_name(image.stem+"_EVIDENCE.json");result=subprocess.run([sys.executable,os.fspath(VALIDATOR),os.fspath(image),"--output",os.fspath(output)],cwd=ROOT,capture_output=True,text=True,check=False)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        report=json.loads(output.read_text(encoding="utf-8"));evidence.append({"image":{"path":rel(image),"sha256":sha256(image),"resolution":[1920,1080]},"validator":{"path":rel(output),"sha256":sha256(output),"gate":report["gate"]}})
    directions=[]
    for direction in DIRECTIONS:
        atlas=RUNTIME/direction/f"ASTER_FIRE_{direction}_NO_SHOULDER_UAL6_ATLAS_RGBA.png";aim=one(FINAL/direction,"*AIM_SET*RGBA.png");ready=one(FINAL/direction,"*READY_RETURN*RGBA.png");directions.append({"direction":direction,"source_master":{"path":rel(green_aim[direction]),"sha256":sha256(green_aim[direction])},"runtime_atlas":{"path":rel(atlas),"sha256":sha256(atlas),"resolution":[2304,384]},"loop_pixel_identical":bool(np.array_equal(np.asarray(Image.open(aim).convert("RGBA")),np.asarray(Image.open(ready).convert("RGBA"))))})
    corrected=("WNW","NW","NNW","N","NNE");qa={"schema":VERSION,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"result":"PASS_TECHNICAL_PONYTAIL_FULL_FINAL_REAUDIT_REQUIRED","direction_count":16,"phase_count_per_direction":6,"frame_count":96,"corrected_directions":list(corrected),"all_loops_identical":all(x["loop_pixel_identical"] for x in directions),"both_shoulders_contract":"PLAIN_NAVY_FABRIC_REQUIRES_PONYTAIL_FULL_FINAL_REAUDIT","visual_pass_claimed":False,"evidence":evidence}
    if not qa["all_loops_identical"]:raise RuntimeError("loop failure")
    qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    wnw_source_version=VERSION-1 if 4<=VERSION<=6 else (5 if VERSION>=7 else 2)
    provenance=[PACKAGE/f"corrections/wnw_imagegen_v{wnw_source_version}/blender_scene/ASTER_FIRE_WNW_IMAGEGEN_V{wnw_source_version}_UAL6_CORRECTION_MANIFEST.json",PACKAGE/"corrections/rear4_no_ring_v2/blender_scene/ASTER_FIRE_REAR4_NO_RING_UAL6_CORRECTION_MANIFEST.json"]
    if VERSION>=7:
        keyfix=9 if VERSION>=9 else (8 if VERSION>=8 else 6)
        provenance.append(PACKAGE/f"corrections/wnw_imagegen_v5_chroma_final_v{keyfix}/qa/current/ASTER_FIRE_WNW_IMAGEGEN_V{keyfix}_CHROMA_FINAL_QA.json")
    manifest={"schema":VERSION,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"role":"ASTER corrected true sixteen-direction no-shoulder Blender/UAL runtime package","status":"PONYTAIL_FULL_FINAL_REAUDIT_REQUIRED","promotion_ready":False,"runtime_asset":True,"visual_pass_claimed":False,"visible_source_author":"built-in ImageGen","local_motion_tools":["Blender 5.2.1 LTS","UAL1 Pistol_Shoot CC0-1.0"],"correction_provenance":[{"path":rel(path),"sha256":sha256(path)} for path in provenance],"directions":directions,"qa":{"path":rel(qa_path),"sha256":sha256(qa_path),"result":qa["result"]},"retention":f"current corrected V{VERSION} plus exactly one immediately previous candidate"};manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"manifest":rel(manifest_path),"contact":rel(contact),"details":rel(details),"directions":16,"corrected":list(corrected)}));return 0
if __name__=="__main__":raise SystemExit(main())
