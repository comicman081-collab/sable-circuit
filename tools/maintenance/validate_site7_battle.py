"""Bounded in-app regression checks; does not generate art or import all assets."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "qa/site7_current_regression"
GODOT = Path("D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tmp").mkdir(exist_ok=True)
run_env = {**os.environ, "PYTHONDONTWRITEBYTECODE":"1", "PYTHONUTF8":"1", "TEMP":str(OUT / "tmp"), "TMP":str(OUT / "tmp")}
checks = []
jobs = [("project_static", [sys.executable, "-B", "tools/validate_project.py"])]
for name in ["motion_lab_character_runtime_smoke", "m7_authored_visual_smoke", "prototype_smoke", "m2_story_flow_smoke", "rook_motion_lab_app_smoke", "site7_battle_flow_smoke", "site7_battle_geometry_smoke", "m3_unique_art_smoke", "aster_projectile_v6_smoke"]:
    jobs.append((name, [str(GODOT), "--headless", "--path", str(ROOT), "--script", f"res://tests/smoke/{name}.gd"]))
for name, command in jobs:
    print("Checking " + name, flush=True)
    with (OUT / (name + ".log")).open("w", encoding="utf-8") as stream:
        result = subprocess.run(command, cwd=ROOT, env=run_env, stdout=stream, stderr=subprocess.STDOUT, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
    content = (OUT / (name + ".log")).read_text(encoding="utf-8")
    passed = result.returncode == 0 and ": PASS" in content and "ERROR:" not in content
    checks.append({"name":name,"pass":passed,"exit_code":result.returncode})
    print(name + ": " + ("PASS" if passed else "FAIL"), flush=True)
sources = {}
for ident in ["aster", "rook", "mica"]:
    for path in sorted((ROOT / "motion_lab_v1/public/assets/atlas" / ident).glob("*")):
        if path.suffix in [".webp", ".json", ".png"]:
            sources[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
implementation = {}
for folder, pattern in [("scripts","*.gd"),("scenes","*.tscn"),("data","*.json")]:
    for path in sorted((ROOT / folder).rglob(pattern)):
        implementation[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
for path in [ROOT / "project.godot", Path(__file__)]:
    implementation[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
report = {"status":"PASS_TECHNICAL_ONLY" if all(x["pass"] for x in checks) else "FAIL", "checks":checks,"character_scale_from_original":1.8,"current_source_hashes":sources,"implementation_hashes":implementation,"visual_approval":"Not inferred from technical tests"}
(OUT / "regression.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
raise SystemExit(0 if all(x["pass"] for x in checks) else 1)
