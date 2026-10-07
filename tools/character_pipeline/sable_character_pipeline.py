#!/usr/bin/env python3
"""Shortest-path SABLE operator art pipeline.

This tool does not generate source art.  Codex built-in ImageGen remains the
only source-art author.  The tool creates the handoff pack, accepts a verified
Blender+UAL motion export, promotes exact-green atlases to runtime RGBA,
computes auditable muzzle proposals, writes a data-driven Godot descriptor,
and can register the resulting operator profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motion_harness


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
STATES = ["idle", "move", "fire"]
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
DIRECTION_VECTORS = {
    "E": (1.0, 0.0),
    "SE": (math.sqrt(0.5), math.sqrt(0.5)),
    "S": (0.0, 1.0),
    "SW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "N": (0.0, -1.0),
    "NE": (math.sqrt(0.5), -math.sqrt(0.5)),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_path(value: str | Path, label: str, *, must_exist: bool = False) -> Path:
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside project: {resolved}") from exc
    if must_exist and not resolved.exists():
        raise ValueError(f"{label} is missing: {resolved}")
    return resolved


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    project_path(path, "JSON output")
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_suffix(path.suffix + ".tmp")
    staging.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staging.replace(path)


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["actor_id", "slug", "display_name", "role", "costume_id", "identity_lock", "visual_lock", "runtime", "paths", "registration"]
    for key in required:
        if key not in spec:
            errors.append(f"missing spec field: {key}")
    if errors:
        return errors
    actor_id = str(spec["actor_id"])
    slug = str(spec["slug"])
    if not actor_id.startswith("CHR_"):
        errors.append("actor_id must start with CHR_")
    if not slug or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in slug):
        errors.append("slug must use lowercase ASCII letters, numbers, and underscore only")

    identity = spec.get("identity_lock", {})
    if not isinstance(identity, dict) or identity.get("adult") is not True:
        errors.append("identity_lock.adult must be true")
    for key in ["faction", "body_type", "face_read", "weapon_class", "combat_role"]:
        if not str(identity.get(key, "")).strip():
            errors.append(f"identity_lock.{key} is required")

    visual = spec.get("visual_lock", {})
    if not isinstance(visual, dict):
        errors.append("visual_lock must be an object")
    else:
        if visual.get("source_author") != "built-in ImageGen":
            errors.append("visual_lock.source_author must be exactly 'built-in ImageGen'")
        if str(visual.get("generation_matte", "")).upper() != "#00FF00":
            errors.append("visual_lock.generation_matte must be #00FF00")
        if len(visual.get("palette", [])) < 3:
            errors.append("visual_lock.palette needs at least three colors")
        if not visual.get("silhouette_modules"):
            errors.append("visual_lock.silhouette_modules is required")
        if "forbidden_features" not in visual:
            errors.append("visual_lock.forbidden_features is required, even when empty")
        for key in ["exposure_coverage", "accessories", "weapon_grip_zones"]:
            if key not in visual:
                errors.append(f"visual_lock.{key} is required for the costume fingerprint")

    runtime = spec.get("runtime", {})
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
    else:
        cell = int(runtime.get("cell_size", 0))
        if cell < 256:
            errors.append("runtime.cell_size must be at least 256")
        state_specs = runtime.get("states", {})
        for state in STATES:
            row = state_specs.get(state, {}) if isinstance(state_specs, dict) else {}
            if int(row.get("frames", 0)) < 1 or float(row.get("fps", 0.0)) <= 0.0:
                errors.append(f"runtime.states.{state} needs positive frames and fps")

    paths = spec.get("paths", {})
    if isinstance(paths, dict):
        for key in ["work_root", "runtime_root", "descriptor"]:
            try:
                project_path(str(paths.get(key, "")), f"paths.{key}")
            except ValueError as exc:
                errors.append(str(exc))
    else:
        errors.append("paths must be an object")
    return errors


def spec_paths(spec: dict[str, Any]) -> dict[str, Path]:
    paths = spec["paths"]
    work_root = project_path(paths["work_root"], "work_root")
    runtime_root = project_path(paths["runtime_root"], "runtime_root")
    return {
        "work_root": work_root,
        "imagegen_current": work_root / "imagegen" / "current",
        "imagegen_previous": work_root / "imagegen" / "previous",
        "motion_current": work_root / "motion" / "current",
        "motion_previous": work_root / "motion" / "previous",
        "runtime_root": runtime_root,
        "runtime_current": runtime_root / "current",
        "runtime_previous": runtime_root / "previous",
        "descriptor": project_path(paths["descriptor"], "descriptor"),
    }


def read_spec(path: Path) -> dict[str, Any]:
    spec = load_json(project_path(path, "spec", must_exist=True))
    errors = validate_spec(spec)
    if errors:
        raise ValueError("SPEC_VALIDATION_FAIL\n- " + "\n- ".join(errors))
    return spec


def prompt_pack(spec: dict[str, Any]) -> str:
    identity = spec["identity_lock"]
    visual = spec["visual_lock"]
    forbidden = ", ".join(visual.get("forbidden_features", [])) or "none beyond the global project rules"
    palette = ", ".join(visual["palette"])
    modules = ", ".join(visual["silhouette_modules"])
    accessories = ", ".join(visual.get("accessories", [])) or "none"
    grip_zones = ", ".join(visual.get("weapon_grip_zones", []))
    return f"""# {spec['display_name']} — built-in ImageGen source-art handoff

