#!/usr/bin/env python3
"""Fail-closed motion audit, real-engine runner and content-bound promotion gate.

No source pixels are generated or repaired here. Structural PASS is never visual
PASS. `audit` is safe for broken candidates; `run` starts bounded, owned Godot
children only. A seal is issued only from complete independently reviewed evidence.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "tools/character_pipeline/motion_contract.json"
REJECTIONS = ROOT / "artifacts/quarantine/motion_rejections.json"
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = ("idle", "move", "fire")
IMPLEMENTATION = (
    "tools/character_pipeline/motion_harness.py",
    "tools/character_pipeline/motion_contract.json",
    "tools/character_pipeline/sable_character_pipeline.py",
    "tools/character_pipeline/render_fast_motion_blender_ual.py",
    "tools/character_pipeline/export_evaluated_motion_geometry.py",
    "tools/character_pipeline/root_locked_capture.py",
    "tools/character_pipeline/generation_harness.py",
    "tools/character_pipeline/generation_contract.json",
    "tools/character_pipeline/inspect_vrm_source.py",
    "tools/character_pipeline/collect_generation_mesh_preflight.py",
    "tools/character_pipeline/build_mica_skinned_pilot.py",
    "tools/character_pipeline/run_mica_skinned_pilot.py",
    "tools/art_pipeline/validate_visual_evidence_1080p.py",
    "tools/character_pipeline/package_mica_interactive_preview_v5.py",
    "tests/render/character_motion_harness.gd",
    "scripts/animation/fast_character_runtime.gd",
    "scripts/actors/operator_actor.gd",
    "scripts/combat/prototype_projectile.gd",
    "scenes/actors/player/OperatorActor.tscn",
    "data/art_profiles/playable_profiles.json",
    "project.godot",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def inside(value, *, exists=True):
    value = str(value).removeprefix("res://")
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    if p == ROOT or not p.is_relative_to(ROOT):
        raise ValueError(f"Project-local non-root path required: {p}")
    if exists and not p.exists():
        raise ValueError(f"Missing evidence/input: {p}")
    return p


def rel(p):
    return inside(p, exists=False).relative_to(ROOT).as_posix()


def digest(p):
    h = hashlib.sha256()
    with inside(p).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def read(p):
    def invalid(v):
        raise ValueError(f"Non-finite JSON value: {v}")
    value = json.loads(inside(p).read_text(encoding="utf-8-sig"), parse_constant=invalid)
    if not isinstance(value, dict):
        raise ValueError(f"Object required: {p}")
    return value


def write(p, value):
    p = inside(p, exists=False)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(p)


def number(value, label, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"Finite number required: {label}")
    if positive and value <= 0:
        raise ValueError(f"Positive number required: {label}")
    return float(value)


def rejection_reasons(paths):
    """Path AND content matching: renaming rejected inputs cannot clear rejection."""
    if not REJECTIONS.exists():
        raise ValueError("Rejection registry missing; refusing to bypass quarantine")
    records = read(REJECTIONS).get("records", [])
    failures = []
    for p in {inside(x) for x in paths}:
        for record in records:
            if record.get("status") != "FAIL_NOT_PROMOTABLE":
                continue
            matched = any(p == inside(x, exists=False) or p.is_relative_to(inside(x, exists=False))
                          for x in record.get("roots", []))
            if not matched and p.is_file():
                matched = digest(p) in record.get("file_sha256", [])
            if matched:
                failures.append(f"REJECTED_SOURCE:{record['id']}:{rel(p)}")
    return sorted(set(failures))


def assert_not_rejected(paths):
    failures = rejection_reasons(paths)
    if failures:
        raise ValueError("\n".join(failures))


def state_names(d):
    states = d.get("states", {})
    allowed = {"idle", "move", "fire", "run", "move_fire", "run_fire"}
    if not isinstance(states, dict) or not set(STATES).issubset(states) or not set(states).issubset(allowed):
        raise ValueError("UNSUPPORTED_STATE_REPRESENTATION: add a tested adapter, not uninspected assets")
    return tuple(states)


def phase_starts(row):
    count = int(number(row['frames'], 'representation frames', positive=True))
    values = row.get('phase_starts', [i/count for i in range(count)])
    if not isinstance(values, list) or len(values) != count:
        raise ValueError('INVALID_COMBINED_PHASE_STARTS')
    values = [number(value, 'phase start') for value in values]
    if not values or values[0] != 0 or values[-1] >= 1 or any(b <= a for a,b in zip(values,values[1:])):
        raise ValueError('INVALID_COMBINED_PHASE_STARTS')
    return values


def phase_frame(row, phase):
    return bisect.bisect_right(phase_starts(row), phase % 1)-1


def representation_errors(d):
    representation = d.get("representation", {})
    kind = d.get("aim_move_policy")
    if representation.get("schema") != 1 or representation.get("kind") != kind:
        return ["MISSING_BOUND_MOVE_AIM_REPRESENTATION"]
    rows = representation.get("assets", [])
    if kind == "independent_upper_lower":
        # ASTER has a separate layer renderer; this descriptor is consumed by
        # FastCharacterRuntime, which must not claim support from filenames.
        return ["INDEPENDENT_LAYER_RUNTIME_ADAPTER_NOT_IMPLEMENTED"]
    elif kind == "authored_8x8":
        expected = {(mode, move, aim, fire) for mode in ("walk","run") for move in DIRECTIONS for aim in DIRECTIONS for fire in (False,True)}
        keys = [(r.get("mode"),r.get("move"),r.get("aim"),r.get("firing")) for r in rows]
    else:
        return ["UNSUPPORTED_MOVE_AIM_REPRESENTATION"]
    if set(keys) != expected or len(keys) != len(expected):
        return ["MOVE_AIM_ASSET_COVERAGE"]
    cadence = {}
    for row in rows:
        p = verify_evidence_file(row)
        cell = number(row["cell_size"], "representation cell", positive=True)
        frames = number(row["frames"], "representation frames", positive=True)
        fps = number(row["fps"], "representation fps", positive=True)
        if cell != int(cell) or frames != int(frames) or cell != d.get('cell_size') or not 8 <= frames <= 512 or type(row['firing']) is not bool:
            return ["INVALID_REPRESENTATION_TIMING_OR_CELL"]
        cell,frames=int(cell),int(frames)
        timing=(frames,fps,tuple(phase_starts(row)))
        if cadence.setdefault(row['mode'],timing) != timing:
            return ["COMBINED_PHASE_CADENCE_MISMATCH"]
        points=row.get('muzzle_xy',[])
        if not isinstance(points,list) or len(points)!=frames:
            return ["COMBINED_FRAME_MUZZLES_REQUIRED"]
        for point in points:
            if not isinstance(point,list) or len(point)!=2 or any(not 0 <= number(v,'combined muzzle') < cell for v in point):
                return ["COMBINED_MUZZLE_OUT_OF_CELL"]
        with Image.open(p) as image:
            if cell > 4096 or frames > 512 or image.mode != "RGBA" or image.size != (cell,cell*frames):
                return ["INVALID_REPRESENTATION_ATLAS"]
    return []


def snapshot(descriptor_path, extra_paths=()):
    """Bind source atlases, descriptor, generator, runtime and review contract."""
    descriptor_path = inside(descriptor_path)
    d = read(descriptor_path)
    paths = {descriptor_path, REJECTIONS}
    paths.update(inside(p) for p in IMPLEMENTATION)
    paths.update(inside(p) for p in extra_paths)
    for direction in DIRECTIONS:
        for state in state_names(d):
            paths.add(inside(d["directions"][direction][state + "_atlas"]))
    for row in d.get("representation", {}).get("assets", []):
        paths.add(verify_evidence_file(row))
    provenance = d.get("source_contract", {}).get("provenance")
    if provenance:
        p = inside(provenance)
        paths.add(p)
        for direction in DIRECTIONS:
            for state in state_names(d):
                source = p.parent / direction / (state + "_green.png")
                if source.exists():
                    paths.add(source)
    # Candidate builders must list exact input/tool files, not a prose version.
    build_path = descriptor_path.parent / "MOTION_BUILD_INPUTS.json"
    if build_path.exists():
        paths.add(build_path)
        for value, expected in read(build_path).get("files", {}).items():
            p = inside(value)
            if digest(p) != expected:
                raise ValueError(f"STALE_BUILD_INPUT:{value}")
            paths.add(p)
    files = {rel(p): digest(p) for p in sorted(paths)}
    return {"descriptor": rel(descriptor_path), "files": files, "subject_sha256": canonical(files)}


def build_closure_errors(path):
    if not inside(path, exists=False).is_file():
        return ["MISSING_CONTENT_BOUND_BUILD_INPUTS"]
    build = read(path)
    errors = []
    extensions = {"source_art": {".png", ".webp"}, "blender_scene": {".blend"},
                  "ual": {".json", ".fbx", ".glb"}, "generator": {".py"}, "license": {".json", ".md", ".txt"},
                  "generation_receipt": {".json"}}
    for role, allowed in extensions.items():
        files = build.get("roles", {}).get(role, [])
        if not files or not isinstance(files, list):
            errors.append("MISSING_BUILD_ROLE:" + role)
            continue
        for value in files:
            p = inside(value)
            if p.suffix.lower() not in allowed or build.get("files", {}).get(rel(p)) != digest(p):
                errors.append("INVALID_BUILD_ROLE:" + role)
    if build.get("qa_fixture_only"):
        errors.append("SYNTHETIC_TEST_FIXTURE_NOT_PRODUCTION")
    if build.get('roles',{}).get('generation_receipt'):
        import generation_harness as generation
        approval=generation.motion_build_bindings(build['roles']['generation_receipt'],build.get('actor_id'),build.get('costume_id'))
        if any(build.get('files',{}).get(p)!=value for p,value in approval['files'].items()):
            errors.append('MISSING_GENERATION_APPROVAL_HASH_CLOSURE')
        for role in ('source_art','blender_scene'):
            if not {rel(p) for p in build['roles'].get(role,[])}.issubset(approval[role]):
                errors.append('UNAPPROVED_GENERATION_BUILD_ROLE:'+role)
    return errors


def audit(descriptor_path):
    contract = read(CONTRACT)
    d = read(descriptor_path)
    errors, holds, metrics = [], [], {}
    try:
        snap = snapshot(descriptor_path)
        errors.extend(rejection_reasons(snap["files"]))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        snap = {}
        errors.append(f"SNAPSHOT:{exc}")
    if set(d.get("directions", {})) != set(DIRECTIONS):
        errors.append("DIRECTION_COVERAGE")
    if d.get("actor_id") not in contract["actors"]:
        errors.append("UNDECLARED_ACTOR_SPEED_CONTRACT")
    try:
        holds.extend(build_closure_errors(inside(descriptor_path).parent / "MOTION_BUILD_INPUTS.json"))
        build_path=inside(descriptor_path).parent/'MOTION_BUILD_INPUTS.json'
        if build_path.exists() and any(read(build_path).get(k)!=d.get(k) for k in ('actor_id','costume_id')):
            errors.append('GENERATION_BUILD_ACTOR_OR_COSTUME_MISMATCH')
    except (ValueError, TypeError, OSError) as exc:
        errors.append("BUILD_CLOSURE:" + str(exc))
    try:
        cell = int(number(d["cell_size"], "cell_size", positive=True))
        number(d["display_scale"], "display_scale", positive=True)
        for direction in DIRECTIONS:
            entry = d["directions"][direction]
            metrics[direction] = {}
            for state in state_names(d):
                cfg = d["states"][state]
                frames = int(number(cfg["frames"], "frame_count", positive=True))
                fps = number(cfg["fps"], "fps", positive=True)
                if frames > 512 or cell > 4096:
                    raise ValueError("Unbounded atlas dimensions")
                p = inside(entry[state + "_atlas"])
                with Image.open(p) as image:
                    if image.size != (cell, cell * frames) or image.mode != "RGBA":
                        raise ValueError(f"ATLAS_LAYOUT_RGBA:{rel(p)}")
                    points = entry.get(state + "_muzzle_xy")
                    if not isinstance(points, list) or len(points) != frames:
                        errors.append(f"FRAME_SOCKET_COVERAGE:{direction}:{state}")
                        continue
                    floating, hashes = [], []
                    for frame in range(frames):
                        rgba = image.crop((0, cell * frame, cell, cell * (frame + 1)))
                        hashes.append(hashlib.sha256(rgba.tobytes()).hexdigest())
                        xy = points[frame]
                        if not isinstance(xy, list) or len(xy) != 2:
                            raise ValueError("MALFORMED_SOCKET")
                        x, y = [number(v, "muzzle") for v in xy]
                        if not (0 <= x < cell and 0 <= y < cell):
                            errors.append(f"SOCKET_OUTSIDE_CELL:{direction}:{state}:{frame}")
                            continue
                        radius = int(contract["runtime"]["socket_to_opaque_pixel_max"])
                        alpha = rgba.getchannel("A").crop((max(0, int(x) - radius), max(0, int(y) - radius),
                                                           min(cell, int(x) + radius + 1), min(cell, int(y) + radius + 1)))
                        if alpha.getextrema()[1] < 128:
                            floating.append(frame)
                    metrics[direction][state] = {"unique_full_cells": len(set(hashes)), "floating_socket_frames": floating}
                    if floating:
                        errors.append(f"SOCKET_IN_EMPTY_SPACE:{direction}:{state}:{floating}")
                    # Presence of pixels does NOT identify a barrel tip. Manual per-frame observation is still mandatory.
                    if state == "move" and len(set(hashes)) < 8:
                        errors.append(f"INSUFFICIENT_MOVE_POSES:{direction}")
            track = d.get("move_root_sync", {}).get("directional_tracks", {}).get(direction)
            if track:
                count = int(d["states"]["move"]["frames"])
                pos = [number(x, "root position") for x in track.get("frame_positions", [])]
                advance = number(track.get("cycle_advance"), "cycle advance", positive=True)
                if len(pos) != count or any(b < a for a, b in zip(pos, pos[1:])) or not pos or pos[0] < 0 or pos[-1] >= advance:
                    errors.append(f"INVALID_ROOT_TRACK:{direction}")
                speed = advance * d["states"]["move"]["fps"] / count
                metrics[direction]["authored_world_px_per_second"] = speed
                wanted = contract["actors"].get(d["actor_id"], {}).get("walk", 0)
                if wanted and abs(speed / wanted - 1) > contract["runtime"]["speed_relative_error_max"]:
                    errors.append(f"ROOT_SPEED_CONTRACT:{direction}:authored={speed:.4f}:walk={wanted}")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        errors.append(f"MALFORMED_ASSET:{exc}")
    try:
        holds.extend(representation_errors(d))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        errors.append("REPRESENTATION:"+str(exc))
    holds.extend(["INDEPENDENT_GAIT_AND_VISIBLE_MUZZLE_OBSERVATIONS_REQUIRED", "DYNAMIC_ENGINE_AND_HTML_PARITY_REQUIRED", "TEMPORAL_VISUAL_PONYTAIL_WEB_REVIEWS_REQUIRED"])
    return {"schema": 1, "created_utc": now(), "gate": "FAIL" if errors else "HOLD", "scope": "static_diagnostic_not_visual_approval",
            "snapshot": snap, "errors": errors, "holds": holds, "metrics": metrics}


def expected_cases():
    keys = set()
    for mode in ("walk", "run"):
        for move in DIRECTIONS:
            keys.add(f"{mode}/{move}/travel")
            for aim in DIRECTIONS:
                keys.add(f"{mode}/{move}/fire/{aim}")
    for d in DIRECTIONS:
        for kind in ("idle_fire", "stop_resume", "turn_adjacent", "turn_opposite", "speed_switch", "reload", "boundary", "collision", "boundary_fire", "collision_fire", "start_turn_fire", "aim_turn_fire"):
            keys.add(f"{kind}/{d}")
    return keys


def case_command(case_id, index, count, speeds):
    parts = case_id.split("/")
    mode = parts[0] if parts[0] in ("walk", "run") else "walk"
    kind = parts[2] if parts[0] in ("walk", "run") else parts[0]
    direction = DIRECTIONS.index(parts[1])
    aim = DIRECTIONS.index(parts[3]) if kind == "fire" else direction
    if index >= count / 2:
        if kind == "turn_adjacent": direction = (direction + 1) % 8
        if kind == "turn_opposite": direction = (direction + 4) % 8
        if kind == "speed_switch": mode = "run"
        if kind in ('start_turn_fire','aim_turn_fire'): aim=(aim+4)%8
    stopped = kind == "idle_fire" or (kind == "stop_resume" and count / 3 <= index < count * 2 / 3) or (kind=='start_turn_fire' and index<count/2)
    vector = (math.cos(direction * math.pi / 4), math.sin(direction * math.pi / 4))
    return {"speed": 0 if stopped else speeds[mode], "mode":mode, "move_sector":direction, "move": (0, 0) if stopped else vector,
            "aim": (math.cos(aim * math.pi / 4), math.sin(aim * math.pi / 4)), "aim_sector": aim,
            "blocked": kind in ("boundary", "collision", "boundary_fire", "collision_fire"),
            "fire": kind in ("fire", "idle_fire", "reload", "boundary_fire", "collision_fire", "aim_turn_fire") or (kind=='start_turn_fire' and index>=count/2), "kind": kind}


def angle_error(a, b):
    length = math.hypot(*a) * math.hypot(*b)
    if length < 1e-8:
        return 180.0
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x,y in zip(a,b)) / length))))


def score_runtime(raw):
    contract = read(CONTRACT)
    limits = contract["runtime"]
    failures, summaries = [], []
    if raw.get("input_method") != "Input.parse_input_event" or raw.get("clock") != "production_physics_delta":
        failures.append("NON_PRODUCTION_INPUT_OR_CLOCK")
    hz = raw.get("physics_hz")
    if hz not in contract["physics_hz"] or raw.get("actor_id") not in contract["actors"]:
        raise ValueError("DECLARED_ACTOR_AND_PHYSICS_RATE_REQUIRED")
    speeds = contract["actors"][raw["actor_id"]]
    seen = [case.get("id") for case in raw.get("cases", [])]
    if len(seen) != len(set(seen)) or set(seen) != expected_cases():
        failures.append("CASE_COVERAGE")
    for case in raw.get("cases", []):
        local = []
        if case.get("id") not in expected_cases():
            failures.append("UNKNOWN_CASE")
            continue
        samples = case.get("samples", [])
        if len(samples) != int(hz * limits["case_seconds"]):
            local.append("INCOMPLETE_CASE_DURATION")
        travel, expected, duration, frozen = 0.0, 0.0, 0.0, 0
        windows, move_frames = {}, set()
        last_pos = case.get("start_position", [960.0, 540.0])
        command = case_command(case["id"], 0, len(samples), speeds)
        blocked = command["blocked"]
        for index, row in enumerate(samples):
            command = case_command(case["id"], index, len(samples), speeds)
            dt = number(row["dt"], "physics dt", positive=True)
            if abs(dt * hz - 1) > 1e-5:
                local.append("WRONG_PHYSICS_DELTA")
            position = [number(v, "actual position") for v in row["world_position"]]
            delta = [b-a for a,b in zip(last_pos, position)]
            last_pos = position
            if math.dist(delta, row["delta"]) > 0.0001:
                local.append("DISPLACEMENT_LEDGER_INCONSISTENT")
            wanted = command["speed"]
            if abs(number(row["requested_speed"], "requested speed") - wanted) > 0.001:
                local.append("INPUT_SPEED_DOES_NOT_MATCH_INDEPENDENT_CONTRACT")
            if math.dist(command["move"], row["move_vector"]) > 0.0001:
                local.append("CASE_INPUT_NOT_EXERCISED")
            if angle_error(command["aim"], row["aim_vector"]) > 0.1:
                local.append("HARNESS_AIM_INPUT_NOT_DELIVERED")
            if str(row.get("active_descriptor", "")).removeprefix("res://") != str(raw.get("descriptor", "")).removeprefix("res://"):
                local.append("WRONG_ACTIVE_DESCRIPTOR")
            duration += dt
            travel += math.hypot(*delta)
            expected += wanted * dt
            window = windows.setdefault(wanted, [0.0, 0.0])
            window[0] += math.hypot(*delta)
            window[1] += wanted * dt
            if wanted == 0 and math.hypot(*delta) > 0.05:
                local.append("MOVING_DURING_STOP")
            if not row.get("runtime_active"):
                local.append("RUNTIME_INACTIVE")
            if wanted > 0 and not blocked and row.get("state") not in ("move", "run", "move_fire", "run_fire"):
                frozen += 1
            if wanted > 0:
                move_frames.add(row.get("frame"))
            if raw.get('representation_kind')=='authored_8x8' and wanted > 0 and not blocked:
                phase=number(row.get('locomotion_phase',-1),'observed gait phase')
                if not 0 <= phase < 1:
                    local.append('INVALID_OBSERVED_GAIT_PHASE')
                moving_fire=row.get('state') in ('move_fire','run_fire')
                expected_channel='/'.join((command['mode'],DIRECTIONS[command['move_sector']],
                    DIRECTIONS[command['aim_sector']],'fire' if moving_fire else 'travel'))
                if row.get('representation_channel')!=expected_channel:
                    local.append('WRONG_ACTUAL_MOVE_AIM_CHANNEL')
                if row.get('state') not in (('run','run_fire') if command['mode']=='run' else ('move','move_fire')):
                    local.append('WALK_RUN_CLIP_NOT_SEPARATE')
            # Root velocity is measured from positions, NOT actor.velocity.
            if wanted > 0 and math.hypot(*delta) > 0.0001 and not blocked:
                if angle_error(delta, command["move"]) > limits["direction_error_degrees_max"]:
                    local.append("WRONG_MOVE_AXIS")
            if command["kind"] in ("boundary", "boundary_fire") and any(abs(v - s) > 3.01 for v,s in zip(position,case.get("start_position", [960,540]))):
                local.append("BOUNDARY_PENETRATION")
        speed = travel / duration if duration else 0
        for wanted, (actual, target) in windows.items():
            if wanted > 0 and not blocked and abs(actual / target - 1) > limits["speed_relative_error_max"]:
                local.append("ACTUAL_SPEED_MISMATCH")
        if blocked:
            tail = samples[len(samples)//2:]
            stationary = any(math.hypot(*row["delta"]) < 0.01 for row in tail)
            collision = command["kind"] not in ("collision", "collision_fire") or any(row.get("slide_collisions", 0) > 0 for row in tail)
            if not stationary or not collision:
                local.append("COLLISION_OR_BOUNDARY_NOT_EXERCISED")
        if samples and frozen / len(samples) > limits["moving_fire_static_leg_fraction_max"]:
            local.append("STATIC_LEGS_WHILE_MOVING")
        if expected > 0 and not blocked and len(move_frames) < 8:
            local.append("NO_TEMPORAL_LEG_FRAME_COVERAGE")
        if command["fire"] and len(case.get("shots", [])) < 2:
            local.append("NO_SUSTAINED_FIRE")
        for shot in case.get("shots", []):
            shot_command=case_command(case['id'],shot.get('physics_sample_index',len(samples)-1),len(samples),speeds)
            if math.dist(shot["origin"], shot["socket"]) > limits["muzzle_world_error_max"]:
                local.append("SPAWN_SOCKET_MISMATCH")
            if angle_error(shot["direction"], shot_command["aim"]) > 8.0:
                local.append("SHOT_AIM_MISMATCH")
            if shot.get("shown_sector") != shot_command["aim_sector"]:
                local.append("SHOT_VISUAL_DIRECTION_MISMATCH")
            if shot.get("reloading"):
                local.append("SHOT_DURING_RELOAD")
        if case['id'].startswith('start_turn_fire/') and raw.get('representation_kind')=='authored_8x8':
            if not case.get('shots') or case['shots'][0].get('physics_sample_index')!=math.ceil(len(samples)/2):
                local.append('SIMULTANEOUS_START_AIM_FIRE_NOT_EXERCISED')
        if case["id"].startswith("reload/"):
            flags = [row.get("reloading") for row in samples]
            if not any(flags) or flags[-1]:
                local.append("RELOAD_NOT_EXERCISED_OR_NOT_FINISHED")
        summaries.append({"id": case["id"], "actual_speed": speed, "expected_speed": expected / duration if duration else 0,
                          "errors": sorted(set(local))})
        failures.extend(f"{case['id']}:{x}" for x in sorted(set(local)))
    return {"gate": "PASS_TECHNICAL_ONLY" if not failures else "FAIL", "errors": failures, "cases": summaries}


def gait_channel(seq, descriptor):
    """Resolve the consumed channel; a base travel atlas is not 8x8 evidence."""
    if descriptor and descriptor.get('representation',{}).get('kind')=='authored_8x8':
        channel=seq.get('motion_channel')
        if not isinstance(channel,dict) or set(channel)!={'mode','move','aim','firing'} or type(channel['firing']) is not bool:
            raise ValueError('EXACT_COMBINED_GAIT_CHANNEL_REQUIRED')
        if seq.get('mode')!=channel['mode'] or seq.get('direction')!=channel['aim']:
            raise ValueError('GAIT_CHANNEL_VIEW_OR_MODE_MISMATCH')
        rows=[r for r in descriptor['representation']['assets'] if all(r[k]==v for k,v in channel.items())]
        if len(rows)!=1: raise ValueError('GAIT_CHANNEL_NOT_IN_REVIEWED_RUNTIME')
        row=rows[0]
        return tuple(channel[k] for k in ('mode','move','aim','firing')),row
    return (seq['mode'],seq['direction']),None


def measured_travel_axis(geometry, ids, height):
    """Use evaluated ground-frame travel, never an IK target or declared speed.

    The anatomical frame stays forward/left/up even during strafing. Project
    excursion onto measured travel instead of relabelling left as forward.
    """
    matrices=[np.asarray(geometry['frames'][str(i)]['world_to_body_m'],dtype=float) for i in ids]
    for m in matrices:
        if (m.shape!=(4,4) or not np.isfinite(m).all() or not np.allclose(m[3],[0,0,0,1],atol=1e-6)
                or not np.allclose(m[:3,:3]@m[:3,:3].T,np.eye(3),atol=1e-5)
                or not np.isclose(np.linalg.det(m[:3,:3]),1,atol=1e-5)):
            raise ValueError('INVALID_MEASURED_ANATOMICAL_FRAME')
    bodies=[np.linalg.inv(m) for m in matrices]
    if any(not np.allclose(b[:3,:3],bodies[0][:3,:3],atol=1e-5) for b in bodies):
        raise ValueError('ANATOMICAL_FRAME_ROTATED_WITHIN_SINGLE_CHANNEL')
    if any(not np.allclose(b[:3,2],[0,0,1],atol=1e-5) or abs(b[2,3]-bodies[0][2,3])>1e-5 for b in bodies):
        raise ValueError('GROUND_FRAME_CANNOT_FOLLOW_PELVIS_BOB')
    travel=bodies[-1][:3,3]-bodies[0][:3,3]
    if np.linalg.norm(travel[:2])<height*.1:
        raise ValueError('ACTUAL_WORLD_ROOT_TRAVEL_REQUIRED_FOR_CONTACT')
    axis=matrices[0][:3,:3]@travel
    axis[2]=0
    return axis/np.linalg.norm(axis)


def validate_observations(observations, subject, descriptor_path=None):
    """Independent evaluated geometry in body coordinates; screen Y is NOT height.

    Input is annotations of decoded rendered frames plus evaluated sole vertices,
    not controller targets. Metres/seconds, x=forward, y=anatomical left, z=up.
    Both feet need measured world positions for contact sliding. Reviewers must
    inspect the corresponding images; this test cannot recognize anatomy itself.
    """
    if observations.get("subject_sha256") != subject:
        raise ValueError("STALE_OBSERVATIONS")
    if observations.get("method") != "decoded_frames_and_evaluated_skinned_vertices" or observations.get("units") != "metres_seconds_body_forward_left_up":
        raise ValueError("INDEPENDENT_3D_OBSERVATIONS_REQUIRED_NOT_IK_TARGETS_OR_SCREEN_Y")
    limits = read(CONTRACT)["gait"]
    descriptor = read(descriptor_path) if descriptor_path else None
    errors, seen = [], []
    for seq in observations.get("sequences", []):
        key,channel = gait_channel(seq,descriptor)
        seen.append(key)
        g = limits[key[0]]
        height = number(seq["body_height_m"], "body height", positive=True)
        frames = seq["frames"]
        if len(frames) < 48:
            errors.append(f"{key}:TWO_FULL_CYCLES_REQUIRED")
            continue
        times = [number(f["time_s"], "time") for f in frames]
        if any(b <= a for a, b in zip(times, times[1:])):
            errors.append(f"{key}:NON_MONOTONIC_TIME")
        geometry = read(verify_evidence_file(seq["geometry"]))
        if geometry.get("method") != "Blender_evaluated_depsgraph_vertices" or geometry.get("subject_sha256") != subject:
            raise ValueError("EVALUATED_GEOMETRY_NOT_TARGETS_REQUIRED")
        if geometry.get("exporter_sha256") != digest(ROOT / "tools/character_pipeline/export_evaluated_motion_geometry.py"):
            raise ValueError("STALE_GEOMETRY_EXPORTER")
        cycle_frames = int(number(seq["frames_per_cycle"], "cycle count", positive=True))
        if cycle_frames < 12 or len(frames) != cycle_frames * 2 + 1:
            errors.append(f"{key}:TWO_CYCLES_PLUS_WRAP_SAMPLE_REQUIRED")
        ids = [f["geometry_frame"] for f in frames]
        if len(set(ids)) != len(ids) or ids != sorted(ids):
            errors.append(f"{key}:REPEATED_OR_REORDERED_GEOMETRY_FRAMES")
        if len({f["image_sha256"] for f in frames}) < 8:
            errors.append(f"{key}:REPEATED_STATIC_RENDER")
        travel_axis=np.array([1.,0.,0.])
        if channel:
            if geometry.get('motion_channel')!=seq['motion_channel']:
                raise ValueError('COMBINED_GAIT_GEOMETRY_FOR_DIFFERENT_CHANNEL')
            travel_axis=measured_travel_axis(geometry,ids,height)
            starts=phase_starts(channel)
            period=channel['frames']/channel['fps']
            expected_times=[(i//channel['frames']+starts[i%channel['frames']])*period for i in range(len(times))]
            if cycle_frames!=channel['frames'] or any(abs(t-times[0]-expected)>1e-6 for t,expected in zip(times,expected_times)):
                errors.append(f'{key}:GAIT_TIMING_NOT_CONSUMED_CHANNEL')
        if not any(f["left_contact"] and not f["right_contact"] for f in frames) or not any(f["right_contact"] and not f["left_contact"] for f in frames):
            errors.append(f"{key}:LEFT_RIGHT_SUPPORT_EXCHANGE_MISSING")
        for frame_index,f in enumerate(frames):
            if digest(f["image"]) != f["image_sha256"] or digest(f["evaluated_mesh_evidence"]) != f["evaluated_mesh_sha256"]:
                errors.append(f"{key}:STALE_FRAME_OBSERVATION")
            if not isinstance(f["left_contact"], bool) or not isinstance(f["right_contact"], bool):
                raise ValueError("Contact flags must be independently observed booleans")
            if descriptor:
                state = seq.get("atlas_state")
                atlas_path = inside(channel['path'] if channel else descriptor["directions"][seq["direction"]][state + "_atlas"])
                count = int(channel['frames'] if channel else descriptor["states"][state]["frames"])
                index = int(f["atlas_frame"])
                if not 0 <= index < count:
                    raise ValueError("Observation frame outside runtime atlas")
                if channel and index != frame_index%count:
                    errors.append(f'{key}:GAIT_FRAME_ORDER_NOT_CONSUMED_CHANNEL')
                cell = int(descriptor["cell_size"])
                with Image.open(atlas_path) as atlas, Image.open(inside(f["image"])) as actual_image:
                    expected_image = atlas.crop((0,index*cell,cell,(index+1)*cell)).convert("RGBA")
                    if actual_image.size != (cell,cell) or actual_image.convert("RGBA").tobytes() != expected_image.tobytes():
                        errors.append(f"{key}:OBSERVED_IMAGE_NOT_RUNTIME_FRAME")
            mesh_frame = geometry["frames"][str(f["geometry_frame"])]
            if mesh_frame["image_sha256"] != f["image_sha256"] or abs(mesh_frame["time_s"] - f["time_s"]) > 1e-6:
                errors.append(f"{key}:GEOMETRY_IMAGE_TIME_MISMATCH")
            transform = np.asarray(mesh_frame["world_to_body_m"], dtype=float)
            if transform.shape != (4, 4) or not np.isfinite(transform).all():
                raise ValueError("Invalid measured body transform")
            for side in ("left", "right"):
                indices = geometry["sole_vertex_ids"][side]
                vertices = np.asarray([mesh_frame["vertices_world_m"][str(i)] for i in indices], dtype=float)
                actual = vertices.mean(axis=0)
                body = (transform @ np.append(actual, 1))[:3]
                if not np.isfinite(vertices).all() or math.dist(actual, f[side+"_sole_world_m"]) > 1e-5 or math.dist(body, f[side+"_sole_body_m"]) > 1e-5:
                    errors.append(f"{key}:{side}:SOLE_NOT_FROM_EVALUATED_VERTICES")
        flight = sum(not f["left_contact"] and not f["right_contact"] for f in frames) / len(frames)
        if not g["flight_fraction_min"] <= flight <= g["flight_fraction_max"]:
            errors.append(f"{key}:FLIGHT_FRACTION")
        for side in ("left", "right"):
            positions = [[number(v, "sole vertex") for v in f[side + "_sole_body_m"]] for f in frames]
            excursion=[float(np.dot(p,travel_axis)) for p in positions]
            stride = (max(excursion) - min(excursion)) / height
            lift = max(p[2] for p in positions) / height
            if not g["stride_over_height_min"] <= stride <= g["stride_over_height_max"]:
                errors.append(f"{key}:{side}:STRIDE")
            if not g["lift_over_height_min"] <= lift <= g["lift_over_height_max"]:
                errors.append(f"{key}:{side}:LIFT")
            anchor, previous, accumulated = None, None, 0.0
            contacts = [f[side+"_contact"] for f in frames]
            transitions = sum(not a and b for a,b in zip(contacts,contacts[1:]))
            if transitions < 2:
                errors.append(f"{key}:{side}:CONTACT_ALTERNATION_MISSING")
            for f in frames:
                if not f[side + "_contact"]:
                    anchor, previous, accumulated = None, None, 0.0
                    continue
                actual = f[side + "_sole_world_m"]
                if anchor is None:
                    anchor = actual
                if previous is not None:
                    accumulated += math.dist(actual, previous)
                previous = actual
                if max(math.dist(anchor, actual), accumulated) / height > limits["contact_slip_over_height_max"]:
                    errors.append(f"{key}:{side}:CONTACT_SLIP")
            for f in frames:
                width = number(f[side + "_calf_width_ratio"], "calf width ratio", positive=True)
                if not limits["calf_width_ratio_min"] <= width <= limits["calf_width_ratio_max"]:
                    errors.append(f"{key}:{side}:CALF_VOLUME")
                if abs(number(f[side + "_ankle_reference_error_degrees"], "ankle")) > limits["ankle_reference_error_degrees_max"]:
                    errors.append(f"{key}:{side}:ANKLE")
                if abs(number(f[side + "_toe_heading_error_degrees"], "toe heading")) > limits["toe_heading_error_degrees_max"]:
                    errors.append(f"{key}:{side}:TOE_HEADING")
        for f in frames:
            if f["left_sole_body_m"][1] < f["right_sole_body_m"][1] - limits["lateral_lane_cross_over_height_max"] * height:
                errors.append(f"{key}:ANATOMICAL_LANE_CROSS")
        z = [number(f["pelvis_world_z_m"], "pelvis") for f in frames]
        if (max(z) - min(z)) / height > limits["torso_bob_over_height_max"]:
            errors.append(f"{key}:BODY_BOB")
        seam = max(math.dist(frames[i][side+"_sole_body_m"], frames[i+cycle_frames][side+"_sole_body_m"])
                   for side in ("left","right") for i in range(min(cycle_frames+1,len(frames)-cycle_frames)))
        if seam / height > limits["cycle_seam_over_height_max"]:
            errors.append(f"{key}:CYCLE_SEAM")
    if descriptor and descriptor.get('representation',{}).get('kind')=='authored_8x8':
        required={(m,d,a,f) for m in ('walk','run') for d in DIRECTIONS for a in DIRECTIONS for f in (False,True)}
    else:
        required = {(m, d) for m in ("walk", "run") for d in DIRECTIONS}
    if set(seen) != required or len(seen) != len(required):
        errors.append("GAIT_OBSERVATION_COVERAGE")
    return sorted(set(errors))


def verify_evidence_file(ref):
    p = inside(ref["path"])
    if digest(p) != ref["sha256"]:
        raise ValueError(f"STALE_EVIDENCE:{rel(p)}")
    return p


def validate_visible_muzzles(muzzle, d, evidence):
    """Observe the actual consumed atlas, including every move/aim channel.

    Base direction sockets cannot stand in for a different moving-fire image.
    Decode each atlas once, retaining only that atlas while checking its cells.
    """
    expected={}
    for di in DIRECTIONS:
        for state in state_names(d):
            for frame in range(d['states'][state]['frames']):
                expected[('base',di,state,frame)]=(d['directions'][di][state+'_atlas'],
                    d['cell_size'],d['directions'][di][state+'_muzzle_xy'][frame])
    combined=d.get('representation',{}).get('kind')=='authored_8x8'
    if combined:
        for clip in d['representation']['assets']:
            for frame in range(clip['frames']):
                expected[('combined',clip['mode'],clip['move'],clip['aim'],clip['firing'],frame)]=(
                    clip['path'],clip['cell_size'],clip['muzzle_xy'][frame])
    rows=[(('base',r['direction'],r['state'],r['frame']),r) for r in muzzle.get('frames',[])]
    rows.extend((('combined',r['mode'],r['move'],r['aim'],r['firing'],r['frame']),r)
                for r in muzzle.get('combined_frames',[]))
    seen=set(); grouped={}
    for key,row in rows:
        if key in seen or key not in expected:
            raise ValueError('INVALID_MUZZLE_FRAME_COVERAGE')
        seen.add(key)
        path,cell,socket=expected[key]
        grouped.setdefault(path,[]).append((key,row,int(cell),socket))
    if seen != set(expected):
        raise ValueError('INCOMPLETE_VISIBLE_MUZZLE_REVIEW')
    for path,records in grouped.items():
        with Image.open(inside(path)) as atlas:
            for key,row,cell,socket in records:
                frame=key[-1]
                pixels=atlas.crop((0,frame*cell,cell,(frame+1)*cell)).convert('RGBA').tobytes()
                if row.get('atlas_frame_rgba_sha256')!=hashlib.sha256(pixels).hexdigest():
                    raise ValueError('VISIBLE_MUZZLE_ANNOTATION_FOR_DIFFERENT_FRAME')
                if math.dist(socket,row['visible_tip_xy'])>2.0:
                    raise ValueError(f'VISIBLE_MUZZLE_MISMATCH:{key}')
                if abs(number(row['barrel_to_shot_error_degrees'],'barrel axis'))>8.0:
                    raise ValueError(f'BARREL_AXIS_MISMATCH:{key}')
                evidence(row['evidence'])


def validate_geometry_generation(geometry, direction, descriptor, motion_channel=None):
    """Connect actual render geometry to its exact reviewed direction/scene."""
    import generation_harness as generation
    build = read(inside(descriptor).parent / 'MOTION_BUILD_INPUTS.json')
    if geometry.get('qa_fixture_only') is not False:
        raise ValueError('GEOMETRY_SYNTHETIC_OR_UNDECLARED_PRODUCTION_STATUS')
    approval_ref = geometry.get('generation_receipt')
    approved = [generation.ref(p) for p in build.get('roles', {}).get('generation_receipt', [])]
    if not approval_ref or approval_ref not in approved:
        raise ValueError('GEOMETRY_NOT_FROM_APPROVED_GENERATION_RECEIPT')
    approval = generation.verify_receipt(generation.resolve(approval_ref), stage='first_pose')
    config_path = verify_evidence_file(geometry['config'])
    config = read(config_path)
    if motion_channel is not None and (geometry.get('motion_channel')!=motion_channel or config.get('motion_channel')!=motion_channel):
        raise ValueError('GEOMETRY_CONFIG_MOTION_CHANNEL_MISMATCH')
    if (geometry.get('direction') != direction or config.get('direction') != direction or
            direction not in approval['approved_scope']):
        raise ValueError('GEOMETRY_GENERATION_DIRECTION_MISMATCH')
    if (geometry.get('blend_sha256') != approval['blend']['sha256'] or
            geometry.get('config_sha256') != digest(config_path) or
            config.get('qa_fixture_only', False) is not False or
            generation.ref(config['generation_receipt']) != approval_ref):
        raise ValueError('GEOMETRY_GENERATION_SCENE_OR_CONFIG_MISMATCH')
    generation.authorize_animation(config, generation.resolve(approval['blend']))
    for key in ('skinned_mesh','body_coordinate_frame','sole_vertex_ids','subject_sha256'):
        if geometry.get(key) != config.get(key):
            raise ValueError('GEOMETRY_CONFIG_BINDING_MISMATCH:' + key)
    render = read(verify_evidence_file(geometry['render_receipt']))
    pose=read(verify_evidence_file(approval['pose_bundle']))
    collected=read(verify_evidence_file(pose['mesh_preflight']))
    if geometry.get('scene_unit_scale',1)!=collected['scene']['unit_scale'] or config.get('scene_unit_scale',1)!=collected['scene']['unit_scale']:
        raise ValueError('GEOMETRY_UNITS_NOT_ACTUAL_REVIEWED_SCENE')
    if render.get('camera_space','world_locked')!=config.get('camera_space','world_locked'):
        raise ValueError('CAPTURE_SPACE_NOT_REVIEWED_CONFIG')
    if render.get('camera_space')=='root_translation_locked':
        if render.get('approved_camera')!=collected['scene']['camera'] or render.get('approved_ground_frame')!=collected['body_frame_matrix']:
            raise ValueError('CAPTURE_ANCHOR_NOT_APPROVED_FIRST_POSE')
    for key in ('qa_fixture_only','generation_receipt','direction','config','skinned_mesh','body_coordinate_frame','motion_channel','scene_unit_scale'):
        if render.get(key) != geometry.get(key):
            raise ValueError('RENDER_GENERATION_BINDING_MISMATCH:' + key)
    if len(config['frames']) != len(geometry['frames']):
        raise ValueError('GEOMETRY_CONFIG_FRAME_COVERAGE')
    for row in config['frames']:
        frame = str(row['frame'])
        actual = geometry['frames'][frame]
        rendered = render['frames'][frame]
        if (actual['time_s'] != row['time_s'] or
                rendered['runtime'] != generation.ref(row['image']) or
                rendered['native'] != generation.ref(row['master_image'])):
            raise ValueError('GEOMETRY_CONFIG_FRAME_BINDING_MISMATCH')
    return config_path


def check_bundle(bundle, *, require_reviews=True):
    """Recompute all technical results; never trust a caller's generic PASS field."""
    descriptor = inside(bundle["descriptor"])
    report = audit(descriptor)
    if report["errors"]:
        raise ValueError("STATIC_AUDIT_FAILED:" + ";".join(report["errors"][:12]))
    snap = snapshot(descriptor)
    subject = snap["subject_sha256"]
    if bundle.get("subject_sha256") != subject:
        raise ValueError("STALE_BUNDLE_SUBJECT")
    if build_closure_errors(descriptor.parent / "MOTION_BUILD_INPUTS.json") or representation_errors(read(descriptor)):
        raise ValueError("BUILD_PROVENANCE_OR_MOVE_AIM_POLICY_MISSING")
    contract = read(CONTRACT)
    rates, by_case = [], {}
    evidence_files = {}
    def evidence(ref):
        p = verify_evidence_file(ref)
        evidence_files[rel(p)] = digest(p)
        return p
    for ref in bundle.get("runtime_reports", []):
        raw = read(evidence(ref))
        validate_runtime_subject(raw, subject, descriptor)
        scored = score_runtime(raw)
        if scored["errors"]:
            raise ValueError("RUNTIME_FAILED:" + ";".join(scored["errors"][:12]))
        rates.append(raw["physics_hz"])
        for case in scored["cases"]:
            by_case.setdefault(case["id"], []).append(case["actual_speed"])
    if sorted(rates) != contract["physics_hz"]:
        raise ValueError("30_60_120_HZ_COVERAGE_REQUIRED")
    for key, speeds in by_case.items():
        if max(speeds) > 1 and (max(speeds) - min(speeds)) / max(speeds) > contract["runtime"]["frame_rate_relative_difference_max"]:
            raise ValueError(f"FRAME_RATE_DEPENDENCE:{key}")
    obs = read(evidence(bundle["observations"]))
    errors = validate_observations(obs, subject, descriptor)
    if errors:
        raise ValueError("GAIT_OBSERVATIONS_FAILED:" + ";".join(errors[:12]))
    for seq in obs["sequences"]:
        geometry = read(verify_evidence_file(seq["geometry"]))
        config_path = validate_geometry_generation(geometry, seq['direction'], descriptor,seq.get('motion_channel'))
        evidence_files[rel(config_path)] = digest(config_path)
        validate_render_binding(geometry, subject)
    # Every direction/state/frame needs a separately observed visible barrel tip.
    muzzle = read(evidence(bundle["visible_muzzles"]))
    if muzzle.get("subject_sha256") != subject or muzzle.get("method") != "human_decoded_frame_barrel_tip_and_axis":
        raise ValueError("VISIBLE_MUZZLE_REVIEW_REQUIRED")
    d = read(descriptor)
    validate_visible_muzzles(muzzle,d,evidence)
    # HTML must be an engine export of the same code/assets, or actually run the
    # same behavioral matrix. An atlas-copy manifest or source grep is not parity.
    parity = read(evidence(bundle["html_parity"]))
    if parity.get("subject_sha256") != subject or parity.get("method") != "browser_input_runtime_matrix" or parity.get("case_ids") != sorted(expected_cases()):
        raise ValueError("DYNAMIC_HTML_PARITY_REQUIRED")
    browser_raw = read(evidence(parity["runtime_report"]))
    validate_runtime_subject(browser_raw, subject, descriptor)
    if browser_raw.get("headless") is not False:
        raise ValueError("NON_BROWSER_RUNTIME")
    browser_scored = score_runtime(browser_raw)
    if browser_scored["errors"]:
        raise ValueError("BROWSER_RUNTIME_MATRIX_FAILED")
    evidence(parity["html"])
    capture = read(evidence(parity["capture_1080p_validation"]))
    if capture.get("gate") != "PASS" or capture.get("dynamic_capture_gate") != "PASS" or not capture.get("dynamic_capture_required") or not parity.get("native_capture", False):
        raise ValueError("NATIVE_DYNAMIC_1080P_EVIDENCE_REQUIRED")
    capture_path = evidence(parity["capture"])
    # Decode the exact submitted video again, not a detached historical PASS.
    import importlib.util
    module_spec = importlib.util.spec_from_file_location("motion_1080p", ROOT / "tools/art_pipeline/validate_visual_evidence_1080p.py")
    validator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(validator)
    video_check = validator.inspect_video(capture_path)
    if not video_check["decodable"] or not video_check["native_1080p_container"]:
        raise ValueError("CAPTURE_DECODE_OR_RESOLUTION_FAILED")
    capture_records = capture.get("evidence", [])
    if not any(str(r.get("path", "")).replace("\\", "/") in (str(capture_path).replace("\\", "/"), rel(capture_path)) and r.get("sha256") == digest(capture_path) for r in capture_records):
        raise ValueError("1080P_VALIDATOR_FOR_DIFFERENT_CAPTURE")
    reviewed_evidence_sha256 = canonical(evidence_files)
    if not require_reviews:
        return {"schema": 1, "gate": "HOLD_FOR_INDEPENDENT_REVIEWS", "subject_sha256": subject,
                "reviewed_evidence_sha256": reviewed_evidence_sha256, "required_roles": contract["review_roles"],
                "snapshot": snap, "evidence_files": evidence_files}
    roles = []
    for review in bundle.get("reviews", []):
        roles.append(review["role"])
        if review.get("subject_sha256") != subject or review.get("verdict") != "PASS":
            raise ValueError("REVIEW_NOT_PASS_OR_STALE")
        if review.get("reviewed_evidence_sha256") != reviewed_evidence_sha256:
            raise ValueError("REVIEW_FOR_DIFFERENT_EVIDENCE_SET")
        if set(review.get("directions", [])) != set(DIRECTIONS) or set(review.get("checks", [])) != set(contract["required_visual_checks"]):
            raise ValueError("INCOMPLETE_TEMPORAL_VISUAL_REVIEW")
        if not review.get("reviewer") or not review.get("reviewed_utc"):
            raise ValueError("UNATTRIBUTED_REVIEW")
        if review["role"] == "ChatGPT web" and review.get("conversation") != contract["web_review_conversation"]:
            raise ValueError("WRONG_WEB_REVIEW_CONVERSATION")
        evidence(review["reply_evidence"])
    if sorted(roles) != sorted(contract["review_roles"]):
        raise ValueError("ALL_INDEPENDENT_REVIEW_ROLES_REQUIRED")
    return {"schema": 1, "gate": "PASS_ALL_REQUIRED_GATES", "subject_sha256": subject,
            "snapshot": snap, "evidence_files": evidence_files, "reviewed_evidence_sha256": reviewed_evidence_sha256, "verified_utc": now()}


