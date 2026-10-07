#!/usr/bin/env python3
"""Render a 12-pose ImageGen gait through Blender on UAL contact timing.

Unlike the retired V25 renderer, this script rejects a two-pose source pair.
Each move cell selects one of twelve separately authored full-body gait poses;
Blender only performs deterministic compositing and the permitted W mirror.
UAL supplies the 24-sample timing/contact contract.  Idle and fire deliberately
freeze the lower body on a single planted source pose.
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
GAIT_POSES = 12
# The UAL event stream is left-support at samples 0-4 and right-support at
# samples 12-16.  Source indices are used twice in sequence, so the authored
# source sequence must preserve this support order.  It is recorded for review
# and checked against the chosen UAL contact sample below.
SOURCE_SUPPORT = ("left", "left", "left", "transfer", "swing", "swing", "right", "right", "right", "transfer", "swing", "swing")
PLANTED_POSE_INDEX = 10
DIRECTION_TO_PLANE = {
    "E": (1.0, 0.0),
    "SE": (0.7071, -0.7071),
    "S": (0.0, -1.0),
    "SW": (-0.7071, -0.7071),
    "W": (-1.0, 0.0),
    "NW": (-0.7071, 0.7071),
    "N": (0.0, 1.0),
    "NE": (0.7071, 0.7071),
}
FIRE_RECOIL_UNITS = (0.0, 0.004, 0.014, 0.030, 0.012, 0.002)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--cycle-sources", type=Path, required=True)
    parser.add_argument("--ual-locomotion", type=Path, required=True)
    parser.add_argument("--ual-fire", type=Path, required=True)
    parser.add_argument("--normalization-dir", default="normalized", help="derived chroma/matte folder beneath each source candidate")
    parser.add_argument("--gait-version", default="v6", help="candidate gait-source revision, for example v3 or v6")
    parser.add_argument(
        "--root-registration",
        type=Path,
        help=(
            "project-local immutable-source root-registration record. Blender applies "
            "its per-pose translations to whole-body planes, fixing visual root drift "
            "without translating, cropping, or repainting the ImageGen source art."
        ),
    )
    parser.add_argument(
        "--safe-source-selection",
        type=Path,
        help=(
            "optional project-local 12-slot-per-direction source selection. "
            "Each slot maps a UAL support phase to a reviewed full-body ImageGen pose, "
            "allowing unsafe high-knee source frames to be excluded without altering art."
        ),
    )
    parser.add_argument("--fallback-gait-version", help="legacy fallback revision; rejected unless explicitly allowed")
    parser.add_argument(
        "--allow-mixed-source-revisions",
        action="store_true",
        help="legacy escape hatch for diagnostics only; never use for a promotable candidate",
    )
    return parser.parse_args(argv)


def project_path(value: Path, label: str) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside the project: {path}") from exc
    return path


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


def load_safe_source_selection(path: Path | None) -> tuple[dict[str, list[int]], dict[str, int], Path | None]:
    """Validate an optional, explicit low-lift selection contract.

    The source set remains twelve immutable ImageGen poses for provenance.  A
    reviewed selection can deliberately reuse a safe contact pose in place of
    an unsafe high-knee pose; the manifest records both the original source
    index and its UAL support slot so the reuse is never mistaken for a new
    authored image.
    """
    identity = {direction: list(range(GAIT_POSES)) for direction in DIRECTIONS}
    planted = {direction: PLANTED_POSE_INDEX for direction in DIRECTIONS}
    if path is None:
        return identity, planted, None
    selection_path = project_path(path, "safe source selection")
    value = load_json(selection_path, "safe source selection")
    if value.get("schema") != 1 or value.get("review_status") != "HOLD_PENDING_VISUAL_QA":
        raise SystemExit("safe source selection must be schema 1 and remain HOLD_PENDING_VISUAL_QA")
    rows = value.get("directions")
    if not isinstance(rows, dict) or set(rows) != set(DIRECTIONS):
        raise SystemExit("safe source selection must provide exactly the eight movement directions")
    result: dict[str, list[int]] = {}
    planted_result: dict[str, int] = {}
    for direction in DIRECTIONS:
        entry = rows[direction]
        if not isinstance(entry, dict):
            raise SystemExit(f"safe source selection entry must be an object: {direction}")
        slots = entry.get("source_indices")
        planted_index = entry.get("planted_source_index")
        if not isinstance(slots, list) or len(slots) != GAIT_POSES or any(not isinstance(index, int) or not 0 <= index < GAIT_POSES for index in slots):
            raise SystemExit(f"{direction} must provide exactly twelve source indices in 0..11")
        if not isinstance(planted_index, int) or planted_index not in slots:
            raise SystemExit(f"{direction}.planted_source_index must be one selected source index")
        result[direction] = slots
        planted_result[direction] = planted_index
    return result, planted_result, selection_path


def load_root_registration(path: Path | None, art_prefix: str, gait_version: str) -> tuple[dict[str, list[tuple[int, int]]], Path | None]:
    """Validate per-source whole-body translations derived from source mattes."""
    identity = {direction: [(0, 0)] * GAIT_POSES for direction in DIRECTIONS}
    if path is None:
        return identity, None
    registration_path = project_path(path, "root registration")
    value = load_json(registration_path, "root registration")
    if value.get("schema") != 1 or value.get("source_art_modified") is not False:
        raise SystemExit("root registration must be schema 1 and declare immutable source art")
    if value.get("art_prefix") != art_prefix or value.get("gait_version") != gait_version:
        raise SystemExit("root registration art prefix/source revision does not match this candidate")
    rows = value.get("directions")
    if not isinstance(rows, dict) or set(rows) != set(DIRECTIONS):
        raise SystemExit("root registration must contain exactly the eight movement directions")
    limits = value.get("limits")
    if not isinstance(limits, dict):
        raise SystemExit("root registration lacks bounded transform limits")
    max_x = limits.get("max_abs_x_pixels")
    max_y = limits.get("max_abs_y_pixels")
    if not isinstance(max_x, int) or not isinstance(max_y, int) or max_x <= 0 or max_y <= 0:
        raise SystemExit("root registration limits are invalid")
    result: dict[str, list[tuple[int, int]]] = {}
    for direction in DIRECTIONS:
        entry = rows[direction]
        if not isinstance(entry, dict) or entry.get("reference_pose_index") != PLANTED_POSE_INDEX:
            raise SystemExit(f"root registration reference is invalid: {direction}")
        frames = entry.get("frames")
        if not isinstance(frames, list) or len(frames) != GAIT_POSES:
            raise SystemExit(f"root registration must contain twelve source poses: {direction}")
        translations: list[tuple[int, int]] = []
        for index, frame in enumerate(frames):
            shift = frame.get("translation_pixels") if isinstance(frame, dict) else None
            if not isinstance(shift, list) or len(shift) != 2 or any(not isinstance(value, int) for value in shift):
                raise SystemExit(f"root registration frame is invalid: {direction} F{index:02d}")
            x_shift, y_shift = shift
            if abs(x_shift) > max_x or abs(y_shift) > max_y:
                raise SystemExit(f"root registration exceeds its bounded transform: {direction} F{index:02d}")
            translations.append((x_shift, y_shift))
        if translations[PLANTED_POSE_INDEX] != (0, 0):
            raise SystemExit(f"root registration planted source must remain the fixed origin: {direction}")
        result[direction] = translations
    return result, registration_path


def root_translation_units(translation_pixels: tuple[int, int]) -> tuple[float, float]:
    """Map native square-source pixels to the renderer's 3x3 world plane."""
    x_shift, y_shift = translation_pixels
    scale = 3.0 / 512.0
    # Image y grows downward; Blender's plane y grows upward.
    return (x_shift * scale, -y_shift * scale)