This request is for Codex built-in ImageGen. Do not use ComfyUI, a local
diffusion model, local inpainting, ControlNet, LoRA, or another generator.

## Immutable identity and costume lock

- actorId: `{spec['actor_id']}`
- adult: `true`
- role: `{spec['role']}`
- faction: `{identity['faction']}`
- body type: `{identity['body_type']}`
- mature face read: `{identity['face_read']}`
- weapon class: `{identity['weapon_class']}`
- combat role: `{identity['combat_role']}`
- costumeId: `{spec['costume_id']}`
- palette placement: `{palette}`
- silhouette modules: `{modules}`
- exposure coverage: `{visual['exposure_coverage']}`
- accessories: `{accessories}`
- readable weapon/grip zones: `{grip_zones}`
- prohibited features: `{forbidden}`

## Generation contract

Create one native 1024px-or-larger full-body combat authority master first, followed
by eight independently authored direction masters in this exact order:
`E, SE, S, SW, W, NW, N, NE`. Preserve identity, costume modules, handedness,
weapon length, grip, and palette placement in every direction. Do not mirror an
asymmetric costume or weapon.

Every source uses one perfectly flat `#00FF00` background with no gradient,
floor, cast shadow, scenery, text, glow, reflected spill, or transparency.
Keep the subject completely inside frame, including hair and weapon.

Save selected current sources below:
`{relative(spec_paths(spec)['imagegen_current'])}`

Keep exactly one prior accepted candidate in `imagegen/previous`; remove older
rejected candidates only after the replacement is copied and hash-verified.

## Required review gate

