#!/usr/bin/env python3
"""Render a visible eight-direction walk from approved ImageGen pose pairs.

This Blender-only motion stage deliberately selects whole, approved ImageGen
walk poses rather than bending a static leg cutout.  UAL1 provides the exact
left/right contact timing; Blender selects the corresponding full-body pose
per phase and writes RGBA cells for atlas packaging.  No source pixel is
painted, regenerated, or modified here.

The W direction is a horizontal Blender pose-transfer of E.  The ImageGen W
candidates failed the strict alternating-foot review; mirroring the reviewed
E pair retains the approved character art while producing the same two clear
left/right gait phases for leftward travel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import render_fast_motion_blender_ual as base


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": 4, "move": 24, "fire": 6}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--walk-sources", type=Path, required=True)
    parser.add_argument("--ual-locomotion", type=Path, required=True)
    parser.add_argument("--ual-fire", type=Path, required=True)
    return parser.parse_args(argv)


def project_path(path: Path, label: str) -> Path:
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


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{label} must be a JSON object: {path}")
    return value


def source_stem(direction: str, phase: str) -> str:
    return f"ROOK_C02_{direction}_STEP_{phase}"


def source_paths(walk_root: Path, direction: str, phase: str) -> tuple[Path, Path, Path, bool, str]:
    """Resolve reviewed source/matte/QA; W uses reviewed E poses mirrored."""
    source_direction = "E" if direction == "W" else direction
    mirrored = direction == "W"
    # E V4 is the Ponytail-Full-approved strict side-profile gait authority.
    # Both E and
    # its Blender-mirrored W derivative must use it so boot, knee and pelvis
    # direction agree with horizontal travel rather than facing the camera.
    source_revision = "v4" if source_direction == "E" else "v1"
    candidate = walk_root / f"candidate_rook_c02_walk_{source_direction.lower()}_{source_revision}"
    stem = source_stem(source_direction, phase)
    rgb = candidate / "normalized" / f"{stem}_EXACT_GREEN.png"
    mask = candidate / "normalized" / f"{stem}_MASK.png"
    qa = candidate / "normalized" / f"{stem}_NORMALIZATION_QA.json"
    for path, label in ((rgb, "normalized source"), (mask, "source matte"), (qa, "normalization QA")):
        if not path.is_file():
            raise SystemExit(f"missing {label} for {direction} {phase}: {path}")
    evidence = load_json(qa, f"{direction} {phase} normalization QA")
    if evidence.get("pass") is not True or evidence.get("generated_pixels_modified") is not False:
        raise SystemExit(f"source normalization did not preserve ImageGen pixels: {qa}")
    if evidence.get("resolution") != [1024, 1536]:
        raise SystemExit(f"source is below the required native resolution: {qa}")
    return rgb, mask, qa, mirrored, source_direction


def build_pose(
    rgb: Path,
    mask: Path,
    name: str,
    mirrored: bool,
    uv_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
) -> bpy.types.Object:
    plane = base.build_subject_plane(rgb, mask, name, uv_rect=uv_rect)
    # A negative local X scale is a Blender pose transfer of the reviewed
    # east-facing artwork.  It is not a replacement or an edit of the master.
    plane.scale.x = -1.0 if mirrored else 1.0
    return plane


def configure_scene(cell_size: int) -> tuple[bpy.types.Scene, bpy.types.Object]:
    """Use the installed Blender 4.5 EEVEE engine without touching old rigs."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    # These are unlit source-image planes.  Eight EEVEE samples preserve the
    # original hard silhouette while avoiding a needless 64-sample render
    # loop for every deterministic sprite cell.
    scene.eevee.taa_render_samples = 8
    scene.eevee.taa_samples = 8
    scene.render.resolution_x = cell_size
    scene.render.resolution_y = cell_size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.view_settings.look = "None"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    camera_data = bpy.data.cameras.new("ROOK_WALK_POSE_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.92
    camera = bpy.data.objects.new("ROOK_WALK_POSE_CAMERA", camera_data)
    camera.location = (0.0, 0.0, 8.0)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return scene, camera


def phase_for_move(index: int) -> str:
    """Use UAL contact windows: A supports at loop ends, B at half-cycle."""
    if not 0 <= index < 24:
        raise SystemExit(f"invalid UAL locomotion sample index: {index}")
    return "A" if index < 6 or index >= 18 else "B"


def render_frames(
    scene: bpy.types.Scene,
    pose_layers: dict[str, list[bpy.types.Object]],
    candidate: Path,
    direction: str,
    state: str,
    phase_sequence: list[str],
    source_metadata: list[dict],
    ual_rows: list[dict] | None = None,
    recoil_offsets: list[float] | None = None,
) -> list[dict]:
    output_dir = candidate / "blender_frames" / direction / state
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for index, phase in enumerate(phase_sequence):
        for pose, layers in pose_layers.items():
            for plane in layers:
                plane.hide_render = pose != phase
                plane.location.x = 0.0
        if recoil_offsets is not None:
            # UAL fire timing moves the complete held-gun pose by <= 2px at
            # 384px.  This leaves the fixed per-direction muzzle contracts
            # valid while satisfying a real visible fire recovery sequence.
            for plane in pose_layers[phase]:
                plane.location.x = recoil_offsets[index]
        output = output_dir / f"{index:02d}.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        if not output.is_file() or output.stat().st_size <= 0:
            raise SystemExit(f"Blender did not render {direction} {state} frame {index}")
        rows.append({
            "index": index,
            "phase": phase,
            "source": source_metadata[0 if phase == "A" else 1],
            "ual": ual_rows[index] if ual_rows is not None else {"state": state, "sample_index": index},
            "path": output.relative_to(ROOT).as_posix(),
            "sha256": sha256(output),
        })
    return rows


def main() -> int:
    args = parse_args()
    spec_path = project_path(args.spec, "spec")
    candidate = project_path(args.candidate, "candidate")
    walk_root = project_path(args.walk_sources, "walk-sources")
    locomotion_path = project_path(args.ual_locomotion, "ual-locomotion")
    fire_path = project_path(args.ual_fire, "ual-fire")
    if candidate.exists() and any(candidate.iterdir()):
        raise SystemExit(f"refusing to overwrite candidate: {candidate}")

    spec = load_json(spec_path, "runtime spec")
    if int(spec["runtime"]["cell_size"]) != 384:
        raise SystemExit("renderer requires the 384px fast-runtime cell contract")
    locomotion = load_json(locomotion_path, "UAL locomotion")
    move_samples = locomotion.get("locomotion", {}).get("samples")
    events = locomotion.get("locomotion", {}).get("events")
    if not isinstance(move_samples, list) or len(move_samples) != 24 or not isinstance(events, list):
        raise SystemExit("UAL locomotion must provide 24 samples and event timing")
    fire = load_json(fire_path, "UAL fire")
    fire_samples = fire.get("samples")
    if not isinstance(fire_samples, list) or len(fire_samples) != 6:
        raise SystemExit("UAL fire must provide six samples")

    candidate.mkdir(parents=True, exist_ok=True)
    scene, _camera = configure_scene(384)
    records: dict[str, dict[str, list[dict]]] = {}
    authority: dict[str, dict[str, object]] = {}
    for direction in DIRECTIONS:
        sources: dict[str, tuple[Path, Path, bool]] = {}
        source_info: list[dict] = []
        for phase in ("A", "B"):
            rgb, mask, qa, mirrored, source_direction = source_paths(walk_root, direction, phase)
            sources[phase] = (rgb, mask, mirrored)
            source_info.append({
                "phase": phase,
                "source_direction": source_direction,
                "pose_transfer": "horizontal_mirror_in_Blender" if mirrored else "none",
                "rgb": rgb.relative_to(ROOT).as_posix(),
                "rgb_sha256": sha256(rgb),
                "mask": mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(mask),
                "normalization_qa": qa.relative_to(ROOT).as_posix(),
                "normalization_qa_sha256": sha256(qa),
                "pony_full_visual_review": "PASS before source selection",
            })
        # The alternate ImageGen stride poses correctly change the supporting
        # leg but can also rotate ROOK's pelvis/torso toward camera.  That
        # produces a visible 90-degree waist snap in horizontal and diagonal
        # movement.  Keep A's whole upper-body source layer fixed and overlay
        # only B's lower-body source crop for the alternate step in every
        # direction.  This is Blender pose transfer from immutable ImageGen
        # pixels, not source-art repair or redraw.
        a_rgb, a_mask, mirrored = sources["A"]
        b_rgb, b_mask, _ = sources["B"]
        pose_layers = {
            "A": [build_pose(a_rgb, a_mask, f"ROOK_{direction}_A_FULL", mirrored)],
            "B": [
                build_pose(a_rgb, a_mask, f"ROOK_{direction}_B_FIXED_UPPER", mirrored, (0.0, 0.46, 1.0, 1.0)),
                build_pose(b_rgb, b_mask, f"ROOK_{direction}_B_ALTERNATE_LOWER", mirrored, (0.0, 0.0, 1.0, 0.54)),
            ],
        }
        source_info[1]["upper_body_pose"] = "A fixed in Blender; B lower-body crop only"
        source_info[1]["upper_body_source_sha256"] = sha256(a_rgb)
        authority[direction] = {"phases": source_info}
        move_phases = [phase_for_move(index) for index in range(24)]
        # Four independent idle frames and six fire frames intentionally use
        # both approved contact poses, but locomotion itself always follows
        # UAL's left/right support window at frames 0-5 and 12-17.
        records[direction] = {
            "idle": render_frames(scene, pose_layers, candidate, direction, "idle", ["A", "A", "B", "B"], source_info),
            "move": render_frames(scene, pose_layers, candidate, direction, "move", move_phases, source_info, ual_rows=move_samples),
            "fire": render_frames(scene, pose_layers, candidate, direction, "fire", ["A", "A", "B", "B", "A", "A"], source_info, recoil_offsets=[0.0, 0.0, -0.006, -0.010, -0.004, 0.0]),
        }
        for layers in pose_layers.values():
            for plane in layers:
                bpy.data.objects.remove(plane, do_unlink=True)

    blend_path = candidate / "blender_scene" / "ROOK_C02_WALK_POSE_SOURCE_UAL.blend"
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    manifest = {
        "schema": 1,
        "role": "ROOK C02 visible alternating walk: approved ImageGen whole-pose frames selected in Blender at UAL1 left/right contact timing",
        "motion_only": True,
        "source_art": "Built-in ImageGen walk pose sources with exact-green/mask technical derivatives",
        "source_art_modified": False,
        "blender": {"version": bpy.app.version_string, "scene": blend_path.relative_to(ROOT).as_posix(), "scene_sha256": sha256(blend_path)},
        "ual": {
            "locomotion_curve": locomotion_path.relative_to(ROOT).as_posix(),
            "locomotion_curve_sha256": sha256(locomotion_path),
            "fire_curve": fire_path.relative_to(ROOT).as_posix(),
            "fire_curve_sha256": sha256(fire_path),
            "license": "CC0-1.0 motion-only reference",
            "contact_events": events,
            "move_frame_contract": "A is selected for UAL samples 0-5 and 18-23; B is selected for samples 6-17, making the two ImageGen leg poses visibly alternate at the left/right UAL support phases.",
        },
        "state_frame_counts": STATES,
        "direction_authorities": authority,
        "directions": records,
        "validation_required": ["Ponytail Full visual review of 8x24 move cells", "native 1920x1080 dynamic interactive capture", "muzzle/projectile contact review"],
    }
    manifest_path = candidate / "ROOK_C02_BLENDER_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ROOK_WALK_POSE_BLENDER_UAL_RENDER_PASS=" + json.dumps({"candidate": candidate.relative_to(ROOT).as_posix(), "frames": 272, "manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
