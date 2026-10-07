#!/usr/bin/env python3
"""Build the MICA R22 wide-stride runtime candidate from the R4 plates.

R21 proved the frame-transition/sole-lock runtime contract, but its source
atlases were the old, very small R8C raster.  R4 is the existing Blender+UAL
segmented render that has the intended full-body jog poses and a visibly wider
left/right foot separation.  This builder performs only deterministic
packaging: it never repaints or regenerates the ImageGen source art.

The root track is derived from the R4 support-foot targets.  While one foot is
planted (frames 00-11 and 12-23 respectively), its projected sole advances
monotonically along the travel axis.  A small cadence-sized bridge is used at
the support switch and at the cycle wrap; the actual root is emitted by the
existing Godot frame-transition runtime only when the authored cell changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": 4, "move": 24, "fire": 6}
CELL = 384
# The R4 Blender camera is orthographic with a 3.92-world-unit vertical
# framing.  Convert its foot-target world units to source-cell pixels before
# applying the shipped runtime display scale; omitting this factor would make
# the new root travel only ~0.2px per cycle (the exact regression this
# candidate is meant to remove).
BLENDER_ORTHO_SCALE = 3.92
WORLD_TO_RUNTIME_PX = CELL / BLENDER_ORTHO_SCALE

# These are the Blender-plane travel axes from the R4 manifest.  Godot's
# screen Y is inverted; the runtime only receives the scalar distance and
# multiplies it by its own canonical direction vector.
AXES = {
    "E": (1.0, 0.0),
    "SE": (2 ** -0.5, -2 ** -0.5),
    "S": (0.0, -1.0),
    "SW": (-2 ** -0.5, -2 ** -0.5),
    "W": (-1.0, 0.0),
    "NW": (-2 ** -0.5, 2 ** -0.5),
    "N": (0.0, 1.0),
    "NE": (2 ** -0.5, 2 ** -0.5),
}

# R4's 384px renders are the source of truth for this candidate.  The socket
# values are deliberately kept as a separate, reviewable table: the old R21
# sockets were authored against the tiny R8C plates and must not be reused.
# They are conservative points on the visible weapon muzzle; the candidate
# remains HOLD until the generated red-crosshair sheets pass visual review.
R4_MUZZLE = {
    "E": (268.0, 137.0),
    "SE": (252.0, 155.0),
    "S": (192.0, 183.0),
    "SW": (224.0, 165.0),
    "W": (112.0, 108.0),
    "NW": (120.0, 107.0),
    "N": (209.0, 54.0),
    "NE": (250.0, 91.0),
}


def inside(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {resolved}") from exc
    return resolved


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


def point_along(point: list[float], direction: str) -> float:
    axis = AXES[direction]
    return float(point[0]) * axis[0] + float(point[1]) * axis[1]


def build_root_track(manifest: dict, direction: str, display_scale: float) -> dict:
    records = manifest.get("directions", {}).get(direction, {}).get("move", [])
    if not isinstance(records, list) or len(records) != STATES["move"]:
        raise SystemExit(f"R4 manifest has no complete move records for {direction}")

    left = [point_along(record["gait_cycle"]["screen_left"]["foot_target"], direction) for record in records[:12]]
    right = [point_along(record["gait_cycle"]["screen_right"]["foot_target"], direction) for record in records[12:]]
    if any(left[i] >= left[i - 1] for i in range(1, len(left))):
        raise SystemExit(f"R4 left support sole is not monotonic for {direction}: {left}")
    if any(right[i] >= right[i - 1] for i in range(1, len(right))):
        raise SystemExit(f"R4 right support sole is not monotonic for {direction}: {right}")

    left_steps = [left[i - 1] - left[i] for i in range(1, len(left))]
    right_steps = [right[i - 1] - right[i] for i in range(1, len(right))]
    # The switch is a timing boundary, not a teleport between the two feet.
    # Use the local cadence-sized step from each support window.
    switch_step = (left_steps[-1] + right_steps[0]) * 0.5
    wrap_step = (right_steps[-1] + left_steps[0]) * 0.5
    if switch_step <= 0.0 or wrap_step <= 0.0:
        raise SystemExit(f"R4 support cadence has a non-positive bridge for {direction}")

    positions = [0.0]
    for step in left_steps:
        positions.append(positions[-1] + step * WORLD_TO_RUNTIME_PX * display_scale)
    positions.append(positions[-1] + switch_step * WORLD_TO_RUNTIME_PX * display_scale)
    for step in right_steps:
        positions.append(positions[-1] + step * WORLD_TO_RUNTIME_PX * display_scale)
    if len(positions) != STATES["move"]:
        raise AssertionError(f"internal track length error for {direction}: {len(positions)}")
    cycle_advance = positions[-1] + wrap_step * WORLD_TO_RUNTIME_PX * display_scale
    deltas = [positions[i] - positions[i - 1] for i in range(1, len(positions))]
    deltas.append(cycle_advance - positions[-1])
    if min(deltas) <= 0.0:
        raise SystemExit(f"R4 root track has a non-positive transition for {direction}: {deltas}")

    return {
        "space": "runtime_world_along_move_axis",
        "frame_positions": [round(value, 9) for value in positions],
        "cycle_advance": round(cycle_advance, 9),
        "frame_transition_min": round(min(deltas), 9),
        "frame_transition_max": round(max(deltas), 9),
        "support_windows": {"screen_left": [0, 11], "screen_right": [12, 23]},
        "source_support_axis": AXES[direction],
        "source_left_anchor_axis": [round(value, 9) for value in left],
        "source_right_anchor_axis": [round(value, 9) for value in right],
        "source_switch_step": round(switch_step, 9),
        "source_wrap_step": round(wrap_step, 9),
        "display_scale_applied": display_scale,
        "blender_ortho_scale": BLENDER_ORTHO_SCALE,
        "world_to_runtime_px": WORLD_TO_RUNTIME_PX * display_scale,
    }


def copy_atlas(source_dir: Path, state: str, count: int, target: Path) -> dict:
    frames: list[Image.Image] = []
    frame_hashes: list[str] = []
    for index in range(count):
        frame_path = source_dir / state / f"{index:02d}.png"
        if not frame_path.is_file():
            raise SystemExit(f"missing R4 {state} frame: {frame_path}")
        with Image.open(frame_path) as image:
            rgba = image.convert("RGBA")
            if rgba.size != (CELL, CELL):
                raise SystemExit(f"unexpected R4 frame size {frame_path}: {rgba.size}")
            frames.append(rgba.copy())
            frame_hashes.append(sha256(frame_path))
    atlas = Image.new("RGBA", (CELL, CELL * count), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        atlas.paste(frame, (0, index * CELL), frame)
    target.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(target, format="PNG")
    with Image.open(target) as check:
        if check.mode != "RGBA" or check.size != (CELL, CELL * count):
            raise SystemExit(f"atlas round-trip failed: {target}")
    return {
        "atlas": target.relative_to(ROOT).as_posix(),
        "sha256": sha256(target),
        "frame_count": count,
        "atlas_resolution": [CELL, CELL * count],
        "source_frames": frame_hashes,
        "unique_source_frames": len(set(frame_hashes)),
    }


def socket_table(direction: str, state: str, count: int) -> list[list[float]]:
    x, y = R4_MUZZLE[direction]
    # R4 keeps the upper body/weapon rigid during locomotion.  Keeping the
    # move socket fixed is therefore more truthful than borrowing R21's
    # unrelated tiny-plate offsets.  Fire recoil is reviewed separately.
    return [[x, y] for _ in range(count)]


def main() -> int:
    raise SystemExit(
        "FAIL_NOT_PROMOTABLE: R4 segmented plates were explicitly rejected by the user. "
        "R22 repackaging does not repair coat separation/legs. Retain both in quarantine; "
        "use motion_harness audit and a newly reviewed rig, not this retired builder."
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--r4-root",
        type=Path,
        default=Path("art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v9_neutral_r4_wide_step_segmented"),
    )
    parser.add_argument(
        "--base-descriptor",
        type=Path,
        default=Path("art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_r21_r8c_frame_transition_sole_lock/runtime_descriptor.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-name", default="r22_r4_wide_stride_sole_lock")
    args = parser.parse_args()

    r4_root = inside(args.r4_root, "R4 source")
    base_descriptor_path = inside(args.base_descriptor, "base descriptor")
    output = inside(args.output, "output")
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing candidate: {output}")
    render_manifest_path = r4_root / "MICA_C03_BLENDER_UAL_RENDER_MANIFEST.json"
    render_manifest = read_json(render_manifest_path, "R4 Blender+UAL manifest")
    if render_manifest.get("motion_only") is not True:
        raise SystemExit("R4 manifest must declare motion_only=true")
    if render_manifest.get("leg_rig", {}).get("move_rig_mode") != "segmented":
        raise SystemExit("R4 source is not the segmented two-leg rig")
    base = read_json(base_descriptor_path, "base runtime descriptor")
    if base.get("schema") != 2 or set(base.get("directions", {})) != set(DIRECTIONS):
        raise SystemExit("base descriptor is not a complete schema-2 MICA runtime")
    display_scale = float(base.get("display_scale", 0.34))
    if not 0.0 < display_scale <= 1.0:
        raise SystemExit("base descriptor has an invalid display_scale")

    output.mkdir(parents=True)
    atlas_records: dict[str, dict[str, dict[str, object]]] = {}
    descriptor = json.loads(json.dumps(base))
    descriptor["candidate"] = args.candidate_name
    descriptor["source_runtime"] = r4_root.relative_to(ROOT).as_posix()
    descriptor["source_runtime_manifest_sha256"] = sha256(render_manifest_path)
    descriptor["muzzle_source"] = "R4_rendered_weapon_tip_conservative_socket_table_PENDING_VISUAL_REVIEW"
    tracks: dict[str, dict] = {}
    for direction in DIRECTIONS:
        source_dir = r4_root / "blender_frames" / direction
        atlas_records[direction] = {}
        for state, count in STATES.items():
            target = output / direction / f"{state}.png"
            atlas_records[direction][state] = copy_atlas(source_dir, state, count, target)
            spec = descriptor["directions"][direction]
            spec[f"{state}_atlas"] = target.relative_to(ROOT).as_posix()
            spec[f"{state}_muzzle_xy"] = socket_table(direction, state, count)
        spec = descriptor["directions"][direction]
        spec["muzzle_xy"] = list(R4_MUZZLE[direction])
        spec["muzzle_source"] = "R4_rendered_weapon_tip_conservative_socket_table"
        tracks[direction] = build_root_track(render_manifest, direction, display_scale)

    descriptor["move_root_sync"] = {
        "enabled": True,
        "mode": "frame_transition_sole_lock",
        "frame_count": STATES["move"],
        "track_space": "runtime_world_along_move_axis",
        "rationale": (
            "R22 uses the R4 Blender+UAL segmented full-body jog plates. Root travel is derived "
            "from each direction's planted support-foot target and emitted only at visible-frame "
            "transitions; repeated high-rate samples hold the support sole in world space."
        ),
        "source_formula": (
            "project the planted support foot target onto the R4 Blender-plane travel axis; "
            "accumulate negative anchor deltas for frames 00-11 and 12-23; bridge the support "
            "switch and cycle wrap with the mean local cadence step; convert Blender world units "
            "to 384px/3.92 orthographic cell pixels, then multiply by display_scale."
        ),
        "directional_tracks": tracks,
    }
    descriptor_path = output / "runtime_descriptor.json"
    descriptor_path.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": 1,
        "role": "MICA C03 R22 R4 Blender+UAL segmented wide-stride runtime candidate",
        "candidate_status": "UNREVIEWED_DO_NOT_PROMOTE",
        "promotion": "HOLD_PENDING_CONTACT_SHEET_MUZZLE_GODOT_RUNTIME_PONYTAIL_FULL_AND_WEB_VISUAL_GATES",
        "source_art_modified": False,
        "motion_only": True,
        "motion_source": "existing Blender+UAL R4 segmented full-body jog plates",
        "source_render_manifest": render_manifest_path.relative_to(ROOT).as_posix(),
        "source_render_manifest_sha256": sha256(render_manifest_path),
        "source_render_candidate": r4_root.relative_to(ROOT).as_posix(),
        "base_descriptor": base_descriptor_path.relative_to(ROOT).as_posix(),
        "base_descriptor_sha256": sha256(base_descriptor_path),
        "runtime_descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "runtime_descriptor_sha256": sha256(descriptor_path),
        "atlas_records": atlas_records,
        "directional_tracks": tracks,
        "muzzle": {
            "status": "HOLD_PENDING_VISUAL_SOCKET_REVIEW",
            "source": "R4 384px rendered weapon-tip table",
            "points_by_direction": {direction: list(R4_MUZZLE[direction]) for direction in DIRECTIONS},
            "frame_policy": "fixed during move/idle/fire until red-crosshair review confirms recoil socket",
        },
        "quarantine": {
            "r20_r21_and_prior_failed_or_hold_candidates_preserved": True,
            "deletion_performed": False,
            "retirement_manifest_required_before_disposal": True,
        },
    }
    manifest_path = output / "MICA_C03_R22_R4_WIDE_STRIDE_CANDIDATE.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": output.relative_to(ROOT).as_posix(),
        "descriptor": descriptor_path.relative_to(ROOT).as_posix(),
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
        "directions": len(DIRECTIONS),
        "move_frames_per_direction": STATES["move"],
        "cycle_runtime_px": {direction: tracks[direction]["cycle_advance"] for direction in DIRECTIONS},
        "promotion": manifest["promotion"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