def source_paths(cycle_root: Path, art_prefix: str, gait_version: str, fallback_gait_version: str | None, direction: str, index: int, normalization_dir: str) -> tuple[Path, Path, Path, Path, bool, str]:
    slug = art_prefix.lower()
    direct_candidate = cycle_root / f"candidate_{slug}_walk_{direction.lower()}_{gait_version}_real_gait"
    if direct_candidate.is_dir():
        source_direction = direction
        mirrored = False
        candidate = direct_candidate
    elif fallback_gait_version:
        fallback = cycle_root / f"candidate_{slug}_walk_{direction.lower()}_{fallback_gait_version}_real_gait"
        if fallback.is_dir():
            source_direction = direction
            mirrored = False
            candidate = fallback
        elif direction == "W":
            source_direction = "E"
            mirrored = True
            candidate = cycle_root / f"candidate_{slug}_walk_e_{fallback_gait_version}_real_gait"
        else:
            source_direction = direction
            mirrored = False
            candidate = direct_candidate
    elif direction == "W":
        source_direction = "E"
        mirrored = True
        candidate = cycle_root / f"candidate_{slug}_walk_e_{gait_version}_real_gait"
    else:
        source_direction = direction
        mirrored = False
        candidate = direct_candidate
    stem = f"{art_prefix}_{source_direction}_GAIT_F{index:02d}"
    rgb = candidate / normalization_dir / f"{stem}_EXACT_GREEN.png"
    mask = candidate / normalization_dir / f"{stem}_MASK.png"
    qa = candidate / normalization_dir / f"{stem}_NORMALIZATION_QA.json"
    if not rgb.is_file():
        # The clean-matte derivative retains the raw extracted filename as
        # part of its auditable output name; accept that explicit variant
        # without changing the authoritative ImageGen source itself.
        derived_stem = f"{stem}_IMAGEGEN_GREEN"
        rgb = candidate / normalization_dir / f"{derived_stem}_EXACT_GREEN.png"
        mask = candidate / normalization_dir / f"{derived_stem}_MASK.png"
        qa = candidate / normalization_dir / f"{derived_stem}_NORMALIZATION_QA.json"
    sheet = candidate / f"{art_prefix}_{source_direction}_GAIT_SHEET_{'A' if index < 6 else 'B'}_EXTRACTION.json"
    for path, label in ((rgb, "normalized gait source"), (mask, "gait matte"), (qa, "gait normalization QA"), (sheet, "lossless sheet extraction")):
        if not path.is_file():
            raise SystemExit(f"missing {label} for {direction} source pose F{index:02d}: {path}")
    evidence = load_json(qa, f"{direction} F{index:02d} normalization QA")
    if evidence.get("pass") is not True or evidence.get("generated_pixels_modified") is not False:
        raise SystemExit(f"source normalization did not preserve ImageGen pixels: {qa}")
    if evidence.get("resolution") != [512, 512]:
        raise SystemExit(f"source cell must be native 512x512: {qa}")
    extraction = load_json(sheet, f"{direction} F{index:02d} sheet extraction")
    grid = extraction.get("grid")
    if not isinstance(grid, dict) or grid.get("columns") != 2 or grid.get("rows") != 3:
        raise SystemExit(f"source sheet lacks a valid 2x3 extraction contract: {sheet}")
    output_cell_resolution = grid.get("output_cell_resolution", grid.get("cell_resolution"))
    if extraction.get("pass") is not True or output_cell_resolution != [512, 512]:
        raise SystemExit(f"source sheet does not provide native 512x512 gait cells: {sheet}")
    return rgb, mask, qa, sheet, mirrored, source_direction


