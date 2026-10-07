#!/usr/bin/env python3
"""Package generic Blender+UAL direction-master renders into exact-green atlases.

This is deterministic technical compositing only. It does not generate or
repaint character art; every visible pixel comes from the approved ImageGen
direction masters rendered through Blender's motion rig.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)


def project_path(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
    return resolved


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"JSON object required: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def longest_repeat(values: list[str]) -> int:
    maximum = run = 0
    previous = None
    for value in values:
        run = run + 1 if value == previous else 1
        previous = value
        maximum = max(maximum, run)
    return maximum


def source_revision(source_root: Path) -> str:
    """Read the immutable ImageGen-master revision from its candidate folder.

    A direction-master rig is a valid motion pipeline only when every facing
    comes from the same selected master revision.  Do not quietly fall back to
    an earlier ``current`` master: that was the mechanism behind the mixed
    MICA V3/V4 export.
    """
    match = re.search(r"(v[0-9][a-z0-9._-]*)$", source_root.name, re.IGNORECASE)
    if not match:
        raise SystemExit(f"direction-master root must end with an explicit revision: {source_root.name}")
    return match.group(1).lower()


def pack_frame(path: Path, cell: int) -> np.ndarray:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    if rgba.shape != (cell, cell, 4):
        raise SystemExit(f"unexpected Blender frame dimensions: {path} {rgba.shape}")
    values = rgba[:, :, :3].astype(np.int16)
    green_spill = (values[:, :, 1] >= values[:, :, 0] + 40) & (values[:, :, 1] >= values[:, :, 2] + 40)
    visible = (rgba[:, :, 3] >= 128) & ~green_spill
    packed = np.broadcast_to(GREEN, (cell, cell, 3)).copy()
    packed[visible] = rgba[:, :, :3][visible]
    return packed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, help="project-local selected ImageGen direction-master directory")
    parser.add_argument("--authority-review", type=Path, help="Ponytail-reviewed source-master continuity JSON")
    args = parser.parse_args()
    spec_path = project_path(args.spec, "spec")
    candidate = project_path(args.candidate, "candidate")
    spec = load_json(spec_path)
    prefix = str(spec.get("art_prefix", str(spec["slug"]).upper()))
    cell = int(spec["runtime"]["cell_size"])
    states = {name: int(row["frames"]) for name, row in spec["runtime"]["states"].items()}
    manifest_path = candidate / f"{prefix}_BLENDER_UAL_RENDER_MANIFEST.json"
    manifest = load_json(manifest_path)
    if manifest.get("motion_only") is not True:
        raise SystemExit("renderer manifest must declare motion_only")
    source_root = (
        project_path(args.source_root, "source-root")
        if args.source_root is not None
        else ROOT / spec["paths"]["work_root"] / "imagegen" / "current"
    )
    if not source_root.is_dir():
        raise SystemExit(f"ImageGen direction-master root is missing: {source_root}")
    revision = source_revision(source_root)
    review_path = (
        project_path(args.authority_review, "authority-review")
        if args.authority_review is not None
        else source_root / f"{prefix}_COSTUME_CONTINUITY_REVIEW.json"
    )
    review = load_json(review_path)
    if review.get("costume_continuity") != "PASS":
        raise SystemExit("costume continuity review must PASS")
    expected_source_root = source_root.relative_to(ROOT).as_posix()
    if review.get("source_master_root") not in (None, expected_source_root):
        raise SystemExit("costume continuity review identifies a different source-master root")
    if review.get("source_revision") not in (None, revision):
        raise SystemExit("costume continuity review source revision mismatch")
    if manifest.get("source_master_root") != expected_source_root:
        raise SystemExit("renderer manifest source master root does not match packaging source root")
    rendered_sources = manifest.get("source_master_images")
    if not isinstance(rendered_sources, dict):
        raise SystemExit("renderer manifest must pin every selected source-master image")
    # Prevent source drift between Blender rendering and atlas packaging.  A
    # matching folder name alone is not provenance: a master can be replaced in
    # place.  All raw authority, exact-green input and mask hashes must match
    # the files that Blender used.
    for direction in DIRECTIONS:
        row = rendered_sources.get(direction)
        if not isinstance(row, dict):
            raise SystemExit(f"renderer manifest is missing source pin: {direction}")
        expected = {
            "selected_master": source_root / f"{prefix}_{direction}_IMAGEGEN_GREEN.png",
            "render_input": (
                source_root / f"{prefix}_{direction}_IMAGEGEN_EXACT_GREEN.png"
                if (source_root / f"{prefix}_{direction}_IMAGEGEN_EXACT_GREEN.png").is_file()
                else source_root / f"{prefix}_{direction}_IMAGEGEN_GREEN.png"
            ),
            "mask": source_root / f"{prefix}_{direction}_IMAGEGEN_MASK.png",
        }
        for key, path in expected.items():
            if row.get(key) != path.relative_to(ROOT).as_posix() or row.get(f"{key}_sha256") != sha256(path):
                raise SystemExit(f"renderer source pin drift detected: {direction} {key}")
    if (candidate / "SOURCE_PROVENANCE.json").exists():
        raise SystemExit("refusing to overwrite packaged candidate")

    outputs: dict[str, dict[str, object]] = {}
    for direction in DIRECTIONS:
        state_rows: dict[str, object] = {}
        for state, count in states.items():
            frames = [candidate / "blender_frames" / direction / state / f"{index:02d}.png" for index in range(count)]
            if not all(path.is_file() for path in frames):
                raise SystemExit(f"missing Blender frames: {direction} {state}")
            cells = [pack_frame(path, cell) for path in frames]
            hashes = [hashlib.sha256(value.tobytes()).hexdigest() for value in cells]
            unique = len(set(hashes))
            if state == "move" and (unique < 8 or longest_repeat(hashes) > 2):
                raise SystemExit(f"visible gait structure failed: {direction} unique={unique} repeat={longest_repeat(hashes)}")
            atlas = np.concatenate(cells, axis=0)
            coverage = float(np.mean(np.all(atlas == GREEN, axis=2)))
            if not 0.10 <= coverage < 0.995:
                raise SystemExit(f"exact-green coverage failed: {direction} {state} {coverage:.6f}")
            output = candidate / direction / f"{state}_green.png"
            output.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(atlas, mode="RGB").save(output)
            state_rows[state] = {
                "atlas": output.relative_to(ROOT).as_posix(),
                "sha256": sha256(output),
                "frame_count": count,
                "atlas_resolution": [cell, cell * count],
                "unique_composite_frames": unique,
                "max_repeat": longest_repeat(hashes),
                "exact_green_coverage": round(coverage, 6),
            }
        outputs[direction] = state_rows

    authorities: dict[str, object] = {}
    minimum_edge = None
    for direction in DIRECTIONS:
        rgb = source_root / f"{prefix}_{direction}_IMAGEGEN_GREEN.png"
        mask = source_root / f"{prefix}_{direction}_IMAGEGEN_MASK.png"
        with Image.open(rgb) as image:
            resolution = list(image.size)
        minimum_edge = min(resolution) if minimum_edge is None else min(minimum_edge, min(resolution))
        authorities[direction] = {
            "rgb": rgb.relative_to(ROOT).as_posix(),
            "rgb_sha256": sha256(rgb),
            "mask": mask.relative_to(ROOT).as_posix(),
            "mask_sha256": sha256(mask),
            "source_resolution": resolution,
        }
    provenance = {
        "schema": 1,
        "actor_id": spec["actor_id"],
        "imagegen_author": "built-in ImageGen",
        "blender_ual_motion": True,
        "costume_id": spec["costume_id"],
        "costume_continuity": "PASS",
        "authority_resolution": [int(minimum_edge), int(minimum_edge)],
        "authority_review": review_path.relative_to(ROOT).as_posix(),
        "authority_review_sha256": sha256(review_path),
        "direction_authorities": authorities,
        "gait_source_revision": revision,
        "gait_source_revisions_by_direction": {direction: revision for direction in DIRECTIONS},
        "motion_only_contract": {
            "source_art_modified": False,
            "source_art_regenerated_locally": False,
            "renderer_manifest": manifest_path.relative_to(ROOT).as_posix(),
            "renderer_manifest_sha256": sha256(manifest_path),
            "blender_scene": manifest["blender"]["scene"],
            "blender_scene_sha256": manifest["blender"]["scene_sha256"],
            "blender_version": manifest["blender"]["version"],
            "ual_locomotion_curve": manifest["ual"]["locomotion_curve"],
            "ual_locomotion_curve_sha256": manifest["ual"]["locomotion_curve_sha256"],
            "ual_fire_curve": manifest["ual"]["fire_curve"],
            "ual_fire_curve_sha256": manifest["ual"]["fire_curve_sha256"],
            "ual_license_evidence": manifest["ual"]["license"],
        },
        "technical_packaging": "Binary alpha compositing and exact-green matte replacement only; no source-art redraw.",
        "outputs": outputs,
    }
    provenance_path = candidate / "SOURCE_PROVENANCE.json"
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DIRECTION_MASTER_BLENDER_UAL_PACKAGE_PASS=" + json.dumps({
        "actor_id": spec["actor_id"],
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "directions": len(outputs),
        "provenance": provenance_path.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