def presentation_is_moving(distance, dt):
    """Independent acceptance rule for visual gait, not altered root evidence."""
    if number(dt,'actual sample seconds')<=0:
        raise ValueError('POSITIVE_RUNTIME_SAMPLE_DT_REQUIRED')
    return number(distance,'actual distance')/dt > read(CONTRACT)['runtime']['presentation_stop_speed_pixels_per_second']


def validate_runtime_subject(raw, subject, descriptor):
    d = read(descriptor)
    if raw.get("subject_sha256") != subject or raw.get("actor_id") != d["actor_id"] or inside(raw.get("descriptor", "")) != inside(descriptor):
        raise ValueError("WRONG_RUNTIME_SUBJECT_ACTOR_OR_DESCRIPTOR")
    representation=d.get('representation',{})
    if representation and raw.get('representation_kind')!=representation.get('kind'):
        raise ValueError('RUNTIME_DID_NOT_CONSUME_DECLARED_REPRESENTATION')
    if representation.get('kind')=='authored_8x8':
        channels={'/'.join((r['mode'],r['move'],r['aim'],'fire' if r['firing'] else 'travel')):r
                  for r in representation['assets']}
        timings={mode:next(r for r in channels.values() if r['mode']==mode) for mode in ('walk','run')}
        speeds=read(CONTRACT)['actors'][d['actor_id']]
        decoded={}
        for case in raw['cases']:
            phase=number(case.get('start_locomotion_phase',-1),'initial actual phase')
            if not 0 <= phase < 1: raise ValueError('INITIAL_GAIT_PHASE_REQUIRED')
            position=case['start_position']
            for index,sample in enumerate(case['samples']):
                command=case_command(case['id'],index,len(case['samples']),speeds)
                distance=math.dist(position,sample['world_position'])
                position=sample['world_position']
                timing=timings[command['mode']]
                moving=presentation_is_moving(distance,sample['dt'])
                expected=(phase+(distance/(speeds[command['mode']]*timing['frames']/timing['fps']) if moving else 0))%1
                actual=number(sample.get('locomotion_phase',-1),'actual phase')
                if not 0 <= actual < 1 or abs((actual-expected+.5)%1-.5)>1e-5:
                    raise ValueError('GAIT_PHASE_NOT_ACTUAL_DISTANCE_OR_RESET_DURING_FIRE')
                phase=actual
                channel=sample.get('representation_channel','')
                if bool(channel)!=moving:
                    raise ValueError('GAIT_CHANNEL_DISAGREES_WITH_ACTUAL_STOP_DEADBAND')
                if channel:
                    allowed_frames={phase_frame(timing,phase+eps) for eps in (-1e-6,0,1e-6)}
                    if sample['frame'] not in allowed_frames:
                        raise ValueError('SHOWN_GAIT_FRAME_NOT_PHASE')
            for shot in case.get('shots',[]):
                index=shot.get('physics_sample_index',-1)
                if not 0 <= index < len(case['samples']):
                    raise ValueError('SHOT_PHYSICS_SAMPLE_REQUIRED')
                sample=case['samples'][index]
                command=case_command(case['id'],index,len(case['samples']),speeds)
                previous=case['start_position'] if index==0 else case['samples'][index-1]['world_position']
                moving=presentation_is_moving(math.dist(previous,sample['world_position']),sample['dt'])
                if moving:
                    displacement=[b-a for a,b in zip(previous,sample['world_position'])]
                    sector=int(math.floor((math.atan2(displacement[1],displacement[0])+math.pi/8)/(math.pi/4)))%8
                    expected_channel='/'.join((command['mode'],DIRECTIONS[sector],DIRECTIONS[command['aim_sector']],'fire'))
                    expected_state='run_fire' if command['mode']=='run' else 'move_fire'
                else:
                    expected_channel='';expected_state='fire'
                if shot.get('representation_channel')!=expected_channel or shot.get('state')!=expected_state:
                    raise ValueError('ACTUAL_SHOT_DID_NOT_DISPLAY_REQUIRED_FIRE_CHANNEL')
                if (shot.get('representation_channel')!=sample.get('representation_channel') or
                    shot['frame']!=sample['frame'] or shot.get('locomotion_phase')!=sample.get('locomotion_phase')):
                    raise ValueError('SHOT_AND_DISPLAY_DIFFERENT_PHYSICS_FRAME')
            for sample in case['samples']+case.get('shots',[]):
                channel=sample.get('representation_channel','')
                if channel:
                    row=channels.get(channel)
                    if not row or inside(sample.get('representation_atlas',''))!=inside(row['path']) or not 0 <= sample['frame'] < row['frames']:
                        raise ValueError('RUNTIME_USED_UNREVIEWED_CHANNEL_ATLAS_OR_FRAME')
                    atlas_path=inside(row['path']);cell=int(row['cell_size'])
                else:
                    direction=DIRECTIONS[sample.get('sector',sample.get('shown_sector',-1))]
                    atlas_path=inside(d['directions'][direction][sample['state']+'_atlas']);cell=int(d['cell_size'])
                if raw.get('sprite_pixel_probe') is True:
                    if d.get('qa_fixture_only') is not True:
                        raise ValueError('SYNTHETIC_PIXEL_PROBE_CANNOT_APPROVE_CHARACTER')
                    if atlas_path not in decoded:
                        with Image.open(atlas_path) as atlas:
                            decoded[atlas_path]=[hashlib.sha256(atlas.crop((0,f*cell,cell,(f+1)*cell)).convert('RGBA').tobytes()).hexdigest()
                                for f in range(atlas.height//cell)]
                    if (sample.get('sprite_region')!=[0,sample['frame']*cell,cell,cell] or
                        sample.get('shown_frame_rgba_sha256')!=decoded[atlas_path][sample['frame']]):
                        raise ValueError('ACTUAL_SPRITE_PIXELS_NOT_SELECTED_CHANNEL_FRAME')
                    if (sample.get('visible_marker_count')!=1 or sample.get('sprite_visible') is not True or
                        sample.get('sprite_alpha')!=1 or sample.get('sprite_centered') is not True or sample.get('sprite_flip')!=[False,False]):
                        raise ValueError('ACTUAL_SPRITE_HIDDEN_FLIPPED_OR_AMBIGUOUS_MARKER')
                    if 'origin' in sample and math.dist(sample['origin'],sample.get('actual_marker_world',[]))>.05:
                        raise ValueError('SHOT_ORIGIN_NOT_ACTUAL_SPRITE_MARKER_WORLD_POSITION')


def validate_render_binding(geometry, subject):
    receipt = read(verify_evidence_file(geometry["render_receipt"]))
    if receipt.get("method") != "same_process_render_and_evaluated_vertices" or receipt.get("subject_sha256") != subject or receipt.get("blend_sha256") != geometry.get("blend_sha256") or receipt.get("generator_sha256") != geometry.get("exporter_sha256"):
        raise ValueError("UNBOUND_RENDER_AND_GEOMETRY")
    if set(receipt.get("frames", {})) != set(geometry["frames"]):
        raise ValueError("RENDER_GEOMETRY_FRAME_COVERAGE")
    for key, frame in geometry["frames"].items():
        render = receipt["frames"][key]
        if receipt.get('camera_space')=='root_translation_locked':
            import root_locked_capture
            if verify_evidence_file(receipt['capture_validator'])!=Path(root_locked_capture.__file__).resolve():
                raise ValueError('WRONG_CAPTURE_COORDINATE_VALIDATOR')
            root_locked_capture.verify(receipt['approved_camera'],render['actual_camera'],
                                       receipt['approved_ground_frame'],render['actual_ground_frame'])
            # Compare measured render ground frame with the geometry transform,
            # converting translations through the scene's reviewed unit scale.
            config=read(verify_evidence_file(geometry['config']))
            unit_scale=number(config.get('scene_unit_scale',1),'scene unit scale',positive=True)
            ground=np.asarray(render['actual_ground_frame'],dtype=float).copy();ground[:3,3]*=unit_scale
            if not np.allclose(np.linalg.inv(ground),frame['world_to_body_m'],atol=1e-5):
                raise ValueError('RENDER_GROUND_NOT_GEOMETRY_BODY_FRAME')
        if render.get("geometry_frame_sha256") != hashlib.sha256(json.dumps(frame,sort_keys=True).encode()).hexdigest() or not render.get("actions"):
            raise ValueError("RENDERED_DIFFERENT_POSE_OR_NO_ACTION")
        if digest(verify_evidence_file(render["runtime"])) != frame["image_sha256"]:
            raise ValueError("RENDERED_DIFFERENT_IMAGE")
        with Image.open(verify_evidence_file(render["native"])) as image:
            if list(image.size) != render["native_resolution"] or image.width < 1920 or image.height < 1080:
                raise ValueError("NON_NATIVE_RENDER_MASTER")


def require_seal(receipt_path, descriptor_path=None):
    if not receipt_path:
        raise ValueError("PROMOTION_BLOCKED: --receipt from motion_harness seal is required; build a candidate first")
    receipt = read(receipt_path)
    bundle_path = verify_evidence_file(receipt["bundle"])
    result = check_bundle(read(bundle_path))
    if receipt.get("subject_sha256") != result["subject_sha256"] or receipt.get("gate") != result["gate"]:
        raise ValueError("STALE_OR_INVALID_PROMOTION_RECEIPT")
    if descriptor_path and inside(descriptor_path) != inside(result["snapshot"]["descriptor"]):
        raise ValueError("RECEIPT_FOR_DIFFERENT_DESCRIPTOR")
    return result


def quarantine(path, reason):
    """Recoverable relocation only, with a complete pre-move inventory."""
    path = inside(path)
    base = inside("artifacts/quarantine/retained", exists=False)
    if path == base or base.is_relative_to(path):
        raise ValueError("Unsafe quarantine target")
    target = base / (path.name + "_" + uuid.uuid4().hex)
    inventory = {rel(p): digest(p) for p in path.rglob("*") if p.is_file()}
    if any(p.is_symlink() for p in path.rglob("*")):
        raise ValueError("Refusing to relocate a linked tree")
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"source": rel(path), "target": rel(target), "reason": reason, "status": "QUARANTINE_NOT_DISPOSED", "files": inventory, "created_utc": now()}
    write(target.with_suffix(".inventory.json"), record)
    path.replace(target)
    return target


def run_engine(descriptor_path, godot, out, rates=None):
    """Sequential bounded children, no render workers/daemon or global process kill."""
    out = inside(out, exists=False)
    if out.exists():
        raise ValueError("Use a fresh --out directory; retained QA may not be overwritten")
    snap = snapshot(descriptor_path)
    out.mkdir(parents=True)
    write(out / "input_snapshot.json", snap)
    contract = read(CONTRACT)
    reports = []
    for hz in rates or contract["physics_hz"]:
        raw_path = out / f"runtime_{hz}hz.json"
        work = out / f"process_{hz}hz"
        work.mkdir()
        env = os.environ.copy()
        for key in ("TEMP", "TMP", "TMPDIR", "XDG_CACHE_HOME", "XDG_DATA_HOME", "APPDATA", "LOCALAPPDATA"):
            env[key] = str(work)
        env.pop("SABLE_RUNTIME_CAPTURE_MODE", None)
        env.update(SABLE_HARNESS_DESCRIPTOR="res://" + rel(descriptor_path),
                   SABLE_HARNESS_OUTPUT="res://" + rel(raw_path),
                   SABLE_HARNESS_SUBJECT=snap["subject_sha256"], SABLE_HARNESS_HZ=str(hz))
        command = [str(godot), "--headless", "--path", str(ROOT), "--fixed-fps", str(hz),
                   "--audio-driver", "Dummy", "--log-file", str(work / "godot.log"),
                   "--script", "res://tests/render/character_motion_harness.gd"]
        with (work / "stdout.log").open("w", encoding="utf-8") as log:
            with subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0) as process:
                try:
                    code = process.wait(timeout=contract["runtime"]["timeout_seconds_per_process"])
                except BaseException:
                    process.kill()  # Only the exact owned child, never by process name.
                    process.wait(timeout=10)
                    raise
        if code or not raw_path.is_file():
            raise ValueError(f"Godot harness failed ({code}); inspect {rel(work / 'stdout.log')}")
        raw=read(raw_path)
        validate_runtime_subject(raw,snap['subject_sha256'],descriptor_path)
        result = score_runtime(raw)
        result.update(physics_hz=hz, raw_evidence={"path": rel(raw_path), "sha256": digest(raw_path)})
        write(out / f"score_{hz}hz.json", result)
        reports.append({"hz": hz, "gate": result["gate"], "failures": len(result["errors"])})
    if snapshot(descriptor_path)["subject_sha256"] != snap["subject_sha256"]:
        raise ValueError("INPUT_CHANGED_DURING_RUNTIME_TEST")
    summary = {"schema": 1, "scope": "technical_runtime_not_visual_approval", "subject_sha256": snap["subject_sha256"], "reports": reports,
               "gate": "FAIL" if any(r["gate"] == "FAIL" for r in reports) else "PASS_TECHNICAL_ONLY", "owned_children_exited": True}
    write(out / "runtime_summary.json", summary)
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("audit")
    a.add_argument("--descriptor", required=True)
    a.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--descriptor", required=True)
    r.add_argument("--godot", required=True, type=Path)
    r.add_argument("--out", required=True)
    r.add_argument("--hz", type=int, choices=(30, 60, 120), help="Diagnostic subset only; cannot seal")
    s = sub.add_parser("seal")
    s.add_argument("--bundle", required=True)
    s.add_argument("--out", required=True)
    pack = sub.add_parser("review-pack")
    pack.add_argument("--bundle", required=True)
    pack.add_argument("--out", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--receipt", required=True)
    args = p.parse_args()
    try:
        if args.command == "audit":
            result = audit(args.descriptor)
            write(args.out, result)
        elif args.command == "run":
            result = run_engine(args.descriptor, args.godot, args.out, [args.hz] if args.hz else None)
        elif args.command in ("seal", "review-pack"):
            result = check_bundle(read(args.bundle), require_reviews=args.command == "seal")
            result["bundle"] = {"path": rel(args.bundle), "sha256": digest(args.bundle)}
            write(args.out, result)
        else:
            result = require_seal(args.receipt)
        print(json.dumps({k: v for k, v in result.items() if k in ("gate", "scope", "reports", "subject_sha256", "owned_children_exited")}, ensure_ascii=False))
        return 1 if result["gate"] == "FAIL" or result["gate"].startswith("HOLD") else 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.TimeoutExpired) as exc:
        print(f"MOTION_HARNESS_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