Before motion work, create a labeled 1920×1080 contact sheet and record
`COSTUME_CONTINUITY_PASS` or `COSTUME_DRIFT_FAIL`, alpha-readiness, scale, and
weapon-grip readability. Only a PASS may enter Blender+UAL.
"""


def init_pipeline(spec: dict[str, Any]) -> dict[str, Any]:
    paths = spec_paths(spec)
    for key in ["imagegen_current", "imagegen_previous", "motion_current", "motion_previous", "runtime_root"]:
        paths[key].mkdir(parents=True, exist_ok=True)
    work_root = paths["work_root"]
    (work_root / "IMAGEGEN_HANDOFF.md").write_text(prompt_pack(spec), encoding="utf-8")
    handoff = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "costume_id": spec["costume_id"],
        "purpose": "Blender+UAL motion export contract; source art remains immutable",
        "input_authority": relative(paths["imagegen_current"]),
        "output": relative(paths["motion_current"]),
        "directions": DIRECTIONS,
        "states": spec["runtime"]["states"],
        "cell_size": int(spec["runtime"]["cell_size"]),
        "required_output_pattern": "<DIR>/<idle|move|fire>_green.png",
        "required_provenance": "SOURCE_PROVENANCE.json",
        "rules": [
            "Blender and UAL implement movement/rigging only",
            "do not repaint or regenerate source art locally",
            "write every cache, temp, render, and log below work_root",
            "export exact #00FF00 authoring atlases",
        ],
    }
    write_json(work_root / "BLENDER_UAL_HANDOFF.json", handoff)
    state = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "stage": "WAITING_FOR_IMAGEGEN_AUTHORITY",
        "created_at_utc": utc_now(),
        "next": "ImageGen authority + eight direction masters, then Blender+UAL export",
    }
    write_json(work_root / "PIPELINE_STATE.json", state)
    return state


def expected_motion_files(spec: dict[str, Any], root: Path | None = None) -> list[Path]:
    motion_root = root or spec_paths(spec)["motion_current"]
    return [motion_root / direction / f"{state}_green.png" for direction in DIRECTIONS for state in STATES]


def validate_gait_completion_gate(spec: dict[str, Any], motion_root: Path, provenance: dict[str, Any]) -> dict[str, Any] | None:
    """Validate the explicit all-direction visual acceptance gate before promotion.

    Frame uniqueness, alpha, and an eight-panel contact sheet are structural
    checks.  They cannot establish a believable low-lift walk.  Projects that
    opt into this gate must provide a Ponytail-reviewed native-resolution
    decision for every direction before a motion candidate may replace
    ``current``.
    """
    policy = spec.get("gait_completion_gate")
    if policy is None:
        return None
    if not isinstance(policy, dict) or policy.get("required") is not True:
        raise ValueError("gait_completion_gate must be an object with required: true")
    expected_revision = policy.get("required_source_revision")
    if not isinstance(expected_revision, str) or not expected_revision:
        raise ValueError("gait_completion_gate.required_source_revision is required")
    if provenance.get("gait_source_revision") != expected_revision:
        raise ValueError(
            "gait source revision is not promotable: "
            f"expected {expected_revision}, got {provenance.get('gait_source_revision')!r}"
        )
    revisions = provenance.get("gait_source_revisions_by_direction")
    if not isinstance(revisions, dict) or list(revisions.keys()) != DIRECTIONS:
        raise ValueError("gait source revision coverage must include exactly E..NE in canonical order")
    if any(revisions.get(direction) != expected_revision for direction in DIRECTIONS):
        raise ValueError("mixed gait-source revisions are not promotable")

    filename = policy.get("review_filename")
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise ValueError("gait_completion_gate.review_filename must be a candidate-local filename")
    review_path = motion_root / filename
    if not review_path.is_file():
        raise ValueError(f"missing full-direction gait acceptance gate: {review_path}")
    review = load_json(review_path)
    if review.get("gate") != "PASS":
        raise ValueError("full-direction gait acceptance gate is not PASS")
    reviewer = policy.get("required_reviewer")
    if reviewer and review.get("reviewer") != reviewer:
        raise ValueError(f"full-direction gait acceptance requires reviewer {reviewer!r}")
    if review.get("source_revision") != expected_revision:
        raise ValueError("full-direction gait acceptance revision mismatch")
    expected_candidate = relative(motion_root)
    if review.get("candidate") != expected_candidate:
        raise ValueError("full-direction gait acceptance does not identify this candidate")
    direction_reviews = review.get("directions")
    if not isinstance(direction_reviews, dict) or list(direction_reviews.keys()) != DIRECTIONS:
        raise ValueError("full-direction gait acceptance must contain every direction in canonical order")
    minimum = policy.get("minimum_review_resolution", [1920, 1080])
    if not isinstance(minimum, list) or len(minimum) != 2:
        raise ValueError("gait_completion_gate.minimum_review_resolution must be [width, height]")
    min_width, min_height = map(int, minimum)
    for direction in DIRECTIONS:
        entry = direction_reviews[direction]
        if not isinstance(entry, dict) or entry.get("gate") != "PASS":
            raise ValueError(f"full-direction gait acceptance is not PASS for {direction}")
        image_ref = entry.get("review_image")
        if not isinstance(image_ref, str):
            raise ValueError(f"missing native gait review image for {direction}")
        image_path = project_path(image_ref, f"gait review image {direction}", must_exist=True)
        with Image.open(image_path) as image:
            if image.width < min_width or image.height < min_height:
                raise ValueError(
                    f"gait review evidence for {direction} is below native minimum: "
                    f"{image.size} < {(min_width, min_height)}"
                )
        if entry.get("source_revision") not in (None, expected_revision):
            raise ValueError(f"gait review revision mismatch for {direction}")
    return review


def validate_provenance(spec: dict[str, Any], motion_root: Path, *, require_gait_completion: bool = False) -> dict[str, Any]:
    path = motion_root / "SOURCE_PROVENANCE.json"
    if not path.is_file():
        raise ValueError(f"missing Blender+UAL provenance: {path}")
    provenance = load_json(path)
    if provenance.get("imagegen_author") != "built-in ImageGen":
        raise ValueError("SOURCE_PROVENANCE imagegen_author must be built-in ImageGen")
    if provenance.get("blender_ual_motion") is not True:
        raise ValueError("SOURCE_PROVENANCE blender_ual_motion must be true")
    if provenance.get("costume_id") != spec["costume_id"]:
        raise ValueError("SOURCE_PROVENANCE costume_id mismatch")
    if provenance.get("costume_continuity") != "PASS":
        raise ValueError("COSTUME_CONTINUITY_PASS is required")
    resolution = provenance.get("authority_resolution", [])
    if not isinstance(resolution, list) or len(resolution) != 2 or min(map(int, resolution)) < 1024:
        raise ValueError("authority source must be native 1024px or larger; do not upscale a smaller source")
    if require_gait_completion:
        validate_gait_completion_gate(spec, motion_root, provenance)
    return provenance


def inspect_green_atlas(path: Path, expected_size: tuple[int, int]) -> tuple[np.ndarray, float]:
    if not path.is_file():
        raise ValueError(f"missing motion atlas: {path}")
    rgb = np.asarray(Image.open(path).convert("RGB"))
    if (rgb.shape[1], rgb.shape[0]) != expected_size:
        raise ValueError(f"atlas size mismatch {path}: {(rgb.shape[1], rgb.shape[0])} != {expected_size}")
    green = np.all(rgb == GREEN, axis=2)
    coverage = float(green.mean())
    if not 0.10 <= coverage < 0.995:
        raise ValueError(f"exact-green coverage failed {path}: {coverage:.6f}")
    return rgb, coverage


def rgba_from_green(rgb: np.ndarray) -> Image.Image:
    green = np.all(rgb == GREEN, axis=2)
    alpha = np.where(green, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack((rgb, alpha)), mode="RGBA")


def muzzle_proposal(fire_rgb: np.ndarray, direction: str, cell_size: int) -> list[float]:
    first = fire_rgb[:cell_size, :cell_size]
    opaque = ~np.all(first == GREEN, axis=2)
    ys, xs = np.nonzero(opaque)
    if xs.size < 32:
        raise ValueError(f"insufficient opaque pixels for muzzle proposal: {direction}")
    dx, dy = DIRECTION_VECTORS[direction]
    cx = cy = (cell_size - 1) * 0.5
    rel_x = xs.astype(np.float64) - cx
    rel_y = ys.astype(np.float64) - cy
    projection = rel_x * dx + rel_y * dy
    perpendicular = np.abs(-rel_x * dy + rel_y * dx)
    corridor = perpendicular <= cell_size * 0.34
    if int(corridor.sum()) < 16:
        corridor = np.ones_like(corridor, dtype=bool)
    candidate_indices = np.flatnonzero(corridor)
    best = candidate_indices[int(np.argmax(projection[candidate_indices]))]
    x = float(xs[best]) + dx * 3.0
    y = float(ys[best]) + dy * 3.0
    for _ in range(24):
        px = int(round(max(0.0, min(cell_size - 1.0, x))))
        py = int(round(max(0.0, min(cell_size - 1.0, y))))
        if not opaque[py, px]:
            return [round(x, 4), round(y, 4)]
        x += dx
        y += dy
    raise ValueError(f"muzzle proposal remained inside silhouette: {direction}")


def tracked_muzzle_for_cell(
    cell_rgb: np.ndarray,
    direction: str,
    anchor: list[float],
    tracking: dict[str, Any],
) -> list[float]:
    """Track the authored barrel tip near a reviewed direction anchor.

    The old whole-silhouette extreme incorrectly selected boots and coat tails
    for S/SE/SW.  This tracker is deliberately local to the reviewed weapon
    region.  Foreshortened views use the visible cyan emitter rather than a
    silhouette edge because the barrel points toward the camera.
    """
    height, width = cell_rgb.shape[:2]
    opaque = ~np.all(cell_rgb == GREEN, axis=2)
    yy, xx = np.indices((height, width))
    ax, ay = map(float, anchor)
    radius = float(tracking.get("radius", 72.0))
    local = opaque & (((xx - ax) ** 2 + (yy - ay) ** 2) <= radius**2)
    search_box = tracking.get("search_boxes", {}).get(direction)
    if isinstance(search_box, list) and len(search_box) == 4:
        x0, y0, x1, y1 = map(float, search_box)
        local = opaque & (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    if int(local.sum()) < 8:
        raise ValueError(f"insufficient local muzzle pixels: {direction} at {anchor}")

    if direction in set(tracking.get("foreshortened_directions", [])):
        cyan_radius = float(tracking.get("cyan_radius", 34.0))
        r = cell_rgb[:, :, 0].astype(np.float32)
        g = cell_rgb[:, :, 1].astype(np.float32)
        b = cell_rgb[:, :, 2].astype(np.float32)
        cyan = (
            local
            & (((xx - ax) ** 2 + (yy - ay) ** 2) <= cyan_radius**2)
            & (g >= 105.0)
            & (b >= 90.0)
            & (g >= r * 1.08)
            & (b >= r * 1.05)
        )
        ys, xs = np.nonzero(cyan)
        if xs.size >= 4:
            weights = (g[ys, xs] + b[ys, xs] - r[ys, xs]).clip(min=1.0)
            return [
                round(float(np.average(xs, weights=weights)), 4),
                round(float(np.average(ys, weights=weights)), 4),
            ]
        return [round(ax, 4), round(ay, 4)]

    ys, xs = np.nonzero(local)
    # A locomotion direction is usually also the authored weapon-facing
    # direction, but a project may explicitly declare a reviewed barrel vector
    # for an asymmetric three-quarter source.  Do not infer it from a boot or
    # coat silhouette when the art shows a different weapon orientation.
    configured_vector = tracking.get("aim_vectors", {}).get(direction)
    if isinstance(configured_vector, list) and len(configured_vector) == 2:
        dx, dy = map(float, configured_vector)
        magnitude = math.hypot(dx, dy)
        if magnitude < 0.001:
            raise ValueError(f"invalid zero-length reviewed aim vector: {direction}")
        dx, dy = dx / magnitude, dy / magnitude
    else:
        dx, dy = DIRECTION_VECTORS[direction]
    rel_x = xs.astype(np.float64) - ax
    rel_y = ys.astype(np.float64) - ay
    perpendicular = np.abs(-rel_x * dy + rel_y * dx)
    # A reviewed weapon-only box is stronger than a static corridor because
    # ImageGen gait poses legitimately translate the held carbine between
    # frames.  The box excludes legs/coat while preserving that translation.
    corridor = (
        np.ones_like(perpendicular, dtype=bool)
        if isinstance(search_box, list) and len(search_box) == 4
        else perpendicular <= float(tracking.get("perpendicular_limit", 24.0))
    )
    if int(corridor.sum()) < 4:
        corridor = np.ones_like(corridor, dtype=bool)
    candidates = np.flatnonzero(corridor)
    projection = rel_x * dx + rel_y * dy
    best = candidates[int(np.argmax(projection[candidates]))]
    x = float(xs[best]) + dx * float(tracking.get("outside_offset", 3.0))
    y = float(ys[best]) + dy * float(tracking.get("outside_offset", 3.0))
    return [round(max(0.0, min(width - 1.0, x)), 4), round(max(0.0, min(height - 1.0, y)), 4)]


def tracked_muzzle_frames(
    atlas_rgb: np.ndarray,
    direction: str,
    cell_size: int,
    frame_count: int,
    tracking: dict[str, Any],
) -> list[list[float]]:
    anchors = tracking.get("anchors", {})
    anchor = anchors.get(direction)
    if not isinstance(anchor, list) or len(anchor) != 2:
        raise ValueError(f"reviewed muzzle anchor missing: {direction}")
    return [
        tracked_muzzle_for_cell(
            atlas_rgb[index * cell_size : (index + 1) * cell_size, :cell_size],
            direction,
            anchor,
            tracking,
        )
        for index in range(frame_count)
    ]


def build_contact_sheet(runtime_dir: Path, spec: dict[str, Any]) -> Path:
    cell_size = int(spec["runtime"]["cell_size"])
    canvas = Image.new("RGB", (1920, 1080), (12, 20, 28))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((48, 28), f"{spec['display_name']} | {spec['costume_id']} | FAST 8-DIRECTION RUNTIME", fill=(225, 240, 248), font=font)
    thumb = 240
    start_x, start_y = 360, 90
    for index, direction in enumerate(DIRECTIONS):
        row, col = divmod(index, 4)
        with Image.open(runtime_dir / direction / "fire.png") as atlas:
            first = atlas.crop((0, 0, cell_size, cell_size))
            first.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
            x = start_x + col * 300
            y = start_y + row * 430
            checker = Image.new("RGB", (thumb, thumb), (238, 242, 246) if row == 0 else (35, 42, 50))
            checker.paste(first, ((thumb - first.width) // 2, (thumb - first.height) // 2), first)
            canvas.paste(checker, (x, y))
            draw.text((x, y + thumb + 12), direction, fill=(105, 220, 245), font=font)
    draw.text((48, 1024), "Native 1920x1080 review container | source cells shown without upscale", fill=(155, 175, 188), font=font)
    output = runtime_dir / "FAST_RUNTIME_CONTACT_1920X1080.png"
    canvas.save(output)
    return output


def validate_static_contact_1080p(contact: Path, output: Path) -> None:
    validator = ROOT / "tools" / "art_pipeline" / "validate_visual_evidence_1080p.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(validator),
            str(contact),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise ValueError("1080P_EVIDENCE_VALIDATION_FAIL\n" + completed.stdout + completed.stderr)


def rotate_verified(staging: Path, current: Path, previous: Path, receipt: str | Path | None = None) -> None:
    motion_harness.require_seal(receipt)
    for path in [staging, current, previous]:
        project_path(path, "promotion path")
    resolved = [path.resolve() for path in [staging, current, previous]]
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(resolved) for b in resolved[i + 1:]):
        raise ValueError("promotion paths must be distinct non-overlapping directories")
    if previous.exists():
        motion_harness.quarantine(previous, "retained prior candidate; not disposal")
    if current.exists():
        current.replace(previous)
    try:
        staging.replace(current)
    except OSError:
        if previous.exists() and not current.exists():
            previous.replace(current)
        raise


def same_runtime_atlases(staging: Path, current: Path) -> bool:
    """Keep the retained previous candidate when only descriptor metadata changes."""
    if not current.is_dir():
        return False
    for direction in DIRECTIONS:
        for state in STATES:
            staged = staging / direction / f"{state}.png"
            existing = current / direction / f"{state}.png"
            if not existing.is_file() or sha256(staged) != sha256(existing):
                return False
    return True


def build_runtime(spec: dict[str, Any], candidate_value: str | None = None) -> dict[str, Any]:
    paths = spec_paths(spec)
    motion_root = project_path(candidate_value, "motion candidate", must_exist=True) if candidate_value else paths["motion_current"]
    motion_harness.assert_not_rejected([motion_root])
    provenance = validate_provenance(spec, motion_root)
    import generation_harness as generation
    fixture=provenance.get('qa_fixture_only',False)
    if type(fixture) is not bool:
        raise ValueError('QA_FIXTURE_FLAG_MUST_BE_BOOLEAN')
    generation_files={}
    if fixture:
        isolated=ROOT/'artifacts/character_pipeline_smoke'
        if spec.get('actor_id')!='CHR_SMOKE_FAST' or not motion_root.is_relative_to(isolated) or any(not p.is_relative_to(isolated) for p in paths.values()):
            raise ValueError('SYNTHETIC_PACKAGING_CANNOT_ESCAPE_INTO_PRODUCTION')
    else:
        approved=generation.motion_build_bindings(spec.get('motion_build_roles',{}).get('generation_receipt',[]),spec['actor_id'],spec['costume_id'])
        generation_files=approved['files']
    runtime = spec["runtime"]
    cell_size = int(runtime["cell_size"])
    runtime_root = paths["runtime_root"]
    # Immutable candidate path: build NEVER overwrites current, previous, the
    # registered descriptor, or existing QA. Rejected work remains recoverable.
    staging = runtime_root / "candidates" / ("build_" + uuid.uuid4().hex)
    staging.mkdir(parents=True)

    directions: dict[str, Any] = {}
    files: list[dict[str, Any]] = []
    for direction in DIRECTIONS:
        direction_dir = staging / direction
        direction_dir.mkdir(parents=True)
        entry: dict[str, Any] = {}
        state_muzzles: dict[str, list[list[float]]] = {}
        tracking = spec.get("muzzle_tracking")
        for state in STATES:
            state_spec = runtime["states"][state]
            source = motion_root / direction / f"{state}_green.png"
            rgb, green_coverage = inspect_green_atlas(
                source,
                (cell_size, cell_size * int(state_spec["frames"])),
            )
            output = direction_dir / f"{state}.png"
            rgba_from_green(rgb).save(output)
            with Image.open(output) as check:
                extrema = check.getchannel("A").getextrema()
                if extrema != (0, 255):
                    raise ValueError(f"runtime alpha extrema failed: {output} {extrema}")
            entry[state + "_atlas"] = relative(output)
            files.append({
                "direction": direction,
                "state": state,
                "source": relative(source),
                "source_sha256": sha256(source),
                "runtime": entry[state + "_atlas"],
                "runtime_sha256": sha256(output),
                "exact_green_coverage": green_coverage,
            })
            if isinstance(tracking, dict):
                state_muzzles[state] = tracked_muzzle_frames(
                    rgb,
                    direction,
                    cell_size,
                    int(state_spec["frames"]),
                    tracking,
                )
                entry[state + "_muzzle_xy"] = state_muzzles[state]
        hint = spec.get("muzzle_hints", {}).get(direction)
        if isinstance(tracking, dict):
            # Fire frame 2 is the authored contact frame and remains the
            # backwards-compatible scalar socket for older consumers.
            fire_contact = min(2, len(state_muzzles["fire"]) - 1)
            entry["muzzle_xy"] = state_muzzles["fire"][fire_contact]
            entry["muzzle_source"] = "reviewed_anchor_local_frame_tracking"
            entry["muzzle_review"] = spec.get("muzzle_review", "USER_REVIEW_REQUIRED")
        elif isinstance(hint, list) and len(hint) == 2:
            entry["muzzle_xy"] = [float(hint[0]), float(hint[1])]
            entry["muzzle_source"] = spec.get("muzzle_hint_source", "spec_hint")
            if spec.get("muzzle_review"):
                entry["muzzle_review"] = spec["muzzle_review"]
        else:
            fire_source = motion_root / direction / "fire_green.png"
            fire_rgb, _ = inspect_green_atlas(
                fire_source,
                (cell_size, cell_size * int(runtime["states"]["fire"]["frames"])),
            )
            entry["muzzle_xy"] = muzzle_proposal(fire_rgb, direction, cell_size)
            entry["muzzle_source"] = "automatic_proposal_requires_visual_review"
        directions[direction] = entry

    descriptor = {
        "schema": 2 if isinstance(spec.get("muzzle_tracking"), dict) else 1,
        "actor_id": spec["actor_id"],
        "display_name": spec["display_name"],
        "costume_id": spec["costume_id"],
        "candidate": staging.name,
        "runtime_bundle": relative(staging),
        "cell_size": cell_size,
        "display_scale": float(runtime["display_scale"]),
        "display_offset": runtime["display_offset"],
        "states": runtime["states"],
        "directions": directions,
        "source_contract": {
            "imagegen_author": "built-in ImageGen",
            "motion_authoring": "Blender+UAL",
            "costume_continuity": "PASS",
            "provenance": relative(motion_root / "SOURCE_PROVENANCE.json"),
        },
    }
    # Never infer independent movement/aim support from an eight-row atlas.
    if spec.get("aim_move_policy"):
        descriptor["aim_move_policy"] = spec["aim_move_policy"]
    write_json(staging / "BUILD_SPEC.json", spec)
    inputs = [motion_root / "SOURCE_PROVENANCE.json", Path(__file__).resolve(), staging / "BUILD_SPEC.json"]
    inputs += expected_motion_files(spec, motion_root)
    inputs.extend(project_path(p,'generation approval input',must_exist=True) for p in generation_files)
    roles = spec.get("motion_build_roles", {})
    for role_paths in roles.values():
        inputs.extend(project_path(p, "motion build input", must_exist=True) for p in role_paths)
    write_json(staging / "MOTION_BUILD_INPUTS.json", {"schema": 1, "roles": roles,
        "actor_id":spec['actor_id'],"costume_id":spec['costume_id'],
        "qa_fixture_only": bool(provenance.get("qa_fixture_only", False)),
        "files": {relative(p): sha256(p) for p in inputs}})
    write_json(staging / "runtime_descriptor.json", descriptor)
    contact = build_contact_sheet(staging, spec)
    contact_qa = staging / "FAST_RUNTIME_CONTACT_1080P_QA.json"
    # This is a static contact sheet.  It proves only container/decoder
    # properties and must never be recorded as an interactive capture.
    validate_static_contact_1080p(contact, contact_qa)
    manifest = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "costume_id": spec["costume_id"],
        "built_at_utc": utc_now(),
        "source_provenance": provenance,
        "directions": DIRECTIONS,
        "files": files,
        "contact_sheet": relative(contact),
        "contact_1080p_qa": relative(contact_qa),
        "contact_resolution": [1920, 1080],
        "retention": "immutable candidate; failed assets retained until all-gate final and retirement manifest",
        "visual_gate": "STATIC_CONTACT_ONLY__RUNTIME_DYNAMIC_CAPTURE_REQUIRED",
    }
    write_json(staging / "FAST_RUNTIME_MANIFEST.json", manifest)
    state = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "stage": "CANDIDATE_BUILT_NOT_PROMOTED",
        "updated_at_utc": utc_now(),
        "descriptor": relative(staging / "runtime_descriptor.json"),
        "contact_sheet": relative(contact),
        "production_pointer_changed": False,
        "next": "motion_harness audit/run, independent observed gait/muzzles, live HTML parity, all reviews, seal, promote-runtime",
    }
    write_json(paths["work_root"] / "PIPELINE_STATE.json", state)
    return state


def validate_runtime(spec: dict[str, Any], allow_missing_assets: bool = False, descriptor_value: str | None = None) -> dict[str, Any]:
    paths = spec_paths(spec)
    descriptor_path = project_path(descriptor_value, "descriptor") if descriptor_value else paths["descriptor"]
    if not descriptor_path.is_file():
        if allow_missing_assets:
            return {"gate": "PASS_SCAFFOLD_ONLY", "descriptor": relative(descriptor_path)}
        raise ValueError(f"runtime descriptor missing: {descriptor_path}")
    descriptor = load_json(descriptor_path)
    errors: list[str] = []
    if descriptor.get("actor_id") != spec["actor_id"]:
        errors.append("descriptor actor_id mismatch")
    if list(descriptor.get("directions", {}).keys()) != DIRECTIONS:
        errors.append("descriptor direction order mismatch")
    cell_size = int(spec["runtime"]["cell_size"])
    for direction in DIRECTIONS:
        entry = descriptor.get("directions", {}).get(direction, {})
        for state in STATES:
            path = project_path(entry.get(state + "_atlas", ""), f"{direction}.{state}")
            frames = int(spec["runtime"]["states"][state]["frames"])
            if not path.is_file():
                errors.append(f"missing runtime atlas: {relative(path)}")
                continue
            with Image.open(path) as image:
                if image.size != (cell_size, cell_size * frames) or image.mode != "RGBA":
                    errors.append(f"invalid runtime atlas: {relative(path)} {image.size} {image.mode}")
                elif image.getchannel("A").getextrema() != (0, 255):
                    errors.append(f"invalid alpha extrema: {relative(path)}")
            sockets = entry.get(state + "_muzzle_xy")
            if descriptor.get("schema", 1) >= 2:
                if not isinstance(sockets, list) or len(sockets) != frames:
                    errors.append(f"invalid frame muzzle count: {direction}.{state}")
                elif any(not isinstance(point, list) or len(point) != 2 for point in sockets):
                    errors.append(f"invalid frame muzzle socket: {direction}.{state}")
    bundle = project_path(descriptor["runtime_bundle"], "runtime bundle") if descriptor.get("runtime_bundle") else paths["runtime_current"]
    contact = bundle / "FAST_RUNTIME_CONTACT_1920X1080.png"
    if not contact.is_file():
        errors.append("missing 1080p contact sheet")
    else:
        with Image.open(contact) as image:
            if image.size != (1920, 1080):
                errors.append(f"contact sheet is not native 1920x1080: {image.size}")
    report = {
        "schema": 1,
        "generated_at_utc": utc_now(),
        "gate": "PASS_STRUCTURE_ONLY" if not errors else "FAIL",
        "actor_id": spec["actor_id"],
        "descriptor": relative(descriptor_path),
        "errors": errors,
    }
    write_json(paths["work_root"] / "FAST_PIPELINE_QA.json", report)
    if errors:
        raise ValueError("RUNTIME_VALIDATION_FAIL\n- " + "\n- ".join(errors))
    return report


def promote_motion_candidate(spec: dict[str, Any], candidate_value: str, receipt: str | Path | None = None) -> dict[str, Any]:
    verified = motion_harness.require_seal(receipt)
    paths = spec_paths(spec)
    candidate = project_path(candidate_value, "motion candidate", must_exist=True)
    if not candidate.is_dir():
        raise ValueError("motion candidate must be a directory")
    motion_harness.assert_not_rejected([candidate])
    for source in expected_motion_files(spec, candidate):
        if verified["snapshot"]["files"].get(relative(source)) != sha256(source):
            raise ValueError("motion input is not bound to the approved runtime receipt")
    validate_provenance(spec, candidate, require_gait_completion=True)
    runtime = spec["runtime"]
    cell_size = int(runtime["cell_size"])
    for direction in DIRECTIONS:
        for state in STATES:
            inspect_green_atlas(
                candidate / direction / f"{state}_green.png",
                (cell_size, cell_size * int(runtime["states"][state]["frames"])),
            )
    staging = paths["work_root"] / "motion" / ".staging_current"
    if staging.exists():
        motion_harness.quarantine(staging, "interrupted input promotion")
    shutil.copytree(candidate, staging)
    source_hashes = {relative(path): sha256(path) for path in expected_motion_files(spec, staging)}
    rotate_verified(staging, paths["motion_current"], paths["motion_previous"], receipt)
    return {"gate": "PASS_INPUT_SELECTION_ONLY", "motion_current": relative(paths["motion_current"]), "source_hashes": source_hashes}


def promote_runtime(spec: dict[str, Any], receipt: str | Path | None) -> dict[str, Any]:
    verified = motion_harness.require_seal(receipt)
    paths = spec_paths(spec)
    candidate_descriptor = project_path(verified["snapshot"]["descriptor"], "sealed descriptor", must_exist=True)
    descriptor = load_json(candidate_descriptor)
    if descriptor.get("actor_id") != spec["actor_id"]:
        raise ValueError("receipt actor_id mismatch")
    validate_runtime(spec, descriptor_value=relative(candidate_descriptor))
    # Only one atomic public pointer is replaced. Assets stay at their reviewed,
    # immutable paths, so review hashes and rollback references remain valid.
    if paths["descriptor"].exists():
        backup = paths["work_root"] / "pointer_history" / ("descriptor_" + uuid.uuid4().hex + ".json")
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths["descriptor"], backup)
    paths["descriptor"].parent.mkdir(parents=True, exist_ok=True)
    temp = paths["descriptor"].with_name(paths["descriptor"].name + "." + uuid.uuid4().hex + ".pending")
    shutil.copy2(candidate_descriptor, temp)
    if sha256(temp) != verified['snapshot']['files'].get(relative(candidate_descriptor)):
        raise ValueError("candidate descriptor byte identity failed BEFORE promotion")
    temp.replace(paths["descriptor"])
    return {"gate": "PASS_ALL_REQUIRED_GATES", "descriptor": relative(paths["descriptor"]), "receipt": relative(Path(receipt))}


def register_profile(spec: dict[str, Any], receipt: str | Path | None = None) -> dict[str, Any]:
    paths = spec_paths(spec)
    verified = motion_harness.require_seal(receipt)
    sealed = project_path(verified["snapshot"]["descriptor"], "sealed descriptor", must_exist=True)
    if not paths["descriptor"].is_file() or sha256(paths["descriptor"]) != sha256(sealed):
        raise ValueError("register requires the exact sealed descriptor; run promote-runtime first")
    validate_runtime(spec)
    registry_path = ROOT / "data" / "art_profiles" / "playable_profiles.json"
    registry = load_json(registry_path)
    profiles = registry.get("profiles", [])
    if not isinstance(profiles, list):
        raise ValueError("playable profile registry is malformed")
    if any(row.get("actor_id") == spec["actor_id"] for row in profiles if isinstance(row, dict)):
        raise ValueError(f"actor_id already registered: {spec['actor_id']}")
    registration = dict(spec["registration"])
    for asset_key in ["master_asset", "portrait_asset", "rig_sheet", "detail_overlay_asset", "weapon_hud_asset"]:
        asset_path = project_path(registration.get(asset_key, ""), f"registration.{asset_key}")
        if not asset_path.is_file():
            raise ValueError(f"registration asset missing: {relative(asset_path)}")
    profile = {
        "actor_id": spec["actor_id"],
        "name": spec["display_name"],
        "role": spec["role"],
        "visual_profile": registration["visual_profile"],
        "authored_runtime_descriptor": relative(paths["descriptor"]),
        "costume_id": spec["costume_id"],
        **registration,
    }
    profiles.append(profile)
    registry["profiles"] = profiles
    write_json(registry_path, registry)
    return {"gate": "PASS", "registered_actor_id": spec["actor_id"], "profile_count": len(profiles)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "promote-motion", "promote-runtime", "build", "validate", "all", "register"])
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--candidate", help="project-local Blender+UAL candidate directory")
    parser.add_argument("--receipt", help="content-bound all-gate motion_harness receipt; required for promotion/registration")
    parser.add_argument("--descriptor", help="candidate descriptor for structural validation")
    parser.add_argument("--allow-missing-assets", action="store_true")
    args = parser.parse_args()
    try:
        spec = read_spec(args.spec)
        if args.command == "init":
            result = init_pipeline(spec)
        elif args.command == "promote-motion":
            if not args.candidate:
                raise ValueError("--candidate is required for promote-motion")
            result = promote_motion_candidate(spec, args.candidate, args.receipt)
        elif args.command == "promote-runtime":
            result = promote_runtime(spec, args.receipt)
        elif args.command == "build":
            result = build_runtime(spec, args.candidate)
        elif args.command == "validate":
            result = validate_runtime(spec, args.allow_missing_assets, args.descriptor)
        elif args.command == "all":
            init_pipeline(spec)
            result = build_runtime(spec, args.candidate)
            result["structural_qa"] = validate_runtime(spec, descriptor_value=result["descriptor"])
        else:
            result = register_profile(spec, args.receipt)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