def configure_scene(cell_size: int) -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    engine_ids = {item.identifier for item in scene.bl_rna.properties["render"].fixed_type.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engine_ids else "BLENDER_EEVEE_NEXT"
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
    camera_data = bpy.data.cameras.new("ROOK_REAL_GAIT_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.92
    camera = bpy.data.objects.new("ROOK_REAL_GAIT_CAMERA", camera_data)
    camera.location = (0.0, 0.0, 8.0)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return scene


def build_fire_split_planes(
    rgb: Path,
    mask: Path,
    direction: str,
    source_index: int,
    mirrored: bool,
    root_translation: tuple[float, float],
) -> tuple[bpy.types.Object, bpy.types.Object, tuple[float, float], tuple[float, float]]:
    """Build a static lower body plus an independently recoiling upper body.

    The two planes sample the same immutable source and overlap around the
    waist.  Blender applies only the UAL-driven upper-body transform, leaving
    the lower body mathematically fixed across the six fire frames.
    """
    lower = base.build_subject_plane(
        rgb,
        mask,
        f"ROOK_{direction}_FIRE_LOWER_F{source_index:02d}",
        uv_rect=(0.0, 0.0, 1.0, 0.50),
    )
    upper = base.build_subject_plane(
        rgb,
        mask,
        f"ROOK_{direction}_FIRE_UPPER_F{source_index:02d}",
        uv_rect=(0.0, 0.44, 1.0, 1.0),
    )
    lower.scale.x = -1.0 if mirrored else 1.0
    upper.scale.x = -1.0 if mirrored else 1.0
    waist_pivot = base.normalized_to_plane((0.5, 0.46))
    base.pivot_plane(upper, waist_pivot, 0.20)
    root_x, root_y = root_translation
    lower.location = (root_x, root_y, 0.10)
    # ``render_state`` reapplies this root on every recoil frame because it
    # deliberately resets the upper plane to its waist pivot before rotating.
    upper.location = (waist_pivot[0] + root_x, waist_pivot[1] + root_y, 0.20)
    return lower, upper, waist_pivot, root_translation


def fire_upper_transform(direction: str, frame: int, ual_sample: dict) -> dict:
    if not 0 <= frame < len(FIRE_RECOIL_UNITS):
        raise SystemExit(f"invalid fire frame index: {frame}")
    vector = DIRECTION_TO_PLANE[direction]
    magnitude = FIRE_RECOIL_UNITS[frame]
    label = ual_sample.get("label")
    if not isinstance(label, str):
        raise SystemExit(f"UAL fire sample is missing a label at {frame}")
    # Recoil is opposite the weapon-facing plane vector.  It is deliberately
    # compact (less than 1.2px at the 384px atlas scale), then made readable
    # by the distinct contact/peak timing and the runtime muzzle flash.
    return {
        "ual_label": label,
        "upper_offset_units": [round(-vector[0] * magnitude, 6), round(-vector[1] * magnitude, 6)],
        "upper_rotation_radians": round((-1.0 if vector[0] >= 0.0 else 1.0) * magnitude * 0.75, 6),
        "lower_body_transform": [0.0, 0.0, 0.0],
    }


def render_state(
    scene: bpy.types.Scene,
    planes: list[bpy.types.Object],
    fire_lower_planes: list[bpy.types.Object],
    fire_upper_planes: list[bpy.types.Object],
    fire_upper_pivots: list[tuple[float, float]],
    fire_upper_roots: list[tuple[float, float]],
    candidate: Path,
    direction: str,
    state: str,
    source_indices: list[int],
    sources: list[dict],
    ual_samples: list[dict] | None,
) -> list[dict]:
    output_dir = candidate / "blender_frames" / direction / state
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for frame, source_index in enumerate(source_indices):
        for index, plane in enumerate(planes):
            plane.hide_render = index != source_index
        for plane in fire_lower_planes:
            plane.hide_render = True
        for plane in fire_upper_planes:
            plane.hide_render = True
        recoil = None
        if state == "fire":
            if ual_samples is None:
                raise SystemExit("fire render requires UAL samples")
            for plane in planes:
                plane.hide_render = True
            fire_lower_planes[source_index].hide_render = False
            upper = fire_upper_planes[source_index]
            upper.hide_render = False
            recoil = fire_upper_transform(direction, frame, ual_samples[frame])
            pivot = fire_upper_pivots[source_index]
            root_x, root_y = fire_upper_roots[source_index]
            dx, dy = recoil["upper_offset_units"]
            upper.location = (pivot[0] + root_x + dx, pivot[1] + root_y + dy, 0.20)
            upper.rotation_euler = (0.0, 0.0, recoil["upper_rotation_radians"])
        output = output_dir / f"{frame:02d}.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        if not output.is_file() or output.stat().st_size <= 0:
            raise SystemExit(f"Blender did not render {direction} {state} frame {frame}")
        records.append({
            "index": frame,
            "gait_source_index": source_index,
            "source": sources[source_index],
            "ual": ual_samples[frame] if ual_samples is not None else {"state": state, "sample_index": frame},
            "upper_recoil": recoil,
            "path": output.relative_to(ROOT).as_posix(),
            "sha256": sha256(output),
        })
    return records


def main() -> int:
    args = parse_args()
    # A partial source replacement previously produced a candidate called V4
    # even though only E used V4 and the other seven directions silently came
    # from V3.  That makes a direction-specific repair look complete in a
    # technical frame-count gate.  Production candidates must have one source
    # revision across every direction; keep the old behavior only behind an
    # unmistakable diagnostic-only switch.
    if args.fallback_gait_version and not args.allow_mixed_source_revisions:
        raise SystemExit(
            "mixed gait-source revisions are prohibited for a promotable candidate; "
            "generate the requested revision for all eight directions first"
        )
    spec_path = project_path(args.spec, "spec")
    candidate = project_path(args.candidate, "candidate")
    cycle_root = project_path(args.cycle_sources, "cycle-sources")
    locomotion_path = project_path(args.ual_locomotion, "ual-locomotion")
    fire_path = project_path(args.ual_fire, "ual-fire")
    safe_selection, planted_sources, safe_selection_path = load_safe_source_selection(args.safe_source_selection)
    if candidate.exists() and any(candidate.iterdir()):
        raise SystemExit(f"refusing to overwrite candidate: {candidate}")
    spec = load_json(spec_path, "runtime spec")
    art_prefix = str(spec.get("art_prefix") or "ROOK_C02")
    root_registration, root_registration_path = load_root_registration(args.root_registration, art_prefix, args.gait_version)
    if int(spec["runtime"]["cell_size"]) != 384:
        raise SystemExit("renderer requires the 384px fast-runtime cell contract")
    locomotion = load_json(locomotion_path, "UAL locomotion")
    move_samples = locomotion.get("locomotion", {}).get("samples")
    contact_events = locomotion.get("locomotion", {}).get("events")
    if not isinstance(move_samples, list) or len(move_samples) != 24 or not isinstance(contact_events, list):
        raise SystemExit("UAL locomotion requires 24 samples and contact events")
    fire = load_json(fire_path, "UAL fire")
    fire_samples = fire.get("samples")
    if not isinstance(fire_samples, list) or len(fire_samples) != 6:
        raise SystemExit("UAL fire requires six samples")

    candidate.mkdir(parents=True, exist_ok=True)
    scene = configure_scene(384)
    records: dict[str, dict[str, list[dict]]] = {}
    authorities: dict[str, list[dict]] = {}
    # Every authored pose appears twice at 24fps.  This produces a 12Hz visual
    # gait with no 6- or 12-frame pose freeze and preserves UAL's 24 contacts.
    # UAL's support phase belongs to the authored *slot*, not to whichever
    # reviewed ImageGen source index is selected for that slot.  Keeping the
    # two identities separate avoids falsely relabelling a deliberately reused
    # low-lift contact image as a new source frame.
    move_slots = [index // 2 for index in range(24)]
    for sample_index in range(0, 5):
        if SOURCE_SUPPORT[move_slots[sample_index]] != "left":
            raise SystemExit("gait source order no longer matches UAL left-support contact window")
    for sample_index in range(12, 17):
        if SOURCE_SUPPORT[move_slots[sample_index]] != "right":
            raise SystemExit("gait source order no longer matches UAL right-support contact window")
    for direction in DIRECTIONS:
        source_records: list[dict] = []
        planes: list[bpy.types.Object] = []
        fire_lower_planes: list[bpy.types.Object] = []
        fire_upper_planes: list[bpy.types.Object] = []
        fire_upper_pivots: list[tuple[float, float]] = []
        fire_upper_roots: list[tuple[float, float]] = []
        for index in range(GAIT_POSES):
            rgb, mask, qa, sheet, mirrored, source_direction = source_paths(cycle_root, art_prefix, args.gait_version, args.fallback_gait_version, direction, index, args.normalization_dir)
            plane = base.build_subject_plane(rgb, mask, f"ROOK_{direction}_GAIT_F{index:02d}")
            plane.scale.x = -1.0 if mirrored else 1.0
            root_translation_px = root_registration[direction][index]
            root_translation = root_translation_units(root_translation_px)
            plane.location.x, plane.location.y = root_translation
            planes.append(plane)
            fire_lower, fire_upper, fire_pivot, fire_root = build_fire_split_planes(
                rgb, mask, direction, index, mirrored, root_translation
            )
            fire_lower_planes.append(fire_lower)
            fire_upper_planes.append(fire_upper)
            fire_upper_pivots.append(fire_pivot)
            fire_upper_roots.append(fire_root)
            source_records.append({
                "gait_source_index": index,
                "source_direction": source_direction,
                "pose_transfer": "horizontal_mirror_in_Blender" if mirrored else "none",
                "rgb": rgb.relative_to(ROOT).as_posix(),
                "rgb_sha256": sha256(rgb),
                "mask": mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(mask),
                "normalization_qa": qa.relative_to(ROOT).as_posix(),
                "normalization_qa_sha256": sha256(qa),
                "gait_sheet_extraction": sheet.relative_to(ROOT).as_posix(),
                "gait_sheet_extraction_sha256": sha256(sheet),
                "gait_support": SOURCE_SUPPORT[index],
                "root_translation_pixels": list(root_translation_px),
                "root_translation_blender_units": [round(root_translation[0], 6), round(root_translation[1], 6)],
            })
        authorities[direction] = source_records
        selected_slots = safe_selection[direction]
        move_indices = [selected_slots[slot] for slot in move_slots]
        planted_index = planted_sources[direction]
        # F10 is the approved low, planted stance; it is intentionally the only
        # lower-body source used by idle and firing to eliminate leg popping.
        records[direction] = {
            "idle": render_state(scene, planes, fire_lower_planes, fire_upper_planes, fire_upper_pivots, fire_upper_roots, candidate, direction, "idle", [planted_index] * 4, source_records, None),
            "move": render_state(scene, planes, fire_lower_planes, fire_upper_planes, fire_upper_pivots, fire_upper_roots, candidate, direction, "move", move_indices, source_records, move_samples),
            "fire": render_state(scene, planes, fire_lower_planes, fire_upper_planes, fire_upper_pivots, fire_upper_roots, candidate, direction, "fire", [planted_index] * 6, source_records, fire_samples),
        }
        for plane in [*planes, *fire_lower_planes, *fire_upper_planes]:
            bpy.data.objects.remove(plane, do_unlink=True)

    blend_path = candidate / "blender_scene" / f"{art_prefix}_REAL_GAIT_UAL.blend"
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    manifest = {
        "schema": 1,
        "role": f"{art_prefix} full-body ImageGen gait poses deterministically rendered in Blender on UAL1 24-sample contact timing",
        "motion_only": True,
        "source_art": "Built-in ImageGen twelve-pose gait sets with exact-green/mask technical derivatives",
        "source_art_modified": False,
        "root_registration": (
            {
                "path": root_registration_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(root_registration_path),
                "method": "whole-body Blender plane translation from torso/pelvis matte correlation; source pixels remain unchanged",
                "coordinates": "native source pixels [x right, y down], converted to Blender y-up plane coordinates",
            }
            if root_registration_path is not None
            else {"mode": "identity_no_translation"}
        ),
        "blender": {"version": bpy.app.version_string, "scene": blend_path.relative_to(ROOT).as_posix(), "scene_sha256": sha256(blend_path)},
        "ual": {
            "locomotion_curve": locomotion_path.relative_to(ROOT).as_posix(),
            "locomotion_curve_sha256": sha256(locomotion_path),
            "fire_curve": fire_path.relative_to(ROOT).as_posix(),
            "fire_curve_sha256": sha256(fire_path),
            "license": "CC0-1.0 motion-only reference",
            "contact_events": contact_events,
            "move_frame_contract": "twelve UAL support slots each persist for two consecutive samples; each slot selects a reviewed full-body ImageGen gait pose, and a low-lift selection may explicitly reuse a safe source without creating or altering art",
            "source_support_contract": list(SOURCE_SUPPORT),
            "idle_fire_contract": "idle uses F10 planted source only; fire keeps the F10 lower body fixed while Blender applies six UAL-driven upper-body recoil transforms",
        },
        "state_frame_counts": STATES,
        "safe_source_selection": (
            {
                "path": safe_selection_path.relative_to(ROOT).as_posix(),
                "sha256": sha256(safe_selection_path),
                "review_status": "HOLD_PENDING_VISUAL_QA",
                "slots": safe_selection,
                "planted_source_indices": planted_sources,
            }
            if safe_selection_path is not None
            else {"mode": "identity_0_to_11", "planted_source_indices": planted_sources}
        ),
        "direction_authorities": authorities,
        "directions": records,
        "validation_required": [
            "validate_rook_gait_contract.py PASS",
            "Ponytail Full visual temporal review of all 8 directions",
            "native 1920x1080 dynamic interactive capture",
            "muzzle/projectile contact review",
        ],
    }
    manifest_path = candidate / f"{art_prefix}_BLENDER_UAL_RENDER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ROOK_REAL_GAIT_BLENDER_UAL_RENDER_PASS=" + json.dumps({"candidate": candidate.relative_to(ROOT).as_posix(), "frames": 272, "manifest": manifest_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
