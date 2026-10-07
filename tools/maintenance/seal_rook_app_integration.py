"""Bind the approved Studio bytes to observed Godot app integration evidence."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "motion_lab_v1"
OUT = ROOT / "qa/rook_app_integration_20260913"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

package = read(LAB / "dist/rook.package.json")
delivery = read(LAB / "dist/rook.delivery.json")
assert delivery["status"] == "REVIEWED_DELIVERY"
assert delivery["package"]["sha256"] == sha(LAB / "dist/rook.package.json")
assert delivery["inputSHA256"] == package["inputSHA256"]
for name, digest in package["inputs"].items():
    assert sha(LAB / name) == digest, f"Changed approved Studio input: {name}"
assert sha(LAB / "dist/ROOK_Motion_Studio.html") == package["sha256"]
assert sha(LAB / "public/standalone/rook.html") == package["sha256"]
for field in ("sourceReviews", "cycleReviews", "runtimeReviews"):
    assert sha(LAB / delivery[field]["path"]) == delivery[field]["sha256"]

log_names = ["rook_smoke.log", "motion_lab_smoke_final.log", "site7_battle_flow.log",
             "site7_battle_geometry_smoke.log", "prototype_smoke.log",
             "m3_unique_art_smoke.log", "m7_authored_visual_smoke.log",
             "final_capture.stdout.log"]
checks = []
for name in log_names:
    content = (OUT / name).read_text(encoding="utf-8-sig")
    passed = ": PASS" in content and "ERROR:" not in content and ": FAIL" not in content
    assert passed, f"App check failed: {name}"
    checks.append({"log": name, "pass": passed, "sha256": sha(OUT / name),
                   "warnings": [line for line in content.splitlines() if "WARNING:" in line]})
assert not (OUT / "final_capture.stderr.log").read_text().strip()
capture = read(OUT / "final_capture/capture_report.json")
assert capture["status"] == "PASS_INPUT_AND_CAPTURE_ONLY" and not capture["failures"]
assert len(capture["stages"]) == 3

paths = ["AGENTS.md", "data/art_profiles/playable_profiles.json",
         "scripts/animation/motion_lab_character_runtime.gd", "scripts/actors/operator_actor.gd",
         "scripts/core/battle_texture_library.gd", "scripts/ui/story_stage_hud.gd",
         "scripts/ui/base_lobby.gd", "scripts/ui/title_screen.gd",
         "tests/smoke/motion_lab_character_runtime_smoke.gd",
         "tests/smoke/rook_motion_lab_app_smoke.gd",
         "tests/render/rook_motion_lab_app_capture.gd", "tools/maintenance/validate_site7_battle.py",
         "tools/maintenance/seal_rook_app_integration.py"]
evidence = [*sorted((OUT / "final_capture").glob("*.png")), OUT / "final_capture/capture_report.json",
            OUT / "visual_evidence_1080p.json", OUT / "RESULT_KO.md"]
result = {"recordedAt": datetime.now(timezone.utc).isoformat(),
          "status": "PASS_APP_INTEGRATION", "character": "rook", "remoteDeployment": False,
          "approvedStudioBuild": package["inputSHA256"], "studioInputsUnchanged": package["inputs"],
          "appChecks": checks, "appImplementation": {name: sha(ROOT / name) for name in paths},
          "evidence": {path.relative_to(ROOT).as_posix(): sha(path) for path in evidence},
          "scope": "Current accepted source reused in Godot; no new source/gait or Luna approval"}
(OUT / "integration_manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ROOK_APP_INTEGRATION_SEAL: PASS")
