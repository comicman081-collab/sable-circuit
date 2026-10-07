"""Bounded, project-local intake for Tripo motion/body references.

No network, new model generation, visible-art export or runtime promotion.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g
from inspect_vrm_source import decode_glb, accessor

BUILDER = ROOT / "tools/character_pipeline/build_tripo_standing_reference.py"


def inspect(source, license_path):
    doc, binary = decode_glb(source)
    license_record = g.read(license_path)
    if license_record.get("model") != g.ref(source):
        raise ValueError("EXACT_GLB_LICENSE_REQUIRED")
    if (license_record.get("paid_at_generation_user_attested") is not True or
        license_record.get("commercial_use") != "ALLOW" or
        license_record.get("derivatives") != "ALLOW" or
        license_record.get("intended_use") != "internal_motion_and_body_reference" or
        not license_record.get("evidence")):
        raise ValueError("PAID_OUTPUT_LICENSE_EVIDENCE_REQUIRED")
    for evidence in license_record["evidence"]:
        g.resolve(evidence)
    if len(doc.get("skins", [])) != 1 or len(doc.get("animations", [])) != 1:
        raise ValueError("ONE_SKIN_AND_RUN_ACTION_REQUIRED")
    nodes = doc["nodes"]
    joints = doc["skins"][0]["joints"]
    if len(joints) != len(set(joints)) or any(type(i) is not int or not 0 <= i < len(nodes) for i in joints):
        raise ValueError("INVALID_SKIN_JOINTS")
    names = [nodes[i].get("name") for i in joints]
    required = {"Root", "Hip", "Pelvis", "L_Thigh", "L_Calf", "L_Foot", "L_ToeBase",
                "R_Thigh", "R_Calf", "R_Foot", "R_ToeBase", "Head", "L_Hand", "R_Hand"}
    if len(set(names)) != len(names) or not required.issubset(names):
        raise ValueError("UNIQUE_TRIPO_ANATOMICAL_BONES_REQUIRED")
    count = 0
    for node in nodes:
        if "mesh" not in node:
            continue
        if node.get("skin") != 0:
            raise ValueError("UNSKINNED_MESH")
        for primitive in doc["meshes"][node["mesh"]]["primitives"]:
            attrs = primitive["attributes"]
            positions = accessor(doc, binary, attrs["POSITION"])
            joint_rows = accessor(doc, binary, attrs["JOINTS_0"])
            weights = accessor(doc, binary, attrs["WEIGHTS_0"])
            if not len(positions) == len(joint_rows) == len(weights):
                raise ValueError("MISMATCHED_SKIN_ROWS")
            for indices, row in zip(joint_rows, weights):
                if (len(indices) != 4 or len(row) != 4 or abs(sum(row)-1) > .001 or
                    any(w < 0 or w > 1 for w in row) or
                    any(type(i) is not int or not 0 <= i < len(joints) for i in indices)):
                    raise ValueError("INVALID_ACTUAL_SKIN_WEIGHT")
            count += len(positions)
    if not count:
        raise ValueError("NO_SKINNED_VERTICES")
    animation = doc["animations"][0]
    times = []
    for sampler in animation["samplers"]:
        values = [r[0] for r in accessor(doc, binary, sampler["input"])]
        if len(values) < 2 or any(b <= a for a, b in zip(values, values[1:])):
            raise ValueError("STRICT_INCREASING_NATIVE_TIMESTAMPS_REQUIRED")
        times.extend(values)
        accessor(doc, binary, sampler["output"])
    return {"schema": 1, "stage": "tripo_motion_reference_intake", "production_ready": False,
        "visible_art_authority": "none", "model": g.ref(source), "license": g.ref(license_path),
        "inspector": g.ref(__file__), "decoder": g.ref(ROOT / "tools/character_pipeline/inspect_vrm_source.py"),
        "joint_count": len(joints), "vertices": count, "animation": animation["name"],
        "native_time_range_s": [min(times), max(times)],
        "duration_s": max(times)-min(times), "bone_names": names}


def build(source, license_path, out):
    audit = inspect(source, license_path)
    out = g.local(out)
    if not out.is_relative_to(ROOT / "art_src/motion_reference"):
        raise ValueError("MOTION_REFERENCE_OUTPUT_ROOT_REQUIRED")
    out.mkdir(parents=True, exist_ok=False)
    g.write(out / "INTAKE.json", audit)
    cache = out / "cache"
    cache.mkdir()
    env = os.environ.copy()
    for key in ("TEMP", "TMP", "TMPDIR", "APPDATA", "LOCALAPPDATA", "XDG_CACHE_HOME",
                "XDG_DATA_HOME", "BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "PYTHONPYCACHEPREFIX"):
        env[key] = str(cache)
    env.update(OMP_NUM_THREADS="2", PYTHONDONTWRITEBYTECODE="1")
    command = [str(ROOT / "tools/blender/5.2.1/blender.exe"), "--background", "--factory-startup",
        "--disable-autoexec", "--offline-mode", "--threads", "2", "--python-exit-code", "2",
        "--python", str(BUILDER), "--", "--input", str(g.local(source)),
        "--license", str(g.local(license_path)), "--out", str(out)]
    inputs = {"builder": g.ref(BUILDER), "runner": g.ref(__file__),
        "source": audit["model"], "license": audit["license"],
        "generation_harness": g.ref(ROOT / "tools/character_pipeline/generation_harness.py"),
        "decoder": audit["decoder"], "blender": g.ref(ROOT / "tools/blender/5.2.1/blender.exe")}
    g.write(out / "EXECUTION_INPUTS.json", inputs)
    try:
        with (out / "blender.log").open("w", encoding="utf-8") as log:
            child = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                timeout=240, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except subprocess.TimeoutExpired:
        g.write(out / "FAILURE.json", {"status":"FAIL", "reason":"OWNED_CHILD_TIMEOUT",
            "owned_child_killed_and_waited":True,"production_ready":False})
        raise
    if child.returncode:
        raise ValueError("TRIPO_CHILD_FAILED:" + str(out / "blender.log"))
    report = g.read(out / "INSPECTION.json")
    for evidence in [report["blend"], *report["images"], *inputs.values()]:
        g.resolve(evidence)
    pack = report.get("pack", {})
    for key in ("standing_pack", "run_reference", "humanoid_map", "run_geometry", "calibrator_input"):
        g.resolve(pack[key])
    g.write(out / "completion.json", {"schema":1, "stage":"tripo_reference_pack",
        "status": "COMPLETE_REFERENCE_PACK_ONLY",
        "visible_art_authority":"none", "execution_inputs":g.ref(out / "EXECUTION_INPUTS.json"),
        "child_claim":g.ref(out / "CHILD_CLAIM.json"),
        "production_ready": False, "owned_child_exited": True,
        "inspection": g.ref(out / "INSPECTION.json"), "intake": g.ref(out / "INTAKE.json")})
    return {"completion": g.ref(out / "completion.json"), "duration_s": report["duration_s"]}


def verify(pack_path):
    completion = g.read(pack_path)
    if (completion.get("stage") != "tripo_reference_pack" or completion.get("schema") != 1 or
        completion.get("production_ready") is not False or
        completion.get("visible_art_authority") != "none" or
        completion.get("owned_child_exited") is not True):
        raise ValueError("REFERENCE_ONLY_COMPLETION_REQUIRED")
    inputs = g.read(g.resolve(completion["execution_inputs"]))
    for reference in inputs.values():
        g.resolve(reference)
    if inputs.get("runner") != g.ref(__file__) or inputs.get("builder") != g.ref(BUILDER):
        raise ValueError("CURRENT_REFERENCE_IMPLEMENTATION_REQUIRED")
    claim = g.read(g.resolve(completion["child_claim"]))
    if (claim.get("inputs") != completion["execution_inputs"] or
        claim.get("builder") != inputs["builder"] or claim.get("source") != inputs["source"]):
        raise ValueError("EXACT_CONSUMED_CHILD_CLAIM_REQUIRED")
    intake = g.read(g.resolve(completion["intake"]))
    fresh = inspect(g.resolve(intake["model"]), g.resolve(intake["license"]))
    if fresh != intake:
        raise ValueError("INTAKE_NO_LONGER_REPRODUCES")
    report = g.read(g.resolve(completion["inspection"]))
    if report.get("source") != intake["model"] or report.get("builder") != inputs["builder"]:
        raise ValueError("PACK_SOURCE_OR_BUILDER_MISMATCH")
    pack = report["pack"]
    for reference in [report["blend"], *report["images"],
                      *[pack[k] for k in ("standing_pack","run_reference","humanoid_map","run_geometry","calibrator_input")]]:
        g.resolve(reference)
    geometry = g.read(g.resolve(pack["run_geometry"]))
    if (geometry.get("pack") != pack["standing_pack"] or geometry.get("source") != intake["model"] or
        geometry.get("production_ready") is not False or geometry.get("visible_art_authority") != "none" or
        geometry.get("extractor") != inputs["builder"] or
        pack.get("native_run_keys_unchanged") is not True or
        abs(geometry["duration_s"]-intake["duration_s"]) > 1e-6):
        raise ValueError("SOURCE_TIMING_OR_APPEARANCE_BOUNDARY_MISMATCH")
    for key in ("classifier", "contact_contract", "visual_promotion_contract"):
        g.resolve(geometry[key])
    humanoid = g.read(g.resolve(pack["humanoid_map"]))
    calibrator = g.read(g.resolve(pack["calibrator_input"]))
    if humanoid.get("source") != intake["model"] or humanoid.get("appearance_authority") != "none":
        raise ValueError("HUMANOID_MAP_SOURCE_MISMATCH")
    if (calibrator.get("source") != intake["model"] or
        calibrator.get("output_blend") != pack["run_reference"] or
        calibrator.get("run_geometry") != pack["run_geometry"] or
        calibrator.get("sole_mesh") != geometry.get("sole_mesh") or
        calibrator.get("sole_vertex_ids") != geometry.get("sole_vertex_ids") or
        calibrator.get("baked_frame_range") != report.get("frame_range")):
        raise ValueError("CALIBRATOR_PACK_BINDING_MISMATCH")
    return {"stage":"tripo_reference_pack", "status":"VERIFIED_REFERENCE_FILES_ONLY",
        "production_ready":False, "visible_art_authority":"none", "pack":g.ref(pack_path),
        "standing_pack":pack["standing_pack"], "run_reference":pack["run_reference"],
        "geometry":pack["run_geometry"], "contact_errors":geometry["contact_errors"],
        "allowed_next_action":"REVIEW_AND_CALIBRATE_TRIPO_MOTION_GEOMETRY"}


def next_action(job_path):
    job = g.read(job_path)
    if job.get("schema") != 1 or job.get("stage") != "motion_reference_resume":
        raise ValueError("MOTION_REFERENCE_RESUME_JOB_REQUIRED")
    reference = verify(g.resolve(job["reference_pack"]))
    generation = g.next_action(g.resolve(job["generation_job"]))
    for evidence in job.get("evidence", []):
        g.resolve(evidence)
    return {"job":g.ref(job_path), "production_ready":False, "allow_batch_generation":False,
        "motion_reference":reference, "generation":generation,
        "allowed_next_action":generation["allowed_next_action"],
        "independent_reference_action":reference["allowed_next_action"],
        "note":"Reference intake cannot grant source, pose, gait, runtime, review or promotion approval."}


def bridge(pack_path, out):
    """Bind actual joint motion to SABLE roles/directions, without raster output."""
    checked = verify(pack_path)
    geometry = g.read(g.resolve(checked["geometry"]))
    rows = geometry["samples"]
    first, last = rows[0]["joints_world_m"]["hips"], rows[-1]["joints_world_m"]["hips"]
    displacement = [last[i]-first[i] for i in (0,1)]
    duration = geometry["duration_s"]
    contract_path = ROOT / "tools/character_pipeline/motion_contract.json"
    contract = g.read(contract_path)
    # Body coordinates: forward = native -Y; anatomical left = native +X.
    # A linear reference origin removes only net planar travel for retarget
    # coordinates. Raw world positions, z/bob/sway and timing remain recorded.
    canonical = []
    for row in rows:
        fraction = row["time_s"] / duration
        origin = [first[i]+displacement[i]*fraction for i in (0,1)]
        joints = {role: [-(p[1]-origin[1]), p[0]-origin[0], p[2]]
                  for role,p in row["joints_world_m"].items()}
        canonical.append({"sample":row["sample"], "source_time_s":row["source_time_s"],
                          "time_s":row["time_s"], "reference_origin_native_xy_m":origin,
                          "joints_body_m":joints})
    directions = {}
    for index, name in enumerate(contract["directions"]):
        theta = -index * math.pi/4
        c,s = math.cos(theta),math.sin(theta)
        directions[name] = {"yaw_degrees":-index*45,
            "samples":[{"sample":row["sample"],"time_s":row["time_s"],
                "joints_world_basis_m":{role:[p[0]*c-p[1]*s,p[0]*s+p[1]*c,p[2]]
                    for role,p in row["joints_body_m"].items()}} for row in canonical]}
    result = {"schema":1,"stage":"sable_tripo_joint_motion_input", "production_ready":False,
        "visible_art_authority":"none", "source_pack":g.ref(pack_path),
        "raw_geometry":checked["geometry"],"generator":g.ref(__file__),
        "motion_contract":g.ref(contract_path),"source_motion_kind":"forward_run_with_native_planar_travel",
        "source_action_duration_s":duration, "source_action_cycle_count":"UNAPPROVED_REQUIRES_TEMPORAL_REVIEW",
        "actual_pelvis_net_planar_displacement_m":displacement,
        "actual_pelvis_mean_planar_speed_m_s":math.hypot(*displacement)/duration,
        "canonical_coordinate_system":"x forward, y anatomical left, z world up; metres",
        "canonical_samples":canonical, "directions":directions,
        "character_requirements":{actor:{"run_speed_pixels_per_second":speeds["run"],
            "required_travel_pixels_over_native_action":speeds["run"]*duration,
            "status":"HOLD_TARGET_RIG_SCALE_CONTACT_AND_VISUAL_GATES"} for actor,speeds in contract["actors"].items()},
        "contact_errors":checked["contact_errors"],
        "limitations":["Geometry input only; eight rotations do not approve visible eight-direction art.",
            "No walking, strafing, backward running or independent 8x8 firing is inferred from forward Run.",
            "Raw native source motion remains the measurement authority; linear coordinates are not a ground-contact correction.",
            "Use visible_frame_harness_current.py for future visible frames after exact contact and independent reviews."]}
    g.write(out, result)
    return {"bridge":g.ref(out),"directions":len(directions),"samples_per_direction":len(canonical),
            "production_ready":False}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["inspect", "build", "verify", "next", "bridge"])
    p.add_argument("--input", required=True)
    p.add_argument("--license")
    p.add_argument("--out")
    a = p.parse_args()
    if a.command in ("build", "inspect") and (not a.license or not a.out):
        p.error("build/inspect require --license and --out")
    if a.command == "bridge":
        if not a.out: p.error("bridge requires --out")
        result = bridge(a.input, a.out)
    elif a.command == "verify":
        result = verify(a.input)
    elif a.command == "next":
        result = next_action(a.input)
    elif a.command == "build":
        result = build(a.input, a.license, a.out)
    else:
        result = inspect(a.input, a.license)
        g.write(a.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
