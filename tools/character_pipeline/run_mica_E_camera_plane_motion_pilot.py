"""Run exactly one reviewed, bounded MICA E camera-plane motion export."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g
from verify_mica_E_camera_plane_motion_handoff import verify_static_review_bundle


def run(args):
    plan_path = g.local(args.plan)
    review_path = g.local(args.review_bundle)
    plan = g.read(plan_path)
    if plan.get("schema") != 1 or plan.get("stage") != "motion_pilot_plan":
        raise ValueError("EXACT_CAMERA_PLANE_MOTION_PLAN_REQUIRED")
    config_path = g.resolve(plan["inputs"]["export_config"])
    config = g.read(config_path)
    blender_timeout = plan.get("limits", {}).get("timeout_seconds")
    if (isinstance(blender_timeout, bool) or not isinstance(blender_timeout, int)
            or not 240 <= blender_timeout <= 1200):
        raise ValueError("BOUNDED_CAMERA_PLANE_BLENDER_TIMEOUT_REQUIRED")
    out = g.local(plan["outputs"]["root"])
    if (g.local(config["output"]).parent != out or g.local(config["render_receipt"]).parent != out
            or plan["inputs"].get("runner") != g.ref(__file__)
            or plan["inputs"].get("verifier") != g.ref(ROOT / "tools/character_pipeline/verify_mica_E_camera_plane_motion_handoff.py")):
        raise ValueError("CAMERA_PLANE_MOTION_PLAN_RUNNER_BINDING_MISMATCH")
    verify_static_review_bundle(plan_path, config_path, review_path)
    attempt_path = out / "MOTION_PILOT_ATTEMPT.json"
    inputs_path = out / "MOTION_PILOT_INPUTS.json"
    result_path = out / "MOTION_PILOT_EXECUTION_RESULT.json"
    if attempt_path.exists() or inputs_path.exists() or result_path.exists():
        raise ValueError("CAMERA_PLANE_MOTION_INVOCATION_ALREADY_RESERVED")
    output_paths = [g.local(config["output"]), g.local(config["render_receipt"])]
    output_paths.extend(g.local(value) for row in config["frames"] for value in (row["master_image"], row["image"]))
    if any(path.exists() for path in output_paths):
        raise ValueError("CAMERA_PLANE_MOTION_OUTPUT_ALREADY_EXISTS")
    out.mkdir(parents=True, exist_ok=True)
    attempt = {
        "schema": 1,
        "stage": "camera_plane_motion_pilot_attempt",
        "status": "RESERVED_ONE_BLENDER_INVOCATION",
        "plan": g.ref(plan_path),
        "config": g.ref(config_path),
        "review_bundle": g.ref(review_path),
        "runner": g.ref(__file__),
        "limits": plan["limits"],
    }
    g.write(attempt_path, attempt)
    inputs = {
        "schema": 1,
        "stage": "camera_plane_motion_pilot_inputs",
        "plan": g.ref(plan_path),
        "config": g.ref(config_path),
        "attempt": g.ref(attempt_path),
        "review_bundle": g.ref(review_path),
        "runner": g.ref(__file__),
        "verifier": g.ref(ROOT / "tools/character_pipeline/verify_mica_E_camera_plane_motion_handoff.py"),
    }
    g.write(inputs_path, inputs)
    runtime_root = out / ".runtime"
    for name in ("tmp", "cache", "data", "blender_config", "blender_scripts", "pycache"):
        (runtime_root / name).mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        "TEMP": str(runtime_root / "tmp"), "TMP": str(runtime_root / "tmp"), "TMPDIR": str(runtime_root / "tmp"),
        "APPDATA": str(runtime_root / "data"), "LOCALAPPDATA": str(runtime_root / "data"),
        "XDG_CACHE_HOME": str(runtime_root / "cache"), "XDG_DATA_HOME": str(runtime_root / "data"),
        "BLENDER_USER_CONFIG": str(runtime_root / "blender_config"),
        "BLENDER_USER_SCRIPTS": str(runtime_root / "blender_scripts"),
        "PYTHONPYCACHEPREFIX": str(runtime_root / "pycache"),
    })
    verifier = ROOT / "tools/character_pipeline/verify_mica_E_camera_plane_motion_handoff.py"
    permit_log = out / "MOTION_PILOT_PERMIT.log"
    with permit_log.open("w", encoding="utf-8") as log:
        permit = subprocess.run([sys.executable, "-B", str(verifier), "--out", str(out)], cwd=ROOT, env=env,
                                stdout=log, stderr=subprocess.STDOUT, timeout=60,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if permit.returncode:
        g.write(result_path, {"schema": 1, "stage": "camera_plane_motion_pilot_execution", "status": "FAILED_BEFORE_BLENDER",
                              "attempt": g.ref(attempt_path), "permit_log": g.ref(permit_log)})
        raise ValueError("CAMERA_PLANE_MOTION_PERMIT_FAILED")
    receipt = g.verify_receipt(g.read(config_path)["generation_receipt"], stage="first_pose")
    blend = g.resolve(receipt["blend"])
    blender_log = out / "MOTION_PILOT_BLENDER.log"
    command = [str(ROOT / "tools/blender/5.2.1/blender.exe"), "--background", "--factory-startup", "--disable-autoexec",
               "--offline-mode", "--threads", "2", "--python-exit-code", "2", "--python",
               str(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py"), "--", "--config", str(config_path)]
    command.insert(2, str(blend))
    with blender_log.open("w", encoding="utf-8") as log:
        try:
            completed = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       timeout=blender_timeout,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        except subprocess.TimeoutExpired:
            g.write(result_path, {
                "schema": 1,
                "stage": "camera_plane_motion_pilot_execution",
                "status": "FAILED_BLENDER_TIMEOUT",
                "attempt": g.ref(attempt_path),
                "permit_log": g.ref(permit_log),
                "blender_log": g.ref(blender_log),
                "timeout_seconds": blender_timeout,
            })
            raise ValueError("CAMERA_PLANE_MOTION_BLENDER_TIMEOUT")
    result = {"schema": 1, "stage": "camera_plane_motion_pilot_execution",
              "status": "PASS_BLENDER_EXECUTION_NOT_VISUAL_OR_RUNTIME_PASS" if completed.returncode == 0 else "FAILED_BLENDER_EXECUTION",
              "attempt": g.ref(attempt_path), "permit_log": g.ref(permit_log), "blender_log": g.ref(blender_log),
              "exit_code": completed.returncode}
    if completed.returncode == 0:
        result["geometry"] = g.ref(config["output"])
        result["render_receipt"] = g.ref(config["render_receipt"])
    g.write(result_path, result)
    if completed.returncode:
        raise ValueError("CAMERA_PLANE_MOTION_BLENDER_FAILED")
    print("ONE_CAMERA_PLANE_MOTION_PILOT_EXECUTED", result["geometry"]["path"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--review-bundle", required=True)
    run(parser.parse_args())
