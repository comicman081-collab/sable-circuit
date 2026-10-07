#!/usr/bin/env python3
"""Build an isolated MICA R21 frame-transition sole-lock runtime candidate.

R20 applied one shared velocity multiplier to every rendered move sample.  It
did not account for the 0.34 runtime display scale, so the gameplay root
travelled about 2.8 times farther than the authored R8C sole progression.

R21 copies the already-reviewed R8C raster atlases without repainting them and
converts the existing Blender+UAL sole-lock tracks into runtime-world,
per-direction frame positions.  The engine consumes those positions only when
the visible authored frame changes; repeated 60 Hz samples of the same 24 fps
raster remain rooted rather than sliding the sole across the stage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
UNITS = {
    "E": (1.0, 0.0),
    "SE": (2 ** -0.5, 2 ** -0.5),
    "S": (0.0, 1.0),
    "SW": (-2 ** -0.5, 2 ** -0.5),
    "W": (-1.0, 0.0),
    "NW": (-2 ** -0.5, -2 ** -0.5),
    "N": (0.0, -1.0),
    "NE": (2 ** -0.5, -2 ** -0.5),
}

R20_RUNTIME = Path(
    "art_src/characters/mica/fast_pipeline/motion/"
    "candidate_mica_c03_r20_r8c_gait_speed"
)
ROOT_TRACKS = {
    "E": Path(
        "artifacts/mica_c03_v8_r14_e_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_E_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "SE": Path(
        "artifacts/mica_c03_v8_r14_se_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_SE_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "S": Path(
        "artifacts/mica_c03_v8_r14_s_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_S_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "SW": Path(
        "artifacts/mica_c03_v8_r14_sw_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_SW_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "W": Path(
        "artifacts/mica_c03_v8_r14_w_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_W_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "NW": Path(
        "artifacts/mica_c03_v8_r14_nw_shared_handoff_r8_review/"
        "MICA_C03_V8_R14_NW_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "N": Path(
        "artifacts/mica_c03_v8_r14_n_shared_handoff_r8c_review/"
        "MICA_C03_V8_R14_N_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
    "NE": Path(
        "artifacts/mica_c03_v8_r14_ne_shared_handoff_r8_review/"
        "MICA_C03_V8_R14_NE_SHARED_R8C_SUBPIXEL_RUNTIME_ROOT_TRACK.json"
    ),
}


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside the project: {path}") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"invalid {label}: {path}")
    return value


def along(point: list[float], direction: str) -> float:
    unit = UNITS[direction]
    return float(point[0]) * unit[0] + float(point[1]) * unit[1]


def build_track(path: Path, direction: str, display_scale: float) -> dict:
    source = read_json(path, f"{direction} R8C root track")
    if source.get("direction") != direction:
        raise SystemExit(f"root-track direction mismatch: {path}")
    if source.get("trajectory_mode") != "runtime_continuous_sole_lock":
        raise SystemExit(f"root track is not an authored sole-lock track: {path}")
    frames = source.get("frames")
    if not isinstance(frames, list) or len(frames) < 25:
        raise SystemExit(f"root track does not contain one complete cycle + wrap: {path}")
    first = along(frames[0]["root_xy_px"], direction)
    positions = [round((along(frame["root_xy_px"], direction) - first) * display_scale, 9) for frame in frames[:24]]
    cycle_advance = round((along(frames[24]["root_xy_px"], direction) - first) * display_scale, 9)
    deltas = [positions[index] - positions[index - 1] for index in range(1, 24)]
    deltas.append(cycle_advance - positions[-1] + positions[0])
    if min(deltas) <= 0.0:
        raise SystemExit(f"{direction} sole-lock track has a non-positive visible-frame transition: {deltas}")
    drift = source.get("support_sole_axis_drift_px", {})
    if not isinstance(drift, dict) or max(float(drift.get("left", 999.0)), float(drift.get("right", 999.0))) > 1.0:
        raise SystemExit(f"{direction} source root track exceeds its sole-lock band: {drift}")
    return {
        "space": "runtime_world_along_move_axis",
        "frame_positions": positions,
        "cycle_advance": cycle_advance,
        "frame_transition_min": round(min(deltas), 9),
        "frame_transition_max": round(max(deltas), 9),
        "source_track": path.relative_to(ROOT).as_posix(),
        "source_track_sha256": sha256(path),
        "source_support_sole_axis_drift_px": drift,
        "display_scale_applied": display_scale,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-runtime", type=Path, default=R20_RUNTIME)
    parser.add_argument("--candidate-name", default="r21_r8c_frame_transition_sole_lock")
    args = parser.parse_args()

    output = project_path(args.output, "output")
    source_runtime = project_path(args.source_runtime, "source runtime")
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing candidate: {output}")
    descriptor_source = source_runtime / "runtime_descriptor.json"
    descriptor = read_json(descriptor_source, "source descriptor")
    if descriptor.get("schema") != 2 or set(descriptor.get("directions", {})) != set(DIRECTIONS):
        raise SystemExit("source runtime must be a complete MICA schema-2 candidate")
    display_scale = float(descriptor.get("display_scale", 0.0))
    if not 0.0 < display_scale <= 1.0:
        raise SystemExit("source descriptor has an invalid display scale")

    output.mkdir(parents=True)
    for direction in DIRECTIONS:
        source_direction = source_runtime / direction
        target_direction = output / direction
        target_direction.mkdir()
        for state in ("idle", "move", "fire"):
            source = source_direction / f"{state}.png"
            target = target_direction / f"{state}.png"
            if not source.is_file():
                raise SystemExit(f"missing R20 {direction}/{state}: {source}")
            shutil.copy2(source, target)
            if sha256(source) != sha256(target):
                raise SystemExit(f"copy integrity failure: {target}")

    track_by_direction = {
        direction: build_track(project_path(ROOT_TRACKS[direction], f"{direction} root track"), direction, display_scale)
        for direction in DIRECTIONS
    }
    candidate_descriptor = json.loads(json.dumps(descriptor))
    candidate_descriptor["candidate"] = args.candidate_name
    candidate_descriptor["move_root_sync"] = {
        "enabled": True,
        "mode": "frame_transition_sole_lock",
        "frame_count": 24,
        "track_space": "runtime_world_along_move_axis",
        "rationale": (
            "R21 derives one direction-specific world root path from the R8C Blender+UAL "
            "support-sole tracks after applying the descriptor display scale. Root displacement "
            "is emitted only at an authored visual-frame transition; repeated high-rate samples "
            "of the same raster cell remain planted."
        ),
        "directional_tracks": track_by_direction,
    }
    for direction in DIRECTIONS:
        spec = candidate_descriptor["directions"][direction]
        spec["idle_atlas"] = (output / direction / "idle.png").relative_to(ROOT).as_posix()
        spec["move_atlas"] = (output / direction / "move.png").relative_to(ROOT).as_posix()
        spec["fire_atlas"] = (output / direction / "fire.png").relative_to(ROOT).as_posix()
    descriptor_out = output / "runtime_descriptor.json"
    descriptor_out.write_text(json.dumps(candidate_descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": 1,
        "role": "MICA C03 R21 R8C frame-transition sole-lock runtime candidate",
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "promotion": "HOLD_PENDING_GODOT_RUNTIME_PONYTAIL_FULL_AND_WEB_VISUAL_GATES",
        "source_art_modified": False,
        "motion_source": "existing Blender + UAL R8C plates and immutable root tracks",
        "source_runtime": source_runtime.relative_to(ROOT).as_posix(),
        "source_runtime_descriptor_sha256": sha256(descriptor_source),
        "runtime_descriptor": descriptor_out.relative_to(ROOT).as_posix(),
        "runtime_descriptor_sha256": sha256(descriptor_out),
        "directional_tracks": track_by_direction,
        "quarantine": {
            "r20_and_prior_failed_or_hold_candidates_preserved": True,
            "deletion_performed": False,
            "retirement_manifest_required_before_disposal": True,
        },
    }
    manifest_path = output / "MICA_C03_R21_FRAME_TRANSITION_SOLE_LOCK_CANDIDATE.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": output.relative_to(ROOT).as_posix(),
        "descriptor": descriptor_out.relative_to(ROOT).as_posix(),
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
        "directions": len(track_by_direction),
        "promotion": manifest["promotion"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
