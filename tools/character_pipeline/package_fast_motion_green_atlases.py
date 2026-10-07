#!/usr/bin/env python3
"""Package Blender RGBA frame renders into exact-green fast-pipeline atlases.

The only image operation here is deterministic technical compositing: each
Blender-rendered alpha pixel is either retained or placed on exact #00FF00.
It does not generate or redraw character art.  Source masters stay untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ("E", "SE", "S", "SW", "W", "NW", "N", "NE")
STATES = {"idle": 4, "move": 24, "fire": 6}
GREEN = np.asarray([0, 255, 0], dtype=np.uint8)
GAIT_SOURCE_REVISION = re.compile(r"/candidate_[^/]+_walk_[a-z]+_(v[0-9][a-z0-9._-]*)_real_gait/", re.IGNORECASE)


def inside_project(path: Path, label: str) -> Path:
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must remain inside project: {resolved}") from exc
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
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise SystemExit(f"{label} must be a JSON object")
    return parsed


def pack_frame(frame_path: Path, cell_size: int) -> np.ndarray:
    if not frame_path.is_file():
        raise SystemExit(f"missing Blender frame: {frame_path}")
    rgba = np.asarray(Image.open(frame_path).convert("RGBA"), dtype=np.uint8)
    if tuple(rgba.shape[:2]) != (cell_size, cell_size):
        raise SystemExit(f"unexpected frame size {frame_path}: {rgba.shape[1]}x{rgba.shape[0]}")
    # Binary alpha is intentional: the runtime consumes exact chroma keyed
    # color, so semi-transparent renderer edges must not become green halos.
    values = rgba[:, :, :3].astype(np.int16)
    # Rook's locked palette contains no green costume module.  A 40-level
    # dominance threshold therefore removes the renderer/source matte fringe
    # while preserving charcoal, white hair, and amber equipment pixels.
    green_spill = (values[:, :, 1] >= values[:, :, 0] + 40) & (values[:, :, 1] >= values[:, :, 2] + 40)
    visible = (rgba[:, :, 3] >= 128) & ~green_spill
    rgb = np.broadcast_to(GREEN, (cell_size, cell_size, 3)).copy()
    rgb[visible] = rgba[:, :, :3][visible]
    return rgb


def longest_repeat(values: list[str]) -> int:
    largest = run = 0
    previous = None
    for value in values:
        run = run + 1 if value == previous else 1
        previous = value
        largest = max(largest, run)
    return largest


def gait_source_revision(value: str, direction: str) -> str:
    """Return the ImageGen gait revision embedded in an authority path.

    A non-matching source is a hard error.  Revision provenance is not
    decorative: a mixed V3/V4 export can satisfy every frame-count and alpha
    test while leaving unrepaired directions in the runtime.
    """
    match = GAIT_SOURCE_REVISION.search(value.replace("\\", "/"))
    if not match:
        raise SystemExit(f"missing gait-source revision in {direction} authority: {value}")
    return match.group(1).lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--cleanup-frames", action="store_true")
    parser.add_argument("--resume-packed", action="store_true", help="finalize a complete candidate after a later gate failed without rewriting matching atlases")
    args = parser.parse_args()
    spec_path = inside_project(args.spec, "spec")
    candidate = inside_project(args.candidate, "candidate")
    spec = load_json(spec_path, "spec")
    art_prefix = str(spec.get("art_prefix") or "ROOK_C02")
    render_manifest_path = candidate / f"{art_prefix}_BLENDER_UAL_RENDER_MANIFEST.json"
    render_manifest = load_json(render_manifest_path, "Blender render manifest")
    if render_manifest.get("motion_only") is not True:
        raise SystemExit("Blender render manifest does not declare motion_only")
    cell_size = int(spec["runtime"]["cell_size"])
    source_root = ROOT / spec["paths"]["work_root"] / "imagegen" / "current"
    review_path = source_root / f"{art_prefix}_COSTUME_CONTINUITY_REVIEW.json"
    review = load_json(review_path, "costume continuity review")
    if review.get("costume_continuity") != "PASS":
        raise SystemExit("costume continuity must PASS before packaging motion")
    destinations = [candidate / direction / f"{state}_green.png" for direction in DIRECTIONS for state in STATES]
    existing_destinations = [destination for destination in destinations if destination.exists()]
    if (candidate / "SOURCE_PROVENANCE.json").exists():
        raise SystemExit("refusing to overwrite existing packed candidate outputs")
    if existing_destinations and (not args.resume_packed or len(existing_destinations) != len(destinations)):
        raise SystemExit("refusing to overwrite existing packed candidate outputs")

    output_records: dict[str, dict[str, object]] = {}
    for direction in DIRECTIONS:
        direction_record: dict[str, object] = {}
        for state, count in STATES.items():
            frames = [candidate / "blender_frames" / direction / state / f"{index:02d}.png" for index in range(count)]
            cells = [pack_frame(path, cell_size) for path in frames]
            hashes = [hashlib.sha256(cell.tobytes()).hexdigest() for cell in cells]
            unique_frames = len(set(hashes))
            if state == "move":
                if unique_frames < 8 or longest_repeat(hashes) > 2:
                    raise SystemExit(f"real-gait contract failed in {direction} move: unique={unique_frames}, max_repeat={longest_repeat(hashes)}")
            elif state == "idle" and unique_frames != 1:
                raise SystemExit(f"idle lower-body lock requires exactly one static source in {direction} {state}")
            elif state == "fire" and unique_frames < 2:
                raise SystemExit(f"UAL upper-body fire recoil is missing in {direction}: only {unique_frames} composite frame")
            atlas = np.concatenate(cells, axis=0)
            green_coverage = float(np.mean(np.all(atlas == GREEN, axis=2)))
            if not 0.10 <= green_coverage < 0.995:
                raise SystemExit(f"exact green coverage failed {direction} {state}: {green_coverage:.6f}")
            output = candidate / direction / f"{state}_green.png"
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                with Image.open(output) as existing:
                    expected = np.asarray(existing.convert("RGB"), dtype=np.uint8)
                if expected.shape != atlas.shape or not np.array_equal(expected, atlas):
                    raise SystemExit(f"resume candidate atlas does not exactly match Blender frames: {output}")
            else:
                Image.fromarray(atlas, mode="RGB").save(output)
            with Image.open(output) as check:
                if check.size != (cell_size, cell_size * count) or check.mode != "RGB":
                    raise SystemExit(f"atlas round-trip failed: {output}")
            direction_record[state] = {
                "atlas": output.relative_to(ROOT).as_posix(),
                "sha256": sha256(output),
                "frame_count": count,
                "atlas_resolution": [cell_size, cell_size * count],
                "exact_green_coverage": round(green_coverage, 6),
                "unique_binary_composite_frames": unique_frames,
            }
        output_records[direction] = direction_record

    gait_validator = ROOT / "tools" / "art_pipeline" / "validate_rook_gait_contract.py"
    gait_report = candidate / (f"{art_prefix}_GAIT_CONTRACT_FINAL.json" if args.resume_packed else f"{art_prefix}_GAIT_CONTRACT.json")
    result = subprocess.run(
        [sys.executable, str(gait_validator), "--root", str(candidate), "--suffix", "_green.png", "--report", str(gait_report)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("gait structural gate failed after packaging:\n" + (result.stdout or result.stderr))

    # V26+ carries twelve reviewed full-body gait sources per direction.  The
    # retired pair schema is deliberately rejected: two poses cannot satisfy
    # a visible left/right walk, regardless of UAL timing metadata.
    source_sets = render_manifest.get("direction_authorities")
    if not isinstance(source_sets, dict):
        raise SystemExit("render manifest is missing twelve-pose gait authorities")
    authority: dict[str, object] = {}
    source_revisions_by_direction: dict[str, str] = {}
    for direction in DIRECTIONS:
        sources = source_sets.get(direction)
        if not isinstance(sources, list) or len(sources) != 12:
            raise SystemExit(f"render manifest requires exactly twelve reviewed gait sources for {direction}")
        support = [source.get("gait_support") for source in sources if isinstance(source, dict)]
        if support[:3] != ["left", "left", "left"] or support[6:9] != ["right", "right", "right"]:
            raise SystemExit(f"gait source support order does not match UAL contact windows for {direction}")
        verified_sources: list[dict[str, object]] = []
        for index, source in enumerate(sources):
            if not isinstance(source, dict) or int(source.get("gait_source_index", -1)) != index:
                raise SystemExit(f"invalid pose authority record for {direction}")
            rgb_ref, mask_ref, qa_ref = source.get("rgb"), source.get("mask"), source.get("normalization_qa")
            extraction_ref = source.get("gait_sheet_extraction")
            if not all(isinstance(value, str) for value in (rgb_ref, mask_ref, qa_ref)):
                raise SystemExit(f"incomplete pose authority record for {direction}")
            if not isinstance(extraction_ref, str):
                raise SystemExit(f"missing source-sheet extraction evidence for {direction} F{index:02d}")
            rgb = inside_project(Path(rgb_ref), f"{direction} pose RGB")
            mask = inside_project(Path(mask_ref), f"{direction} pose matte")
            qa_path = inside_project(Path(qa_ref), f"{direction} pose normalization QA")
            extraction_path = inside_project(Path(extraction_ref), f"{direction} source-sheet extraction")
            qa = load_json(qa_path, f"{direction} pose normalization QA")
            if qa.get("pass") is not True or qa.get("generated_pixels_modified") is not False:
                raise SystemExit(f"pose authority normalization did not PASS: {qa_path}")
            with Image.open(rgb) as image:
                resolution = list(image.size)
            if resolution != [512, 512]:
                raise SystemExit(f"gait source cell must retain native 512x512 crop: {rgb} {resolution}")
            extraction = load_json(extraction_path, f"{direction} source-sheet extraction")
            if extraction.get("pass") is not True or extraction.get("input_resolution") != [1024, 1536]:
                raise SystemExit(f"gait source sheet must retain native 1024x1536 evidence: {extraction_path}")
            if sha256(rgb) != source.get("rgb_sha256") or sha256(mask) != source.get("mask_sha256") or sha256(extraction_path) != source.get("gait_sheet_extraction_sha256"):
                raise SystemExit(f"pose authority hash mismatch for {direction}: {rgb}")
            verified_sources.append({
                "gait_source_index": index,
                "source_direction": source.get("source_direction"),
                "pose_transfer": source.get("pose_transfer"),
                "gait_support": source.get("gait_support"),
                "rgb": rgb.relative_to(ROOT).as_posix(),
                "rgb_sha256": sha256(rgb),
                "mask": mask.relative_to(ROOT).as_posix(),
                "mask_sha256": sha256(mask),
                "normalization_qa": qa_path.relative_to(ROOT).as_posix(),
                "normalization_qa_sha256": sha256(qa_path),
                "gait_sheet_extraction": extraction_path.relative_to(ROOT).as_posix(),
                "gait_sheet_extraction_sha256": sha256(extraction_path),
                "native_cell_resolution": resolution,
                "native_source_sheet_resolution": extraction.get("input_resolution"),
            })
        revisions = {gait_source_revision(str(source["rgb"]), direction) for source in verified_sources}
        if len(revisions) != 1:
            raise SystemExit(f"mixed gait-source revisions within {direction}: {sorted(revisions)}")
        source_revisions_by_direction[direction] = next(iter(revisions))
        authority[direction] = {"gait_sources": verified_sources}

    all_source_revisions = set(source_revisions_by_direction.values())
    if len(all_source_revisions) != 1:
        rendered = ", ".join(f"{direction}={source_revisions_by_direction[direction]}" for direction in DIRECTIONS)
        raise SystemExit(
            "mixed gait-source revisions across directions are not promotable; "
            f"rendered revisions: {rendered}"
        )
    gait_revision = next(iter(all_source_revisions))

    blender_info = render_manifest.get("blender", {})
    ual_info = render_manifest.get("ual", {})
    provenance = {
        "schema": 1,
        "imagegen_author": "built-in ImageGen",
        "blender_ual_motion": True,
        "costume_id": spec["costume_id"],
        "costume_continuity": "PASS",
        "authority_resolution": [1024, 1536],
        "authority_source_review": review_path.relative_to(ROOT).as_posix(),
        "authority_source_review_sha256": sha256(review_path),
        "direction_authorities": authority,
        "gait_source_revision": gait_revision,
        "gait_source_revisions_by_direction": source_revisions_by_direction,
        "motion_only_contract": {
            "source_art_modified": False,
            "source_art_regenerated_locally": False,
            "blender_scene": blender_info.get("scene"),
            "blender_scene_sha256": blender_info.get("scene_sha256"),
            "blender_version": blender_info.get("version"),
            "ual_locomotion_curve": ual_info.get("locomotion_curve"),
            "ual_locomotion_curve_sha256": ual_info.get("locomotion_curve_sha256"),
            "ual_fire_curve": ual_info.get("fire_curve"),
            "ual_fire_curve_sha256": ual_info.get("fire_curve_sha256"),
            "ual_license_evidence": ual_info.get("license"),
            "renderer_manifest": render_manifest_path.relative_to(ROOT).as_posix(),
            "renderer_manifest_sha256": sha256(render_manifest_path),
        },
        "technical_packaging": "Binary alpha compositing plus deterministic green-spill removal to exact #00FF00 after Blender render; no source-art redraw.",
        "outputs": output_records,
    }
    provenance_path = candidate / "SOURCE_PROVENANCE.json"
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.cleanup_frames:
        frames_root = candidate / "blender_frames"
        if frames_root.exists():
            shutil.rmtree(frames_root)
    print("ROOK_FAST_MOTION_PACK_PASS=" + json.dumps({"candidate": candidate.relative_to(ROOT).as_posix(), "provenance": provenance_path.relative_to(ROOT).as_posix(), "directions": len(output_records), "frames_cleaned": bool(args.cleanup_frames)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
