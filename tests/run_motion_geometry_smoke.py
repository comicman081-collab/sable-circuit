"""One owned, hidden, two-frame CPU Blender test; all files remain project-local."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools/character_pipeline"))
import motion_harness as h

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--blender",required=True)
p.add_argument("--out",required=True)
p.add_argument("--root-follow",action="store_true")
a = p.parse_args()
out = h.inside(a.out,exists=False)
if out.exists() or not out.is_relative_to(ROOT/"artifacts/motion_harness_audit/technical_fixtures"):
    raise ValueError("Fresh dedicated technical fixture output required")
out.mkdir(parents=True)
env = os.environ.copy()
for key in ("TEMP","TMP","TMPDIR","APPDATA","LOCALAPPDATA","XDG_CACHE_HOME","XDG_DATA_HOME","PYTHONPYCACHEPREFIX","BLENDER_USER_CONFIG","BLENDER_USER_SCRIPTS"):
    env[key] = str(out)
env["OMP_NUM_THREADS"] = "2"
command = [a.blender,"--background","--factory-startup","--disable-autoexec","--offline-mode","--threads","2","--python-exit-code","2",
           "--python",str(ROOT/"tests/blender/motion_geometry_smoke.py"),"--","--out",str(out)]
if a.root_follow:command.append('--root-follow')
with (out/"blender.log").open("w",encoding="utf-8") as log:
    completed = subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                               timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
if completed.returncode:
    raise SystemExit(f"Geometry smoke failed: {out/'blender.log'}")
geometry = h.read(out/"geometry.json")
h.validate_render_binding(geometry,"SYNTHETIC_QA_NOT_PRODUCTION")
first = geometry["frames"]["1"]["vertices_world_m"]["0"]
second = geometry["frames"]["2"]["vertices_world_m"]["0"]
assert first != second, "Actual evaluated vertices did not move"
assert geometry["frames"]["1"]["image_sha256"] != geometry["frames"]["2"]["image_sha256"], "Actual rendered poses did not change"
if a.root_follow:
    import math
    receipt=h.read(out/'render_receipt.json')
    assert receipt['camera_space']=='root_translation_locked'
    assert math.dist([second[i]-first[i] for i in range(3)],[1.45,-.5,.08])<1e-5, 'Root travel or actual skin deformation lost'
    assert geometry['frames']['2']['world_to_body_m'][0][3]==-1.25
    assert geometry['frames']['2']['world_to_body_m'][1][3]==.5
h.write(out/"test_result.json",{"gate":"PASS_HARNESS_SMOKE_ONLY","frames":2,"native_resolution":[1920,1920],
    "runtime_resolution":[384,384],"root_follow_tested":a.root_follow,"owned_child_exited":True,"candidate_status":"SYNTHETIC_QA_DO_NOT_PROMOTE"})
print("PAIRED_BLENDER_RENDER_AND_EVALUATED_VERTICES: PASS_HARNESS_SMOKE_ONLY")
